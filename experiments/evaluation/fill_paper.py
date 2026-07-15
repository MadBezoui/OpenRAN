"""
Safe, non-destructive table exporter.

The previous version of this script edited ../../main.tex in place with
regular expressions and corrupted several passages (orphaned sentence
fragments, mismatched table columns, physically impossible values). It has
been replaced. This module now only regenerates a LaTeX fragment of the
main results table from the audited CSV logs; it never rewrites main.tex.
Copy the emitted fragment into the manuscript manually if desired.
"""
import os
import pandas as pd

RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')


def export_main_table():
    src = os.path.join(RES_DIR, 'main_results.csv')
    if not os.path.exists(src):
        print("main_results.csv not found; run report.py first.")
        return
    df = pd.read_csv(src)
    lines = [r"\begin{tabular}{lrrrr}", r"\toprule",
             r"Method & Verified feasible (\%) & Stall rate (\%) & "
             r"Median latency (ms) & P95 latency (ms) \\", r"\midrule"]
    for _, r in df.iterrows():
        lines.append(
            f"{r['Method']} & {r['Verified feasible (%)']:.1f} & "
            f"{r['Stall rate (%)']:.1f} & {r['Median latency (ms)']:.2f} & "
            f"{r['P95 latency (ms)']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    out = os.path.join(RES_DIR, 'main_results.tex')
    with open(out, 'w') as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {out} (fragment only; main.tex is never modified).")


if __name__ == "__main__":
    export_main_table()
