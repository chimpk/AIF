"""Script to generate figures for the IEEE final project report."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set academic style
style_name = (
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.style.use(style_name)
plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.titlesize": 11,
})

root = Path(__file__).resolve().parents[1]
fig_dir = root / "report" / "figures"
(fig_dir / "task1").mkdir(parents=True, exist_ok=True)
(fig_dir / "task2").mkdir(parents=True, exist_ok=True)
(fig_dir / "task3").mkdir(parents=True, exist_ok=True)

# 1. Task 1: SAT Clauses & Scaling
sat_df = pd.read_csv(root / "experiments" / "results" / "task1" / "task1_sat.csv")
fig, ax1 = plt.subplots(figsize=(4.5, 3), dpi=300)
color = "tab:blue"
ax1.set_xlabel("Board Size N")
ax1.set_ylabel("CNF Clauses", color=color)
ax1.plot(
    sat_df["n"],
    sat_df["num_clauses"],
    marker="o",
    color=color,
    linewidth=1.5,
    label="CNF Clauses",
)
ax1.tick_params(axis="y", labelcolor=color)

ax2 = ax1.twinx()
color = "tab:red"
ax2.set_ylabel("Solve Time (s)", color=color)
ax2.plot(
    sat_df["n"],
    sat_df["solve_time_s"],
    marker="s",
    color=color,
    linestyle="--",
    linewidth=1.5,
    label="Time (s)",
)
ax2.tick_params(axis="y", labelcolor=color)

fig.tight_layout()
plt.title("Glucose3 SAT Solver: Clauses & Scaling")
plt.savefig(fig_dir / "task1" / "sat_scaling.png", bbox_inches="tight")
plt.close()

# 2. Task 1: Min-Conflicts: Random vs Max-Conflict Heuristic
mc_df = pd.read_csv(root / "experiments" / "results" / "task1" / "task1_min_conflicts_summary.csv")
fig, ax = plt.subplots(figsize=(4.5, 3), dpi=300)
for method, label, marker, color in [
    ("MC_RANDOM", "Standard (Random)", "o", "tab:blue"),
    ("MC_MAX_CONFLICT", "Proposed (Max-Conflict)", "s", "tab:orange"),
]:
    sub = mc_df[mc_df["method"] == method]
    ax.plot(sub["n"], sub["mean_steps"], marker=marker, color=color, linewidth=1.5, label=label)

ax.set_xlabel("Board Size N")
ax.set_ylabel("Mean Search Steps")
ax.set_title("Min-Conflicts: Variable Selection Comparison")
ax.legend()
fig.tight_layout()
plt.savefig(fig_dir / "task1" / "min_conflicts_comparison.png", bbox_inches="tight")
plt.close()

# 3. Task 2: Search Nodes Expanded (Minimax vs AlphaBeta)
search_df = pd.read_csv(root / "experiments" / "results" / "task2" / "task2_search_summary.csv")
s1_df = search_df[search_df["scenario"] == "s1_duel_5x5"]
fig, ax = plt.subplots(figsize=(4.5, 3), dpi=300)

for cfg, label, color in [
    ("MINIMAX", "Minimax", "tab:red"),
    ("ALPHABETA", "Alpha-Beta", "tab:blue"),
    ("H_MINIMAX", "Heuristic Minimax", "tab:orange"),
    ("H_ALPHABETA", "Heuristic Alpha-Beta", "tab:green"),
]:
    sub = s1_df[s1_df["config"] == cfg]
    if not sub.empty:
        ax.plot(
            sub["depth_ply"],
            sub["mean_nodes"],
            marker="o",
            color=color,
            linewidth=1.5,
            label=label,
        )

ax.set_yscale("log")
ax.set_xlabel("Search Depth (Plies)")
ax.set_ylabel("Mean Nodes Expanded (Log scale)")
ax.set_title("Adversarial Search: Pruning Efficiency")
ax.legend()
fig.tight_layout()
plt.savefig(fig_dir / "task2" / "search_nodes_comparison.png", bbox_inches="tight")
plt.close()

# 4. Task 3: Kakuro Presets Performance on Large 9x9
k_df = pd.read_csv(root / "experiments" / "results" / "task3" / "task3_kakuro_benchmark.csv")
k_large = (
    k_df[k_df["puzzle"] == "large_9x9"]
    .groupby("preset")[["nodes", "backtracks", "elapsed_ms"]]
    .mean()
)
order = ["bt", "fc", "fc-mrv", "mac-mrv", "mac-mrvdeg-lcv"]
k_large = k_large.reindex(order)

fig, ax = plt.subplots(figsize=(4.8, 3), dpi=300)
x = np.arange(len(order))
labels = ["BT", "FC", "FC+MRV", "MAC+MRV", "MAC+MRV\n+DEG+LCV"]
ax.bar(x, k_large["nodes"], color="tab:purple", width=0.55, edgecolor="black")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Mean Search Nodes (Log scale)")
ax.set_title("Kakuro 9x9: CSP Solver Presets Comparison")
fig.tight_layout()
plt.savefig(fig_dir / "task3" / "kakuro_presets_nodes.png", bbox_inches="tight")
plt.close()

print("All report figures successfully generated in report/figures/!")
