import pandas as pd
import numpy as np
import os
import scipy.stats as stats

SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]
METHOD_ORDER = ["Uncoordinated", "Static priority", "Continuous only",
                "CP-SAT", "VeriXApp"]
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')


def mean_ci(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    if n < 2:
        return float(np.mean(a)) if n else 0.0, 0.0
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2., n - 1)
    return float(m), float(h)


def holm_correction(p_values):
    p_values = np.asarray(p_values, dtype=float)
    n = len(p_values)
    order = np.argsort(p_values)
    adj = np.zeros(n)
    for i, idx in enumerate(order):
        adj[idx] = min(1.0, p_values[idx] * (n - i))
    for i in range(1, n):
        adj[order[i]] = max(adj[order[i]], adj[order[i - 1]])
    return adj


def generate_report():
    in_path = os.path.join(RES_DIR, 'raw_results.csv')
    if not os.path.exists(in_path):
        print("No raw_results.csv found.")
        return
    df = pd.read_csv(in_path)
    main_df = df[df['Scenario'].isin(SCENARIOS)].copy()
    methods = [m for m in METHOD_ORDER if m in main_df["Method"].unique()]

    # ---- 1. Main results (feasibility, stall, latency, Holm p) --------
    base_method = "Continuous only"
    base_feas = main_df[main_df["Method"] == base_method]["Feasible"].values.astype(float)

    p_values, comparisons = [], []
    for method in methods:
        if method == base_method:
            continue
        comp = main_df[main_df["Method"] == method]["Feasible"].values.astype(float)
        if len(comp) == len(base_feas) and len(base_feas) > 1 and \
                (np.var(comp) > 0 or np.var(base_feas) > 0):
            try:
                _, p = stats.ttest_rel(comp, base_feas)
            except Exception:
                p = 1.0
        else:
            p = 1.0
        p = 1.0 if np.isnan(p) else p
        p_values.append(p)
        comparisons.append(method)
    adj_p = holm_correction(p_values) if p_values else []
    p_dict = dict(zip(comparisons, adj_p))
    p_dict[base_method] = 1.0

    main_results = []
    for method in methods:
        mdf = main_df[main_df["Method"] == method]
        m_feas, h_feas = mean_ci(mdf["Feasible"].values.astype(float) * 100)
        stall_pct = mdf["Stall"].mean() * 100 if len(mdf) else 0.0
        main_results.append({
            "Method": method,
            "Verified feasible (%)": round(m_feas, 1),
            "VF_CI": round(h_feas, 1),
            "Holm_p": round(float(p_dict.get(method, 1.0)), 4),
            "Stall rate (%)": round(stall_pct, 1),
            "Median latency (ms)": round(mdf["Latency_ms"].median(), 2),
            "P95 latency (ms)": round(mdf["Latency_ms"].quantile(0.95), 2),
        })
    res_df = pd.DataFrame(main_results)
    res_df.to_csv(os.path.join(RES_DIR, 'main_results.csv'), index=False)

    # ---- 2. Network KPIs ----------------------------------------------
    net = []
    for method in methods:
        mdf = main_df[main_df["Method"] == method]
        net.append({
            "Method": method,
            "Throughput": round(mdf["Throughput"].mean(), 2),
            "Energy": mdf["Energy"].mean(),
            "HOF": round(mdf["HOF"].mean() * 100, 2),
            "Fairness": round(mdf["Fairness"].mean(), 3),
        })
    pd.DataFrame(net).to_csv(os.path.join(RES_DIR, 'network_kpis.csv'), index=False)

    # ---- 3. Repair statistics -----------------------------------------
    vx = main_df[main_df["Method"] == "VeriXApp"]
    attempts = int(vx["RepairAttempted"].sum())
    successes = int(vx["Repaired"].sum())
    repaired_rows = vx[vx["Repaired"]]
    med_core = repaired_rows["CoreSize"].median() if len(repaired_rows) else 0
    p95_core = repaired_rows["CoreSize"].quantile(0.95) if len(repaired_rows) else 0
    max_core = repaired_rows["CoreSize"].max() if len(repaired_rows) else 0
    timeouts = int(vx["RepairTimeout"].sum())
    pd.DataFrame([{
        "Attempts": attempts, "Successes": successes,
        "MedCore": med_core, "P95Core": p95_core, "MaxCore": max_core,
        "Timeouts": timeouts,
    }]).to_csv(os.path.join(RES_DIR, 'repair_stats.csv'), index=False)

    # ---- 4. Per-scenario stall diagnostics ----------------------------
    stall_rows = []
    for sc in SCENARIOS:
        sdf = main_df[(main_df["Scenario"] == sc) & (main_df["Method"] == "VeriXApp")]
        if not len(sdf):
            continue
        invalid = sdf["RepairAttempted"]
        stall_rows.append({
            "Scenario": sc,
            "Stalls (%)": round(sdf["Stall"].mean() * 100, 1),
            "Invalid decode (%)": round(invalid.mean() * 100, 1),
            "Repaired (%)": round((sdf[invalid]["Repaired"].mean() * 100)
                                  if invalid.sum() else 100.0, 1),
        })
    pd.DataFrame(stall_rows).to_csv(os.path.join(RES_DIR, 'stalls_by_scenario.csv'),
                                    index=False)

    # ---- 5. Ablation ---------------------------------------------------
    abl_df = df[df["Scenario"] == "AblationCfg"].copy()
    abl_rows = []
    if len(abl_df):
        order = ["Full VeriXApp", "No polarization", "No exact repair",
                 "Repair radius h=0", "Repair radius h=1", "Repair radius h=2"]
        for cfg in order:
            cdf = abl_df[abl_df["AblationConfig"] == cfg]
            if not len(cdf):
                continue
            abl_rows.append({
                "Configuration": cfg,
                "Feasible (%)": round(cdf["Feasible"].mean() * 100, 1),
                "P95 latency (ms)": round(cdf["Latency_ms"].quantile(0.95), 1),
            })
    pd.DataFrame(abl_rows).to_csv(os.path.join(RES_DIR, 'ablation.csv'), index=False)

    # ---- 6. Scalability over number of xApps --------------------------
    scale_df = df[df["Scenario"] == "Scale"]
    load_rows = []
    if len(scale_df):
        for size in sorted(scale_df["Size"].dropna().unique()):
            sdf = scale_df[scale_df["Size"] == size]
            vx = sdf[sdf["Method"] == "VeriXApp"]
            cp = sdf[sdf["Method"] == "CP-SAT"]
            co = sdf[sdf["Method"] == "Continuous only"]
            load_rows.append({
                "Size": int(size),
                "VeriXApp feasible (%)": round(vx["Feasible"].mean() * 100, 1),
                "Continuous stall (%)": round(co["Stall"].mean() * 100, 1),
                "VeriXApp median latency (ms)": round(vx["Latency_ms"].median(), 1),
                "CP-SAT median latency (ms)": round(cp["Latency_ms"].median(), 1),
            })
    pd.DataFrame(load_rows).to_csv(os.path.join(RES_DIR, 'scalability.csv'),
                                   index=False)

    print("=== Main results ===")
    print(res_df.to_string(index=False))
    print("\n=== Network KPIs ===")
    print(pd.DataFrame(net).to_string(index=False))
    print("\n=== Repair ===")
    print(pd.read_csv(os.path.join(RES_DIR, 'repair_stats.csv')).to_string(index=False))
    print("\n=== Stalls by scenario ===")
    print(pd.DataFrame(stall_rows).to_string(index=False))
    print("\n=== Ablation ===")
    print(pd.DataFrame(abl_rows).to_string(index=False))
    print("\n=== Scalability ===")
    print(pd.DataFrame(load_rows).to_string(index=False))


if __name__ == "__main__":
    generate_report()
