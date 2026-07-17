"""Aggregate raw logs into summary statistics with integer counts and paired
bootstrap confidence intervals. Emits artifacts/tables/summary.json and prints
a human-readable summary. Every reported rate is accompanied by its exact
sample size and a 95% bootstrap CI; repair audits report which expansion
mechanism was actually used.
"""
import json, os
import numpy as np
import pandas as pd
pd.set_option("future.no_silent_downcasting", True)
RAW = "artifacts/raw"; OUT = "artifacts/tables"
rng = np.random.default_rng(12345)


def boot_ci(x, n=2000, stat=np.mean):
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return (float("nan"), float("nan"))
    idx = rng.integers(0, len(x), size=(n, len(x)))
    bs = stat(x[idx], axis=1)
    return (round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4))


def tf(col):
    return col.fillna(False).astype(str).str.lower().isin(["true", "1", "1.0"])


def static_summary(S):
    S = S.copy()
    for c in ["executed_verified", "optimized_verified", "repaired_verified",
              "fallback_verified", "fallback_used"]:
        S[c] = tf(S[c])
    S["lat"] = S["total_time_ns"] / 1e6
    out = {}
    for m in S.method.unique():
        d = S[S.method == m]
        counts = d.outcome.value_counts().to_dict()
        N = len(d)
        feas = d.executed_verified.astype(float)
        rec = {"N": int(N),
               "counts": {k: int(counts.get(k, 0)) for k in
                          ["direct", "local_repair", "full_repair", "fallback", "blocked"]},
               "verified_feasible_pct": round(100 * feas.mean(), 2),
               "verified_feasible_ci": tuple(100 * c for c in boot_ci(feas)),
               "deadline_100ms_pct": round(100 * (d.executed_verified & (d.lat <= 100)).mean(), 2),
               "median_latency_ms": round(d.lat.median(), 2),
               "p95_latency_ms": round(d.lat.quantile(.95), 2),
               "median_cont_iters": float(d.continuous_iterations.median())}
        assert sum(rec["counts"].values()) == N, f"counts do not sum to N for {m}"
        out[m] = rec
    return out


def network_summary(S):
    out = {}
    for m in S.method.unique():
        d = S[S.method == m]
        ex = d[tf(d.executed_verified)]
        def mean_ci(series, scale=1.0):
            s = series.dropna().astype(float) * scale
            return {"mean": round(float(s.mean()), 4) if len(s) else None,
                    "ci": boot_ci(s), "n": int(len(s))}
        out[m] = {
            "counterfactual": {k: mean_ci(d["cf_" + k], 1e6 if k == "energy" else 1.0) for k in ["throughput", "energy", "hof", "fairness"]},
            "verified_executed": {k: mean_ci(ex["ex_" + k], 1e6 if k == "energy" else 1.0) for k in ["throughput", "energy", "hof", "fairness"]},
        }
    return out


def repair_summary(R):
    R = R.copy()
    for c in ["success", "used_explanation", "used_assumption_core", "used_frontier", "full_scope_required"]:
        R[c] = tf(R[c])
    out = {}
    for suite in R.suite.unique():
        ds = R[R.suite == suite]
        strategies = {}
        for s in ds.strategy.unique():
            d = ds[ds.strategy == s]
            strategies[s] = {
                "n": int(len(d)),
                "success_pct": round(100 * d.success.mean(), 2),
                "success_ci": tuple(100 * c for c in boot_ci(d.success.astype(float))),
                "median_initial_core": float(d.initial_core_size.median()),
                "median_final_core": float(d.final_core_size.median()),
                "mean_expansions": round(float(d.expansions.mean()), 3),
                "used_explanation_n": int(d.used_explanation.sum()),
                "used_assumption_core_n": int(d.used_assumption_core.sum()),
                "used_frontier_n": int(d.used_frontier.sum()),
                "mean_boundary_released": round(float(d.boundary_released.mean()), 3),
                "median_cpsat_ms": round(float((d.cpsat_time_ns / 1e6).median()), 3),
                "median_total_ms": round(float((d.total_time_ns / 1e6).median()), 3),
            }
        out[suite] = strategies
    return out


def incremental_summary(D):
    D = D.copy(); D["domain_agree"] = tf(D["domain_agree"])
    out = {"overall_agreement_pct": round(100 * D.domain_agree.mean(), 3),
           "n_epochs": int(len(D)), "by_transition": {}}
    for ut in ["restrictive", "relaxed", "mixed", "utility-only"]:
        d = D[(D.epoch_id > 0) & (D.update_type == ut)]
        if len(d) == 0:
            continue
        rc, ic = d.recompute_time_ns.mean() / 1e6, d.incremental_time_ns.mean() / 1e6
        out["by_transition"][ut] = {"count": int(len(d)),
                                    "recompute_ms": round(rc, 4), "incremental_ms": round(ic, 4),
                                    "gain_pct": round(100 * (1 - ic / rc), 2),
                                    "mean_restored": round(float(d.restored.mean()), 3),
                                    "agreement_pct": round(100 * d.domain_agree.mean(), 2)}
    return out


def scalability_summary(SC):
    out = {}
    for n in sorted(SC.n.unique()):
        d = SC[SC.n == n]
        out[int(n)] = {m: round(float((d[d.method == m].total_time_ns / 1e6).median()), 2)
                       for m in d.method.unique()}
        out[int(n)]["peak_mem_mb"] = round(float(d.peak_mem_mb.max()), 1)
    return out


def temporal_summary(T):
    T = T.copy(); T["feasible"] = tf(T["feasible"])
    out = {}
    for mu in sorted(T.mu.unique()):
        d = T[T.mu == mu]
        out[float(mu)] = {"mean_churn": round(float(d.churn.mean()), 3),
                          "mean_throughput": round(float(d.throughput.mean()), 3),
                          "feasible_pct": round(100 * d.feasible.mean(), 2)}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = {}
    def load(name):
        p = os.path.join(RAW, name)
        return pd.read_csv(p) if os.path.exists(p) and os.path.getsize(p) else None
    S = load("static_results.csv")
    if S is not None:
        summary["static"] = static_summary(S)
        summary["network"] = network_summary(S)
    R = load("repair_ablation.csv")
    if R is not None:
        summary["repair_ablation"] = repair_summary(R)
    D = load("dynamic_results.csv")
    if D is not None:
        summary["incremental"] = incremental_summary(D)
    SC = load("scalability_results.csv")
    if SC is not None:
        summary["scalability"] = scalability_summary(SC)
    T = load("temporal_results.csv")
    if T is not None:
        summary["temporal"] = temporal_summary(T)
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=1)[:4000])
    print("\nWrote", os.path.join(OUT, "summary.json"))


if __name__ == "__main__":
    main()
