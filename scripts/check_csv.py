import pandas as pd

df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
for col in ["optimized_verified", "repaired_verified", "fallback_used", "timeout", "infeasible"]:
    df[col] = df[col].fillna(False).astype(str).str.lower() == 'true'

for m in ["M0", "M1", "M4", "M9"]:
    m_df = df[df["method_id"] == m]
    if len(m_df) > 0:
        opt_verif = m_df["optimized_verified"].mean() * 100
        rep_verif = m_df["repaired_verified"].mean() * 100
        fall = m_df["fallback_used"].mean() * 100
        time = m_df["timeout"].mean() * 100
        inf = m_df["infeasible"].mean() * 100
        print(f"{m}: Opt: {opt_verif:.1f}%, Rep: {rep_verif:.1f}%, Fall: {fall:.1f}%, Time: {time:.1f}%, Inf: {inf:.1f}%")

