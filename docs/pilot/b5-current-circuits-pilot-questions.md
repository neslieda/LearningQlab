# Pilot question set: B.5 Current and circuits

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node B.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; no PDF was opened.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. The resistivity of nichrome, 1.1 × 10⁻⁶ Ω m, was used and is given in the question.
> **Not verified:** passed an independent blind solver; has not passed expert review; qualitative points (Question 5c, the reasoning in 5d) cannot be checked by
> code; the resistivity of nichrome and the resistance values of the LDR were taken from general knowledge and not confirmed against a source; in Question 5 the resistance of the
> wire was assumed not to change with temperature (stated in the question) — for a real heating wire this holds only approximately; the circuit
> diagrams were not drawn, only described in words; no expert check was made for resemblance to a known exam question.

## Scope table

| # | Section | Level | Outcome (B.5) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Resistivity; dependence of resistance on length and cross-sectional area (proportion) | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Internal resistance; power dissipated in the external resistor | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Potential divider with a variable resistor (LDR) | AO3 | — | 1 | Medium |
| 4 | Paper 1A | SL | Series and parallel connection; sharing of current in parallel branches | AO2 | — | 1 | Medium |
| 5 | Paper 2 | SL | Resistivity; emf, internal resistance and terminal pd; power; evaluating the effect of connecting in parallel | AO2–AO3 | Show that, Calculate, Explain, Determine | 9 | Medium–hard |

This set does not cover all of B.5. Not covered: comparison of a chemical cell and a solar cell as sources of emf; drawing circuit diagrams
and their symbols; definition of current as the rate of flow of charge (I = Δq/Δt); Ohm's law and non-ohmic behaviour (I–V characteristic);
thermistor and potentiometer; circuits containing non-ideal meters; determining emf and internal resistance from a graph.

Scope boundary check: direct current circuits only; all meters are ideal and this is stated in the question (Question 3); the only variable
resistor used is the LDR (on the permitted list). No derivatives or integrals.

---

## Question 1 — Paper 1A

A metal wire X has resistance *R*. Wire Y is made of the same metal and is at the same temperature as X. Y has **twice** the length
and **twice** the diameter of X.

What is the resistance of Y?

A. *R* ⁄ 2
B. *R*
C. 2*R*
D. 4*R*

**Answer: A**

**Solution.** *R* = ρ*L*/*A* and *A* ∝ *d*². The length is doubled and the cross-sectional area is quadrupled: the resistance falls to 2 / 4 = 1⁄2 of its value.

| Option | Misconception |
|---|---|
| B | Cross-sectional area is taken as directly proportional to the diameter (*A* ∝ *d*): 2 / 2 = 1 |
| C | The effect of the diameter is ignored; only the length is taken into account: 2*R* |
| D | Resistance is taken to increase with both length and diameter: 2 × 2 = 4 |

---

## Question 2 — Paper 1A

A battery of emf 6.0 V and internal resistance 0.50 Ω is connected to a resistor of resistance 2.5 Ω.

What is the power dissipated in the 2.5 Ω resistor?

A. 2.0 W
B. 10 W
C. 12 W
D. 14 W

**Answer: B**

**Solution.** *I* = ε / (*R* + *r*) = 6.0 / 3.0 = 2.0 A. Power dissipated in the resistor = *I*²*R* = 2.0² × 2.5 = 10 W.

| Option | Misconception |
|---|---|
| A | The power dissipated in the internal resistance is calculated: 2.0² × 0.50 = 2.0 W |
| C | The total power of the battery is given: ε*I* = 6.0 × 2.0 = 12 W |
| D | The internal resistance is ignored: ε²/*R* = 36 / 2.5 = 14.4 W |

---

## Question 3 — Paper 1A

A light-dependent resistor (LDR) and a fixed resistor of resistance 10 kΩ are connected in series with a battery of emf 9.0 V and
negligible internal resistance. An ideal voltmeter is connected across the fixed resistor. In bright light the resistance of the
LDR is 2.0 kΩ.

> **Figure:** Single-loop series circuit: a 9.0 V battery, an LDR and a 10 kΩ fixed resistor connected one after another. The voltmeter is connected only
> in parallel across the 10 kΩ resistor.

What is the reading on the voltmeter in bright light?

A. 1.5 V
B. 1.8 V
C. 4.5 V
D. 7.5 V

**Answer: D**

**Solution.** Potential divider: *V* = 9.0 × 10 / (10 + 2.0) = 7.5 V.

| Option | Misconception |
|---|---|
| A | The pd across the LDR is calculated: 9.0 × 2.0 / 12 = 1.5 V |
| B | The pd is found from the ratio of the resistances to each other (not divided by the sum): 9.0 × 2.0 / 10 = 1.8 V |
| C | Two components in series are assumed to share the pd equally: 9.0 / 2 = 4.5 V |

---

## Question 4 — Paper 1A

A resistor of resistance 6.0 Ω is connected in series with a parallel combination of a 12 Ω resistor and a 4.0 Ω resistor. The
arrangement is connected to a battery of emf 18 V and negligible internal resistance.

> **Figure:** The conductor leaving one terminal of the 18 V battery first passes through the 6.0 Ω resistor and then splits into two branches: one branch has a 12 Ω resistor, the other has a
> 4.0 Ω resistor. The branches rejoin and return to the other terminal of the battery.

What is the current in the 4.0 Ω resistor?

A. 0.50 A
B. 1.0 A
C. 1.5 A
D. 2.0 A

**Answer: C**

**Solution.** Parallel section: (12 × 4.0) / (12 + 4.0) = 3.0 Ω. Total resistance 9.0 Ω; current in the main branch 18 / 9.0 = 2.0 A. The pd across the parallel
section is 2.0 × 3.0 = 6.0 V. Current in the 4.0 Ω resistor = 6.0 / 4.0 = 1.5 A.

| Option | Misconception |
|---|---|
| A | The current is shared in direct proportion to resistance (or the current in the 12 Ω resistor is given): 2.0 × 4.0 / 16 = 0.50 A |
| B | The current is assumed to split equally between the two branches: 2.0 / 2 = 1.0 A |
| D | The current in the main branch is given; the split into branches is not taken into account: 2.0 A |

---

## Question 5 — Paper 2 (9 marks)

A student builds a hot-wire cutter for foam. A nichrome wire of diameter 0.20 mm is connected to a battery of emf 6.0 V and internal
resistance 1.2 Ω. The resistance of the wire is 4.8 Ω and can be assumed to be constant.

Resistivity of nichrome = 1.1 × 10⁻⁶ Ω m

**(a)** Show that the length of the wire is about 0.14 m. [2]

**(b)** Calculate the power dissipated in the wire. [2]

**(c)** Explain why the potential difference across the terminals of the battery is less than 6.0 V when the wire is connected. [2]

To cut faster, the student connects a second, identical nichrome wire in parallel with the first. The student predicts that the
total power dissipated in the two wires will be double the value in (b).

> **Figure:** Two nichrome wires, each of 4.8 Ω, are connected in parallel with each other across the terminals of the battery (emf 6.0 V, internal resistance 1.2 Ω).

**(d)** Determine whether the prediction of the student is correct. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *A* = π × (0.10 × 10⁻³)² «= 3.14 × 10⁻⁸ m²» ✓<br>*L* = *RA*/ρ = 4.8 × 3.14 × 10⁻⁸ / 1.1 × 10⁻⁶ = 0.137 «m» ✓ | *Answer 0.14 m is given; award the second mark only if 0.137 or the complete substitution is seen.*<br>*Award [1 max] if the diameter is used as the radius (0.55 m).* | 2 |
| 5. | b | | *I* = 6.0 / (4.8 + 1.2) «= 1.0 A» ✓<br>*P* = 1.0² × 4.8 = 4.8 «W» ✓ | *Award [1 max] for 7.5 W (internal resistance ignored).* | 2 |
| 5. | c | | there is a current in the battery so there is a potential difference across / energy is dissipated in the internal resistance ✓<br>terminal pd = emf − *Ir* «= 6.0 − 1.0 × 1.2 = 4.8 V» **OR** less energy per unit charge is available to the external circuit ✓ | *OWTTE* | 2 |
| 5. | d | | resistance of the parallel wires = 2.4 «Ω» **AND** *I* = 6.0 / (2.4 + 1.2) «= 1.67 A» ✓<br>total power in the wires = 1.67² × 2.4 = 6.7 «W» ✓<br>this is less than 2 × 4.8 = 9.6 «W», so the prediction is not correct «because the larger current increases the pd across the internal resistance / the terminal pd falls to 4.0 V / the power in each wire falls to 3.3 W» ✓ | *Allow ECF from (b).*<br>**ALTERNATIVE for the second mark:** terminal pd = 4.0 V, power in each wire = 4.0² / 4.8 = 3.3 «W» ✓<br>*The third mark requires a numerical comparison and a conclusion.* | 3 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `d = 0.20e-3 m`, `R = 4.8 ohm`, `emf = 6.0 V`, `r = 1.2 ohm`; constant `rho = 1.1e-6 ohm m` | |
| `A` | `pi*(d/2)**2` | 3.14 × 10⁻⁸ m² |
| `L` | `R*A/rho` | 0.137 m |
| `I1` | `emf/(R + r)` | 1.00 A |
| `P1` | `I1**2*R` | 4.80 W |
| `V_term1` | `emf - I1*r` | 4.80 V |
| `R_par` | `R/2` | 2.40 Ω |
| `I2` | `emf/(R_par + r)` | 1.67 A |
| `P2` | `I2**2*R_par` | 6.67 W |
| `V_term2` | `emf - I2*r` | 4.00 V |
| Comparison | `P2 < 2*P1` | 6.67 W < 9.60 W → prediction wrong |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + (figure) + a separate single question sentence ("What is …?") + A–D listed one under another | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–4 conform (ascending) |
| 1A: negation / key word in bold | Question 1 ("twice") conforms; no negative stem |
| 1A: position of the correct answer balanced | A, B, D, C |
| 1A: solvable without a figure | In Questions 3 and 4 the circuit is fully described in words in the question text; the `> **Figure:**` description is only supplementary. Circuit diagrams were not drawn |
| 1A: round, clean numbers | Questions 1–4 conform; in Question 2 the D distractor was rounded 14.4 → 14 W |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 2, 3; total 9) |
| Paper 2: at least one AO3 part; "Show that" pattern | Question 5 conforms: (a) Show that, (c) Explain, (d) Determine |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE, ALTERNATIVE | Question 5 conforms |
| Value–unit notation (Ω m), 2 significant figures | Conforms |
| Meters ideal unless stated otherwise | In Question 3 "ideal voltmeter" is stated explicitly |
| Paper 2: answer box, dotted lines | Not in this draft; will be added in the publication template |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver independent of its author, without seeing the answers (circuits from the verbal
description only); all answer keys and markscheme results were reproduced independently (no CRITICAL or MEDIUM findings). Detail:
[review/b5-review.md](review/b5-review.md). This check does not replace expert review.

Changes made as a result of the review (no numerical value changed; the keys are the same):

- **Question 2, LOW-1:** "A cell of emf 6.0 V" → "A battery of emf 6.0 V" (6.0 V is unusual for a single chemical cell). The answer B
  (10 W) and the distractors did not change.
- **Question 5 (d), LOW-2:** "the power in each wire falls to 3.3 W" was added to the third markscheme point as an accepted reason
  (4.0² / 4.8 = 3.33 W).
- **LOW-3 (9 marks in an SL short question) and LOW-4 (circuit diagrams not drawn):** no change made; the first is a record awaiting expert
  confirmation, the second cannot be resolved until figure generation is available and is already flagged in "Format conformance".
