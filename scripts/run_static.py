import argparse
import csv
import os
import uuid
import numpy as np

from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.network.physical_model import NetworkSimulator
from src.model.utility import UtilityMapper

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    scenarios = ["S1", "S2", "S3", "S4", "S5"]
    seeds = list(range(42, 42 + 50)) # Run 50 seeds as requested
    methods = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10"]
    
    out_dir = "artifacts/raw"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "static_results.csv")
    
    fields = [
        "run_id", "method_id", "scenario_id", "instance_seed",
        "num_variables", "num_constraints",
        "wipeout", "global_wipeout", "explanation_size", "initial_core_size",
        "continuous_iterations", "final_residual", "final_fractionality",
        "operational_stall", "invalid_decode",
        "repair_attempted", "repair_success",
        "raw_verified", "fallback_used", "fallback_verified", "executed_verified",
        "optimized_verified", "repaired_verified", "timeout", "infeasible",
        "values_before", "values_after", "tuples_before", "tuples_after",
        "propagation_time_ns", "continuous_time_ns", "repair_time_ns", "total_time_ns",
        "model_build_time_ns", "solver_time_ns",
        "throughput_mbps", "energy_per_bit", "hof_rate", "jain_fairness"
    ]
    
    with open(out_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for scenario in scenarios:
            for seed in seeds:
                variables, domains, relations, planted_solution = generate_static_instance(scenario, seed)
                dsize_map = {v.id: len(domains[v.id].base_values) for v in variables}
                
                for method in methods:
                    verifier = Verifier(domains, relations)
                    ctx_id = f"ctx_{scenario}_{seed}"
                    
                    metrics = run_pipeline(variables, domains, relations, ctx_id, verifier, method)
                    
                    executed_assignment = metrics.pop("executed_decision", {})
                    net_sim = NetworkSimulator(seed=seed)
                    kpis = net_sim.compute_kpis(executed_assignment, variables, dsize_map)
                    
                    row = {
                        "run_id": str(uuid.uuid4()),
                        "method_id": method,
                        "scenario_id": scenario,
                        "instance_seed": seed,
                        "num_variables": SCENARIO_PRESETS[scenario]["num_vars"],
                        "num_constraints": SCENARIO_PRESETS[scenario]["num_constraints"]
                    }
                    
                    for k, v in metrics.items():
                        if k in fields:
                            row[k] = v
                    for k, v in kpis.items():
                        if k in fields:
                            row[k] = v
                            
                    writer.writerow(row)
                    
    print(f"Results saved to {out_file}")

if __name__ == "__main__":
    main()
