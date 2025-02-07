"""
Statistical analysis and visualisation for the D-P Gap study.

Computes:
  • Declarative Accuracy  (DA)
  • Procedural Accuracy   (PA)
  • Primed Accuracy       (PrA)
  • D-P Gap  = DA − PA
  • Priming Effect = PrA − PA
  • Per-rule and per-complexity breakdowns
  • Statistical tests (paired t-tests, Wilcoxon, ANOVA, correlations)
  • Publication-quality figures (Scissors Graph, Heatmap, Complexity Scatter)

Usage:
    python -m src.analysis --input results/experiment_results.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

logger = logging.getLogger(__name__)
sns.set_theme(style="whitegrid", font_scale=1.1)

# Colour palette
C_DEC = "#2563eb"   # blue  — declarative
C_PRO = "#dc2626"   # red   — procedural
C_PRI = "#16a34a"   # green — primed


def load_results(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


# ── Aggregate metrics ────────────────────────────────────────────────────────

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-rule aggregated metrics."""
    rows = []
    for rule_id, grp in df.groupby("rule_id"):
        da = grp.loc[grp["condition"] == "declarative", "score"].mean()
        pa = grp.loc[grp["condition"] == "procedural", "score"].mean()
        pra = grp.loc[grp["condition"] == "primed", "score"].mean()
        rule_name = grp["rule_name"].iloc[0]
        complexity = grp["complexity"].iloc[0]
        rows.append({
            "rule_id": rule_id,
            "rule_name": rule_name,
            "complexity": complexity,
            "DA": da,
            "PA": pa,
            "PrA": pra,
            "DP_Gap": da - pa,
            "Priming_Effect": pra - pa,
        })
    return pd.DataFrame(rows).sort_values("rule_id").reset_index(drop=True)


def print_summary(metrics: pd.DataFrame) -> None:
    """Print a formatted summary table."""
    print("\n" + "=" * 80)
    print("  D-P GAP EXPERIMENT — RESULTS SUMMARY")
    print("=" * 80)
    print(f"\n{'Rule':<30} {'DA':>6} {'PA':>6} {'PrA':>6} {'Gap':>7} {'Prime':>7}")
    print("-" * 70)
    for _, r in metrics.iterrows():
        print(
            f"  {r['rule_name']:<28} {r['DA']:>5.2f} {r['PA']:>5.2f} "
            f"{r['PrA']:>5.2f} {r['DP_Gap']:>+6.2f} {r['Priming_Effect']:>+6.2f}"
        )
    print("-" * 70)
    print(
        f"  {'OVERALL MEAN':<28} {metrics['DA'].mean():>5.2f} {metrics['PA'].mean():>5.2f} "
        f"{metrics['PrA'].mean():>5.2f} {metrics['DP_Gap'].mean():>+6.2f} "
        f"{metrics['Priming_Effect'].mean():>+6.2f}"
    )
    print("=" * 80)


# ── Statistical tests ────────────────────────────────────────────────────────

def run_statistics(df: pd.DataFrame, metrics: pd.DataFrame) -> dict:
    """Run core statistical tests."""
    results = {}

    # 1. Paired t-test: DA vs PA
    da_scores = metrics["DA"].values
    pa_scores = metrics["PA"].values
    pra_scores = metrics["PrA"].values

    t_da_pa, p_da_pa = stats.ttest_rel(da_scores, pa_scores)
    results["DA_vs_PA_ttest"] = {"t": t_da_pa, "p": p_da_pa}

    # 2. Paired t-test: PrA vs PA (priming effect)
    t_pra_pa, p_pra_pa = stats.ttest_rel(pra_scores, pa_scores)
    results["PrA_vs_PA_ttest"] = {"t": t_pra_pa, "p": p_pra_pa}

    # 3. Wilcoxon signed-rank (non-parametric alternative)
    if len(da_scores) >= 6:
        try:
            w_stat, p_wilcox = stats.wilcoxon(da_scores, pa_scores)
            results["DA_vs_PA_wilcoxon"] = {"W": w_stat, "p": p_wilcox}
        except ValueError:
            results["DA_vs_PA_wilcoxon"] = {"note": "Insufficient variance"}

    # 4. Spearman correlation: complexity vs D-P Gap
    rho, p_rho = stats.spearmanr(metrics["complexity"], metrics["DP_Gap"])
    results["complexity_vs_gap_spearman"] = {"rho": rho, "p": p_rho}

    # 5. Cohen's d for DA-PA
    diff = da_scores - pa_scores
    d = diff.mean() / diff.std() if diff.std() > 0 else 0
    results["DA_PA_cohens_d"] = d

    # 6. One-way ANOVA across conditions
    dec = df.loc[df["condition"] == "declarative", "score"]
    pro = df.loc[df["condition"] == "procedural", "score"]
    pri = df.loc[df["condition"] == "primed", "score"]
    f_stat, p_anova = stats.f_oneway(dec, pro, pri)
    results["one_way_ANOVA"] = {"F": f_stat, "p": p_anova}

    _print_stats(results)
    return results


def _print_stats(results: dict) -> None:
    print("\n" + "=" * 60)
    print("  STATISTICAL TESTS")
    print("=" * 60)
    for key, val in results.items():
        if isinstance(val, dict):
            parts = "  ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in val.items())
            print(f"  {key}: {parts}")
        else:
            print(f"  {key}: {val:.4f}")
    print("=" * 60)


# ── Figures ──────────────────────────────────────────────────────────────────

def plot_scissors(metrics: pd.DataFrame, output_dir: Path) -> None:
    """
    The Scissors Graph — the signature visualisation.
    X-axis: rules sorted by complexity.
    Y-axis: accuracy.
    Two lines: DA (blue, solid) and PA (red, dashed) that diverge like scissors.
    Third line: PrA (green, dotted) showing recovery.
    """
    m = metrics.sort_values("complexity")
    fig, ax = plt.subplots(figsize=(12, 6))

    x = range(len(m))
    ax.plot(x, m["DA"], "o-", color=C_DEC, label="Declarative (DA)", linewidth=2)
    ax.plot(x, m["PA"], "s--", color=C_PRO, label="Procedural (PA)", linewidth=2)
    ax.plot(x, m["PrA"], "^:", color=C_PRI, label="Primed (PrA)", linewidth=2)

    # Shade the gap between DA and PA
    ax.fill_between(x, m["DA"], m["PA"], alpha=0.12, color="#f59e0b", label="D-P Gap")

    ax.set_xticks(list(x))
    ax.set_xticklabels(
        [f"{r['rule_name']}\n(C={r['complexity']})" for _, r in m.iterrows()],
        rotation=45,
        ha="right",
        fontsize=8,
    )
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_xlabel("Logical Rule (sorted by complexity)", fontsize=12)
    ax.set_title("The Scissors Graph: Declarative vs. Procedural Accuracy", fontsize=14)
    ax.set_ylim(-0.05, 1.1)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output_dir / "scissors_graph.pdf", dpi=300)
    fig.savefig(output_dir / "scissors_graph.png", dpi=300)
    plt.close(fig)
    print(f"  → Saved scissors_graph.pdf/png")


def plot_heatmap(metrics: pd.DataFrame, output_dir: Path) -> None:
    """Heatmap: rules × conditions."""
    m = metrics.sort_values("complexity")
    data = m[["DA", "PA", "PrA"]].values
    fig, ax = plt.subplots(figsize=(6, 10))
    sns.heatmap(
        data,
        annot=True,
        fmt=".2f",
        xticklabels=["Declarative", "Procedural", "Primed"],
        yticklabels=[f"{r['rule_name']}" for _, r in m.iterrows()],
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        ax=ax,
    )
    ax.set_title("Accuracy Heatmap by Rule × Condition", fontsize=14)
    fig.tight_layout()
    fig.savefig(output_dir / "heatmap.pdf", dpi=300)
    fig.savefig(output_dir / "heatmap.png", dpi=300)
    plt.close(fig)
    print(f"  → Saved heatmap.pdf/png")


def plot_complexity_scatter(metrics: pd.DataFrame, output_dir: Path) -> None:
    """Scatter: complexity vs D-P Gap with regression line."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(metrics["complexity"], metrics["DP_Gap"], s=80, c=C_PRO, alpha=0.7, edgecolors="k")

    # Regression
    slope, intercept, r_val, p_val, _ = stats.linregress(metrics["complexity"], metrics["DP_Gap"])
    xs = np.linspace(metrics["complexity"].min() - 0.5, metrics["complexity"].max() + 0.5, 100)
    ax.plot(xs, intercept + slope * xs, "--", color=C_DEC, linewidth=2,
            label=f"r = {r_val:.2f}, p = {p_val:.3f}")

    for _, r in metrics.iterrows():
        ax.annotate(r["rule_name"], (r["complexity"], r["DP_Gap"]),
                     fontsize=7, ha="left", va="bottom")

    ax.set_xlabel("Rule Complexity", fontsize=12)
    ax.set_ylabel("D-P Gap (DA − PA)", fontsize=12)
    ax.set_title("Does Complexity Predict the D-P Gap?", fontsize=14)
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "complexity_scatter.pdf", dpi=300)
    fig.savefig(output_dir / "complexity_scatter.png", dpi=300)
    plt.close(fig)
    print(f"  → Saved complexity_scatter.pdf/png")


def plot_priming_bars(metrics: pd.DataFrame, output_dir: Path) -> None:
    """Grouped bar chart: PA vs PrA per rule (priming effect)."""
    m = metrics.sort_values("complexity")
    x = np.arange(len(m))
    w = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - w / 2, m["PA"], w, label="Procedural (PA)", color=C_PRO, alpha=0.8)
    ax.bar(x + w / 2, m["PrA"], w, label="Primed (PrA)", color=C_PRI, alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{r['rule_name']}" for _, r in m.iterrows()],
        rotation=45, ha="right", fontsize=8,
    )
    ax.set_ylabel("Accuracy")
    ax.set_title("Priming Effect: Does a Rule Reminder Help?", fontsize=14)
    ax.legend()
    ax.set_ylim(0, 1.15)
    fig.tight_layout()
    fig.savefig(output_dir / "priming_bars.pdf", dpi=300)
    fig.savefig(output_dir / "priming_bars.png", dpi=300)
    plt.close(fig)
    print(f"  → Saved priming_bars.pdf/png")


def plot_overall_summary(metrics: pd.DataFrame, output_dir: Path) -> None:
    """Overall bar chart: mean DA, PA, PrA with error bars."""
    means = [metrics["DA"].mean(), metrics["PA"].mean(), metrics["PrA"].mean()]
    sems = [
        metrics["DA"].sem(),
        metrics["PA"].sem(),
        metrics["PrA"].sem(),
    ]
    labels = ["Declarative\n(DA)", "Procedural\n(PA)", "Primed\n(PrA)"]
    colors = [C_DEC, C_PRO, C_PRI]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, means, yerr=sems, capsize=5, color=colors, alpha=0.85, edgecolor="k")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Mean Accuracy (± SEM)")
    ax.set_title("Overall Performance by Condition", fontsize=14)

    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                f"{m:.2f}", ha="center", fontsize=11, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_dir / "overall_summary.pdf", dpi=300)
    fig.savefig(output_dir / "overall_summary.png", dpi=300)
    plt.close(fig)
    print(f"  → Saved overall_summary.pdf/png")


# ── Main pipeline ────────────────────────────────────────────────────────────

def run_analysis(input_path: Path, output_dir: Path | None = None) -> None:
    """Run the full analysis pipeline."""
    output_dir = output_dir or input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_results(input_path)
    print(f"Loaded {len(df)} data points from {input_path}")

    metrics = compute_metrics(df)
    print_summary(metrics)

    # Save metrics table
    metrics.to_csv(output_dir / "metrics_summary.csv", index=False)

    # Run stats
    stat_results = run_statistics(df, metrics)

    # Generate all figures
    print("\nGenerating figures...")
    plot_scissors(metrics, output_dir)
    plot_heatmap(metrics, output_dir)
    plot_complexity_scatter(metrics, output_dir)
    plot_priming_bars(metrics, output_dir)
    plot_overall_summary(metrics, output_dir)
    print("\n✓ Analysis complete!")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Analyse D-P Gap results")
    parser.add_argument("--input", required=True, help="Path to experiment_results.csv")
    parser.add_argument("--output-dir", default=None, help="Output directory for figures")
    args = parser.parse_args()
    run_analysis(Path(args.input), Path(args.output_dir) if args.output_dir else None)
