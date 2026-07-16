import argparse
import csv
import os
import uuid

from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.generators.dynamic_generator import generate_dynamic_transition
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.network.physical_model import NetworkSimulator

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    scenarios = ["S1", "S2", "S3", "S4", "S5"]
    episodes = 30
    epochs = 100
    methods = ["M9", "M10"]
    
    out_dir = "artifacts/raw"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "dynamic_results.csv")
    
    fields = [
        "run_id", "method_id", "scenario_id", "episode_id", "epoch_id",
        "update_type", "total_time_ns", "propagation_time_ns", "executed_verified", "repair_success",
        "wipeout", "global_wipeout", "repair_attempted", "optimized_verified", "repaired_verified",
        "fallback_used", "timeout", "infeasible", "model_build_time_ns", "solver_time_ns",
        "values_before", "values_after", "tuples_before", "tuples_after",
        "throughput_mbps", "energy_per_bit", "hof_rate", "jain_fairness"
    ]
    
    with open(out_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for scenario in scenarios:
            for episode in range(episodes):
                seed = 1000 + episode
                print(f"Running Dynamic Scenario: {scenario}, Episode: {episode}")
                
                # Base epoch
                variables, domains, relations, planted_solution = generate_static_instance(scenario, seed)
                dsize_map = {v.id: len(domains[v.id].base_values) for v in variables}
                
                for epoch in range(epochs):
                    if epoch > 0:
                        domains, relations = generate_dynamic_transition(variables, domains, relations, 0.1, seed + epoch)
                        
                    for method in methods:
                        verifier = Verifier(domains, relations)
                        ctx_id = f"ctx_{scenario}_{episode}_{epoch}"
                        
                        metrics = run_pipeline(variables, domains, relations, ctx_id, verifier, method)
                        
                        executed_assignment = metrics.pop("executed_decision", {})
                        net_sim = NetworkSimulator(seed=seed+epoch)
                        kpis = net_sim.compute_kpis(executed_assignment, variables, dsize_map)
                        
                        row = {
                            "run_id": str(uuid.uuid4()),
                            "method_id": method,
                            "scenario_id": scenario,
                            "episode_id": episode,
                            "epoch_id": epoch,
                            "update_type": "base" if epoch == 0 else "mixed",
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
