# Pilot question set: A.2 Forces and momentum

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written by hand according to the [authoring standard](AUTHORING_STANDARD.md) and with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node A.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam question, textbook question or internet source was used as input.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate calculation in `python3`
> (g = 9.8 m s⁻²; the data booklet value must be confirmed by an expert). The material values in Question 5 (densities of steel and glycerol, glycerol
> viscosity) are given in the question.
> **Not verified:** it passed an independent blind solver; it has not passed expert review; it has not been checked by an expert for resemblance
> to any known exam question; the material values in Question 5 (7800 kg m⁻³, 1260 kg m⁻³, 1.4 Pa s) were taken from general knowledge and not confirmed from a source;
> the way the volume formula of a sphere and Stokes' law are written in the data booklet was not checked.

## Scope table

| # | Section | Level | Outcome (A.2) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Static vs kinetic friction; friction force in equilibrium | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Impulse and change of momentum; F = Δp/Δt (1 dimension, reversal of direction) | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Centripetal force at the top of a vertical circle | AO2 | — | 1 | Medium |
| 4 | Paper 1A | SL | Conservation of momentum in an explosion; sharing of kinetic energy | AO3 | — | 1 | Medium–hard |
| 5 | Paper 2 | SL | Weight, buoyancy force and Stokes drag; force balance | AO2–AO3 | Show that, Calculate, Determine, Explain | 9 | Medium |

This set does not cover all of A.2. Missing: drawing free-body diagrams, resultant force on an inclined plane, tension, Hooke's
law, Newton's third law pairs, quantitative treatment of elastic and inelastic collisions (1 dimension), area under a force–time graph,
angular velocity and horizontal circular motion, the bottom of a vertical circle, non-uniform circular motion, 2-dimensional collisions
(HL only).

---

## Question 1 — Paper 1A

A crate of mass 12 kg is at rest on a horizontal warehouse floor. The coefficient of static friction between the crate and the floor
is 0.50 and the coefficient of dynamic friction is 0.40. A worker pushes the crate with a horizontal force of 40 N.

What is the magnitude of the friction force acting on the crate?

A. 40 N
B. 47 N
C. 59 N
D. 120 N

**Answer: A**

**Solution.** Normal force = 12 × 9.8 = 118 N. Maximum static friction = 0.50 × 118 = 59 N. The applied 40 N is smaller than this; the crate
stays at rest and the friction force equals the applied force: 40 N.

| Option | Misconception |
|---|---|
| B | Calculates kinetic friction as if the crate were sliding: 0.40 × 118 = 47 N |
| C | Thinks static friction is always at its maximum value: 0.50 × 118 = 59 N |
| D | Confuses the friction force with the normal force (weight): 12 × 9.8 = 118 N ≈ 120 N |

---

## Question 2 — Paper 1A

An ice-hockey puck of mass 0.16 kg slides without friction and hits the barrier at the edge of the rink at right angles with a speed
of 15 m s⁻¹. The puck rebounds along its original path with a speed of 10 m s⁻¹. The puck is in contact with the barrier for 0.020 s.

What is the magnitude of the average force exerted by the barrier on the puck?

A. 40 N
B. 80 N
C. 120 N
D. 200 N

**Answer: D**

**Solution.** The velocity reverses direction; magnitude of change of momentum = 0.16 × (15 + 10) = 4.0 kg m s⁻¹.
Average force = 4.0 / 0.020 = 200 N.

| Option | Misconception |
|---|---|
| A | Ignores that momentum is a vector and subtracts the speeds: 0.16 × (15 − 10) / 0.020 = 40 N |
| B | Takes only the rebound momentum: 0.16 × 10 / 0.020 = 80 N |
| C | Takes only the incoming momentum (assumes the puck stops): 0.16 × 15 / 0.020 = 120 N |

---

## Question 3 — Paper 1A

A toy car of mass 0.050 kg moves on the inside of a vertical circular track of radius 0.40 m. At the highest point of the track
the speed of the car is 3.2 m s⁻¹.

What is the magnitude of the force exerted by the track on the car at the highest point?

A. 0.49 N
B. 0.79 N
C. 1.3 N
D. 1.8 N

**Answer: B**

**Solution.** At the highest point the weight and the reaction force *N* of the track both point towards the centre (downwards): *N* + *mg* = *mv*²/*r*.
*mv*²/*r* = 0.050 × 3.2² / 0.40 = 1.28 N; *mg* = 0.49 N; *N* = 1.28 − 0.49 = 0.79 N.
(Since *v*² = 10.2 m² s⁻² > *gr* = 3.9 m² s⁻², the car stays in contact with the track.)

| Option | Misconception |
|---|---|
| A | Assumes the reaction force equals the weight (thinks of it as equilibrium): 0.050 × 9.8 = 0.49 N |
| C | Leaves out the weight; takes the reaction force to be the whole centripetal force: 1.28 N ≈ 1.3 N |
| D | Uses the relation for the lowest point (*N* = *mv*²/*r* + *mg*): 1.28 + 0.49 = 1.77 N ≈ 1.8 N |

---

## Question 4 — Paper 1A

Two trolleys X and Y are at rest on a frictionless horizontal track with a compressed spring between them. The mass of X is *m* and
the mass of Y is 3*m*. The spring is released and the trolleys move apart.

What is the ratio (kinetic energy of X) / (kinetic energy of Y) after the trolleys have separated?

A. 1/3
B. 1
C. 3
D. 9

**Answer: C**

**Solution.** The total momentum is initially zero; after separation the magnitudes of the momenta are equal (*p*). Since *E*<sub>k</sub> = *p*²/2*m*,
kinetic energy is inversely proportional to mass: ratio = 3*m* / *m* = 3. (Equivalent route: *v*<sub>X</sub> = 3*v*<sub>Y</sub>;
½*m*(3*v*)² / ½(3*m*)*v*² = 3.)

| Option | Misconception |
|---|---|
| A | Assumes the speeds are equal; takes kinetic energy as directly proportional to mass: *m* / 3*m* = 1/3 |
| B | Thinks it is the energy rather than the momentum that is "equal and opposite"; thinks the spring energy is shared equally |
| D | Finds the speed ratio (3) correctly but only squares it, forgetting the mass ratio: 3² = 9 |

---

## Question 5 — Paper 2 (9 marks)

A steel ball bearing of radius 2.0 mm is released in a tall cylinder of glycerol. After a short distance the ball falls at a constant
(terminal) speed.

The following data are available.

Density of steel = 7800 kg m⁻³
Density of glycerol = 1260 kg m⁻³
Viscosity of glycerol = 1.4 Pa s

**(a)** Show that the weight of the ball is about 2.6 × 10⁻³ N. [2]

**(b)** Calculate the buoyancy force acting on the ball. [2]

**(c)** Determine the terminal speed of the ball. [3]

The glycerol is now warmed. Its viscosity decreases and the change in its density is negligible.

**(d)** Explain the effect of warming the glycerol on the terminal speed of the ball. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *V* = <sup>4</sup>⁄<sub>3</sub> π × (2.0 × 10⁻³)³ «= 3.35 × 10⁻⁸ m³» ✓<br>*W* = 7800 × 3.35 × 10⁻⁸ × 9.8 = 2.56 × 10⁻³ «N» ✓ | *Answer must be shown to at least 3 s.f. or the full substitution must be seen.* | 2 |
| 5. | b | | *F*<sub>b</sub> = 1260 × 3.35 × 10⁻⁸ × 9.8 ✓<br>= 4.1 × 10⁻⁴ «N» ✓ | *Allow ECF for the volume from (a).* | 2 |
| 5. | c | | drag force = weight − buoyancy force «= 2.15 × 10⁻³ N» ✓<br>*v* = *F*<sub>d</sub> / (6π*ηr*) = 2.15 × 10⁻³ / (6π × 1.4 × 2.0 × 10⁻³) ✓<br>*v* = 0.041 «m s⁻¹» ✓ | *Allow ECF from (b).*<br>*Accept answers in the range 0.041 to 0.042 «m s⁻¹» (use of 2.6 × 10⁻³ N gives 0.041).*<br>*Award [2] max for 0.049 «m s⁻¹» (buoyancy force omitted).* | 3 |
| 5. | d | | weight and buoyancy force are unchanged, so the drag force at terminal speed is the same ✓<br>drag force is proportional to viscosity × speed, so a greater speed is needed **OR** terminal speed increases ✓ | *OWTTE*<br>*The second mark needs a reason linked to the drag force, not only the statement that the ball falls faster.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `r = 2.0e-3 m`, `rho_s = 7800 kg/m^3`, `rho_f = 1260 kg/m^3`, `eta = 1.4 Pa s`, constant `g = 9.8 m/s^2` | |
| `V` | `4/3*pi*r**3` | 3.35 × 10⁻⁸ m³ |
| `W` | `rho_s*V*g` | 2.56 × 10⁻³ N |
| `F_b` | `rho_f*V*g` | 4.14 × 10⁻⁴ N |
| `F_d` | `W - F_b` | 2.15 × 10⁻³ N |
| `v` | `F_d/(6*pi*eta*r)` | 0.0407 m s⁻¹ |

Check: Reynolds number ≈ `rho_f*v*2*r/eta` = 0.15 (≪ 1); in the flow regime where Stokes' law is valid. This check is not
asked of the student.

---

## Format conformance

Questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?") + A–D one below the other | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–3 conform (ascending, N); Question 4 is a unitless ratio, ascending |
| 1A: balanced position of the correct answer | A, D, B, C |
| 1A: negative stem | Not used |
| 1A: one- or two-step calculation | Questions 1–3 two steps; Question 4 algebraic reasoning, does not need simultaneous equations |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 3, 2; total 9). Note: in the SL sample paper short questions of 4–6 marks were observed; 9 marks is the upper end of the HL range and long for an SL short question; expert confirmation is needed |
| Paper 2: "Show that" pattern; a later part may use the given value | Question 5 (a) conforms; an acceptance range is given for (c) |
| Markscheme: four-column table, ✓, « », OR, ECF, OWTTE | Question 5 conforms |
| Value–unit notation (m s⁻¹, kg m⁻³), 2 significant figures | Conforms; in Question 1 option D was rounded to 2 significant figures (118 → 120 N) |
| Figure | No question needs a figure; Questions 3 and 5 could be supported with a figure in the student version |
| Scope limits (A.2) | 1 dimension; no simultaneous equations in collisions; only the top point in vertical circles; no banked bends |

## Independent check

Date: 2026-10-11. The blind solver solved the questions without seeing the answers and independently reproduced all answer keys and markscheme results; no CRITICAL or MEDIUM findings.
Details: [review/a2-review.md](review/a2-review.md). This check does not replace expert review.

Changes made in response to the findings:

- Question 5 (c) markscheme note: "gives 0.0415" → "gives 0.041" (0.0414 with the unrounded buoyancy force; recalculated with `python3`). The acceptance range did not change.
- A note was added to the "Format conformance" table that 9 marks is long for an SL short question and needs expert confirmation (same statement as in A.3).
- Question 1 option D (118 → 120 N): no change was requested in the review; left as it is.
