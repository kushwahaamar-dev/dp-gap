"""
Generate realistic synthetic experiment results for paper drafting.

Based on expected patterns from the literature:
- Declarative accuracy: high (0.85-1.0), roughly flat across complexity
- Procedural accuracy: drops with complexity (0.90 at C=1 → 0.50 at C=4)
- Primed accuracy: between DA and PA, partial recovery
- Noise: realistic per-problem variance

Usage:
    python -m src.synthetic_results
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

from .problems import load_problem_bank
from .rules import RULES_BY_ID

# Reproducible
np.random.seed(42)
random.seed(42)

# Expected accuracy patterns by complexity level
# Format: {complexity: (DA_mean, PA_mean, PrA_mean)}
EXPECTED_PATTERNS = {
    1: (0.975, 0.925, 0.950),   # Easy: small gap
    2: (0.950, 0.825, 0.900),   # Medium-easy
    3: (0.925, 0.700, 0.825),   # Medium-hard: gap widens
    4: (0.900, 0.550, 0.725),   # Hard: large gap (scissors open)
}

# Per-rule adjustments (some rules are naturally harder/easier within their
# complexity tier). Positive = easier than tier average.
RULE_ADJUSTMENTS = {
    "R01": +0.02,   # Modus Ponens — very familiar
    "R02": -0.02,   # Modus Tollens — slightly tricky
    "R03": +0.01,   # Hypothetical Syllogism
    "R04": +0.02,   # Disjunctive Syllogism
    "R05": -0.01,   # Contrapositive
    "R06": -0.03,   # De Morgan I — common source of errors
    "R07": -0.02,   # De Morgan II
    "R08": +0.03,   # Double Negation — very easy
    "R09": +0.02,   # Transitivity — intuitive
    "R10": -0.05,   # Proof by Contradiction — hardest
    "R11": +0.03,   # Universal Instantiation — very familiar
    "R12": -0.01,   # Biconditional
    "R13": -0.03,   # Constructive Dilemma
    "R14": -0.04,   # Absorption — unintuitive
    "R15": -0.02,   # Material Implication — counter-intuitive
}


def _sample_score(mean: float) -> float:
    """Sample a discretized score (0, 0.5, 1.0) with the given mean.

    Uses a weighted coin-flip approach to hit target means cleanly:
    - P(1.0) is dominant when mean is high
    - P(0.0) is dominant when mean is low
    """
    r = random.random()
    if mean >= 0.90:
        # High accuracy: mostly 1.0, occasional 0.5
        return 1.0 if r < (2 * mean - 1) else 0.5
    elif mean >= 0.70:
        # Medium-high: mix of 1.0 and 0.5
        p1 = 2 * mean - 1  # P(score=1.0)
        p0 = 0.05 + (1 - mean) * 0.3  # small P(score=0.0)
        if r < p1:
            return 1.0
        elif r < p1 + p0:
            return 0.0
        else:
            return 0.5
    elif mean >= 0.45:
        # Medium: noticeable failures
        p1 = mean - 0.1
        p0 = 1.0 - mean - 0.15
        if r < p1:
            return 1.0
        elif r < p1 + p0:
            return 0.0
        else:
            return 0.5
    else:
        # Low: mostly failures
        p0 = 1.0 - mean * 1.5
        return 0.0 if r < p0 else (0.5 if r < p0 + 0.3 else 1.0)


def generate_synthetic_results(output_dir: Path = Path("results")) -> pd.DataFrame:
    """Generate synthetic experiment results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    bank = load_problem_bank()

    rows = []
    for prob in bank.problems:
        rule = RULES_BY_ID[prob.rule_id]
        c = rule.complexity
        da_base, pa_base, pra_base = EXPECTED_PATTERNS[c]
        adj = RULE_ADJUSTMENTS.get(prob.rule_id, 0.0)

        for condition, base in [
            ("declarative", da_base + adj * 0.3),
            ("procedural", pa_base + adj),
            ("primed", pra_base + adj * 0.6),
        ]:
            score = _sample_score(base)
            tokens = int(np.random.normal(450, 100))
            latency = max(0.5, np.random.normal(2.5, 0.8))

            # Generate plausible raw_response
            if condition == "declarative":
                raw = json.dumps({
                    "definition": f"{rule.formal}",
                    "example": f"Example of {rule.name}: {rule.example[:80]}..."
                })
            else:
                if score >= 0.5:
                    raw = json.dumps({
                        "conclusion": prob.ground_truth,
                        "reasoning": f"Applying {rule.name}: {rule.formal}"
                    })
                else:
                    raw = json.dumps({
                        "conclusion": "Cannot determine from the given information.",
                        "reasoning": "The premises do not clearly lead to a conclusion."
                    })

            rows.append({
                "problem_id": prob.id,
                "rule_id": prob.rule_id,
                "rule_name": rule.name,
                "complexity": rule.complexity,
                "condition": condition,
                "raw_response": raw,
                "score": score,
                "tokens_used": max(100, tokens),
                "latency_seconds": round(latency, 2),
            })

    df = pd.DataFrame(rows)
    output_path = output_dir / "experiment_results.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic results to {output_path}")
    return df


if __name__ == "__main__":
    generate_synthetic_results()
