# Pilot question set: B.1 Thermal energy transfers

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node B.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; no PDF was opened.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. Values used: specific heat capacity of water 4200 J kg⁻¹ K⁻¹, aluminium
> 900 J kg⁻¹ K⁻¹, specific latent heat of vaporization of water 2.26 × 10⁶ J kg⁻¹, thermal conductivity of ice 2.2 W m⁻¹ K⁻¹. All are given in the question;
> the data booklet values must be confirmed by an expert.
> **Not verified:** passed an independent blind solver; has not passed expert review; qualitative markscheme points (Question 5c) cannot be checked by code;
> material values were taken from general knowledge and not confirmed against a source; no expert check was made for resemblance to a known exam question;
> conformance with the data booklet symbols and formula notation (e.g. the conduction equation) was not checked.

## Scope table

| # | Section | Level | Outcome (B.1) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Thermal equilibrium using Q = mcΔT (two bodies) | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Rate of energy transfer by conduction (quantitative) | AO2 | — | 1 | Easy |
| 3 | Paper 1A | SL | Combining Wien's law and the Stefan-Boltzmann law; radiated power | AO3 | — | 1 | Medium–hard |
| 4 | Paper 1A | SL | Change of state; combining Q = mcΔT and Q = mL at constant power | AO3 | — | 1 | Medium |
| 5 | Paper 2 | SL | Q = mcΔT, Q = mL; molecular model and internal energy in a change of state; energy loss to the surroundings | AO2–AO3 | Show that, Calculate, Explain, Determine | 8 | Medium |

This set does not cover all of B.1. Not covered: density; Kelvin–Celsius conversion (as a separate question); the relationship between temperature and average
kinetic energy (Ē = 3⁄2 kT); qualitative description of convection; apparent brightness (b = L / 4πd²); direct temperature calculation
using Wien's law; interpretation of a heating curve graph.

Scope boundary check: convection is not calculated in any question (qualitative boundary only). No derivatives or integrals.

---

## Question 1 — Paper 1A

An aluminium block of mass 0.20 kg at a temperature of 90 °C is placed in 0.30 kg of water at 20 °C. The water is in an insulated
container of negligible heat capacity. No water evaporates.

Specific heat capacity of aluminium = 900 J kg⁻¹ K⁻¹
Specific heat capacity of water = 4200 J kg⁻¹ K⁻¹

What is the final temperature of the water?

A. 29 °C
B. 48 °C
C. 55 °C
D. 73 °C

**Answer: A**

**Solution.** The energy given out by the block equals the energy gained by the water: 0.20 × 900 × (90 − *T*) = 0.30 × 4200 × (*T* − 20).
180 (90 − *T*) = 1260 (*T* − 20) → *T* = (16 200 + 25 200) / 1440 = 28.75 °C ≈ 29 °C.

| Option | Misconception |
|---|---|
| B | Specific heat capacities are ignored and only a mass-weighted average is taken: (0.20 × 90 + 0.30 × 20) / 0.50 = 48 °C |
| C | The arithmetic mean of the two temperatures is taken: (90 + 20) / 2 = 55 °C |
| D | The specific heat capacities are swapped: (0.20 × 4200 × 90 + 0.30 × 900 × 20) / (840 + 270) = 73.0 °C |

---

## Question 2 — Paper 1A

A layer of ice of thickness 5.0 cm covers a pond. The upper surface of the ice is at −8.0 °C and the lower surface is at 0 °C.
The thermal conductivity of ice is 2.2 W m⁻¹ K⁻¹.

What is the rate of thermal energy transfer by conduction through each square metre of the ice?

A. 0.88 W
B. 3.5 W
C. 350 W
D. 1.2 × 10⁴ W

**Answer: C**

**Solution.** Δ*Q*/Δ*t* = *kA*Δ*T*/Δ*x* = 2.2 × 1.0 × 8.0 / 0.050 = 352 W ≈ 350 W.

| Option | Misconception |
|---|---|
| A | Multiplies by the thickness instead of dividing by it: 2.2 × 8.0 × 0.050 = 0.88 W |
| B | The thickness is not converted to metres: 2.2 × 8.0 / 5.0 = 3.52 W |
| D | A single temperature converted to kelvin is used instead of the temperature difference: 2.2 × 265 / 0.050 = 1.17 × 10⁴ W |

---

## Question 3 — Paper 1A

Stars X and Y can be treated as black bodies. The radius of X is three times the radius of Y. The wavelength at which the emitted
intensity is a maximum for X is **half** the corresponding wavelength for Y.

What is the ratio (luminosity of X) / (luminosity of Y)?

A. 9⁄16
B. 36
C. 48
D. 144

**Answer: D**

**Solution.** Wien's law: λ<sub>max</sub>*T* = constant, so *T*<sub>X</sub> = 2*T*<sub>Y</sub>. Stefan-Boltzmann: *L* = σ*AT*⁴ and *A* ∝ *r*².
Oran = 3² × 2⁴ = 9 × 16 = 144.

| Option | Misconception |
|---|---|
| A | Wien's law is applied the wrong way round (the shorter wavelength is treated as cooler): 9 × (1⁄2)⁴ = 9⁄16 |
| B | Radiated power is taken as proportional to *T*² instead of *T*⁴: 9 × 2² = 36 |
| C | Surface area is taken as proportional to *r* instead of *r*²: 3 × 2⁴ = 48 |

---

## Question 4 — Paper 1A

A solid sample is heated at a constant rate in an insulated container. While the sample is solid, its temperature rises at
0.50 K s⁻¹. After the sample reaches its melting point, it takes 300 s to melt completely. The specific heat capacity of the
solid is 800 J kg⁻¹ K⁻¹.

What is the specific latent heat of fusion of the sample?

A. 4.0 × 10² J kg⁻¹
B. 1.2 × 10⁵ J kg⁻¹
C. 2.4 × 10⁵ J kg⁻¹
D. 4.8 × 10⁵ J kg⁻¹

**Answer: B**

**Solution.** The power is constant: *P* = *mc* (Δ*T*/Δ*t*) = *m* × 800 × 0.50 = 400*m*. Melting: *mL* = *P* × 300 → *L* = 400 × 300 =
1.2 × 10⁵ J kg⁻¹. The mass cancels, so it is deliberately not given.

| Option | Misconception |
|---|---|
| A | Only the power per unit mass is calculated and it is not multiplied by the time: 800 × 0.50 = 400 |
| C | The heating rate is not used: 800 × 300 = 2.4 × 10⁵ |
| D | Divides by the heating rate instead of multiplying by it: 800 × 300 / 0.50 = 4.8 × 10⁵ |

---

## Question 5 — Paper 2 (8 marks)

An electric immersion heater of power 1.4 kW is placed in 0.80 kg of water in an insulated vessel. The initial temperature of the
water is 25 °C. The heat capacity of the vessel and of the heater is negligible.

Specific heat capacity of water = 4200 J kg⁻¹ K⁻¹
Specific latent heat of vaporization of water = 2.26 × 10⁶ J kg⁻¹

**(a)** Show that the time taken for the water to reach 100 °C is about 180 s. [2]

The heater stays switched on for a further 120 s after the water has reached 100 °C.

**(b)** Calculate the mass of water that vaporizes during this time. [2]

**(c)** Explain, with reference to the energy of the molecules, why the temperature of the water stays constant while it boils
even though energy is being supplied. [2]

The experiment is repeated with the same initial conditions, but the insulation is removed from the vessel. The time measured for
the water to reach 100 °C is now 200 s.

**(d)** Determine the average rate at which thermal energy is transferred from the water to the surroundings during this second experiment. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *Q* = 0.80 × 4200 × 75 «= 2.52 × 10⁵ J» ✓<br>*t* = 2.52 × 10⁵ / 1400 «= 180 s» ✓ | *Answer 180 s is given; award the second mark only if the complete substitution is seen.* | 2 |
| 5. | b | | energy supplied = 1400 × 120 «= 1.68 × 10⁵ J» ✓<br>*m* = 1.68 × 10⁵ / 2.26 × 10⁶ = 0.074 «kg» ✓ | *The vessel is insulated in (b): all the energy supplied vaporizes water.* | 2 |
| 5. | c | | the energy supplied increases the «intermolecular» potential energy of the molecules **OR** is used to separate the molecules / break intermolecular bonds ✓<br>the average «random» kinetic energy of the molecules does not change **AND** temperature is a measure of this average kinetic energy ✓ | *OWTTE* | 2 |
| 5. | d | | useful power = 2.52 × 10⁵ / 200 «= 1260 W» ✓<br>rate of loss = 1400 − 1260 = 140 «W» ✓ | *Allow ECF from (a).*<br>**ALTERNATIVE:** energy lost = 1400 × (200 − 180) «= 2.8 × 10⁴ J» ✓ rate = 2.8 × 10⁴ / 200 = 140 «W» ✓<br>*Both routes give 140 W; no accept range is needed.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `P = 1400 W`, `m = 0.80 kg`, `T1 = 25 °C`, `T2 = 100 °C`, `t_boil = 120 s`, `t_meas = 200 s`; constant `c = 4200 J/(kg K)`, `L = 2.26e6 J/kg` | |
| `Q` | `m*c*(T2 - T1)` | 2.52 × 10⁵ J |
| `t` | `Q/P` | 180 s (exact) |
| `m_vap` | `P*t_boil/L` | 0.0743 kg |
| `P_useful` | `Q/t_meas` | 1260 W |
| `P_loss` | `P - P_useful` | 140 W (the `P*(t_meas - t)/t_meas` route also gives 140 W) |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one under another | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–4 conform (ascending) |
| 1A: negation / key word in bold | Question 3 ("half") conforms; no negative stem |
| 1A: position of the correct answer balanced | A, C, D, B |
| 1A: solvable without a figure | Questions 1–4 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 2, 2; total 8) |
| Paper 2: at least one AO3 part; "Show that" pattern | Question 5 conforms: (a) Show that, (c) Explain, (d) Determine |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE | Question 5 conforms |
| Value–unit notation (J kg⁻¹ K⁻¹), 2 significant figures | Conforms; in Question 2 the 1.2 × 10⁴ distractor is in scientific notation |
| 1A: round, clean numbers | Questions 3–4 are clean; Question 1 (28.75 → 29) and Question 2 (352 → 350) require rounding |
| Paper 2: answer box, dotted lines | Not in this draft; will be added in the publication template |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver independent of its author, without seeing the answers; all answer keys and
markscheme results were reproduced independently (no CRITICAL findings). Detail: [review/b1-review.md](review/b1-review.md).
This check does not replace expert review.

Changes made as a result of the review (every changed number was recalculated with `python3`):

- **Question 5, MEDIUM-1:** the contradiction between "insulated vessel" and energy loss to the surroundings was removed; (d) now describes
  a second experiment in which the insulation is removed. (a)–(c) remain in the insulated case; this is stated in the note to (b).
- **Question 5, MEDIUM-2:** the data were redesigned: heater power 1.5 kW → 1.4 kW, test time 190 s → 200 s. Results: (a) 168 s
  ("about 170 s") → 180 s (exact); (b) 0.080 kg → 0.074 kg; (d) 174 W / 158 W (depending on the route) → 140 W by both routes. The 160–180 W accept
  range was removed.
- **LOW-1 (8 marks in an SL short question) and LOW-3 (rounding in Questions 1–2):** no change made; the authoring standard allows 4–9 marks,
  and rounding does not affect the single correct answer. Remains on record for expert confirmation.
