"""Conflict-aware decoder baselines (reviewer 3.3).

For each of the 250 static instances (5 scenarios x 50 seeds) we run four cheap
candidate generators and check DIRECT verified feasibility (no CP-SAT repair):

  utility     : per-variable most-preferred value over the GAC-filtered domain
                (reproduces the paper's weak decode)
  greedy_fc   : greedy sequential assignment with immediate constraint checks
  fc_search   : sequential assignment with forward checking + backtracking
  min_conflict: min-conflicts local search from the utility decode

Preference order is ascending value (value 0 most preferred), matching the
pipeline's utility decode; the "kept-preferred" objective is the fraction of
variables assigned their most-preferred value (value 0).

When a candidate is NOT directly feasible we feed it into the explanation
repair engine and record repair success, final core size, and repair latency,
to test whether explanation-guided repair remains valuable and cheap when
started from a competent heuristic.
"""
import sys, os, time, csv, random, statistics
sys.path.insert(0, "/sessions/zealous-wonderful-darwin/mnt/ORAN")
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.propagation.gac import GAC
from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.repair.engine import RepairEngine

SCEN = ["S1","S2","S3","S4","S5"]
SEEDS = range(42, 92)

def incident(relations, vid):
    return [r for r in relations if vid in r.scope]

def num_violations(assign, relations):
    n = 0
    for r in relations:
        if not r.is_hard: continue
        try:
            if not r.is_allowed(tuple(assign[v] for v in r.scope)): n += 1
        except KeyError:
            n += 1
    return n

def kept_pref(assign):
    # preferred value is 0 for every variable (ascending preference)
    return sum(1 for v in assign.values() if v == 0) / len(assign)

# ---------- decoders ----------
def decode_utility(variables, D, R):
    filtered = {v.id: FilteredDomain(D[v.id]) for v in variables}
    active = [ActiveRelation(r) for r in R]
    GAC(variables, filtered, active).enforce()
    return {v.id: (sorted(filtered[v.id].active_values)[0]
                   if filtered[v.id].active_values else D[v.id].base_values[0])
            for v in variables}

def decode_greedy_fc(variables, D, R):
    """Greedy sequential + immediate consistency check (single pass, no backtrack)."""
    assign = {}
    order = sorted(v.id for v in variables)
    inc = {vid: incident(R, vid) for vid in order}
    for vid in order:
        chosen = None
        for val in sorted(D[vid].base_values):          # preference order
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
    """Sequential assignment with forward checking + chronological backtracking."""
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
            # forward check: prune future domains
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
        # fall back to greedy candidate if search exhausted budget
        return decode_greedy_fc(variables, D, R)
    return res

def decode_min_conflicts(variables, D, R, max_steps=200, seed=0):
    rng = random.Random(seed)
    assign = decode_utility(variables, D, R)
    order = [v.id for v in variables]
    inc = {vid: incident(R, vid) for vid in order}
    for _ in range(max_steps):
        conflicted = [vid for vid in order
                      if any(not r.is_allowed(tuple(assign[s] for s in r.scope))
                             for r in inc[vid] if r.is_hard)]
        if not conflicted:
            return assign
        vid = rng.choice(conflicted)
        best_val, best_c = assign[vid], None
        for val in sorted(D[vid].base_values):          # ties -> preferred
            c = 0
            for r in inc[vid]:
                tup = tuple(val if s == vid else assign[s] for s in r.scope)
                if not r.is_allowed(tup): c += 1
            if best_c is None or c < best_c:
                best_c, best_val = c, val
        assign[vid] = best_val
    return assign

DECODERS = {
    "utility":      lambda V,D,R,seed: decode_utility(V,D,R),
    "greedy_fc":    lambda V,D,R,seed: decode_greedy_fc(V,D,R),
    "fc_search":    lambda V,D,R,seed: decode_fc_search(V,D,R),
    "min_conflict": lambda V,D,R,seed: decode_min_conflicts(V,D,R,seed=seed),
}

rows = []
for scen in SCEN:
    for seed in SEEDS:
        V, D, R, planted = generate_static_instance(scen, seed)
        ver = Verifier(D, R)
        for dname, fn in DECODERS.items():
            t0 = time.monotonic_ns()
            cand = fn(V, D, R, seed)
            dec_ns = time.monotonic_ns() - t0
            feas = ver.verify(cand, "x", "x")
            viol = num_violations(cand, R)
            kp = kept_pref(cand)
            rep_success = feas
            rep_core = 0; rep_ns = 0; rep_exp = 0
            if not feas:
                eng = RepairEngine(V, D, R, ver)
                rr = eng.repair("explanation", cand, "repair", deadline_ms=100)
                rep_success = rr["success"]; rep_core = rr["final_core_size"]
                rep_ns = rr["total_time_ns"]; rep_exp = rr["expansions"]
            rows.append(dict(scenario=scen, seed=seed, decoder=dname,
                             direct_feasible=int(feas), violations=viol,
                             kept_pref=round(kp,4), decode_ms=round(dec_ns/1e6,4),
                             repair_success=int(rep_success), repair_core=rep_core,
                             repair_expansions=rep_exp, repair_ms=round(rep_ns/1e6,4),
                             end2end_ms=round((dec_ns+rep_ns)/1e6,4)))
    print("done", scen, flush=True)

out = "/tmp/decoder_baselines.csv"
with open(out,"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------- summary ----------
def agg(dname):
    rs = [r for r in rows if r["decoder"]==dname]
    n = len(rs)
    df = sum(r["direct_feasible"] for r in rs)
    kp = statistics.mean(r["kept_pref"] for r in rs)
    med_dec = statistics.median(r["decode_ms"] for r in rs)
    med_viol = statistics.median(r["violations"] for r in rs)
    rep_needed = [r for r in rs if not r["direct_feasible"]]
    rep_ok = sum(r["repair_success"] for r in rs)
    med_e2e = statistics.median(r["end2end_ms"] for r in rs)
    med_core = statistics.median([r["repair_core"] for r in rep_needed]) if rep_needed else 0
    return dict(decoder=dname, n=n, direct=df, direct_pct=round(100*df/n,1),
                med_violations=med_viol, kept_pref_pct=round(100*kp,1),
                med_decode_ms=round(med_dec,3), rep_needed=len(rep_needed),
                after_repair=rep_ok, after_repair_pct=round(100*rep_ok/n,1),
                med_repair_core=med_core, med_e2e_ms=round(med_e2e,3))

print("\n=== SUMMARY (250 instances each) ===")
hdr = ["decoder","direct","direct_pct","med_violations","kept_pref_pct","med_decode_ms","rep_needed","after_repair_pct","med_repair_core","med_e2e_ms"]
print("\t".join(hdr))
for d in ["utility","greedy_fc","fc_search","min_conflict"]:
    a = agg(d)
    print("\t".join(str(a[k]) for k in hdr))
