"""Static suite: 5 scenarios x 50 seeds, hard wall-clock budget.
Records per-(method,scenario,seed) outcome, continuous iterations, repair audit,
and both counterfactual (raw decode) and verified-executed network KPIs.
"""
import argparse, csv, os, sys
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.network.physical_model import NetworkSimulator

METHODS = [
    ("Uncoordinated",       dict(gac=False, continuous=False, repair=False, strategy="fullscope", decode="random")),
    ("Static priority",     dict(gac=False, continuous=False, repair=False, strategy="fullscope", decode="priority")),
    ("Continuous only",     dict(gac=False, continuous=True,  repair=False, strategy="fullscope", decode="continuous")),
    ("GAC + decode",        dict(gac=True,  continuous=True,  repair=False, strategy="fullscope", decode="continuous")),
    ("CP-SAT",              dict(gac=False, continuous=False, repair=True,  strategy="fullscope", decode="utility")),
    ("GAC + CP-SAT",        dict(gac=True,  continuous=False, repair=True,  strategy="fullscope", decode="utility")),
    ("GAC + expl repair",   dict(gac=True,  continuous=False, repair=True,  strategy="explanation", decode="utility")),
    ("ConsistXApp expl",    dict(gac=True,  continuous=True,  repair=True,  strategy="explanation", decode="continuous")),
    ("ConsistXApp radius",  dict(gac=True,  continuous=True,  repair=True,  strategy="radius1",     decode="continuous")),
    ("ConsistXApp assume",  dict(gac=True,  continuous=True,  repair=True,  strategy="assumption",  decode="continuous")),
    ("FC + expl repair",    dict(gac=True,  continuous=False, repair=True,  strategy="explanation", decode="forward_check")),
]


FIELDS = ["method", "scenario", "seed", "num_variables", "outcome",
          "executed_verified", "optimized_verified", "repaired_verified",
          "fallback_used", "fallback_verified", "raw_verified", "wipeout",
          "operational_stall", "invalid_decode", "continuous_iterations",
          "total_time_ns", "propagation_time_ns", "continuous_time_ns",
          "repair_time_ns", "repair_attempted", "repair_initial_core",
          "repair_final_core", "repair_expansions", "repair_used_explanation",
          "repair_used_assumption_core", "repair_used_frontier",
          "repair_boundary_released", "repair_full_scope", "repair_status",
          "cert_overhead_ns", "cert_size_bytes",
          "values_before", "values_after", "tuples_before", "tuples_after",

          "cf_throughput", "cf_energy", "cf_hof", "cf_fairness",
          "ex_throughput", "ex_energy", "ex_hof", "ex_fairness"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--deadline_ms", type=int, default=100)
    ap.add_argument("--out", default="artifacts/raw/static_results.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    f = open(a.out, "w", newline=""); w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    for scenario in ["S1", "S2", "S3", "S4", "S5"]:
        for seed in range(42, 42 + a.seeds):
            V, D, R, _ = generate_static_instance(scenario, seed)
            dmap = {v.id: len(D[v.id].base_values) for v in V}
            sim = NetworkSimulator(seed=seed)
            for name, cfg in METHODS:
                ver = Verifier(D, R)
                m = run_pipeline(V, D, R, f"{scenario}_{seed}_{name}", ver, cfg, a.deadline_ms)
                decoded = m.pop("decoded", {})
                cf = sim.compute_kpis(decoded, V, dmap) if decoded else {}
                ex = sim.compute_kpis(m["_executed"], V, dmap) if m.get("_executed") else {}
                row = {"method": name, "scenario": scenario, "seed": seed,
                       "num_variables": SCENARIO_PRESETS[scenario]["num_vars"]}
                for k in FIELDS:
                    if k in m: row[k] = m[k]
                row["cf_throughput"] = cf.get("throughput_mbps"); row["cf_energy"] = cf.get("energy_per_bit")
                row["cf_hof"] = cf.get("hof_rate"); row["cf_fairness"] = cf.get("jain_fairness")
                row["ex_throughput"] = ex.get("throughput_mbps"); row["ex_energy"] = ex.get("energy_per_bit")
                row["ex_hof"] = ex.get("hof_rate"); row["ex_fairness"] = ex.get("jain_fairness")
                w.writerow(row)
            f.flush()
        print(f"done {scenario}", flush=True)
    f.close()


if __name__ == "__main__":
    main()
