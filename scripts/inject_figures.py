import re

def main():
    tex_file = "main3.tex"
    with open(tex_file, "r") as f:
        content = f.read()
        
    # Find all \placeholderfigure instances
    # \placeholderfigure{...}{...} can span multiple lines.
    # regex: \\placeholderfigure\{.*?\}\{.*?\} with re.DOTALL
    
    figures = [
        "artifacts/figures/fig1_reduction.pdf",
        "artifacts/figures/fig2_deadline.pdf",
        "artifacts/figures/fig3_stall.pdf",
        "artifacts/figures/fig4_utility.pdf",
        "artifacts/figures/fig5_repair.pdf"
    ]
    
    # We will replace them one by one
    def replacer(match, idx=[0]):
        replacement = f"\\includegraphics[width=\\columnwidth]{{{figures[idx[0]]}}}"
        idx[0] += 1
        return replacement

    content_new = re.sub(r"\\placeholderfigure\{.*?\}\{.*?\}", replacer, content, flags=re.DOTALL)
    
    # Wait, the macro \placeholderfigure itself shouldn't cause problems now that it's unused,
    # but I'll make sure it worked.
    
    with open(tex_file, "w") as f:
        f.write(content_new)
        
    print("Figures injected into LaTeX successfully.")

if __name__ == "__main__":
    main()
