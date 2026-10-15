# Pilot question set: A.4 Rigid body mechanics

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written by hand according to the [authoring standard](AUTHORING_STANDARD.md) and with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
> A.4 is an HL-only node; all questions are labelled HL and do not enter the SL pool.
>
> **Source:** only syllabus node A.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam question, textbook question or internet source was used as input.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate calculation in `python3`
> (g = 9.8 m s⁻²; the data booklet value must be confirmed by an expert). The moment of inertia formulas of specific shapes are given in the question.
> **Not verified:** it passed an independent blind solver; it has not passed expert review; it has not been checked by an expert for resemblance
> to any known exam question; in Question 5 the condition on the coefficient of friction needed for the pipe to roll without slipping was given in the question as an assumption and was not
> tested separately; that the weight of the uniform beam in Question 1 acting at its midpoint is consistent with the "no centre of mass calculation" limit
> is the author's interpretation.

## Scope table

| # | Section | Level | Outcome (A.4) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Torque and rotational equilibrium | AO2 | — | 1 | Medium |
| 2 | Paper 1A | HL | *τ* = *Iα* and the equations of constant angular acceleration | AO2 | — | 1 | Medium |
| 3 | Paper 1A | HL | Conservation of angular momentum; *mr*² for a point mass | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Sharing of translational and rotational kinetic energy in rolling without slipping | AO3 | — | 1 | Medium–hard |
| 5 | Paper 2 | HL | Rolling without slipping; conservation of energy; angular momentum; effect of moment of inertia on motion | AO1–AO3 | State, Show that, Calculate, Explain | 9 | Medium–hard |

This set does not cover all of A.4. Missing: angular impulse (area under a torque–time graph), finding angular displacement with the equations of constant
angular acceleration, calculating Σ*mr*² for several point masses, applying translational and rotational equilibrium together
(hinge force), change of rotational kinetic energy while angular momentum is conserved, torque of a force applied at an angle (*Fr* sin *θ*).

---

## Question 1 — Paper 1A

A uniform horizontal beam of length 3.0 m and weight 200 N is hinged to a wall at one end. The beam is held horizontal by a vertical
cable attached to the beam at a distance of 2.0 m from the hinge. A lamp of weight 150 N hangs from the free end of the beam.

> **Figure:** On the left a vertical wall; a horizontal 3.0 m beam hinged to the wall and extending to the right. A vertical cable rising from the beam
> at 2.0 m from the hinge. A lamp hanging from the right (free) end of the beam. *Diagram not to scale.*

What is the tension in the cable?

A. 225 N
B. 350 N
C. 375 N
D. 525 N

**Answer: C**

**Solution.** Torque balance about the hinge: *T* × 2.0 = 200 × 1.5 + 150 × 3.0 = 750 N m; *T* = 375 N.
(The hinge exerts a downward force of 25 N on the beam; the torque of this force about the hinge is zero.)

| Option | Misconception |
|---|---|
| A | Leaves out the weight of the beam itself: 150 × 3.0 / 2.0 = 225 N |
| B | Writes only the vertical force balance instead of the torque balance, ignoring the hinge force: 200 + 150 = 350 N |
| D | Assumes the weight of the beam acts at the free end instead of the midpoint: (200 × 3.0 + 150 × 3.0) / 2.0 = 525 N |

---

## Question 2 — Paper 1A

A flywheel is a uniform solid disc of mass 8.0 kg and radius 0.25 m that can rotate about a fixed frictionless axle through its
centre. The moment of inertia of the disc about the axle is ½*MR*². The flywheel is at rest. A constant force of 6.0 N is then applied
tangentially at the rim of the disc.

What is the angular speed of the flywheel after 5.0 s?

A. 15 rad s⁻¹
B. 30 rad s⁻¹
C. 60 rad s⁻¹
D. 120 rad s⁻¹

**Answer: B**

**Solution.** *I* = ½ × 8.0 × 0.25² = 0.25 kg m². *τ* = *FR* = 6.0 × 0.25 = 1.5 N m. *α* = *τ*/*I* = 6.0 rad s⁻².
*ω* = *αt* = 6.0 × 5.0 = 30 rad s⁻¹.

| Option | Misconception |
|---|---|
| A | Skips the given factor ½ and takes *I* = *MR*² = 0.50 kg m²: *α* = 3.0 rad s⁻², *ω* = 15 rad s⁻¹ |
| C | Takes the diameter instead of the radius as the perpendicular distance from the axis to the force: *τ* = 6.0 × 0.50 = 3.0 N m, *α* = 12 rad s⁻², *ω* = 60 rad s⁻¹ |
| D | Uses the force itself instead of the torque (*α* = *F*/*I*): 6.0 / 0.25 = 24, × 5.0 = 120 |

---

## Question 3 — Paper 1A

A horizontal turntable rotates freely about a vertical axis with an angular speed of 3.0 rad s⁻¹. The moment of inertia of the
turntable about the axis is 0.80 kg m². A small lump of clay of mass 2.0 kg is dropped vertically onto the turntable and sticks to it
at a distance of 0.50 m from the axis.

What is the angular speed of the turntable after the clay has stuck to it?

A. 1.8 rad s⁻¹
B. 2.4 rad s⁻¹
C. 3.0 rad s⁻¹
D. 4.9 rad s⁻¹

**Answer: A**

**Solution.** Because the clay falls vertically, it has no angular momentum about the axis; as there is no external torque, the angular momentum of the system is conserved.
New moment of inertia = 0.80 + 2.0 × 0.50² = 1.30 kg m². *ω* = 0.80 × 3.0 / 1.30 = 1.8 rad s⁻¹.

| Option | Misconception |
|---|---|
| B | Assumes rotational kinetic energy is conserved instead of angular momentum: 3.0 × √(0.80 / 1.30) = 2.4 rad s⁻¹ |
| C | Thinks the vertically falling clay does not affect the rotation; the angular speed does not change |
| D | Inverts the ratio of the moments of inertia: 3.0 × 1.30 / 0.80 = 4.9 rad s⁻¹ |

---

## Question 4 — Paper 1A

A uniform solid sphere of mass *M* and radius *R* rolls without slipping along a horizontal surface. The moment of inertia of the
sphere about an axis through its centre is ⅖*MR*².

What is the ratio (translational kinetic energy of the sphere) / (total kinetic energy of the sphere)?

A. 2/7
B. 2/5
C. 1/2
D. 5/7

**Answer: D**

**Solution.** In rolling without slipping *ω* = *v*/*R*. Rotational kinetic energy = ½ × ⅖*MR*² × (*v*/*R*)² = ⅕*Mv*². Translational kinetic energy
= ½*Mv*². Total = 7/10 *Mv*². Ratio = (1/2) / (7/10) = 5/7.

| Option | Misconception |
|---|---|
| A | Gives the share of rotational kinetic energy instead of the requested ratio: (1/5) / (7/10) = 2/7 |
| B | Takes the coefficient in the moment of inertia to be the energy ratio directly: 2/5 |
| C | Assumes energy is always shared equally between translation and rotation: 1/2 |

---

## Question 5 — Paper 2 (9 marks)

A thin-walled steel pipe of mass 12 kg and radius 0.15 m is released from rest at the top of a loading ramp. The pipe rolls without
slipping down the ramp. The centre of the pipe falls through a vertical height of 0.90 m. The moment of inertia of the pipe about its
central axis is *MR*². Air resistance is negligible.

**(a)** State the relationship between the linear speed *v* of the centre of the pipe and its angular speed *ω* when the pipe rolls
without slipping. [1]

**(b)** Show that the speed of the centre of the pipe at the bottom of the ramp is about 3.0 m s⁻¹. [3]

**(c)** Calculate the angular momentum of the pipe about its central axis at the bottom of the ramp. [2]

A uniform solid cylinder has the same mass and the same radius as the pipe. Its moment of inertia about its central axis is ½*MR*².
The cylinder is released from rest at the top of the same ramp and also rolls without slipping.

**(d)** Explain, without calculation, whether the cylinder takes a longer or a shorter time than the pipe to reach the bottom of
the ramp. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *v* = *ωR* ✓ | *Accept ω = v / R or the relation in words.* | 1 |
| 5. | b | | *Mgh* = ½*Mv*² + ½*Iω*² ✓<br>use of *I* = *MR*² **AND** *ω* = *v*/*R* to get *Mgh* = *Mv*² **OR** *v* = √(*gh*) ✓<br>*v* = √(9.8 × 0.90) = 2.97 «m s⁻¹» ✓ | *Third mark needs an answer to at least 3 s.f. (2.97) from a correct substitution.*<br>*Award [1] max for v = √(2gh) = 4.2 «m s⁻¹» (rotation ignored).* | 3 |
| 5. | c | | *ω* = 3.0 / 0.15 «= 20 rad s⁻¹» **OR** *L* = *Iω* = *MRv* ✓<br>*L* = 12 × 0.15² × 20 = 5.4 «kg m² s⁻¹» ✓ | *Accept answers in the range 5.3 to 5.4 «kg m² s⁻¹» (use of 2.97 m s⁻¹ gives 5.35).*<br>*Accept the unit N m s.* | 2 |
| 5. | d | | both lose the same gravitational potential energy / have the same total kinetic energy «at any given height» ✓<br>the cylinder has a smaller moment of inertia so a smaller fraction of its kinetic energy is rotational / a greater fraction is translational ✓<br>the cylinder has a greater linear speed «at every point on the ramp» so it takes a shorter time ✓ | *OWTTE*<br>*Do not award the third mark for "shorter time" without a reason.*<br>*Accept an argument using a greater linear acceleration for the cylinder for the third mark.*<br>*Accept a correct algebraic comparison of the speeds.* | 3 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `M = 12 kg`, `R = 0.15 m`, `h = 0.90 m`, `k = 1` (`I = k*M*R**2`), constant `g = 9.8 m/s^2` | |
| `v` | `sqrt(2*g*h/(1 + k))` | 2.97 m s⁻¹ |
| `omega` | `v/R` | 19.8 rad s⁻¹ |
| `I` | `k*M*R**2` | 0.270 kg m² |
| `L` | `I*omega` | 5.35 kg m² s⁻¹ |

The same chain with the "Show that" value (3.0 m s⁻¹): `omega` = 20 rad s⁻¹, `L` = 5.40 kg m² s⁻¹. Check for (d) (not asked of the student): for the solid
cylinder, `k = 0.5`, `v` = 3.43 m s⁻¹ > 2.97 m s⁻¹.

---

## Format conformance

Questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + (figure) + separate single question sentence ("What is …?") + A–D one below the other | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–3 conform (ascending; N, rad s⁻¹); Question 4 is a fraction, ascending |
| 1A: balanced position of the correct answer | C, B, A, D |
| 1A: negative stem | Not used |
| 1A: stem length | Questions 1–3 about 50–60 words; within the profile range (8–90), above the median |
| Figure | Question 1 is described in text; the question can be solved without the figure. A figure must be generated for the student version |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (1, 3, 2, 3; total 9) |
| Paper 2: "Show that" pattern; a later part uses the given value | Question 5 (b) → (c) conforms; an acceptance range is given for (c) |
| Markscheme: four-column table, ✓, « », OR, AND, OWTTE | Question 5 conforms |
| Value–unit notation (rad s⁻¹, kg m² s⁻¹), 2 significant figures | Conforms; in Question 1 the data and options are given to 3 significant figures (200 N, 150 N, 375 N) |
| Scope limits (A.4) | The *I* formulas of specific shapes are given in Questions 2, 4, 5; in Question 3 the *I* value of the turntable is given numerically, the clay is a point mass; rotation + translation only in rolling without slipping; no vector operations or centre of mass calculation |

## Independent check

Date: 2026-10-11. The blind solver solved the questions without seeing the answers and independently reproduced all answer keys and markscheme results; no CRITICAL or MEDIUM findings.
Details: [review/a4-review.md](review/a4-review.md). This check does not replace expert review.

Changes made in response to the findings:

- Question 5 (b) markscheme: the "/" separating the two alternatives could be read as a division sign; rewritten as "*Mgh* = *Mv*² **OR** *v* = √(*gh*)".
- Question 5 (b): target value "about 3 m s⁻¹" → "about 3.0 m s⁻¹"; the note became "at least 3 significant figures (2.97)". The values in (c) were recalculated: 5.35 with 2.97, 5.40 kg m² s⁻¹ with 3.0; the acceptance range did not change.
- "Accept a correct algebraic comparison of the speeds" was added to the Question 5 (d) markscheme note.
- Significant figures of Question 1 (200 N, 150 N, 375 N): no change was requested in the review; left as it is.
