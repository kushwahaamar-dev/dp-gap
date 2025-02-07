#!/usr/bin/env python3
"""
D-P Gap Experiment — Tiered Pipeline

Runs the 3-tier × 3-condition experiment:
  Tier I:   Natural language (original problems)
  Tier II:  Abstract / Nonsense ("Wug test")
  Tier III: Noisy / Adversarial (distractors + belief bias)

Each tier: 300 problems × 3 conditions = 900 data points.
Total: 2700 data points.

Usage:
    python run_tiered.py                    # full pipeline
    python run_tiered.py --tiers 2 3        # only Tier II & III
    python run_tiered.py --smoke            # smoke test
"""

import argparse
import logging
from pathlib import Path

from src.analysis_tiered import run_tiered_analysis
from src.experiment import run_experiment
from src.problems_tiered import save_tiered_banks, load_tiered_bank

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("dp-gap-tiered")


def main():
    parser = argparse.ArgumentParser(description="D-P Gap tiered pipeline")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test (2 rules × 3 problems)")
    parser.add_argument("--tiers", nargs="+", type=int, default=[1, 2, 3], help="Which tiers to run")
    parser.add_argument("--rules", nargs="+", default=None, help="Rule IDs to test")
    parser.add_argument("--max-problems", type=int, default=None, help="Max problems per rule")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model")
    parser.add_argument("--output-dir", default="results", help="Output directory")
    parser.add_argument("--skip-analysis", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if args.smoke:
        args.rules = args.rules or ["R01", "R02"]
        args.max_problems = args.max_problems or 3

    # Step 1: Generate all tiered problem banks
    logger.info("Step 1: Generating tiered problem banks...")
    save_tiered_banks()

    # Step 2: Run each tier
    tier_names = {1: "tier1", 2: "tier2", 3: "tier3"}

    for tier_num in args.tiers:
        tier_name = tier_names[tier_num]
        tier_output = output_dir / tier_name
        tier_output.mkdir(parents=True, exist_ok=True)

        logger.info("Step 2.%d: Running Tier %d experiment...", tier_num, tier_num)

        # Load the tier's problem bank
        bank = load_tiered_bank(tier_name)
        bank_path = Path("data") / f"problems_{tier_name}.json"

        run_experiment(
            rules=args.rules,
            max_problems_per_rule=args.max_problems,
            model=args.model,
            output_dir=tier_output,
            problem_bank_path=bank_path,
        )

    # Step 3: Analysis
    if not args.skip_analysis:
        logger.info("Step 3: Running tiered analysis...")
        run_tiered_analysis(output_dir)
    else:
        logger.info("Step 3: Skipped analysis (--skip-analysis)")

    logger.info("Pipeline complete!")


if __name__ == "__main__":
    main()
