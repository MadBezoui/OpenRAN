import pandas as pd

df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
for m in ["M0", "M4", "M9"]:
    m_df = df[df["method_id"] == m]
    if len(m_df) > 0:
        ho = m_df["hof_rate"].mean() * 100
        print(f"{m}: HO: {ho:.2f}%")

