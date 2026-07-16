import pandas as pd

df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
print("Columns:", df.columns.tolist())

# compute Energy/HO for M0, M4, M9
for m in ["M0", "M4", "M9"]:
    m_df = df[df["method_id"] == m]
    if len(m_df) > 0:
        energy = m_df["energy_mj"].mean() if "energy_mj" in m_df.columns else m_df["energy_per_bit"].mean() if "energy_per_bit" in m_df.columns else 0
        ho = m_df["ho_failures"].mean() if "ho_failures" in m_df.columns else m_df["ho_failure_rate"].mean() if "ho_failure_rate" in m_df.columns else 0
        print(f"{m}: Energy: {energy}, HO: {ho}")

