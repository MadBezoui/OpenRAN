"""Paired statistics v2 (review-driven).

Replaces Cliff's delta with paired-appropriate effect measures:
matched-pairs rank-biserial correlation and the Hodges-Lehmann estimate of
the median paired difference (with bootstrap CI). Adds (i) the repair
ablation on the operational utility-decode candidates and (ii) episode-level
tests for the sequential suite, treating the episode (seed), not the epoch,
as the experimental unit.

Output: artifacts/tables/stats_v2.json
"""
import json
import math
import os

import numpy as np
import pandas as pd
from scipy import stats

RAW = "artifacts/raw"
OUT = "artifacts/tables/stats_v2.json"
RNG = np.random.default_rng(20260716)


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(0, k + 1)) * 0.5 ** n
    return min(1.0, p)


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(1.0, running)
    return adj.tolist()


def rank_biserial(diff):
    """Matched-pairs rank-biserial correlation from paired differences."""
    d = np.asarray(diff)
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(d))
    w_pos = ranks[d > 0].sum()
    w_neg = ranks[d < 0].sum()
    return float((w_pos - w_neg) / (w_pos + w_neg))


def hodges_lehmann(diff):
    d = np.asarray(diff)
    n = len(d)
    walsh = (d[:, None] + d[None, :]) / 2.0
    return float(np.median(walsh[np.triu_indices(n)]))


def hl_ci(diff, n_boot=2000):
    d = np.asarray(diff)
    ests = []
    for _ in range(n_boot):
        s = RNG.choice(d, size=len(d), replace=True)
        ests.append(np.median(s))
    return [float(np.percentile(ests, 2.5)),
            float(np.percentile(ests, 97.5))]


def paired_block(la, lb):
    diff = la - lb
    try:
        p = float(stats.wilcoxon(la, lb).pvalue) if not np.allclose(la, lb) \
            else 1.0
    except ValueError:
        p = 1.0
    return {"wilcoxon_p": float(f"{p:.3g}"),
            "rank_biserial": round(rank_biserial(diff), 3),
            "hl_median_diff": round(hodges_lehmann(diff), 3),
            "median_diff_ci": [round(x, 3) for x in hl_ci(diff)]}


def main():
    results = {}

    # ---- static suite: key latency comparisons ----
    s = pd.read_csv(os.path.join(RAW, "static_results.csv"))
    s["latency_ms"] = s["total_time_ns"] / 1e6
    s["key"] = s["scenario"] + "_" + s["seed"].astype(str)
    out = []
    for a, b in [("GAC + expl repair", "CP-SAT"),
                 ("GAC + expl repair", "GAC + CP-SAT")]:
        da = s[s.method == a].set_index("key")
        db = s[s.method == b].set_index("key")
        common = da.index.intersection(db.index)
        blk = paired_block(da.loc[common, "latency_ms"].values,
                           db.loc[common, "latency_ms"].values)
        blk.update({"a": a, "b": b, "n_pairs": int(len(common)),
                    "med_a": round(float(da.loc[common, "latency_ms"]
                                         .median()), 2),
                    "med_b": round(float(db.loc[common, "latency_ms"]
                                         .median()), 2)})
        out.append(blk)
    results["static_latency"] = out

    # ---- repair ablation on operational (utility-decode) candidates ----
    r = pd.read_csv(os.path.join(RAW, "repair_ablation_utility.csv"))
    r["key"] = (r["suite"] + "_" + r["instance"].astype(str) + "_" +
                r["seed"].astype(str))
    rs = r[r.suite == "standard"]
    abl = []
    ps = []
    for a, b in [("explanation", "violated0"), ("explanation", "radius0"),
                 ("explanation", "radius1"), ("explanation", "radius2"),
                 ("explanation", "fullscope"), ("assumption", "radius2")]:
        da = rs[rs.strategy == a].set_index("key")
        db = rs[rs.strategy == b].set_index("key")
        common = da.index.intersection(db.index)
        sa = da.loc[common, "success"].astype(bool)
        sb = db.loc[common, "success"].astype(bool)
        disc_b = int((sa & ~sb).sum())
        disc_c = int((~sa & sb).sum())
        p_mc = mcnemar_exact(disc_b, disc_c)
        ta = da.loc[common, "total_time_ns"].values / 1e6
        tb = db.loc[common, "total_time_ns"].values / 1e6
        blk = paired_block(ta, tb)
        blk.update({"a": a, "b": b, "n_pairs": int(len(common)),
                    "succ_a_pct": round(100 * sa.mean(), 2),
                    "succ_b_pct": round(100 * sb.mean(), 2),
                    "disc": [disc_b, disc_c], "mcnemar_p": round(p_mc, 6),
                    "core_med_a": float(da.loc[common,
                                               "final_core_size"].median()),
                    "core_med_b": float(db.loc[common,
                                               "final_core_size"].median()),
                    "ms_med_a": round(float(np.median(ta)), 3),
                    "ms_med_b": round(float(np.median(tb)), 3)})
        abl.append(blk)
        ps.append(p_mc)
    adj = holm(ps)
    for i, blk in enumerate(abl):
        blk["mcnemar_p_holm"] = round(adj[i], 6)
    results["ablation_utility_standard"] = abl

    # ---- sequential suite: episode-level analysis ----
    d = pd.read_csv(os.path.join(RAW, "dynamic_scale_v2.csv"))
    ep = (d.groupby(["delta", "n", "seed", "method"])["total_ms"]
            .median().reset_index())
    seq = []
    for (delta, n), grp in ep.groupby(["delta", "n"]):
        piv = grp.pivot(index="seed", columns="method", values="total_ms")
        la = piv["incr_repair"].values
        lb = piv["cpsat_rebuild"].values
        blk = paired_block(la, lb)
        blk.update({"delta": delta, "n": int(n),
                    "episodes": int(len(piv)),
                    "incr_med_of_medians": round(float(np.median(la)), 2),
                    "rebuild_med_of_medians": round(float(np.median(lb)), 2)})
        seq.append(blk)
    results["sequential_episode_level"] = seq

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
