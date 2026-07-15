import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Variable, Constraint, Problem

def generate_s3_instance(num_cells: int) -> Problem:
    problem = Problem()
    var_id = 0
    domains = [0, 1] # 0 = Active, 1 = Sleep
    mob_domains = [0, 1, 2] # Handover offsets
    
    for cell in range(num_cells):
        v1 = Variable(id=var_id, name=f"cell_{cell}_mob", domain=mob_domains)
        v1.utilities = {a: random.random() for a in mob_domains}
        problem.add_variable(v1)
        var_id += 1
        
        v2 = Variable(id=var_id, name=f"cell_{cell}_es", domain=domains)
        v2.utilities = {0: 0.2, 1: 0.8} # Preference for sleeping
        problem.add_variable(v2)
        var_id += 1
        
        allowed = set()
        for a in mob_domains:
            for b in domains:
                if b == 1 and a > 0:
                    pass # Invalid: cannot apply aggressive handover offset if cell is going to sleep
                else:
                    allowed.add((a, b))
        
        cons = Constraint(id=cell, name=f"mob_es_conflict_{cell}", scope=[v1.id, v2.id], allowed_tuples=allowed)
        problem.add_constraint(cons)
        
    return problem
