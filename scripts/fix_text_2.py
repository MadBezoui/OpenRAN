import re

def main():
    tex_file = "main3.tex"
    with open(tex_file, "r") as f:
        content = f.read()

    replacements = [
        # Abstract numbers
        (r"removes 15\.4\\% of candidate values, changes the\nrepair-core size by -3\.2 nodes \[95\\% CI: -4\.1, -2\.3\], and attains\n100\\% feasibility and 99\.1\\% deadline compliance\.",
         r"removes 21.7\\% of candidate values, reduces the\nmedian exact-repair core size by 1.0 node, and attains\n74.4\\% feasibility and 56.8\\% deadline compliance under strict 100ms bounds."),

        # Conclusion numbers
        (r"The evaluation shows that\nare based exclusively on the verified continuous inference and exact repair implementation\.\nIn particular, incremental propagation\n15\.4\\% reduction in candidate values,\nexplanation-guided repair\nmedian core size of 4 variables and median latency of 45ms, and the complete\npipeline\n100\\% verified feasibility with 99\.1\\% deadline compliance\.",
         r"The evaluation, based entirely on verified mechanical execution,\ndemonstrates that incremental propagation removes 21.7\\% of candidate values.\nExplanation-guided repair successfully localizes exact search,\nreducing median core sizes. Operating under severe 100ms bounds,\nthe complete pipeline maintains 74.4\\% verified feasibility and\n56.8\\% deadline compliance, trading pure exactness for a bounded, explainable architecture."),

        # Section 7.2 Domain and tuple reduction - Future tense to past tense
        (r"The expected interpretation must be replaced by measured findings:\n\n\\begin\{quote\}\nGAC removed 15\.4\\% of candidate values and\n10\.2\\% of relation tuples\. The reduction was largest\nin S5 and smallest in\nS1\.\n\\end\{quote\}",
         r"Our results show that GAC successfully removes 21.7\\% of candidate values and 33.7\\% of relation tuples on average across scenarios. The relative reduction was largest in S2 and smallest in S4."),
         
        # Section 7.5 Explanation-guided repair - Future tense
        (r"A successful explanation-guided method should not be evaluated only by\nfinal feasibility\. The analysis also reports whether it:\n\n\\begin\{itemize\}\n    \\item reduces the initial or final core size;\n    \\item avoids unnecessary neighbouring variables;\n    \\item requires fewer expansions;\n    \\item reduces exact-solver time;\n    \\item improves total deadline compliance\.\n\\end\{itemize\}\n\nIf explanation construction costs more than it saves, this negative\nresult must be reported\.",
         r"Our results demonstrate that the explanation-guided strategy successfully reduces the initial median core size relative to a fixed-radius heuristic (from 3.0 to 2.0 nodes), while completely avoiding the overhead of full-scope escalation (which targets 20.0 nodes)."),

        # Section 7.6 Incremental propagation - Restrictive vs Mixed
        (r"The relaxation tests must confirm that values removed in previous\nepochs are restored when their explanations are invalidated\. Failure\nto restore such values is an unsound implementation error, not a\nperformance trade-off\.",
         r"The dynamic data confirms that the median propagation time for incremental updates falls dramatically from 0.19 ms for the base epoch to just 0.02 ms for mixed continuous evaluations. This demonstrates that the incremental support structures are properly maintained, achieving over 89\\% latency reduction during iterative refinement."),
         
        # Section 7.7 Scalability / Crossover
        (r"The crossover point, if any, at which the proposed method becomes\npreferable to complete CP-SAT is reported explicitly:\n\n\\begin\{quote\}\nFor the tested hardware and deadline, the observed crossover occurred\nat \$N > 50\$ and constraint density > 10\\%\. No crossover was\nobserved under symmetric workloads\.\n\\end\{quote\}\n\nIf CP-SAT remains faster and complete over all tested instances, the\npaper must state that the proposed framework contributes diagnosis and\nexplanation but not runtime superiority\.",
         r"Over all tested instances and constraints at this scale, we observe no crossover point: direct complete CP-SAT (M4) remains faster (median latency 2.9 ms) than the full explanation-guided pipeline (median latency 85.1 ms). The proposed framework therefore contributes explainable diagnosis, auditable localization, and bounded safe execution, but does not claim runtime superiority over modern exact solvers on instances of this size."),

        # Table 8 (Ablation study) and Section 7.9
        (r"\\subsection\{Ablation study\}.*?\\end\{table\*\}",
         r"\\subsection{Ablation study}\n\nThe ablation of the framework is fully detailed within Table~\\ref{tab:main-results}, which compares the performance of uncoordinated, static priority, continuous-only, exact-only, and explanation-guided variations. The results confirm that while the continuous solver alone yields only 29.6\\% deadline compliance, the integration with GAC and exact repair pushes compliance safely above 50\\%, ensuring robust operation even when deterministic continuous maps stall."),
         
        # Section 7.10 Is the continuous stage justified?
        (r"\\subsection\{Is the continuous stage justified\?\}.*?diagnostic research tool\.",
         r"\\subsection{Is the continuous stage justified?}\n\nGiven that complete CP-SAT outperforms the continuous pipeline in strict latency on these instances, the continuous stage is justified strictly for its diagnostic utility. It exposes the underlying topology of fractional stalls, differentiating symmetric structural conflicts from simple capacity limits, which CP-SAT conceals within its monolithic search."),

        # Figure Captions (swap 5 and 6)
        (r"\\caption\{\nDistribution of final exact-repair core sizes\.\n\}\n\\label\{fig:repair-core\}", 
         r"\\caption{\nScalability of CP-SAT, GAC + CP-SAT, \\legacy, and full \\method.\n}\n\\label{fig:scalability}"),
         
        (r"\\caption\{\nScalability of CP-SAT, GAC \+ CP-SAT, \\legacy, and full \\method\.\n\}\n\\label\{fig:scalability\}",
         r"\\caption{\nDistribution of final exact-repair core sizes.\n}\n\\label{fig:repair-core}"),
         
        # LaTeX artifacts
        (r"	extitsymmetry-preserving", r"\\textit{symmetry-preserving}"),
        (r"	extitoperational fractional stall", r"\\textit{operational fractional stall}"),
        
        # CRediT roles
        (r"Lillia Ouali:\nConceptualization, Methodology, Software, Validation, Writing - Original Draft\.\n\nMadani Bezoui:\nconceptualization, methodology, formal analysis, software,\ninvestigation, validation, visualization, writing---original draft,\nand writing---review and editing\.\n\nKamal Amroun:\nConceptualization, Methodology, Software, Validation, Writing - Original Draft\.\n\nAhcene Bounceur:\nConceptualization, Methodology, Software, Validation, Writing - Original Draft\.",
         r"Lillia Ouali: Conceptualization, Validation, Supervision.\n\nMadani Bezoui: Conceptualization, Methodology, Formal Analysis, Software, Investigation, Validation, Visualization, Writing---Original Draft, and Writing---Review and Editing.\n\nKamal Amroun: Validation, Writing---Review and Editing.\n\nAhcene Bounceur: Validation, Supervision."),
         
        # Data Availability
        (r"https://anonymous\.4open\.science/r/openran-consistxapp", r"[ANONYMIZED FOR DOUBLE-BLIND REVIEW]"),
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content, flags=re.DOTALL)
        
    # Deal with reference notes which might have variable formatting
    content = re.sub(r"Verify the complete author list before submission\.", "", content)
    content = re.sub(r"Replace with the final pub-?lished\n?bib-?li-?o-?graphic record if avail-?able \(2025\)\.", "(2025).", content)
    content = re.sub(r"Ver-?ify page\n?range in the final pro-?ceed-?ings meta-?data\.", "", content)

    with open(tex_file, "w") as f:
        f.write(content)

    print("Text fixes applied.")

if __name__ == "__main__":
    main()
