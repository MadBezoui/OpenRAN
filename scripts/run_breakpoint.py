"""E1 -- One-shot scale frontier: CP-SAT full solve vs GAC + explanation repair.

For each size n, generates near-threshold planted-feasible instances and
measures, in a cold-start (one-shot) setting:
  * CP-SAT: full model build + solve time (reported separately),
  * GAC + explanation repair: observable GAC, deterministic decode, local
    explanation-guided repair, verification.

Output: artifacts/raw/breakpoint_results.csv
"""
import argparse
import csv
import os
import time

from scripts.scale_generator import generate_scale_instance
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.repair.cpsat_adapter import CPSATAdapter

FIELDS = ["method", "n", "d", "c_ratio", "tightness", "seed", "outcome",
          "build_ms", "solve_ms", "total_ms", "verified"]


def run_cpsat_full(variables, domains, relations, verifier, time_limit_ms):
    t0 = time.monotonic_ns()
    adapter = CPSATAdapter(variables, domains, relations)
    res = adapter.solve(core_vars={v.id for v in variables},
                        core_rels={r.id for r in relations},
                        boundary_assignments={},
                        time_limit_ms=time_limit_ms)
    total_ms = (time.monotonic_ns() - t0) / 1e6
    ok = res["assignment"] is not None and verifier.verify(
        res["assignment"], "bp", "bp")
    return {"outcome": "full_solve" if ok else "failed",
            "build_ms": res["model_build_time_ns"] / 1e6,
            "solve_ms": res["solver_time_ns"] / 1e6,
            "total_ms": total_ms, "verified": ok}


def run_gac_repair(variables, domains, relations, verifier, deadline_ms):
    cfg = dict(gac=True, continuous=False, repair=True,
               strategy="explanation", decode="utility")
    m = run_pipeline(variables, domains, relations, "bp", verifier, cfg,
                     deadline_ms)
    return {"outcome": m["outcome"],
            "build_ms": m["propagation_time_ns"] / 1e6,
            "solve_ms": m["repair_time_ns"] / 1e6,
            "total_ms": m["total_time_ns"] / 1e6,
            "verified": m["executed_verified"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="30,100,300,600,1000")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--d", type=int, default=6)
    ap.add_argument("--c_ratio", type=float, default=2.0)
    ap.add_argument("--tightness", type=float, default=0.25)
    ap.add_argument("--time_limit_ms", type=int, default=10000)
    ap.add_argument("--out", default="artifacts/raw/breakpoint_results.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    sizes = [int(x) for x in a.sizes.split(",")]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for n in sizes:
            for seed in range(42, 42 + a.seeds):
                V, D, R, _ = generate_scale_instance(
                    n, a.d, a.c_ratio, a.tightness, seed=seed)
                for name, fn in [("CP-SAT", run_cpsat_full),
                                 ("GAC + expl repair", run_gac_repair)]:
                    ver = Verifier(D, R)
                    rec = fn(V, D, R, ver, a.time_limit_ms)
                    rec.update({"method": name, "n": n, "d": a.d,
                                "c_ratio": a.c_ratio,
                                "tightness": a.tightness, "seed": seed})
                    rec["build_ms"] = round(rec["build_ms"], 3)
                    rec["solve_ms"] = round(rec["solve_ms"], 3)
                    rec["total_ms"] = round(rec["total_ms"], 3)
                    w.writerow(rec)
                f.flush()
            print(f"n={n} done", flush=True)


if __name__ == "__main__":
    main()
