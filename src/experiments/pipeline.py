"""
Coordination pipeline, parameterised by a method configuration.

A method config is a dict with keys:
  gac:        bool   -- run observable incremental GAC
  continuous: bool   -- run relation-conditioned continuous inference
  repair:     bool   -- run exact repair when the decode is invalid
  strategy:   str    -- repair strategy for the RepairEngine
                        (violated0 | frontier | explanation | assumption |
                         radius0 | radius1 | radius2 | fullscope)
  decode:     str    -- 'continuous' | 'utility' | 'random' | 'priority'

Every returned record includes the decoded candidate and its counterfactual
KPIs (what would happen if the raw proposal were executed) as well as the
verified-executed outcome, so that network KPIs can be reported separately for
counterfactual, verified-optimized, and fallback execution.
"""
import time
import random
from typing import Dict, Any

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.propagation.gac import GAC
from src.continuous.consensus import ContinuousConsensus
from src.continuous.decoder import Decoder
from src.continuous.diagnostics import Diagnostics
from src.repair.engine import RepairEngine

REPAIR_FIELDS = ["initial_core_size", "final_core_size", "expansions",
                 "used_explanation", "used_assumption_core", "used_frontier",
                 "boundary_released", "gac_time_ns", "cpsat_time_ns",
                 "full_scope_required", "status"]



def decode_greedy_fc(variables, D, R):
    assign = {}
    order = sorted(v.id for v in variables)
    inc = {vid: [r for r in R if vid in r.scope] for vid in order}
    for vid in order:
        chosen = None
        for val in sorted(D[vid].base_values):
            ok = True
            for r in inc[vid]:
                if all((sv in assign or sv == vid) for sv in r.scope):
                    tup = tuple(val if sv == vid else assign[sv] for sv in r.scope)
                    if not r.is_allowed(tup):
                        ok = False; break
            if ok:
                chosen = val; break
        assign[vid] = chosen if chosen is not None else sorted(D[vid].base_values)[0]
    return assign

def decode_fc_search(variables, D, R, budget_ms=50):
    import time
    order = sorted(v.id for v in variables)
    binrels = {}
    for r in R:
        if len(r.scope) == 2:
            binrels.setdefault(r.scope[0], []).append(r)
            binrels.setdefault(r.scope[1], []).append(r)
    dom = {vid: list(sorted(D[vid].base_values)) for vid in order}
    assign = {}
    t0 = time.monotonic_ns()
    def consistent(vid, val):
        for r in binrels.get(vid, []):
            other = r.scope[0] if r.scope[1] == vid else r.scope[1]
            if other in assign:
                tup = tuple(val if s == vid else assign[s] for s in r.scope)
                if not r.is_allowed(tup): return False
        return True
    def bt(i, curdom):
        if (time.monotonic_ns() - t0)/1e6 > budget_ms: return None
        if i == len(order): return dict(assign)
        vid = order[i]
        for val in curdom[vid]:
            if not consistent(vid, val): continue
            assign[vid] = val
            newdom = {k: list(v) for k, v in curdom.items()}
            dead = False
            for r in binrels.get(vid, []):
                other = r.scope[0] if r.scope[1] == vid else r.scope[1]
                j = order.index(other) if other in order else -1
                if other in assign or j <= i: continue
                keep = []
                for ov in newdom[other]:
                    tup = tuple(val if s == vid else (ov if s == other else assign.get(s)) for s in r.scope)
                    if r.is_allowed(tup): keep.append(ov)
                newdom[other] = keep
                if not keep: dead = True; break
            if not dead:
                res = bt(i+1, newdom)
                if res is not None: return res
            del assign[vid]
        return None
    res = bt(0, dom)
    if res is None:
        return decode_greedy_fc(variables, D, R)
    return res

def run_pipeline(variables, base_domains, relations, context_id, verifier,
                 config: Dict[str, Any], deadline_ms: int = 100) -> Dict[str, Any]:
    m = {"propagation_time_ns": 0, "continuous_time_ns": 0, "repair_time_ns": 0,
         "total_time_ns": 0, "wipeout": False, "continuous_iterations": 0,
         "final_residual": 0.0, "final_fractionality": 0.0,
         "operational_stall": False, "invalid_decode": False,
         "repair_attempted": False, "repair_success": False,
         "raw_verified": False, "optimized_verified": False,
         "repaired_verified": False, "fallback_used": False,
         "fallback_verified": False, "executed_verified": False,
         "outcome": "blocked", "timeout": False, "infeasible": False,
         "values_before": 0, "values_after": 0, "tuples_before": 0,
         "tuples_after": 0, "repair_initial_core": 0, "repair_final_core": 0,
         "repair_expansions": 0, "repair_used_explanation": False,
         "repair_used_assumption_core": False, "repair_used_frontier": False,
         "repair_boundary_released": 0, "repair_full_scope": False,
         "repair_status": "none", "decoded": {}}

    t0 = time.monotonic_ns()
    filtered = {v.id: FilteredDomain(base_domains[v.id]) for v in variables}
    active = [ActiveRelation(r) for r in relations]
    m["values_before"] = sum(len(d.base_values) for d in base_domains.values())
    m["tuples_before"] = sum(len(r.relation.allowed_tuples) for r in active if r.relation.is_hard)

    # safe fallback (registered): first base value of each variable
    fallback = {v.id: base_domains[v.id].base_values[0] for v in variables}


    def finish(decoded, executed, outcome):
        m["decoded"] = decoded
        m["_executed"] = executed
        m["outcome"] = outcome
        m["executed_verified"] = executed is not None
        
        # Generate Certificate
        cert_overhead = 0
        cert_size = 0
        if executed is not None:
            ok, cert = verifier.verify(executed, context_id, context_id, return_cert=True)
            if ok:
                cert_overhead = cert["overhead_ns"]
                cert_size = cert["size_bytes"]
        else:
            ok, cert = verifier.verify(fallback, context_id, context_id, return_cert=True)
            if ok:
                cert_overhead = cert["overhead_ns"]
                cert_size = cert["size_bytes"]
        
        m["cert_overhead_ns"] = cert_overhead
        m["cert_size_bytes"] = cert_size
        m["total_time_ns"] = (time.monotonic_ns() - t0) + cert_overhead
        return m


    # ----- non-coordinated decodes -----
    if config["decode"] == "random":
        rng = random.Random(hash(context_id) & 0xffffffff)
        decoded = {v.id: rng.choice(base_domains[v.id].base_values) for v in variables}
        if verifier.verify(decoded, context_id, context_id):
            m["raw_verified"] = True; m["optimized_verified"] = True
            return finish(decoded, decoded, "direct")
        return _fallback(m, fallback, verifier, context_id, decoded, finish)
    if config["decode"] == "priority":
        decoded = {v.id: sorted(base_domains[v.id].base_values)[0] for v in variables}
        if verifier.verify(decoded, context_id, context_id):
            m["raw_verified"] = True; m["optimized_verified"] = True
            return finish(decoded, decoded, "direct")
        return _fallback(m, fallback, verifier, context_id, decoded, finish)

    
    if config["decode"] == "forward_check":
        decoded = decode_fc_search(variables, base_domains, [r.relation for r in active])
        m["raw_verified"] = verifier.verify(decoded, context_id, context_id)
        if m["raw_verified"]:
            m["optimized_verified"] = True
            return finish(decoded, decoded, "direct")

    # ----- 1. GAC -----
    if config["gac"]:
        tg = time.monotonic_ns()
        ok = GAC(variables, filtered, active).enforce()
        m["propagation_time_ns"] = time.monotonic_ns() - tg
        m["values_after"] = sum(len(d.active_values) for d in filtered.values())
        m["tuples_after"] = sum(len(r.active_tuples) for r in active if r.relation.is_hard)
        if not ok:
            m["wipeout"] = True
            return _fallback(m, fallback, verifier, context_id, {}, finish)
    else:
        m["values_after"] = m["values_before"]
        m["tuples_after"] = m["tuples_before"]

    # ----- 2. decode -----
    if config["continuous"]:
        tc = time.monotonic_ns()
        cons = ContinuousConsensus(variables, filtered, active)
        residual, iters = cons.solve()
        m["continuous_time_ns"] = time.monotonic_ns() - tc
        m["continuous_iterations"] = iters
        m["final_residual"] = residual
        decoded = Decoder(cons).decode()
        diag = Diagnostics(cons, verifier)
        dres = diag.diagnose(decoded, context_id)
        m["final_fractionality"] = diag.get_fractionality()
        m["operational_stall"] = dres["operational_stall"]
        m["invalid_decode"] = dres["invalid_non_stalled_decode"]
        m["raw_verified"] = dres["is_valid"]
    else:
        # utility-style deterministic decode over filtered domains
        decoded = {v.id: sorted(filtered[v.id].active_values)[0]
                   if filtered[v.id].active_values else base_domains[v.id].base_values[0]
                   for v in variables}
        m["raw_verified"] = verifier.verify(decoded, context_id, context_id)

    if m["raw_verified"]:
        m["optimized_verified"] = True
        return finish(decoded, decoded, "direct")

    # ----- 3. repair -----
    if config["repair"]:
        m["repair_attempted"] = True
        eng = RepairEngine(variables, base_domains, relations, verifier)
        r = eng.repair(config["strategy"], decoded, context_id,
                       deadline_ms=max(1, int(deadline_ms - (time.monotonic_ns() - t0) / 1e6)))
        m["repair_time_ns"] = r["total_time_ns"]
        m["repair_initial_core"] = r["initial_core_size"]
        m["repair_final_core"] = r["final_core_size"]
        m["repair_expansions"] = r["expansions"]
        m["repair_used_explanation"] = r["used_explanation"]
        m["repair_used_assumption_core"] = r["used_assumption_core"]
        m["repair_used_frontier"] = r["used_frontier"]
        m["repair_boundary_released"] = r["boundary_released"]
        m["repair_full_scope"] = r["full_scope_required"]
        m["repair_status"] = r["status"]
        m["timeout"] = (r["status"] == "timeout")
        m["infeasible"] = (r["status"] == "infeasible")
        if r["success"]:
            m["repair_success"] = True; m["repaired_verified"] = True
            outcome = "full_repair" if r["full_scope_required"] else "local_repair"
            return finish(r["assignment"], r["assignment"], outcome)

    return _fallback(m, fallback, verifier, context_id, decoded, finish)


def _fallback(m, fallback, verifier, ctx, decoded, finish):
    m["fallback_used"] = True
    m["fallback_verified"] = verifier.verify(fallback, ctx, ctx)
    if m["fallback_verified"]:
        return finish(decoded if decoded else fallback, fallback, "fallback")
    return finish(decoded if decoded else fallback, None, "blocked")
