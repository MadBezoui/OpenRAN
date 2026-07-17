"""Repair-strategy ablation on identical repair-triggering decodes.

For each instance (standard scenarios and repair-stress instances) we compute a
GAC + continuous decode. On the decodes that fail verification we run EVERY
repair strategy on the SAME decoded candidate and boundary, each with a full
repair budget, recording the complete per-repair audit. This isolates the
contribution of core construction/expansion from the rest of the pipeline and
lets us verify repair-feasibility monotonicity across nested cores.
"""
import argparse, csv, os, random
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.generators.stress_generator import generate_stress_instance
from src.verification.verifier import Verifier
from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.propagation.gac import GAC
from src.continuous.consensus import ContinuousConsensus
from src.continuous.decoder import Decoder
from src.repair.engine import RepairEngine

STRATEGIES = ["violated0", "radius0", "radius1", "radius2",
              "frontier", "explanation", "assumption", "fullscope"]
FIELDS = ["suite", "instance", "seed", "num_variables", "strategy", "success",
          "status", "initial_core_size", "final_core_size", "expansions",
          "used_explanation", "used_assumption_core", "used_frontier",
          "boundary_released", "gac_time_ns", "cpsat_time_ns", "total_time_ns",
          "full_scope_required"]


def decode(V, D, R):
    filtered = {v.id: FilteredDomain(D[v.id]) for v in V}
    active = [ActiveRelation(r) for r in R]
    if not GAC(V, filtered, active).enforce():
        return None
    cons = ContinuousConsensus(V, filtered, active)
    cons.solve()
    return Decoder(cons).decode()


def run_instance(suite, inst, seed, V, D, R, w, budget):
    ver = Verifier(D, R)
    dec = decode(V, D, R)
    if dec is None or ver.verify(dec, "c", "c"):
        return 0
    eng = RepairEngine(V, D, R, ver)
    for strat in STRATEGIES:
        m = eng.repair(strat, dec, deadline_ms=budget)
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
                    "gac_time_ns": m["gac_time_ns"], "cpsat_time_ns": m["cpsat_time_ns"],
                    "total_time_ns": m["total_time_ns"],
                    "full_scope_required": m["full_scope_required"]})
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--budget_ms", type=int, default=100)
    ap.add_argument("--out", default="artifacts/raw/repair_ablation.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    f = open(a.out, "w", newline=""); w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    n = 0
    for scenario in ["S1", "S2", "S3", "S4", "S5"]:
        for seed in range(42, 42 + a.seeds):
            V, D, R, _ = generate_static_instance(scenario, seed)
            n += run_instance("standard", scenario, seed, V, D, R, w, a.budget_ms)
        f.flush(); print(f"standard {scenario} done", flush=True)
    for seed in range(42, 42 + a.seeds):
        V, D, R, planted = generate_stress_instance(24, 4, 34, seed)
        ver = Verifier(D, R)
        rng = random.Random(seed * 7)
        dec = dict(planted)
        for vid in rng.sample([v.id for v in V], 3):
            dec[vid] = rng.choice([x for x in range(4) if x != planted[vid]])
        if ver.verify(dec, "c", "c"):
            continue
        eng = RepairEngine(V, D, R, ver)
        for strat in STRATEGIES:
            m = eng.repair(strat, dec, deadline_ms=a.budget_ms)
            w.writerow({"suite": "stress", "instance": "stress24", "seed": seed,
                        "num_variables": len(V), "strategy": strat,
                        "success": m["success"], "status": m["status"],
                        "initial_core_size": m["initial_core_size"],
                        "final_core_size": m["final_core_size"], "expansions": m["expansions"],
                        "used_explanation": m["used_explanation"],
                        "used_assumption_core": m["used_assumption_core"],
                        "used_frontier": m["used_frontier"],
                        "boundary_released": m["boundary_released"],
                        "gac_time_ns": m["gac_time_ns"], "cpsat_time_ns": m["cpsat_time_ns"],
                        "total_time_ns": m["total_time_ns"],
                        "full_scope_required": m["full_scope_required"]})
        n += 1
    f.close()
    print(f"repair-triggering instances: {n}", flush=True)


if __name__ == "__main__":
    main()
