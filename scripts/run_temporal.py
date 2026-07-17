"""Temporal-stability experiment (RQ6): sweep the churn weight mu.

Over dynamic episodes we compute, at each epoch, a verifier-accepted candidate
decision (GAC + explanation-guided repair). A churn-aware rule then decides
whether to switch to the candidate or retain the previous verified decision:
switch iff the utility gain exceeds mu times the number of changed actions,
and only if the retained action is still feasible under the current context
(re-verified). We report, per mu, the mean action churn, mean throughput
(utility proxy), and verified-feasibility rate, exposing the stability/utility
trade-off the model's dynamic utility U^dyn = U - mu*H is meant to capture.
"""
import argparse, csv, os
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS
from src.verification.verifier import Verifier
from src.experiments.pipeline import run_pipeline
from src.network.physical_model import NetworkSimulator

MUS = [0.0, 0.01, 0.1, 0.5, 1.0]
BASE = dict(gac=True, continuous=False, repair=True, strategy="explanation", decode="utility")
FIELDS = ["mu", "scenario", "episode", "epoch", "executed", "churn",
          "throughput", "feasible"]


def churn(a, b):
    if not a or not b:
        return 0
    return sum(1 for k in a if k in b and a[k] != b[k])


def _feasible_transition(variables, domains, relations, planted, ratio, seed):
    """Restrict/relax domains and relations while always retaining the planted
    value / planted tuple, so the sequence stays feasible (no monotone drift to
    infeasibility). Mirrors the planted-preservation of the incremental suite."""
    import random as _r
    from src.model.domains import Domain
    from src.model.relations import Relation
    rng = _r.Random(seed)
    dsz = {vid: max(v for v in dom.base_values) + 1 for vid, dom in domains.items()}
    nd = {}
    for vid, dom in domains.items():
        vals = set(dom.base_values)
        if rng.random() < ratio:
            if rng.random() < 0.5:
                cand = [v for v in vals if v != planted[vid]]
                if len(vals) > 1 and cand:
                    vals.discard(rng.choice(cand))
            else:
                missing = set(range(dsz[vid])) - vals
                if missing:
                    vals.add(rng.choice(sorted(missing)))
        nd[vid] = Domain(sorted(vals))
    nr = []
    for rel in relations:
        allowed = set(rel.allowed_tuples)
        pt = tuple(planted[v] for v in rel.scope)
        if rng.random() < ratio and len(allowed) > 1:
            cand = [t for t in allowed if t != pt]
            if cand:
                allowed.discard(rng.choice(cand))
        nr.append(Relation(id=rel.id, name=rel.name, scope=rel.scope,
                           allowed_tuples=allowed, is_hard=rel.is_hard))
    return nd, nr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=30)
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--out", default="artifacts/raw/temporal_results.csv")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    f = open(a.out, "w", newline=""); w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    for mu in MUS:
        for scenario in ["S1", "S3", "S5"]:
            for episode in range(a.episodes):
                seed = 2000 + episode
                V, D, R, planted = generate_static_instance(scenario, seed)
                dmap = {v.id: len(D[v.id].base_values) for v in V}
                prev = None
                for epoch in range(a.epochs):
                    if epoch > 0:
                        D, R = _feasible_transition(V, D, R, planted, 0.1, seed + epoch)
                    ver = Verifier(D, R)
                    sim = NetworkSimulator(seed=seed + epoch)
                    m = run_pipeline(V, D, R, f"{scenario}_{episode}_{epoch}", ver, BASE)
                    cand = m.get("_executed")
                    cand_thr = sim.compute_kpis(cand, V, dmap)["throughput_mbps"] if cand else 0.0
                    # churn-aware selection
                    chosen, thr = cand, cand_thr
                    if prev is not None and ver.verify(prev, "keep", "keep"):
                        prev_thr = sim.compute_kpis(prev, V, dmap)["throughput_mbps"]
                        c = churn(prev, cand) if cand else 0
                        if cand is None or (cand_thr - prev_thr) <= mu * c:
                            chosen, thr = prev, prev_thr
                    ch = churn(prev, chosen) if prev is not None else 0
                    feasible = chosen is not None and ver.verify(chosen, "e", "e")
                    w.writerow({"mu": mu, "scenario": scenario, "episode": episode,
                                "epoch": epoch, "executed": chosen is not None,
                                "churn": ch, "throughput": round(thr, 4),
                                "feasible": feasible})
                    if chosen is not None:
                        prev = chosen
            f.flush()
        print(f"mu={mu} done", flush=True)
    f.close()


if __name__ == "__main__":
    main()
