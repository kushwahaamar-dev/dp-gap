"""
Scoring engine for D-P Gap experiment responses.

Two modes:
  1. LLM-based evaluation (uses a separate OpenAI call to grade)
  2. Keyword-based fast matching (for CI / offline scoring)

Usage:
    python -m src.evaluator --input results/raw_responses.csv --output results/scored_results.csv
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .llm_client import LLMClient
from .models import Condition, EvaluatorVerdict
from .prompts import EVAL_DEC_SYSTEM, EVAL_DEC_USER, EVAL_PRO_SYSTEM, EVAL_PRO_USER
from .rules import RULES_BY_ID

logger = logging.getLogger(__name__)


def _normalise(s: str) -> str:
    """Lowercase, strip punctuation and whitespace for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def _quick_match(response: str, ground_truth: str) -> float | None:
    """Fast keyword match — returns 1.0 / 0.0 or None if unsure.

    Made stricter: only auto-score 1.0 for very high overlap,
    and fall back to LLM-as-judge for anything ambiguous.
    For complex answers (>8 words), always use LLM-as-judge.
    """
    r, g = _normalise(response), _normalise(ground_truth)
    if not r or not g:
        return None

    gt_words = set(g.split())

    # Complex answers always go to LLM judge
    if len(gt_words) > 8:
        return None

    if g in r:
        return 1.0

    resp_words = set(r.split())
    overlap = len(gt_words & resp_words) / max(len(gt_words), 1)

    if overlap > 0.90:
        return 1.0
    if overlap < 0.20:
        return 0.0
    return None  # uncertain → fall back to LLM


def score_declarative(
    rule_id: str,
    raw_response: str,
    llm: LLMClient,
) -> EvaluatorVerdict:
    """Score a DECLARATIVE condition response."""
    rule = RULES_BY_ID[rule_id]
    prompt = EVAL_DEC_USER.format(
        rule_name=rule.name,
        rule_formal=rule.formal,
        rule_description=rule.description,
        response=raw_response,
    )
    try:
        return llm.call(EVAL_DEC_SYSTEM, prompt, EvaluatorVerdict)
    except Exception as e:
        logger.warning("Evaluator failed for %s: %s", rule_id, e)
        return EvaluatorVerdict(score=0.0, feedback=f"Evaluator error: {e}")


def score_procedural(
    problem_text: str,
    ground_truth: str,
    raw_response: str,
    llm: LLMClient,
) -> EvaluatorVerdict:
    """Score a PROCEDURAL or PRIMED condition response."""
    # Try to extract the conclusion from JSON
    conclusion = raw_response
    try:
        parsed = json.loads(raw_response)
        conclusion = parsed.get("conclusion", raw_response)
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fast path: keyword match
    quick = _quick_match(conclusion, ground_truth)
    if quick is not None:
        return EvaluatorVerdict(
            score=quick,
            feedback="Auto-scored via keyword match.",
        )

    # Slow path: LLM evaluation
    prompt = EVAL_PRO_USER.format(
        problem_text=problem_text,
        ground_truth=ground_truth,
        conclusion=conclusion,
    )
    try:
        return llm.call(EVAL_PRO_SYSTEM, prompt, EvaluatorVerdict)
    except Exception as e:
        logger.warning("Evaluator failed: %s", e)
        return EvaluatorVerdict(score=0.0, feedback=f"Evaluator error: {e}")


def score_results_csv(
    input_path: Path,
    output_path: Path,
    model: str = "gpt-4o-mini",
) -> pd.DataFrame:
    """Score all rows in a raw_responses CSV and save scored results."""
    df = pd.read_csv(input_path)
    llm = LLMClient(model=model)

    from .problems import load_problem_bank
    from .rules import RULES_BY_ID

    bank = load_problem_bank()
    problems_by_id = {p.id: p for p in bank.problems}

    scores: list[float] = []
    feedbacks: list[str] = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Scoring"):
        condition = row["condition"]
        raw = str(row.get("raw_response", ""))
        rule_id = row["rule_id"]
        pid = row["problem_id"]

        if condition == Condition.DECLARATIVE.value:
            verdict = score_declarative(rule_id, raw, llm)
        else:
            prob = problems_by_id.get(pid)
            gt = prob.ground_truth if prob else ""
            txt = prob.text if prob else ""
            verdict = score_procedural(txt, gt, raw, llm)

        scores.append(verdict.score)
        feedbacks.append(verdict.feedback)

    df["score"] = scores
    df["feedback"] = feedbacks
    df.to_csv(output_path, index=False)
    logger.info("Saved scored results to %s", output_path)
    return df


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Score D-P Gap responses")
    parser.add_argument("--input", required=True, help="Path to raw_responses.csv")
    parser.add_argument("--output", required=True, help="Path for scored_results.csv")
    parser.add_argument(
        "--model",
        default=None,
        help="Model for judge (default: mistral:7b if OLLAMA_BASE_URL set, else gpt-4o-mini)",
    )
    args = parser.parse_args()
    model = (
        args.model
        if args.model is not None
        else ("mistral:7b" if os.getenv("OLLAMA_BASE_URL", "").strip() else "gpt-4o-mini")
    )
    score_results_csv(Path(args.input), Path(args.output), model=model)
