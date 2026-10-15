# Pilot question set: A.5 Galilean and special relativity

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written by hand according to the [authoring standard](AUTHORING_STANDARD.md) and with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
> A.5 is an HL-only node; all questions are labelled HL and do not enter the SL pool.
>
> **Source:** only syllabus node A.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam question, textbook question or internet source was used as input.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate calculation in `python3`
> (c = 3.00 × 10⁸ m s⁻¹; the data booklet value must be confirmed by an expert). In Question 5 it was also checked that the spacetime interval between two events
> comes out equal in the two frames.
> **Not verified:** it passed an independent blind solver; it has not passed expert review; it has not been checked by an expert for resemblance
> to any known exam question; the sign convention the guide uses for the spacetime interval ((*c*Δ*t*)² − Δ*x*²) and the way the Lorentz transformations are written in the data
> booklet were not checked; the measurement of the angle from the *ct* axis in Question 4 is based on the statement "tan *θ* = *v*/*c*" in the syllabus analysis.


## Scope table

| # | Section | Level | Outcome (A.5) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Proper time and time dilation; which frame measures the proper time | AO2 | — | 1 | Medium |
| 2 | Paper 1A | HL | Relativistic velocity addition (compared with Galilean addition) | AO2 | — | 1 | Medium |
| 3 | Paper 1A | HL | Invariance of the spacetime interval | AO3 | — | 1 | Medium–hard |
| 4 | Paper 1A | HL | Angle of the worldline on a spacetime diagram (tan *θ* = *v*/*c*) | AO2 | — | 1 | Easy |
| 5 | Paper 2 | HL | Proper length; *γ*; proper time; Lorentz transformation and the relativity of simultaneity | AO1–AO3 | State, Show that, Calculate, Determine | 9 | Medium–hard |

This set does not cover all of A.5. Missing: the Galilean transformation and the concept of a reference frame, statement of the postulates of relativity,
direct calculation of length contraction, muon decay evidence, drawing a spacetime diagram and simultaneity on the diagram,
the Lorentz transformation for position (*x*′ = *γ*(*x* − *vt*)).

---

## Question 1 — Paper 1A

Two space buoys X and Y are at rest relative to each other. In the reference frame of the buoys the distance between X and Y is
9.0 × 10⁸ m. A probe travels in a straight line from X to Y at a constant speed of 0.60*c* relative to the buoys.

What is the time taken for the probe to travel from X to Y as measured by a clock on the probe?

A. 3.0 s
B. 4.0 s
C. 5.0 s
D. 6.3 s

**Answer: B**

**Solution.** Time in the buoys' frame = 9.0 × 10⁸ / (0.60 × 3.00 × 10⁸) = 5.0 s. The two events (passing X, passing Y) both occur at the position of the
probe; the probe's clock measures the proper time. *γ* = 1/√(1 − 0.60²) = 1.25. Proper time = 5.0 / 1.25 = 4.0 s.

| Option | Misconception |
|---|---|
| A | Uses the speed of light instead of the speed of the probe: 9.0 × 10⁸ / 3.00 × 10⁸ = 3.0 s |
| C | Applies no relativistic effect; gives the time in the buoys' frame: 5.0 s |
| D | Confuses the frame in which the proper time is measured; multiplies by *γ* instead of dividing: 5.0 × 1.25 = 6.25 s ≈ 6.3 s |

---

## Question 2 — Paper 1A

A spacecraft moves directly away from the Earth at a speed of 0.60*c* relative to the Earth. The spacecraft launches a probe in its
direction of motion. The speed of the probe relative to the spacecraft is 0.70*c*.

What is the speed of the probe relative to the Earth?

A. 1.3*c*
B. *c*
C. 0.92*c*
D. 0.17*c*

**Answer: C**

**Solution.** Relativistic velocity addition: *u* = (0.60*c* + 0.70*c*) / (1 + 0.60 × 0.70) = 1.30*c* / 1.42 = 0.92*c*.

| Option | Misconception |
|---|---|
| A | Uses Galilean velocity addition: 0.60*c* + 0.70*c* = 1.3*c* |
| B | Thinks "the sum exceeds *c*, so the speed is *c*"; an object with mass cannot reach speed *c* |
| D | Applies the formula with the opposite sign (as if the probe were launched backwards): (0.70*c* − 0.60*c*) / (1 − 0.42) = 0.17*c* |

---

## Question 3 — Paper 1A

In an inertial reference frame S, two events are separated by a distance Δ*x* = 3.0 m and by a time interval Δ*t* such that
*c*Δ*t* = 5.0 m. In another inertial reference frame S′ the two events occur at the same position.

What is *c*Δ*t*′, where Δ*t*′ is the time interval between the events in S′?

A. 8.0 m
B. 5.8 m
C. 5.0 m
D. 4.0 m

**Answer: D**

**Solution.** The spacetime interval is invariant: (*c*Δ*t*′)² − (Δ*x*′)² = (*c*Δ*t*)² − (Δ*x*)². Since Δ*x*′ = 0,
(*c*Δ*t*′)² = 5.0² − 3.0² = 16 m²; *c*Δ*t*′ = 4.0 m. (S′ moves at 0.60*c* relative to S; Δ*t*′ is the proper time.)

| Option | Misconception |
|---|---|
| A | Calculates the interval without squares and by adding: 5.0 + 3.0 = 8.0 m |
| B | Calculates the interval with a plus sign like a Euclidean distance: √(5.0² + 3.0²) = 5.8 m |
| C | Assumes the time interval is the same in all frames (Galilean view): 5.0 m |

---

## Question 4 — Paper 1A

A spacetime diagram is drawn for an inertial reference frame S, with the *x* axis horizontal and the *ct* axis vertical. Both axes
have the same scale. A particle moves along the *x* direction at a constant speed of 0.50*c* relative to S.

What is the angle between the worldline of the particle and the *ct* axis?

A. 27°
B. 30°
C. 45°
D. 63°

**Answer: A**

**Solution.** For the angle that the worldline makes with the *ct* axis, tan *θ* = *v*/*c* = 0.50; *θ* = 27°.

| Option | Misconception |
|---|---|
| B | Uses sin instead of tan: sin⁻¹(0.50) = 30° |
| C | Thinks every worldline is at 45° like that of light (confusion with the light line) |
| D | Measures the angle from the *x* axis instead of the *ct* axis: tan⁻¹(1 / 0.50) = 63° |

---

## Question 5 — Paper 2 (9 marks)

A long space platform has two ends, P and Q. The proper length PQ of the platform is 480 m. A shuttle moves at a constant velocity of
0.80*c* relative to the platform, parallel to PQ, in the direction from P to Q. The shuttle passes end P (event 1) and later passes
end Q (event 2).

> **Figure:** A long horizontal platform; the left end labelled P and the right end labelled Q; a "480 m" dimension arrow between the two ends. Just
> above the platform, near P, a shuttle drawn with a velocity arrow labelled "0.80*c*" pointing to the right (from P to Q). *Diagram not to scale.*

**(a)** State what is meant by proper length. [1]

**(b)** Show that the Lorentz factor *γ* for the shuttle relative to the platform is about 1.7. [1]

**(c)** Calculate the time between event 1 and event 2 in the reference frame of the platform. [2]

**(d)** Determine the time between event 1 and event 2 as measured by a clock on the shuttle. [2]

A lamp at P and a lamp at Q each emit one flash of light. In the reference frame of the platform the two flashes are emitted at the
same time.

**(e)** Determine, for the reference frame of the shuttle, which lamp (at P or at Q) flashes first and the time interval between
the two flashes. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the length of an object measured in the reference frame in which the object is at rest ✓ | *OWTTE* | 1 |
| 5. | b | | *γ* = 1 / √(1 − 0.80²) = 1.67 ✓ | *Substitution or an answer to at least 3 s.f. must be seen.* | 1 |
| 5. | c | | Δ*t* = 480 / (0.80 × 3.00 × 10⁸) ✓<br>= 2.0 × 10⁻⁶ «s» ✓ | | 2 |
| 5. | d | | **ALTERNATIVE 1**<br>shuttle clock measures the proper time «both events occur at the shuttle» so Δ*t*′ = Δ*t* / *γ* ✓<br>Δ*t*′ = 2.0 × 10⁻⁶ / 1.67 = 1.2 × 10⁻⁶ «s» ✓<br>**ALTERNATIVE 2**<br>length of platform in shuttle frame = 480 / 1.67 «= 288 m» ✓<br>Δ*t*′ = 288 / (0.80 × 3.00 × 10⁸) = 1.2 × 10⁻⁶ «s» ✓ | *Allow ECF from (c).*<br>*Award [1] max for 3.3 × 10⁻⁶ «s» (multiplying by γ).* | 2 |
| 5. | e | | use of Δ*t*′ = *γ*(Δ*t* − *v*Δ*x*/*c*²) with Δ*t* = 0 **AND** Δ*x* = 480 «m» ✓<br>«magnitude of» Δ*t*′ = 1.67 × 0.80 × 480 / (3.00 × 10⁸) = 2.1 × 10⁻⁶ «s» ✓<br>the lamp at Q flashes first ✓ | *Accept answers in the range 2.1 × 10⁻⁶ to 2.2 × 10⁻⁶ «s» (use of γ = 1.7 gives 2.18 × 10⁻⁶).*<br>*Award the third mark only if it is supported by the sign of Δt′ or by a simultaneity argument; do not award it for a bare statement.*<br>*Accept "the lamp the shuttle is moving towards" for "the lamp at Q".* | 3 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `beta = 0.80`, `L0 = 480 m`, constant `c = 3.00e8 m/s` | |
| `gamma` | `1/sqrt(1 - beta**2)` | 1.667 |
| `dt` | `L0/(beta*c)` | 2.00 × 10⁻⁶ s |
| `dt_proper` | `dt/gamma` | 1.20 × 10⁻⁶ s |
| `L` (check) | `L0/gamma` | 288 m; `L/(beta*c)` = 1.20 × 10⁻⁶ s |
| `dt_flash` | `gamma*(0 - beta*L0/c)` | −2.13 × 10⁻⁶ s (Q lamp − P lamp; minus sign: the Q lamp first) |

Check (not asked of the student): the interval between events 1 and 2 in the platform frame is (*c*Δ*t*)² − Δ*x*² = 600² − 480² = 1.296 × 10⁵ m²;
in the shuttle frame (*c*Δ*t*′)² = 360² = 1.296 × 10⁵ m². The two values are equal.

Reasoning for the direction in (e): take end P at *x* = 0 and end Q at *x* = +480 m; the shuttle moves in the +*x* direction (from P to Q).
In the transformation *t*′ = *γ*(*t* − *vx*/*c*²), of two events that are simultaneous (*t* = 0) in the platform frame, the one with the larger *x* value (the Q lamp) gets the
smaller *t*′; that is, the lamp the shuttle is approaching (Q) flashes first.

---

## Format conformance

Questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?") + A–D one below the other | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1 and 4 ascending (s, degrees); Questions 2 and 3 descending (multiples of *c*, m) |
| 1A: balanced position of the correct answer | B, C, D, A |
| 1A: negative stem | Not used |
| Figure | Question 4 describes the spacetime diagram in words; it is solved without a figure. Question 5 is described in text (ends P and Q, direction of the shuttle); the question can be solved without the figure too, a figure must be generated for the student version |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (1, 1, 2, 2, 3; total 9) |
| Paper 2: "Show that" pattern; a later part may use the given value | Question 5 (b) → (d), (e) conforms; an acceptance range is given for (e) |
| Markscheme: four-column table, ✓, « », AND, ECF, OWTTE, ALTERNATIVE 1 / 2 | Question 5 conforms |
| Value–unit notation, 2 significant figures; speeds in terms of *c* | Conforms |
| Scope limits (A.5) | No derivations asked; time axis *ct*; worldline of constant velocity; inertial frames only |
| Terminology | "proper time", "proper length", "worldline", "reference frame" were used as guide terms; the guide's equivalent of the term "Lorentz factor" was not confirmed |

## Independent check

Date: 2026-10-11. The blind solver solved the questions without seeing the answers and independently reproduced all answer keys and markscheme results; no CRITICAL or MEDIUM findings.
Details: [review/a5-review.md](review/a5-review.md). This check does not replace expert review.

Changes made in response to the findings:

- Question 5: the ends of the platform were named P and Q instead of "rear/front"; the stem now states explicitly that the shuttle goes from P to Q and a figure description was added. (e) became "which lamp (at P or at Q)"; the markscheme, formula chain and direction reasoning were updated accordingly (correct answer: the Q lamp). The numbers did not change; recalculated with `python3` (2.13 × 10⁻⁶ s; 2.18 × 10⁻⁶ s with *γ* = 1.7).
- Question 5 (e) markscheme note: "third mark is independent" was removed; the third mark is now awarded only with the sign of Δ*t*′ or a simultaneity argument, an unsupported guess of direction gets no mark.
- The figure row in the "Format conformance" table was updated to cover Question 5.
- **Not applied:** the suggestion to replace option B (*c*) in Question 2 with a value below *c* (the review says "not required"). Reason: "if the sum exceeds *c*, the speed is *c*" is a real and common misconception; the proposed alternative (dividing the sum by *γ*) is ambiguous about which frame's *γ* is meant, is not based on a defined student error, and the standard requires every distractor to rest on a specific misconception. Whether the question discriminates poorly was left to expert review.
