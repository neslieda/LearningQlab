# Pilot question set: C.1 Simple harmonic motion

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written to the [authoring standard](AUTHORING_STANDARD.md), with the same structure as the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node C.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook or internet question was used as input; the scenarios are original.
> **Numerical check:** all numerical answers and all numerical distractors were recomputed with `python3` (standard library only);
> the gradients in Question 7 were computed from the data in the table. g = 9.8 m s⁻² was used (the data booklet value should be confirmed by an expert).
> **Not verified:** (1) it was solved by an independent blind solver; it has not been through expert review; (2) it has not been
> checked by an expert for similarity to a known exam question; (3) the wording of the SHM equations in the data booklet (x = x₀ sin(ωt + φ)) was not confirmed from the booklet, so in Question 5 the
> equation is given in the question; (4) qualitative questions (Question 3, Question 6 d–e, Question 7 a and d) cannot be verified by code; (5) the graph of Question 7 was not
> generated.

## Scope table

| # | Section | Level | Outcome (C.1) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Period of a mass–spring system; T ∝ √m | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | a = −ω²x; relation between frequency and angular frequency | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Qualitative description of energy changes (timing of the kinetic–potential conversion) | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | v = ±ω√(x₀² − x²) | AO2 | — | 1 | Medium |
| 5 | Paper 1A | HL | Phase angle; x = x₀ sin(ωt + φ) | AO3 | — | 1 | Hard |
| 6 | Paper 2 | SL | Conditions for SHM; period of a simple pendulum; a = −ω²x; qualitative energy; small-angle limit | AO1–AO3 | State, Show that, Calculate, Describe, Suggest | 9 | Medium |
| 7 | Paper 1B | SL | Processing mass–spring period data; uncertainty; linearization; systematic error | AO2–AO3 | State, Calculate, Determine, Suggest, Explain | 10 | Medium–hard |

This set does not cover all of C.1. Not covered: interpretation of displacement–time and acceleration–displacement graphs; the velocity equation
v = ωx₀ cos(ωt + φ); quantitative calculation of total and potential energy (HL); the dependence of pendulum period on g; the phase difference between two oscillators.

---

## Question 1 — Paper 1A

A block of mass 0.20 kg hangs from a light vertical spring and oscillates with a period of 0.60 s. The block is replaced by a
block of mass 0.80 kg on the same spring.

What is the period of oscillation of the 0.80 kg block?

A. 0.30 s
B. 0.60 s
C. 1.2 s
D. 2.4 s

**Answer: C**

**Solution.** T = 2π√(m/k), so T ∝ √m. The mass increases by a factor of 4; the period increases by a factor of √4 = 2: 2 × 0.60 = 1.2 s.

| Option | Misconception |
|---|---|
| A | Inverts the proportionality (T ∝ 1/√m): 0.60 / 2 = 0.30 s |
| B | Assumes the period is independent of mass (confusion with the simple pendulum): 0.60 s |
| D | Forgets the square root (T ∝ m): 0.60 × 4 = 2.4 s |

---

## Question 2 — Paper 1A

A buoy floating on the sea moves vertically with simple harmonic motion of frequency 0.50 Hz and amplitude 0.40 m.

What is the magnitude of the acceleration of the buoy when its displacement from the equilibrium position is 0.20 m?

A. 0.63 m s⁻²
B. 2.0 m s⁻²
C. 3.9 m s⁻²
D. 32 m s⁻²

**Answer: B**

**Solution.** ω = 2πf = 2π × 0.50 = 3.14 rad s⁻¹. |a| = ω²x = 3.14² × 0.20 = 1.97 ≈ 2.0 m s⁻².

| Option | Misconception |
|---|---|
| A | Does not square ω: ωx = 3.14 × 0.20 = 0.63 |
| C | Uses the amplitude instead of the displacement (the maximum acceleration): 3.14² × 0.40 = 3.9 |
| D | Takes 0.50 to be the period: ω = 2π / 0.50 = 12.6 rad s⁻¹; 12.6² × 0.20 = 31.6 ≈ 32 |

---

## Question 3 — Paper 1A

A trolley attached to a horizontal spring oscillates on a frictionless track with simple harmonic motion of period *T*.

What is the shortest time between an instant when the kinetic energy of the trolley is a maximum and an instant when the elastic
potential energy of the spring is a maximum?

A. *T*/4
B. *T*/2
C. *T*
D. 2*T*

**Answer: A**

**Solution.** Kinetic energy is greatest at the equilibrium position, and potential energy is greatest at the largest displacement. Moving from the equilibrium position to an extreme
takes a quarter of a period: T/4.

| Option | Misconception |
|---|---|
| B | Takes the time to go from one extreme to the other (this is the time between two successive maximum values of the potential energy) |
| C | Assumes the energy conversion has the same period as the displacement and that the conversion takes a full period |
| D | Assumes the period of the energy is twice the period of the motion (it is actually half) |

---

## Question 4 — Paper 1A

A particle moves with simple harmonic motion of amplitude 0.10 m. The maximum speed of the particle is 2.0 m s⁻¹.

What is the speed of the particle when its displacement from the equilibrium position is 0.060 m?

A. 0.80 m s⁻¹
B. 1.2 m s⁻¹
C. 1.3 m s⁻¹
D. 1.6 m s⁻¹

**Answer: D**

**Solution.** v<sub>max</sub> = ωx₀ → ω = 2.0 / 0.10 = 20 rad s⁻¹. v = ω√(x₀² − x²) = 20 × √(0.10² − 0.060²) = 20 × 0.080 = 1.6 m s⁻¹.

| Option | Misconception |
|---|---|
| A | Assumes the speed decreases linearly with displacement: 2.0 × (1 − 0.60) = 0.80 |
| B | Takes the speed to be directly proportional to displacement (confusion with acceleration): 2.0 × 0.60 = 1.2 |
| C | Does not square the terms: 2.0 × √(1 − 0.60) = 1.26 ≈ 1.3 |

---

## Question 5 — Paper 1A

The displacement *x* of a particle that moves with simple harmonic motion is given by *x* = *x*₀ sin(*ωt* + *φ*), where *x*₀ is the
amplitude. At time *t* = 0 the displacement of the particle is +*x*₀/2 and the particle is moving in the positive direction.

What is the phase angle *φ*?

A. π/6 rad
B. π/3 rad
C. 2π/3 rad
D. 5π/6 rad

**Answer: A**

**Solution.** At t = 0, sin φ = 0.50 → φ = π/6 or 5π/6. The velocity is proportional to ωx₀ cos φ; for motion in the positive direction cos φ > 0 is required.
This is satisfied only for φ = π/6 (cos(5π/6) < 0).

| Option | Misconception |
|---|---|
| B | Uses cosine instead of sine: cos φ = 0.50 → φ = π/3 (sin(π/3) = 0.87, does not satisfy the displacement condition) |
| C | Builds on the error in B by taking π − π/3 for the direction (sin(2π/3) = 0.87, does not satisfy the displacement condition) |
| D | Satisfies the displacement condition (sin(5π/6) = 0.50) but does not check the direction of motion; at this phase the particle moves in the negative direction |

---

## Question 6 — Paper 2 (9 marks)

A lamp of mass 1.5 kg hangs from the ceiling of a hall on a long light cable. The lamp is pulled a small distance to one side and
released. The lamp then swings and the time for 10 complete oscillations is 49 s. The lamp can be modelled as a simple pendulum.

**(a)** State, in terms of the acceleration of the lamp, the **two** conditions for its motion to be simple harmonic. [2]

**(b)** Show that the length of the pendulum is about 6 m. [2]

The amplitude of the oscillations is 0.30 m.

**(c)** Calculate the maximum acceleration of the lamp. [2]

**(d)** Describe the energy changes of the lamp as it moves from one extreme position to the other extreme position. Air resistance
is negligible. [2]

**(e)** The lamp is now released with an amplitude of 3.0 m. Suggest why the motion is no longer simple harmonic. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | acceleration / restoring force is proportional to the displacement «from the equilibrium position» ✓<br>acceleration / restoring force is directed towards the equilibrium position **OR** is opposite to the displacement ✓ | *Accept* a = −ω²x *only if the symbols are defined, for both marks.* | 2 |
| 6. | b | | *T* = 4.9 «s» ✓<br>*L* = 9.8 × 4.9² / 4π² **OR** 5.96 «m» ✓ | *Answer must be seen to at least 2 s.f. or the substitution must be shown.* | 2 |
| 6. | c | | *ω* = 2π / 4.9 «= 1.28 rad s⁻¹» ✓<br>*a* = 1.28² × 0.30 = 0.49 «m s⁻²» ✓ | *Allow ECF from an incorrect T in (b).*<br>*Allow* a = gx₀ / L *with L = 6 m, giving 0.49.* | 2 |
| 6. | d | | «gravitational» potential energy is transferred to kinetic energy as the lamp moves to the equilibrium position / lowest point ✓<br>kinetic energy is transferred back to «gravitational» potential energy **AND** the total energy is constant ✓ | *OWTTE* | 2 |
| 6. | e | | the restoring force / acceleration is not proportional to the displacement «for a large angle» ✓ | *Accept "the small-angle approximation is no longer valid".*<br>*OWTTE* | 1 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `t10 = 49 s`, `N = 10`, `x0 = 0.30 m`, constant `g = 9.8 m/s^2` | |
| `T` | `t10/N` | 4.90 s |
| `L` | `g*T**2/(4*pi**2)` | 5.96 m |
| `omega` | `2*pi/T` | 1.28 rad s⁻¹ |
| `a_max` | `omega**2*x0` | 0.493 m s⁻² |
| Check (not asked in the question) | `asin(x0/L)` and `asin(3.0/L)` | 2.9° and 30° |

The mass (1.5 kg) is not used in any calculation; it is deliberately given as extra information (testing the ability to choose the formula).

---

## Question 7 — Paper 1B (10 marks)

A student investigates how the period of oscillation of a load on a vertical spring depends on the mass of the load. Slotted
masses are placed on a hanger that is attached to the lower end of the spring. For each total mass *m* of slotted masses, the load
is displaced vertically and released, and the time *t* for 10 complete oscillations is measured with a stopwatch.

> **Figure:** A vertical spring attached to a support rod; a hanger at the lower end of the spring with slotted masses on it; beside it a vertical ruler
> and a mark showing the equilibrium position. "diagram not to scale".

| *m* / kg | *t* / s ± 0.2 s |
|---|---|
| 0.100 | 4.9 |
| 0.200 | 6.3 |
| 0.300 | 7.4 |
| 0.400 | 8.4 |
| 0.500 | 9.3 |

The uncertainty in *m* is negligible. The period of oscillation is *T*.

**(a)** State **one** reason why the student measures the time for 10 oscillations rather than the time for one oscillation. [1]

**(b)** (i) State the absolute uncertainty in *T*. [1]

 (ii) Calculate the percentage uncertainty in *T*² for *m* = 0.100 kg. [2]

The student expects that *T* = 2π√(*m*/*k*), where *k* is the spring constant. The student plots a graph of *T*² against *m* with
uncertainty bars. The gradient of the line of best fit is 1.56 s² kg⁻¹. The lines of maximum and minimum gradient have gradients of
1.70 s² kg⁻¹ and 1.42 s² kg⁻¹.

**(c)** Determine the spring constant *k*, with its absolute uncertainty. [3]

The line of best fit is straight but does **not** pass through the origin. Its intercept on the *T*² axis is +0.08 s².

**(d)** (i) Suggest a reason for the intercept. [1]

 (ii) Explain whether the intercept affects the value of *k* determined in (c). [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 7. | a | | the percentage / fractional uncertainty in *T* is reduced **OR** the «reaction time» uncertainty is shared between 10 oscillations ✓ | *OWTTE*<br>*Do not accept "more accurate" without reference to uncertainty.* | 1 |
| 7. | b | i | «±» 0.02 «s» ✓ | | 1 |
| 7. | b | ii | fractional uncertainty in *T* = 0.2 / 4.9 **OR** 0.02 / 0.49 «= 0.041» ✓<br>percentage uncertainty in *T*² = 2 × 4.1 = 8 «%» ✓ | *Allow ECF from (b)(i).*<br>*Accept 8.2 %.* | 2 |
| 7. | c | | *k* = 4π² / gradient = 4π² / 1.56 «= 25.3 N m⁻¹» ✓<br>uncertainty in gradient = (1.70 − 1.42) / 2 = 0.14 «s² kg⁻¹» **OR** 9 % ✓<br>*k* = (25 ± 2) «N m⁻¹» ✓ | *Accept the range method:* 4π²/1.42 = 27.8 *and* 4π²/1.70 = 23.2, *giving the half-range* (27.8 − 23.2)/2 = *± 2.3.*<br>*Third mark requires the uncertainty to 1 s.f. and a consistent number of decimal places.* | 3 |
| 7. | d | i | the mass of the hanger / of the spring also oscillates but is not included in *m* ✓ | *Accept "there is a constant extra mass" OWTTE.* | 1 |
| 7. | d | ii | the extra mass is constant / is a systematic error, so every point is shifted by the same amount «along the *m* axis» ✓<br>the gradient is unchanged, so *k* is not affected ✓ | *OWTTE*<br>*Second mark requires the reference to the gradient.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `dt = 0.2 s`, `N = 10`, `t(0.100 kg) = 4.9 s`, `grad = 1.56`, `grad_max = 1.70`, `grad_min = 1.42` (s² kg⁻¹) | |
| `dT` | `dt/N` | 0.02 s |
| `pct_T2` | `2*dt/t*100` | 8.2 % |
| `k` | `4*pi**2/grad` | 25.3 N m⁻¹ |
| `d_grad` | `(grad_max - grad_min)/2` | 0.14 s² kg⁻¹ (9.0 %) |
| `dk` | `k*d_grad/grad` | 2.3 N m⁻¹ |
| Range check | `4*pi**2/grad_min`, `4*pi**2/grad_max` | 27.8 and 23.2 N m⁻¹; half-range (27.8 − 23.2)/2 = 2.3 N m⁻¹ |

### Figure note

The version shown to the student includes, together with the table, a *T*²–*m* graph with uncertainty bars; the graph is generated by code from the same data.
Values calculated from the data in the table: *T*² = 0.240, 0.397, 0.548, 0.706, 0.865 s²; the *T*² uncertainties (2*T*Δ*T*) are 0.020–0.037 s²;
the least-squares gradient is 1.558 s² kg⁻¹, the intercept 0.084 s²; the gradients of the lines through the ends of the uncertainty bars are 1.704 and
1.420 s² kg⁻¹. The values 1.56, 1.70, 1.42 and 0.08 given in the question are rounded versions of these. The data were generated with *k* = 25 N m⁻¹ and a constant extra mass
of 0.050 kg (the hanger) that is not written in the table, and rounded to 0.1 s; the intercept / gradient = 0.054 kg is consistent with this.

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one below the other | Questions 1–5 conform |
| 1A: four options of the same type, same unit, in order of magnitude | Questions 1–5 conform (ascending) |
| 1A: correct-answer letters balanced | C, B, A, D, A |
| 1A: solvable without a figure | Questions 1–5 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 6 conforms (2, 2, 2, 2, 1; total 9). On an SL paper short questions of 4–6 marks were observed; 9 marks is the top of the HL range — for an SL paper (d) or (e) can be removed |
| Paper 2: "Show that" pattern and at least one AO3 part | Question 6 (b) Show that, (e) Suggest |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE | Questions 6 and 7 conform |
| 1B: experiment question of about 10 marks, sub-parts 1–3 marks | Question 7 conforms (1, 1, 2, 3, 1, 2; total 10) |
| 1B: table header "quantity / unit ± uncertainty" | Question 7 conforms |
| 1B: student draws the best-fit line on a given graph and finds the gradient themselves | **Question 7 does not conform:** because the graph was not generated, the gradients and intercept are given in the text. When the graph template is ready, (c) and (d) must be rewritten |
| 1B: apparatus diagram | **Missing:** only described in words (`> **Figure:**`) |
| Syllabus limit: in SL energy is qualitative; phase angle in radians; no derivatives/integrals | Question 3 and 6(d) are qualitative; Question 5 uses radians; the velocity expression is derivative-free, used as a data booklet relation |
| Level label | Questions 4 and 5 HL (additional HL content); the others SL |
| Value–unit notation (m s⁻¹), 2 significant figures | Conforms |

## Independent check

Date: 2026-10-11. This file was solved by an independent blind solver who did not see the answers; the solver independently reproduced all answer
keys and markscheme results (no CRITICAL findings). Findings:
[review/c1-review.md](review/c1-review.md). This does not replace expert review.

Changes made in response to the findings (every changed number was rechecked with `python3` against the final text of the file):

- **Question 6 (a) (MEDIUM):** the stem was rewritten to ask only for the defining conditions ("State, in terms of the acceleration of the lamp, …"). The markscheme is unchanged.
- **Question 6 (LOW):** a note was added to the "Format conformance" table that 9 marks is long for an SL short question.
- **Question 7 (c) (LOW):** the markscheme note and the formula chain now state that ± 2.3 is the half-range, (27.8 − 23.2)/2.
- **Not applied:** replacing distractor D of Question 3 (2*T*) with 3*T*/4. The review lists it as "doubtful"; 3*T*/4 is not based on a specific misconception and, because it suggests the same physical situation (equilibrium to extreme) as *T*/4, was judged weaker. Left to the expert's decision.
