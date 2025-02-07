"""
300-problem bank for the D-P Gap experiment.

20 problems per rule × 15 rules = 300 problems.
Each problem requires exactly one target rule and has unambiguous ground truth.
Problems use varied entity names and domains to prevent memorization effects.

Usage:
    python -m src.problems --output data/problems.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import Problem, ProblemBank

# ── Helpers ──────────────────────────────────────────────────────────────────

_NAMES = [
    ("Alice", "Bob", "Carol", "Dave", "Eve"),
    ("Kai", "Mia", "Leo", "Zoe", "Ava"),
    ("Sam", "Jordan", "Riley", "Quinn", "Piper"),
    ("Xavier", "Yara", "Zane", "Wren", "Uma"),
]


def _n(batch: int, idx: int) -> str:
    return _NAMES[batch % len(_NAMES)][idx % 5]


# ── Problem definitions ─────────────────────────────────────────────────────
# Each list has 20 (text, ground_truth) tuples.

def _r01_modus_ponens() -> list[tuple[str, str]]:
    return [
        ("If it is raining, then the streets are wet. It is raining. What can you conclude?",
         "The streets are wet."),
        ("If a student studies hard, they will pass the exam. Alice studied hard. What follows?",
         "Alice will pass the exam."),
        ("If the temperature drops below 0°C, water freezes. The temperature dropped to -5°C. What can you conclude?",
         "Water freezes."),
        ("If you press the button, the light turns on. You pressed the button. What happens?",
         "The light turns on."),
        ("If it is a weekday, the office is open. Today is Wednesday. What follows?",
         "The office is open."),
        ("If the alarm sounds, employees must evacuate. The alarm is sounding. What must happen?",
         "Employees must evacuate."),
        ("If a number is divisible by 4, it is divisible by 2. The number 12 is divisible by 4. What can you conclude?",
         "12 is divisible by 2."),
        ("If the cake is in the oven for 30 minutes, it is done. The cake has been in the oven for 30 minutes. What follows?",
         "The cake is done."),
        ("If Sam gets an A on every test, Sam makes the honor roll. Sam got an A on every test. What can you conclude?",
         "Sam makes the honor roll."),
        ("If the battery is charged, the phone works. The battery is charged. What follows?",
         "The phone works."),
        ("If a plant receives sunlight, it grows. This plant receives sunlight. What can you conclude?",
         "The plant grows."),
        ("If it is Sunday, the library is closed. It is Sunday. What follows?",
         "The library is closed."),
        ("If a figure has three sides, it is a triangle. This figure has three sides. What can you conclude?",
         "It is a triangle."),
        ("If the dog barks, the neighbors complain. The dog is barking. What follows?",
         "The neighbors complain."),
        ("If Jordan finishes the report, the boss is satisfied. Jordan finished the report. What can you conclude?",
         "The boss is satisfied."),
        ("If traffic is heavy, commuters are late. Traffic is heavy today. What follows?",
         "Commuters are late."),
        ("If the code compiles, the tests can run. The code compiled successfully. What can you conclude?",
         "The tests can run."),
        ("If the river floods, the road closes. The river has flooded. What follows?",
         "The road closes."),
        ("If an element is a noble gas, it is chemically inert. Neon is a noble gas. What can you conclude?",
         "Neon is chemically inert."),
        ("If the meeting starts at 9, participants must arrive by 8:45. The meeting starts at 9. What follows?",
         "Participants must arrive by 8:45."),
    ]


def _r02_modus_tollens() -> list[tuple[str, str]]:
    return [
        ("If it is raining, then the ground is wet. The ground is not wet. What can you conclude?",
         "It is not raining."),
        ("If Alice is home, the lights are on. The lights are not on. What follows?",
         "Alice is not home."),
        ("If the package was delivered, there is a notification. There is no notification. What can you conclude?",
         "The package was not delivered."),
        ("If the engine is running, there is noise. There is no noise. What follows?",
         "The engine is not running."),
        ("If Bob passed the exam, he is celebrating. Bob is not celebrating. What can you conclude?",
         "Bob did not pass the exam."),
        ("If a number is prime and greater than 2, it is odd. The number is not odd. What follows about a number greater than 2?",
         "The number is not prime."),
        ("If the store is open, the sign says 'Open'. The sign does not say 'Open'. What can you conclude?",
         "The store is not open."),
        ("If the plant is watered, it does not wilt. The plant is wilting. What follows?",
         "The plant was not watered."),
        ("If Sam took the bus, Sam arrived by 9 AM. Sam did not arrive by 9 AM. What can you conclude?",
         "Sam did not take the bus."),
        ("If the file was saved, there is a backup. There is no backup. What follows?",
         "The file was not saved."),
        ("If it snowed, schools are closed. Schools are not closed. What can you conclude?",
         "It did not snow."),
        ("If the bird is a penguin, it cannot fly. This bird can fly. What follows?",
         "The bird is not a penguin."),
        ("If Quinn studied French, Quinn can read the menu. Quinn cannot read the menu. What can you conclude?",
         "Quinn did not study French."),
        ("If the software is updated, the bug is fixed. The bug is not fixed. What follows?",
         "The software is not updated."),
        ("If the concert sold out, no tickets are available. Tickets are available. What can you conclude?",
         "The concert did not sell out."),
        ("If the patient took the medicine, the fever subsided. The fever did not subside. What follows?",
         "The patient did not take the medicine."),
        ("If electricity is flowing, the circuit is closed. The circuit is not closed. What can you conclude?",
         "Electricity is not flowing."),
        ("If the volcano erupted, ash covers the town. Ash does not cover the town. What follows?",
         "The volcano did not erupt."),
        ("If Kai ran the marathon, Kai is tired. Kai is not tired. What can you conclude?",
         "Kai did not run the marathon."),
        ("If the door is locked, we cannot enter. We can enter. What follows?",
         "The door is not locked."),
    ]


def _r03_hypothetical_syllogism() -> list[tuple[str, str]]:
    return [
        ("If it rains, the ground gets wet. If the ground gets wet, the flowers bloom. What can you conclude if it rains?",
         "The flowers bloom."),
        ("If Alice studies, she passes. If she passes, she graduates. What follows if Alice studies?",
         "Alice graduates."),
        ("If the alarm rings, people wake up. If people wake up, they eat breakfast. What can you conclude if the alarm rings?",
         "People eat breakfast."),
        ("If the economy grows, jobs increase. If jobs increase, unemployment falls. What follows if the economy grows?",
         "Unemployment falls."),
        ("If it is cold, the lake freezes. If the lake freezes, people go skating. What can you conclude if it is cold?",
         "People go skating."),
        ("If Bob exercises, he gets fit. If he gets fit, he runs faster. What follows if Bob exercises?",
         "Bob runs faster."),
        ("If the code passes review, it is merged. If it is merged, it goes to production. What can you conclude if the code passes review?",
         "It goes to production."),
        ("If the sun sets, it gets dark. If it gets dark, the streetlights turn on. What follows if the sun sets?",
         "The streetlights turn on."),
        ("If demand rises, prices rise. If prices rise, consumers complain. What can you conclude if demand rises?",
         "Consumers complain."),
        ("If Sam eats sugar, Sam gets energy. If Sam gets energy, Sam stays awake. What follows if Sam eats sugar?",
         "Sam stays awake."),
        ("If you plant seeds, they sprout. If they sprout, you have a garden. What can you conclude if you plant seeds?",
         "You have a garden."),
        ("If the team wins, they qualify. If they qualify, they go to nationals. What follows if the team wins?",
         "They go to nationals."),
        ("If Mia reads a lot, Mia gains knowledge. If Mia gains knowledge, Mia gets promoted. What can you conclude if Mia reads a lot?",
         "Mia gets promoted."),
        ("If traffic increases, pollution increases. If pollution increases, health problems rise. What follows if traffic increases?",
         "Health problems rise."),
        ("If the password is correct, access is granted. If access is granted, data is visible. What can you conclude if the password is correct?",
         "Data is visible."),
        ("If a star collapses, it forms a black hole. If a black hole forms, light cannot escape. What follows if a star collapses?",
         "Light cannot escape."),
        ("If it is spring, flowers bloom. If flowers bloom, bees appear. What can you conclude if it is spring?",
         "Bees appear."),
        ("If Leo practices piano, Leo improves. If Leo improves, Leo performs at the recital. What follows if Leo practices piano?",
         "Leo performs at the recital."),
        ("If the paper is accepted, it is published. If it is published, it gets citations. What can you conclude if the paper is accepted?",
         "It gets citations."),
        ("If you heat ice, it melts. If it melts, you get water. What follows if you heat ice?",
         "You get water."),
    ]


def _r04_disjunctive_syllogism() -> list[tuple[str, str]]:
    return [
        ("Either it is sunny or it is cloudy. It is not sunny. What can you conclude?",
         "It is cloudy."),
        ("Either Alice or Bob broke the vase. Alice did not break the vase. What follows?",
         "Bob broke the vase."),
        ("The answer is either 42 or 57. The answer is not 57. What can you conclude?",
         "The answer is 42."),
        ("Either the train or the bus goes to the airport. The train does not go to the airport. What follows?",
         "The bus goes to the airport."),
        ("Sam is in either New York or London. Sam is not in New York. What can you conclude?",
         "Sam is in London."),
        ("Either the server crashed or the network is down. The server did not crash. What follows?",
         "The network is down."),
        ("Either math or science is scheduled for Monday. Math is not scheduled for Monday. What can you conclude?",
         "Science is scheduled for Monday."),
        ("Either the lock is jammed or the key is wrong. The lock is not jammed. What follows?",
         "The key is wrong."),
        ("Either Riley drives or takes the subway. Riley does not drive. What can you conclude?",
         "Riley takes the subway."),
        ("Either the test passed or there is a bug. The test passed. What can you conclude about whether there is a bug?",
         "We cannot conclude anything additional from this alone."),
        ("Either the movie starts at 7 or at 9. It does not start at 7. What follows?",
         "The movie starts at 9."),
        ("Either we go hiking or swimming. We do not go hiking. What can you conclude?",
         "We go swimming."),
        ("Either Zoe or Kai will present first. Zoe will not present first. What follows?",
         "Kai will present first."),
        ("Either the cat is inside or outside. The cat is not inside. What can you conclude?",
         "The cat is outside."),
        ("Either Python or Java was used. Python was not used. What follows?",
         "Java was used."),
        ("Either the hypothesis is correct or the experiment was flawed. The hypothesis is not correct. What can you conclude?",
         "The experiment was flawed."),
        ("Either the flight is on time or delayed. The flight is not on time. What follows?",
         "The flight is delayed."),
        ("Either the painting is original or a forgery. It is not original. What can you conclude?",
         "The painting is a forgery."),
        ("Either renewable or fossil fuel powers this city. Fossil fuel does not power it. What follows?",
         "Renewable energy powers this city."),
        ("Either Quinn or Piper won the prize. Quinn did not win. What can you conclude?",
         "Piper won the prize."),
    ]


def _r05_contrapositive() -> list[tuple[str, str]]:
    return [
        ("'If it is a dog, it is an animal.' What is the contrapositive of this statement?",
         "If it is not an animal, then it is not a dog."),
        ("'If it rains, the picnic is cancelled.' What is the contrapositive?",
         "If the picnic is not cancelled, then it is not raining."),
        ("'If you are a citizen, you can vote.' State the contrapositive.",
         "If you cannot vote, then you are not a citizen."),
        ("'If the shape is a square, it has four equal sides.' What is the contrapositive?",
         "If it does not have four equal sides, then it is not a square."),
        ("'If the battery is dead, the car won't start.' State the contrapositive.",
         "If the car starts, then the battery is not dead."),
        ("'If Alice passed, she studied.' What is the contrapositive?",
         "If Alice did not study, then she did not pass."),
        ("'If a number is even, it is divisible by 2.' What is the contrapositive?",
         "If a number is not divisible by 2, then it is not even."),
        ("'If the light is green, you may proceed.' State the contrapositive.",
         "If you may not proceed, then the light is not green."),
        ("'If there is smoke, there is fire.' What is the contrapositive?",
         "If there is no fire, then there is no smoke."),
        ("'If it is winter, it is cold.' State the contrapositive.",
         "If it is not cold, then it is not winter."),
        ("'If you eat too much sugar, you gain weight.' What is the contrapositive?",
         "If you do not gain weight, then you did not eat too much sugar."),
        ("'If the homework is done, the student may play.' State the contrapositive.",
         "If the student may not play, then the homework is not done."),
        ("'If X > 10, then X > 5.' What is the contrapositive?",
         "If X is not greater than 5, then X is not greater than 10."),
        ("'If Leo is a doctor, Leo has a medical degree.' State the contrapositive.",
         "If Leo does not have a medical degree, then Leo is not a doctor."),
        ("'If it is a mammal, it is warm-blooded.' What is the contrapositive?",
         "If it is not warm-blooded, then it is not a mammal."),
        ("'If the door is open, anyone can enter.' State the contrapositive.",
         "If no one can enter, then the door is not open."),
        ("'If she is running, her heart rate is elevated.' What is the contrapositive?",
         "If her heart rate is not elevated, then she is not running."),
        ("'If the program is correct, it produces no errors.' State the contrapositive.",
         "If the program produces errors, then it is not correct."),
        ("'If you are in Paris, you are in France.' What is the contrapositive?",
         "If you are not in France, then you are not in Paris."),
        ("'If Kai passes all courses, Kai graduates.' State the contrapositive.",
         "If Kai does not graduate, then Kai did not pass all courses."),
    ]


def _r06_demorgan_1() -> list[tuple[str, str]]:
    return [
        ("It is NOT the case that both Alice and Bob passed. What is an equivalent statement?",
         "Alice did not pass, or Bob did not pass (or both)."),
        ("It is false that the car is fast AND fuel-efficient. Restate using De Morgan's Law.",
         "The car is not fast, or it is not fuel-efficient (or both)."),
        ("It is not true that both the printer and scanner work. What follows by De Morgan's Law?",
         "The printer does not work, or the scanner does not work (or both)."),
        ("'Not (P and Q)' is equivalent to what?",
         "Not P, or not Q."),
        ("It is not the case that Sam is tall and strong. What can you conclude?",
         "Sam is not tall, or Sam is not strong (or both)."),
        ("The statement 'it is false that both conditions A and B hold' is equivalent to what?",
         "Condition A does not hold, or condition B does not hold (or both)."),
        ("Not (the sky is blue AND the grass is green). Rewrite this.",
         "The sky is not blue, or the grass is not green (or both)."),
        ("It is not the case that the test is easy and short. What follows?",
         "The test is not easy, or the test is not short (or both)."),
        ("'Not (raining and cold)' — rewrite using De Morgan's Law.",
         "It is not raining, or it is not cold (or both)."),
        ("It is false that both X and Y are positive. What can you conclude?",
         "X is not positive, or Y is not positive (or both)."),
        ("Not (the restaurant is cheap AND good). What does this mean?",
         "The restaurant is not cheap, or not good (or both)."),
        ("It is not the case that Mia is a singer and a dancer. What follows?",
         "Mia is not a singer, or Mia is not a dancer (or both)."),
        ("Not (the software is fast AND reliable). Restate.",
         "The software is not fast, or not reliable (or both)."),
        ("It is false that both Leo and Zoe were invited. What can you conclude?",
         "Leo was not invited, or Zoe was not invited (or both)."),
        ("Not (it is Monday AND sunny). Rewrite.",
         "It is not Monday, or it is not sunny (or both)."),
        ("It is not the case that the answer is correct and complete. What follows?",
         "The answer is not correct, or not complete (or both)."),
        ("Not (the room is clean AND quiet). What does this mean?",
         "The room is not clean, or not quiet (or both)."),
        ("It is false that both flights are on time. What can you conclude?",
         "The first flight is not on time, or the second is not on time (or both)."),
        ("Not (A ∧ B) where A='the cat is black' and B='the cat is large'. Restate.",
         "The cat is not black, or the cat is not large (or both)."),
        ("It is not the case that Quinn passed math and science. What follows?",
         "Quinn did not pass math, or Quinn did not pass science (or both)."),
    ]


def _r07_demorgan_2() -> list[tuple[str, str]]:
    return [
        ("It is NOT the case that Alice or Bob passed. What can you conclude?",
         "Alice did not pass AND Bob did not pass."),
        ("It is false that either the bus or train is running. What follows?",
         "The bus is not running AND the train is not running."),
        ("Not (it is raining or snowing). What can you conclude?",
         "It is not raining AND it is not snowing."),
        ("'Not (P or Q)' is equivalent to what?",
         "Not P and not Q."),
        ("It is not the case that Sam speaks French or German. What follows?",
         "Sam does not speak French AND Sam does not speak German."),
        ("It is false that either condition X or condition Y holds. Restate.",
         "Condition X does not hold AND condition Y does not hold."),
        ("Not (the store is open or the website is up). What can you conclude?",
         "The store is not open AND the website is not up."),
        ("It is not true that either the left or right path leads home. What follows?",
         "The left path does not lead home AND the right path does not lead home."),
        ("Not (Mia or Leo attended the party). What can you conclude?",
         "Mia did not attend AND Leo did not attend."),
        ("It is false that it is hot or humid. Restate.",
         "It is not hot AND it is not humid."),
        ("Not (the email was sent or the call was made). What follows?",
         "The email was not sent AND the call was not made."),
        ("It is not the case that Riley or Jordan volunteered. What can you conclude?",
         "Riley did not volunteer AND Jordan did not volunteer."),
        ("Not (A ∨ B) where A='it is morning' and B='it is afternoon'. What follows?",
         "It is not morning AND it is not afternoon."),
        ("It is false that either team scored. Restate.",
         "Neither team scored; the first team did not score AND the second team did not score."),
        ("Not (the window is open or the fan is on). What can you conclude?",
         "The window is not open AND the fan is not on."),
        ("It is not the case that Kai or Ava was promoted. What follows?",
         "Kai was not promoted AND Ava was not promoted."),
        ("Not (the paper was published or submitted). Restate.",
         "The paper was not published AND the paper was not submitted."),
        ("It is false that either candidate won a majority. What can you conclude?",
         "The first candidate did not win a majority AND the second candidate did not win a majority."),
        ("Not (the experiment succeeded or was repeated). What follows?",
         "The experiment did not succeed AND was not repeated."),
        ("It is not the case that Quinn likes coffee or tea. What can you conclude?",
         "Quinn does not like coffee AND Quinn does not like tea."),
    ]


def _r08_double_negation() -> list[tuple[str, str]]:
    return [
        ("It is not the case that it is not raining. What can you conclude?",
         "It is raining."),
        ("It is false that Alice is not happy. What follows?",
         "Alice is happy."),
        ("It is not true that the door is not locked. What can you conclude?",
         "The door is locked."),
        ("The claim 'it is not the case that the answer is not 42' simplifies to what?",
         "The answer is 42."),
        ("It is not the case that Sam did not attend. What follows?",
         "Sam attended."),
        ("'Not not P' is equivalent to what?",
         "P."),
        ("It is false that Bob is not guilty. What can you conclude?",
         "Bob is guilty."),
        ("It is not true that it is not cold outside. What follows?",
         "It is cold outside."),
        ("The statement 'not (not sunny)' simplifies to what?",
         "It is sunny."),
        ("It is not the case that the light is not on. What can you conclude?",
         "The light is on."),
        ("It is false that Mia does not like chocolate. What follows?",
         "Mia likes chocolate."),
        ("'It is not the case that it is not Monday' simplifies to what?",
         "It is Monday."),
        ("It is not true that the project is not complete. What can you conclude?",
         "The project is complete."),
        ("Not (not (X > 5)). What does this simplify to?",
         "X > 5."),
        ("It is false that Leo is not a student. What follows?",
         "Leo is a student."),
        ("It is not the case that the statement is not true. What can you conclude?",
         "The statement is true."),
        ("'It is not the case that it is not the case that P' equals what?",
         "P."),
        ("It is not true that the window is not broken. What follows?",
         "The window is broken."),
        ("It is false that Quinn did not win. What can you conclude?",
         "Quinn won."),
        ("Not (not (the file exists)). What does this simplify to?",
         "The file exists."),
    ]


def _r09_transitivity() -> list[tuple[str, str]]:
    return [
        ("Alice is taller than Bob. Bob is taller than Carol. Who is taller, Alice or Carol?",
         "Alice is taller than Carol."),
        ("X > Y and Y > Z. What is the relationship between X and Z?",
         "X > Z."),
        ("The elephant is heavier than the horse. The horse is heavier than the dog. Compare the elephant and the dog.",
         "The elephant is heavier than the dog."),
        ("Team A beat Team B. Team B beat Team C. If these results are transitive, what follows?",
         "Team A beat Team C."),
        ("Red is darker than blue. Blue is darker than yellow. Compare red and yellow.",
         "Red is darker than yellow."),
        ("Sam is older than Jordan. Jordan is older than Riley. Who is oldest?",
         "Sam is oldest."),
        ("Building A is taller than Building B. Building B is taller than Building C. Which is tallest?",
         "Building A is tallest."),
        ("Math is harder than English. English is harder than Art. Compare Math and Art.",
         "Math is harder than Art."),
        ("The oak tree is older than the maple. The maple is older than the birch. Compare the oak and birch.",
         "The oak tree is older than the birch."),
        ("If A > B and B > C, and C > D, what is the relationship between A and D?",
         "A > D."),
        ("Paris is farther from Tokyo than London is. London is farther from Tokyo than Berlin is. Compare Paris and Berlin in distance from Tokyo.",
         "Paris is farther from Tokyo than Berlin."),
        ("Kai is faster than Mia. Mia is faster than Leo. Who is fastest?",
         "Kai is fastest."),
        ("Gold is denser than silver. Silver is denser than aluminum. Compare gold and aluminum.",
         "Gold is denser than aluminum."),
        ("Task A takes longer than Task B. Task B takes longer than Task C. Which task takes longest?",
         "Task A takes longest."),
        ("Novel X has more pages than Novel Y. Novel Y has more pages than Novel Z. Compare X and Z.",
         "Novel X has more pages than Novel Z."),
        ("The CEO ranks above the VP. The VP ranks above the manager. Compare the CEO and the manager.",
         "The CEO ranks above the manager."),
        ("River A is longer than River B. River B is longer than River C. Which river is longest?",
         "River A is longest."),
        ("Diamond is harder than quartz. Quartz is harder than talc. Compare diamond and talc.",
         "Diamond is harder than talc."),
        ("Alice scored higher than Bob. Bob scored higher than Carol. Who scored highest?",
         "Alice scored highest."),
        ("If speed(A) > speed(B) and speed(B) > speed(C), what can you say about speed(A) vs speed(C)?",
         "speed(A) > speed(C)."),
    ]


def _r10_proof_by_contradiction() -> list[tuple[str, str]]:
    return [
        ("Assume there is a largest prime number N. Then consider N! + 1. It is not divisible by any number ≤ N, contradicting that N is the largest prime. What can you conclude?",
         "There is no largest prime number; there are infinitely many primes."),
        ("Assume √2 is rational, i.e., √2 = p/q in lowest terms. Then 2q² = p², so p is even. Then p = 2k, giving 2q² = 4k², so q is even. But p and q cannot both be even if p/q is in lowest terms. What follows?",
         "√2 is irrational."),
        ("Assume that the sum of two odd numbers is odd. Let them be 2a+1 and 2b+1. Their sum is 2(a+b+1), which is even — a contradiction. What can you conclude?",
         "The sum of two odd numbers is even."),
        ("Assume a triangle has two right angles. Then the sum of angles exceeds 180°, which contradicts the triangle angle sum theorem. What follows?",
         "A triangle cannot have two right angles."),
        ("Assume there exists an integer that is both even and odd. Then it is divisible by 2 and leaves remainder 1 when divided by 2 — a contradiction. What can you conclude?",
         "No integer is both even and odd."),
        ("Assume the empty set is not a subset of every set. Then there exists an element in the empty set not in some set S. But the empty set has no elements — contradiction. What follows?",
         "The empty set is a subset of every set."),
        ("Assume that log₂(3) is rational, equal to a/b. Then 2^(a/b) = 3, so 2^a = 3^b. But a power of 2 cannot equal a power of 3 (unique prime factorization). What can you conclude?",
         "log₂(3) is irrational."),
        ("Assume statement S and its negation ¬S are both true. This is a direct contradiction. What follows in classical logic?",
         "The assumption is false; S and ¬S cannot both be true."),
        ("Assume a chess board missing two diagonally opposite corners can be tiled by dominoes. Each domino covers one black and one white square. The removed squares are the same color, leaving unequal counts — contradiction. What follows?",
         "The board cannot be tiled by dominoes."),
        ("Assume that among any 3 people, it is possible that none of them know each other and none are mutual strangers. By the Pigeonhole Principle applied to 2 relationship types, at least 2 of the 3 must share a type — contradiction. What can you conclude?",
         "Among any 3 people, either at least 2 know each other or at least 2 are mutual strangers."),
        ("Assume line L is both parallel and not parallel to line M. This is a contradiction. What follows?",
         "The assumption is false; a line cannot be both parallel and not parallel to another line."),
        ("Assume 0.999... ≠ 1. Let d = 1 - 0.999... > 0. But no positive number d can be found between them (since 10d = 10 - 9.999... = d). Contradiction. What can you conclude?",
         "0.999... = 1."),
        ("Assume a function is continuous on [a,b], f(a) < 0 < f(b), but f has no root in (a,b). By the Intermediate Value Theorem, f must cross zero — contradiction. What follows?",
         "The function has at least one root in (a,b)."),
        ("Assume an even number greater than 2 is prime. Then it is divisible by 2 and thus not prime — contradiction. What can you conclude?",
         "No even number greater than 2 is prime."),
        ("Assume there is a set of all sets. It would contain itself. Consider the subset of sets that don't contain themselves — this leads to Russell's Paradox. What follows?",
         "There is no set of all sets."),
        ("Assume two distinct lines in a plane intersect at two different points. Two points determine a unique line — contradiction. What can you conclude?",
         "Two distinct lines can intersect at most at one point."),
        ("Assume a non-zero number x satisfies x = -x. Then 2x = 0, so x = 0, contradicting x ≠ 0. What follows?",
         "No non-zero number equals its own negation."),
        ("Assume the set of real numbers between 0 and 1 is countable. Cantor's diagonal argument constructs a real number not in the list — contradiction. What can you conclude?",
         "The set of real numbers between 0 and 1 is uncountable."),
        ("Assume n² is even but n is odd. Then n = 2k+1 and n² = 4k²+4k+1, which is odd — contradicting n² being even. What follows?",
         "If n² is even, then n is even."),
        ("Assume a finite group has no identity element. Group axioms require an identity — contradiction. What can you conclude?",
         "Every finite group has an identity element."),
    ]


def _r11_universal_instantiation() -> list[tuple[str, str]]:
    return [
        ("All mammals are warm-blooded. A dog is a mammal. What can you conclude about the dog?",
         "The dog is warm-blooded."),
        ("All students must submit homework. Alice is a student. What follows?",
         "Alice must submit homework."),
        ("Every prime number greater than 2 is odd. 7 is prime and greater than 2. What can you conclude?",
         "7 is odd."),
        ("All birds have feathers. A robin is a bird. What follows?",
         "A robin has feathers."),
        ("Every employee must attend the meeting. Jordan is an employee. What can you conclude?",
         "Jordan must attend the meeting."),
        ("All even numbers are divisible by 2. 14 is even. What follows?",
         "14 is divisible by 2."),
        ("All planets orbit a star. Earth is a planet. What can you conclude?",
         "Earth orbits a star."),
        ("Every citizen has the right to vote. Sam is a citizen. What follows?",
         "Sam has the right to vote."),
        ("All metals conduct electricity. Copper is a metal. What can you conclude?",
         "Copper conducts electricity."),
        ("Every triangle has angles summing to 180°. Figure F is a triangle. What follows?",
         "Figure F has angles summing to 180°."),
        ("All roses are flowers. This rose is a rose. What can you conclude?",
         "This rose is a flower."),
        ("Every file in the folder is encrypted. report.pdf is in the folder. What follows?",
         "report.pdf is encrypted."),
        ("All members must pay dues. Kai is a member. What can you conclude?",
         "Kai must pay dues."),
        ("Every natural number is an integer. 5 is a natural number. What follows?",
         "5 is an integer."),
        ("All squares are rectangles. Figure S is a square. What can you conclude?",
         "Figure S is a rectangle."),
        ("Every participant receives a certificate. Mia is a participant. What follows?",
         "Mia receives a certificate."),
        ("All fruits contain seeds. An apple is a fruit. What can you conclude?",
         "An apple contains seeds."),
        ("Every element in the list is positive. 7 is in the list. What follows?",
         "7 is positive."),
        ("All novels in this series have more than 200 pages. Book 3 is in this series. What can you conclude?",
         "Book 3 has more than 200 pages."),
        ("Every function in this module is tested. parse() is in this module. What follows?",
         "parse() is tested."),
    ]


def _r12_biconditional() -> list[tuple[str, str]]:
    return [
        ("'A triangle is equilateral if and only if all three sides are equal.' Given the triangle is equilateral, what follows?",
         "All three sides are equal."),
        ("'P if and only if Q.' P is true. What can you conclude about Q?",
         "Q is true."),
        ("'You pass if and only if you score above 60.' You scored 75. What follows?",
         "You pass."),
        ("'The door opens if and only if the key is correct.' The door opened. What can you conclude?",
         "The key is correct."),
        ("'A number is even if and only if it is divisible by 2.' The number is not divisible by 2. What follows?",
         "The number is not even."),
        ("'It is Tuesday if and only if the store has a sale.' It is not Tuesday. What can you conclude?",
         "The store does not have a sale."),
        ("'X = Y if and only if Y = X.' X equals Y. What follows?",
         "Y equals X."),
        ("'The alarm rings if and only if there is an intruder.' There is no intruder. What can you conclude?",
         "The alarm does not ring."),
        ("'A figure is a square if and only if it is a rectangle with equal sides.' The figure is a rectangle with equal sides. What follows?",
         "The figure is a square."),
        ("'It rains if and only if clouds are present.' It is not raining. What can you conclude?",
         "Clouds are not present."),
        ("'Access is granted if and only if the password is correct.' The password is correct. What follows?",
         "Access is granted."),
        ("'P ↔ Q' — what two implications does this give us?",
         "P implies Q, and Q implies P."),
        ("'Alice attends if and only if Bob attends.' Alice is attending. What can you conclude?",
         "Bob is attending."),
        ("'The circuit is complete if and only if current flows.' Current is not flowing. What follows?",
         "The circuit is not complete."),
        ("'Leo is eligible if and only if Leo is 18 or older.' Leo is 17. What can you conclude?",
         "Leo is not eligible."),
        ("'It is daytime if and only if the sun is up.' The sun is up. What follows?",
         "It is daytime."),
        ("'The function returns true if and only if the input is valid.' The function returned false. What can you conclude?",
         "The input is not valid."),
        ("'P ↔ Q' and Q is false. What follows about P?",
         "P is false."),
        ("'A reaction occurs if and only if the catalyst is present.' No reaction occurred. What can you conclude?",
         "The catalyst is not present."),
        ("'The class runs if and only if at least 5 students enroll.' Exactly 5 students enrolled. What follows?",
         "The class runs."),
    ]


def _r13_constructive_dilemma() -> list[tuple[str, str]]:
    return [
        ("If I study, I pass. If I work, I earn money. I will either study or work. What can you conclude?",
         "I will either pass or earn money."),
        ("If it rains, we use an umbrella. If it snows, we wear a coat. It will either rain or snow. What follows?",
         "We will either use an umbrella or wear a coat."),
        ("If Alice applies, she gets an interview. If Bob applies, he gets an interview. Either Alice or Bob will apply. What can you conclude?",
         "Either Alice or Bob gets an interview."),
        ("If you take Route A, you arrive by 10. If you take Route B, you arrive by 11. You take either Route A or B. What follows?",
         "You arrive by either 10 or 11."),
        ("If the economy grows, stocks rise. If the economy shrinks, bonds rise. The economy will either grow or shrink. What can you conclude?",
         "Either stocks rise or bonds rise."),
        ("If it is hot, we swim. If it is cold, we ski. It is either hot or cold. What follows?",
         "We either swim or ski."),
        ("If P then Q. If R then S. P or R. What can you conclude?",
         "Q or S."),
        ("If Sam drives, Sam arrives early. If Sam takes the bus, Sam saves money. Sam either drives or takes the bus. What follows?",
         "Sam either arrives early or saves money."),
        ("If the test passes, deploy. If the test fails, debug. The test either passes or fails. What can you conclude?",
         "We either deploy or debug."),
        ("If Mia sings, the audience cheers. If Mia dances, the audience applauds. Mia will either sing or dance. What follows?",
         "The audience either cheers or applauds."),
        ("If X is positive, the sum increases. If X is negative, the sum decreases. X is either positive or negative. What can you conclude?",
         "The sum either increases or decreases."),
        ("If it is a weekday, the office opens. If it is a weekend, the mall opens. Today is either a weekday or weekend. What follows?",
         "Either the office or the mall opens."),
        ("If power is on, the screen lights up. If power is off, the battery charges. Power is either on or off. What can you conclude?",
         "Either the screen lights up or the battery charges."),
        ("If you choose math, you solve equations. If you choose art, you paint. You choose either math or art. What follows?",
         "You either solve equations or paint."),
        ("If the data is valid, the model trains. If the data is invalid, an error is raised. The data is either valid or invalid. What can you conclude?",
         "Either the model trains or an error is raised."),
        ("If Leo studies medicine, Leo becomes a doctor. If Leo studies law, Leo becomes a lawyer. Leo studies either medicine or law. What follows?",
         "Leo becomes either a doctor or a lawyer."),
        ("If the signal is green, the train moves. If the signal is red, the train stops. The signal is either green or red. What can you conclude?",
         "The train either moves or stops."),
        ("If demand is high, prices increase. If supply is high, prices decrease. Either demand or supply is high. What follows?",
         "Prices either increase or decrease."),
        ("If the wind blows, the windmill turns. If the sun shines, the solar panel generates power. Either the wind blows or the sun shines. What can you conclude?",
         "Either the windmill turns or the solar panel generates power."),
        ("If you go left, you find the lake. If you go right, you find the mountain. You go either left or right. What follows?",
         "You find either the lake or the mountain."),
    ]


def _r14_absorption() -> list[tuple[str, str]]:
    return [
        ("If it rains, then the ground is wet. By absorption, what can you conclude?",
         "If it rains, then it rains AND the ground is wet."),
        ("If P implies Q, what does absorption give us?",
         "P implies (P and Q)."),
        ("If Alice studies, she passes. What does absorption tell us?",
         "If Alice studies, then Alice studies AND she passes."),
        ("If the button is pressed, the light turns on. Apply absorption.",
         "If the button is pressed, then the button is pressed AND the light turns on."),
        ("If X > 0, then X is positive. What follows by absorption?",
         "If X > 0, then X > 0 AND X is positive."),
        ("If Sam is running, Sam is exercising. Apply the absorption rule.",
         "If Sam is running, then Sam is running AND Sam is exercising."),
        ("If it is Sunday, the shop is closed. What does absorption give us?",
         "If it is Sunday, then it is Sunday AND the shop is closed."),
        ("If the code compiles, it can be tested. Apply absorption.",
         "If the code compiles, then the code compiles AND it can be tested."),
        ("If the temperature exceeds 100°C, water boils. By absorption?",
         "If the temperature exceeds 100°C, then the temperature exceeds 100°C AND water boils."),
        ("If P → Q, then absorption gives P → ?",
         "P → (P ∧ Q)."),
        ("If Mia is a student, Mia gets a discount. Apply absorption.",
         "If Mia is a student, then Mia is a student AND Mia gets a discount."),
        ("If the ball is thrown, the ball moves. By absorption?",
         "If the ball is thrown, then the ball is thrown AND the ball moves."),
        ("If it is winter, it is cold. Apply absorption.",
         "If it is winter, then it is winter AND it is cold."),
        ("If an animal is a cat, it has whiskers. What does absorption give?",
         "If an animal is a cat, then it is a cat AND it has whiskers."),
        ("If Leo passed, Leo is happy. By absorption?",
         "If Leo passed, then Leo passed AND Leo is happy."),
        ("If power is on, the machine runs. Apply absorption.",
         "If power is on, then power is on AND the machine runs."),
        ("If you study, you learn. What does absorption tell us?",
         "If you study, then you study AND you learn."),
        ("If traffic is light, the commute is short. By absorption?",
         "If traffic is light, then traffic is light AND the commute is short."),
        ("If the sky is clear, stars are visible. Apply absorption.",
         "If the sky is clear, then the sky is clear AND stars are visible."),
        ("If Q follows from P, absorption says P implies what?",
         "P implies both P and Q."),
    ]


def _r15_material_implication() -> list[tuple[str, str]]:
    return [
        ("'If it is a cat, then it is an animal.' Rewrite using material implication (without 'if...then').",
         "It is not a cat, or it is an animal."),
        ("'P → Q' is equivalent to what disjunction?",
         "¬P ∨ Q."),
        ("'If it rains, I carry an umbrella.' Rewrite without 'if...then'.",
         "It does not rain, or I carry an umbrella."),
        ("'If you are a student, you have an ID.' Restate as a disjunction.",
         "You are not a student, or you have an ID."),
        ("'If the light is red, stop.' Rewrite using material implication.",
         "The light is not red, or you stop."),
        ("'If X > 10, then X > 5.' Restate without the conditional.",
         "X is not greater than 10, or X is greater than 5."),
        ("Express 'If Alice wins, she celebrates' without using 'if...then'.",
         "Alice does not win, or she celebrates."),
        ("'If the file exists, it can be opened.' Rewrite as a disjunction.",
         "The file does not exist, or it can be opened."),
        ("'P implies Q' means what in terms of 'or' and 'not'?",
         "Not P or Q."),
        ("'If it is Friday, the report is due.' Restate using material implication.",
         "It is not Friday, or the report is due."),
        ("'If the battery is low, the phone shuts down.' Rewrite without 'if...then'.",
         "The battery is not low, or the phone shuts down."),
        ("'If Bob is late, the meeting is delayed.' Express as a disjunction.",
         "Bob is not late, or the meeting is delayed."),
        ("'If n is even, n² is even.' Restate using material implication.",
         "n is not even, or n² is even."),
        ("'If you break the law, you get a fine.' Rewrite as a disjunction.",
         "You do not break the law, or you get a fine."),
        ("'If the dog barks, the neighbors wake up.' Express without 'if...then'.",
         "The dog does not bark, or the neighbors wake up."),
        ("'If it is summer, it is hot.' Apply material implication.",
         "It is not summer, or it is hot."),
        ("'If the key is turned, the engine starts.' Restate as a disjunction.",
         "The key is not turned, or the engine starts."),
        ("'If Leo runs, Leo sweats.' Rewrite using material implication.",
         "Leo does not run, or Leo sweats."),
        ("'A → B' becomes what in disjunctive form?",
         "¬A ∨ B."),
        ("'If the test passes, the build succeeds.' Rewrite without 'if...then'.",
         "The test does not pass, or the build succeeds."),
    ]


# ── Assemble full bank ──────────────────────────────────────────────────────

_GENERATORS = {
    "R01": _r01_modus_ponens,
    "R02": _r02_modus_tollens,
    "R03": _r03_hypothetical_syllogism,
    "R04": _r04_disjunctive_syllogism,
    "R05": _r05_contrapositive,
    "R06": _r06_demorgan_1,
    "R07": _r07_demorgan_2,
    "R08": _r08_double_negation,
    "R09": _r09_transitivity,
    "R10": _r10_proof_by_contradiction,
    "R11": _r11_universal_instantiation,
    "R12": _r12_biconditional,
    "R13": _r13_constructive_dilemma,
    "R14": _r14_absorption,
    "R15": _r15_material_implication,
}


def build_problem_bank() -> ProblemBank:
    """Build the full 300-problem bank."""
    problems: list[Problem] = []
    for rule_id, gen_fn in _GENERATORS.items():
        pairs = gen_fn()
        for i, (text, gt) in enumerate(pairs):
            problems.append(
                Problem(
                    id=f"{rule_id}_P{i + 1:02d}",
                    rule_id=rule_id,
                    text=text,
                    ground_truth=gt,
                )
            )
    return ProblemBank(problems=problems)


def save_problem_bank(path: Path | None = None) -> ProblemBank:
    """Build and save the problem bank to JSON."""
    path = path or Path(__file__).parent.parent / "data" / "problems.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    bank = build_problem_bank()
    with open(path, "w") as f:
        f.write(bank.model_dump_json(indent=2))
    print(f"Saved {len(bank.problems)} problems to {path}")
    return bank


def load_problem_bank(path: Path | None = None) -> ProblemBank:
    """Load problems from JSON, building if not found."""
    path = path or Path(__file__).parent.parent / "data" / "problems.json"
    if not path.exists():
        return save_problem_bank(path)
    import json as _json

    with open(path) as f:
        return ProblemBank.model_validate(_json.load(f))


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate D-P Gap problem bank")
    parser.add_argument("--output", type=str, default="data/problems.json")
    args = parser.parse_args()
    save_problem_bank(Path(args.output))
