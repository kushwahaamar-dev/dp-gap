"""Pydantic data models for the D-P Gap experiment."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Condition(str, Enum):
    DECLARATIVE = "declarative"
    PROCEDURAL = "procedural"
    PRIMED = "primed"


# ---------------------------------------------------------------------------
# Rule & Problem schemas
# ---------------------------------------------------------------------------

class LogicalRule(BaseModel):
    """One of the 15 logical inference rules under study."""
    id: str = Field(..., description="R01..R15")
    name: str
    formal: str = Field(..., description="Symbolic form, e.g. P→Q, P ⊢ Q")
    description: str = Field(..., description="Plain-English explanation")
    example: str = Field(..., description="Worked textbook example")
    complexity: int = Field(..., ge=1, le=5)


class Problem(BaseModel):
    """A single test problem targeting one rule."""
    id: str = Field(..., description="e.g. R01_P01")
    rule_id: str
    text: str = Field(..., min_length=10)
    ground_truth: str
    distractors: list[str] = Field(default_factory=list)


class ProblemBank(BaseModel):
    """The full collection of problems."""
    problems: list[Problem]


# ---------------------------------------------------------------------------
# LLM response schemas (structured JSON from Gemini)
# ---------------------------------------------------------------------------

class DeclarativeResponse(BaseModel):
    """LLM output for the DECLARATIVE condition."""
    definition: str = Field(..., description="The rule's formal definition")
    example: str = Field(..., description="A concrete example of the rule")


class ProceduralResponse(BaseModel):
    """LLM output for PROCEDURAL / PRIMED conditions."""
    conclusion: str = Field(..., description="The logical conclusion")
    reasoning: str = Field(default="", description="Step-by-step reasoning")


class EvaluatorVerdict(BaseModel):
    """LLM evaluator output for scoring."""
    score: float = Field(..., ge=0.0, le=1.0)
    feedback: str = Field(default="")


# ---------------------------------------------------------------------------
# Result row
# ---------------------------------------------------------------------------

class ExperimentResult(BaseModel):
    """One row in the results CSV."""
    problem_id: str
    rule_id: str
    rule_name: str
    complexity: int
    condition: Condition
    raw_response: str = ""
    score: float = 0.0
    tokens_used: int = 0
    latency_seconds: float = 0.0
