# Pilot question set: C.3 Wave phenomena

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written to the [authoring standard](AUTHORING_STANDARD.md), with the same structure as the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node C.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook or internet question was used as input; the scenarios are original.
> **Numerical check:** all numerical answers and all numerical distractors were recomputed with `python3` (standard library only).
> Constants: speed of sound in air 340 m s⁻¹ (given in the question). The refractive indices (plastic 1.6, water 1.3) and the laser wavelength (633 nm) are realistic
> values and are given in the question.
> **Not verified:** (1) it was solved by an independent blind solver; it has not been through expert review; (2) it has not been checked by an expert
> for similarity to a known exam question; (3) the "normal incidence only" limit was applied in this set to the slit and grating questions (Question 2, 4, 5, 6); Snell's law and the critical
> angle inherently involve oblique incidence, so Question 1 was not counted as outside this limit — this interpretation should be confirmed by an expert; (4) in Question 6 (c)(ii)
> the fifth-order fringe lies outside the central maximum (in a secondary maximum); the borderline case was deliberately avoided; (5) the qualitative
> parts (Question 6 a and d) cannot be verified by code.

## Scope table

| # | Section | Level | Outcome (C.3) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Critical angle; total internal reflection between two transparent media | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Double slit; proportionality with s = λD/d | AO2 | — | 1 | Easy |
| 3 | Paper 1A | SL | Sources in phase; path difference and the condition for destructive interference | AO3 | — | 1 | Medium |
| 4 | Paper 1A | HL | Diffraction grating; highest observable order | AO2 | — | 1 | Medium |
| 5 | Paper 1A | HL | Single-slit diffraction; θ = λ/b and the width of the central maximum | AO2 | — | 1 | Medium |
| 6 | Paper 2 | HL | Constructive interference; s = λD/d; modulation of the double-slit pattern by the single slit; multiple slits | AO2–AO3 | Explain, Show that, Calculate, Determine, State | 9 | Medium–hard |

This set does not cover all of C.3. Not covered: drawing wavefronts and rays; reflection and transmission; the angle of refraction using Snell's law and
the change of speed and wavelength on refraction; qualitative description of diffraction at an aperture and an obstacle; sketching the single-slit intensity pattern; the qualitative effect of slit width
on intensity; calculating angles for a diffraction grating (nλ = d sin θ).

---

## Question 1 — Paper 1A

Light travels in a transparent plastic of refractive index 1.6. The light is incident on a boundary between the plastic and water.
The refractive index of water is 1.3.

What is the critical angle for light at this boundary?

A. 36°
B. 39°
C. 50°
D. 54°

**Answer: D**

**Solution.** n₁ sin θ<sub>c</sub> = n₂ sin 90° → sin θ<sub>c</sub> = 1.3 / 1.6 = 0.8125 → θ<sub>c</sub> = 54.3° ≈ 54°.

| Option | Misconception |
|---|---|
| A | Measures the angle from the surface instead of from the normal: 90° − 54.3° = 35.7° ≈ 36° |
| B | Assumes the second medium is air: sin⁻¹(1 / 1.6) = 38.7° ≈ 39° |
| C | Takes the critical angle at the water–air boundary: sin⁻¹(1 / 1.3) = 50.3° ≈ 50° |

---

## Question 2 — Paper 1A

Monochromatic light is incident normally on two narrow parallel slits. Fringes are observed on a distant screen. The separation of
adjacent bright fringes is 2.0 mm. The separation of the slits is then doubled and the distance from the slits to the screen is
increased to three times its original value.

What is the new separation of adjacent bright fringes?

A. 0.33 mm
B. 1.3 mm
C. 3.0 mm
D. 12 mm

**Answer: C**

**Solution.** s = λD / d. D triples and d doubles: new s = 2.0 × 3 / 2 = 3.0 mm.

| Option | Misconception |
|---|---|
| A | Takes s to be inversely proportional to both D and d: 2.0 / (3 × 2) = 0.33 mm |
| B | Swaps the roles of D and d (s ∝ d / D): 2.0 × 2 / 3 = 1.3 mm |
| D | Takes s to be directly proportional to both D and d: 2.0 × 3 × 2 = 12 mm |

---

## Question 3 — Paper 1A

Two loudspeakers X and Y emit sound of the same frequency and are in phase. A microphone is placed at a point P that is 2.00 m from
X and 2.68 m from Y. The speed of sound in air is 340 m s⁻¹.

What is the lowest frequency for which the intensity of the sound at P is a minimum?

A. 125 Hz
B. 250 Hz
C. 500 Hz
D. 750 Hz

**Answer: B**

**Solution.** Path difference = 2.68 − 2.00 = 0.68 m. For destructive interference the path difference = (n + ½)λ; the lowest frequency corresponds to the largest wavelength:
λ/2 = 0.68 m → λ = 1.36 m → f = 340 / 1.36 = 250 Hz.

| Option | Misconception |
|---|---|
| A | Takes the path difference for destructive interference to be a quarter of a wavelength: λ = 2.72 m → 340 / 2.72 = 125 Hz |
| C | Uses the condition for constructive interference (path difference = λ): 340 / 0.68 = 500 Hz |
| D | Takes the next minimum (path difference = 3λ/2); there is also a minimum at this frequency but it is not the lowest: 3 × 340 / (2 × 0.68) = 750 Hz |

---

## Question 4 — Paper 1A

Monochromatic light of wavelength 600 nm is incident normally on a diffraction grating that has 400 lines per millimetre.

What is the highest order of maximum that can be observed?

A. 4
B. 5
C. 8
D. 9

**Answer: A**

**Solution.** d = 1.0 × 10⁻³ / 400 = 2.5 × 10⁻⁶ m. nλ = d sin θ and sin θ ≤ 1 → n ≤ d / λ = 2.5 × 10⁻⁶ / (600 × 10⁻⁹) = 4.17. The highest whole
number is 4 (sin θ₄ = 0.96).

| Option | Misconception |
|---|---|
| B | Rounds 4.17 up; for n = 5, sin θ = 1.2 > 1, so this order does not occur |
| C | Gives the number of maxima on both sides of the centre: 2 × 4 = 8 |
| D | Gives the total number of maxima seen on the screen: 2 × 4 + 1 = 9 |

---

## Question 5 — Paper 1A

Monochromatic light of wavelength 600 nm is incident normally on a single rectangular slit of width 0.10 mm. A diffraction pattern
is observed on a screen that is 2.0 m from the slit.

What is the width of the central maximum on the screen?

A. 6.0 mm
B. 12 mm
C. 24 mm
D. 48 mm

**Answer: C**

**Solution.** The angle of the first minimum is θ = λ / b = 600 × 10⁻⁹ / (0.10 × 10⁻³) = 6.0 × 10⁻³ rad. The distance from the centre to the first minimum = θD =
6.0 × 10⁻³ × 2.0 = 12 mm. The central maximum lies between the first minima on either side: 2 × 12 = 24 mm.

| Option | Misconception |
|---|---|
| A | Takes θ = λ / 2b for the first minimum (confusion with the half-wavelength condition in the double slit) and does not double: 6.0 mm |
| B | Gives the distance from the centre to the first minimum (half-width): λD / b = 12 mm |
| D | Applies the doubling twice: 4λD / b = 48 mm |

---

## Question 6 — Paper 2 (9 marks)

A technician tests a metal foil in which two narrow parallel slits have been cut. Light of wavelength 633 nm from a laser is
incident normally on the foil. A pattern of bright and dark fringes is observed on a screen that is 3.0 m from the foil.

> **Figure:** A laser beam coming from the left is incident normally on a thin plate with two parallel slits; 3.0 m to the right of the plate, parallel to the plate, is a
> screen. On the screen are equally spaced bright fringes; the central fringe is marked. "diagram not to scale". The question can be solved without the figure.

**(a)** Explain how a bright fringe is formed on the screen. [2]

The distance on the screen between the centre of the central bright fringe and the centre of the fourth bright fringe from it is
15.2 mm.

**(b)** Show that the separation of the slits is about 0.5 mm. [2]

Each slit has a width of 0.11 mm. The intensity of the double-slit fringes is modulated by the single-slit diffraction pattern of
each slit. Use a slit separation of 0.50 mm.

**(c)** (i) Calculate the angle between the centre of the pattern and the first minimum of the single-slit diffraction pattern. [1]

 (ii) Determine the number of bright fringes that are observed within the central maximum of the single-slit diffraction
pattern. [3]

The foil is replaced by a foil that has many parallel slits with the same separation and the same width.

**(d)** State **one** change in the appearance of the bright fringes. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | light from the two slits is coherent **AND** superposes / interferes «at the screen» ✓<br>path difference is a whole number of wavelengths / waves arrive in phase, so the interference is constructive ✓ | *OWTTE*<br>*Accept "zero phase difference" for "in phase".* | 2 |
| 6. | b | | *s* = 15.2 / 4 = 3.8 «mm» ✓<br>*d* = 633 × 10⁻⁹ × 3.0 / 3.8 × 10⁻³ **OR** 5.0 × 10⁻⁴ «m» ✓ | *Answer must be seen to at least 2 s.f. or the substitution must be shown.* | 2 |
| 6. | c | i | *θ* = 633 × 10⁻⁹ / 0.11 × 10⁻³ = 5.8 × 10⁻³ «rad» ✓ | *Accept 0.33°.* | 1 |
| 6. | c | ii | angular separation of fringes = *λ* / *d* = 1.27 × 10⁻³ «rad» **OR** ratio *d* / *b* = 4.5 seen ✓<br>fringes of order up to 4 lie inside the central maximum «4 × 1.27 × 10⁻³ < 5.8 × 10⁻³ < 5 × 1.27 × 10⁻³» ✓<br>9 «bright fringes» ✓ | *Allow ECF from (c)(i).*<br>*Accept width of central maximum ÷ fringe separation:* 2 × 3.0 × 5.75 × 10⁻³ = 34.5 mm; 34.5 / 3.8 = 9.1, *giving 9.*<br>*Award [2 max] for an answer of 4 (one side only), 8 (central fringe omitted) or 11 (fifth order included).* | 3 |
| 6. | d | | bright fringes are narrower / sharper **OR** brighter / more intense ✓ | *Accept "fringes stay at the same positions" only if a change in width or intensity is also stated.* | 1 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `lam = 633e-9 m`, `D = 3.0 m`, `y4 = 15.2e-3 m`, `b = 0.11e-3 m`, `d_given = 0.50e-3 m` | |
| `s` | `y4/4` | 3.8 × 10⁻³ m |
| `d` | `lam*D/s` | 5.00 × 10⁻⁴ m |
| `theta_1` | `lam/b` | 5.75 × 10⁻³ rad (0.33°) |
| `dtheta` | `lam/d_given` | 1.27 × 10⁻³ rad |
| `ratio` | `theta_1/dtheta` (= `d_given/b`) | 4.55 → highest order inside the envelope is 4 |
| `N` | `2*floor(ratio) + 1` | 9 |
| Check (width method) | `2*D*theta_1/(lam*D/d_given)` | 34.5 mm / 3.80 mm = 9.09 → 9 |

The slit width was deliberately chosen so that *d*/*b* is not a whole number (4.55): the fifth order (6.33 × 10⁻³ rad) lies outside the first minimum
(5.75 × 10⁻³ rad), in a secondary maximum; the order-counting and width ÷ spacing methods give the same result (9). In (b) the measurement
is made to the fourth fringe; this fringe is inside the central maximum (its intensity is low, about 2 % of the central fringe).

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one below the other | Questions 1–5 conform |
| 1A: four options of the same type, same unit, in order of magnitude | Questions 1–5 conform (ascending) |
| 1A: correct-answer letters balanced | D, C, B, A, C |
| 1A: solvable without a figure | Questions 1–5 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 6 conforms (2, 2, 1, 3, 1; total 9) |
| Paper 2: "Show that" pattern and at least one AO3 part | Question 6 (a) Explain, (b) Show that, (c)(ii) Determine; (c) uses the given value of 0.50 mm |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE | Question 6 conforms |
| Paper 2: figure | **Missing:** the set-up is described only in words; there is no intensity pattern graph |
| Syllabus limit: normal incidence; monochromatic light and rectangular slit; the effect of slit width on intensity is qualitative | Questions 2, 4, 5, 6 "incident normally"; Question 5 "single rectangular slit"; no intensity calculation was asked |
| Level label | Questions 4, 5, 6 HL (diffraction grating, single slit, modulation, multiple slits); Questions 1–3 SL |
| Value–unit notation, 2 significant figures | Conforms; in Question 3 the distances are to 3 significant figures (so that the path difference of 0.68 m stays at two significant figures) |

## Independent check

Date: 2026-10-11. This file was solved by an independent blind solver who did not see the answers; the solver independently reproduced all answer
keys and markscheme results (no CRITICAL findings). Findings:
[review/c3-review.md](review/c3-review.md). This does not replace expert review.

Changes made in response to the findings (every changed number was rechecked with `python3` against the final text of the file):

- **Question 6 (c) (MEDIUM):** slit width 0.10 mm → 0.11 mm. So *d*/*b* changed from 5.0 (borderline case; answers of 9, 10 and 11 were all natural) to 4.55; the order-counting and width ÷ fringe spacing methods both give 9.
- **Question 6 (c)(i):** 6.3 × 10⁻³ rad (0.36°) → 5.8 × 10⁻³ rad (0.33°).
- **Question 6 (c)(ii):** the answer stayed 9; the second point of the markscheme "fifth-order fringe is missing" → "fringes of order up to 4 lie inside the central maximum"; the width ÷ spacing method (34.5 / 3.8 = 9.1) was added as an acceptance note; the [2 max] note was updated. The formula chain and the status note (4) changed accordingly.
- **Unchanged:** (b) and the 15.2 mm data; the 0.10 mm slit in Question 5 (Paper 1A) is a separate question and stayed the same.
- **Not applied:** moving the "coherent" condition in Question 6 (a) to a separate acceptance note, and the C/D distractors of Question 4. The review lists them as "doubtful" and the change is not considered necessary; left to the expert's decision.
