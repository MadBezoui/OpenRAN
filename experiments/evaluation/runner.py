import time
import pandas as pd
import sys
import os
import itertools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.simulator import NetworkSimulator, generate_instance, SCENARIO_PRESETS
from src.verifier import Verifier
from solvers.baselines import (solve_uncoordinated, solve_static_priority,
                               solve_cp_sat)
from solvers.continuous import ContinuousSolver
from solvers.verixapp import VeriXApp

# Polarization exponent used by the continuous coordinator (beta > 1).
BETA = 2.0


def _record(results, method, assignment, latency, verifier, simulator,
            problem, scenario_info, stats=None):
    is_valid = verifier.verify(assignment) if assignment else False
    kpis = simulator.compute_kpis(assignment, problem) if assignment else {}
    res = {
        "Method": method,
        "Feasible": is_valid,
        "Latency_ms": latency,
        "Stall": stats.get("stall", False) if stats else False,
        "RepairAttempted": stats.get("repair_attempted", False) if stats else False,
        "Repaired": stats.get("repaired", False) if stats else False,
        "RepairTimeout": stats.get("repair_timeout", False) if stats else False,
        "CoreSize": stats.get("core_size", 0) if stats else 0,
        "Throughput": kpis.get("throughput_mbps", 0.0),
        "Energy": kpis.get("energy_per_bit", 0.0),
        "HOF": kpis.get("hof_rate", 0.0),
        "Fairness": kpis.get("jain_fairness", 0.0),
    }
    res.update(scenario_info)
    results.append(res)


def evaluate_instance(problem, simulator, scenario_info):
    """Run every baseline and VeriXApp on one instance."""
    results = []
    verifier = Verifier(problem)

    t0 = time.time()
    uncoord = solve_uncoordinated(problem)
    _record(results, "Uncoordinated", uncoord, (time.time() - t0) * 1000,
            verifier, simulator, problem, scenario_info)

    t0 = time.time()
    stat_prio = solve_static_priority(problem)
    _record(results, "Static priority", stat_prio, (time.time() - t0) * 1000,
            verifier, simulator, problem, scenario_info)

    t0 = time.time()
    cont_solver = ContinuousSolver(problem, beta=BETA)
    cont_solver.solve()
    cont = cont_solver.decode()
    lat = (time.time() - t0) * 1000
    frac = cont_solver.get_fractionality()
    cont_stall = frac > 0.05 and not verifier.verify(cont)
    _record(results, "Continuous only", cont, lat, verifier, simulator,
            problem, scenario_info, {"stall": cont_stall})

    t0 = time.time()
    cpsat = solve_cp_sat(problem)
    _record(results, "CP-SAT", cpsat, (time.time() - t0) * 1000,
            verifier, simulator, problem, scenario_info)

    t0 = time.time()
    verixapp = VeriXApp(problem, beta=BETA)
    vx_assign, stats = verixapp.solve(fallback_assignment=uncoord)
    _record(results, "VeriXApp", vx_assign, (time.time() - t0) * 1000,
            verifier, simulator, problem, scenario_info, stats)

    return results


def evaluate_ablation(problem, simulator, scenario_info):
    """Run VeriXApp ablation configurations on one instance."""
    results = []
    verifier = Verifier(problem)
    uncoord = solve_uncoordinated(problem)

    configs = [
        ("Full VeriXApp", dict(beta=BETA, repair=True, max_hops=2)),
        ("No polarization", dict(beta=1.0, repair=True, max_hops=2)),
        ("No exact repair", dict(beta=BETA, repair=False, max_hops=0)),
        ("Repair radius h=0", dict(beta=BETA, repair=True, max_hops=0)),
        ("Repair radius h=1", dict(beta=BETA, repair=True, max_hops=1)),
        ("Repair radius h=2", dict(beta=BETA, repair=True, max_hops=2)),
    ]
    for name, cfg in configs:
        t0 = time.time()
        vx = VeriXApp(problem, beta=cfg["beta"])
        assign, stats = vx.solve(fallback_assignment=uncoord,
                                 repair_enabled=cfg["repair"],
                                 max_hops=cfg["max_hops"])
        lat = (time.time() - t0) * 1000
        info = dict(scenario_info)
        info["AblationConfig"] = name
        _record(results, "VeriXApp", assign, lat, verifier, simulator,
                problem, info, stats)
    return results


RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
N_MAIN = 30
N_ABL = 25
N_SCALE = 20
SIZES = [8, 16, 24, 32, 40]


def run_main():
    res = []
    print(f"Running main experiment: 5 scenarios x {N_MAIN} seeds ...")
    for scenario, preset in SCENARIO_PRESETS.items():
        for seed in range(N_MAIN):
            sim = NetworkSimulator(num_cells=10, num_users=100,
                                   traffic_load=0.6, mobility_speed=3.0, seed=seed)
            p = generate_instance(seed=seed, **preset)
            info = {"Scenario": scenario, "Load": 0.6, "Mobility": 3.0,
                    "Cells": 10, "Seed": seed, "AblationConfig": ""}
            res.extend(evaluate_instance(p, sim, info))
    pd.DataFrame(res).to_csv(os.path.join(RES_DIR, 'raw_main.csv'), index=False)
    print("main done")


def run_ablation():
    res = []
    print(f"Running ablation: {N_ABL} seeds ...")
    preset = SCENARIO_PRESETS["S4"]
    for seed in range(N_ABL):
        sim = NetworkSimulator(num_cells=10, num_users=100, traffic_load=0.6,
                               mobility_speed=3.0, seed=seed)
        p = generate_instance(seed=1000 + seed, **preset)
        info = {"Scenario": "AblationCfg", "Load": 0.6, "Mobility": 3.0,
                "Cells": 10, "Seed": seed}
        res.extend(evaluate_ablation(p, sim, info))
    pd.DataFrame(res).to_csv(os.path.join(RES_DIR, 'raw_abl.csv'), index=False)
    print("ablation done")


def run_scale():
    """Scalability sweep over the number of xApp action variables."""
    res = []
    print(f"Running scalability: {len(SIZES)} sizes x {N_SCALE} seeds ...")
    for size, seed in itertools.product(SIZES, range(N_SCALE)):
        sim = NetworkSimulator(num_cells=10, num_users=100, traffic_load=0.6,
                               mobility_speed=3.0, seed=seed)
        p = generate_instance(num_vars=size, domain_size=4,
                              num_constraints=int(size * 1.1), seed=3000 + seed,
                              sym_frac=0.5)
        info = {"Scenario": "Scale", "Size": size, "Load": 0.6, "Mobility": 3.0,
                "Cells": 10, "Seed": seed, "AblationConfig": ""}
        res.extend(evaluate_instance(p, sim, info))
    pd.DataFrame(res).to_csv(os.path.join(RES_DIR, 'raw_scale.csv'), index=False)
    print("scale done")


def merge():
    parts = []
    for name in ('raw_main.csv', 'raw_abl.csv', 'raw_scale.csv'):
        path = os.path.join(RES_DIR, name)
        if os.path.exists(path):
            parts.append(pd.read_csv(path))
    df = pd.concat(parts, ignore_index=True)
    out = os.path.join(RES_DIR, 'raw_results.csv')
    df.to_csv(out, index=False)
    print(f"Merged {len(df)} rows -> {out}")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase in ("main", "all"):
        run_main()
    if phase in ("ablation", "all"):
        run_ablation()
    if phase in ("scale", "all"):
        run_scale()
    if phase in ("merge", "all"):
        merge()


if __name__ == "__main__":
    main()
