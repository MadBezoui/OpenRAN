import sys
import os
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Problem, Constraint
from ortools.sat.python import cp_model

class ExactRepairSolver:
    def __init__(self, problem: Problem):
        self.problem = problem
        
    def extract_core(self, decoded_assignment: Dict[int, Any], hops: int = 0) -> List[int]:
        core_vars = set()
        for cons in self.problem.constraints.values():
            if cons.is_hard:
                tuple_val = tuple(decoded_assignment.get(v_id) for v_id in cons.scope)
                if tuple_val not in cons.allowed_tuples:
                    core_vars.update(cons.scope)
                    
        for _ in range(hops):
            new_vars = set(core_vars)
            for cons in self.problem.constraints.values():
                if any(v in core_vars for v in cons.scope):
                    new_vars.update(cons.scope)
            core_vars = new_vars
            
        return list(core_vars)

    def repair(self, decoded_assignment: Dict[int, Any], core_vars: List[int], time_limit_ms: int = 100) -> Dict[int, Any]:
        if not core_vars:
            return decoded_assignment.copy()
            
        model = cp_model.CpModel()
        
        cp_vars = {}
        for var_id in core_vars:
            var = self.problem.variables[var_id]
            cp_vars[var_id] = model.NewIntVar(0, len(var.domain) - 1, f"var_{var_id}")
            
        for cons in self.problem.constraints.values():
            if not cons.is_hard:
                continue
            
            scope_in_core = [v_id for v_id in cons.scope if v_id in core_vars]
            if not scope_in_core:
                continue
                
            allowed_core_tuples = set()
            for allowed_tuple in cons.allowed_tuples:
                match = True
                for j_idx, j_id in enumerate(cons.scope):
                    if j_id not in core_vars:
                        if allowed_tuple[j_idx] != decoded_assignment[j_id]:
                            match = False
                            break
                if match:
                    core_tuple = []
                    for j_idx, j_id in enumerate(cons.scope):
                        if j_id in core_vars:
                            val = allowed_tuple[j_idx]
                            idx = self.problem.variables[j_id].domain.index(val)
                            core_tuple.append(idx)
                    allowed_core_tuples.add(tuple(core_tuple))
            
            if allowed_core_tuples:
                model.AddAllowedAssignments([cp_vars[v_id] for v_id in cons.scope if v_id in core_vars], list(allowed_core_tuples))
            else:
                model.AddBoolOr([])
                
        objective_terms = []
        for var_id in core_vars:
            var = self.problem.variables[var_id]
            for idx, a in enumerate(var.domain):
                b = model.NewBoolVar(f"var_{var_id}_{idx}")
                model.Add(cp_vars[var_id] == idx).OnlyEnforceIf(b)
                model.Add(cp_vars[var_id] != idx).OnlyEnforceIf(b.Not())
                
                util = var.utilities.get(a, 0.0)
                change_penalty = -0.01 if a != decoded_assignment[var_id] else 0.0
                weight = int((util + change_penalty) * 1000)
                objective_terms.append(weight * b)
                
        model.Maximize(sum(objective_terms))
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
        status = solver.Solve(model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            new_assignment = decoded_assignment.copy()
            for var_id in core_vars:
                idx = solver.Value(cp_vars[var_id])
                new_assignment[var_id] = self.problem.variables[var_id].domain[idx]
            return new_assignment
        else:
            return None
