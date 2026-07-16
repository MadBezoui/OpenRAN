import re

def main():
    tex_file = "main3.tex"
    with open(tex_file, "r") as f:
        content = f.read()

    replacements = [
        # 1. 150,000 decision epochs -> 15,000 unique decision epochs...
        (r"Across 150,000 decision epochs,", 
         r"We generated 15,000 unique decision epochs and evaluated ten methods on matched instances, yielding 150,000 method-epoch observations. Across these observations,"),
        
        # 2. Fractional stall terminology (find "fractional stall" and replace with symmetry-preserving where appropriate, but maybe safer to add a sentence in section 11.1 equivalent)
        # Actually I can just add it before line 2603 "The analysis distinguishes:"
        (r"(The analysis distinguishes:)", 
         r"Note that mathematically, we refer to the non-converging state as a \textit{symmetry-preserving fractional fixed point}, while in experimental detection with finite precision, we use the term \textit{operational fractional stall}.\n\n\1"),

        # 3. Explanation validity
        (r"(The different-slot example\nproves that GAC can retain every value while a symmetric fractional\nstall persists.)",
         r"\1\n\nFor explanation validity, the verifier explicitly replays the stated premises, restricts the stated domains, and verifies that every tuple supporting the pruned value is disabled. This ensures validity without necessarily implying minimality."),

        # 4. Wipeout definition
        (r"(When propagation detects a domain wipeout,\nits explanations identify a sufficient set of constraints)",
         r"A wipeout in the complete base model establishes global infeasibility of the registered hard model. Explanation-guided recovery in this case requires an explicitly authorized request-retraction or fallback mechanism. By contrast, a wipeout in a boundary-fixed repair subproblem triggers core expansion and does not imply global infeasibility. \1"),

        # 5. Main scientific contribution
        # Wait, the conclusion has to be rewritten entirely anyway. Let's do the contribution part.
        (r"(The proposed framework is supported only in regimes where\nincremental propagation or explanation-guided localization provides\na measurable diagnostic, latency, stability, or deadline-compliance\nadvantage.)",
         r"\1\n\nCrucially, the contribution is not a new GAC algorithm, but an auditable O-RAN coordination architecture that uses incremental propagation explanations to localize exact repair while explicitly separating local-support failure from fractional joint-decoding failure."),

        # 6. GitHub repository
        (r"https://github\.com/google/openran-consistxapp",
         r"https://anonymous.4open.science/r/openran-consistxapp"),

        # 7. CRediT formatting (I will do a manual replace for author section if I can't catch it with regex easily, let's skip for python string replacer unless I know the exact text)
        
        # 8. References (Remove editorial notes)
        (r"Verify the complete author list before submission\.", ""),
        (r"Replace with the final pub-lished\nbib-li-o-graphic record if avail-able \(2025\)\.", "(2025)."),
        (r"Replace with the final published\nbibliographic record if available \(2025\)\.", "(2025)."),
        (r"Ver-ify page\nrange in the final pro-ceed-ings meta-data\.", ""),
        (r"Verify page range in the final proceedings metadata\.", ""),
        (r"N > 50", r"$N > 50$"),
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open(tex_file, "w") as f:
        f.write(content)

    print("Text fixes applied.")

if __name__ == "__main__":
    main()
