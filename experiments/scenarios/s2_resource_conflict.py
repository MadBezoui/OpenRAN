import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Variable, Constraint, Problem

def generate_s2_instance(num_cells: int) -> Problem:
    problem = Problem()
    var_id = 0
    domains = [0, 1, 2, 3]
    for cell in range(num_cells):
        v1 = Variable(id=var_id, name=f"cell_{cell}_pc", domain=domains)
        v1.utilities = {a: random.random() for a in domains}
        problem.add_variable(v1)
        var_id += 1
        
        v2 = Variable(id=var_id, name=f"cell_{cell}_ra", domain=domains)
        v2.utilities = {a: random.random() for a in domains}
        problem.add_variable(v2)
        var_id += 1
        
        allowed = set()
        for a in domains:
            for b in domains:
                if a + b <= 3:
                    allowed.add((a, b))
        
        cons = Constraint(id=cell, name=f"indirect_conflict_{cell}", scope=[v1.id, v2.id], allowed_tuples=allowed)
        problem.add_constraint(cons)
        
    return problem
