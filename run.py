#!/usr/bin/env python3
"""
D-P Gap Experiment — Main Entry Point

Usage:
    # Full pipeline (generate → run → analyse)
    python run.py

    # Smoke test
    python run.py --smoke

    # Custom options
    python run.py --rules R01 R05 R10 --max-problems 5
"""

import argparse
import logging
from pathlib import Path

from src.analysis import run_analysis
from src.experiment import run_experiment
from src.problems import save_problem_bank

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("dp-gap")


def main():
    parser = argparse.ArgumentParser(description="D-P Gap full pipeline")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test (2 rules × 3 problems)")
    parser.add_argument("--rules", nargs="+", default=None, help="Rule IDs to test")
    parser.add_argument("--max-problems", type=int, default=None, help="Max problems per rule")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model")
    parser.add_argument("--output-dir", default="results", help="Output directory")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis step")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if args.smoke:
        args.rules = args.rules or ["R01", "R02"]
        args.max_problems = args.max_problems or 3

    # Step 1: Generate problem bank
    logger.info("Step 1/3: Generating problem bank...")
    save_problem_bank()

    # Step 2: Run experiment
    logger.info("Step 2/3: Running experiment...")
    df = run_experiment(
        rules=args.rules,
        max_problems_per_rule=args.max_problems,
        model=args.model,
        output_dir=output_dir,
    )

    # Step 3: Analysis
    if not args.skip_analysis:
        logger.info("Step 3/3: Running analysis...")
        results_path = output_dir / "experiment_results.csv"
        run_analysis(results_path, output_dir)
    else:
        logger.info("Step 3/3: Skipped analysis (--skip-analysis)")

    logger.info("Pipeline complete!")


if __name__ == "__main__":
    main()
