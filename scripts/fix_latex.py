import re

with open("main3.tex", "r") as f:
    content = f.read()

# Fix prop:persistence body
p_pers_bad = r"\\begin\{proposition\}\[Persistence of a symmetric stall after GAC\]\n\\label\{prop:persistence\}\nIf a fractional probability assignment \$P\$ corresponds to a\nsymmetric stall under base relations \$\\mathcal\{C\}\$, then \$P\$\nremains a stall under GAC-filtered relations \$\\mathcal\{C\}\^\{\*\}\.\n\\end\{proposition\}"
p_pers_good = r"\\begin{proposition}[Persistence of a symmetric stall after GAC]\n\\label{prop:persistence}\nThe different-slot instance above is generalized arc consistent, but\nGAC removes no value and does not prevent invalid deterministic\ndecoding of the uniform continuous state.\n\\end{proposition}"
content = re.sub(p_pers_bad, p_pers_good, content)

# Fix prop:restoration body
p_rest_bad = r"\\begin\{proposition\}\[Necessity of restoration after relaxation\]\n\\label\{prop:restoration\}\nLet \$v\$ be removed by arc-consistency under relations \$\\mathcal\{C\}\$.\nIf the relation set is relaxed to \$\\mathcal\{C\}\^\{\+\} \\supset \\mathcal\{C\}\$,\n\$v\$ cannot be safely omitted from evaluation without a restoration\nor re-evaluation step verifying its continued unsupported status\nunder \$\\mathcal\{C\}\^\{\+\}\.\n\\end\{proposition\}"
p_rest_good = r"\\begin{proposition}[Necessity of restoration after relaxation]\n\\label{prop:restoration}\nSuppose a value $a$ is removed at epoch $t-1$ because it has no\nsupport in relation $R_c(\\bm{s}_{t-1})$. If the relation is relaxed at\nepoch $t$, retaining the deletion without re-evaluating the base value\nmay remove a value that belongs to a feasible assignment of\n$\\mathcal{M}_t$.\n\\end{proposition}"
content = re.sub(p_rest_bad, p_rest_good, content)

# I messed up remarks. Let's fix them.
# The only remark that should be Proposition is "Decision soundness".
# All others should be Remark.
# So let's find \begin{remark} and \end{remark} that were changed to proposition.
# The previous multi_replace replaced \end{proof} with \end{remark} and \end{proposition} with \end{remark}?!
# No, let's look at the diff:
# -\end{proof}
# +\end{remark}
# \begin{remark}
# ...
# -\end{proposition}
# +\end{remark}

# That was because my multi_replace was trying to fix what my python script broke!
# But it did a very bad job because I didn't specify it carefully.
