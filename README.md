# Formalizing the Scissors Pattern: The Declarative-Procedural Paradox in Logical Inference

**Target venue:** ACL 2026 Student Research Workshop  
**Deadline:** March 18, 2026  
**Status:** Active development

---

## Abstract

Large Language Models can flawlessly *state* logical rules yet systematically fail to *apply* them. While recent work has observed this knowing-doing dissociation in cultural reasoning (KinshipQA, 2026) and game environments (TiG, 2025), no study has *formally quantified* the gap across the full spectrum of classical inference rules. We design a controlled 300-problem benchmark spanning 15 formal inference rules at four complexity levels (1--4), testing Mistral~7B (Ollama) under three conditions: **Declarative** (explain the rule), **Procedural** (apply it without a hint), and **Primed** (apply it after an explicit reminder); we also report Qwen~2.5~7B for comparison. We introduce the **Scissors Pattern**: a characteristic divergence where Declarative Accuracy remains high and flat while Procedural Accuracy declines with rule complexity, opening like scissors. For Mistral~7B priming yields minimal recovery (+0.02), indicating the deficit is largely a *binding* failure rather than retrieval. Our benchmark and metrics provide a reusable diagnostic lens for evaluating logical competence in LLMs.

> **Framing note:** We do *not* claim to have discovered the D-P Gap concept. We *formalize* it — quantifying its topology (the Scissors Pattern), isolating its mechanism (binding failure), and grounding it in formal logic rather than cultural or game domains.

---

## Motivation

### The Problem

Modern LLMs achieve impressive scores on logic benchmarks, yet:
- They **hallucinate** logically invalid conclusions on novel problems.
- They can **recite** a rule perfectly while misapplying it in the same conversation.
- **Scaling** model size does not reliably close this gap.

This mirrors the cognitive science distinction (Ryle, 1949; Anderson, 1983) between **declarative knowledge** (facts you can state) and **procedural knowledge** (skills you can execute).

### Why It Matters

1. **Safety:** If an LLM "knows" that Modus Tollens is valid but applies it incorrectly when reasoning about drug interactions or legal arguments, the consequences are real.
2. **Evaluation gap:** Current benchmarks conflate knowing-that with knowing-how. Our study disentangles them.
3. **Priming as a lever:** For our primary model (Mistral~7B), priming yields minimal recovery (+0.02), indicating a *binding* deficit; RAG or rule-stating may help other models and is a direction for future work.

---

## Methodology

### The 15 Logical Rules Under Study

| ID  | Rule                        | Complexity |
|-----|-----------------------------|:----------:|
| R01 | Modus Ponens                | 1          |
| R02 | Modus Tollens               | 2          |
| R03 | Hypothetical Syllogism      | 2          |
| R04 | Disjunctive Syllogism       | 2          |
| R05 | Contrapositive              | 2          |
| R06 | De Morgan's Law I           | 3          |
| R07 | De Morgan's Law II          | 3          |
| R08 | Double Negation             | 1          |
| R09 | Transitivity                | 2          |
| R10 | Proof by Contradiction      | 4          |
| R11 | Universal Instantiation     | 2          |
| R12 | Biconditional Elimination   | 3          |
| R13 | Constructive Dilemma        | 4          |
| R14 | Absorption                  | 3          |
| R15 | Material Implication        | 4          |

### Problem Bank

- **300 problems** (20 per rule)
- Each problem has an unambiguous ground-truth answer
- Problems use diverse entity names and scenarios to prevent memorisation
- Problems require **only** the target rule (no multi-step chains)

### Three Experimental Conditions

| Condition    | Prompt                                          | What we measure       |
|--------------|------------------------------------------------|-----------------------|
| **A. Declarative** | "Explain the rule of Modus Ponens"        | Can the LLM *state* the rule? |
| **B. Procedural**  | "Solve: If P→Q, P is true. What follows?" | Can the LLM *apply* the rule (without being told which one)? |
| **C. Primed**      | "Recall: Modus Ponens is P→Q, P ⊢ Q. Now solve…" | Does a reminder recover performance? |

### Evaluation Protocol

- **Declarative:** LLM-as-judge scores definition accuracy and example validity (0, 0.5, or 1.0)
- **Procedural/Primed:** Keyword matching with LLM-as-judge fallback for borderline cases
- All raw responses and verdicts logged for reproducibility

### Reproducibility

To reproduce paper results: set `OLLAMA_BASE_URL` (e.g. in `.env`) and run `python -m src.experiment`; the default model is `mistral:7b`. See `EXECUTION_PLAN.md` for full steps. Exact scores may vary slightly across runs due to API non-determinism.

### Metrics

| Metric          | Formula          | Meaning                                       |
|-----------------|------------------|-----------------------------------------------|
| DA              | E[score\|Dec]    | Declarative Accuracy                          |
| PA              | E[score\|Pro]    | Procedural Accuracy                           |
| PrA             | E[score\|Pri]    | Primed Accuracy                               |
| **D-P Gap**     | DA − PA          | The paradox: knowing vs. doing                |
| **Priming Effect** | PrA − PA      | Does a reminder help?                         |

---

## Visual Concepts

### Figure 1 — The Scissors Graph

The signature visualisation. X-axis: 15 rules sorted by complexity. Y-axis: accuracy (0–1). Two lines:
- **Blue solid (DA):** High and relatively flat — the LLM can explain almost every rule.
- **Red dashed (PA):** Declining as complexity grows — the LLM struggles to apply harder rules.
- **Green dotted (PrA):** Between DA and PA; for Mistral~7B recovery is limited (+0.02).

The area between DA and PA is shaded amber, visually representing the D-P Gap. The lines diverge like opening scissors as complexity increases.

### Figure 2 — Accuracy Heatmap

A 15×3 heatmap (rules × conditions), coloured red-yellow-green. Reveals:
- Which specific rules have the largest gaps
- Where priming fails to recover performance
- Clusters of difficulty

### Figure 3 — Complexity Scatter

Scatter plot of rule complexity vs D-P Gap, with a regression line and Spearman's ρ. Tests our core hypothesis that the gap widens with complexity.

### Figure 4 — Priming Effect Bars

Grouped bar chart (PA vs PrA) for each rule. Shows which rules benefit most from priming.

### Figure 5 — Overall Summary

Three bars (DA, PA, PrA) with error bars (SEM). The headline result at a glance.

---

## Hypotheses

**H1:** The D-P Gap is positive (DA > PA) across most rules. LLMs can state rules better than they can apply them.

**H2:** The D-P Gap grows with rule complexity (positive Spearman correlation).

**H3:** For Mistral~7B priming yields minimal recovery (PrA − PA ≈ +0.02), indicating the deficit is largely *binding* rather than retrieval; other models (e.g. Qwen) may show different patterns.

---

## 6-Week Roadmap

| Week | Milestone                     | Deliverables                                       |
|------|-------------------------------|----------------------------------------------------|
| 1    | **Problem bank + Pipeline**   | 300 problems, LLM client, prompt templates         |
| 2    | **Experiment run**            | 900 data points (300 × 3 conditions), raw CSV      |
| 3    | **Analysis + Figures**        | Scissors graph, heatmap, all statistical tests      |
| 4    | **Draft paper**               | ACL 2026 LaTeX (4 pages + references)              |
| 5    | **Peer review + Revision**    | Advisor feedback, ablation studies                  |
| 6    | **Final submission**          | Camera-ready by March 18                           |

---

## Expected Contributions

1. **The D-P Gap metric** — a new, reusable diagnostic measure for LLM reasoning.
2. **A 300-problem benchmark** spanning 15 logical rules at four complexity levels (1--4).
3. **Empirical evidence** that LLMs have a structural knowing–doing dissociation.
4. **Priming analysis** — quantifying when and how much a rule reminder helps.
5. **Complexity–gap correlation** — linking formal rule difficulty to LLM failure modes.

---

## Technical Stack

- **Subject model:** Gemini 2.0 Flash (via `google-generativeai` SDK)
- **Language:** Python 3.11+
- **Libraries:** Pydantic, Pandas, Matplotlib, Seaborn, SciPy, Tenacity
- **Structured output:** JSON via `response_mime_type="application/json"`
- **Evaluation:** Hybrid keyword + LLM-as-judge scoring

---

## Related Work

- **Ryle (1949)** — *The Concept of Mind*: knowing-that vs knowing-how.
- **Anderson (1983)** — ACT-R theory of declarative vs procedural memory.
- **Wei et al. (2022)** — Chain-of-Thought prompting.
- **Saparov & He (2023)** — PrOntoQA: probing logical reasoning in LMs.
- **Xu et al. (2024)** — LogicBench: systematic evaluation of logic reasoning.
- **Berglund et al. (2024)** — The Reversal Curse: LLMs trained on "A is B" fail to infer "B is A."
- **Allen-Zhu & Li (2024)** — Physics of Language Models: knowledge capacity analysis.

---

## Quick Start

```bash
# Clone and setup
cd dp-gap
pip install -r requirements.txt
cp .env.example .env  # add your GEMINI_API_KEY

# Generate problem bank
python -m src.problems --output data/problems.json

# Smoke test (2 rules, 3 problems each)
python -m src.experiment --rules R01 R02 --max-problems 3

# Full experiment
python -m src.experiment

# Analysis
python -m src.analysis --input results/experiment_results.csv
```

---

## License

MIT
