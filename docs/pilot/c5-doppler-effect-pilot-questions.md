# Pilot question set: C.5 Doppler effect

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written to the [authoring standard](AUTHORING_STANDARD.md), with the same structure as the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node C.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook or internet question was used as input; the scenarios are original.
> **Numerical check:** all numerical answers and all numerical distractors were recomputed with `python3` (standard library only).
> Constants: c = 3.00 × 10⁸ m s⁻¹; speed of sound in air 340 m s⁻¹ (given in every question where it is used). Data booklet values should be confirmed
> by an expert.
> **Not verified:** (1) it was solved by an independent blind solver; it has not been through expert review; (2) it has not been checked by an expert
> for similarity to a known exam question; (3) in Questions 3 and 4 the distractors are numerically close to the correct answer (680 / 671 Hz; 720 / 727 Hz) — this is a deliberate
> choice (distinguishing the two formulae) but an expert may find it too subtle; (4) in Question 5 an ultrasound emitter of 40.0 kHz and, for a drone,
> 16 m s⁻¹ (about 58 km h⁻¹) are reasonable magnitudes but were not confirmed from a source; (5) in Question 5 (d) the difference between the two cases is 0.1 kHz
> and is visible at 3 significant figures, but the detector is assumed to measure at this resolution;
> (6) the qualitative parts (Question 2, Question 5 a) cannot be verified by code.

## Scope table

| # | Section | Level | Outcome (C.5) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Doppler effect for light: Δλ/λ ≈ v/c; shift of a spectral line | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Qualitative description of the Doppler effect for sound (source approaching at constant speed) | AO3 | — | 1 | Medium |
| 3 | Paper 1A | HL | Sound: moving-source formula | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Sound: moving-observer formula | AO2 | — | 1 | Medium |
| 5 | Paper 2 | HL | Explanation using wavefronts; moving source; comparison with a moving observer | AO2–AO3 | Explain, Show that, Calculate, Discuss | 9 | Medium–hard |

This set does not cover all of C.5. Not covered: drawing a wavefront diagram; calculation using the frequency shift for light (Δf/f);
blueshift; determining the direction of velocity from the shift of a spectral line; applications of the Doppler effect (e.g. line broadening in rotating bodies).

Limit check: in no question do the source and the observer move at the same time. In Question 5 (d) two separate cases are compared (first only
the source moving, then only the observer moving).

---

## Question 1 — Paper 1A

A spectral line has a wavelength of 650 nm when measured in a laboratory on Earth. The same line is observed in the light from a
galaxy that is moving away from Earth at a speed of 6.0 × 10⁶ m s⁻¹.

What is the wavelength of the line observed in the light from the galaxy?

A. 637 nm
B. 650 nm
C. 663 nm
D. 676 nm

**Answer: C**

**Solution.** Δλ / λ ≈ v / c = 6.0 × 10⁶ / 3.00 × 10⁸ = 0.020. Δλ = 0.020 × 650 = 13 nm. Because the source is receding, the wavelength increases:
650 + 13 = 663 nm.

| Option | Misconception |
|---|---|
| A | Takes the direction of the shift the wrong way round (as for an approaching source): 650 − 13 = 637 nm |
| B | Assumes the motion of the source changes only the frequency and that the wavelength stays the same |
| D | Doubles the shift (the idea that the light makes a "round trip"): 650 + 2 × 13 = 676 nm |

---

## Question 2 — Paper 1A

A train moves at a constant speed directly towards a stationary observer. The train sounds a horn that emits sound of constant
frequency *f*. The air is still.

What describes the frequency of the sound heard by the observer while the train is approaching?

A. Higher than *f* and increasing
B. Higher than *f* and constant
C. Equal to *f*
D. Lower than *f* and constant

**Answer: B**

**Solution.** While the source moves towards the observer, successive wavefronts get closer together in the region ahead; the wavelength at the observer
decreases, the speed of sound is unchanged, and the frequency is greater than *f*. The shift depends on the speed of the source, not its distance; because the speed is constant and directly
towards the observer, the frequency heard is constant.

| Option | Misconception |
|---|---|
| A | Assumes the frequency increases as the distance decreases (what increases is the loudness; confuses frequency with intensity) |
| C | Assumes the frequency belongs only to the source and does not change with motion |
| D | Takes the direction of the shift the wrong way round (receding source) |

---

## Question 3 — Paper 1A

A siren on a vehicle emits sound of frequency 600 Hz. The vehicle moves at 40.0 m s⁻¹ directly towards a stationary observer. The
speed of sound in air is 340 m s⁻¹.

What is the frequency of the sound heard by the observer?

A. 529 Hz
B. 537 Hz
C. 671 Hz
D. 680 Hz

**Answer: D**

**Solution.** Moving source, approaching: f′ = f v / (v − u<sub>s</sub>) = 600 × 340 / (340 − 40) = 680 Hz.

| Option | Misconception |
|---|---|
| A | Moving-observer formula and the wrong direction (receding): 600 × (340 − 40) / 340 = 529 Hz |
| B | Correct formula, wrong direction (receding source): 600 × 340 / (340 + 40) = 537 Hz |
| C | Uses the moving-observer formula: 600 × (340 + 40) / 340 = 671 Hz. Applying the approximate relation valid for light (Δf/f ≈ v/c) to sound gives the same value: 600 + 600 × 40 / 340 = 671 Hz |

---

## Question 4 — Paper 1A

A stationary siren emits sound of frequency 800 Hz. A motorcyclist moves at 34.0 m s⁻¹ directly away from the siren. The speed of sound
in air is 340 m s⁻¹.

What is the frequency of the sound heard by the motorcyclist?

A. 720 Hz
B. 727 Hz
C. 880 Hz
D. 889 Hz

**Answer: A**

**Solution.** Moving observer, receding: f′ = f (v − u<sub>o</sub>) / v = 800 × (340 − 34) / 340 = 720 Hz.

| Option | Misconception |
|---|---|
| B | Uses the moving-source formula (receding): 800 × 340 / (340 + 34) = 727 Hz |
| C | Correct formula, wrong direction (approaching observer): 800 × (340 + 34) / 340 = 880 Hz |
| D | Moving-source formula and the wrong direction: 800 × 340 / (340 − 34) = 889 Hz |

Note: 34.0 m s⁻¹ is about 122 km h⁻¹; this is realistic for a motorcyclist. The speed was not reduced, because at smaller speeds the difference between the key and
the moving-source distractor falls below 1 %.

---

## Question 5 — Paper 2 (9 marks)

A technician tests a small drone that carries an ultrasound transmitter. The transmitter emits sound of frequency 40.0 kHz. The
drone flies horizontally at a constant speed directly towards a stationary detector. The detector records a frequency of 42.0 kHz.
The speed of sound in air is 340 m s⁻¹ and the air is still.

> **Figure:** A drone (source) on the left, a stationary detector on the right; a velocity arrow pointing from the drone towards the detector. Around the drone, as wavefronts in the form of circles with their centres shifted to the left:
> closely spaced on the detector side, widely spaced at the back. "diagram not to scale". The question can be solved without
> the figure.

**(a)** Explain, with reference to wavefronts, why the frequency recorded by the detector is higher than 40.0 kHz. [2]

**(b)** Show that the speed of the drone is about 16 m s⁻¹. [2]

The drone now flies directly away from the detector at the same speed. Use a speed of 16 m s⁻¹ for the drone.

**(c)** Calculate the frequency recorded by the detector. [2]

**(d)** A student suggests that the detector would also record 42.0 kHz if the drone were stationary and the detector moved towards
the drone at 16 m s⁻¹. Discuss this suggestion. [3]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the drone / source moves towards the detector between emitting successive wavefronts, so the wavefronts are closer together / the wavelength «at the detector» is shorter ✓<br>the speed of sound «in air» is unchanged, so more wavefronts arrive per unit time / *f* = *v* / *λ* is greater ✓ | *OWTTE*<br>*Do not award the second mark if the speed of sound is said to increase.* | 2 |
| 5. | b | | 42.0 = 40.0 × 340 / (340 − *u*) ✓<br>*u* = 340 × (1 − 40.0 / 42.0) **OR** 16.2 «m s⁻¹» ✓ | *Use of the moving-observer equation gives 17.0 m s⁻¹, which does not match the target, and scores [0].*<br>*Answer must be seen to at least 3 s.f. or the rearrangement must be shown.* | 2 |
| 5. | c | | *f* = 40.0 × 340 / (340 + 16) ✓<br>= 38.2 «kHz» ✓ | *Accept u = 16.2 m s⁻¹, which also gives 38.2 kHz.* | 2 |
| 5. | d | | moving observer: *f* = 40.0 × (340 + 16) / 340 = 41.9 «kHz» ✓<br>this is less than 42.0 kHz / the two situations are described by different equations «because the motion is relative to the air» ✓<br>the suggestion is incorrect, although the difference is small «0.1 kHz» because the speed is much less than the speed of sound ✓ | *Third mark requires a conclusion supported by the values.*<br>*OWTTE* | 3 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `f = 40.0 kHz`, `f_obs = 42.0 kHz`, `v = 340 m/s`, `u_given = 16 m/s` | |
| `u` | `v*(1 - f/f_obs)` | 16.19 m s⁻¹ |
| `f_away` | `f*v/(v + u_given)` | 38.20 kHz (38.18 kHz with u = 16.19) |
| `f_moving_observer` | `f*(v + u_given)/v` | 41.88 kHz |
| `f_moving_source` | `f*v/(v - u_given)` | 41.98 kHz |
| `diff` | `f_moving_source - f_moving_observer` | 0.09 kHz (at 3 significant figures 42.0 − 41.9 = 0.1 kHz) |
| Check (wrong formula) | `v*(f_obs/f - 1)` | 17.0 m s⁻¹ — does not match the "about 16" target; scores no mark in (b) |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one below the other | Questions 1–4 conform (Question 2: "What describes …?") |
| 1A: four options of the same type, same unit, in order of magnitude | Questions 1, 3, 4 conform (ascending); Question 2 has short verbal statements, ordered from high to low |
| 1A: correct-answer letters balanced | C, B, D, A |
| 1A: solvable without a figure | Questions 1–4 need no figure |
| 1A: round, clean numbers | Correct answers are clean (663 nm, 680 Hz, 720 Hz); distractors rounded to 3 significant figures |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 2, 3; total 9) |
| Paper 2: "Show that" pattern and at least one AO3 part | Question 5 (a) Explain, (b) Show that, (d) Discuss; (c) and (d) use the given value of 16 m s⁻¹ ("Use a speed of 16 m s⁻¹" in the stem) |
| Markscheme: four-column table, ✓, « », OR, OWTTE | Question 5 conforms |
| Paper 2: figure | **Missing:** the wavefront diagram is described only in words |
| Syllabus limit: source and observer do not move together | Conforms; a context involving an echo (both source and observer roles) was deliberately not used |
| Level label | Questions 3, 4, 5 HL (moving-source / moving-observer formulae for sound); Questions 1 and 2 SL |
| Value–unit notation, significant figures | Conforms; in Question 5 the frequencies are to 3 significant figures (necessary because the shift is small) |

## Independent check

Date: 2026-10-11. This file was solved by an independent blind solver who did not see the answers; the solver independently reproduced all answer
keys and markscheme results (no CRITICAL findings). Findings:
[review/c5-review.md](review/c5-review.md). This does not replace expert review.

Changes made in response to the findings (every changed number was rechecked with `python3` against the final text of the file):

- **Question 5 (b) (MEDIUM):** recorded frequency 41.2 kHz → 42.0 kHz; target "about 10 m s⁻¹" → "about 16 m s⁻¹". The correct (moving-source) formula gives 16.19 m s⁻¹, the wrong (moving-observer) formula gives 17.0 m s⁻¹; the target now distinguishes the two methods (previously 9.90 and 10.2, both "about 10").
- **Question 5 (c):** 38.9 kHz → 38.2 kHz; the sentence "Use a speed of 16 m s⁻¹ for the drone" was added to the stem (LOW finding 5: the markscheme and the "same speed" wording now agree).
- **Question 5 (d) (MEDIUM):** comparison 41.18 / 41.21 kHz (both 41.2 at 3 significant figures) → 41.9 / 42.0 kHz; the difference is visible at the precision of the data. Markscheme conclusion "not exactly correct" → "incorrect, although the difference is small".
- **Question 5 context:** source bat → small drone carrying an ultrasound emitter. 16 m s⁻¹ is debatable for a bat and reasonable for a drone (about 58 km h⁻¹); the physics is the same. "the air is still" was added to the stem.
- **Question 4 (MEDIUM):** "cyclist" → "motorcyclist"; numbers and options unchanged (720, 727, 880, 889 Hz).
- **Questions 3 and 4 (LOW):** speeds were written to 3 significant figures: 40 → 40.0 m s⁻¹, 34 → 34.0 m s⁻¹. A second misconception route (applying the relation Δf/f ≈ v/c to sound) was added to distractor C of Question 3.
- **Not applied:** changing the observer speed in Question 4 to 68 m s⁻¹ (the review says "not mandatory"; the existing options are distinct at 3 significant figures) and distractor D of Question 1 ("doubtful"; the number is consistent).
