# Independent Senior Review — ACL 2026 SRW
## D-P Gap: Declarative-Procedural Paradox in Logical Inference

**Role:** Independent reviewer / ACL-RW PC member / Reproducibility & methodology auditor  
**Stance:** No defence of the paper; identification of mistakes, weaknesses, and rejection risks only.

---

## POST-REVISION UPDATE (all fixes applied)

All issues below have been addressed:

- **Contribution 3** (ACL SRW): Wording changed to “minimal recovery (+0.02), indicating the deficit is largely binding rather than retrieval.” Figure caption (Scissors) updated to “limited recovery for Mistral~7B.”
- **Default model:** When `OLLAMA_BASE_URL` is set, `python -m src.experiment` now defaults to `mistral:7b` (paper reproducibility). Documented in README and EXECUTION_PLAN.
- **rules.py:** Docstring updated to “1 = easiest, 4 = hardest.”
- **Reproducibility:** Paper Limitations now include a bullet: problem bank and code released; paper results use Mistral~7B with `--model mistral:7b`; exact scores may vary slightly due to API non-determinism.
- **Other papers (starsem, iclr-ws, colm):** “Partially recovers” / “partially closes” aligned to “minimal recovery” / “binding” where applicable.

**Updated verdict: ACCEPT.** The paper is internally consistent, reproducible (with clear instructions and sensible defaults), and appropriate for ACL-RW.

---

## 1. Verdict Summary (original)

**Verdict (after revisions): ACCEPT**

The paper formalises a clear diagnostic (D-P Gap, Scissors Pattern) and uses a controlled benchmark with three conditions and hybrid scoring. The main result (large DA–PA gap, minimal priming for Mistral~7B) is internally consistent and honestly reported; limitations (same-model judge, single domain, author-assigned complexity, reproducibility) are stated. After the revisions above, the contributions list and figure captions align with “minimal recovery” and “binding,” and reproducibility is documented with an env-based default for the paper model. For a student workshop the work is methodologically sound and the framing is relevant to ACL 2026.

---

## 2. Confirmed Mistakes (if any) — all FIXED

| Issue | Severity | Status |
|-------|----------|--------|
| **Contribution 3** (main.tex): “partially recovers” vs. minimal recovery. | **Medium** | **FIXED:** Replaced with “minimal recovery (+0.02), indicating the deficit is largely binding rather than retrieval.” |
| **Default model in code**: CLI default differed from paper. | **Medium** | **FIXED:** Default is `mistral:7b` when `OLLAMA_BASE_URL` is set; documented in README and EXECUTION_PLAN. |
| **rules.py docstring**: “5 = hardest” but scale is 1–4. | **Low** | **FIXED:** Docstring now says “4 = hardest.” |
| **No reproducibility statement**: Exact scores may vary. | **Low** | **FIXED:** Paper Limitations include a Reproducibility bullet. |

No critical data-leakage or metric-misuse bugs were found. Same-model generation + judge is acknowledged in Limitations.

---

## 3. Experiment Audit

- **Data loading:** Problem bank loaded from JSON (or built from fixed generators in `problems.py`). No shuffle; order is deterministic. No train/test split (benchmark is fixed).
- **Preprocessing:** None beyond loading; problem text and ground truth used as-is.
- **Model usage:** One model used for both generation and LLM-as-judge (`experiment.py`: same `model` for `llm` and `eval_llm`). Paper states this in Limitations.
- **Evaluation:** Declarative: LLM-as-judge with 3-point rubric. Procedural/Primed: keyword match first (normalised string, threshold 0.9/0.2), else LLM-as-judge. Keyword path can produce 0/1 only; LLM path can produce 0/0.5/1 (EvaluatorVerdict). Procedural scoring uses `ground_truth` from the problem; no leakage from declarative or primed responses.
- **Seed control:** None in the main experiment. Problem bank is deterministic. LLM non-determinism is not addressed.
- **Data leakage:** None identified. Declarative condition does not see the problem; procedural sees only the problem; primed sees rule + problem. Ground truth is not shown to the model at generation time.
- **Metric use:** DA, PA, PrA as means per condition; D-P Gap = DA − PA; Priming Effect = PrA − PA. All match the paper. Paired t-test and Wilcoxon on **per-rule** means (n=15); ANOVA on raw scores (900). Appropriate.
- **Silent bugs:** Failures in `experiment.py` are recorded with `score=0.0` and `raw_response="ERROR: ..."`; they are not dropped. R04_P10 in real runs sometimes produces validation errors (model output not valid JSON); those rows get score 0. So no silent drop of data.

**Edge case:** R04_P10 (Disjunctive Syllogism): “Either the test passed or there is a bug. The test passed. What can you conclude about whether there is a bug?” Ground truth: “We cannot conclude anything additional from this alone.” This tests *correct non-application* of the rule (do not conclude “no bug”). It is logically valid but differs from the usual “apply rule → get conclusion” pattern. A reviewer could call it ambiguous or a “trick” item; worth a brief note in the method or appendix.

---

## 4. Results Validity Check

- **Statistical meaning:** Paired t-test (DA vs PA) and ANOVA are significant; Spearman (complexity vs gap) is not (ρ = 0.38, p = 0.17). Paper correctly reports “positive trend that does not reach significance.” No overclaim.
- **Context:** Mistral~7B (primary) vs Qwen~2.5~7B (comparison) is clearly stated; Qwen’s smaller/negative gap is mentioned. Model-dependent interpretation is appropriate.
- **Overinterpretation:** Contribution 3 has been fixed. Elsewhere the paper correctly says priming gives minimal recovery (+0.02) and frames the deficit as binding. The Scissors Pattern is described as “characteristic” and “signature”—acceptable for a single primary model if kept as a diagnostic pattern rather than a universal law.

---

## 5. Model Usage Sanity Check

- **Mistral~7B (Ollama):** Primary model; paper is built around its results. Justified.
- **Qwen~2.5~7B:** Explicitly for comparison; shows that gap size and priming effect are model-dependent. Justified.
- **Same model for generation and judge:** Not ideal for validity; paper acknowledges this and states that an independent evaluator would strengthen validity. Acceptable as a stated limitation.

No arbitrary or unjustified model comparisons.

---

## 6. Paper Consistency Check

- **Abstract ↔ Body ↔ Discussion ↔ Conclusion:** All align on: four complexity levels (1–4), Mistral~7B primary, Qwen for comparison, minimal priming (+0.02), deficit as largely *binding*.
- **Consistency (post-revision):** Contribution 3 and figure captions now align with “minimal recovery” and “binding.”
- **Method ↔ Results:** Table 3 (per-rule) and Table 2 (overall) match the described metrics. Figure captions match the narrative.

---

## 7. Language & Framing Audit — Risky Sentences

| Quoted text | Risk |
|-------------|------|
| “No prior study has identified or measured this topological signature.” | Strong novelty claim; a reviewer may cite Li et al. (declarative/procedural hints) or kinship/TiG work and ask for a clearer distinction. |
| ~~“We present evidence… via a Priming condition that **partially recovers** performance.”~~ | **FIXED:** Now states “minimal recovery (+0.02), indicating the deficit is largely binding rather than retrieval.” |
| “Our benchmark and metrics provide a **reusable** diagnostic lens.” | “Reusable” is fine if code/data are released; “diagnostic lens” is slightly promotional but acceptable for a workshop. |
| “The Scissors Pattern is the **visual signature**.” | Could be read as overclaim if only one primary model; paper already limits to Mistral~7B. Acceptable. |

---

## 8. Novelty Re-evaluation

- **What’s new:** (1) Formal D-P Gap metric and Scissors Pattern as a complexity-indexed diagnostic; (2) 300-problem benchmark with 15 rules and three conditions; (3) Priming condition used to argue for binding (not retrieval) failure when recovery is minimal.
- **What’s incremental:** The knowing–doing gap is already discussed (e.g. kinship QA, TiG, Li et al.). This work adds **quantification**, **isolation by rule and complexity**, and a **single-model binding interpretation** when priming fails to help.
- **ACL-RW fit:** For a student workshop, the contribution is sufficient: clear framing, reproducible design, honest limitations. A reviewer focused on “incremental” may still score down; the fix to Contribution 3 and clearer reproducibility would reduce that risk.

---

## 9. Reproducibility Check (post-revision)

- **Clone + run:** Yes. With `OLLAMA_BASE_URL` set, `python -m src.experiment` defaults to `mistral:7b`; no `--model` needed for paper results. README and EXECUTION_PLAN document this.
- **Reproduce results:** Same problem bank + same model + same scoring logic yield similar aggregate results; paper states that exact scores may vary slightly (API non-determinism).
- **Risks:** Evaluator uses same model as generator (documented in Limitations).

---

## 10. Ethics & Transparency

- Model choices (Mistral, Qwen, Ollama) and limitations (same-model judge, single domain, author-assigned complexity) are stated.
- Ethics statement: no human subjects, synthetic benchmark. LLM-as-judge bias acknowledged.
- **Omission risk:** A reader might assume “priming partially closes the gap” from prior drafts; the current text correctly says “minimal recovery” for Mistral. Contribution 3 is the only remaining inconsistency.

---

## 11. Acceptance Likelihood (0–100%) — post-revision

**Estimate: 70–80%**

- **Novelty:** Moderate (formalisation + benchmark + binding interpretation); sufficient for a workshop.
- **Rigor:** Good: controlled design, three conditions, hybrid scoring, stated limitations.
- **Experimental soundness:** Good; same-model judge disclosed.
- **Writing quality:** Clear; internal consistency restored (Contribution 3 and captions fixed).
- **Reproducibility:** Documented; default model aligns with paper when Ollama is used.
- **Workshop fit (ACL-RW):** Good; student work, diagnostic focus, explainability-relevant.

Rejection risk is reduced after the applied fixes.

---

## 12. Rejection Scenarios

| Scenario | Fatal? | Fixable before camera-ready? |
|----------|--------|------------------------------|
| **“Same model for generation and scoring invalidates the main result.”** | Not fatal if framed as limitation. | Already in Limitations. Optional: add one run with a different judge model and report in appendix. |
| **“Contribution 3 contradicts the rest of the paper (partially vs minimal recovery).”** | Was fixable. | **FIXED.** |
| **“Reproducibility is weak: default model and no seed.”** | Can hurt score. | **Yes.** Document required `--model` and problem-bank fix; add one sentence on non-determinism. |

---

## 13. Final Acceptance Probability (post-revision)

**70–80%** — Accept. Contribution 3 and reproducibility are fixed; the paper is consistent and reproducible with clear instructions.

---

## 14. Confidence Statement (post-revision)

**Would I personally vote to accept this paper at ACL-RW?**

**Yes.** The requested revisions (Contribution 3, reproducibility note, default model when Ollama is set) have been applied. The paper is internally consistent, reproducible with clear instructions, and appropriate for ACL-RW. The core idea (D-P Gap, Scissors Pattern, binding interpretation when priming fails) is clear and useful.
