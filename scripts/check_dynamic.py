import pandas as pd
df = pd.read_csv("artifacts/raw/dynamic_results.csv", low_memory=False)
relax = df[df["values_after"] > df["values_before"]]
print("Relaxation rows:", len(relax))
if len(relax) > 0:
    print("Values restored sum:", (relax["values_after"] - relax["values_before"]).sum())
