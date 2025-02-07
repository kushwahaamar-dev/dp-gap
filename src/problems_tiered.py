"""
Tiered problem generator for the D-P Gap experiment.

Three tiers of increasing binding complexity:
  Tier I:   Atomic / Natural — simple propositions, real-world entities
  Tier II:  Compositional — compound propositions with 3-5 variables
  Tier III: Adversarial — belief bias + distractors + complex binding

The key insight: we preserve the SAME logical rule but increase the
BINDING LOAD. The model must recognize that a complex expression
like (A ∧ ¬B) fills the role of a single variable P in P→Q.

Usage:
    python -m src.problems_tiered --output data
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .models import Problem, ProblemBank
from .problems import build_problem_bank

# ── Abstract entities for compositional problems ────────────────────────────

_VARS = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "theta",
         "kappa", "lambda", "mu", "sigma", "omega", "phi", "psi", "rho"]

_NONSENSE = [
    ("glorp", "frabjous"), ("snark", "boojum"), ("quex", "mimsy"),
    ("blif", "slithy"), ("zim", "vorpal"), ("trelk", "brillig"),
    ("droon", "galumphing"), ("varn", "uffish"), ("plox", "wabe"),
    ("boop", "manxome"), ("freg", "beamish"), ("yonk", "chortle"),
    ("kraz", "tumtum"), ("wib", "jubjub"), ("prel", "rathful"),
    ("norf", "gimble"), ("dax", "gyre"), ("qim", "outgrabe"),
    ("zelp", "burbling"), ("trov", "whiffling"),
]

_DISTRACTORS = [
    "Statement X: The population of France is 67 million. (Ignore this.)",
    "Statement Y: Pi equals 3.14159. (Not relevant.)",
    "Statement Z: Water boils at 100°C. (Disregard.)",
    "Statement W: The speed of light is 299,792 km/s. (Irrelevant.)",
    "Statement V: Shakespeare wrote 37 plays. (Ignore.)",
    "Statement U: The Earth orbits the Sun once per year. (Disregard.)",
    "Statement T: Coffee contains caffeine. (Not relevant.)",
    "Statement S: Elephants are the largest land mammals. (Ignore.)",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  TIER II: COMPOSITIONAL BINDING
#  Same rules, but propositions are compound/abstract.
# ═══════════════════════════════════════════════════════════════════════════════

def _t2_r01() -> list[tuple[str, str]]:
    """Modus Ponens with compound propositions."""
    return [
        ("If (alpha is true AND beta is false), then (gamma OR delta) holds. "
         "We know that alpha is true AND beta is false. What can you conclude?",
         "Gamma OR delta holds."),
        ("If (the sensor is active AND the threshold is exceeded), then the alarm triggers. "
         "The sensor is active AND the threshold is exceeded. What follows?",
         "The alarm triggers."),
        ("If (NOT P OR Q) is true, then (R AND S) must hold. "
         "We are given that (NOT P OR Q) is true. What can you conclude?",
         "R AND S must hold."),
        ("If (zim is vorpal AND blif is NOT slithy), then (glorp becomes frabjous). "
         "Zim is vorpal AND blif is NOT slithy. What follows?",
         "Glorp becomes frabjous."),
        ("If (A implies B) AND (B implies C), we can treat the conjunction as a single premise P. "
         "Given P → Q where P = '(A→B) ∧ (B→C)' and Q = 'the chain is valid'. P is true. "
         "What can you conclude using only Modus Ponens?",
         "The chain is valid."),
        ("If (it is NOT the case that both X and Y are true), then (Z or W must be false). "
         "It is NOT the case that both X and Y are true. What can you conclude?",
         "Z or W must be false."),
        ("If (the reactor pressure exceeds 100 AND the coolant level drops below 50), "
         "then (emergency protocol activates OR manual override is required). "
         "The reactor pressure exceeds 100 AND the coolant level dropped below 50. What follows?",
         "Emergency protocol activates OR manual override is required."),
        ("If (snark is boojum AND trelk is NOT brillig AND plox is wabe), then droon galumphs. "
         "Snark is boojum, trelk is NOT brillig, and plox is wabe. What follows?",
         "Droon galumphs."),
        ("Let P = '(alpha > 0) ∧ (beta ≤ gamma)' and Q = 'delta is positive'. "
         "Given that if P then Q, and P is true. What is the conclusion?",
         "Delta is positive."),
        ("If (the function is continuous AND the interval is closed AND the function changes sign), "
         "then a root exists. The function is continuous, the interval is closed, and the function "
         "changes sign. What follows?",
         "A root exists."),
        ("If ((A ∨ B) ∧ ¬C), then (D ↔ E). We know (A ∨ B) ∧ ¬C. What must be true?",
         "D if and only if E."),
        ("If (quex is mimsy AND freg is beamish), then (yonk chortles OR boop is manxome). "
         "Quex is mimsy AND freg is beamish. What follows?",
         "Yonk chortles OR boop is manxome."),
        ("If (the patient has symptom A AND symptom B but NOT symptom C), then diagnosis D applies. "
         "The patient has symptom A and symptom B but not symptom C. What follows?",
         "Diagnosis D applies."),
        ("If (P₁ ∧ P₂ ∧ P₃) → Q, and all of P₁, P₂, P₃ are true. What follows?",
         "Q is true."),
        ("If (NOT (alpha AND beta)) is true, then (gamma is false AND delta is true). "
         "NOT (alpha AND beta) is true. What can you conclude?",
         "Gamma is false AND delta is true."),
        ("If (the signal strength is above threshold AND noise ratio is below limit AND "
         "the channel is not blocked), then transmission succeeds. All three conditions hold. "
         "What follows?",
         "Transmission succeeds."),
        ("If (plox is wabe AND varn is uffish AND droon is NOT galumphing), "
         "then (snark becomes boojum AND glorp becomes frabjous). "
         "Plox is wabe, varn is uffish, and droon is NOT galumphing. What follows?",
         "Snark becomes boojum AND glorp becomes frabjous."),
        ("If ((X → Y) ∧ (Y → Z)) is true, then (X → Z) is true. "
         "We know (X → Y) ∧ (Y → Z). Using Modus Ponens on this compound premise, what follows?",
         "X → Z is true."),
        ("If (the variable is initialized AND the type is correct AND no overflow occurs), "
         "then the computation returns a valid result. All three conditions are met. Conclusion?",
         "The computation returns a valid result."),
        ("If (A ∧ B ∧ ¬C ∧ D) → (E ∨ F ∨ ¬G), and A, B, D are true while C is false. What follows?",
         "E ∨ F ∨ ¬G."),
    ]


def _t2_r02() -> list[tuple[str, str]]:
    """Modus Tollens with compound propositions."""
    return [
        ("If (alpha AND beta), then (gamma AND delta). "
         "We know that it is NOT the case that (gamma AND delta). What can you conclude?",
         "It is NOT the case that (alpha AND beta). At least one of alpha or beta is false."),
        ("If (the system is online AND the database is connected), then queries return results. "
         "Queries are NOT returning results. What follows?",
         "It is NOT the case that (the system is online AND the database is connected)."),
        ("If (P ∧ Q ∧ R), then (S ∨ T). Neither S nor T is true. What follows?",
         "It is NOT the case that (P ∧ Q ∧ R). At least one of P, Q, R is false."),
        ("If (glorp is frabjous AND snark is boojum), then (quex becomes mimsy). "
         "Quex is NOT mimsy. What follows?",
         "It is NOT the case that (glorp is frabjous AND snark is boojum)."),
        ("If (the temperature is above 30 AND humidity exceeds 80%), then condensation forms. "
         "No condensation has formed. What can you conclude?",
         "It is NOT the case that (temperature is above 30 AND humidity exceeds 80%)."),
        ("If (A ∨ B) → C, and C is false. What can you conclude about (A ∨ B)?",
         "(A ∨ B) is false, meaning both A and B are false."),
        ("If (NOT P) → (Q AND R). We know (Q AND R) is false. What follows?",
         "NOT P is false, so P is true."),
        ("If (blif is slithy OR zim is vorpal) → (trelk is brillig). "
         "Trelk is NOT brillig. What follows?",
         "Neither blif is slithy nor zim is vorpal."),
        ("If (the experiment succeeds AND results are significant AND bias is controlled), "
         "then the paper is accepted. The paper was NOT accepted. What can you conclude?",
         "It is NOT the case that all three conditions hold simultaneously."),
        ("If (X ↔ Y) → Z, and Z is false. What can you conclude?",
         "X ↔ Y is false, meaning X and Y have different truth values."),
        ("If (alpha > beta AND beta > gamma), then alpha > gamma. "
         "Alpha is NOT greater than gamma. What follows?",
         "It is NOT the case that (alpha > beta AND beta > gamma)."),
        ("If (P₁ ∧ P₂) → (Q₁ ∧ Q₂ ∧ Q₃). We know Q₂ is false. What follows?",
         "(P₁ ∧ P₂) is false, since (Q₁ ∧ Q₂ ∧ Q₃) is false."),
        ("If (freg is beamish AND yonk is NOT chortle), then boop is manxome. "
         "Boop is NOT manxome. What follows?",
         "It is NOT the case that (freg is beamish AND yonk is NOT chortle)."),
        ("If ((A → B) ∧ (C → D)) → (E ∧ F). (E ∧ F) is false. What can you conclude?",
         "It is NOT the case that ((A → B) ∧ (C → D))."),
        ("If (the circuit is complete AND voltage is applied AND resistance is finite), "
         "then current flows. Current is NOT flowing. What follows?",
         "At least one condition is false: circuit incomplete, no voltage, or infinite resistance."),
        ("If (¬A ∧ B) → (C ∨ D). Neither C nor D is true. What can you conclude?",
         "¬A ∧ B is false. Since B's truth is unknown, either A is true or B is false."),
        ("If (droon galumphs AND plox is wabe) → (varn is uffish). "
         "Varn is NOT uffish. What follows?",
         "It is NOT the case that (droon galumphs AND plox is wabe)."),
        ("If (X > Y AND Y > Z AND Z > W) → X > W. X is NOT greater than W. What follows?",
         "It is NOT the case that (X > Y AND Y > Z AND Z > W)."),
        ("If (the file exists AND permissions are granted AND disk space is available), "
         "then the write operation succeeds. The write failed. What follows?",
         "At least one condition is false."),
        ("If (A ∧ B ∧ C ∧ D) → E. E is false. What follows about A, B, C, D?",
         "At least one of A, B, C, D is false."),
    ]


def _t2_r03() -> list[tuple[str, str]]:
    """Hypothetical Syllogism with compound propositions."""
    return [
        ("If (A ∧ B), then (C ∨ D). If (C ∨ D), then E. What follows if (A ∧ B)?",
         "E."),
        ("If (glorp is frabjous), then (snark AND quex are boojum). "
         "If (snark AND quex are boojum), then trelk becomes brillig. "
         "What follows if glorp is frabjous?",
         "Trelk becomes brillig."),
        ("If (the input is valid AND sanitized), then the query executes. "
         "If the query executes, then (results are cached AND logged). "
         "What follows if the input is valid AND sanitized?",
         "Results are cached AND logged."),
        ("If (NOT P), then (Q ∧ R). If (Q ∧ R), then (S → T). What follows if NOT P?",
         "S → T."),
        ("If (alpha ∧ beta) → gamma. If gamma → (delta ∨ epsilon). What follows if alpha ∧ beta?",
         "Delta ∨ epsilon."),
    ] + [
        (f"If ({a} is {p}), then ({b} is {q}). If ({b} is {q}), then ({c} is {r}). "
         f"What follows if {a} is {p}?",
         f"{c} is {r}.")
        for (a, p), (b, q), (c, r) in [
            (_NONSENSE[0], _NONSENSE[1], _NONSENSE[2]),
            (_NONSENSE[3], _NONSENSE[4], _NONSENSE[5]),
            (_NONSENSE[6], _NONSENSE[7], _NONSENSE[8]),
            (_NONSENSE[9], _NONSENSE[10], _NONSENSE[11]),
            (_NONSENSE[0], _NONSENSE[3], _NONSENSE[6]),
            (_NONSENSE[1], _NONSENSE[4], _NONSENSE[7]),
            (_NONSENSE[2], _NONSENSE[5], _NONSENSE[8]),
            (_NONSENSE[9], _NONSENSE[0], _NONSENSE[1]),
            (_NONSENSE[10], _NONSENSE[2], _NONSENSE[3]),
            (_NONSENSE[11], _NONSENSE[6], _NONSENSE[9]),
            (_NONSENSE[0], _NONSENSE[5], _NONSENSE[10]),
            (_NONSENSE[1], _NONSENSE[8], _NONSENSE[11]),
            (_NONSENSE[2], _NONSENSE[7], _NONSENSE[4]),
            (_NONSENSE[3], _NONSENSE[9], _NONSENSE[0]),
            (_NONSENSE[4], _NONSENSE[11], _NONSENSE[1]),
        ]
    ][:20]


def _t2_r04() -> list[tuple[str, str]]:
    """Disjunctive Syllogism with compound propositions."""
    return [
        ("Either (alpha AND beta) or (gamma AND delta). "
         "It is NOT the case that (alpha AND beta). What can you conclude?",
         "Gamma AND delta."),
        ("Either (P → Q) or (R ∧ S). (P → Q) is false. What follows?",
         "R ∧ S."),
        ("Either (the server is down AND maintenance is scheduled) or (a DDoS attack is occurring). "
         "The server is NOT down or maintenance is NOT scheduled. What follows?",
         "A DDoS attack is occurring."),
        ("Either (glorp is frabjous AND snark is boojum) or (quex is mimsy). "
         "It is NOT the case that (glorp is frabjous AND snark is boojum). What follows?",
         "Quex is mimsy."),
        ("Either (A ∧ B ∧ C) or (D ∨ E). NOT (A ∧ B ∧ C). What follows?",
         "D ∨ E."),
    ] + [
        (f"Either ({a} is {p}) or ({b} is {q}). {a} is NOT {p}. What follows?",
         f"{b} is {q}.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+1) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r05() -> list[tuple[str, str]]:
    """Contrapositive with compound propositions."""
    return [
        ("'If (A ∧ B), then (C ∨ D)' is logically equivalent to what contrapositive?",
         "If NOT (C ∨ D) — i.e., (¬C ∧ ¬D) — then NOT (A ∧ B)."),
        ("'If (the engine runs AND fuel is present), then exhaust is produced' — "
         "state the contrapositive.",
         "If exhaust is NOT produced, then it is NOT the case that (the engine runs AND fuel is present)."),
        ("'If (P ∧ Q ∧ R), then S' — what is the contrapositive?",
         "If NOT S, then NOT (P ∧ Q ∧ R)."),
        ("'If (glorp is frabjous OR snark is boojum), then quex is mimsy' — contrapositive?",
         "If quex is NOT mimsy, then (glorp is NOT frabjous AND snark is NOT boojum)."),
        ("'If (NOT A), then (B ∧ C)' — state the contrapositive.",
         "If NOT (B ∧ C), then A."),
    ] + [
        (f"'If ({a} is {p}), then ({b} is {q})' — state the contrapositive.",
         f"If {b} is NOT {q}, then {a} is NOT {p}.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+3) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r06() -> list[tuple[str, str]]:
    """De Morgan's Law I with compound/nested propositions."""
    return [
        ("It is NOT the case that ((A ∧ B) AND (C ∧ D)). "
         "Apply De Morgan's Law. What follows?",
         "Either NOT (A ∧ B) or NOT (C ∧ D) (or both)."),
        ("It is NOT the case that (the server is running AND the database is connected AND the cache is warm). "
         "Apply De Morgan's Law to the outermost negation. What follows?",
         "Either the server is not running, or the database is not connected, or the cache is not warm."),
        ("¬((P → Q) ∧ (R → S)). What does this mean?",
         "Either (P → Q) is false or (R → S) is false (or both)."),
        ("It is NOT the case that (glorp is frabjous AND snark is boojum AND quex is mimsy). What follows?",
         "At least one is false: glorp is not frabjous, or snark is not boojum, or quex is not mimsy."),
        ("¬(A ∧ B ∧ C ∧ D). Apply De Morgan's Law.",
         "¬A ∨ ¬B ∨ ¬C ∨ ¬D."),
    ] + [
        (f"It is NOT the case that ({a} is {p} AND {b} is {q}). What follows?",
         f"Either {a} is NOT {p}, or {b} is NOT {q} (or both).")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+2) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r07() -> list[tuple[str, str]]:
    """De Morgan's Law II with compound propositions."""
    return [
        ("It is NOT the case that ((A ∧ B) OR (C ∧ D)). "
         "Apply De Morgan's Law. What follows?",
         "NOT (A ∧ B) AND NOT (C ∧ D)."),
        ("¬(P ∨ Q ∨ R). What does this simplify to?",
         "¬P ∧ ¬Q ∧ ¬R."),
        ("It is NOT the case that (the alarm sounds OR the lights flash OR the siren activates). What follows?",
         "The alarm does not sound AND the lights do not flash AND the siren does not activate."),
        ("¬((glorp is frabjous) ∨ (snark is boojum) ∨ (quex is mimsy)). What can you conclude?",
         "Glorp is NOT frabjous AND snark is NOT boojum AND quex is NOT mimsy."),
        ("It is NOT the case that ((X > Y) OR (Y > Z)). What follows?",
         "X is NOT greater than Y AND Y is NOT greater than Z."),
    ] + [
        (f"It is NOT the case that ({a} is {p} OR {b} is {q}). What follows?",
         f"{a} is NOT {p} AND {b} is NOT {q}.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+4) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r08() -> list[tuple[str, str]]:
    """Double Negation with compound propositions."""
    return [
        ("It is NOT the case that (A ∧ B) is NOT true. What can you conclude?",
         "(A ∧ B) is true."),
        ("It is false that (the system is NOT operational). What follows?",
         "The system is operational."),
        ("¬¬(P ∨ Q). Simplify.",
         "P ∨ Q."),
        ("It is NOT the case that (glorp is NOT frabjous AND snark is NOT boojum). "
         "Can you simplify using double negation? Be careful — this is De Morgan + double negation.",
         "Glorp is frabjous OR snark is boojum."),
        ("It is NOT NOT NOT the case that P is true. What is the truth value of P?",
         "P is false. (Three negations = one negation.)"),
    ] + [
        (f"It is NOT the case that {a} is NOT {p}. What follows?",
         f"{a} is {p}.")
        for (a, p) in _NONSENSE[:15]
    ][:20]


def _t2_r09() -> list[tuple[str, str]]:
    """Transitivity with compound propositions."""
    return [
        ("(A ∧ B) is strictly greater than (C ∧ D). (C ∧ D) is strictly greater than E. "
         "What follows about (A ∧ B) and E?",
         "(A ∧ B) is strictly greater than E."),
        ("The processing speed of System X exceeds that of System Y. "
         "System Y's speed exceeds System Z. What follows?",
         "System X's speed exceeds System Z."),
        ("Glorp is more frabjous than snark. Snark is more frabjous than quex. "
         "What follows about glorp and quex?",
         "Glorp is more frabjous than quex."),
        ("If α > β and β > γ and γ > δ, what follows about α and δ?",
         "α > δ."),
        ("Team A scored more than Team B. Team B scored more than Team C. "
         "Team C scored more than Team D. What follows about A and D?",
         "Team A scored more than Team D."),
    ] + [
        (f"{a} is more {p} than {b}. {b} is more {p} than {c}. "
         f"What follows about {a} and {c}?",
         f"{a} is more {p} than {c}.")
        for (a, p), (b, _), (c, __) in [
            (_NONSENSE[i], _NONSENSE[(i+1) % len(_NONSENSE)], _NONSENSE[(i+2) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r10() -> list[tuple[str, str]]:
    """Proof by Contradiction with compound propositions."""
    return [
        ("Assume (A ∧ B ∧ C) is false. This leads to a contradiction. What can you conclude?",
         "(A ∧ B ∧ C) is true."),
        ("Assume that NOT (P → Q). This assumption leads to a logical contradiction. What follows?",
         "P → Q is true."),
        ("Assume (glorp is NOT frabjous OR snark is NOT boojum). "
         "This leads to a contradiction. What can you conclude?",
         "Glorp IS frabjous AND snark IS boojum."),
        ("Assume the set S is finite. This assumption leads to a contradiction "
         "when combined with the given axioms. What follows?",
         "The set S is infinite."),
        ("Assume ¬(∃x: P(x)). This leads to a contradiction. What can you conclude?",
         "There exists an x such that P(x)."),
    ] + [
        (f"Assume {a} is NOT {p}. This leads to a contradiction. What follows?",
         f"{a} is {p}.")
        for (a, p) in _NONSENSE[:15]
    ][:20]


def _t2_r11() -> list[tuple[str, str]]:
    """Universal Instantiation with compound propositions."""
    return [
        ("For all x: if x is (type-A AND type-B), then x has property-C. "
         "Object 'omega' is type-A AND type-B. What follows about omega?",
         "Omega has property-C."),
        ("All (systems that are online AND authenticated) can access the database. "
         "System X is online AND authenticated. What follows?",
         "System X can access the database."),
        ("For all x: if x is a glorp and x is frabjous, then x snarks. "
         "Quex is a glorp and quex is frabjous. What follows?",
         "Quex snarks."),
        ("∀x: (P(x) ∧ Q(x)) → R(x). We know P(a) ∧ Q(a). What follows?",
         "R(a)."),
        ("All entities that satisfy (condition-1 AND condition-2 AND NOT condition-3) "
         "are classified as type-D. Entity E satisfies condition-1 and condition-2, "
         "and does NOT satisfy condition-3. What follows?",
         "Entity E is classified as type-D."),
    ] + [
        (f"All {a}s that are {p} are also {q}. This {b} is a {a} that is {p}. What follows?",
         f"This {b} is {q}.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+5) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r12() -> list[tuple[str, str]]:
    """Biconditional Elimination with compound propositions."""
    return [
        ("(A ∧ B) if and only if (C ∨ D). We know (A ∧ B) is true. What follows?",
         "(C ∨ D) is true."),
        ("(The system is stable) if and only if (load < 80% AND no errors). "
         "The system is stable. What follows?",
         "Load < 80% AND no errors."),
        ("(glorp is frabjous) if and only if (snark is boojum AND quex is mimsy). "
         "Glorp IS frabjous. What can you conclude?",
         "Snark is boojum AND quex is mimsy."),
        ("P ↔ (Q ∧ R). P is false. What can you conclude about (Q ∧ R)?",
         "(Q ∧ R) is false."),
        ("(X > Y) ↔ (Z < W). (Z < W) is true. What follows?",
         "X > Y."),
    ] + [
        (f"({a} is {p}) if and only if ({b} is {q}). {a} is {p}. What follows?",
         f"{b} is {q}.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+6) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r13() -> list[tuple[str, str]]:
    """Constructive Dilemma with compound propositions."""
    return [
        ("If (A ∧ B), then C. If (D ∨ E), then F. "
         "Either (A ∧ B) or (D ∨ E). What can you conclude?",
         "Either C or F."),
        ("If (glorp is frabjous), then snark activates. "
         "If (quex is mimsy), then trelk activates. "
         "Either glorp is frabjous or quex is mimsy. What follows?",
         "Either snark activates or trelk activates."),
        ("If (P ∧ Q) → R, and (S ∧ T) → U. (P ∧ Q) ∨ (S ∧ T). What follows?",
         "R ∨ U."),
        ("If (the server crashes), then data is lost. "
         "If (the backup fails), then recovery is impossible. "
         "Either the server crashes or the backup fails. What follows?",
         "Either data is lost or recovery is impossible."),
        ("If alpha, then (beta ∧ gamma). If delta, then (epsilon ∧ zeta). "
         "Either alpha or delta. What can you conclude?",
         "Either (beta ∧ gamma) or (epsilon ∧ zeta)."),
    ] + [
        (f"If ({a} is {p}), then result-X. If ({b} is {q}), then result-Y. "
         f"Either ({a} is {p}) or ({b} is {q}). What follows?",
         "Either result-X or result-Y.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+3) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r14() -> list[tuple[str, str]]:
    """Absorption with compound propositions."""
    return [
        ("If (A ∧ B), then C. Using absorption, what can you derive?",
         "If (A ∧ B), then ((A ∧ B) ∧ C)."),
        ("If P → Q. By absorption, what can you derive?",
         "P → (P ∧ Q)."),
        ("If (glorp is frabjous), then (snark is boojum). By absorption?",
         "If (glorp is frabjous), then (glorp is frabjous AND snark is boojum)."),
        ("If (the test passes), then (the build succeeds). Apply absorption.",
         "If (the test passes), then (the test passes AND the build succeeds)."),
        ("If (X > 0 ∧ Y > 0), then Z > 0. By absorption?",
         "If (X > 0 ∧ Y > 0), then ((X > 0 ∧ Y > 0) ∧ Z > 0)."),
    ] + [
        (f"If ({a} is {p}), then ({b} is {q}). Apply the absorption rule.",
         f"If ({a} is {p}), then ({a} is {p} AND {b} is {q}).")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+1) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


def _t2_r15() -> list[tuple[str, str]]:
    """Material Implication with compound propositions."""
    return [
        ("'If (A ∧ B), then C' — rewrite using material implication.",
         "NOT (A ∧ B) OR C. Equivalently: (¬A ∨ ¬B) ∨ C."),
        ("'If (glorp is frabjous AND snark is boojum), then quex is mimsy' — "
         "express as a disjunction.",
         "Either (glorp is NOT frabjous OR snark is NOT boojum) OR quex is mimsy."),
        ("P → Q is equivalent to what disjunction?",
         "¬P ∨ Q."),
        ("'If the reactor overheats AND coolant fails, then meltdown occurs' — "
         "rewrite as disjunction.",
         "Either (the reactor does NOT overheat OR coolant does NOT fail) OR meltdown occurs."),
        ("(A ∧ B ∧ C) → D. Rewrite using material implication.",
         "¬(A ∧ B ∧ C) ∨ D. Equivalently: (¬A ∨ ¬B ∨ ¬C) ∨ D."),
    ] + [
        (f"'If ({a} is {p}), then ({b} is {q})' — rewrite as a disjunction.",
         f"Either {a} is NOT {p}, or {b} is {q}.")
        for (a, p), (b, q) in [
            (_NONSENSE[i], _NONSENSE[(i+2) % len(_NONSENSE)])
            for i in range(15)
        ]
    ][:20]


_T2_GENERATORS = {
    "R01": _t2_r01, "R02": _t2_r02, "R03": _t2_r03, "R04": _t2_r04,
    "R05": _t2_r05, "R06": _t2_r06, "R07": _t2_r07, "R08": _t2_r08,
    "R09": _t2_r09, "R10": _t2_r10, "R11": _t2_r11, "R12": _t2_r12,
    "R13": _t2_r13, "R14": _t2_r14, "R15": _t2_r15,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  TIER III: ADVERSARIAL — distractors + belief bias + complex binding
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap_adversarial(text: str, rng: random.Random) -> str:
    """Add 3-5 distractor statements and adversarial framing."""
    n = rng.randint(3, 5)
    distractors = rng.sample(_DISTRACTORS, n)
    # Interleave distractors with the problem
    parts = []
    parts.append(distractors[0])
    parts.append(distractors[1])
    parts.append("IMPORTANT: Based ONLY on the following logical premises, answer the question. "
                 "Ignore ALL other statements in this prompt.")
    parts.append(text)
    for d in distractors[2:]:
        parts.append(d)
    return " ".join(parts)


def build_tiered_problem_bank(seed: int = 42) -> dict[str, ProblemBank]:
    """Build all three tier problem banks."""
    rng = random.Random(seed)

    # Tier I: original problems
    tier1 = build_problem_bank()

    # Tier II: compositional problems
    tier2_problems: list[Problem] = []
    for rule_id, gen_fn in _T2_GENERATORS.items():
        pairs = gen_fn()
        for i, (text, gt) in enumerate(pairs[:20]):
            tier2_problems.append(Problem(
                id=f"{rule_id}_T2_P{i+1:02d}",
                rule_id=rule_id,
                text=text,
                ground_truth=gt,
            ))

    # Tier III: adversarial wrapping of Tier II problems
    tier3_problems: list[Problem] = []
    for rule_id, gen_fn in _T2_GENERATORS.items():
        pairs = gen_fn()
        for i, (text, gt) in enumerate(pairs[:20]):
            adversarial_text = _wrap_adversarial(text, rng)
            tier3_problems.append(Problem(
                id=f"{rule_id}_T3_P{i+1:02d}",
                rule_id=rule_id,
                text=adversarial_text,
                ground_truth=gt,
            ))

    return {
        "tier1": tier1,
        "tier2": ProblemBank(problems=tier2_problems),
        "tier3": ProblemBank(problems=tier3_problems),
    }


def save_tiered_banks(base_dir: Path | None = None) -> dict[str, ProblemBank]:
    """Save all three tiers to separate JSON files."""
    base_dir = base_dir or Path(__file__).parent.parent / "data"
    base_dir.mkdir(parents=True, exist_ok=True)

    banks = build_tiered_problem_bank()

    for tier_name, bank in banks.items():
        path = base_dir / f"problems_{tier_name}.json"
        with open(path, "w") as f:
            f.write(bank.model_dump_json(indent=2))
        print(f"  Saved {len(bank.problems)} {tier_name} problems to {path}")

    return banks


def load_tiered_bank(tier: str, base_dir: Path | None = None) -> ProblemBank:
    """Load a specific tier's problem bank."""
    base_dir = base_dir or Path(__file__).parent.parent / "data"
    path = base_dir / f"problems_{tier}.json"
    if not path.exists():
        banks = save_tiered_banks(base_dir)
        return banks[tier]
    with open(path) as f:
        return ProblemBank.model_validate(json.load(f))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tiered problem banks")
    parser.add_argument("--output-dir", type=str, default="data")
    args = parser.parse_args()
    save_tiered_banks(Path(args.output_dir))
