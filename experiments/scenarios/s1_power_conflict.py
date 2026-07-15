import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Variable, Constraint, Problem

def generate_s1_instance(num_cells: int, num_xapps: int) -> Problem:
    problem = Problem()
    
    var_id = 0
    domains = [0, 1, 2]
    
    for cell in range(num_cells):
        v1 = Variable(id=var_id, name=f"cell_{cell}_cov", domain=domains)
        v1.utilities = {0: 0.1, 1: 0.5, 2: 0.9}
        problem.add_variable(v1)
        var_id += 1
        
        v2 = Variable(id=var_id, name=f"cell_{cell}_es", domain=domains)
        v2.utilities = {0: 0.9, 1: 0.5, 2: 0.1}
        problem.add_variable(v2)
        var_id += 1
        
        allowed = set()
        for a in domains:
            allowed.add((a, a))
        
        cons = Constraint(id=cell, name=f"direct_conflict_{cell}", scope=[v1.id, v2.id], allowed_tuples=allowed)
        problem.add_constraint(cons)
        
    return problem
