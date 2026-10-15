# Pilot question set: B.3 Gas laws

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
> The only Paper 1B (data-based) question requested for theme B is in this file (Question 6).
>
> **Source:** only syllabus node B.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; no PDF was opened.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. The line of best fit (least squares) in Question 6 and the steepest / shallowest lines passing through all
> uncertainty bars were also calculated by code from the data in the table. Constants: R = 8.31 J K⁻¹ mol⁻¹, k<sub>B</sub> = 1.38 × 10⁻²³ J K⁻¹,
> N<sub>A</sub> = 6.02 × 10²³ mol⁻¹; given in the question where needed; the data booklet values must be confirmed by an expert.
> **Not verified:** passed an independent blind solver; has not passed expert review; qualitative points (Questions 3, 5c, 5e, 6a–c, 6g) cannot be checked
> by code; the data of Question 6 are fictional (written by adding measurement scatter to ideal gas behaviour) and were not taken from a real experiment;
> it was not confirmed that the term "root mean square speed" is the same as the term the guide uses for P = ⅓ρv² (Question 4); no expert check was made for resemblance
> to a known exam question.

## Scope table

| # | Section | Level | Outcome (B.3) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Number of molecules using PV = NkT; kelvin temperature | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Internal energy of a monatomic ideal gas (U = 3⁄2 PV) | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Conditions under which the ideal gas approximation is valid | AO1 | — | 1 | Easy |
| 4 | Paper 1A | SL | Proportional reasoning with P = ⅓ρv² | AO3 | — | 1 | Medium |
| 5 | Paper 2 | SL | Ideal gas law, constant volume; pressure from kinetic theory; change in internal energy; limit of the model | AO2–AO3 | Show that, Calculate, Explain, Suggest | 9 | Medium |
| 6 | Paper 1B | SL | Pressure–temperature data at constant volume; linear versus directly proportional; extrapolation; uncertainty | AO2–AO3 | State, Outline, Discuss, Determine, Comment, Suggest | 11 | Medium–hard |

This set does not cover all of B.3. Not covered: calculations using the definition of pressure (P = F/A); mole–mass–molar mass conversions; processes at constant
temperature (PV = constant) and constant pressure (V/T = constant); drawing and interpreting a P–V diagram; listing the assumptions of the ideal gas model;
direct numerical calculation with P = ⅓ρv².

Scope boundary check: the processes are only constant volume (Questions 5, 6) and the application of the ideal gas law to a single state (Questions 1, 2, 4);
there are no adiabatic or other processes. No derivatives or integrals.

---

## Question 1 — Paper 1A

A sealed flask of volume 2.0 × 10⁻³ m³ contains an ideal gas at a pressure of 1.5 × 10⁵ Pa and a temperature of 27 °C.

Boltzmann constant = 1.38 × 10⁻²³ J K⁻¹

What is the number of gas molecules in the flask?

A. 7.2 × 10²²
B. 6.0 × 10²³
C. 8.1 × 10²³
D. 2.2 × 10²⁵

**Answer: A**

**Solution.** *T* = 27 + 273 = 300 K. *N* = *PV* / *kT* = (1.5 × 10⁵ × 2.0 × 10⁻³) / (1.38 × 10⁻²³ × 300) = 300 / 4.14 × 10⁻²¹ =
7.2 × 10²².

| Option | Misconception |
|---|---|
| B | The flask is assumed to contain one mole of gas; the Avogadro constant is given as the answer: 6.0 × 10²³ |
| C | The temperature is not converted to kelvin: 300 / (1.38 × 10⁻²³ × 27) = 8.05 × 10²³ |
| D | The temperature is not taken into account: *PV* / *k* = 300 / 1.38 × 10⁻²³ = 2.17 × 10²⁵ |

---

## Question 2 — Paper 1A

A monatomic ideal gas is in a container of volume 0.040 m³ at a pressure of 2.0 × 10⁵ Pa.

What is the internal energy of the gas?

A. 5.3 kJ
B. 8.0 kJ
C. 12 kJ
D. 24 kJ

**Answer: C**

**Solution.** *U* = 3⁄2 *NkT* = 3⁄2 *PV* = 1.5 × 2.0 × 10⁵ × 0.040 = 1.2 × 10⁴ J = 12 kJ. The temperature and the amount of substance are not needed.

| Option | Misconception |
|---|---|
| A | The factor is inverted: 2⁄3 *PV* = 5.33 kJ |
| B | Internal energy is taken to be equal to *PV*: 8.0 kJ |
| D | The factor 3 in the expression *P* = ⅓ρ*v*² is carried over to the energy: 3*PV* = 24 kJ |

---

## Question 3 — Paper 1A

The behaviour of a real gas is compared with the predictions of the ideal gas model.

Under which conditions is the ideal gas model the best approximation for a real gas?

A. high pressure and high temperature
B. high pressure and low temperature
C. low pressure and low temperature
D. low pressure and high temperature

**Answer: D**

**Solution.** At low pressure (low density) the molecules are far apart from one another; the volume of the molecules is negligible compared with the volume of the container. At high
temperature the kinetic energy of the molecules is large compared with the potential energy of the intermolecular forces. Together these best satisfy the
assumptions of the ideal gas.

| Option | Misconception |
|---|---|
| A | Only the temperature condition is right; it overlooks that at high pressure the volume of the molecules cannot be neglected |
| B | Both conditions are reversed; the state closest to liquefaction is thought to be "ideal" |
| C | Only the pressure condition is right; it overlooks that at low temperature the intermolecular forces become significant |

---

## Question 4 — Paper 1A

Containers X and Y hold different ideal gases at the same pressure. The density of the gas in X is four times the density of the
gas in Y.

What is the ratio (root mean square speed of the molecules in X) / (root mean square speed of the molecules in Y)?

A. 1⁄4
B. 1⁄2
C. 2
D. 4

**Answer: B**

**Solution.** *P* = ⅓ρ*v*² → *v* = √(3*P*/ρ). Since the pressure is the same, *v* ∝ 1/√ρ. Ratio = 1/√4 = 1⁄2.

| Option | Misconception |
|---|---|
| A | The square root is not taken (*v* ∝ 1/ρ): 1⁄4 |
| C | The proportion is set up the wrong way round (*v* ∝ √ρ): 2 |
| D | The proportion is both inverted and the square root is not taken (*v* ∝ ρ): 4 |

---

## Question 5 — Paper 2 (9 marks)

A rigid steel cylinder of volume 0.012 m³ contains helium at a pressure of 1.5 × 10⁷ Pa and a temperature of 17 °C. Helium is a
monatomic gas and is assumed to behave as an ideal gas.

Gas constant *R* = 8.31 J K⁻¹ mol⁻¹

**(a)** Show that the amount of helium in the cylinder is about 75 mol. [2]

The cylinder is left in sunlight and the temperature of the helium rises to 46 °C.

**(b)** Calculate the new pressure of the helium. [2]

**(c)** Explain, using the kinetic model of a gas, why the pressure of the helium increases. [2]

**(d)** Calculate the increase in the internal energy of the helium. [2]

**(e)** Suggest why the ideal gas model may **not** be accurate for the helium in this cylinder. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *T* = 290 «K» ✓<br>*n* = (1.5 × 10⁷ × 0.012) / (8.31 × 290) = 74.7 «mol» ✓ | *Answer 75 mol is given; award the second mark only if 74.7 or the complete substitution is seen.* | 2 |
| 5. | b | | *P*/*T* = constant **OR** *P*₂ = 1.5 × 10⁷ × 319 / 290 ✓<br>*P*₂ = 1.65 × 10⁷ «Pa» ✓ | *Allow use of PV = nRT with n = 75 mol (gives 1.66 × 10⁷ Pa).*<br>*Award [1 max] if Celsius temperatures are used (4.1 × 10⁷ Pa).* | 2 |
| 5. | c | | the average speed / kinetic energy of the atoms increases ✓<br>collisions with the walls are more frequent **OR** the change in momentum in each collision is greater ✓<br>so the «average» force on the walls increases «and the area is unchanged» ✓ | *OWTTE* | 2 max |
| 5. | d | | Δ*U* = 3⁄2 *nR*Δ*T* = 1.5 × 75 × 8.31 × 29 ✓<br>Δ*U* = 2.7 × 10⁴ «J» ✓ | *Allow ECF from (a) and (b).*<br>**ALTERNATIVE:** Δ*U* = 3⁄2 *V*Δ*P* = 1.5 × 0.012 × 1.5 × 10⁶ ✓ = 2.7 × 10⁴ «J» ✓ | 2 |
| 5. | e | | the pressure / density is high so the volume of the atoms is not negligible «compared with the volume of the cylinder» **OR** the atoms are close together so the forces between them are not negligible ✓ | *OWTTE*<br>*Do not accept "helium is a real gas" without a reason.* | 1 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `V = 0.012 m^3`, `P1 = 1.5e7 Pa`, `T1 = 290 K`, `T2 = 319 K`; constant `R = 8.31 J/(K mol)` | |
| `n` | `P1*V/(R*T1)` | 74.7 mol |
| `P2` | `P1*T2/T1` | 1.65 × 10⁷ Pa |
| `dU` | `1.5*n*R*(T2 - T1)` | 2.70 × 10⁴ J (2.71 × 10⁴ J with n = 75 mol) |

---

## Question 6 — Paper 1B (11 marks)

A student investigates how the pressure of a gas depends on its temperature. A sealed flask of air is connected by a short narrow
tube to a pressure gauge. The flask is fully immersed in a water bath. The student changes the temperature *θ* of the water, waits
several minutes and then records *θ* and the pressure *P* of the air.

> **Figure:** A glass flask fully immersed in a water bath, its neck closed with a stopper. A short, narrow tube leaving the stopper is connected to a pressure gauge
> above the water surface. The water contains a thermometer and a stirrer. The figure is not to scale.

| *θ* / °C ± 0.5 °C | *P* / kPa ± 1 kPa |
|---|---|
| 10.0 | 98 |
| 30.0 | 106 |
| 50.0 | 112 |
| 70.0 | 119 |
| 90.0 | 126 |

**(a)** State **one** quantity, other than those in the table, that must stay constant during the investigation. [1]

**(b)** Outline why the student waits several minutes before taking each pair of readings. [1]

The student plots a graph of *P* against *θ* with uncertainty bars for *P*. The uncertainty bars for *θ* are too small to draw.
The line of best fit has a gradient of 0.345 kPa °C⁻¹ and an intercept on the *P*-axis of 95.0 kPa.

**(c)** The student states that *P* is directly proportional to *θ*. Discuss, using the data, whether this statement is correct. [2]

**(d)** The line of best fit is extrapolated to *P* = 0. Determine the temperature *θ*₀, in °C, at which the line predicts that the
pressure is zero. [2]

The lines of maximum and minimum gradient that pass through all the uncertainty bars are (values rounded to four significant
figures):

| Line | Gradient / kPa °C⁻¹ | Intercept on *P*-axis / kPa |
|---|---|---|
| maximum gradient | 0.3667 | 94.00 |
| minimum gradient | 0.3250 | 95.75 |

**(e)** Determine the absolute uncertainty in *θ*₀. [2]

**(f)** The accepted value of absolute zero is −273 °C. Comment on whether the result of the experiment is consistent with this
value. [1]

**(g)** Suggest **one** change to the investigation that would reduce the uncertainty in *θ*₀. Give a reason for your answer. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | volume «of the air / flask» **OR** mass / amount / number of molecules of air ✓ | | 1 |
| 6. | b | | so that the air «in the flask» reaches the temperature of the water / thermal equilibrium ✓ | *OWTTE* | 1 |
| 6. | c | | the line does not pass through the origin / the intercept is 95 kPa, not zero **OR** *P*/*θ* is not constant, with two values calculated «e.g. 98 / 10 = 9.8 and 126 / 90 = 1.4» ✓<br>so the statement is not correct; the relationship is linear but not directly proportional «*P* is proportional to the kelvin temperature» ✓ | *The first mark requires reference to the data or the intercept.* | 2 |
| 6. | d | | 0 = 95.0 + 0.345 *θ*₀ **OR** *θ*₀ = −95.0 / 0.345 ✓<br>*θ*₀ = −275 «°C» ✓ | *Award [1 max] if the negative sign is missing.* | 2 |
| 6. | e | | *θ*₀ = −94.00 / 0.3667 = −256 «°C» **AND** *θ*₀ = −95.75 / 0.3250 = −295 «°C» ✓<br>uncertainty = (295 − 256) / 2 = «±» 19 «°C» ✓ | *Accept 20 °C.*<br>*Accept the difference between either value and the best-fit value (19 or 20 °C).* | 2 |
| 6. | f | | consistent, because −273 °C lies within the range of the result «−295 °C to −255 °C» ✓ | *Allow ECF from (d) and (e).*<br>*A conclusion without reference to the range does not gain the mark.* | 1 |
| 6. | g | | **ALTERNATIVE 1**<br>use a wider range of temperatures «e.g. include an ice bath or a freezing mixture» ✓<br>so that the extrapolation is shorter / the gradient is determined more precisely ✓<br>**ALTERNATIVE 2**<br>use a pressure gauge with a smaller uncertainty / better resolution ✓<br>so that the uncertainty bars are smaller and the range of possible lines is narrower ✓ | *OWTTE*<br>*The second mark is for a reason linked to the change.*<br>*Do not accept "repeat the readings" without a link to the uncertainty in P.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | data table; `dP = 1 kPa` | |
| `m_best`, `c_best` | least-squares line | 0.345 kPa °C⁻¹, 94.95 kPa |
| `theta0` | `-c_best/m_best` | −275.2 °C (−275.4 °C with the 95.0 given in the question) |
| `m_max`, `c_max` | steepest line passing through all the uncertainty bars | 0.3667 kPa °C⁻¹, 94.00 kPa |
| `m_min`, `c_min` | shallowest line passing through all the uncertainty bars | 0.325 kPa °C⁻¹, 95.75 kPa |
| `theta0_max` | `-c_max/m_max` | −256.4 °C (−256.3 °C with the 0.3667 given in the question) |
| `theta0_min` | `-c_min/m_min` | −294.6 °C |
| `d_theta0` | `(theta0_max - theta0_min)/2` | 19.1 °C ≈ 19 °C (20 °C to one significant figure) |

### Figure note

The version shown to the student includes, together with the table, a *P*–*θ* graph with uncertainty bars; the horizontal axis is extended to −300 °C so that extrapolation
can be carried out. The graph is generated by code from the same data (D-14). The steepest line passes through the bar ends (30 °C; 105 kPa) and
(90 °C; 127 kPa), the shallowest line through the bar ends (10 °C; 99 kPa) and (90 °C; 125 kPa); the gradient and
intercept values given in the question are these rounded to four significant figures. Result: *θ*₀ = (−275 ± 19) °C or (−280 ± 20) °C.

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence + A–D listed one under another | Questions 1, 2, 4 "What is …?"; Question 3 "Under which conditions …?" (rare "Which" form) |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1, 2, 4 conform (ascending); Question 3 has short verbal options with two variables |
| 1A: table-format options could not be confirmed | Question 3 was written with short options of the "… and …" pattern instead of a table |
| 1A: position of the correct answer balanced | A, C, D, B |
| 1A: solvable without a figure | Questions 1–4 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 2, 2, 1; total 9) |
| Paper 2: at least one AO3 part; "Show that" pattern | Question 5 conforms: (a) Show that, (c) Explain, (e) Suggest |
| Paper 2: negation word in bold | Question 5(e) ("not") conforms |
| Markscheme: four-column table, ✓, « », OR, AND, max, ECF, OWTTE | Questions 5 and 6 conform (Question 6 also in the four-column format) |
| 1B: experiment question of about 10 marks, sub-parts 1–3 marks | Question 6 conforms (1, 1, 2, 2, 2, 1, 2; total 11) |
| 1B: table heading "quantity / unit ± uncertainty" | Question 6 conforms; the text says which uncertainty bar is not drawn |
| 1B: apparatus diagram | Only a `> **Figure:**` description is present; no drawing was produced. The question can be solved without the figure |
| 1B: the student draws the line of best fit on the given graph and finds the gradient and intercept themselves | **Question 6 does not conform:** because the graph could not be generated, the gradient and intercept values are given in the text. Parts (d) and (e) must be rewritten when the graph template is ready |
| 1B: part structure (a), (i)–(iv) under (b) | Question 6 is only at the (a)–(g) level; sub-numbering was not used |
| Value–unit notation (kPa °C⁻¹), significant figures | Conforms; the gradient and intercept of the best-fit line are given to 3 significant figures, those of the steepest / shallowest lines to 4 (the extrapolation is sensitive to rounding; 3 figures exceeded the bar ends) |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver independent of its author, without seeing the answers; all answer keys and
markscheme results (including the data processing of Question 6) were reproduced independently (no CRITICAL or MEDIUM findings). Detail:
[review/b3-review.md](review/b3-review.md). This check does not replace expert review.

Changes made as a result of the review (every changed number was recalculated with `python3`):

- **Question 6 (e), LOW-2:** the values of the steepest / shallowest lines 0.367 / 94.0 and 0.325 / 95.8 were changed to 0.3667 / 94.00 and 0.3250 / 95.75;
  the note "values rounded to four significant figures" was added. The earlier values exceeded the bar ends by 0.03–0.05 kPa; with the new
  values the shallowest line fits the ends exactly and the steepest line exceeds them at 90 °C by only 0.003 kPa (the 0.36666… rounding).
  The *θ*₀ values changed from −256.1 / −294.8 °C to −256.3 / −294.6 °C; the half-range from 19.3 °C to 19.1 °C.
- **Question 6 (e), LOW-3:** the markscheme answer "20 «°C», accept 19 or 19.5" became "19 «°C», accept 20"; the note about the difference from
  the best-fit value was corrected to "19 or 20 °C". The formula chain and the figure note were updated accordingly.
- **Question 4, LOW-1 ("root mean square speed" term):** no change made; the review also finds the term physically correct and recommends
  keeping it until expert confirmation.
- **LOW-4 (gradient given in the text in 1B) and LOW-5 (9 marks in an SL short question):** no change made; the first cannot be resolved until the graph template
  is available and is already flagged in "Format conformance"; the second is a record awaiting expert confirmation.
