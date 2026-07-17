"""End-to-end experiment orchestrator.

Writes a reproducibility manifest (versions, host, seeds, parameters), runs
every experiment, and aggregates the raw logs. Use --quick for a fast smoke
run; omit it for the full campaign reported in the paper.

    PYTHONPATH=. python scripts/run_all.py            # full run
    PYTHONPATH=. python scripts/run_all.py --quick    # smoke run
"""
import argparse, json, os, platform, subprocess, sys, time

RAW = "artifacts/raw"; TAB = "artifacts/tables"


def manifest():
    os.makedirs(TAB, exist_ok=True)
    try:
        import ortools
        ortools_v = ortools.__version__
    except Exception:
        ortools_v = "unknown"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                         stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = "unknown"
    man = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "python": sys.version.split()[0],
        "ortools": ortools_v,
        "numpy": __import__("numpy").__version__,
        "pandas": __import__("pandas").__version__,
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "cpu_count": os.cpu_count(),
        "git_commit": commit,
        "seeds": {"static": "42..", "dynamic": "1000..", "temporal": "2000..",
                  "scalability": "42..", "repair_stress": "42.."},
        "continuous_params": {"tau": 1.0, "alpha": 0.0, "beta": 2.0,
                              "epsilon": 1e-12, "max_iter": 100, "tol": 1e-4},
        "cpsat": {"num_search_workers": 1, "time_limit_ms": 100,
                  "assumptions": "reified boolean literals b_j => x_j=xhat_j"},
        "deadline_ms": 100,
    }
    with open(os.path.join(TAB, "manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print("manifest:", json.dumps(man, indent=1))


def sh(cmd):
    print("\n$", cmd, flush=True)
    env = dict(os.environ, PYTHONPATH=".")
    subprocess.check_call(cmd, shell=True, env=env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    manifest()
    seeds = 3 if a.quick else 50
    rep_seeds = 5 if a.quick else 50
    eps = 2 if a.quick else 30
    epk = 20 if a.quick else 100
    sizes = "12,30" if a.quick else "12,30,50,100,200,500"
    sc_seeds = 2 if a.quick else 10

    sh("python scripts/run_sanity.py")
    sh(f"python scripts/run_static.py --seeds {seeds}")
    sh(f"python scripts/run_repair_ablation.py --seeds {rep_seeds}")
    # dynamic incremental suite (truncate then run all 5 scenarios)
    open(os.path.join(RAW, "dynamic_results.csv"), "w").close()
    dyn_eps = 2 if a.quick else 30
    for scn in ["S1", "S2", "S3", "S4", "S5"]:
        sh(f"python scripts/run_incremental.py {scn} 0 {dyn_eps}")
    sh(f"python scripts/run_temporal.py --episodes {eps} --epochs {epk}")
    sh(f"python scripts/run_scalability.py --sizes {sizes} --seeds {sc_seeds}")
    sh("python scripts/aggregate.py")
    print("\nAll experiments complete. See artifacts/tables/summary.json and manifest.json")


if __name__ == "__main__":
    main()
