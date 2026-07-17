"""E3 -- Literature-inspired baselines on the same static scenario suite.

Two additional coordination baselines derived from the O-RAN
conflict-management literature, run on the identical S1-S5 instances:

  * qacm_like : QoS-aware conflict mitigation in the spirit of QACM
    (Wadud et al., IEEE TGCN 2024): maximize the number of xApp action
    variables whose preferred (requested) action is kept, subject to all
    registered hard relations, solved exactly with CP-SAT.
  * nswf_like : cooperative-bargaining resolution in the spirit of the
    game-theoretic CMS (Wadud et al., 2023): maximize a Nash-social-welfare
    surrogate (sum of per-variable log-utilities, discretized), subject to
    the same hard relations.

Both produce verifier-checked decisions with per-instance latency, so the
comparison with ConsistXApp variants is like-for-like. Neither method emits
explanations or repair cores; this is the qualitative differentiator.

Output: artifacts/raw/literature_baselines.csv
"""
import argparse
import csv
import math
import os
import random
import time

from ortools.sat.python import cp_model

from src.generators.static_generator import generate_static_instance
from src.verification.verifier import Verifier

FIELDS = ["method", "scenario", "seed", "total_ms", "verified",
          "preferred_kept_frac", "objective"]

SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]


def solve_with_objective(variables, domains, relations, weights,
                         time_limit_ms=1000):
    """weights: dict var_id -> dict value -> int weight (to maximize)."""
    t0 = time.monotonic_ns()
    model = cp_model.CpModel()
    cp_vars, lits = {}, []
    for v in variables:
        dom = domains[v.id].base_values
        cp_vars[v.id] = model.NewIntVar(min(dom), max(dom), f"v{v.id}")
        model.AddAllowedAssignments([cp_vars[v.id]], [(x,) for x in dom])
    for r in relations:
        if r.is_hard:
            model.AddAllowedAssignments([cp_vars[v] for v in r.scope],
                                        list(r.allowed_tuples))
    terms = []
    for vid, wmap in weights.items():
        for val, wgt in wmap.items():
            b = model.NewBoolVar(f"b_{vid}_{val}")
            model.Add(cp_vars[vid] == val).OnlyEnforceIf(b)
            model.Add(cp_vars[vid] != val).OnlyEnforceIf(b.Not())
            terms.append(wgt * b)
    model.Maximize(sum(terms))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)
    ms = (time.monotonic_ns() - t0) / 1e6
    sol, obj = None, None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sol = {v.id: solver.Value(cp_vars[v.id]) for v in variables}
        obj = solver.ObjectiveValue()
    return sol, ms, obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--scenarios", default=",".join(SCENARIOS))
    ap.add_argument("--out", default="artifacts/raw/literature_baselines.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    write_header = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        for scen in a.scenarios.split(","):
            for seed in range(42, 42 + a.seeds):
                V, D, R, planted = generate_static_instance(scen, seed)
                rng = random.Random(seed + 777)
                # xApp requested (preferred) actions: random proposals,
                # identical for both baselines.
                preferred = {v.id: rng.choice(D[v.id].base_values)
                             for v in V}
                ver = Verifier(D, R)
                # --- QACM-like: maximize #preferred requests kept ---
                weights = {vid: {val: 1} for vid, val in preferred.items()}
                sol, ms, obj = solve_with_objective(V, D, R, weights)
                ok = sol is not None and ver.verify(sol, "lb", "lb")
                kept = (sum(1 for vid in preferred
                            if sol and sol[vid] == preferred[vid])
                        / len(preferred)) if sol else 0.0
                w.writerow({"method": "qacm_like", "scenario": scen,
                            "seed": seed, "total_ms": round(ms, 3),
                            "verified": ok,
                            "preferred_kept_frac": round(kept, 3),
                            "objective": obj})
                # --- NSWF-like: maximize sum of discretized log-utilities ---
                weights = {}
                for v in V:
                    wmap = {}
                    for val in D[v.id].base_values:
                        u = 1.0 if val == preferred[v.id] else \
                            0.25 + 0.5 * rng.random()
                        wmap[val] = int(100 * math.log(1 + 9 * u))
                    weights[v.id] = wmap
                sol, ms, obj = solve_with_objective(V, D, R, weights)
                ok = sol is not None and ver.verify(sol, "lb", "lb")
                kept = (sum(1 for vid in preferred
                            if sol and sol[vid] == preferred[vid])
                        / len(preferred)) if sol else 0.0
                w.writerow({"method": "nswf_like", "scenario": scen,
                            "seed": seed, "total_ms": round(ms, 3),
                            "verified": ok,
                            "preferred_kept_frac": round(kept, 3),
                            "objective": obj})
            f.flush()
            print(f"{scen} done", flush=True)


if __name__ == "__main__":
    main()
