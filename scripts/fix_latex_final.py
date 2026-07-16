import re

with open("main3.tex", "r") as f:
    content = f.read()

# 1. Restore prop:persistence
p_pers_bad = r"\\label\{prop:persistence\}\nIf a fractional probability assignment \$P\$ corresponds to a\nsymmetric stall under base relations \$\\mathcal\{C\}\$, then \$P\$\nremains a stall under GAC-filtered relations \$\\mathcal\{C\}\^\{\*\}\."
p_pers_good = r"\\label{prop:persistence}\nThe different-slot instance above is generalized arc consistent, but\nGAC removes no value and does not prevent invalid deterministic\ndecoding of the uniform continuous state."
content = re.sub(p_pers_bad, p_pers_good, content)

# 2. Restore prop:restoration
p_rest_bad = r"\\label\{prop:restoration\}\nLet \$v\$ be removed by arc-consistency under relations \$\\mathcal\{C\}\$.\nIf the relation set is relaxed to \$\\mathcal\{C\}\^\{\+\} \\supset \\mathcal\{C\}\$,\n\$v\$ cannot be safely omitted from evaluation without a restoration\nor re-evaluation step verifying its continued unsupported status\nunder \$\\mathcal\{C\}\^\{\+\}\."
p_rest_good = r"\\label{prop:restoration}\nSuppose a value $a$ is removed at epoch $t-1$ because it has no\nsupport in relation $R_c(\\bm{s}_{t-1})$. If the relation is relaxed at\nepoch $t$, retaining the deletion without re-evaluating the base value\nmay remove a value that belongs to a feasible assignment of\n$\\mathcal{M}_t$."
content = re.sub(p_rest_bad, p_rest_good, content)

# 3. Fix \end{proposition} back to \end{remark} where it was broken
# There are two specific ones:
# 1) Local versus global consistency
p_remark1 = r"(\\begin\{remark\}\[Local versus global consistency\].*?)\\end\{proposition\}"
content = re.sub(p_remark1, r"\1\\end{remark}", content, flags=re.DOTALL)

# 2) The remark starting with "A repair restricted to a proper subset"
p_remark2 = r"(\\begin\{remark\}\s+A repair restricted to a proper subset.*?)\\end\{proposition\}"
content = re.sub(p_remark2, r"\1\\end{remark}", content, flags=re.DOTALL)

with open("main3.tex", "w") as f:
    f.write(content)
