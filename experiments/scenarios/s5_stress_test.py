import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Variable, Constraint, Problem

def generate_s5_instance(num_cells: int) -> Problem:
    problem = Problem()
    var_id = 0
    domains = [0, 1, 2]
    
    # Stress test: generate highly coupled graph
    vars = []
    for i in range(num_cells * 5): # 5 xapps per cell
        v = Variable(id=var_id, name=f"var_{var_id}", domain=domains)
        v.utilities = {a: random.random() for a in domains}
        problem.add_variable(v)
        vars.append(v)
        var_id += 1
        
    # Dense constraints
    c_id = 0
    for i in range(len(vars)):
        for j in range(i+1, min(i+4, len(vars))):
            allowed = set()
            for a in domains:
                for b in domains:
                    if random.random() > 0.4:
                        allowed.add((a, b))
            cons = Constraint(id=c_id, name=f"stress_cons_{c_id}", scope=[vars[i].id, vars[j].id], allowed_tuples=allowed)
            problem.add_constraint(cons)
            c_id += 1
            
    return problem
