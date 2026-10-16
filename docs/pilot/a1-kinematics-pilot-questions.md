# Pilot question set: A.1 Kinematics

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set is a hand-made trial of the approach of generating original questions from the syllabus analysis ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)).
> When the product pipeline is ready, the same work goes through the steps Blueprint → generation → code check → blind solve → review.
>
> **Source:** only syllabus node A.1 and general physics. No exam question was used as input.
> **Numerical check:** all results were reproduced with a separate calculation (g = 9.8 m s⁻² was used; the data booklet value must be confirmed by an expert).
> **Independent check:** all five questions were solved by a blind solver other than the author, without seeing the answers; the keys, distractor
> calculations and markscheme values matched ([review/recheck-2026-10-11.md](review/recheck-2026-10-11.md)).
> **Not verified:** it has not passed expert review; it has not been checked by an expert for resemblance to any known exam question.

## Scope table

| # | Section | Level | Outcome (A.1) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Distance vs displacement; average velocity | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Solving projectile motion launched below the horizontal using components | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Qualitative effect of fluid resistance on acceleration | AO2 | — | 1 | Medium |
| 4 | Paper 2 | SL | Horizontal projection; velocity components; qualitative effect of resistive motion | AO1–AO3 | State, Calculate, Determine, Explain | 9 | Medium |
| 5 | Paper 1B | SL | Processing free-fall data; uncertainty; systematic error | AO2–AO3 | Outline, Calculate, Determine, Explain | 10 | Medium–hard |

This set does not cover all of A.1. Missing: determining instantaneous velocity from a graph, interpreting graphs of motion with variable acceleration, projectile motion launched
above the horizontal, terminal speed.

---

## Question 1 — Paper 1A

A cyclist rides 600 m due east in 60 s and then 800 m due north in 140 s.

What is the magnitude of the average velocity of the cyclist for the whole journey?

A. 5.0 m s⁻¹
B. 7.0 m s⁻¹
C. 7.9 m s⁻¹
D. 10 m s⁻¹

**Answer: A**

**Solution.** Displacement = √(600² + 800²) = 1000 m. Total time = 200 s. Magnitude of average velocity = 1000 / 200 = 5.0 m s⁻¹.

| Option | Misconception |
|---|---|
| B | Uses total distance instead of displacement: 1400 / 200 (average speed) |
| C | Takes the arithmetic mean of the speeds of the two stages (10 and 5.7 m s⁻¹) |
| D | Takes only the speed of the first stage |

---

## Question 2 — Paper 1A

A stone is thrown from the top of a vertical cliff with a speed of 12 m s⁻¹ at an angle of 30° **below** the horizontal. The stone
is released 15 m above the sea. Air resistance is negligible.

What is the horizontal distance from the base of the cliff to the point where the stone hits the sea?

A. 13 m
B. 15 m
C. 18 m
D. 26 m

**Answer: A**

**Solution.** Downward positive. Initial vertical velocity = 12 sin 30° = 6.0 m s⁻¹; horizontal velocity = 12 cos 30° = 10.4 m s⁻¹.
15 = 6.0t + 4.9t² → t = 1.24 s. Horizontal distance = 10.4 × 1.24 = 12.9 m ≈ 13 m.

| Option | Misconception |
|---|---|
| B | Uses the whole velocity instead of the horizontal component: 12 × 1.24 = 14.9 m |
| C | Ignores the initial vertical velocity (solves it like a horizontal projection): t = 1.75 s, 10.4 × 1.75 = 18.2 m |
| D | Solves as if the stone were thrown upwards at an angle: t = 2.47 s, 10.4 × 2.47 = 25.6 m |

---

## Question 3 — Paper 1A

A ball is thrown vertically upwards. Air resistance is **not** negligible.

What is the magnitude of the acceleration of the ball immediately after it is released?

A. zero
B. less than *g*
C. *g*
D. greater than *g*

**Answer: D**

**Solution.** While the ball rises, the resistive force acts downwards, that is, in the same direction as the weight. The resultant force is greater than the weight; the
magnitude of the acceleration is greater than *g*.

| Option | Misconception |
|---|---|
| A | Thinks "its speed is greatest at the moment of release, and it has no acceleration"; confuses velocity with acceleration |
| B | Assumes resistance always reduces the acceleration (true for the descent, false for the ascent) |
| C | Ignores resistance; takes the acceleration of free fall |

---

## Question 4 — Paper 2 (9 marks)

A drone flies horizontally at a constant speed of 18 m s⁻¹ at a height of 44 m above level ground. It releases a small package.
Air resistance on the package is negligible in parts (a) to (c).

**(a)** State the horizontal component of the velocity of the package at the instant it is released. [1]

**(b)** Calculate the time taken for the package to reach the ground. [2]

**(c)** Determine the magnitude and the direction of the velocity of the package as it reaches the ground. [3]

In practice, air resistance on the package is not negligible.

**(d)** (i) Explain, without calculation, the effect of air resistance on the time taken for the package to reach the ground. [2]

 (ii) State how the horizontal component of the velocity of the package at the ground compares with your answer to (a). [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 4. | a | | 18 «m s⁻¹» ✓ | | 1 |
| 4. | b | | 44 = ½ × 9.8 × *t*² ✓<br>*t* = 3.0 «s» ✓ | | 2 |
| 4. | c | | *v*<sub>y</sub> = 9.8 × 3.0 «= 29 m s⁻¹» ✓<br>*v* = √(18² + 29²) = 34 «m s⁻¹» ✓<br>58° below the horizontal **OR** 32° to the vertical ✓ | *Allow ECF from (b).* | 3 |
| 4. | d | i | air resistance has an upward / vertical component «opposing the fall» ✓<br>vertical acceleration is less than *g* so the time is longer ✓ | *OWTTE* | 2 |
| 4. | d | ii | less «than 18 m s⁻¹» ✓ | | 1 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `u = 18 m/s`, `H = 44 m`, constant `g = 9.8 m/s^2` | |
| `t` | `sqrt(2*H/g)` | 3.00 s |
| `v_y` | `g*t` | 29.4 m s⁻¹ |
| `v` | `sqrt(u**2 + v_y**2)` | 34.4 m s⁻¹ |
| `angle` | `atan(v_y/u)` | 58.5° |

---

## Question 5 — Paper 1B (10 marks)

A student investigates free fall. A steel ball is held by an electromagnet. When the current is switched off, a timer starts and
the ball falls a height *h* onto a trapdoor switch that stops the timer. The student repeats the measurement for each height and
records the mean time *t*.

| *h* / m | *t* / s ± 0.01 s |
|---|---|
| 0.200 | 0.20 |
| 0.400 | 0.29 |
| 0.600 | 0.35 |
| 0.800 | 0.40 |
| 1.000 | 0.45 |

The uncertainty in *h* is negligible.

**(a)** Outline why a graph of *h* against *t*² is expected to be a straight line through the origin. [2]

**(b)** Calculate the percentage uncertainty in *t*² for *h* = 1.000 m. [2]

The student plots *h* against *t*² with uncertainty bars. The gradient of the line of best fit is 5.0 m s⁻². The lines of maximum and
minimum gradient have gradients of 5.4 m s⁻² and 4.6 m s⁻².

**(c)** Determine the acceleration of free fall *g* given by this experiment, with its absolute uncertainty. [3]

**(d)** The accepted value of *g* is 9.8 m s⁻². Comment on whether the result of the experiment is consistent with the accepted value. [1]

**(e)** The electromagnet takes a short, constant time to release the ball after the timer has started. Explain the effect of this
on the value of *g* obtained. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *h* = ½*gt*² «as the ball starts from rest» ✓<br>*h* is proportional to *t*² **OR** gradient = ½*g* is constant ✓ | | 2 |
| 5. | b | | fractional uncertainty in *t* = 0.01 / 0.45 «= 0.022» ✓<br>doubled for *t*²: 4.4 % ✓ | *Accept 4 %.* | 2 |
| 5. | c | | *g* = 2 × gradient = 10 «m s⁻²» ✓<br>uncertainty in gradient = (5.4 − 4.6) / 2 = 0.4 «m s⁻²» ✓<br>*g* = (10.0 ± 0.8) «m s⁻²» ✓ | *Accept ± 1 m s⁻² if the answer is given as (10 ± 1).* | 3 |
| 5. | d | | consistent, as 9.8 m s⁻² lies within the range 9.2–10.8 m s⁻² ✓ | *Allow ECF from (c): the conclusion must follow from the candidate's own range.* | 1 |
| 5. | e | | measured times are greater than the true times of fall / this is a systematic error ✓<br>the gradient is smaller so the value of *g* obtained is too small ✓ | *OWTTE* | 2 |

### Figure note

In the version shown to the student, an *h*–*t*² graph with uncertainty bars accompanies the table. The graph is generated by code from the same data
(D-14). The least-squares gradient calculated from the data in the table is 4.98 m s⁻²; the gradients of the lines through the ends of the uncertainty bars are
5.35 and 4.56 m s⁻²; the values 5.0, 5.4 and 4.6 given in the question are these rounded to two significant figures.

---

## Format conformance

Questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?") + A–D one below the other | Questions 1–3 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–2 conform (ascending); Question 3 is a verbal ordered scale |
| 1A: negation word in bold | Question 2 ("below") and Question 3 ("not") conform |
| 1A: table-style options could not be verified in the example | Question 3 was therefore changed to a single-concept format with short options |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 4 conforms (1, 2, 3, 2, 1; total 9) |
| Markscheme: four-column table, ✓, « », OR, ECF, OWTTE | Questions 4 and 5 conform |
| 1B: experiment question of about 10 marks, sub-parts 1–3 marks | Question 5 conforms (2, 2, 3, 1, 2; total 10) |
| 1B: table header "quantity / unit ± uncertainty" | Question 5 conforms |
| 1B: the student draws the best-fit line on a given graph and finds its gradient themselves | **Question 5 does not conform:** because the graph could not be generated, the gradients are given in the text. Part (c) must be rewritten when the graph template is ready |
| Value–unit notation (m s⁻¹), 2 significant figures | Conforms |

## Observations from this trial

1. **The formula chain works for numerical questions** (Questions 2, 4, 5). For qualitative questions (Question 3) there is nothing to verify with code; assurance
   must come from the critic and the expert.
2. **Distractors are computable.** In Questions 1 and 2 each wrong option follows from the formula of a specific misconception; if the schema keeps a
   "misconception + formula" per distractor, code can verify these too.
3. **A data-based question depends on the figure.** Question 5 is incomplete without the graph; generating the graph from a template is a prerequisite for this question type.
4. **Coverage balance is hard by hand.** Five questions do not even cover half of A.1; an outcome × objective × question type table per node must be kept at the
   Blueprint stage.
