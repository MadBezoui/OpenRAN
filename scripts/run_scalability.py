import argparse
import csv
import os
import uuid

from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    scalability_sizes = [12, 30, 50, 100, 200, 500]
    seeds = [42, 43, 44] # Just 3 seeds to be reasonably fast
    methods = ["M4", "M5", "M9"]
    
    out_dir = "artifacts/raw"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "scalability_results.csv")
    
    fields = [
        "run_id", "method_id", "scenario_id", "instance_seed",
        "num_variables", "num_constraints", "total_time_ns", "propagation_time_ns",
        "repair_time_ns", "continuous_time_ns", "wipeout"
    ]
    
    with open(out_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for size in scalability_sizes:
            for seed in seeds:
                print(f"Running Scalability: n={size}, Seed: {seed}")
                
                # S5_Scale preset
                SCENARIO_PRESETS["S5_Scale"] = dict(num_vars=size, domain_size=4, num_constraints=size, sym_frac=0.5)
                
                variables, domains, relations, planted_solution = generate_static_instance("S5_Scale", seed)
                verifier = Verifier(domains, relations)
                
                for method in methods:
                    ctx_id = f"ctx_scale_{size}_{seed}_{method}"
                    metrics = run_pipeline(variables, domains, relations, ctx_id, verifier, method)
                    
                    row = {
                        "run_id": str(uuid.uuid4()),
                        "method_id": method,
                        "scenario_id": f"Scale_{size}",
                        "instance_seed": seed,
                        "num_variables": size,
                        "num_constraints": size,
                    }
                    
                    for k, v in metrics.items():
                        if k in fields:
                            row[k] = v
                            
                    writer.writerow(row)
                    
    print(f"Results saved to {out_file}")

if __name__ == "__main__":
    main()
