"""Structural sensitivity experiment."""
import argparse, csv, os, random, time
from src.generators.stress_generator import generate_stress_instance
from src.verification.verifier import Verifier
from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.propagation.gac import GAC
from src.continuous.consensus import ContinuousConsensus
from src.continuous.decoder import Decoder
from src.repair.engine import RepairEngine

STRATEGIES = ["radius1", "explanation", "fullscope"]
FIELDS = ["suite", "instance", "seed", "num_variables", "domain_size", "density",
          "strategy", "success", "status", "initial_core_size", "final_core_size",
          "expansions", "total_time_ns", "full_scope_required"]

def decode(V, D, R):
    filtered = {v.id: FilteredDomain(D[v.id]) for v in V}
    active = [ActiveRelation(r) for r in R]
    if not GAC(V, filtered, active).enforce(): return None
    cons = ContinuousConsensus(V, filtered, active)
    cons.solve()
    return Decoder(cons).decode()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--budget_ms", type=int, default=100)
    ap.add_argument("--out", default="artifacts/raw/structural_results.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    f = open(a.out, "w", newline=""); w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    
    n_vars = 24
    for dom_size in [2, 4, 8, 16]:
        for density in [1.0, 1.5, 2.0, 3.0]:
            n_cons = int(n_vars * density)
            for seed in range(42, 42 + a.seeds):
                V, D, R, planted = generate_stress_instance(n_vars, dom_size, n_cons, seed)
                ver = Verifier(D, R)
                rng = random.Random(seed * 7)
                dec = dict(planted)
                # Plant errors
                for vid in rng.sample([v.id for v in V], min(3, n_vars)):
                    opts = [x for x in range(dom_size) if x != planted[vid]]
                    if opts: dec[vid] = rng.choice(opts)
                if ver.verify(dec, "c", "c"): continue
                
                eng = RepairEngine(V, D, R, ver)
                for strat in STRATEGIES:
                    m = eng.repair(strat, dec, deadline_ms=a.budget_ms)
                    w.writerow({"suite": "structural", "instance": f"d{dom_size}_c{n_cons}",
                                "seed": seed, "num_variables": n_vars, "domain_size": dom_size,
                                "density": density, "strategy": strat, "success": m["success"],
                                "status": m["status"], "initial_core_size": m["initial_core_size"],
                                "final_core_size": m["final_core_size"], "expansions": m["expansions"],
                                "total_time_ns": m["total_time_ns"], "full_scope_required": m["full_scope_required"]})
                f.flush()
            print(f"dom_size={dom_size} density={density} done", flush=True)
    f.close()

if __name__ == "__main__":
    main()
