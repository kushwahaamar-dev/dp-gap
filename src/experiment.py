"""
Main experiment runner for the D-P Gap study.

For each of the 300 problems, runs three conditions:
  A. Declarative — ask the LLM to explain the rule
  B. Procedural — ask the LLM to apply the rule (without naming it)
  C. Primed     — remind the LLM of the rule, then ask it to apply

Results are saved incrementally to CSV and scored by the evaluator.

Usage:
    python -m src.experiment                       # full run
    python -m src.experiment --rules R01 R02       # subset
    python -m src.experiment --max-problems 5      # quick smoke test
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .evaluator import score_declarative, score_procedural
from .llm_client import LLMClient
from .models import (
    Condition,
    DeclarativeResponse,
    ExperimentResult,
    ProceduralResponse,
)
from .problems import load_problem_bank
from .prompts import (
    DEC_SYSTEM,
    DEC_USER,
    PRI_SYSTEM,
    PRI_USER,
    PRO_SYSTEM,
    PRO_USER,
)
from .rules import RULES_BY_ID

logger = logging.getLogger(__name__)


def _default_model() -> str:
    """Default model: mistral:7b when using Ollama, else gpt-4o-mini (paper reproducibility)."""
    return "mistral:7b" if os.getenv("OLLAMA_BASE_URL", "").strip() else "gpt-4o-mini"


def run_declarative(
    rule_id: str,
    problem_id: str,
    llm: LLMClient,
    eval_llm: LLMClient,
) -> ExperimentResult:
    """Condition A: ask the model to explain the rule."""
    rule = RULES_BY_ID[rule_id]
    prompt = DEC_USER.format(rule_name=rule.name)

    start = time.time()
    try:
        resp = llm.call(DEC_SYSTEM, prompt, DeclarativeResponse)
        raw = json.dumps({"definition": resp.definition, "example": resp.example})
    except Exception as e:
        raw = str(e)
    elapsed = time.time() - start

    verdict = score_declarative(rule_id, raw, eval_llm)

    return ExperimentResult(
        problem_id=problem_id,
        rule_id=rule_id,
        rule_name=rule.name,
        complexity=rule.complexity,
        condition=Condition.DECLARATIVE,
        raw_response=raw,
        score=verdict.score,
        tokens_used=llm.total_tokens_used,
        latency_seconds=elapsed,
    )


def run_procedural(
    rule_id: str,
    problem_id: str,
    problem_text: str,
    ground_truth: str,
    llm: LLMClient,
    eval_llm: LLMClient,
) -> ExperimentResult:
    """Condition B: solve the problem without being told the rule."""
    rule = RULES_BY_ID[rule_id]
    prompt = PRO_USER.format(problem_text=problem_text)

    start = time.time()
    try:
        resp = llm.call(PRO_SYSTEM, prompt, ProceduralResponse)
        raw = json.dumps({"conclusion": resp.conclusion, "reasoning": resp.reasoning})
    except Exception as e:
        raw = str(e)
    elapsed = time.time() - start

    verdict = score_procedural(problem_text, ground_truth, raw, eval_llm)

    return ExperimentResult(
        problem_id=problem_id,
        rule_id=rule_id,
        rule_name=rule.name,
        complexity=rule.complexity,
        condition=Condition.PROCEDURAL,
        raw_response=raw,
        score=verdict.score,
        tokens_used=llm.total_tokens_used,
        latency_seconds=elapsed,
    )


def run_primed(
    rule_id: str,
    problem_id: str,
    problem_text: str,
    ground_truth: str,
    llm: LLMClient,
    eval_llm: LLMClient,
) -> ExperimentResult:
    """Condition C: remind the model of the rule, then solve."""
    rule = RULES_BY_ID[rule_id]
    prompt = PRI_USER.format(
        rule_name=rule.name,
        rule_description=rule.description,
        rule_formal=rule.formal,
        problem_text=problem_text,
    )

    start = time.time()
    try:
        resp = llm.call(PRI_SYSTEM, prompt, ProceduralResponse)
        raw = json.dumps({"conclusion": resp.conclusion, "reasoning": resp.reasoning})
    except Exception as e:
        raw = str(e)
    elapsed = time.time() - start

    verdict = score_procedural(problem_text, ground_truth, raw, eval_llm)

    return ExperimentResult(
        problem_id=problem_id,
        rule_id=rule_id,
        rule_name=rule.name,
        complexity=rule.complexity,
        condition=Condition.PRIMED,
        raw_response=raw,
        score=verdict.score,
        tokens_used=llm.total_tokens_used,
        latency_seconds=elapsed,
    )


def _load_completed(output_path: Path) -> set[str]:
    """Load already-completed (problem_id, condition) pairs from an existing CSV."""
    if not output_path.exists():
        return set()
    try:
        df = pd.read_csv(output_path)
        return {f"{row['problem_id']}_{row['condition']}" for _, row in df.iterrows()}
    except Exception:
        return set()


def _append_rows(output_path: Path, rows: list[dict]) -> None:
    """Append rows to CSV, creating header if file doesn't exist."""
    df = pd.DataFrame(rows)
    write_header = not output_path.exists() or output_path.stat().st_size == 0
    df.to_csv(output_path, mode="a", header=write_header, index=False)


def run_experiment(
    rules: list[str] | None = None,
    max_problems_per_rule: int | None = None,
    model: str | None = None,
    output_dir: Path = Path("results"),
    problem_bank_path: Path | None = None,
) -> pd.DataFrame:
    """Run the full 3-condition experiment with incremental saves."""
    if model is None:
        model = _default_model()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "experiment_results.csv"
    bank = load_problem_bank(problem_bank_path)

    # Check for existing progress (resume support)
    completed = _load_completed(output_path)
    if completed:
        logger.info("Resuming: found %d already-completed data points", len(completed))

    # Setup LLM clients (separate for generation and evaluation)
    llm = LLMClient(model=model, temperature=0.0)
    eval_llm = LLMClient(model=model, temperature=0.0)

    # Group problems by rule
    problems_by_rule: dict[str, list] = {}
    for prob in bank.problems:
        if rules and prob.rule_id not in rules:
            continue
        problems_by_rule.setdefault(prob.rule_id, []).append(prob)

    total = sum(
        min(len(ps), max_problems_per_rule or 999)
        for ps in problems_by_rule.values()
    )
    pbar = tqdm(total=total * 3, desc="Running experiment")

    # Skip already completed in progress bar
    skip_count = 0
    buffer: list[dict] = []
    flush_every = 30  # save every 30 rows

    for rule_id in sorted(problems_by_rule.keys()):
        probs = problems_by_rule[rule_id]
        if max_problems_per_rule:
            probs = probs[:max_problems_per_rule]

        for prob in probs:
            for condition_fn, condition_name in [
                (run_declarative, "declarative"),
                (run_procedural, "procedural"),
                (run_primed, "primed"),
            ]:
                key = f"{prob.id}_{condition_name}"
                if key in completed:
                    skip_count += 1
                    pbar.update(1)
                    continue

                llm.reset_tracking()

                try:
                    if condition_name == "declarative":
                        result = run_declarative(prob.rule_id, prob.id, llm, eval_llm)
                    elif condition_name == "procedural":
                        result = run_procedural(
                            prob.rule_id, prob.id, prob.text, prob.ground_truth, llm, eval_llm
                        )
                    else:
                        result = run_primed(
                            prob.rule_id, prob.id, prob.text, prob.ground_truth, llm, eval_llm
                        )
                    buffer.append(result.model_dump())
                except Exception as e:
                    logger.error("Failed %s %s: %s", prob.id, condition_name, e)
                    # Record the failure
                    rule = RULES_BY_ID[prob.rule_id]
                    buffer.append(ExperimentResult(
                        problem_id=prob.id,
                        rule_id=prob.rule_id,
                        rule_name=rule.name,
                        complexity=rule.complexity,
                        condition=Condition(condition_name),
                        raw_response=f"ERROR: {e}",
                        score=0.0,
                        tokens_used=0,
                        latency_seconds=0.0,
                    ).model_dump())

                pbar.update(1)

                # Flush buffer periodically
                if len(buffer) >= flush_every:
                    _append_rows(output_path, buffer)
                    buffer.clear()

    # Flush remaining
    if buffer:
        _append_rows(output_path, buffer)
        buffer.clear()

    pbar.close()

    if skip_count:
        logger.info("Skipped %d already-completed data points", skip_count)

    # Read back full results
    df = pd.read_csv(output_path)
    logger.info("Saved %d results to %s", len(df), output_path)
    print(f"\n✓ Experiment complete: {len(df)} data points saved to {output_path}")
    print(f"  Generation API usage: {llm.usage_summary}")
    print(f"  Evaluator  API usage: {eval_llm.usage_summary}")
    return df


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Run D-P Gap experiment")
    parser.add_argument("--rules", nargs="+", default=None, help="Rule IDs to test (e.g. R01 R05)")
    parser.add_argument("--max-problems", type=int, default=None, help="Max problems per rule")
    parser.add_argument(
        "--model",
        default=None,
        help="Model name (default: mistral:7b if OLLAMA_BASE_URL set, else gpt-4o-mini)",
    )
    parser.add_argument("--output-dir", default="results", help="Output directory")
    args = parser.parse_args()
    model = args.model if args.model is not None else _default_model()

    run_experiment(
        rules=args.rules,
        max_problems_per_rule=args.max_problems,
        model=model,
        output_dir=Path(args.output_dir),
    )
