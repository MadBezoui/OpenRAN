import argparse
import pandas as pd
import os

def audit_logs(input_dir):
    static_file = os.path.join(input_dir, "static_results.csv")
    if not os.path.exists(static_file):
        print(f"Error: {static_file} not found.")
        return 1
        
    df = pd.read_csv(static_file)
    errors = 0
    
    # Check 1: total_time_ns >= 0
    if (df['total_time_ns'] < 0).any():
        print("Error: Found negative total_time_ns")
        errors += 1
        
    # Check 2: executed_decision is always verified
    if not df['executed_verified'].all():
        print("Error: Found executed decisions that are not verified")
        errors += 1
        
    if errors == 0:
        print("Audit passed successfully! 0 errors.")
        return 0
    else:
        print(f"Audit failed with {errors} errors.")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="artifacts/raw")
    args = parser.parse_args()
    exit(audit_logs(args.input))
