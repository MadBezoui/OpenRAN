"""
Repair-stress instance generator.

Produces planted-feasible instances that nevertheless force the exact-repair
stage to *expand* its core: a fraction of the constraints are equality-biased,
allowed = {(a,a) for a in D} union {(p_i,p_j)} where (p_i,p_j) is the planted
pair. When the continuous decode assigns two coupled variables unequal,
non-planted values, a repair core restricted to the violated scope (with the
coupled neighbour fixed to its decoded value) is infeasible, so the neighbour
must be released. Chaining these constraints yields repairs whose resolution
requires releasing several boundary variables, which is exactly the regime in
which explanation-guided / assumption-core expansion can differ from blind
adjacency (frontier) or fixed-radius expansion.
"""
import random
from typing import Dict, List, Tuple
from src.model.domains import Domain
from src.model.relations import Variable, Relation


def generate_stress_instance(num_vars: int, domain_size: int,
                             num_constraints: int, seed: int = 42,
                             eq_frac: float = 0.7
                             ) -> Tuple[List[Variable], Dict[int, Domain], List[Relation], Dict[int, int]]:
    rng = random.Random(seed)
    variables, domains, planted = [], {}, {}
    for i in range(num_vars):
        variables.append(Variable(id=i, name=f"cell_{i % 10}_pc_{i}"))
        domains[i] = Domain(list(range(domain_size)))
        planted[i] = rng.choice(range(domain_size))

    relations = []
    # A backbone chain guarantees a connected equality-biased structure.
    order = list(range(num_vars))
    rng.shuffle(order)
    cid = 0
    for k in range(num_vars - 1):
        a, b = order[k], order[k + 1]
        allowed = {(v, v) for v in range(domain_size)}
        allowed.add((planted[a], planted[b]))
        relations.append(Relation(id=cid, name=f"eq_{cid}", scope=[a, b],
                                   allowed_tuples=allowed, is_hard=True))
        cid += 1

    while cid < num_constraints and num_vars >= 2:
        a, b = rng.sample(range(num_vars), 2)
        if rng.random() < eq_frac:
            allowed = {(v, v) for v in range(domain_size)}
            allowed.add((planted[a], planted[b]))
        else:
            allowed = {(x, y) for x in range(domain_size) for y in range(domain_size)
                       if rng.random() < 0.4}
            allowed.add((planted[a], planted[b]))
        relations.append(Relation(id=cid, name=f"c_{cid}", scope=[a, b],
                                   allowed_tuples=allowed, is_hard=True))
        cid += 1
    return variables, domains, relations, planted
