import re

def main():
    with open('main.tex', 'r') as f:
        content = f.read()

    # 1. Feasibility and Latency
    fig1 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.9\columnwidth]{experiments/results/fig_feasibility_stall.pdf}
\caption{Verified feasibility and stall rates across arbitration methods. \method\ successfully repairs stalls to approach the feasibility of the exact solver.}
\label{fig:feasibility}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=0.9\columnwidth]{experiments/results/fig_latency_cdf.pdf}
\caption{Cumulative distribution of decision latency. \method\ reduces median latency compared to full CP-SAT while retaining an acceptable tail.}
\label{fig:latency}
\end{figure}
"""
    # Insert after Table 3
    content = content.replace(r'\end{table*}', r'\end{table*}' + '\n' + fig1, 1)

    # 2. Scalability
    fig2 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.9\columnwidth]{experiments/results/fig_scalability.pdf}
\caption{Scalability of the verified feasible rate as network traffic load increases from 30\% to 90\%.}
\label{fig:scalability}
\end{figure}
"""
    # Insert after Table 4 (tab:stalls)
    content = re.sub(r'(\\label\{tab:stalls\}.*?\\end\{table\})', lambda m: m.group(1) + '\n' + fig2, content, flags=re.DOTALL)

    # 3. Network KPIs
    fig3 = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=0.8\textwidth]{experiments/results/fig_network_kpis.pdf}
\caption{Normalized physical network performance metrics. \method\ achieves a competitive balance of throughput and fairness.}
\label{fig:network_kpis}
\end{figure*}
"""
    # Insert after Table 5 (tab:network-results)
    content = re.sub(r'(\\label\{tab:network-results\}.*?\\end\{table\*\})', lambda m: m.group(1) + '\n' + fig3, content, flags=re.DOTALL)

    # 4. Ablation
    fig4 = r"""
\begin{figure}[t]
\centering
\includegraphics[width=0.9\columnwidth]{experiments/results/fig_ablation.pdf}
\caption{Ablation study demonstrating the contribution of each algorithmic component to the final feasible rate.}
\label{fig:ablation}
\end{figure}
"""
    # Insert after Table 7 (tab:ablation)
    content = re.sub(r'(\\label\{tab:ablation\}.*?\\end\{table\})', lambda m: m.group(1) + '\n' + fig4, content, flags=re.DOTALL)

    # Add references in the text
    content = content.replace(r'Table~\ref{tab:main-results} reports the main results.', 
                              r'Table~\ref{tab:main-results} and Figures~\ref{fig:feasibility}--\ref{fig:latency} report the main results.')
    content = content.replace(r'This analysis is essential:', 
                              r'Figure~\ref{fig:scalability} illustrates the scalability limits under high load. This analysis is essential:')
    content = content.replace(r'experimental setup is finalized.', 
                              r'experimental setup is finalized. Figure~\ref{fig:network_kpis} provides a visual normalized comparison.')
    content = content.replace(r'Table~\ref{tab:ablation} presents', 
                              r'Table~\ref{tab:ablation} and Figure~\ref{fig:ablation} present')
    
    with open('main.tex', 'w') as f:
        f.write(content)
        
    print("Figures inserted successfully.")

if __name__ == '__main__':
    main()
