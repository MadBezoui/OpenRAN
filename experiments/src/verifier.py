from typing import Dict, Any
from .models import Problem

class Verifier:
    def __init__(self, problem: Problem):
        self.problem = problem
        
    def verify(self, assignment: Dict[int, Any]) -> bool:
        # Check domain membership
        for var_id, var in self.problem.variables.items():
            if assignment.get(var_id) not in var.domain:
                return False
                
        # Check hard relations
        for cons in self.problem.constraints.values():
            if cons.is_hard:
                tuple_val = tuple(assignment.get(v_id) for v_id in cons.scope)
                if tuple_val not in cons.allowed_tuples:
                    return False
        return True
