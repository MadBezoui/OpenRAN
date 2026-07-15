import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Variable, Constraint, Problem

def generate_s4_instance(num_cells: int) -> Problem:
    problem = Problem()
    var_id = 0
    cio_domains = [-2, -1, 0, 1, 2]
    ho_domains = [-2, -1, 0, 1, 2]
    
    for cell in range(num_cells):
        v1 = Variable(id=var_id, name=f"cell_{cell}_lb", domain=cio_domains)
        v1.utilities = {a: random.random() for a in cio_domains}
        problem.add_variable(v1)
        var_id += 1
        
        v2 = Variable(id=var_id, name=f"cell_{cell}_mob", domain=ho_domains)
        v2.utilities = {a: random.random() for a in ho_domains}
        problem.add_variable(v2)
        var_id += 1
        
        allowed = set()
        for a in cio_domains:
            for b in ho_domains:
                if abs(a - b) <= 2: # Keep them somewhat aligned
                    allowed.add((a, b))
        
        cons = Constraint(id=cell, name=f"lb_mob_conflict_{cell}", scope=[v1.id, v2.id], allowed_tuples=allowed)
        problem.add_constraint(cons)
        
    return problem
