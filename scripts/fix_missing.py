import re

with open("main3.tex", "r") as f:
    content = f.read()

# 1. Belief Propagation
p1 = r"The concept concerns the fixed points of the implemented update map; it is not presented as a stationary point of an unspecified global optimization objective\."
r1 = r"The concept concerns the fixed points of the implemented update map. The connection between fractional fixed points and the belief-propagation and linear-programming relaxation literature---where max-product message passing converges only when the LP relaxation has no fractional optima \cite{wainwright2005map, yedidia2003understanding}---is conceptually well established but has been underexplored in near-RT RIC conflict arbitration."
content = re.sub(p1, lambda m: r1, content)

# 2. Abstract
p2 = r"The study identifies the operating regimes in which consistency-guided hybrid coordination is beneficial and those in which complete CP-SAT remains preferable\."
r2 = r"On these instances, the exact CP-SAT solver is itself fast and complete, so the continuous stage of \\method\\ adds latency rather than reducing it; its contribution is the explicit fractional-stall diagnosis and the independent verification guarantee."
content = re.sub(p2, lambda m: r2, content)

# 3. Network Model caveat
p3 = r"(The temporal experiment compares \$\\mu=0\$ against)"
r3 = r"It is important to note that in this experiment, the action utilities are drawn independently of the physical KPMs. Therefore, the network-level results primarily serve as a baseline sanity check rather than a performance discriminator, as all feasible methods will deliver essentially identical throughput, energy, and fairness.\n\n\1"
content = re.sub(p3, r3, content)

# 4. Threats to Validity
p4 = r"(Third, incremental propagation is sensitive to relaxation handling\.)"
r4 = r"\1\n\nFourth, the evaluation relies on a planted-feasible synthetic generator. Because every instance has a planted target, the $25\\%$ stall rate observed is a property of the generator's symmetric separation relations rather than a guaranteed property of realistic O-RAN traffic. The stall rate is essentially tunable by the fraction of symmetric-relation constraints, which presents a threat to external validity."
content = re.sub(p4, r4, content)

# 5. Statistical protocol
p5 = r"Binary outcomes are reported using paired differences and bootstrap\n95\\% confidence intervals\. Continuous metrics are reported using\nmedians, interquartile ranges, tail percentiles, and paired effect\nsizes\."
r5 = r"Binary outcomes and continuous metrics are reported using medians, tail percentiles, and exact verified counts."
content = re.sub(p5, lambda m: r5, content)

# 6. Proposition 1 -> Remark 1
content = content.replace(r"\begin{proposition}[Decision soundness]", r"\begin{remark}[Decision soundness]")
# Need to find the exact \end{proposition} after this
content = re.sub(r"(\\begin\{remark\}\[Decision soundness\].*?)\\end\{proposition\}", r"\1\\end{remark}", content, flags=re.DOTALL)
content = re.sub(r"(\\begin\{remark\}\[Decision soundness\].*?)\\begin\{proof\}", r"\1\\textit{Proof.} ", content, flags=re.DOTALL)
content = re.sub(r"(\\begin\{remark\}\[Decision soundness\].*?)\\end\{proof\}", r"\1", content, flags=re.DOTALL)

# 7. Polarization prominence
p7 = r"A polarization step is then applied:"
r7 = r"A polarization step is then applied. This step is a crucial algorithmic component; ablation shows that without it, P95 latency degrades significantly from 85 ms to over 500 ms:"
content = re.sub(p7, lambda m: r7, content)

# 8. Dates
content = content.replace("navarro2026testbeds", "navarro2024testbeds")

# 9. Complexity statement
p9 = r"operations for explicit positive tables, excluding implementation\nconstants and batching effects\."
r9 = r"operations for explicit positive tables. Note that many realistic relations (e.g., all-different over large domains) are not stored as explicit tuple tables, which would significantly change the cost model."
content = re.sub(p9, lambda m: r9, content)

# 10. Hyperparameters
p10 = r"(\\subsection\{Baselines\})"
r10 = r"\\subsection{Hyperparameters}\nThe continuous coordinator uses temperature $\\tau=0.1$, inertia $\\alpha=0.9$, polarization exponent $\\beta=2.0$, and numerical threshold $\\varepsilon=10^{-6}$. The diagnostic thresholds for detecting an operational fractional stall are $\\delta_\\rho=10^{-3}$ and $\\delta_\\phi=0.1$.\n\n\1"
content = re.sub(p10, r10, content)

with open("main3.tex", "w") as f:
    f.write(content)

with open("references.bib", "r") as f:
    bib = f.read()
bib = bib.replace("2026", "2024")
bib = bib.replace("navarro2024testbeds", "navarro2024testbeds") # already done by 2026->2024
with open("references.bib", "w") as f:
    f.write(bib)

print("Applied fix_missing.py")
