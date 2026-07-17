"""
Instrumented repair engine used both by the coordination pipeline and by the
repair-ablation experiment. Every strategy fixes the boundary variables to the
decoded values and searches for a verifier-accepted full assignment; the
strategies differ only in how the repair core is initialised and expanded.

Instrumented fields (per repair call):
  strategy, success, status, initial_core_size, final_core_size, expansions,
  used_explanation, used_assumption_core, used_frontier, used_radius,
  boundary_released, gac_time_ns, cpsat_time_ns, total_time_ns, full_scope_required
"""
import time
from typing import Dict, Any, List, Set

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.propagation.gac import GAC
from src.propagation.explanations import extract_wipeout_explanation
from src.repair.cpsat_adapter import CPSATAdapter
from src.repair.radius_core import RadiusCoreBuilder

EXPANDING = {"frontier", "explanation", "assumption"}
FIXED = {"violated0", "radius0", "radius1", "radius2", "fullscope"}


class RepairEngine:
    def __init__(self, variables, base_domains, relations, verifier):
        self.variables = variables
        self.base_domains = base_domains
        self.relations = relations
        self.verifier = verifier
        self.rel_map = {r.id: r for r in relations}
        self.all_vars = set(v.id for v in variables)
        self.all_rels = set(r.id for r in relations)
        self.cpsat = CPSATAdapter(variables, base_domains, relations)

    # ----- helpers ---------------------------------------------------------
    def _violated_core(self, decoded):
        vr, vv = set(), set()
        for r in self.relations:
            if not r.is_hard:
                continue
            try:
                tup = tuple(decoded[v] for v in r.scope)
                ok = r.is_allowed(tup)
            except KeyError:
                ok = False
            if not ok:
                vr.add(r.id); vv.update(r.scope)
        if not vv:
            return set(self.all_vars), set(self.all_rels)
        return vv, vr

    def _incident_rels(self, core_vars):
        return {r.id for r in self.relations if any(v in core_vars for v in r.scope)}

    def _frontier(self, core_vars):
        add = set()
        for r in self.relations:
            if any(v in core_vars for v in r.scope):
                add.update(v for v in r.scope if v not in core_vars)
        return add

    def _induced_gac(self, core_vars, core_rels, decoded):
        """Enforce GAC on the induced model (core vars free, boundary vars
        fixed to decoded singletons). Returns (ok, wipeout_var, domains)."""
        involved = set(core_vars)
        for rid in core_rels:
            involved.update(self.rel_map[rid].scope)
        fdoms = {}
        for vid in involved:
            fd = FilteredDomain(self.base_domains[vid])
            if vid not in core_vars:
                fd.active_values = {decoded[vid]} if decoded[vid] in fd.active_values else set()
            fdoms[vid] = fd
        ars = [ActiveRelation(self.rel_map[rid]) for rid in core_rels]
        ok = GAC([v for v in self.variables if v.id in involved], fdoms, ars).enforce()
        wv = None
        if not ok:
            for vid, fd in fdoms.items():
                if fd.is_empty():
                    wv = vid; break
        return ok, wv, fdoms

    def _verify_full(self, decoded, core_solution):
        full = dict(decoded)
        full.update(core_solution)
        return full if self.verifier.verify(full, "repair", "repair") else None

    # ----- main entry ------------------------------------------------------
    def repair(self, strategy, decoded, context_id="repair", deadline_ms=100):
        t0 = time.monotonic_ns()
        m = {"strategy": strategy, "success": False, "status": "none",
             "initial_core_size": 0, "final_core_size": 0, "expansions": 0,
             "used_explanation": False, "used_assumption_core": False,
             "used_frontier": False, "used_radius": strategy.startswith("radius"),
             "boundary_released": 0, "gac_time_ns": 0, "cpsat_time_ns": 0,
             "total_time_ns": 0, "full_scope_required": False, "assignment": None}

        core_vars, core_rels = self._violated_core(decoded)
        m["initial_core_size"] = len(core_vars)

        def remaining_ms():
            used = (time.monotonic_ns() - t0) / 1e6
            return max(1, int(deadline_ms - used))

        # ---- fixed-scope strategies ----
        if strategy in FIXED:
            if strategy == "fullscope":
                core_vars, core_rels = set(self.all_vars), set(self.all_rels)
            elif strategy.startswith("radius"):
                h = int(strategy[-1])
                core_vars, core_rels = RadiusCoreBuilder(self.relations).build_core_from_vars(core_vars, h)
            else:  # violated0
                core_rels = self._incident_rels(core_vars)
            m["initial_core_size"] = len(core_vars)
            boundary = {vid: decoded[vid] for vid in decoded if vid not in core_vars}
            res = self.cpsat.solve(core_vars, self._incident_rels(core_vars), boundary, remaining_ms())
            m["cpsat_time_ns"] += res["model_build_time_ns"] + res["solver_time_ns"]
            m["status"] = self._status_name(res["status"])
            if res["assignment"]:
                full = self._verify_full(decoded, res["assignment"])
                if full:
                    m["success"] = True; m["assignment"] = full
            m["final_core_size"] = len(core_vars)
            m["full_scope_required"] = (core_vars >= self.all_vars)
            m["total_time_ns"] = time.monotonic_ns() - t0
            return m

        # ---- expanding strategies ----
        for _ in range(len(self.variables) + 1):
            core_rels = self._incident_rels(core_vars)
            boundary = {vid: decoded[vid] for vid in decoded if vid not in core_vars}

            if strategy == "assumption":
                res = self.cpsat.solve_with_assumptions(core_vars, core_rels, boundary, remaining_ms())
                m["cpsat_time_ns"] += res["model_build_time_ns"] + res["solver_time_ns"]
                m["status"] = self._status_name(res["status"])
                if res["assignment"]:
                    full = self._verify_full(decoded, res["assignment"])
                    if full:
                        m["success"] = True; m["assignment"] = full; break
                release = res.get("sufficient_core", set())
                if release:
                    m["used_assumption_core"] = True
                    m["boundary_released"] += len(release)
                    core_vars = core_vars | release
                else:
                    core_vars = core_vars | self._frontier(core_vars)
                    m["used_frontier"] = True
            else:  # frontier or explanation
                tg = time.monotonic_ns()
                ok, wv, _ = self._induced_gac(core_vars, core_rels, decoded)
                m["gac_time_ns"] += time.monotonic_ns() - tg
                if not ok:
                    if strategy == "explanation" and wv is not None:
                        _, _, fdoms = self._induced_gac(core_vars, core_rels, decoded)
                        expl = extract_wipeout_explanation(fdoms, wv)
                        addv = set()
                        for cid in expl.constraints:
                            addv.update(self.rel_map[cid].scope)
                        addv = {v for v in addv if v not in core_vars}
                        if not addv:
                            addv = self._frontier(core_vars); m["used_frontier"] = True
                        else:
                            m["used_explanation"] = True
                    else:
                        addv = self._frontier(core_vars); m["used_frontier"] = True
                    m["boundary_released"] += len(addv & set(boundary))
                    core_vars = core_vars | addv
                else:
                    res = self.cpsat.solve(core_vars, core_rels, boundary, remaining_ms())
                    m["cpsat_time_ns"] += res["model_build_time_ns"] + res["solver_time_ns"]
                    m["status"] = self._status_name(res["status"])
                    if res["assignment"]:
                        full = self._verify_full(decoded, res["assignment"])
                        if full:
                            m["success"] = True; m["assignment"] = full; break
                    addv = self._frontier(core_vars)
                    m["used_frontier"] = True
                    m["boundary_released"] += len(addv & set(boundary))
                    core_vars = core_vars | addv

            if core_vars >= self.all_vars:
                res = self.cpsat.solve(self.all_vars, self.all_rels, {}, remaining_ms())
                m["cpsat_time_ns"] += res["model_build_time_ns"] + res["solver_time_ns"]
                m["status"] = self._status_name(res["status"])
                if res["assignment"]:
                    full = self._verify_full(decoded, res["assignment"])
                    if full:
                        m["success"] = True; m["assignment"] = full
                core_vars = set(self.all_vars); break
            m["expansions"] += 1
            if (time.monotonic_ns() - t0) / 1e6 >= deadline_ms:
                m["status"] = "timeout"; break

        m["final_core_size"] = len(core_vars)
        m["full_scope_required"] = (core_vars >= self.all_vars)
        m["total_time_ns"] = time.monotonic_ns() - t0
        return m

    @staticmethod
    def _status_name(status):
        from ortools.sat.python import cp_model
        return {cp_model.OPTIMAL: "optimal", cp_model.FEASIBLE: "feasible",
                cp_model.INFEASIBLE: "infeasible", cp_model.UNKNOWN: "unknown"}.get(status, "none")
