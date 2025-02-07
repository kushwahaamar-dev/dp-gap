# D-P Gap — Engineering Execution Plan

> Step-by-step technical guide for building and running the experiment pipeline.

---

## 1. Environment Setup

```bash
# Create project directory (already done)
cd dp-gap

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Optional: configure Ollama base URL (default: http://localhost:11434/v1)
cp .env.example .env
# Edit .env if needed: OLLAMA_BASE_URL=http://localhost:11434/v1
```

### Running models (Ollama, no API key for local runs)
- **Ollama:** Install [Ollama](https://ollama.com/) and run `ollama pull mistral:7b` (and optionally `ollama pull qwen2.5:7b`).
- Default base URL: `http://localhost:11434/v1`. No API key required for local runs.
- Supported model names: `mistral:7b`, `qwen2.5:7b` (or as configured in your Ollama installation).

---

## 2. Project Structure

```
dp-gap/
├── README.md                  # Academic proposal (Deliverable A)
├── EXECUTION_PLAN.md          # This file (Deliverable B)
├── requirements.txt           # Python dependencies
├── .env.example               # API key template
├── .gitignore
├── data/
│   └── problems.json          # Generated problem bank (300 problems)
├── results/
│   ├── experiment_results.csv # Raw results (900 rows)
│   ├── metrics_summary.csv    # Per-rule aggregated metrics
│   ├── scissors_graph.pdf     # Figure 1
│   ├── heatmap.pdf            # Figure 2
│   ├── complexity_scatter.pdf # Figure 3
│   ├── priming_bars.pdf       # Figure 4
│   └── overall_summary.pdf    # Figure 5
├── paper/                     # LaTeX paper (Week 4)
└── src/
    ├── __init__.py
    ├── models.py              # Pydantic data models
    ├── rules.py               # 15 logical rules with metadata
    ├── problems.py            # 300-problem bank generator
    ├── llm_client.py          # LLM client (Ollama / OpenAI-compatible API)
    ├── prompts.py             # Prompt templates (3 conditions + evaluator)
    ├── evaluator.py           # Scoring engine (keyword + LLM-as-judge)
    ├── experiment.py          # Main experiment runner
    └── analysis.py            # Statistical analysis + figure generation
```

---

## 3. Data Layer

### 3.1 Problem Bank (`src/problems.py`)

The problem bank contains **300 problems** (20 per rule × 15 rules):

```bash
python -m src.problems --output data/problems.json
```

**Design principles:**
- Each problem targets exactly **one** logical rule
- Ground truth is **unambiguous**
- Diverse entity names (Alice, Bob, Kai, Mia, etc.) to prevent memorisation
- Complexity ranges from 1 (Modus Ponens) to 4 (Proof by Contradiction)

**Schema:**
```json
{
  "problems": [
    {
      "id": "R01_P01",
      "rule_id": "R01",
      "text": "If it is raining, then the streets are wet. It is raining. What can you conclude?",
      "ground_truth": "The streets are wet.",
      "distractors": []
    }
  ]
}
```

### 3.2 Rules (`src/rules.py`)

15 `LogicalRule` objects with fields:
- `id`, `name`, `formal` (symbolic form), `description` (plain English)
- `example` (worked textbook example)
- `complexity` (1–4 scale)

---

## 4. LLM Integration

### 4.1 Client (`src/llm_client.py`)

```python
from src.llm_client import LLMClient
from src.models import ProceduralResponse

# Use Ollama (default base URL http://localhost:11434/v1)
llm = LLMClient(model="mistral:7b", temperature=0.0)
result = llm.call(
    system_prompt="You are a logic expert.",
    user_prompt="Solve: If P→Q and P, what follows?",
    response_model=ProceduralResponse,
)
print(result.conclusion)  # "Q"
```

**Key features:**
- Ollama / OpenAI-compatible API; set `OLLAMA_BASE_URL` in `.env` if needed
- Pydantic validation with automatic retry (3 attempts)
- Token tracking when available from the API
- Separate `call()` (structured) and `call_raw()` (unstructured) methods

### 4.2 Prompts (`src/prompts.py`)

Three condition templates:

| Template      | Variables                                    | Output Schema         |
|---------------|----------------------------------------------|-----------------------|
| `DEC_*`       | `{rule_name}`                                | `DeclarativeResponse` |
| `PRO_*`       | `{problem_text}`                             | `ProceduralResponse`  |
| `PRI_*`       | `{rule_name, rule_description, rule_formal, problem_text}` | `ProceduralResponse`  |

Plus evaluator templates (`EVAL_DEC_*`, `EVAL_PRO_*`) for LLM-as-judge scoring.

---

## 5. Experiment Runner (`src/experiment.py`)

### 5.1 Pipeline

For each of the 300 problems:
1. **Declarative (A):** Ask the LLM to explain the target rule → score with evaluator
2. **Procedural (B):** Ask the LLM to solve the problem (no rule hint) → score
3. **Primed (C):** Remind the LLM of the rule, then ask it to solve → score

Each condition produces one `ExperimentResult` row (900 total).

### 5.2 Commands

```bash
# Smoke test: 2 rules × 3 problems = 18 API calls
python -m src.experiment --rules R01 R02 --max-problems 3

# Full run: 15 rules × 20 problems × 3 conditions = 900 calls + ~900 eval calls
# With OLLAMA_BASE_URL set, default model is mistral:7b (paper results)
python -m src.experiment

# Custom model (Ollama)
python -m src.experiment --model mistral:7b --output-dir results
python -m src.experiment --model qwen2.5:7b --output-dir results_qwen
```

**Reproducing paper results:** Set `OLLAMA_BASE_URL` (e.g. in `.env`) and run `python -m src.experiment` with no `--model`; the default is `mistral:7b`. Exact scores may vary slightly across runs due to API non-determinism.

### 5.3 Output Schema (CSV)

| Column          | Type    | Description                     |
|-----------------|---------|-------------------------------|
| problem_id      | str     | e.g. R01_P01                   |
| rule_id         | str     | e.g. R01                       |
| rule_name       | str     | e.g. Modus Ponens              |
| complexity      | int     | 1–4                            |
| condition       | str     | declarative / procedural / primed |
| raw_response    | str     | Full JSON response from LLM    |
| score           | float   | 0.0 / 0.5 / 1.0               |
| tokens_used     | int     | API tokens consumed            |
| latency_seconds | float   | Wall-clock time                |

### 5.4 Cost Estimate (Ollama)

- Local Ollama: no per-token cost. Ensure sufficient RAM/GPU for 7B models.
- Estimated ~1800 LLM calls (900 generation + 900 evaluation) when using the same model for both.

---

## 6. Scoring Engine (`src/evaluator.py`)

### 6.1 Declarative Scoring

Uses LLM-as-judge with rubric:
- **1.0:** Definition correct AND example valid
- **0.5:** Definition correct OR example valid
- **0.0:** Fundamental misstatement

### 6.2 Procedural/Primed Scoring

Two-tier approach:
1. **Fast path:** Normalised keyword matching against ground truth (overlap > 85% → 1.0, < 25% → 0.0)
2. **Slow path:** LLM-as-judge for borderline cases

### 6.3 Standalone Scoring

```bash
python -m src.evaluator --input results/raw_responses.csv --output results/scored_results.csv
```

---

## 7. Analysis Pipeline (`src/analysis.py`)

### 7.1 Metrics Computed

Per rule:
- DA, PA, PrA (mean accuracy per condition)
- D-P Gap (DA − PA)
- Priming Effect (PrA − PA)

### 7.2 Statistical Tests

| Test                    | Purpose                                | Significance Level |
|-------------------------|----------------------------------------|:------------------:|
| Paired t-test (DA vs PA)| Core hypothesis: D-P Gap > 0          | p < 0.05           |
| Paired t-test (PrA vs PA)| Priming effect significance          | p < 0.05           |
| Wilcoxon signed-rank   | Non-parametric alternative             | p < 0.05           |
| Spearman's ρ           | Complexity–gap correlation             | p < 0.05           |
| Cohen's d              | Effect size for DA–PA difference       | d > 0.5 = medium   |
| One-way ANOVA          | Cross-condition comparison             | p < 0.05           |

### 7.3 Figures Generated

1. **scissors_graph.pdf** — The signature visualisation (DA, PA, PrA lines)
2. **heatmap.pdf** — 15×3 accuracy heatmap
3. **complexity_scatter.pdf** — Complexity vs D-P Gap with regression
4. **priming_bars.pdf** — PA vs PrA grouped bars
5. **overall_summary.pdf** — Three-bar overall means

### 7.4 Command

```bash
python -m src.analysis --input results/experiment_results.csv
# Outputs: results/metrics_summary.csv + 5 figures (PDF + PNG)
```

---

## 8. Debugging & Troubleshooting

### Common Issues

| Issue                        | Solution                                        |
|------------------------------|------------------------------------------------|
| `GEMINI_API_KEY` not set     | `cp .env.example .env` and add key             |
| JSON parse errors            | Retry logic handles most; check prompt format   |
| Rate limiting                | Tenacity handles backoff; reduce parallelism    |
| Keyword match inaccurate     | Falls back to LLM-as-judge automatically        |
| Empty responses              | Logged as score=0.0; check quota                |

### Validation Checklist

```bash
# 1. Verify problem bank
python -m src.problems --output data/problems.json
# Should print: "Saved 300 problems to data/problems.json"

# 2. Smoke test (fast)
python -m src.experiment --rules R01 --max-problems 2
# Should produce 6 rows in results/experiment_results.csv

# 3. Check analysis on smoke test output
python -m src.analysis --input results/experiment_results.csv
# Should produce figures in results/
```

---

## 9. Timeline-to-Deadline

| Date              | Task                                            |
|-------------------|-------------------------------------------------|
| Feb 6–8           | Code complete (all modules implemented)         |
| Feb 9–10          | Smoke test, debug, iterate on prompts           |
| Feb 11–14         | Full experiment run (900 data points)            |
| Feb 15–21         | Analysis, figure generation                      |
| Feb 22–Mar 4      | Draft paper in LaTeX (ACL SRW format)            |
| Mar 5–12          | Peer review, advisor feedback                    |
| Mar 13–18         | Camera-ready, submit by March 18                |

---

## 10. Key Design Decisions

1. **Temperature 0.0:** Ensures deterministic outputs for reproducibility.
2. **Separate eval LLM:** Evaluation uses a different LLMClient instance to keep token tracking clean.
3. **Hybrid scoring:** Keyword matching for speed, LLM-as-judge for accuracy.
4. **20 problems/rule:** Enough for statistical power while keeping costs low.
5. **Models:** Primary results from Mistral~7B (Ollama); Qwen~2.5~7B is also run for comparison. Multi-model comparison is a natural extension.
