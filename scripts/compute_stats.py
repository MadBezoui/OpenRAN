import pandas as pd
import numpy as np

def main():
    static_df = pd.read_csv("artifacts/raw/static_results.csv")
    dynamic_df = pd.read_csv("artifacts/raw/dynamic_results.csv")
    
    # Check boolean format issue
    print("Static M9 Opt Verif unique values:", static_df[static_df["method_id"]=="M9"]["optimized_verified"].unique())
    
    # Calculate GAC reduction
    m9_static = static_df[static_df["method_id"] == "M9"]
    v_b = m9_static["values_before"].sum()
    v_a = m9_static["values_after"].sum()
    print(f"GAC removed values: {100 * (v_b - v_a)/v_b:.1f}%")
    
    # Calculate repair core reduction (M9 vs M6)
    m6_repair = static_df[(static_df["method_id"] == "M6") & (static_df["repair_attempted"] == True)]["initial_core_size"]
    m9_repair = static_df[(static_df["method_id"] == "M9") & (static_df["repair_attempted"] == True)]["initial_core_size"]
    print(f"M6 median core: {m6_repair.median()}, M9 median core: {m9_repair.median()}")
    print(f"Core difference: {m9_repair.median() - m6_repair.median()}")
    
    # Feasibility and deadline compliance for M9
    # Feasible = optimized_verified OR repaired_verified
    m9_opt = m9_static["optimized_verified"].fillna(False).astype(str).str.lower() == 'true'
    m9_rep = m9_static["repaired_verified"].fillna(False).astype(str).str.lower() == 'true'
    m9_feasible = m9_opt | m9_rep
    print(f"M9 Feasibility: {100 * m9_feasible.sum() / len(m9_static):.1f}%")
    
    m9_lat = m9_static["total_time_ns"] / 1e6
    print(f"M9 Deadline compliance (<=100ms): {100 * (m9_lat <= 100).sum() / len(m9_static):.1f}%")

if __name__ == "__main__":
    main()
