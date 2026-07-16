import pandas as pd
import numpy as np
import re
import os

def load_data():
    static_df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
    dynamic_df = pd.read_csv("artifacts/raw/dynamic_results.csv", low_memory=False)
    
    # Clean booleans
    for df in [static_df, dynamic_df]:
        for col in ["optimized_verified", "repaired_verified", "fallback_used", "timeout", "infeasible", "repair_attempted"]:
            if col in df:
                df[col] = df[col].fillna(False).astype(str).str.lower() == 'true'
                
    return static_df, dynamic_df

def generate_end_to_end_table(static_df):
    method_names = {
        "M0": "Uncoordinated",
        "M1": "Static priority",
        "M2": "Continuous only",
        "M3": "GAC + decode",
        "M4": "CP-SAT",
        "M5": "GAC + CP-SAT",
        "M6": "\\legacy",
        "M9": "Full \\method"
    }
    
    lines = []
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append("\\caption{End-to-end coordination results on the static suite.}")
    lines.append("\\label{tab:main-results}")
    lines.append("\\begin{tabular}{lrrrrrrrr}")
    lines.append("\\toprule")
    lines.append("Method & Opt. verif & Rep. verif & Fallback & Timeout & Infeasible & Median & $\\le 100$ms \\\\")
    lines.append("& (\\%) & (\\%) & (\\%) & (\\%) & (\\%) & (ms) & (\\%) \\\\")
    lines.append("\\midrule")
    
    for m_id, name in method_names.items():
        m_df = static_df[static_df["method_id"] == m_id]
        if len(m_df) == 0: continue
        total = len(m_df)
        
        opt_pct = 100 * m_df["optimized_verified"].sum() / total
        rep_pct = 100 * m_df["repaired_verified"].sum() / total
        fall_pct = 100 * m_df["fallback_used"].sum() / total
        time_pct = 100 * m_df["timeout"].sum() / total
        inf_pct = 100 * m_df["infeasible"].sum() / total
        
        latencies = m_df["total_time_ns"] / 1e6
        median_ms = latencies.median()
        le100_pct = 100 * (latencies <= 100).sum() / total
        
        lines.append(f"{name} & {opt_pct:.1f} & {rep_pct:.1f} & {fall_pct:.1f} & {time_pct:.1f} & {inf_pct:.1f} & {median_ms:.1f} & {le100_pct:.1f} \\\\")
    
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    return "\n".join(lines)

def generate_propagation_table(static_df):
    lines = []
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append("\\caption{Consistency-propagation results.}")
    lines.append("\\label{tab:propagation-results}")
    lines.append("\\begin{tabular}{lrrrrrrrrr}")
    lines.append("\\toprule")
    lines.append("Scenario & Epochs & Val before & Val after & $r_D$ & Tup before & Tup after & $r_R$ & Med GAC & P95 GAC\\\\")
    lines.append("& & & & (\\%) & & & (\\%) & (ms) & (ms)\\\\")
    lines.append("\\midrule")
    
    m9_df = static_df[static_df["method_id"] == "M9"]
    
    for scenario in sorted(m9_df["scenario_id"].unique()):
        s_df = m9_df[m9_df["scenario_id"] == scenario]
        epochs = len(s_df)
        v_b = s_df["values_before"].sum()
        v_a = s_df["values_after"].sum()
        r_d = 100 * (v_b - v_a) / v_b if v_b > 0 else 0
        
        t_b = s_df["tuples_before"].sum()
        t_a = s_df["tuples_after"].sum()
        r_r = 100 * (t_b - t_a) / t_b if t_b > 0 else 0
        
        gac_ms = s_df["propagation_time_ns"] / 1e6
        med_gac = gac_ms.median()
        p95_gac = gac_ms.quantile(0.95)
        
        lines.append(f"{scenario} & {epochs} & {v_b} & {v_a} & {r_d:.1f} & {t_b} & {t_a} & {r_r:.1f} & {med_gac:.1f} & {p95_gac:.1f}\\\\")
    
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    return "\n".join(lines)

def generate_repair_table(static_df):
    lines = []
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append("\\caption{Exact-repair characteristics.}")
    lines.append("\\label{tab:repair-results}")
    lines.append("\\begin{tabular}{lrrrrrr}")
    lines.append("\\toprule")
    lines.append("Strategy & Attempts & Success (\\%) & Init Core & Median Repair & P95 Repair & Timeout (\\%)\\\\")
    lines.append("\\midrule")
    
    strategies = {"M4": "Full scope", "M6": "Radius $h=1$", "M9": "Explanation-guided"}
    
    for m_id, name in strategies.items():
        m_df = static_df[(static_df["method_id"] == m_id) & (static_df["repair_attempted"] == True)]
        attempts = len(m_df)
        if attempts == 0:
            lines.append(f"{name} & 0 & 0.0 & 0.0 & 0.0 & 0.0 & 0.0\\\\")
            continue
            
        success_pct = 100 * m_df["repaired_verified"].sum() / attempts
        init_core = m_df["initial_core_size"].median()
        rep_ms = m_df["repair_time_ns"] / 1e6
        med_rep = rep_ms.median()
        p95_rep = rep_ms.quantile(0.95)
        timeout_pct = 100 * m_df["timeout"].sum() / attempts
        
        lines.append(f"{name} & {attempts} & {success_pct:.1f} & {init_core:.1f} & {med_rep:.1f} & {p95_rep:.1f} & {timeout_pct:.1f}\\\\")
        
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    return "\n".join(lines)

def generate_dynamic_table(dynamic_df):
    lines = []
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append("\\caption{Incremental propagation by transition type}")
    lines.append("\\label{tab:incremental-results}")
    lines.append("\\begin{tabular}{lrrrrr}")
    lines.append("\\toprule")
    lines.append("Update Type & Total Eval & GAC Median & Overall Median & Repaired & Timeout \\\\")
    lines.append("& & (ms) & (ms) & (\\%) & (\\%) \\\\")
    lines.append("\\midrule")
    
    m9_df = dynamic_df[dynamic_df["method_id"] == "M9"]
    
    for u_type in sorted(m9_df["update_type"].unique()):
        u_df = m9_df[m9_df["update_type"] == u_type]
        evals = len(u_df)
        gac_med = (u_df["propagation_time_ns"] / 1e6).median()
        tot_med = (u_df["total_time_ns"] / 1e6).median()
        rep_pct = 100 * u_df["repaired_verified"].sum() / evals
        timeout_pct = 100 * u_df["timeout"].sum() / evals
        
        lines.append(f"{u_type.capitalize()} & {evals} & {gac_med:.2f} & {tot_med:.2f} & {rep_pct:.1f} & {timeout_pct:.1f} \\\\")
        
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    return "\n".join(lines)

def generate_network_table(static_df):
    lines = []
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append("\\caption{Temporal stability and network-level performance}")
    lines.append("\\label{tab:temporal-results}")
    lines.append("\\begin{tabular}{lrrrrr}")
    lines.append("\\toprule")
    lines.append("Method & Throughput & Energy/bit & HO failures & Fairness\\\\")
    lines.append("& (Mbps) & ($\\mu$J) & (\\%) & (Jain)\\\\")
    lines.append("\\midrule")
    
    strategies = {"M0": "Uncoordinated", "M4": "CP-SAT", "M9": "\\method"}
    for m_id, name in strategies.items():
        m_df = static_df[static_df["method_id"] == m_id]
        if len(m_df) == 0: continue
        throughput = m_df["throughput_mbps"].median() if "throughput_mbps" in m_df else 0
        energy = m_df["energy_per_bit"].median() if "energy_per_bit" in m_df else 0
        hof = m_df["hof_rate"].median() if "hof_rate" in m_df else 0
        jain = m_df["jain_fairness"].median() if "jain_fairness" in m_df else 0
        
        lines.append(f"{name} & {throughput:.1f} & {energy:.1f} & {hof:.1f} & {jain:.3f} \\\\")
        
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    return "\n".join(lines)

def main():
    static_df, dynamic_df = load_data()
    tex_file = "main3.tex"
    with open(tex_file, "r") as f:
        content = f.read()
        
    content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{\nConsistency-propagation results.*?\\end\{tabular\}\n\\end\{table\*\}", generate_propagation_table(static_df).replace("\\", "\\\\"), content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{\nEnd-to-end coordination results.*?\\end\{tabular\}\n\\end\{table\*\}", generate_end_to_end_table(static_df).replace("\\", "\\\\"), content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{Exact-repair characteristics.*?\\end\{tabular\}\n\\end\{table\*\}", generate_repair_table(static_df).replace("\\", "\\\\"), content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{Incremental propagation by transition type.*?\\end\{tabular\}\n\\end\{table\*\}", generate_dynamic_table(dynamic_df).replace("\\", "\\\\"), content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{Temporal stability and network-level performance.*?\\end\{tabular\}\n\\end\{table\*\}", generate_network_table(static_df).replace("\\", "\\\\"), content, flags=re.DOTALL)
    
    with open(tex_file, "w") as f:
        f.write(content)
        
    print("Tables regenerated and injected.")

if __name__ == "__main__":
    main()
