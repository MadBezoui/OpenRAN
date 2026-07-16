import pandas as pd
df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
for m in ["M2", "M3"]:
    m_df = df[df["method_id"] == m]
    invalid = (m_df["invalid_decode"].fillna(False).astype(str).str.lower() == 'true').sum()
    print(f"{m} invalid: {invalid}")
