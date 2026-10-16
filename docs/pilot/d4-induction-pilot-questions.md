# Pilot question set: D.4 Induction

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
> D.4 is an HL-only node; all questions in this file are labelled HL.
>
> **Source:** only syllabus node D.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; the scenarios are the author's inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. No physical constants were used in this file.
> **Independent check:** passed an independent blind solver; has not passed expert review (see end of file).
> **Not verified:** (1) no expert review was done; (2) the induced current and force directions (Question 2) were checked by hand with Lenz's
> law, the right-hand grip rule and also the vector product F = IL × B, not by code; (3) Question 4 requires the knowledge that the peak emf is
> directly proportional to the rotation frequency — it is based on the "effect of rotation frequency" outcome in the syllabus analysis;
> whether the expression ε₀ = NBAω is in the data booklet was not confirmed, so the question asks only for a ratio; (4) in Question 5 it was not confirmed, for realism, that a 0.40 T
> uniform field can be obtained over a region 0.20 m wide (an array of strong permanent magnets);
> (5) no expert check was made for similarity to any known exam question.

## Scope table

| # | Section | Level | Outcome (D.4) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Emf in a rectangular coil entering a field (ε = BvL, N turns) | AO2 | — | 1 | Medium |
| 2 | Paper 1A | HL | Lenz's law: direction of the induced current and force | AO2 | — | 1 | Medium–hard |
| 3 | Paper 1A | HL | Relationship between flux linkage and emf in a rotating coil | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Effect of rotation frequency on a sinusoidal emf | AO2 | — | 1 | Medium |
| 5 | Paper 2 | HL | Emf in a moving conductor; induced current and force; Lenz's law and conservation of energy; Faraday's law | AO2–AO3 | Calculate, Determine, Show that, Explain | 9 | Medium–hard |

This set does not cover all of D.4. Not covered: the definition of magnetic flux and its calculation with angle (Φ = BA cos θ), calculating emf from
flux–time data with Faraday's law, a qualitative description of self-induction, sketching the sinusoidal emf graph.

Scope limit check: quantitative work is only for the side of a rectangular coil / frame entering the field that moves at right angles to the field (Questions 1, 5);
rotating coil questions (Questions 3, 4) ask only for a qualitative relationship and a ratio; no self-induction, inductance or RL circuit; no derivatives or
integrals.

---

## Question 1 — Paper 1A (HL)

A rectangular coil has 20 turns and sides of length 0.10 m and 0.20 m. The coil moves at a constant speed of 0.50 m s⁻¹ into a region
of uniform magnetic field of strength 0.30 T. The plane of the coil is at right angles to the field. The leading side of the coil has
length 0.10 m and is at right angles to the velocity. The coil is partly inside the field.

> **Figure:** A rectangular coil in the plane of the page (short side 0.10 m vertical, long side 0.20 m horizontal) moving to the right with velocity *v*.
> On the right, a region of uniform magnetic field perpendicular to the page (⊗ symbols) begins at a vertical boundary line. The 0.10 m side of the coil
> on the right is inside the field and the side on the left is outside it. Diagram not to scale.

What is the emf induced in the coil?

A. 0.015 V
B. 0.12 V
C. 0.30 V
D. 0.60 V

**Answer: C**

**Solution.** Only the leading side, which is inside the field, cuts the flux lines. For each turn ε = BvL = 0.30 × 0.50 × 0.10 = 0.015 V; the 20 turns
are in series, so ε = 20 × 0.015 = 0.30 V. (Equivalent: the rate of change of flux linkage is N B L v.)

| Option | Misconception |
|---|---|
| A | Forgets the number of turns: 0.30 × 0.50 × 0.10 = 0.015 V |
| B | Calculates the full flux linkage (NBA) instead of the emf: 20 × 0.30 × 0.10 × 0.20 = 0.12 |
| D | Uses the side parallel to the velocity instead of the side perpendicular to it: 20 × 0.30 × 0.50 × 0.20 = 0.60 V |

---

## Question 2 — Paper 1A (HL)

A rectangular conducting loop lies in the plane of the page. Part of the loop is in a region of uniform magnetic field that is
directed **into** the page. The loop is pulled to the right, out of the field region, at constant speed.

> **Figure:** A rectangular conducting frame in the plane of the page. On the left, a region of uniform magnetic field into the page
> (⊗ symbols) ends at a vertical boundary line; there is no field to the right of the boundary. The left side of the frame is inside the field and the right side is outside.
> A velocity arrow (*v*) pointing right is drawn on the frame. Current directions are defined as seen by an observer looking at the page. Diagram not to scale.

Which describes the direction of the induced current in the loop, as seen by an observer looking at the page, and the direction of
the magnetic force on the loop?

A. The current is clockwise and the force is to the left.
B. The current is clockwise and the force is to the right.
C. The current is anticlockwise and the force is to the left.
D. The current is anticlockwise and the force is to the right.

**Answer: A**

**Solution.** As the frame leaves the field, the flux into the page decreases. Lenz's law: the induced current opposes this decrease, that is, it
produces a field into the page inside the frame. Right-hand grip rule (fingers curl in the direction of the current, the thumb points along the field inside
the loop): for a field into the page the current is clockwise.
Force: the clockwise current is towards the top of the page (+y) in the left side, which is in the field. F = IL × B = (+y) × (−z) = −x: to the left.
The forces on the parts of the top and bottom sides that are in the field are equal and opposite. The force opposes the motion; consistent with conservation of energy.

| Option | Misconception |
|---|---|
| B | Current direction correct; but thinks the force assists the motion (contradicts conservation of energy) or applies the hand rule the wrong way round |
| C | Thinks the induced field is always opposite to the external field (misses that the flux is decreasing); correctly remembers "opposes the motion" for the force |
| D | Thinks the induced field is opposite to the external field, and then finds the force by applying the rule to this current: an anticlockwise current is downwards in the left side, (−y) × (−z) = +x, to the right |

---

## Question 3 — Paper 1A (HL)

A rectangular coil rotates at a constant rate in a uniform magnetic field. The axis of rotation lies in the plane of the coil and is
at right angles to the field.
At one instant the plane of the coil is **parallel** to the magnetic field lines.

Which describes the magnitudes of the magnetic flux linkage and of the induced emf at this instant?

A. The flux linkage is zero and the emf is zero.
B. The flux linkage is zero and the emf is a maximum.
C. The flux linkage is a maximum and the emf is zero.
D. The flux linkage is a maximum and the emf is a maximum.

**Answer: B**

**Solution.** When the plane of the coil is parallel to the field lines, no field lines pass through the coil: the flux linkage is zero. At the same instant the sides
of the coil cut the field lines at right angles; the flux linkage changes most rapidly at this instant. By Faraday's law the emf is proportional to the rate of
change of flux linkage, so it is at its maximum value.

| Option | Misconception |
|---|---|
| A | Thinks the emf is proportional to the flux linkage itself (not to its rate of change) |
| C | Confuses the coil plane being parallel to the field with it being perpendicular |
| D | Confuses the position and also thinks the emf is proportional to the flux |

---

## Question 4 — Paper 1A (HL)

A coil rotates at a constant rate in a uniform magnetic field. The emf induced in the coil varies sinusoidally with a maximum value
of 6.0 V and a period of 40 ms. The frequency of rotation of the coil is then doubled. No other change is made.

Which gives the new maximum emf and the new period?

A. 3.0 V and 80 ms
B. 6.0 V and 20 ms
C. 12 V and 40 ms
D. 12 V and 20 ms

**Answer: D**

**Solution.** When the frequency doubles, the period halves: 20 ms. The maximum value of the flux linkage does not change, but the same change takes place in half
the time; the maximum rate of change of flux linkage, and therefore the peak emf, doubles: 12 V.

| Option | Misconception |
|---|---|
| A | Confuses frequency with period (the period doubles) and thinks the emf halves accordingly |
| B | Thinks the peak emf depends only on B, the area and the number of turns; period correct |
| C | Knows the emf increases but does not see that the period of the emf changes together with the rotation period |

---

## Question 5 — Paper 2 (HL, 9 marks)

A rectangular aluminium frame is fixed flat on top of a small cart. The frame is a single loop of resistance 0.050 Ω. The cart is
pulled along a horizontal track at a constant speed of 1.5 m s⁻¹. The frame enters a region of uniform magnetic field of strength
0.40 T that is directed vertically downwards. The leading side of the frame has length 0.20 m and is at right angles to the velocity.
The region of field is longer than the frame.

> **Figure:** View from above. A rectangular frame (the leading and trailing sides 0.20 m, at right angles to the motion; the side edges longer,
> parallel to the motion) moves to the right at 1.5 m s⁻¹. On the right, a region of uniform magnetic field into the page (downwards for an observer looking from above)
> (⊗ symbols) begins at a vertical boundary line. The leading side of the frame is inside the field and the trailing
> side is outside it. Diagram not to scale.

**(a)** Calculate the emf induced in the frame while it is entering the field. [2]

**(b)** Determine the magnitude of the force that must be applied to the cart to keep its speed constant while the frame is entering
the field. Friction and air resistance are negligible. [3]

**(c)** Show that, while the frame is entering the field, the rate at which the applied force does work and the rate at which energy
is dissipated in the frame are both about 0.29 W. [2]

The frame is now completely inside the region of magnetic field and is still moving at 1.5 m s⁻¹.

**(d)** Explain why there is no current in the frame. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *ε* = *BvL* = 0.40 × 1.5 × 0.20 ✓<br>*ε* = 0.12 «V» ✓ | | 2 |
| 5. | b | | *I* = *ε*/*R* = 0.12 / 0.050 «= 2.4 A» ✓<br>«magnetic» force on the leading side = *BIL* = 0.40 × 2.4 × 0.20 ✓<br>«applied force equals the magnetic force as the speed is constant, so» *F* = 0.19 «N» ✓ | *Allow ECF from (a).* | 3 |
| 5. | c | | rate of work done by applied force = *Fv* = 0.192 × 1.5 = 0.288 «W» ✓<br>rate of energy dissipation = *I*²*R* = 2.4² × 0.050 = 0.288 «W» **OR** *εI* = 0.12 × 2.4 = 0.288 «W» ✓ | *Both values must be calculated.*<br>*Allow 0.285 W «0.28–0.29 W» for Fv if the rounded F = 0.19 N is used.*<br>*Allow Fv = BILv = εI for MP1 if one of the two powers is evaluated as 0.29 W.* | 2 |
| 5. | d | | the magnetic flux «linkage» through the frame is constant / is not changing ✓<br>«by Faraday's law» the induced emf is zero, so there is no current ✓ | *OWTTE*<br>**OR** *equal emfs are induced in the leading and trailing sides ✓ they act in opposite senses around the loop so the net emf is zero ✓* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `B = 0.40 T`, `v = 1.5 m/s`, `L = 0.20 m`, `R = 0.050 ohm` | |
| `emf` | `B*v*L` | 0.12 V |
| `I` | `emf/R` | 2.4 A |
| `F` | `B*I*L` | 0.192 N ≈ 0.19 N |
| `P_mech` | `F*v` | 0.288 W |
| `P_elec` | `I**2*R` | 0.288 W |

**Direction note (not asked in the question, for consistency).** As the frame enters the field, the flux into the page increases; by Lenz's law the
induced current produces a field out of the page inside the frame: anticlockwise for an observer looking from above. This current is towards the top of the page (+y) in the
leading side; F = IL × B = (+y) × (−z) = −x: the magnetic force is to the left, that is, opposing the motion. The applied force
is therefore to the right.

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence + A–D listed vertically | Question 1 "What is …?"; Questions 2–4 "Which …?" (rarer in the profile but valid) |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Question 1 conforms (ascending); Questions 2–3 four sentences in the same pattern; Question 4 four value pairs in the same pattern (ascending by emf) |
| 1A: table-option format could not be verified in the example | Questions 2–4 were therefore written in sentence / pair form instead of a two-column table; **sentence-form options are a minority in the profile, 3 of the 4 questions in this file** — convert if the expert approves the table format |
| 1A: critical word in bold | Question 2 ("into"), Question 3 ("parallel") |
| 1A: balanced position of the correct answer | C, A, B, D |
| 1A: options are distinct after rounding | Checked (python) |
| Figure | Questions 1, 2, 5: described in text; the field direction and direction of motion are also given in words |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 3, 2, 2; total 9) |
| Paper 2: "Show that" pattern | Question 5(c): numerical target given (0.29 W); the two quantities are calculated separately |
| Paper 2: at least one AO3 part | Question 5(b) Determine, (c) Show that, (d) Explain |
| Markscheme: four-column table, ✓, « », OR, ECF, OWTTE | Question 5 conforms |
| Value–unit notation (m s⁻¹), 2 significant figures | Conforms |
| Paper 1B | Not in this file; the 1B question for theme D is [in the D.3 file](d3-motion-in-em-fields-pilot-questions.md) |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver other than its author, without seeing the answers; all answer keys,
distractor values and the current / force directions in Questions 2 and 5 (by two independent routes) were reproduced and matched. No CRITICAL or
MEDIUM findings. Details: [review/d4-review.md](review/d4-review.md). This check does not replace expert review.

Changes made in response to the review:

- **Question 3 (stem):** it was added that the axis of rotation is in the plane of the coil ("The axis of rotation lies in the plane of the coil and is at
  right angles to the field").
- **Question 5(c) (question):** a numerical target was given to the "Show that" part: both powers are shown to be about 0.29 W.
- **Question 5(c) (markscheme):** "0.19 × 1.5 = 0.29" (arithmetically 0.285) → "0.192 × 1.5 = 0.288"; an acceptance note for 0.285 W with the rounded F = 0.19 N
  was added. `python3`: 0.192 × 1.5 = 0.288; 2.4² × 0.050 = 0.288; 0.12 × 2.4 = 0.288.
- **Not changed:** the sentence / pair-form options of Questions 2–4. Because the two-column table format was not verified in the format profile,
  it was left to an expert decision (the reviewer agrees).
