"""E2 -- Dynamic amortized comparison at scale.

Simulates episodes of consecutive decision epochs where a fraction delta of
the relations changes between epochs (planted solution preserved, so every
epoch is SAT). Three per-epoch strategies are compared on identical episodes:

  * cpsat_rebuild : build the full CP-SAT model from scratch and solve;
  * cpsat_hint    : same, but the previous verified solution is added as a
                    solution hint (warm start);
  * incr_repair   : keep the previous verified solution; verify it under the
                    new model; if violated, run explanation-guided local
                    repair seeded from the violated relations only.

The point of the experiment: rebuild-based methods pay O(model) work per
epoch even when the change is local, while incremental repair pays O(change).

Output: artifacts/raw/dynamic_scale_results.csv
"""
import argparse
import csv
import os
import random
import time

from ortools.sat.python import cp_model

from scripts.scale_generator import generate_scale_instance, perturb_relations
from src.verification.verifier import Verifier
from src.repair.engine import RepairEngine

FIELDS = ["method", "n", "delta", "seed", "epoch", "changed_rels",
          "violated_rels", "total_ms", "build_ms", "solve_ms", "verified"]


def solve_full_cpsat(variables, domains, relations, hint=None,
                     time_limit_ms=10000):
    t0 = time.monotonic_ns()
    model = cp_model.CpModel()
    cp_vars = {}
    for v in variables:
        dom = domains[v.id].base_values
        cp_vars[v.id] = model.NewIntVar(min(dom), max(dom), f"v{v.id}")
    for r in relations:
        if r.is_hard:
            model.AddAllowedAssignments([cp_vars[v] for v in r.scope],
                                        list(r.allowed_tuples))
    if hint:
        for vid, val in hint.items():
            model.AddHint(cp_vars[vid], val)
    t_build = time.monotonic_ns() - t0
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_ms / 1000.0
    solver.parameters.num_search_workers = 1
    t1 = time.monotonic_ns()
    status = solver.Solve(model)
    t_solve = time.monotonic_ns() - t1
    total_ms = (time.monotonic_ns() - t0) / 1e6
    sol = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sol = {v.id: solver.Value(cp_vars[v.id]) for v in variables}
    return sol, total_ms, t_build / 1e6, t_solve / 1e6


def violated_relations(solution, relations):
    out = []
    for r in relations:
        if not r.is_hard:
            continue
        tup = tuple(solution[v] for v in r.scope)
        if not r.is_allowed(tup):
            out.append(r.id)
    return out


def incr_repair_epoch(variables, domains, relations, verifier, prev_solution,
                      deadline_ms=10000):
    t0 = time.monotonic_ns()
    viol = violated_relations(prev_solution, relations)
    if not viol:
        total_ms = (time.monotonic_ns() - t0) / 1e6
        return prev_solution, total_ms, 0, True
    engine = RepairEngine(variables, domains, relations, verifier)
    res = engine.repair("explanation", dict(prev_solution),
                        context_id="dyn", deadline_ms=deadline_ms)
    total_ms = (time.monotonic_ns() - t0) / 1e6
    sol = res.get("assignment")
    ok = sol is not None
    return (sol if ok else prev_solution), total_ms, len(viol), ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="100,300,600,1000")
    ap.add_argument("--deltas", default="0.02")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--d", type=int, default=6)
    ap.add_argument("--replant", type=float, default=0.0)
    ap.add_argument("--out", default="artifacts/raw/dynamic_scale_results.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    sizes = [int(x) for x in a.sizes.split(",")]
    deltas = [float(x) for x in a.deltas.split(",")]
    write_header = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        for n in sizes:
            for delta in deltas:
                for seed in range(42, 42 + a.seeds):
                    V, D, R, planted = generate_scale_instance(
                        n, a.d, 2.0, 0.25, seed=seed)
                    rng = random.Random(seed * 7919)
                    # initial solve shared by all methods (epoch 0, excluded)
                    base_sol, _, _, _ = solve_full_cpsat(V, D, R)
                    assert base_sol is not None
                    prev = {m: dict(base_sol) for m in
                            ("cpsat_rebuild", "cpsat_hint", "incr_repair")}
                    for ep in range(1, a.epochs + 1):
                        changed = perturb_relations(
                            R, planted, delta, a.d, rng,
                            replant_frac=a.replant)
                        ver = Verifier(D, R)
                        # rebuild
                        sol, ms, bms, sms = solve_full_cpsat(V, D, R)
                        ok = sol is not None and ver.verify(sol, "d", "d")
                        w.writerow({"method": "cpsat_rebuild", "n": n,
                                    "delta": delta, "seed": seed, "epoch": ep,
                                    "changed_rels": len(changed),
                                    "violated_rels": -1,
                                    "total_ms": round(ms, 3),
                                    "build_ms": round(bms, 3),
                                    "solve_ms": round(sms, 3),
                                    "verified": ok})
                        if ok:
                            prev["cpsat_rebuild"] = sol
                        # hint
                        sol, ms, bms, sms = solve_full_cpsat(V, D, R,
                                                   hint=prev["cpsat_hint"])
                        ok = sol is not None and ver.verify(sol, "d", "d")
                        w.writerow({"method": "cpsat_hint", "n": n,
                                    "delta": delta, "seed": seed, "epoch": ep,
                                    "changed_rels": len(changed),
                                    "violated_rels": -1,
                                    "total_ms": round(ms, 3),
                                    "build_ms": round(bms, 3),
                                    "solve_ms": round(sms, 3),
                                    "verified": ok})
                        if ok:
                            prev["cpsat_hint"] = sol
                        # incremental local repair
                        sol, ms, nviol, ok = incr_repair_epoch(
                            V, D, R, ver, prev["incr_repair"])
                        ok = ok and ver.verify(sol, "d", "d")
                        w.writerow({"method": "incr_repair", "n": n,
                                    "delta": delta, "seed": seed, "epoch": ep,
                                    "changed_rels": len(changed),
                                    "violated_rels": nviol,
                                    "total_ms": round(ms, 3),
                                    "build_ms": 0.0, "solve_ms": 0.0,
                                    "verified": ok})
                        if ok:
                            prev["incr_repair"] = sol
                    f.flush()
                print(f"n={n} delta={delta} done", flush=True)


if __name__ == "__main__":
    main()
