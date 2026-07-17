import csv, os, sys, uuid
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.network.physical_model import NetworkSimulator

FIELDS = [
    "run_id","method_id","scenario_id","instance_seed","num_variables","num_constraints",
    "wipeout","global_wipeout","explanation_size","initial_core_size",
    "continuous_iterations","final_residual","final_fractionality",
    "operational_stall","invalid_decode","repair_attempted","repair_success",
    "raw_verified","fallback_used","fallback_verified","executed_verified",
    "optimized_verified","repaired_verified","timeout","infeasible",
    "values_before","values_after","tuples_before","tuples_after",
    "propagation_time_ns","continuous_time_ns","repair_time_ns","total_time_ns",
    "model_build_time_ns","solver_time_ns",
    "throughput_mbps","energy_per_bit","hof_rate","jain_fairness",
]
METHODS = ["M0","M1","M2","M3","M4","M5","M6","M7","M8","M9","M10"]

def main():
    scenarios = sys.argv[1].split(",")
    out_file = "artifacts/raw/static_results.csv"
    os.makedirs("artifacts/raw", exist_ok=True)
    new = not os.path.exists(out_file) or os.path.getsize(out_file) == 0
    f = open(out_file, "a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()
    seeds = list(range(42, 42 + 50))
    for scenario in scenarios:
        for seed in seeds:
            variables, domains, relations, _ = generate_static_instance(scenario, seed)
            dmap = {v.id: len(domains[v.id].base_values) for v in variables}
            for method in METHODS:
                ver = Verifier(domains, relations)
                met = run_pipeline(variables, domains, relations,
                                   f"ctx_{scenario}_{seed}", ver, method)
                ex = met.pop("executed_decision", {})
                kpis = NetworkSimulator(seed=seed).compute_kpis(ex, variables, dmap)
                row = {"run_id": str(uuid.uuid4()), "method_id": method,
                       "scenario_id": scenario, "instance_seed": seed,
                       "num_variables": SCENARIO_PRESETS[scenario]["num_vars"],
                       "num_constraints": SCENARIO_PRESETS[scenario]["num_constraints"]}
                for k, v in met.items():
                    if k in FIELDS: row[k] = v
                for k, v in kpis.items():
                    if k in FIELDS: row[k] = v
                w.writerow(row)
        f.flush()
        print(f"done {scenario}", flush=True)
    f.close()

if __name__ == "__main__":
    main()
