with open("main3.tex") as f:
    lines = f.readlines()
in_tab = False
for i, line in enumerate(lines):
    if "\\begin{tabular}" in line:
        in_tab = True
    if "\\end{tabular}" in line:
        in_tab = False
    if in_tab and line.strip() == "":
        print(f"Empty line at {i+1}")
