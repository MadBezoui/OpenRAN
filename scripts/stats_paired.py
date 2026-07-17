"""Paired statistical tests for the static suite and repair ablation.

Implements what the Statistical-protocol subsection promises:
  - exact McNemar tests on paired binary outcomes (verified feasibility),
  - Wilcoxon signed-rank tests on paired latencies,
  - Cliff's delta effect sizes,
  - Holm-Bonferroni correction within each comparison family.

Outputs artifacts/tables/stats_paired.json and a human-readable summary.
"""
import json
import math
import os

import numpy as np
import pandas as pd
from scipy import stats

RAW = "artifacts/raw"
OUT = "artifacts/tables/stats_paired.json"


def cliffs_delta(x, y):
    """Cliff's delta for paired samples treated as two groups."""
    x, y = np.asarray(x), np.asarray(y)
    n, m = len(x), len(y)
    if n == 0 or m == 0:
        return float("nan")
    gt = sum((xi > y).sum() for xi in x)
    lt = sum((xi < y).sum() for xi in x)
    return (gt - lt) / (n * m)


def mcnemar_exact(b, c):
    """Exact McNemar test from discordant-pair counts b, c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(0, k + 1)) * 0.5 ** n
    return min(1.0, p)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values."""
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(1.0, running)
    return adj.tolist()


def main():
    s = pd.read_csv(os.path.join(RAW, "static_results.csv"))
    s["latency_ms"] = s["total_time_ns"] / 1e6
    s["key"] = s["scenario"] + "_" + s["seed"].astype(str)
    results = {"static_pairs": [], "ablation_pairs": []}

    pairs = [
        ("GAC + expl repair", "CP-SAT"),
        ("GAC + expl repair", "GAC + CP-SAT"),
        ("ConsistXApp expl", "GAC + expl repair"),
        ("ConsistXApp expl", "CP-SAT"),
        ("ConsistXApp expl", "ConsistXApp radius"),
    ]
    feas_p, lat_p = [], []
    for a, b in pairs:
        da = s[s.method == a].set_index("key")
        db = s[s.method == b].set_index("key")
        common = da.index.intersection(db.index)
        da, db = da.loc[common], db.loc[common]
        fa = da["executed_verified"].astype(bool)
        fb = db["executed_verified"].astype(bool)
        disc_b = int((fa & ~fb).sum())   # a ok, b not
        disc_c = int((~fa & fb).sum())   # b ok, a not
        p_mc = mcnemar_exact(disc_b, disc_c)
        la, lb = da["latency_ms"].values, db["latency_ms"].values
        try:
            p_w = float(stats.wilcoxon(la, lb).pvalue) if not np.allclose(la, lb) else 1.0
        except ValueError:
            p_w = 1.0
        results["static_pairs"].append({
            "a": a, "b": b, "n_pairs": int(len(common)),
            "feas_a_pct": round(100 * fa.mean(), 2),
            "feas_b_pct": round(100 * fb.mean(), 2),
            "discordant_a_only": disc_b, "discordant_b_only": disc_c,
            "mcnemar_p": p_mc,
            "lat_median_a": round(float(np.median(la)), 3),
            "lat_median_b": round(float(np.median(lb)), 3),
            "wilcoxon_p": p_w,
            "cliffs_delta_latency": round(cliffs_delta(la, lb), 3),
        })
        feas_p.append(p_mc)
        lat_p.append(p_w)
    feas_adj = holm(feas_p)
    lat_adj = holm(lat_p)
    for i, rec in enumerate(results["static_pairs"]):
        rec["mcnemar_p_holm"] = round(feas_adj[i], 4)
        rec["wilcoxon_p_holm"] = round(lat_adj[i], 6)
        rec["mcnemar_p"] = round(rec["mcnemar_p"], 4)
        rec["wilcoxon_p"] = float(f"{rec['wilcoxon_p']:.3g}")

    # ---- repair ablation ----
    r = pd.read_csv(os.path.join(RAW, "repair_ablation.csv"))
    r["key"] = r["suite"] + "_" + r["instance"].astype(str) + "_" + r["seed"].astype(str)
    abl_pairs = [
        ("explanation", "violated0"),
        ("explanation", "radius0"),
        ("explanation", "radius2"),
        ("explanation", "fullscope"),
        ("assumption", "radius2"),
    ]
    ps = []
    for a, b in abl_pairs:
        da = r[r.strategy == a].set_index("key")
        db = r[r.strategy == b].set_index("key")
        common = da.index.intersection(db.index)
        da, db = da.loc[common], db.loc[common]
        sa, sb = da["success"].astype(bool), db["success"].astype(bool)
        disc_b = int((sa & ~sb).sum())
        disc_c = int((~sa & sb).sum())
        p_mc = mcnemar_exact(disc_b, disc_c)
        ta = da["total_time_ns"].values / 1e6
        tb = db["total_time_ns"].values / 1e6
        try:
            p_w = float(stats.wilcoxon(ta, tb).pvalue) if not np.allclose(ta, tb) else 1.0
        except ValueError:
            p_w = 1.0
        results["ablation_pairs"].append({
            "a": a, "b": b, "n_pairs": int(len(common)),
            "succ_a_pct": round(100 * sa.mean(), 2),
            "succ_b_pct": round(100 * sb.mean(), 2),
            "discordant_a_only": disc_b, "discordant_b_only": disc_c,
            "mcnemar_p": round(p_mc, 4),
            "core_median_a": float(da["final_core_size"].median()),
            "core_median_b": float(db["final_core_size"].median()),
            "time_median_a_ms": round(float(np.median(ta)), 3),
            "time_median_b_ms": round(float(np.median(tb)), 3),
            "wilcoxon_p": float(f"{p_w:.3g}"),
            "cliffs_delta_time": round(cliffs_delta(ta, tb), 3),
        })
        ps.append(p_mc)
    adj = holm(ps)
    for i, rec in enumerate(results["ablation_pairs"]):
        rec["mcnemar_p_holm"] = round(adj[i], 4)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
