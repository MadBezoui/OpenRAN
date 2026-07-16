import random
from typing import Dict, List, Set, Tuple

from src.model.domains import Domain
from src.model.relations import Variable, Relation

_ACTION_TYPES = ["pc", "ra", "mob", "slot"]

SCENARIO_PRESETS = {
    "S1": dict(num_vars=12, domain_size=3, num_constraints=10, sym_frac=0.7),
    "S2": dict(num_vars=18, domain_size=4, num_constraints=16, sym_frac=0.3),
    "S3": dict(num_vars=20, domain_size=4, num_constraints=18, sym_frac=0.5), # From TODO.md: S3 has 20 vars
    "S4": dict(num_vars=24, domain_size=4, num_constraints=22, sym_frac=0.6), # From TODO.md: S4 has 24 vars
    "S5": dict(num_vars=30, domain_size=4, num_constraints=28, sym_frac=0.5), # From TODO.md: S5 has 30 vars
}

def generate_static_instance(scenario_name: str, seed: int = 42, num_cells: int = 10) -> Tuple[List[Variable], Dict[int, Domain], List[Relation], Dict[int, int]]:
    """
    Generates a feasible synthetic O-RAN instance for a given scenario.
    Returns: variables, domains, relations, planted_solution
    """
    preset = SCENARIO_PRESETS[scenario_name]
    num_vars = preset["num_vars"]
    domain_size = preset["domain_size"]
    num_constraints = preset["num_constraints"]
    sym_frac = preset["sym_frac"]
    
    rng = random.Random(seed)
    
    variables = []
    domains = {}
    relations = []
    
    planted_solution = {}
    
    # 1. Variables
    for i in range(num_vars):
        atype = _ACTION_TYPES[i % len(_ACTION_TYPES)]
        cell = i % num_cells
        var = Variable(id=i, name=f"cell_{cell}_{atype}_{i}")
        variables.append(var)
        
        domain_vals = list(range(domain_size))
        domains[i] = Domain(domain_vals)
        planted_solution[i] = rng.choice(domain_vals)
        
    # 2. Constraints
    for c_id in range(num_constraints):
        if num_vars < 2:
            break
            
        scope = rng.sample(range(num_vars), 2)
        d0 = domains[scope[0]].base_values
        d1 = domains[scope[1]].base_values
        ta, tb = planted_solution[scope[0]], planted_solution[scope[1]]
        
        if rng.random() < sym_frac and ta != tb:
            allowed = {(a, b) for a in d0 for b in d1 if a != b}
        else:
            allowed = {(a, b) for a in d0 for b in d1 if rng.random() < 0.35}
            allowed.add((ta, tb))
            
        rel = Relation(id=c_id, name=f"c_{c_id}", scope=list(scope), allowed_tuples=allowed, is_hard=True)
        relations.append(rel)
        
    return variables, domains, relations, planted_solution
