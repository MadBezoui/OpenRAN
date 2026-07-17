import csv, os, sys, uuid
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.network.physical_model import NetworkSimulator
from scripts.run_static_chunk import FIELDS, METHODS

def main():
    scenario = sys.argv[1]
    s0, s1 = int(sys.argv[2]), int(sys.argv[3])
    out_file = "artifacts/raw/static_results.csv"
    new = not os.path.exists(out_file) or os.path.getsize(out_file) == 0
    f = open(out_file, "a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new: w.writeheader()
    for seed in range(s0, s1):
        variables, domains, relations, _ = generate_static_instance(scenario, seed)
        dmap = {v.id: len(domains[v.id].base_values) for v in variables}
        for method in METHODS:
            ver = Verifier(domains, relations)
            met = run_pipeline(variables, domains, relations, f"ctx_{scenario}_{seed}", ver, method)
            ex = met.pop("executed_decision", {})
            kpis = NetworkSimulator(seed=seed).compute_kpis(ex, variables, dmap)
            row = {"run_id": str(uuid.uuid4()), "method_id": method, "scenario_id": scenario,
                   "instance_seed": seed, "num_variables": SCENARIO_PRESETS[scenario]["num_vars"],
                   "num_constraints": SCENARIO_PRESETS[scenario]["num_constraints"]}
            for k, v in met.items():
                if k in FIELDS: row[k] = v
            for k, v in kpis.items():
                if k in FIELDS: row[k] = v
            w.writerow(row)
        f.flush()
    f.close()
    print(f"done {scenario} seeds {s0}-{s1}", flush=True)

if __name__ == "__main__":
    main()
