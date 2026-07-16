import pandas as pd
df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
for m in ["M4", "M6", "M8", "M9"]:
    m_df = df[df["method_id"] == m]
    timeout = (m_df["timeout"].fillna(False).astype(str).str.lower() == 'true').sum()
    repair_success = (m_df["repair_success"].fillna(False).astype(str).str.lower() == 'true').sum()
    infeasible = (m_df["infeasible"].fillna(False).astype(str).str.lower() == 'true').sum()
    print(f"{m}: Timeout: {timeout}, Success: {repair_success}, Infeasible: {infeasible}")
