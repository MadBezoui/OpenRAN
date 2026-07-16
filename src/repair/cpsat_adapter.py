from typing import List, Dict, Any, Set
from ortools.sat.python import cp_model

from src.model.domains import Domain
from src.model.relations import Variable, Relation

class CPSATAdapter:
    """
    Adapter for Google OR-Tools CP-SAT solver to solve exact repair problems.
    """
    def __init__(self, variables: List[Variable], base_domains: Dict[int, Domain], relations: List[Relation]):
        self.variables = variables
        self.base_domains = base_domains
        self.relations = relations

    def solve(self, core_vars: Set[int], core_rels: Set[int], boundary_assignments: Dict[int, Any], time_limit_ms: int = 100) -> Dict[str, Any]:
        """
        Solves the subproblem defined by core_vars and core_rels.
        Variables not in core_vars but in the scopes of core_rels are fixed to their boundary_assignments.
        """
        import time
        t0 = time.monotonic_ns()
        
        model = cp_model.CpModel()
        cp_vars = {}
        
        # We need all variables that appear in core_rels AND core_vars
        involved_vars = set(core_vars)
        for rel_id in core_rels:
            rel = next(r for r in self.relations if r.id == rel_id)
            involved_vars.update(rel.scope)
            
        for v_id in involved_vars:
            domain = self.base_domains[v_id].base_values
            # Create CP variable
            cp_vars[v_id] = model.NewIntVar(min(domain), max(domain), f'v_{v_id}')
            
            # If variable is on the boundary, fix its value
            if v_id not in core_vars:
                if v_id in boundary_assignments:
                    model.Add(cp_vars[v_id] == boundary_assignments[v_id])
                else:
                    # If a boundary variable has no assignment, we fallback to just restricting it to its domain
                    pass
            else:
                # Restrict to domain values if it's not contiguous
                model.AddAllowedAssignments([cp_vars[v_id]], [(val,) for val in domain])

        # Add constraints
        for rel_id in core_rels:
            rel = next(r for r in self.relations if r.id == rel_id)
            if not rel.is_hard:
                continue
            
            scope_vars = [cp_vars[vid] for vid in rel.scope]
            allowed_tuples = list(rel.allowed_tuples)
            model.AddAllowedAssignments(scope_vars, allowed_tuples)

        t_build = time.monotonic_ns() - t0
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
        solver.parameters.num_search_workers = 1 # Determinism
        
        t1 = time.monotonic_ns()
        status = solver.Solve(model)
        t_solve = time.monotonic_ns() - t1
        
        res = {
            "assignment": None,
            "status": status,
            "model_build_time_ns": t_build,
            "solver_time_ns": t_solve
        }
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            assignment = {}
            for v_id in core_vars:
                assignment[v_id] = solver.Value(cp_vars[v_id])
            res["assignment"] = assignment
            
        return res
