import re

with open("main3.tex", "r") as f:
    content = f.read()

# 1. Restore prop:persistence
# It was corrupted into:
# \begin{proposition}[Persistence of a symmetric stall after GAC]
# \label{prop:persistence}
# If a fractional probability assignment $P$ corresponds to a
# symmetric stall under base relations $\mathcal{C}$, then $P$
# remains a stall under GAC-filtered relations $\mathcal{C}^{*}$.
# \end{proposition}
#
# But wait! I replaced it with `multi_replace` AND THEN I ran `scripts/fix_latex.py` which had:
# content = re.sub(p_pers_bad, p_pers_good, content)
# So it might ALREADY be fixed! Let's check!

