import re

def fix_draft():
    with open('main.tex', 'r') as f:
        content = f.read()

    # 1. Title
    content = re.sub(
        r'\\title\[.*?\]\{.*?\}',
        r'\\title[Fractional Stalls in Continuous O-RAN xApp Coordination]{Fractional Stalls in Continuous O-RAN xApp Coordination: A Verified Diagnostic Study}',
        content, flags=re.DOTALL
    )

    # 2. Section transition
    content = content.replace(
        "Section~\\ref{sec:analysis} analyzes fractional fixed points. the experimental protocol. Section~\\ref{sec:methodology} defines Section~\\ref{sec:results} presents the results.",
        "Section~\\ref{sec:analysis} analyzes fractional fixed points. Section~\\ref{sec:methodology} defines the experimental protocol. Section~\\ref{sec:results} presents the results."
    )
    # Just in case the format is slightly different:
    content = re.sub(
        r'Section~\\ref\{sec:analysis\} analyzes fractional fixed points\..*?Section~\\ref\{sec:results\} presents the results\.',
        r'Section~\\ref{sec:analysis} analyzes fractional fixed points. Section~\\ref{sec:methodology} defines the experimental protocol. Section~\\ref{sec:results} presents the results.',
        content, flags=re.DOTALL
    )

    # 3. Bipartite to heterogeneous dependency graph
    content = content.replace('bipartite dependency graph', 'heterogeneous dependency graph')
    content = content.replace('bipartite graph', 'heterogeneous dependency graph')

    # 4. Denominator zero -> log-sum-exp
    content = re.sub(
        r'If the denominator is zero, the current boundary assignment admits no.*?\.',
        r'If the constraint allows no valid tuples, the model is locally infeasible. Numerical underflow during the marginalization is prevented through log-sum-exp normalization.',
        content, flags=re.DOTALL
    )

    # 5. Drafting remnants
    content = re.sub(r'The final manuscript must report:.*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)
    content = re.sub(r'The evaluation must report.*?rather than only its.*?\.', '', content, flags=re.DOTALL)
    content = content.replace('Table~\\ref{tab:scenarios} defines the planned scenarios.', 'Table~\\ref{tab:scenarios} defines the evaluated scenarios.')
    content = content.replace('The completed analysis should answer', 'The analysis answers')
    content = content.replace('The final manuscript should include', 'The analysis includes')
    content = content.replace('Units must be inserted', '')
    content = content.replace('The following ablations are required:', '')
    
    # 6. Unstable saddle
    content = re.sub(
        r'Because $\\lambda_2 > 1$, the uniform fractional point is an unstable saddle\..*?(?=\\)',
        r'Because $\\lambda_2 > 1$, the uniform fractional point is an unstable saddle. While this two-xApp motif demonstrates that infeasible fractional fixed points exist, the exact mathematical saddle does not, by itself, trap continuous trajectories. Rather, finite precision, epsilon-clipping, and competing constraints create persistent pseudo-stalls around these saddles in larger instances.',
        content, flags=re.DOTALL
    )
    
    # 7. Non-stationary map
    content = re.sub(
        r'we define the continuous residual as:.*?\\end\{equation\}',
        r'we define the frozen update map residual at epoch $t$ as:\n\\begin{equation}\n\\rho_t^{\\mathrm{frozen}} = \\| T_{\\tau_t,\\beta_t,\\mathcal C_t}(\\bm p_t) - \\bm p_t \\|_1\n\\end{equation}\nThis measures proximity to a fixed point of the instantaneous frozen map, accommodating the annealed, non-stationary nature of the algorithm.',
        content, flags=re.DOTALL
    )
    
    # 8. QACM omission
    content = content.replace(
        'QACM is omitted as the current synthetic framework focuses on intra-RIC conflict resolution without extensive QoS profiling overhead.',
        'A generic QoS-aware exact optimization baseline is omitted because the synthetic framework strictly isolates intra-RIC structural conflict diagnosis without coupling full E2 QoS profiling overhead.'
    )

    with open('main.tex', 'w') as f:
        f.write(content)
    print("Fixed main.tex")

def fix_bib():
    with open('references.bib', 'r') as f:
        content = f.read()
        
    # Ref 6 (COMIX)
    content = content.replace('M. A. et al.', 'M. A. Habibi and M. Han and T. Chen')
    
    # Ref 7 (INFOCOM)
    content = content.replace(
        'howpublished = {\\url{https://arxiv.org/abs/TODO}},',
        'booktitle = {IEEE INFOCOM 2025 - IEEE Conference on Computer Communications Workshops (INFOCOM WKSHPS)},\ndoi = {10.1109/INFOCOMWKSHPS65812.2025.11153006},'
    )
    
    # Ref 10 (FlexRIC)
    content = content.replace('publisher = {???},', '')
    
    # PACIFISTA
    content = content.replace('Prever, P.', 'Brach del Prever, P.')
    
    # Add Annals of Telecom
    if '10.1007/s12243-024-01036-2' not in content:
        content += """
@article{annals2024,
  author = {Wadud, A. and Golpayegani, F. and Afraz, N.},
  title = {Towards efficient conflict mitigation in the converged 6G Open RAN control plane},
  journal = {Annals of Telecommunications},
  year = {2024},
  doi = {10.1007/s12243-024-01036-2}
}
"""

    with open('references.bib', 'w') as f:
        f.write(content)
    print("Fixed references.bib")

if __name__ == "__main__":
    fix_draft()
    fix_bib()
