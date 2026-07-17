"""E4 -- Verifier validation gates G1-G4 (Protocole section 6).

G1  Exhaustive oracle: on small instances, enumerate every assignment and
    compare the production Verifier against an independently coded oracle.
G2  Second verifier with no shared evaluation code: a declarative CP-SAT
    model re-built from the instance JSON; agreement checked on sampled
    assignments (triple agreement oracle / V1 / V2).
G3  Property-based testing: bulk randomized triples (instance, assignment,
    transformation) checking determinism, constraint-permutation invariance,
    variable-renaming invariance, and explicit rejection of malformed input.
G4  Mutation testing: mutations of planted-feasible solutions labelled by the
    oracle; the verifier must classify 100% of them identically.

Output: artifacts/tables/verifier_validation.json
"""
import itertools
import json
import os
import random
import time

from ortools.sat.python import cp_model

from src.model.domains import Domain
from src.model.relations import Variable, Relation
from src.verification.verifier import Verifier


# --------------------------------------------------------------------------
# Independent oracle (deliberately different code path from Verifier)
# --------------------------------------------------------------------------
def oracle_feasible(assignment, domains, relations):
    """Straight-line evaluation, no shared helpers with src/."""
    for vid, dom in domains.items():
        if vid not in assignment:
            return False
        if assignment[vid] not in dom.base_values:
            return False
    for rel in relations:
        if not rel.is_hard:
            continue
        values = []
        for vid in rel.scope:
            if vid not in assignment:
                return False
            values.append(assignment[vid])
        if tuple(values) not in rel.allowed_tuples:
            return False
    return True


# --------------------------------------------------------------------------
# Second verifier: declarative CP-SAT, rebuilt from a JSON-normalized form
# --------------------------------------------------------------------------
def cpsat_verify(assignment, instance_json):
    inst = json.loads(instance_json)  # independent parser step
    model = cp_model.CpModel()
    cp_vars = {}
    for v in inst["variables"]:
        vid = v["id"]
        dom = v["domain"]
        if vid not in assignment or assignment[vid] not in dom:
            return False
        cp_vars[vid] = model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(dom), f"v{vid}")
        model.Add(cp_vars[vid] == assignment[vid])
    for r in inst["relations"]:
        if not r["is_hard"]:
            continue
        model.AddAllowedAssignments([cp_vars[v] for v in r["scope"]],
                                    [tuple(t) for t in r["allowed"]])
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    return solver.Solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def instance_to_json(domains, relations):
    return json.dumps({
        "variables": [{"id": vid, "domain": list(dom.base_values)}
                      for vid, dom in domains.items()],
        "relations": [{"scope": r.scope, "allowed": [list(t) for t in
                                                     r.allowed_tuples],
                       "is_hard": r.is_hard} for r in relations],
    })


def random_instance(rng, n, d, num_c=None, tightness=0.5):
    variables = [Variable(id=i, name=f"x{i}") for i in range(n)]
    domains = {i: Domain(list(range(d))) for i in range(n)}
    num_c = num_c if num_c is not None else max(1, n)
    relations = []
    for cid in range(num_c):
        scope = rng.sample(range(n), min(2, n))
        allowed = {t for t in itertools.product(*(range(d) for _ in scope))
                   if rng.random() < tightness}
        relations.append(Relation(id=cid, name=f"c{cid}", scope=scope,
                                  allowed_tuples=allowed, is_hard=True))
    return variables, domains, relations


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gates", default="G1,G2,G3,G4")
    ap.add_argument("--g3_trials", type=int, default=100_000)
    ap.add_argument("--out", default="artifacts/tables/verifier_validation.json")
    args = ap.parse_args()
    gates = set(args.gates.split(","))
    rng = random.Random(20260716)
    report = {}

    # ---------------- G1: exhaustive oracle ----------------
    if "G1" in gates:
      t0 = time.time()
      divergences = 0
      assignments_checked = 0
      instances = 0
      for n in range(2, 7):
          for d in (2, 3):
              for _ in range(50):
                  V, D, R = random_instance(rng, n, d,
                                            num_c=rng.randint(1, 2 * n),
                                            tightness=rng.uniform(0.2, 0.8))
                  ver = Verifier(D, R)
                  for combo in itertools.product(range(d), repeat=n):
                      asg = dict(enumerate(combo))
                      expected = oracle_feasible(asg, D, R)
                      observed = ver.verify(asg, "c", "c")
                      assignments_checked += 1
                      if expected != observed:
                          divergences += 1
                  instances += 1
      report["G1_exhaustive"] = {
          "instances": instances, "assignments": assignments_checked,
          "divergences": divergences, "time_s": round(time.time() - t0, 1),
          "pass": divergences == 0}

    # ---------------- G2: CP-SAT second verifier ----------------
    if "G2" in gates:
      t0 = time.time()
      div_v2 = 0
      checked = 0
      for _ in range(150):
          n, d = rng.randint(2, 6), rng.choice((2, 3))
          V, D, R = random_instance(rng, n, d,
                                    num_c=rng.randint(1, 2 * n),
                                    tightness=rng.uniform(0.2, 0.8))
          ver = Verifier(D, R)
          ijson = instance_to_json(D, R)
          for _ in range(12):
              asg = {i: rng.randrange(d) for i in range(n)}
              a = oracle_feasible(asg, D, R)
              b = ver.verify(asg, "c", "c")
              c = cpsat_verify(asg, ijson)
              checked += 1
              if not (a == b == c):
                  div_v2 += 1
      report["G2_triple_agreement"] = {
          "assignments": checked, "divergences": div_v2,
          "time_s": round(time.time() - t0, 1), "pass": div_v2 == 0}

    # ---------------- G3: property-based bulk ----------------
    if "G3" in gates:
      t0 = time.time()
      n_props = 0
      failures = []
      for trial in range(args.g3_trials):
          n, d = rng.randint(2, 5), rng.choice((2, 3, 4))
          V, D, R = random_instance(rng, n, d, num_c=rng.randint(1, n + 2),
                                    tightness=rng.uniform(0.1, 0.9))
          ver = Verifier(D, R)
          asg = {i: rng.randrange(d) for i in range(n)}
          r1 = ver.verify(asg, "c", "c")
          # determinism
          if r1 != ver.verify(asg, "c", "c"):
              failures.append(("determinism", trial))
          # constraint-permutation invariance
          R2 = list(R)
          rng.shuffle(R2)
          if r1 != Verifier(D, R2).verify(asg, "c", "c"):
              failures.append(("permutation", trial))
          # oracle agreement
          if r1 != oracle_feasible(asg, D, R):
              failures.append(("oracle", trial))
          # out-of-domain rejection
          bad = dict(asg)
          bad[0] = d + 5
          if ver.verify(bad, "c", "c"):
              failures.append(("out_of_domain", trial))
          # missing-variable rejection
          bad2 = dict(asg)
          del bad2[n - 1]
          if ver.verify(bad2, "c", "c"):
              failures.append(("missing_var", trial))
          # stale-context rejection
          if ver.verify(asg, "c", "other"):
              failures.append(("context", trial))
          n_props += 6
      # variable-renaming invariance on a smaller structured set
      for trial in range(2_000):
          n, d = rng.randint(2, 5), rng.choice((2, 3))
          V, D, R = random_instance(rng, n, d, num_c=n, tightness=0.5)
          asg = {i: rng.randrange(d) for i in range(n)}
          r1 = Verifier(D, R).verify(asg, "c", "c")
          perm = list(range(n))
          rng.shuffle(perm)
          remap = {old: new for old, new in enumerate(perm)}
          D2 = {remap[i]: D[i] for i in D}
          R2 = [Relation(id=r.id, name=r.name,
                         scope=[remap[v] for v in r.scope],
                         allowed_tuples=set(r.allowed_tuples), is_hard=r.is_hard)
                for r in R]
          asg2 = {remap[i]: asg[i] for i in asg}
          if r1 != Verifier(D2, R2).verify(asg2, "c", "c"):
              failures.append(("renaming", trial))
          n_props += 1
      report["G3_property_based"] = {
          "properties_checked": n_props, "failures": len(failures),
          "failure_kinds": sorted({k for k, _ in failures}),
          "time_s": round(time.time() - t0, 1), "pass": not failures}

    # ---------------- G4: mutation testing ----------------
    if "G4" in gates:
      t0 = time.time()
      total_mut = 0
      misclassified = 0
      invalid_mutants = 0
      for _ in range(4000):
          n, d = rng.randint(3, 7), rng.choice((2, 3, 4))
          # planted-feasible instance
          planted = {i: rng.randrange(d) for i in range(n)}
          V = [Variable(id=i, name=f"x{i}") for i in range(n)]
          D = {i: Domain(list(range(d))) for i in range(n)}
          R = []
          for cid in range(n):
              scope = rng.sample(range(n), 2)
              allowed = {t for t in itertools.product(range(d), range(d))
                         if rng.random() < 0.4}
              allowed.add((planted[scope[0]], planted[scope[1]]))
              R.append(Relation(id=cid, name=f"c{cid}", scope=scope,
                                allowed_tuples=allowed, is_hard=True))
          ver = Verifier(D, R)
          assert ver.verify(planted, "c", "c")
          mutants = []
          m1 = dict(planted)                       # single value change
          m1[rng.randrange(n)] = rng.randrange(d)
          mutants.append(m1)
          m2 = dict(planted)                       # out-of-domain value
          m2[rng.randrange(n)] = d + 3
          mutants.append(m2)
          m3 = dict(planted)                       # remove an action
          del m3[rng.randrange(n)]
          mutants.append(m3)
          m4 = {i: rng.randrange(d) for i in range(n)}  # full scramble
          mutants.append(m4)
          for mut in mutants:
              expected = oracle_feasible(mut, D, R)
              observed = ver.verify(mut, "c", "c")
              total_mut += 1
              if not expected:
                  invalid_mutants += 1
              if expected != observed:
                  misclassified += 1
      report["G4_mutation"] = {
          "mutants": total_mut, "oracle_invalid": invalid_mutants,
          "misclassified": misclassified,
          "time_s": round(time.time() - t0, 1), "pass": misclassified == 0}

    report["gates_pass"] = all(v["pass"] for k, v in report.items()
                                   if isinstance(v, dict))
    os.makedirs("artifacts/tables", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
