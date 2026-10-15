# Pilot question set: C.2 Wave model

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written to the [authoring standard](AUTHORING_STANDARD.md), with the same structure as the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node C.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook or internet question was used as input; the scenarios are original.
> **Numerical check:** all numerical answers and all numerical distractors were recomputed with `python3` (standard library only).
> Constants: c = 3.00 × 10⁸ m s⁻¹; speed of sound in air 340 m s⁻¹ (given in the question where it is used); speed of sound in seawater 1500 m s⁻¹ (given in the
> question). Data booklet values should be confirmed by an expert.
> **Not verified:** (1) it was solved by an independent blind solver; it has not been through expert review; (2) it has not been checked by an expert
> for similarity to a known exam question; (3) Question 2 and Question 5 (a), (c), (e) are qualitative and cannot be verified by code; (4) in Question 5, modelling a water surface wave as a "transverse wave"
> is a simplification (in reality the particles move in approximately circular paths); an expert may not find this context suitable.

## Scope table

| # | Section | Level | Outcome (C.2) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | v = fλ; the speed of a sound wave depends on the medium | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Direction of motion of a medium particle in a transverse wave (displacement against position) | AO3 | — | 1 | Medium |
| 3 | Paper 1A | SL | Longitudinal wave; period from displacement against time; compression–rarefaction separation | AO2 | — | 1 | Medium |
| 4 | Paper 1A | SL | Nature of an electromagnetic wave; v = fλ, prefixes | AO2 | — | 1 | Easy |
| 5 | Paper 2 | SL | Definition of a transverse wave; v = fλ; particle motion with position; energy transfer by a wave | AO1–AO3 | State, Calculate, Determine, Show that, Explain | 9 | Medium |

This set does not cover all of C.2. Not covered: drawing displacement–position and displacement–time graphs and interpreting them
together; the pressure–displacement relationship in a sound wave; explaining the difference between mechanical and electromagnetic waves (need for a medium);
orders of magnitude of the regions of the electromagnetic spectrum.

---

## Question 1 — Paper 1A

A dolphin emits a sound wave of frequency 150 kHz. The speed of sound in seawater is 1500 m s⁻¹.

What is the wavelength of the sound wave in seawater?

A. 0.010 m
B. 10 m
C. 100 m
D. 2000 m

**Answer: A**

**Solution.** λ = v / f = 1500 / (150 × 10³) = 0.010 m.

| Option | Misconception |
|---|---|
| B | Does not convert the kHz prefix: 1500 / 150 = 10 m |
| C | Inverts the ratio (f / v): 150 000 / 1500 = 100 |
| D | Treats the sound wave like an electromagnetic wave and uses the speed of light: 3.00 × 10⁸ / (150 × 10³) = 2000 m |

---

## Question 2 — Paper 1A

A transverse wave travels to the right along a horizontal rope. At one instant, a point P on the rope is at its equilibrium
position. At this instant the crest nearest to P is 0.10 m to the left of P and the trough nearest to P is 0.10 m to the right
of P. At a crest the rope is displaced upwards.

> **Figure:** A snapshot of a sinusoidal wave travelling to the right along a horizontal rope. Point P is on the equilibrium line; to its left,
> 0.10 m away, is a crest and to its right, 0.10 m away, is a trough. The direction of travel of the wave is shown by an arrow pointing right. The question can be solved from the information in the text
> without the figure.

What is the direction of motion of P at this instant?

A. to the left
B. to the right
C. downwards
D. upwards

**Answer: D**

**Solution.** The wave travels to the right; the crest to the left of P reaches P shortly afterwards. So P is moving upwards. In a transverse
wave a particle moves only perpendicular to the direction of travel.

| Option | Misconception |
|---|---|
| A | Assumes the particle is pulled towards the approaching crest (the direction the wave comes from) |
| B | Assumes the medium particles travel along with the wave |
| C | Reads the snapshot like a "slope": because the rope descends from the crest to the trough, P is assumed to move down too (this would be correct if the wave travelled to the left) |

---

## Question 3 — Paper 1A

A sound wave travels through air. The speed of sound in air is 340 m s⁻¹. A graph of displacement against time is drawn for one
particle of the air. On the graph, the time between two adjacent instants at which the displacement is zero is 2.0 ms.

What is the distance between the centre of a compression and the centre of the nearest rarefaction?

A. 0.34 m
B. 0.68 m
C. 1.4 m
D. 2.7 m

**Answer: B**

**Solution.** Two successive zero crossings are half a period apart: T = 4.0 ms. λ = vT = 340 × 4.0 × 10⁻³ = 1.36 m. The distance between the centre of a compression and the
centre of the nearest rarefaction is half a wavelength: 0.68 m.

| Option | Misconception |
|---|---|
| A | Takes 2.0 ms to be the full period: λ = 340 × 2.0 × 10⁻³ = 0.68 m; half of this is 0.34 m |
| C | Takes the compression–rarefaction separation to be a full wavelength: 1.36 ≈ 1.4 m |
| D | Takes 2.0 ms to be a quarter of the period (T = 8.0 ms → λ = 340 × 8.0 × 10⁻³ = 2.72 m) and takes the compression–rarefaction separation to be a full wavelength: 2.7 m |

---

## Question 4 — Paper 1A

A microwave oven produces electromagnetic waves of frequency 2.5 GHz.

What is the wavelength of these waves in air?

A. 1.4 × 10⁻⁷ m
B. 1.2 × 10⁻⁴ m
C. 0.12 m
D. 8.3 m

**Answer: C**

**Solution.** An electromagnetic wave travels in air at approximately speed c. λ = c / f = 3.00 × 10⁸ / (2.5 × 10⁹) = 0.12 m.

| Option | Misconception |
|---|---|
| A | Uses the speed of sound for an electromagnetic wave: 340 / (2.5 × 10⁹) = 1.4 × 10⁻⁷ m |
| B | Takes the G prefix to be 10¹²: 3.00 × 10⁸ / (2.5 × 10¹²) = 1.2 × 10⁻⁴ m |
| D | Inverts the ratio (f / c): 2.5 × 10⁹ / (3.00 × 10⁸) = 8.3 |

---

## Question 5 — Paper 2 (9 marks)

Water waves travel across a lake towards the shore. A small fishing float on the surface moves up and down as the waves pass.
The wave can be modelled as a transverse wave. The float completes 12 oscillations in 30 s. The amplitude of the oscillations is
4.0 cm and the distance between adjacent crests is 3.5 m.

**(a)** State what is meant by a transverse wave. [1]

**(b)** Calculate the speed of the wave. [2]

A second float is 5.25 m from the first float, measured along the direction in which the wave travels.

**(c)** Determine the displacement of the second float at an instant when the first float is at a crest. [2]

**(d)** Show that the total distance moved by the first float in 30 s is about 2 m. [2]

**(e)** The shore is 21 m from the first float. A student predicts that the waves will carry the float to the shore in 15 s.
Explain why this prediction is incorrect. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the oscillations «of the particles of the medium» are perpendicular to the direction of energy transfer / of propagation of the wave ✓ | *Do not accept "the wave moves up and down".* | 1 |
| 5. | b | | *T* = 30 / 12 = 2.5 «s» **OR** *f* = 0.40 «Hz» ✓<br>*v* = 0.40 × 3.5 = 1.4 «m s⁻¹» ✓ | | 2 |
| 5. | c | | 5.25 / 3.5 = 1.5 «wavelengths» **OR** the floats oscillate in antiphase ✓<br>displacement = −4.0 «cm» **OR** 4.0 cm below the equilibrium position / at a trough ✓ | *Second mark requires the direction (sign or words).* | 2 |
| 5. | d | | distance in one oscillation = 4 × 4.0 «= 16 cm» ✓<br>12 × 16 = 192 «cm» **OR** 1.9 «m» ✓ | *Answer must be seen to at least 2 s.f. or the working must be shown.* | 2 |
| 5. | e | | a wave transfers energy, not matter / the medium is not transported ✓<br>the float «only» oscillates «vertically» about a fixed / mean position ✓ | *OWTTE*<br>*Award [1 max] for "21 m in 15 s is the speed of the wave, not of the float" without further explanation.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `N = 12`, `t = 30 s`, `A = 0.040 m`, `lam = 3.5 m`, `dx = 5.25 m` | |
| `T` | `t/N` | 2.5 s |
| `f` | `1/T` | 0.40 Hz |
| `v` | `f*lam` | 1.4 m s⁻¹ |
| `n_lam` | `dx/lam` | 1.5 (antiphase) → displacement −4.0 cm |
| `d_total` | `N*4*A` | 1.92 m |
| Check (e) | `21/15` | 1.4 m s⁻¹ = wave speed; the student's misconception is based on this value |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one below the other | Questions 1–4 conform |
| 1A: four options of the same type, same unit, in order of magnitude | Questions 1, 3, 4 conform (ascending); Question 2 has four directions (verbal) |
| 1A: correct-answer letters balanced | A, D, B, C |
| 1A: solvable without a figure | In Question 2 the figure is described in words; all required information is in the text |
| 1A: round, clean numbers | Conforms; in Question 1 all four options are in plain notation, in Question 4 the options are in scientific notation (C and D plain) because they span a wide range |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (1, 2, 2, 2, 2; total 9). On an SL paper short questions of 4–6 marks were observed; 9 marks is the top of the HL range — for an SL paper (d) or (e) can be removed |
| Paper 2: "Show that" pattern and at least one AO3 part | Question 5 (c) Determine, (d) Show that, (e) Explain |
| Markscheme: four-column table, ✓, « », OR, OWTTE | Question 5 conforms |
| Paper 2: figure | **Missing:** no figure was described for Question 5; the question can be solved without a figure |
| Syllabus limit | Memorizing spectrum orders of magnitude was not required; the concept of "phase" is used in (c) only through "1.5 wavelengths" |
| Value–unit notation (m s⁻¹), 2 significant figures | Conforms |

## Independent check

Date: 2026-10-11. This file was solved by an independent blind solver who did not see the answers; the solver independently reproduced all answer
keys and markscheme results (no CRITICAL findings). Findings:
[review/c2-review.md](review/c2-review.md). This does not replace expert review.

Changes made in response to the findings (every changed number was rechecked with `python3` against the final text of the file):

- **Question 1 (LOW):** the options were put in a single notation: 1.0 × 10⁻² m, 10 m, 1.0 × 10² m, 2.0 × 10³ m → 0.010 m, 10 m, 100 m, 2000 m. Values unchanged, key A.
- **Question 3 (LOW):** the basis of distractor D was rewritten (2.0 ms taken as a quarter period and the full wavelength taken); the number (2.7 m) is unchanged.
- **Question 5 (LOW):** the note that 9 marks is long for SL was already in the "Format conformance" table; the question was not split. The decision to split (5 + 4 marks) should be made when the exam paper is assembled.
- **Not applied:** the options of Question 4 (1.4 × 10⁻⁷ m, 1.2 × 10⁻⁴ m, 0.12 m, 8.3 m) were left in mixed notation; the review does not list this as a finding and plain notation of the 10⁻⁷ order of magnitude would be unreadable.
