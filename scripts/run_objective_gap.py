"""Objective-quality gap: explanation-guided local repair vs exact optimum.

For each scenario instance, xApp requests are drawn as a preferred action per
variable (same generator as the literature baselines). The exact optimum of
the kept-request count subject to all hard relations is computed with CP-SAT
(the QoS-aware baseline objective). The repair-based decision starts from the
preferred vector itself and, when invalid, runs explanation-guided local
repair. The paired difference in kept-request fraction quantifies the price
of local (non-optimizing) repair relative to global optimization.

Output: artifacts/raw/objective_gap.csv
"""
import csv
import os
import random
import time

from src.generators.static_generator import generate_static_instance
from src.verification.verifier import Verifier
from src.repair.engine import RepairEngine
from scripts.run_literature_baselines import solve_with_objective

FIELDS = ["scenario", "seed", "opt_kept", "repair_kept", "repair_ms",
          "opt_ms", "repair_verified"]


def main():
    os.makedirs("artifacts/raw", exist_ok=True)
    with open("artifacts/raw/objective_gap.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for scen in ["S1", "S2", "S3", "S4", "S5"]:
            for seed in range(42, 92):
                V, D, R, _ = generate_static_instance(scen, seed)
                rng = random.Random(seed + 777)
                preferred = {v.id: rng.choice(D[v.id].base_values) for v in V}
                ver = Verifier(D, R)
                # exact optimum of kept-request count
                weights = {vid: {val: 1} for vid, val in preferred.items()}
                sol, opt_ms, _ = solve_with_objective(V, D, R, weights)
                opt_kept = (sum(1 for vid in preferred
                                if sol and sol[vid] == preferred[vid])
                            / len(preferred)) if sol else 0.0
                # repair-based decision from the preferred vector
                t0 = time.monotonic_ns()
                if ver.verify(preferred, "og", "og"):
                    rep, ok = dict(preferred), True
                else:
                    eng = RepairEngine(V, D, R, ver)
                    m = eng.repair("explanation", dict(preferred),
                                   deadline_ms=10000)
                    rep, ok = m.get("assignment"), m["success"]
                rep_ms = (time.monotonic_ns() - t0) / 1e6
                rep_kept = (sum(1 for vid in preferred
                                if rep and rep[vid] == preferred[vid])
                            / len(preferred)) if rep else 0.0
                w.writerow({"scenario": scen, "seed": seed,
                            "opt_kept": round(opt_kept, 4),
                            "repair_kept": round(rep_kept, 4),
                            "repair_ms": round(rep_ms, 3),
                            "opt_ms": round(opt_ms, 3),
                            "repair_verified": ok})
            f.flush()
            print(scen, "done", flush=True)


if __name__ == "__main__":
    main()
