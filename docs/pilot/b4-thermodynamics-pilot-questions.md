# Pilot question set: B.4 Thermodynamics

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
> **B.4 is an HL-only node; no question in this file enters the SL pool.**
>
> **Source:** only syllabus node B.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; no PDF was opened.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. The value of 460 J given in Question 6 is the isothermal compression calculation
> *nRT* ln(*V*<sub>A</sub>/*V*<sub>C</sub>) = −458 J rounded to two significant figures (this calculation is not asked of the student).
> The sign convention is Clausius throughout: *Q* is the energy supplied to the system, *W* is the work done by the system, *Q* = Δ*U* + *W*.
> **Not verified:** passed an independent blind solver; has not passed expert review; qualitative points (the discussion in Question 6d) cannot be checked by code;
> it has not been confirmed by an expert that the counting model in Question 3 is at the level the guide means by a "simple counting model"; it has not been
> confirmed that, in Question 6(d), comparing with the Carnot limit between the highest and lowest temperatures of the cycle is the form of statement the guide expects;
> no expert check was made for resemblance to a known exam question.

## Scope table

| # | Section | Level | Outcome (B.4) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | First law and sign convention (Q = ΔU + W) | AO2 | — | 1 | Easy |
| 2 | Paper 1A | HL | Adiabatic process, PV^(5/3) = constant | AO2 | — | 1 | Medium |
| 3 | Paper 1A | HL | Entropy and the number of microstates, S = k ln Ω (simple counting model) | AO3 | — | 1 | Medium–hard |
| 4 | Paper 1A | HL | Efficiency of a heat engine; distinction from Carnot efficiency | AO2 | — | 1 | Easy |
| 5 | Paper 1A | HL | First law in an isothermal process and ΔS = ΔQ/T | AO3 | — | 1 | Medium |
| 6 | Paper 2 | HL | Cycle with isobaric, adiabatic and isothermal steps; W = PΔV; first law; efficiency; Carnot limit and the second law | AO2–AO3 | Show that, Determine, Discuss | 9 | Medium–hard |

This set does not cover all of B.4. Not covered: the isochoric process; drawing a cycle on a P–V diagram and interpreting the enclosed area as work;
statement of the Clausius and Kelvin forms of the second law; irreversibility and the increase of entropy in an isolated system; the entropy
change of the surroundings; numerical use of the temperature–volume relation in an adiabatic process.

Scope boundary check: all quantitative questions are for a monatomic ideal gas and this is stated in the question text; the sign convention is Clausius;
microstates only with the two-compartment counting model of four particles (Question 3); the logarithmic formula for isothermal work is not asked of the student
(energy values are given in Questions 5 and 6). No derivatives or integrals.

---

## Question 1 — Paper 1A

Thermal energy of 500 J is supplied to a monatomic ideal gas. At the same time, the gas is compressed and 200 J of work is done
**on** the gas.

What is the change in the internal energy of the gas?

A. −700 J
B. −300 J
C. +300 J
D. +700 J

**Answer: D**

**Solution.** Clausius sign convention: *Q* = +500 J (supplied to the system), *W* = −200 J (work is done on the gas, so the work done by the gas is negative).
Δ*U* = *Q* − *W* = 500 − (−200) = +700 J.

| Option | Misconception |
|---|---|
| A | The magnitude is right but the sign is reversed: both energy inputs are taken to decrease the internal energy: −700 J |
| B | The sign of *W* is taken wrongly and the result is also reversed (Δ*U* = *W* − *Q* = 200 − 500): −300 J |
| C | Work done on the gas is treated as work done by the gas (*W* = +200 J): 500 − 200 = +300 J |

---

## Question 2 — Paper 1A

A monatomic ideal gas at pressure *P* is compressed adiabatically to **one eighth** of its initial volume.

What is the final pressure of the gas?

A. 512*P*
B. 32*P*
C. 8*P*
D. 4*P*

**Answer: B**

**Solution.** *PV*<sup>5/3</sup> = constant → *P*₂ = *P* × (*V*₁/*V*₂)<sup>5/3</sup> = *P* × 8<sup>5/3</sup> = *P* × 2⁵ = 32*P*.

| Option | Misconception |
|---|---|
| A | The exponent is taken as 3 instead of 5⁄3: 8³ = 512 |
| C | The process is taken to be isothermal (*PV* = constant): 8*P* |
| D | The temperature ratio is taken to be the pressure ratio (*TV*<sup>2/3</sup> = constant): 8<sup>2/3</sup> = 4 |

---

## Question 3 — Paper 1A

Four distinguishable particles are in a box. Each particle can be in the left half or in the right half of the box. A microstate
is specified by stating which half each particle is in. A macrostate is specified by stating only the number of particles in each
half. The entropy of a macrostate is *S* = *k* ln Ω, where Ω is the number of microstates of that macrostate and *k* is the
Boltzmann constant.

What is the entropy of the macrostate with two particles in each half **minus** the entropy of the macrostate with all four
particles in the left half?

A. *k* ln 2
B. *k* ln 4
C. *k* ln 6
D. *k* ln 16

**Answer: C**

**Solution.** The initial macrostate (4 on the left) has a single microstate: Ω₁ = 1, *S*₁ = *k* ln 1 = 0. For the final macrostate (2 on the left, 2 on the right),
the number of ways of choosing the two particles on the left is Ω₂ = 4! / (2! 2!) = 6. Δ*S* = *k* ln 6 − *k* ln 1 = *k* ln 6.

| Option | Misconception |
|---|---|
| A | The number of compartments (2) is taken as the number of microstates |
| B | The number of particles (4) is taken as the number of microstates |
| D | The number of all possible microstates is taken instead of that of the final macrostate: 2⁴ = 16 (the free-expansion reading, 4*k* ln 2; this reading is excluded because the question text defines the macrostate explicitly) |

---

## Question 4 — Paper 1A

In each cycle, a heat engine absorbs 800 J of thermal energy from a hot reservoir at 500 K and transfers 600 J of thermal energy to
a cold reservoir at 300 K.

What is the efficiency of the heat engine?

A. 0.25
B. 0.33
C. 0.40
D. 0.75

**Answer: A**

**Solution.** Work done per cycle = 800 − 600 = 200 J. Efficiency = useful work / energy absorbed = 200 / 800 = 0.25.

| Option | Misconception |
|---|---|
| B | The work is divided by the energy rejected instead of the energy absorbed: 200 / 600 = 0.33 |
| C | The Carnot efficiency is calculated instead of the actual efficiency: 1 − 300 / 500 = 0.40 |
| D | The ratio of the energy rejected to the energy absorbed is taken as the efficiency: 600 / 800 = 0.75 |

---

## Question 5 — Paper 1A

A monatomic ideal gas expands slowly (reversibly) and isothermally at a temperature of 300 K. The gas does 600 J of work during
the expansion.

What is the change in the entropy of the gas?

A. −2.0 J K⁻¹
B. 0
C. +0.50 J K⁻¹
D. +2.0 J K⁻¹

**Answer: D**

**Solution.** In an isothermal process the internal energy of an ideal gas does not change: Δ*U* = 0, so *Q* = *W* = +600 J (supplied to the gas).
Δ*S* = Δ*Q* / *T* = 600 / 300 = +2.0 J K⁻¹.

| Option | Misconception |
|---|---|
| A | Since the gas does work it is thought to lose energy; *Q* is taken as negative: −600 / 300 = −2.0 |
| B | The thought "the temperature does not change, so there is no energy exchange and no entropy change" (isothermal is confused with adiabatic) |
| C | The ratio is set up the wrong way round: 300 / 600 = 0.50 |

---

## Question 6 — Paper 2 (9 marks)

A fixed mass of a monatomic ideal gas is taken through a cycle A → B → C → A.

- In state A the pressure is 1.0 × 10⁵ Pa, the volume is 2.0 × 10⁻³ m³ and the temperature is 300 K.
- A → B is an isobaric expansion to a volume of 5.0 × 10⁻³ m³. The temperature at B is 750 K.
- B → C is an adiabatic expansion. The temperature at C is 300 K.
- C → A is an isothermal compression.

> **Figure:** Pressure–volume (*P*–*V*) graph; not to scale. From A to B a straight horizontal line to the right (constant pressure). From B to C a steep curve going to the right and
> downwards (adiabatic). From C to A a less steep curve going to the left and upwards (isothermal). The cycle is traversed clockwise.

**(a)** Show that the thermal energy supplied to the gas during A → B is 750 J. [3]

**(b)** Determine the work done by the gas during B → C. [2]

During C → A, 460 J of thermal energy is transferred from the gas to the surroundings.

**(c)** Determine the efficiency of the cycle. [2]

**(d)** Discuss whether your answer to (c) is consistent with the second law of thermodynamics. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *W* = *P*Δ*V* = 1.0 × 10⁵ × 3.0 × 10⁻³ «= 300 J» ✓<br>Δ*U* = 3⁄2 *P*Δ*V* **OR** 3⁄2 *nR*Δ*T* «with *nR* = 0.667 J K⁻¹» = 450 «J» ✓<br>*Q* = Δ*U* + *W* = 450 + 300 «= 750 J» ✓ | *The third mark is for the explicit use of the first law.*<br>*n = 0.080 mol if calculated.* | 3 |
| 6. | b | | *Q* = 0 so *W* = −Δ*U* ✓<br>Δ*U* = −450 «J» «same temperature change as A → B, reversed» so *W* = «+» 450 «J» ✓ | *Accept* Δ*U* = 3⁄2 *nR* (300 − 750) *for the second mark.*<br>*Allow ECF from (a).* | 2 |
| 6. | c | | net work = 750 − 460 **OR** 300 + 450 − 460 «= 290 J» ✓<br>efficiency = 290 / 750 = 0.39 ✓ | *Allow ECF from (b).*<br>*Thermal energy is supplied only during A → B.* | 2 |
| 6. | d | | Carnot efficiency «between 750 K and 300 K» = 1 − 300 / 750 = 0.60 ✓<br>0.39 is less than 0.60, so the cycle is consistent with / does not violate the second law ✓ | *Allow ECF from (c).*<br>*Accept an argument that some thermal energy is rejected to the surroundings, so not all the energy supplied is converted to work «Kelvin form», for the second mark only.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `P_A = 1.0e5 Pa`, `V_A = 2.0e-3 m^3`, `V_B = 5.0e-3 m^3`, `T_A = 300 K`, `Q_CA = -460 J` | |
| `T_B` | `T_A*V_B/V_A` | 750 K (consistent with the value given in the question) |
| `W_AB` | `P_A*(V_B - V_A)` | 300 J |
| `dU_AB` | `1.5*P_A*(V_B - V_A)` | 450 J |
| `Q_AB` | `dU_AB + W_AB` | 750 J |
| `W_BC` | `-dU_BC = dU_AB` | 450 J |
| `W_net` | `Q_AB + Q_CA` | 290 J |
| `eta` | `W_net/Q_AB` | 0.387 |
| `eta_Carnot` | `1 - T_A/T_B` | 0.60 |
| Consistency check (not asked of the student) | `V_C = V_B*(T_B/T_A)**1.5`; `Q_CA = nR*T_A*ln(V_A/V_C)` | *V*<sub>C</sub> = 1.98 × 10⁻² m³; *Q*<sub>CA</sub> = −458 J; efficiency 0.389 |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one under another | Questions 1–5 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1, 3, 4, 5 ascending; Question 2 descending |
| 1A: negation / key word in bold | Question 1 ("on"), Question 2 ("one eighth") and Question 3 ("minus") conform; no negative stem |
| 1A: position of the correct answer balanced | D, B, C, A, D |
| 1A: solvable without a figure | Questions 1–5 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 6 conforms (3, 2, 2, 2; total 9) |
| Paper 2: at least one AO3 part; "Show that" pattern | Question 6 conforms: (a) Show that; (b), (c) Determine; (d) Discuss |
| Paper 2: figure | In Question 6 the *P*–*V* diagram is described with `> **Figure:**`; all data are in the text, and the question can be solved without the figure. No drawing was produced |
| Markscheme: four-column table, ✓, « », OR, ECF | Question 6 conforms |
| Value–unit notation (J K⁻¹), 2 significant figures | Conforms |
| Level label | All questions are HL; cannot be used in an SL paper |
| Paper 2: answer box, dotted lines | Not in this draft; will be added in the publication template |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver independent of its author, without seeing the answers; all answer keys and
markscheme results (including the step-by-step energy balance of the Question 6 cycle) were reproduced independently (no CRITICAL findings).
Detail: [review/b4-review.md](review/b4-review.md). This check does not replace expert review.

Changes made as a result of the review (no numerical value changed; the keys are the same):

- **Question 3, MEDIUM-1:** the question text was rewritten. The macrostate is now explicitly defined ("only the number of particles in each half"),
  the definition *S* = *k* ln Ω is given in the stem and the question sentence asks for the entropy difference of two specific macrostates. This excludes the free-expansion
  reading (*k* ln 16). The answer C (*k* ln 6) and the options did not change. The stem is about 85 words; close to the longest stem
  in the profile (≈ 90).
- **Question 5, LOW-1:** "expands isothermally" → "expands slowly (reversibly) and isothermally"; the condition for using Δ*S* = Δ*Q*/*T*
  is now stated. The answer D (+2.0 J K⁻¹) did not change.
- **LOW-2 (460 J ↔ 458 J), LOW-3 (form of statement of the Carnot comparison), LOW-4 (figure described only in words):** no change
  made; the review recorded these as notes, not as problems, and proposes no concrete correction.
