import pandas as pd
df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
for m in df["method_id"].unique():
    m_df = df[df["method_id"] == m]
    success = (m_df["repair_success"].fillna(False).astype(str).str.lower() == 'true').sum()
    attempt = (m_df["repair_attempted"].fillna(False).astype(str).str.lower() == 'true').sum()
    if attempt > 0:
        print(f"{m}: Attempts: {attempt}, Success: {success}")
