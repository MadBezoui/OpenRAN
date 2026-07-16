import pandas as pd

static_df = pd.read_csv("artifacts/raw/static_results.csv", low_memory=False)
dynamic_df = pd.read_csv("artifacts/raw/dynamic_results.csv", low_memory=False)

print("Dynamic Update Types:", dynamic_df["update_type"].unique())

print("\nM2 (No GAC) stalls by scenario:")
m2 = static_df[static_df["method_id"] == "M2"]
for s in sorted(m2["scenario_id"].unique()):
    stalls = (m2[m2["scenario_id"] == s]["operational_stall"].fillna(False).astype(str).str.lower() == 'true').mean() * 100
    print(f"  {s}: {stalls:.1f}%")

print("\nM3 (GAC) stalls by scenario:")
m3 = static_df[static_df["method_id"] == "M3"]
for s in sorted(m3["scenario_id"].unique()):
    stalls = (m3[m3["scenario_id"] == s]["operational_stall"].fillna(False).astype(str).str.lower() == 'true').mean() * 100
    inv = (m3[m3["scenario_id"] == s]["invalid_decode"].fillna(False).astype(str).str.lower() == 'true').mean() * 100
    print(f"  {s}: Stalls {stalls:.1f}%, Invalid {inv:.1f}%")

