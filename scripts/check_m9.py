import pandas as pd

df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
m9 = df[df["method_id"] == "M9"]
print(f"Total M9: {len(m9)}")
print(f"Repair attempted: {m9['repair_attempted'].fillna(False).astype(str).str.lower() == 'true'}")
print(f"Repair success: {m9['repair_success'].fillna(False).astype(str).str.lower() == 'true'}")

