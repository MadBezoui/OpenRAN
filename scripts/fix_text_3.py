import re

with open("main3.tex", "r") as f:
    content = f.read()

# 1. Rebuild Table 3 (tab:main-results)
table3 = r"""\begin{table*}[t]
\centering
\caption{End-to-end coordination results on the static suite.}
\label{tab:main-results}
\begin{tabular}{lrrrrrrrr}
\toprule
Method & Verified feasible & Fallback & Timeout & Infeasible & Median & P95 & $\le 100$ms & Utility\\
& (\%) & (\%) & (\%) & (\%) & (ms) & (ms) & (\%) & \\
\midrule
Uncoordinated & 0.0 & 100.0 & 0.0 & 0.0 & 0.0 & 0.0 & 100.0 & 0.34\\
Static priority & 0.0 & 100.0 & 0.0 & 0.0 & 0.0 & 0.0 & 100.0 & 0.34\\
Continuous only & 29.6 & 24.4 & 0.0 & 46.0 & 185.5 & 382.6 & 29.6 & 0.42\\
GAC + decode & 56.8 & 25.6 & 0.0 & 17.6 & 84.9 & 271.9 & 56.8 & 0.42\\
CP-SAT & 100.0 & 0.0 & 0.0 & 0.0 & 2.9 & 5.0 & 100.0 & 0.44\\
GAC + CP-SAT & 100.0 & 0.0 & 0.0 & 0.0 & 2.9 & 5.0 & 100.0 & 0.44\\
\method-legacy & 57.2 & 25.6 & 0.0 & 17.2 & 83.8 & 270.6 & 57.2 & 0.42\\
Full \method & 74.4 & 25.6 & 0.0 & 0.0 & 85.1 & 267.2 & 56.8 & 0.42\\
\bottomrule
\end{tabular}
\end{table*}"""

content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{End-to-end coordination results on the static suite\.\}.*?\\end\{tabular\}\n\\end\{table\*\}", lambda m: table3, content, flags=re.DOTALL)

# 2. Table 4 Stalls
table4 = r"""\begin{table}[t]
\centering
\caption{Continuous-stage diagnostics before and after GAC}
\label{tab:stall-results}
\begin{tabular}{lrrr}
\toprule
Scenario &
No GAC stalls &
GAC stalls &
Invalid decode\\
&
(\%) &
(\%) &
(\%)\\
\midrule
S1 & 24.0 & 26.0 & 0.0\\
S2 & 12.0 & 12.0 & 0.0\\
S3 & 22.0 & 22.0 & 0.0\\
S4 & 30.0 & 32.0 & 0.0\\
S5 & 34.0 & 36.0 & 0.0\\
\bottomrule
\end{tabular}
\end{table}"""
content = re.sub(r"\\begin\{table\}\[t\]\n\\centering\n\\caption\{Continuous-stage diagnostics before and after GAC\}.*?\\end\{tabular\}\n\\end\{table\}", lambda m: table4, content, flags=re.DOTALL)

# 3. Table 7 Temporal
table7 = r"""\begin{table*}[t]
\centering
\caption{Temporal stability and network-level performance}
\label{tab:temporal-results}
\begin{tabular}{lrrrrr}
\toprule
Method & Throughput & Energy/bit & HO failures & Fairness\\
& (Mbps) & ($\mu$J) & (\%) & (Jain)\\
\midrule
Uncoordinated & 7.2 & 68.9 & 4.6 & 0.339 \\
CP-SAT & 10.7 & 50.8 & 3.9 & 0.448 \\
\method & 10.0 & 55.2 & 4.0 & 0.428 \\
\bottomrule
\end{tabular}
\end{table*}"""
content = re.sub(r"\\begin\{table\*\}\[t\]\n\\centering\n\\caption\{Temporal stability and network-level performance\}.*?\\end\{tabular\}\n\\end\{table\*\}", lambda m: table7, content, flags=re.DOTALL)

# 4. Remove contradictory sentence in 7.3
content = re.sub(r"Relative to direct CP-SAT, full \\method\\[^>]*?deadline compliance by \+15\.2\\% \[14\.0, 16\.4\]\.", "The framework explicitly trades absolute optimal execution time for safety guarantees and exact local explanations.", content, flags=re.DOTALL)

# 5. Fix abstract and conclusion mismatch
# If abstract says 74.4% feasibility, make sure conclusion doesn't say 100%.
content = re.sub(r"full pipeline reaches 100\% feasibility", "CP-SAT resolves 100\\% of exact models while the full pipeline reaches 74.4\\% independent verified feasibility without unbounded escalation", content)

# 6. Table 5 caption note
content = re.sub(r"\\caption\{\nExact-repair characteristics.\n\}", r"\\caption{\nExact-repair characteristics. Note: restricted-radius and explanation-guided exact repair achieved 0.0\\% success in isolation on these dense instances, falling back to full-scope CP-SAT which always succeeded.\n}", content)

with open("main3.tex", "w") as f:
    f.write(content)

print("Applied fixes to main3.tex")
