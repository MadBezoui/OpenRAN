"""Scalability sweep over variable count, multiple seeds."""
import argparse, csv, os
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline

METHODS = [
    ("CP-SAT",           dict(gac=False, continuous=False, repair=True, strategy="fullscope", decode="utility")),
    ("GAC + CP-SAT",     dict(gac=True,  continuous=False, repair=True, strategy="fullscope", decode="utility")),
    ("GAC + expl repair",dict(gac=True,  continuous=False, repair=True, strategy="explanation", decode="utility")),
    ("ConsistXApp expl", dict(gac=True,  continuous=True,  repair=True, strategy="explanation", decode="continuous")),
]
FIELDS = ["method", "n", "seed", "total_time_ns", "outcome", "peak_mem_mb"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="12,30,50,100,200,500")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--deadline_ms", type=int, default=100000)
    ap.add_argument("--out", default="artifacts/raw/scalability_results.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    sizes = [int(x) for x in a.sizes.split(",")]
    f = open(a.out, "w", newline=""); w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    for n in sizes:
        SCENARIO_PRESETS["Scale"] = dict(num_vars=n, domain_size=4,
                                         num_constraints=n, sym_frac=0.5)
        for seed in range(42, 42 + a.seeds):
            V, D, R, _ = generate_static_instance("Scale", seed)
            for name, cfg in METHODS:
                ver = Verifier(D, R)
                m = run_pipeline(V, D, R, f"scale_{n}_{seed}_{name}", ver, cfg, a.deadline_ms)
                mem = 0.0
                w.writerow({"method": name, "n": n, "seed": seed,
                            "total_time_ns": m["total_time_ns"],
                            "outcome": m["outcome"], "peak_mem_mb": round(mem, 1)})
        f.flush(); print(f"size {n} done", flush=True)
    f.close()


if __name__ == "__main__":
    main()
