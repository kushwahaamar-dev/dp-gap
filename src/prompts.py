"""Prompt templates for the three experimental conditions."""

# ── CONDITION A: DECLARATIVE ─────────────────────────────────────────────────

DEC_SYSTEM = """\
You are an expert in formal logic. Answer accurately and concisely.
Return ONLY valid JSON."""

DEC_USER = """\
Explain the logical principle of "{rule_name}".

Provide:
1. The formal definition of this rule.
2. One concrete, original example demonstrating the rule.

Return JSON: {{"definition": "<formal definition>", "example": "<concrete example>"}}"""

# ── CONDITION B: PROCEDURAL ──────────────────────────────────────────────────

PRO_SYSTEM = """\
You are an expert in formal logic. Solve the problem below.
Show your reasoning step by step, then give a clear conclusion.
Return ONLY valid JSON."""

PRO_USER = """\
Solve this logic problem:

{problem_text}

Return JSON: {{"conclusion": "<your conclusion>", "reasoning": "<step-by-step reasoning>"}}"""

# ── CONDITION C: PRIMED ──────────────────────────────────────────────────────

PRI_SYSTEM = """\
You are an expert in formal logic. You are given a logical rule and a problem.
Apply the provided rule to solve the problem.
Return ONLY valid JSON."""

PRI_USER = """\
Recall the following logical rule:

**{rule_name}**: {rule_description}
Formal statement: {rule_formal}

Now solve this problem using the rule above:

{problem_text}

Return JSON: {{"conclusion": "<your conclusion>", "reasoning": "<step-by-step reasoning>"}}"""

# ── EVALUATOR ────────────────────────────────────────────────────────────────

EVAL_DEC_SYSTEM = """\
You are a strict logic grading assistant. Score the student's explanation of a logical rule.
Be precise: the student must get the SPECIFIC rule correct, not a related but different rule.
For example, De Morgan's Law I (negation of conjunction) is DIFFERENT from De Morgan's Law II (negation of disjunction).
Return ONLY valid JSON."""

EVAL_DEC_USER = """\
Rule name: {rule_name}
Correct formal statement: {rule_formal}
Correct description: {rule_description}

Student's answer:
{response}

Score using this rubric:
- 1.0: Definition is PRECISELY correct for THIS specific rule (not a related rule) AND example is valid.
- 0.5: Definition captures the right idea but has minor imprecision, OR example is valid but definition is for a closely related rule.
- 0.0: Fundamental misstatement, wrong rule, or confused with a different rule.

Return JSON: {{"score": <0.0 or 0.5 or 1.0>, "feedback": "<brief explanation>"}}"""

EVAL_PRO_SYSTEM = """\
You are a strict logic grading assistant. Evaluate whether the student's \
conclusion AND reasoning are logically correct.

IMPORTANT: The student must arrive at the correct conclusion through correct \
reasoning. A correct answer obtained through flawed or irrelevant reasoning \
should receive partial credit at best.

Return ONLY valid JSON."""

EVAL_PRO_USER = """\
Problem: {problem_text}
Correct answer: {ground_truth}
Student's conclusion: {conclusion}

Evaluate the student's response using this rubric:
- 1.0: Conclusion is logically equivalent to the correct answer AND any reasoning shown is valid.
- 0.5: Conclusion is approximately correct but imprecise, OR conclusion is correct but reasoning is flawed/missing key steps.
- 0.0: Conclusion is wrong, or conclusion contradicts the correct answer, or reasoning demonstrates a fundamental logical error even if the final answer happens to match.

Return JSON: {{"score": <0.0 or 0.5 or 1.0>, "feedback": "<brief explanation>"}}"""
