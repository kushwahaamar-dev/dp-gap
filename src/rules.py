"""
The 15 logical inference rules used in the D-P Gap study.

Each rule has a formal definition, natural-language description, a worked
example, and a complexity rating (1 = easiest, 4 = hardest).
"""

from .models import LogicalRule

RULES: list[LogicalRule] = [
    LogicalRule(
        id="R01",
        name="Modus Ponens",
        formal="P → Q, P ⊢ Q",
        description=(
            "Modus Ponens states that if P implies Q, and P is true, "
            "then Q must be true."
        ),
        example=(
            "If it is raining, then the ground is wet. "
            "It is raining. Therefore, the ground is wet."
        ),
        complexity=1,
    ),
    LogicalRule(
        id="R02",
        name="Modus Tollens",
        formal="P → Q, ¬Q ⊢ ¬P",
        description=(
            "Modus Tollens states that if P implies Q, and Q is false, "
            "then P must be false."
        ),
        example=(
            "If it is raining, then the ground is wet. "
            "The ground is not wet. Therefore, it is not raining."
        ),
        complexity=2,
    ),
    LogicalRule(
        id="R03",
        name="Hypothetical Syllogism",
        formal="P → Q, Q → R ⊢ P → R",
        description=(
            "Hypothetical Syllogism states that if P implies Q, and Q implies R, "
            "then P implies R."
        ),
        example=(
            "If it rains, the ground is wet. If the ground is wet, the flowers bloom. "
            "Therefore, if it rains, the flowers bloom."
        ),
        complexity=2,
    ),
    LogicalRule(
        id="R04",
        name="Disjunctive Syllogism",
        formal="P ∨ Q, ¬P ⊢ Q",
        description=(
            "Disjunctive Syllogism states that if P or Q is true, and P is false, "
            "then Q must be true."
        ),
        example=(
            "Either it is sunny or it is cloudy. It is not sunny. "
            "Therefore, it is cloudy."
        ),
        complexity=2,
    ),
    LogicalRule(
        id="R05",
        name="Contrapositive",
        formal="P → Q ≡ ¬Q → ¬P",
        description=(
            "The Contrapositive states that the statement 'if P then Q' is "
            "logically equivalent to 'if not Q then not P'."
        ),
        example=(
            "'If it is a dog, then it is an animal' is equivalent to "
            "'If it is not an animal, then it is not a dog.'"
        ),
        complexity=2,
    ),
    LogicalRule(
        id="R06",
        name="De Morgan's Law I",
        formal="¬(P ∧ Q) ≡ ¬P ∨ ¬Q",
        description=(
            "De Morgan's first law states that the negation of a conjunction "
            "is equivalent to the disjunction of the negations."
        ),
        example=(
            "'It is not the case that both Alice and Bob passed' is equivalent to "
            "'Alice did not pass, or Bob did not pass (or both).'"
        ),
        complexity=3,
    ),
    LogicalRule(
        id="R07",
        name="De Morgan's Law II",
        formal="¬(P ∨ Q) ≡ ¬P ∧ ¬Q",
        description=(
            "De Morgan's second law states that the negation of a disjunction "
            "is equivalent to the conjunction of the negations."
        ),
        example=(
            "'It is not the case that Alice or Bob passed' is equivalent to "
            "'Alice did not pass AND Bob did not pass.'"
        ),
        complexity=3,
    ),
    LogicalRule(
        id="R08",
        name="Double Negation",
        formal="¬¬P ≡ P",
        description=(
            "Double Negation states that negating a negation returns "
            "the original proposition."
        ),
        example=(
            "'It is not the case that it is not raining' is equivalent to "
            "'It is raining.'"
        ),
        complexity=1,
    ),
    LogicalRule(
        id="R09",
        name="Transitivity",
        formal="A > B, B > C ⊢ A > C",
        description=(
            "Transitivity states that if A is related to B, and B is related "
            "to C by the same ordering relation, then A is related to C."
        ),
        example=(
            "Alice is taller than Bob. Bob is taller than Carol. "
            "Therefore, Alice is taller than Carol."
        ),
        complexity=2,
    ),
    LogicalRule(
        id="R10",
        name="Proof by Contradiction",
        formal="Assume ¬P, derive ⊥, therefore P",
        description=(
            "Proof by Contradiction (Reductio ad Absurdum) assumes the negation "
            "of the desired conclusion, then derives a logical contradiction, "
            "thereby proving the original statement."
        ),
        example=(
            "To prove √2 is irrational: assume it is rational (p/q in lowest terms), "
            "derive that both p and q must be even—contradicting 'lowest terms.' "
            "Therefore √2 is irrational."
        ),
        complexity=4,
    ),
    LogicalRule(
        id="R11",
        name="Universal Instantiation",
        formal="∀x P(x) ⊢ P(a)",
        description=(
            "Universal Instantiation states that if a property holds for "
            "all members of a domain, then it holds for any specific member."
        ),
        example=(
            "All mammals are warm-blooded. A dog is a mammal. "
            "Therefore, a dog is warm-blooded."
        ),
        complexity=2,
    ),
    LogicalRule(
        id="R12",
        name="Biconditional Elimination",
        formal="P ↔ Q ⊢ (P → Q) ∧ (Q → P)",
        description=(
            "Biconditional Elimination states that 'P if and only if Q' "
            "is equivalent to 'P implies Q AND Q implies P.'"
        ),
        example=(
            "'A triangle is equilateral if and only if all its sides are equal' "
            "means: if equilateral then equal sides, AND if equal sides then equilateral."
        ),
        complexity=3,
    ),
    LogicalRule(
        id="R13",
        name="Constructive Dilemma",
        formal="(P → Q) ∧ (R → S), P ∨ R ⊢ Q ∨ S",
        description=(
            "Constructive Dilemma states that if P implies Q and R implies S, "
            "and either P or R is true, then either Q or S is true."
        ),
        example=(
            "If I study, I pass. If I work, I earn money. "
            "I will either study or work. "
            "Therefore, I will either pass or earn money."
        ),
        complexity=4,
    ),
    LogicalRule(
        id="R14",
        name="Absorption",
        formal="P → Q ⊢ P → (P ∧ Q)",
        description=(
            "Absorption states that if P implies Q, then P implies both P and Q."
        ),
        example=(
            "If it rains then the ground is wet. Therefore, "
            "if it rains then it rains AND the ground is wet."
        ),
        complexity=3,
    ),
    LogicalRule(
        id="R15",
        name="Material Implication",
        formal="P → Q ≡ ¬P ∨ Q",
        description=(
            "Material Implication states that 'if P then Q' is logically "
            "equivalent to 'not P or Q.'"
        ),
        example=(
            "'If it is a cat, then it is an animal' is equivalent to "
            "'It is not a cat, or it is an animal.'"
        ),
        complexity=4,
    ),
]

RULES_BY_ID: dict[str, LogicalRule] = {r.id: r for r in RULES}
