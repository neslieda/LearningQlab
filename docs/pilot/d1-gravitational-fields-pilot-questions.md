# Pilot question set: D.1 Gravitational fields

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node D.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; the scenarios are the author's inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. Constant used: G = 6.67 × 10⁻¹¹ N m² kg⁻² (the data booklet value should be
> confirmed by an expert).
> **Independent check:** passed an independent blind solver; has not passed expert review (see end of file).
> **Not verified:** (1) no expert review was done; (2) the celestial body data (mass and radius of Mars, the Moon and Titan) were taken from
> the author's general knowledge to 2–3 significant figures and were not confirmed against a source; (3) the assumption that Titan has enough atmosphere at a height of 1500 km
> to cause measurable drag was not confirmed (the question asks only for a qualitative result); (4) because the "orbital speed
> formula" counts as additional HL, Question 5 is labelled HL as a whole; whether parts (a) and (b) could be asked at SL
> should be confirmed by an expert; (5) no expert check was made for similarity to any known exam question.

## Scope table

| # | Section | Level | Outcome (D.1) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Inverse-square variation of field strength with distance from the centre; height vs distance | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Kepler's third law (circular orbit) | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Resultant field strength on the line joining two bodies | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Gravitational potential (zero at infinity); W = mΔV | AO2 | — | 1 | Medium–hard |
| 5 | Paper 2 | HL | Orbital speed; period; orbital energy and escape; qualitative effect of atmospheric drag | AO2–AO3 | Show that, Calculate, Determine, Explain | 9 | Medium–hard |

This set does not cover all of D.1. Not covered: Kepler's first and second laws, the condition for the point-mass approximation, field lines,
field strength = potential gradient, equipotential surfaces, direct use of the escape speed formula.

Scope limit check: all orbits are circular; the resultant field is only on the line joining two bodies (Question 3); potential is
zero at infinity (Questions 4, 5); no derivatives or integrals; drag is only qualitative (Question 5d).

---

## Question 1 — Paper 1A

The gravitational field strength at the surface of Mars is 3.7 N kg⁻¹. The radius of Mars is 3.4 × 10⁶ m. A probe is at a height of
6.8 × 10⁶ m **above the surface** of Mars.

What is the gravitational field strength due to Mars at the position of the probe?

A. 0.41 N kg⁻¹
B. 0.93 N kg⁻¹
C. 1.2 N kg⁻¹
D. 1.9 N kg⁻¹

**Answer: A**

**Solution.** Distance from the centre r = R + h = 3.4 × 10⁶ + 6.8 × 10⁶ = 1.02 × 10⁷ m = 3R. Field strength varies as 1/r²:
g = 3.7 / 3² = 0.41 N kg⁻¹.

| Option | Misconception |
|---|---|
| B | Takes the height to be the distance from the centre (r = 2R): 3.7 / 2² = 0.93 N kg⁻¹ |
| C | Uses the correct distance (3R) but assumes the field varies as 1/r: 3.7 / 3 = 1.2 N kg⁻¹ |
| D | Takes the height as the distance and also uses 1/r: 3.7 / 2 = 1.9 N kg⁻¹ |

---

## Question 2 — Paper 1A

Two small moons X and Y move in circular orbits around the same planet. The orbital radius of X is *r* and its orbital period is
4.0 days. The orbital radius of Y is 4*r*.

What is the orbital period of Y?

A. 8.0 days
B. 10 days
C. 16 days
D. 32 days

**Answer: D**

**Solution.** Kepler's third law: T² ∝ r³, so T ∝ r^(3/2). T<sub>Y</sub> = 4.0 × 4^(3/2) = 4.0 × 8 = 32 days.

| Option | Misconception |
|---|---|
| A | Takes T ∝ √r: 4.0 × 4^(1/2) = 8.0 days |
| B | Inverts the powers (T³ ∝ r²): 4.0 × 4^(2/3) = 10.1 ≈ 10 days |
| C | Takes T ∝ r: 4.0 × 4 = 16 days |

---

## Question 3 — Paper 1A

Two stars P and Q form a binary system. The mass of P is 2.0 × 10³⁰ kg and the mass of Q is 6.0 × 10³⁰ kg. The distance between the
centres of the stars is 4.0 × 10¹¹ m. Point Z is on the line joining the centres, midway between the stars.

G = 6.67 × 10⁻¹¹ N m² kg⁻²

What is the magnitude of the resultant gravitational field strength at Z?

A. 1.7 × 10⁻³ N kg⁻¹
B. 3.3 × 10⁻³ N kg⁻¹
C. 6.7 × 10⁻³ N kg⁻¹
D. 1.3 × 10⁻² N kg⁻¹

**Answer: C**

**Solution.** The distance from Z to each star is 2.0 × 10¹¹ m. The fields are in opposite directions (each towards its own star), so the magnitudes
are subtracted: g = G(M<sub>Q</sub> − M<sub>P</sub>) / r² = 6.67 × 10⁻¹¹ × 4.0 × 10³⁰ / (2.0 × 10¹¹)² = 6.7 × 10⁻³ N kg⁻¹, towards Q.

| Option | Misconception |
|---|---|
| A | Subtracts the fields but uses the whole distance between the stars as the distance: 6.67 × 10⁻¹¹ × 4.0 × 10³⁰ / (4.0 × 10¹¹)² = 1.7 × 10⁻³ |
| B | Adds the fields and uses the whole distance: 6.67 × 10⁻¹¹ × 8.0 × 10³⁰ / (4.0 × 10¹¹)² = 3.3 × 10⁻³ |
| D | Distance correct, but does not see that the fields are in opposite directions and adds the magnitudes: 6.67 × 10⁻¹¹ × 8.0 × 10³⁰ / (2.0 × 10¹¹)² = 1.3 × 10⁻² |

---

## Question 4 — Paper 1A (HL)

The gravitational potential at the surface of the Moon is −2.8 MJ kg⁻¹. The radius of the Moon is *R*. A probe of mass 160 kg is
moved from rest on the surface of the Moon to rest at a point that is a distance 4*R* from the **centre** of the Moon.

What is the minimum energy required to move the probe?

A. 1.1 × 10⁸ J
B. 3.4 × 10⁸ J
C. 4.2 × 10⁸ J
D. 4.5 × 10⁸ J

**Answer: B**

**Solution.** Potential varies as 1/r: at 4R, V = −2.8 / 4 = −0.70 MJ kg⁻¹. ΔV = −0.70 − (−2.8) = +2.1 MJ kg⁻¹.
W = mΔV = 160 × 2.1 × 10⁶ = 3.36 × 10⁸ ≈ 3.4 × 10⁸ J.

| Option | Misconception |
|---|---|
| A | Uses the magnitude of the potential at the final point instead of the potential difference: 160 × 0.70 × 10⁶ = 1.12 × 10⁸ ≈ 1.1 × 10⁸ J |
| C | Assumes potential varies as 1/r²: V = −2.8 / 16 = −0.175; 160 × 2.625 × 10⁶ = 4.2 × 10⁸ J |
| D | Uses the whole surface potential (energy to take the probe to infinity): 160 × 2.8 × 10⁶ = 4.48 × 10⁸ ≈ 4.5 × 10⁸ J |

---

## Question 5 — Paper 2 (HL, 9 marks)

Titan is a moon of Saturn. An orbiter of mass 900 kg moves in a circular orbit at a height of 1.50 × 10⁶ m above the surface of Titan.

mass of Titan = 1.35 × 10²³ kg
radius of Titan = 2.57 × 10⁶ m
G = 6.67 × 10⁻¹¹ N m² kg⁻²

**(a)** Show that the orbital speed of the orbiter is about 1.5 km s⁻¹. [2]

**(b)** Calculate the orbital period of the orbiter. [2]

**(c)** Determine the minimum additional energy that must be supplied to the orbiter for it to escape from the gravitational field
of Titan. Ignore the gravitational effect of Saturn. [2]

The outer atmosphere of Titan exerts a small drag force on the orbiter. The orbit remains approximately circular.

**(d)** Explain, without calculation, the effect of the drag force on the speed of the orbiter. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *GMm*/*r*² = *mv*²/*r* **OR** *v* = √(*GM*/*r*), with *r* = 2.57 × 10⁶ + 1.50 × 10⁶ «= 4.07 × 10⁶ m» ✓<br>*v* = √(6.67 × 10⁻¹¹ × 1.35 × 10²³ / 4.07 × 10⁶) = 1.49 × 10³ «m s⁻¹» ✓ | *Answer must be given to at least 3 s.f. or the full substitution shown.*<br>*Award [1] max if the correct relation is used with r = 1.50 × 10⁶ m or r = 2.57 × 10⁶ m «the given value is then not reached».* | 2 |
| 5. | b | | *T* = 2π*r*/*v* = 2π × 4.07 × 10⁶ / 1.49 × 10³ ✓<br>*T* = 1.7 × 10⁴ «s» ✓ | *Allow use of v = 1.5 × 10³ m s⁻¹.*<br>*Allow 4.8 «h».* | 2 |
| 5. | c | | total energy = ½*mv*² − *GMm*/*r* = −*GMm*/2*r* **OR** = −½*mv*² ✓<br>«total energy must be raised to zero, so» energy = 1.0 × 10⁹ «J» ✓ | *Allow ECF from (a).*<br>*Award [1] max for* 2.0 × 10⁹ J *«kinetic energy ignored».* | 2 |
| 5. | d | | total energy of the orbiter decreases «work is done against drag / energy is transferred to thermal energy» ✓<br>orbital radius decreases «as *E* = −*GMm*/2*r* becomes more negative» ✓<br>speed increases as *v* = √(*GM*/*r*) / *v* ∝ 1/√*r* ✓ | *OWTTE*<br>*Do not award MP3 for "speed decreases because drag opposes motion".* | 3 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `M = 1.35e23 kg`, `R = 2.57e6 m`, `h = 1.50e6 m`, `m = 900 kg`, constant `G = 6.67e-11` | |
| `r` | `R + h` | 4.07 × 10⁶ m |
| `v` | `sqrt(G*M/r)` | 1487 m s⁻¹ |
| `T` | `2*pi*r/v` | 1.72 × 10⁴ s (1.70 × 10⁴ s with v = 1.5 × 10³) |
| `E_total` | `-G*M*m/(2*r)` | −9.96 × 10⁸ J |
| `E_escape` | `-E_total` | 9.96 × 10⁸ J ≈ 1.0 × 10⁹ J (1.01 × 10⁹ J with v = 1.5 × 10³) |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed vertically | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–4 conform (ascending) |
| 1A: critical word in bold | Question 1 ("above the surface"), Question 4 ("centre") |
| 1A: balanced position of the correct answer | A, D, C, B |
| 1A: options are distinct after rounding | Checked (python) |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 2, 3; total 9) |
| Paper 2: "Show that" pattern; the next part may use the given value | Question 5(a) → (b), (c) conform |
| Paper 2: at least one AO3 part | Question 5(a) Show that, (c) Determine, (d) Explain |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE | Question 5 conforms |
| Figure | No question in this file needs a figure |
| Giving constants | G is given in the question text where needed (3, 5) |
| Value–unit notation (N kg⁻¹, m s⁻¹), 2–3 significant figures | Conforms |
| Paper 1B | Not in this file; the 1B question for theme D is [in the D.3 file](d3-motion-in-em-fields-pilot-questions.md) |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver other than its author, without seeing the answers; all answer keys and
distractor values were independently reproduced and matched. No CRITICAL or MEDIUM findings. Details:
[review/d1-review.md](review/d1-review.md). This check does not replace expert review.

Changes made in response to the review:

- **Question 4:** probe mass 150 kg → 160 kg. The correct result 3.15 × 10⁸ J was on a rounding boundary at two significant figures; the new value is
  3.36 × 10⁸ ≈ 3.4 × 10⁸ J. Options 1.1 / 3.2 / 3.9 / 4.2 → 1.1 / 3.4 / 4.2 / 4.5 (× 10⁸ J); the correct answer is still B. All options
  were recalculated with `python3`.
- **Question 5(a) markscheme:** the "scores zero" note for a wrong *r* was softened: if the correct relation is used with a wrong *r*, 1 mark maximum.
- **Not changed:** the HL label for Question 5 as a whole (the reviewer also found it on the safe side); awaiting expert confirmation.
