import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]


def setup_style():
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except Exception:
        plt.style.use('ggplot')
    plt.rcParams.update({
        'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
        'legend.fontsize': 12, 'xtick.labelsize': 12, 'ytick.labelsize': 12,
        'pdf.fonttype': 42,
    })


def _main(df):
    return df[df['Scenario'].isin(SCENARIOS)]


def plot_feasibility_stall(df, out_dir):
    main_df = _main(df)
    methods = ["Uncoordinated", "Static priority", "Continuous only", "CP-SAT", "VeriXApp"]
    labels = ["Uncoord.", "Static Prio.", "Continuous", "CP-SAT", "VeriXApp"]
    feas = [main_df[main_df['Method'] == m]['Feasible'].mean() * 100 for m in methods]
    stall = [main_df[main_df['Method'] == m]['Stall'].mean() * 100 for m in methods]
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, feas, width, label='Verified Feasible', color='#2ca02c', edgecolor='black')
    ax.bar(x + width / 2, stall, width, label='Stall Rate', color='#d62728', edgecolor='black')
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Feasibility and Stall Rates by Method')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15)
    ax.legend()
    ax.set_ylim(0, 105)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'fig_feasibility_stall.pdf'))
    plt.close()


def plot_latency_cdf(df, out_dir):
    main_df = _main(df)
    methods = ["Continuous only", "CP-SAT", "VeriXApp"]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    fig, ax = plt.subplots(figsize=(8, 5))
    for m, color in zip(methods, colors):
        data = np.sort(main_df[main_df['Method'] == m]['Latency_ms'].values)
        if len(data) == 0:
            continue
        y = np.arange(1, len(data) + 1) / float(len(data))
        label = 'VeriXApp (Ours)' if m == 'VeriXApp' else m
        ax.plot(np.maximum(data, 1e-3), y, label=label, color=color, linewidth=2)
    ax.set_xlabel('Decision Latency (ms)')
    ax.set_ylabel('CDF')
    ax.set_title('Cumulative Distribution of Latency')
    ax.set_xscale('log')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'fig_latency_cdf.pdf'))
    plt.close()


def plot_network_kpis(df, out_dir):
    main_df = _main(df)
    methods = ["Uncoordinated", "Static priority", "CP-SAT", "VeriXApp"]
    kpis = ['Throughput', 'Energy', 'Fairness']
    data = {k: [] for k in kpis}
    for m in methods:
        sub = main_df[main_df['Method'] == m]
        data['Throughput'].append(sub['Throughput'].mean())
        e = sub['Energy'].mean()
        data['Energy'].append(1.0 / e if e > 0 else 0.0)
        data['Fairness'].append(sub['Fairness'].mean())
    for k in kpis:
        mx = max(data[k]) if max(data[k]) > 0 else 1.0
        data[k] = [v / mx for v in data[k]]
    x = np.arange(len(kpis))
    width = 0.2
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, m in enumerate(methods):
        vals = [data[k][i] for k in kpis]
        label = 'VeriXApp (Ours)' if m == 'VeriXApp' else m
        ax.bar(x + (i - 1.5) * width, vals, width, label=label, edgecolor='black')
    ax.set_ylabel('Normalized Score (Higher is Better)')
    ax.set_title('Normalized Physical Network KPIs')
    ax.set_xticks(x)
    ax.set_xticklabels(['Throughput', 'Energy Efficiency', 'Jain Fairness'])
    ax.legend()
    ax.set_ylim(0, 1.2)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'fig_network_kpis.pdf'))
    plt.close()


def plot_scalability(res_dir):
    path = os.path.join(res_dir, 'scalability.csv')
    if not os.path.exists(path):
        return
    sdf = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sdf['Size'], sdf['VeriXApp median latency (ms)'], marker='o',
            markersize=8, linewidth=2, color='#2ca02c', label='VeriXApp latency')
    ax.plot(sdf['Size'], sdf['CP-SAT median latency (ms)'], marker='s',
            markersize=7, linewidth=2, color='#ff7f0e', label='CP-SAT latency')
    ax.set_xlabel('Number of xApp Action Variables')
    ax.set_ylabel('Median Decision Latency (ms)')
    ax.grid(True, linestyle='--')
    ax2 = ax.twinx()
    ax2.plot(sdf['Size'], sdf['Continuous stall (%)'], marker='^', markersize=7,
             linewidth=2, color='#d62728', linestyle='--', label='Continuous stall rate')
    ax2.set_ylabel('Fractional Stall Rate (%)')
    ax2.set_ylim(0, 105)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    ax.set_title('Scalability with Problem Size')
    plt.tight_layout()
    plt.savefig(os.path.join(res_dir, 'fig_scalability.pdf'))
    plt.close()


def plot_ablation(res_dir):
    path = os.path.join(res_dir, 'ablation.csv')
    if not os.path.exists(path):
        return
    adf = pd.read_csv(path).iloc[::-1]  # reverse for horizontal bars
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(adf))
    colors = ['#2ca02c' if c == 'Full VeriXApp' else '#7f7f7f'
              for c in adf['Configuration']]
    ax.barh(y, adf['Feasible (%)'], align='center', color=colors, edgecolor='black')
    ax.set_yticks(y)
    ax.set_yticklabels(adf['Configuration'])
    ax.set_xlabel('Verified Feasible Rate (%)')
    ax.set_title('Ablation Study: Impact of Algorithmic Components')
    lo = max(0, adf['Feasible (%)'].min() - 10)
    ax.set_xlim(lo, 105)
    plt.tight_layout()
    plt.savefig(os.path.join(res_dir, 'fig_ablation.pdf'))
    plt.close()


def main():
    setup_style()
    res_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    data_path = os.path.join(res_dir, 'raw_results.csv')
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return
    df = pd.read_csv(data_path)
    plot_feasibility_stall(df, res_dir)
    plot_latency_cdf(df, res_dir)
    plot_network_kpis(df, res_dir)
    plot_scalability(res_dir)
    plot_ablation(res_dir)
    print(f"Successfully generated 5 figures in {res_dir}")


if __name__ == '__main__':
    main()
