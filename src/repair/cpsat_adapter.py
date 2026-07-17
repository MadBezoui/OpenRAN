import time
from typing import List, Dict, Any, Set
from ortools.sat.python import cp_model

from src.model.domains import Domain
from src.model.relations import Variable, Relation


class CPSATAdapter:
    """
    OR-Tools CP-SAT adapter for exact (local) repair subproblems.

    Two entry points are provided:

    * ``solve`` fixes boundary variables with hard equality constraints and
      returns a full assignment over the involved variables.
    * ``solve_with_assumptions`` fixes boundary variables through reified
      Boolean *assumption* literals ``b_j => (x_j = xhat_j)`` and, when the
      subproblem is infeasible, returns the subset of boundary variables that
      OR-Tools reports as a sufficient assumptions core
      (``SufficientAssumptionsForInfeasibility``). Releasing exactly those
      variables is the assumption-core expansion strategy.
    """

    def __init__(self, variables: List[Variable], base_domains: Dict[int, Domain],
                 relations: List[Relation]):
        self.variables = variables
        self.base_domains = base_domains
        self.relations = relations
        self.rel_map = {r.id: r for r in relations}

    def _involved(self, core_vars: Set[int], core_rels: Set[int]) -> Set[int]:
        involved = set(core_vars)
        for rid in core_rels:
            involved.update(self.rel_map[rid].scope)
        return involved

    def _build_common(self, model, core_vars, core_rels, involved):
        cp_vars = {}
        for vid in involved:
            dom = self.base_domains[vid].base_values
            cp_vars[vid] = model.NewIntVar(min(dom), max(dom), f"v_{vid}")
            if vid in core_vars:
                model.AddAllowedAssignments([cp_vars[vid]], [(v,) for v in dom])
        for rid in core_rels:
            rel = self.rel_map[rid]
            if not rel.is_hard:
                continue
            model.AddAllowedAssignments([cp_vars[v] for v in rel.scope],
                                        list(rel.allowed_tuples))
        return cp_vars

    def solve(self, core_vars: Set[int], core_rels: Set[int],
              boundary_assignments: Dict[int, Any], time_limit_ms: int = 100
              ) -> Dict[str, Any]:
        t0 = time.monotonic_ns()
        model = cp_model.CpModel()
        involved = self._involved(core_vars, core_rels)
        cp_vars = self._build_common(model, core_vars, core_rels, involved)
        for vid in involved:
            if vid not in core_vars and vid in boundary_assignments:
                model.Add(cp_vars[vid] == boundary_assignments[vid])
        t_build = time.monotonic_ns() - t0

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
        solver.parameters.num_search_workers = 1
        t1 = time.monotonic_ns()
        status = solver.Solve(model)
        t_solve = time.monotonic_ns() - t1

        res = {"assignment": None, "status": status,
               "model_build_time_ns": t_build, "solver_time_ns": t_solve,
               "sufficient_core": set()}
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            res["assignment"] = {vid: solver.Value(cp_vars[vid]) for vid in involved}
        return res

    def solve_with_assumptions(self, core_vars: Set[int], core_rels: Set[int],
                               boundary_assignments: Dict[int, Any],
                               time_limit_ms: int = 100) -> Dict[str, Any]:
        t0 = time.monotonic_ns()
        model = cp_model.CpModel()
        involved = self._involved(core_vars, core_rels)
        cp_vars = self._build_common(model, core_vars, core_rels, involved)

        lit_to_var = {}
        assumptions = []
        for vid in involved:
            if vid not in core_vars and vid in boundary_assignments:
                b = model.NewBoolVar(f"assume_{vid}")
                model.Add(cp_vars[vid] == boundary_assignments[vid]).OnlyEnforceIf(b)
                assumptions.append(b)
                lit_to_var[b.Index()] = vid
        model.AddAssumptions(assumptions)
        t_build = time.monotonic_ns() - t0

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
        solver.parameters.num_search_workers = 1
        t1 = time.monotonic_ns()
        status = solver.Solve(model)
        t_solve = time.monotonic_ns() - t1

        res = {"assignment": None, "status": status,
               "model_build_time_ns": t_build, "solver_time_ns": t_solve,
               "sufficient_core": set()}
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            res["assignment"] = {vid: solver.Value(cp_vars[vid]) for vid in involved}
        elif status == cp_model.INFEASIBLE:
            core = set()
            for idx in solver.SufficientAssumptionsForInfeasibility():
                if idx in lit_to_var:
                    core.add(lit_to_var[idx])
            # If the solver returns no assumption core, releasing all fixed
            # boundary variables is the sound (if conservative) fallback.
            res["sufficient_core"] = core if core else set(lit_to_var.values())
        return res
