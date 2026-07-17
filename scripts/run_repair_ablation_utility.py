"""Repair-strategy ablation on the OPERATIONAL pipeline candidates.

Identical to run_repair_ablation.py except that repair-triggering candidates
are produced by the deterministic utility decode actually used by the
ConsistXApp pipeline (not by the continuous decode). Every strategy repairs
the same candidate and boundary on each triggering instance.

Output: artifacts/raw/repair_ablation_utility.csv
"""
import argparse
import csv
import os

from src.generators.static_generator import generate_static_instance
from src.generators.stress_generator import generate_stress_instance
from src.verification.verifier import Verifier
from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.propagation.gac import GAC
from src.repair.engine import RepairEngine

STRATEGIES = ["violated0", "radius0", "radius1", "radius2",
              "frontier", "explanation", "assumption", "fullscope"]
FIELDS = ["suite", "instance", "seed", "num_variables", "strategy", "success",
          "status", "initial_core_size", "final_core_size", "expansions",
          "used_explanation", "used_assumption_core", "used_frontier",
          "boundary_released", "gac_time_ns", "cpsat_time_ns",
          "total_time_ns", "full_scope_required"]


def utility_decode(V, D, R):
    """The pipeline's deterministic decode over GAC-filtered domains."""
    filtered = {v.id: FilteredDomain(D[v.id]) for v in V}
    active = [ActiveRelation(r) for r in R]
    if not GAC(V, filtered, active).enforce():
        return None
    return {v.id: sorted(filtered[v.id].active_values)[0]
            if filtered[v.id].active_values else D[v.id].base_values[0]
            for v in V}


def run_instance(suite, inst, seed, V, D, R, w, budget):
    ver = Verifier(D, R)
    dec = utility_decode(V, D, R)
    if dec is None or ver.verify(dec, "c", "c"):
        return 0
    eng = RepairEngine(V, D, R, ver)
    for strat in STRATEGIES:
        m = eng.repair(strat, dict(dec), deadline_ms=budget)
        w.writerow({"suite": suite, "instance": inst, "seed": seed,
                    "num_variables": len(V), "strategy": strat,
                    "success": m["success"], "status": m["status"],
                    "initial_core_size": m["initial_core_size"],
                    "final_core_size": m["final_core_size"],
                    "expansions": m["expansions"],
                    "used_explanation": m["used_explanation"],
                    "used_assumption_core": m["used_assumption_core"],
                    "used_frontier": m["used_frontier"],
                    "boundary_released": m["boundary_released"],
                    "gac_time_ns": m["gac_time_ns"],
                    "cpsat_time_ns": m["cpsat_time_ns"],
                    "total_time_ns": m["total_time_ns"],
                    "full_scope_required": m["full_scope_required"]})
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--budget", type=int, default=10000)
    ap.add_argument("--suite", default="standard,stress")
    ap.add_argument("--out",
                    default="artifacts/raw/repair_ablation_utility.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    write_header = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        n_trig = 0
        if "standard" in a.suite:
            for scen in ["S1", "S2", "S3", "S4", "S5"]:
                for seed in range(42, 42 + a.seeds):
                    V, D, R, _ = generate_static_instance(scen, seed)
                    n_trig += run_instance("standard", scen, seed, V, D, R,
                                           w, a.budget)
                f.flush()
                print(scen, "done", flush=True)
        if "stress" in a.suite:
            import random
            for seed in range(42, 42 + a.seeds):
                V, D, R, planted = generate_stress_instance(24, 4, 34, seed)
                ver = Verifier(D, R)
                rng = random.Random(seed * 7)
                dec = dict(planted)
                for vid in rng.sample([v.id for v in V], 3):
                    dec[vid] = rng.choice(
                        [x for x in range(4) if x != planted[vid]])
                if ver.verify(dec, "c", "c"):
                    continue
                eng = RepairEngine(V, D, R, ver)
                for strat in STRATEGIES:
                    m = eng.repair(strat, dict(dec), deadline_ms=a.budget)
                    w.writerow({"suite": "stress", "instance": "stress24",
                                "seed": seed, "num_variables": len(V),
                                "strategy": strat, "success": m["success"],
                                "status": m["status"],
                                "initial_core_size": m["initial_core_size"],
                                "final_core_size": m["final_core_size"],
                                "expansions": m["expansions"],
                                "used_explanation": m["used_explanation"],
                                "used_assumption_core": m["used_assumption_core"],
                                "used_frontier": m["used_frontier"],
                                "boundary_released": m["boundary_released"],
                                "gac_time_ns": m["gac_time_ns"],
                                "cpsat_time_ns": m["cpsat_time_ns"],
                                "total_time_ns": m["total_time_ns"],
                                "full_scope_required": m["full_scope_required"]})
                n_trig += 1
            f.flush()
            print("stress done", flush=True)
        print("triggering instances:", n_trig)


if __name__ == "__main__":
    main()
