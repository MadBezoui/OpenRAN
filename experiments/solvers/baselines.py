import random
import time
from typing import Dict, Any, Tuple
from ortools.sat.python import cp_model
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Problem
from src.verifier import Verifier

def solve_uncoordinated(problem: Problem) -> Dict[int, Any]:
    assignment = {}
    for var_id, var in problem.variables.items():
        best_a = max(var.domain, key=lambda a: var.utilities.get(a, 0.0))
        assignment[var_id] = best_a
    return assignment

def solve_static_priority(problem: Problem) -> Dict[int, Any]:
    sorted_vars = sorted(problem.variables.values(), key=lambda v: v.priority, reverse=True)
    assignment = {}
    
    for var in sorted_vars:
        best_a = None
        best_util = -float('inf')
        for a in var.domain:
            temp_assignment = assignment.copy()
            temp_assignment[var.id] = a
            
            valid = True
            for cons in problem.constraints.values():
                if cons.is_hard and all(v in temp_assignment for v in cons.scope):
                    tuple_val = tuple(temp_assignment[v] for v in cons.scope)
                    if tuple_val not in cons.allowed_tuples:
                        valid = False
                        break
            if valid:
                util = var.utilities.get(a, 0.0)
                if util > best_util:
                    best_util = util
                    best_a = a
        if best_a is not None:
            assignment[var.id] = best_a
        else:
            assignment[var.id] = random.choice(var.domain)
            
    return assignment

def solve_random_feasible(problem: Problem, max_attempts=1000) -> Dict[int, Any]:
    verifier = Verifier(problem)
    for _ in range(max_attempts):
        assignment = {}
        for var_id, var in problem.variables.items():
            assignment[var_id] = random.choice(var.domain)
        if verifier.verify(assignment):
            return assignment
    return solve_uncoordinated(problem)

def solve_cp_sat(problem: Problem, time_limit_ms=200) -> Dict[int, Any]:
    model = cp_model.CpModel()
    cp_vars = {}
    
    for var_id, var in problem.variables.items():
        cp_vars[var_id] = model.NewIntVar(0, len(var.domain) - 1, f"var_{var_id}")
        
    for cons in problem.constraints.values():
        if not cons.is_hard:
            continue
        
        allowed_tuples = []
        for allowed_tuple in cons.allowed_tuples:
            t = []
            for j_idx, j_id in enumerate(cons.scope):
                val = allowed_tuple[j_idx]
                idx = problem.variables[j_id].domain.index(val)
                t.append(idx)
            allowed_tuples.append(tuple(t))
            
        if allowed_tuples:
            model.AddAllowedAssignments([cp_vars[v_id] for v_id in cons.scope], allowed_tuples)
        else:
            model.AddBoolOr([])
            
    objective_terms = []
    for var_id, var in problem.variables.items():
        for idx, a in enumerate(var.domain):
            b = model.NewBoolVar(f"var_{var_id}_{idx}")
            model.Add(cp_vars[var_id] == idx).OnlyEnforceIf(b)
            model.Add(cp_vars[var_id] != idx).OnlyEnforceIf(b.Not())
            
            util = var.utilities.get(a, 0.0)
            objective_terms.append(int(util * 1000) * b)
            
    model.Maximize(sum(objective_terms))
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
    status = solver.Solve(model)
    
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        assignment = {}
        for var_id in problem.variables:
            idx = solver.Value(cp_vars[var_id])
            assignment[var_id] = problem.variables[var_id].domain[idx]
        return assignment
    else:
        return solve_uncoordinated(problem)
