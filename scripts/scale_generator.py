"""Large-scale near-threshold instance generator for the break-point study.

Generates planted-feasible binary-table instances whose constraint tightness
is close to the satisfiability threshold, so that instances remain SAT by
construction but are no longer trivially loose. Also provides a perturbation
operator for the dynamic amortized study (E2): a fraction of relations is
re-randomized between epochs while preserving the planted assignment.
"""
import random
from typing import Dict, List, Tuple

from src.model.domains import Domain
from src.model.relations import Variable, Relation


def generate_scale_instance(n: int, d: int = 6, c_ratio: float = 2.0,
                            tightness: float = 0.25, neq_frac: float = 0.4,
                            seed: int = 42):
    """Planted-feasible instance with |C| = c_ratio * n binary relations.

    tightness = fraction of random pairs allowed (lower = harder).
    neq_frac  = fraction of constraints that are difference relations.
    """
    rng = random.Random(seed)
    variables = [Variable(id=i, name=f"x{i}") for i in range(n)]
    domains = {i: Domain(list(range(d))) for i in range(n)}
    planted = {i: rng.randrange(d) for i in range(n)}
    relations = []
    num_c = int(c_ratio * n)
    for cid in range(num_c):
        i, j = rng.sample(range(n), 2)
        ta, tb = planted[i], planted[j]
        if rng.random() < neq_frac and ta != tb:
            allowed = {(a, b) for a in range(d) for b in range(d) if a != b}
        else:
            allowed = {(a, b) for a in range(d) for b in range(d)
                       if rng.random() < tightness}
            allowed.add((ta, tb))
        relations.append(Relation(id=cid, name=f"c{cid}", scope=[i, j],
                                  allowed_tuples=allowed, is_hard=True))
    return variables, domains, relations, planted


def perturb_relations(relations, planted, frac: float, d: int, rng,
                      replant_frac: float = 0.0):
    """Re-randomize a fraction of relations, preserving a planted solution.

    With replant_frac > 0, a fraction of the variables is re-planted first
    (their planted value changes), and every relation incident to a
    re-planted variable is repaired to allow the new planted tuple. The
    feasibility anchor therefore drifts through the solution space instead
    of remaining static. Returns the list of modified relation ids.
    """
    moved = []
    if replant_frac > 0.0:
        var_ids = sorted(planted.keys())
        kv = max(1, int(replant_frac * len(var_ids)))
        for vid in rng.sample(var_ids, kv):
            old_val = planted[vid]
            planted[vid] = rng.choice(
                [x for x in range(d) if x != old_val])
        for idx, rel in enumerate(relations):
            i, j = rel.scope
            tup = (planted[i], planted[j])
            if tup not in rel.allowed_tuples:
                rel.allowed_tuples = set(rel.allowed_tuples) | {tup}
                moved.append(rel.id)
    k = max(1, int(frac * len(relations)))
    chosen = rng.sample(range(len(relations)), k)
    for idx in chosen:
        rel = relations[idx]
        i, j = rel.scope
        ta, tb = planted[i], planted[j]
        allowed = {(a, b) for a in range(d) for b in range(d)
                   if rng.random() < 0.25}
        allowed.add((ta, tb))
        rel.allowed_tuples = allowed
    return sorted(set(moved) | {relations[idx].id for idx in chosen})
