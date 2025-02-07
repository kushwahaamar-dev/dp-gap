"""
Cross-tier analysis for the D-P Gap experiment.

Produces:
  • Per-tier summaries (reuses src.analysis for each tier)
  • Cross-tier comparison figures:
      1. Three-panel scissors graph (Tier I / II / III side by side)
      2. Tier × Condition bar chart (the "money figure")
      3. Gap-by-tier heatmap
      4. Complexity × Tier interaction plot

Usage:
    python -m src.analysis_tiered --results-dir results
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

from .analysis import compute_metrics, run_statistics, print_summary

logger = logging.getLogger(__name__)
sns.set_theme(style="whitegrid", font_scale=1.1)

C_T1 = "#3b82f6"  # blue — Tier I
C_T2 = "#f59e0b"  # amber — Tier II
C_T3 = "#ef4444"  # red — Tier III

C_DEC = "#2563eb"
C_PRO = "#dc2626"
C_PRI = "#16a34a"

TIER_LABELS = {"tier1": "Tier I\n(Natural)", "tier2": "Tier II\n(Abstract)", "tier3": "Tier III\n(Adversarial)"}
TIER_COLORS = {"tier1": C_T1, "tier2": C_T2, "tier3": C_T3}


def load_tier_results(results_dir: Path) -> dict[str, pd.DataFrame]:
    """Load experiment results for each tier that exists."""
    tiers = {}
    for tier_name in ["tier1", "tier2", "tier3"]:
        path = results_dir / tier_name / "experiment_results.csv"
        if path.exists():
            df = pd.read_csv(path)
            tiers[tier_name] = df
            logger.info("Loaded %d rows from %s", len(df), path)
    return tiers


def plot_triple_scissors(tier_metrics: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Three-panel scissors graph — one per tier."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    for ax, (tier_name, metrics) in zip(axes, tier_metrics.items()):
        m = metrics.sort_values("complexity")
        x = range(len(m))

        ax.plot(x, m["DA"], "o-", color=C_DEC, label="DA", linewidth=2, markersize=5)
        ax.plot(x, m["PA"], "s--", color=C_PRO, label="PA", linewidth=2, markersize=5)
        ax.plot(x, m["PrA"], "^:", color=C_PRI, label="PrA", linewidth=2, markersize=5)
        ax.fill_between(x, m["DA"], m["PA"], alpha=0.12, color="#f59e0b")

        ax.set_xticks(list(x))
        ax.set_xticklabels(
            [f"C={r['complexity']}" for _, r in m.iterrows()],
            rotation=45, ha="right", fontsize=7,
        )
        label = TIER_LABELS.get(tier_name, tier_name)
        gap = metrics["DP_Gap"].mean()
        ax.set_title(f"{label}\nMean Gap = {gap:+.3f}", fontsize=12, fontweight="bold")
        ax.set_ylim(-0.05, 1.1)
        ax.legend(fontsize=8, loc="lower left")

    axes[0].set_ylabel("Accuracy", fontsize=12)
    fig.suptitle("The Scissors Pattern Across Complexity Tiers", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_dir / "triple_scissors.pdf", dpi=300)
    fig.savefig(output_dir / "triple_scissors.png", dpi=300)
    plt.close(fig)
    print("  → Saved triple_scissors.pdf/png")


def plot_tier_condition_bars(tier_metrics: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """The 'money figure': grouped bars — 3 tiers × 3 conditions."""
    tiers = list(tier_metrics.keys())
    n_tiers = len(tiers)
    x = np.arange(n_tiers)
    w = 0.25

    da_means, pa_means, pra_means = [], [], []
    da_sems, pa_sems, pra_sems = [], [], []

    for tier_name in tiers:
        m = tier_metrics[tier_name]
        da_means.append(m["DA"].mean())
        pa_means.append(m["PA"].mean())
        pra_means.append(m["PrA"].mean())
        da_sems.append(m["DA"].sem())
        pa_sems.append(m["PA"].sem())
        pra_sems.append(m["PrA"].sem())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - w, da_means, w, yerr=da_sems, capsize=4, label="Declarative (DA)",
           color=C_DEC, alpha=0.85, edgecolor="k")
    ax.bar(x, pa_means, w, yerr=pa_sems, capsize=4, label="Procedural (PA)",
           color=C_PRO, alpha=0.85, edgecolor="k")
    ax.bar(x + w, pra_means, w, yerr=pra_sems, capsize=4, label="Primed (PrA)",
           color=C_PRI, alpha=0.85, edgecolor="k")

    ax.set_xticks(x)
    ax.set_xticklabels([TIER_LABELS.get(t, t) for t in tiers], fontsize=11)
    ax.set_ylabel("Mean Accuracy (± SEM)", fontsize=12)
    ax.set_title("D-P Gap by Complexity Tier", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10)

    # Annotate gap values
    for i, tier in enumerate(tiers):
        gap = tier_metrics[tier]["DP_Gap"].mean()
        ax.annotate(f"Gap={gap:+.2f}",
                    xy=(i, max(da_means[i], pa_means[i]) + 0.08),
                    ha="center", fontsize=10, fontweight="bold", color="#b45309")

    fig.tight_layout()
    fig.savefig(output_dir / "tier_condition_bars.pdf", dpi=300)
    fig.savefig(output_dir / "tier_condition_bars.png", dpi=300)
    plt.close(fig)
    print("  → Saved tier_condition_bars.pdf/png")


def plot_gap_by_tier(tier_metrics: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Bar chart of mean D-P Gap by tier (simple and striking)."""
    tiers = list(tier_metrics.keys())
    gaps = [tier_metrics[t]["DP_Gap"].mean() for t in tiers]
    colors = [TIER_COLORS.get(t, "#888") for t in tiers]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        [TIER_LABELS.get(t, t) for t in tiers],
        gaps, color=colors, alpha=0.85, edgecolor="k",
    )
    for bar, g in zip(bars, gaps):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{g:.3f}", ha="center", fontsize=12, fontweight="bold")

    ax.set_ylabel("Mean D-P Gap (DA − PA)", fontsize=12)
    ax.set_title("The D-P Gap Widens with Problem Difficulty", fontsize=14, fontweight="bold")
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_dir / "gap_by_tier.pdf", dpi=300)
    fig.savefig(output_dir / "gap_by_tier.png", dpi=300)
    plt.close(fig)
    print("  → Saved gap_by_tier.pdf/png")


def plot_complexity_tier_interaction(tier_metrics: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Line plot: complexity (x) × D-P Gap (y), one line per tier."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for tier_name, metrics in tier_metrics.items():
        by_c = metrics.groupby("complexity")["DP_Gap"].mean().reset_index()
        label = TIER_LABELS.get(tier_name, tier_name).replace("\n", " ")
        color = TIER_COLORS.get(tier_name, "#888")
        ax.plot(by_c["complexity"], by_c["DP_Gap"], "o-", color=color,
                label=label, linewidth=2.5, markersize=8)

    ax.set_xlabel("Rule Complexity", fontsize=12)
    ax.set_ylabel("Mean D-P Gap", fontsize=12)
    ax.set_title("Complexity × Tier Interaction", fontsize=14, fontweight="bold")
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(output_dir / "complexity_tier_interaction.pdf", dpi=300)
    fig.savefig(output_dir / "complexity_tier_interaction.png", dpi=300)
    plt.close(fig)
    print("  → Saved complexity_tier_interaction.pdf/png")


def run_cross_tier_statistics(tier_metrics: dict[str, pd.DataFrame]) -> dict:
    """Compare D-P Gaps across tiers using ANOVA and pairwise t-tests."""
    results = {}

    tier_names = list(tier_metrics.keys())
    gaps = {t: tier_metrics[t]["DP_Gap"].values for t in tier_names}

    # One-way ANOVA on gap values
    if len(gaps) >= 2:
        f_stat, p_anova = stats.f_oneway(*gaps.values())
        results["cross_tier_ANOVA"] = {"F": f_stat, "p": p_anova}

    # Pairwise t-tests
    for i, t1 in enumerate(tier_names):
        for t2 in tier_names[i + 1:]:
            t_stat, p_val = stats.ttest_ind(gaps[t1], gaps[t2])
            results[f"{t1}_vs_{t2}_ttest"] = {"t": t_stat, "p": p_val}

    print("\n" + "=" * 60)
    print("  CROSS-TIER STATISTICAL TESTS")
    print("=" * 60)
    for key, val in results.items():
        if isinstance(val, dict):
            parts = "  ".join(f"{k}={v:.4f}" for k, v in val.items())
            print(f"  {key}: {parts}")
        else:
            print(f"  {key}: {val:.4f}")
    print("=" * 60)

    return results


def run_tiered_analysis(results_dir: Path) -> None:
    """Run the complete tiered analysis pipeline."""
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load all tier results
    tier_dfs = load_tier_results(results_dir)
    if not tier_dfs:
        print("No tier results found! Run the experiment first.")
        return

    # Compute per-tier metrics
    tier_metrics: dict[str, pd.DataFrame] = {}
    for tier_name, df in tier_dfs.items():
        print(f"\n{'='*80}")
        print(f"  {TIER_LABELS.get(tier_name, tier_name).replace(chr(10), ' ')} — {len(df)} data points")
        print(f"{'='*80}")
        metrics = compute_metrics(df)
        print_summary(metrics)
        tier_metrics[tier_name] = metrics

        # Save per-tier metrics
        tier_dir = results_dir / tier_name
        tier_dir.mkdir(exist_ok=True)
        metrics.to_csv(tier_dir / "metrics_summary.csv", index=False)

        # Run per-tier statistics
        run_statistics(df, metrics)

    # Cross-tier analysis
    if len(tier_metrics) > 1:
        run_cross_tier_statistics(tier_metrics)

        # Cross-tier figures
        print("\nGenerating cross-tier figures...")
        plot_triple_scissors(tier_metrics, results_dir)
        plot_tier_condition_bars(tier_metrics, results_dir)
        plot_gap_by_tier(tier_metrics, results_dir)
        plot_complexity_tier_interaction(tier_metrics, results_dir)

    # Also run per-tier figure generation
    from .analysis import (
        plot_scissors, plot_heatmap, plot_complexity_scatter,
        plot_priming_bars, plot_overall_summary,
    )
    for tier_name, metrics in tier_metrics.items():
        tier_dir = results_dir / tier_name
        print(f"\nGenerating {tier_name} figures...")
        plot_scissors(metrics, tier_dir)
        plot_heatmap(metrics, tier_dir)
        plot_complexity_scatter(metrics, tier_dir)
        plot_priming_bars(metrics, tier_dir)
        plot_overall_summary(metrics, tier_dir)

    print("\n✓ Tiered analysis complete!")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Cross-tier D-P Gap analysis")
    parser.add_argument("--results-dir", default="results", help="Results directory")
    args = parser.parse_args()
    run_tiered_analysis(Path(args.results_dir))
