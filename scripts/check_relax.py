import pandas as pd
import os
files = [f for f in os.listdir("artifacts/raw") if f.endswith(".csv")]
for file in files:
    df = pd.read_csv(f"artifacts/raw/{file}", low_memory=False)
    for col in df.columns:
        if 'relax' in col.lower() or 'restore' in col.lower() or 'transition' in col.lower():
            print(f"{file}: {col}")
