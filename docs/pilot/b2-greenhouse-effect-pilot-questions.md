# Pilot question set: B.2 The greenhouse effect

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node B.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; no PDF was opened.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. The Stefan-Boltzmann constant σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴ was used and is given in the question where
> needed; the data booklet value must be confirmed by an expert.
> **Not verified:** passed an independent blind solver; has not passed expert review; qualitative questions (Question 3, Questions 5a and 5c) cannot be checked by code;
> the planets are fictional and their data do not belong to a real celestial body; it has not been confirmed by an expert that the "effective emissivity" model in Question 5(d) matches the
> energy balance model expected by the guide; no expert check was made for resemblance to a known exam question.

## Scope table

| # | Section | Level | Outcome (B.2) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Solar constant, the S/4 average and albedo; mean absorbed intensity | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Energy balance for the equilibrium temperature; proportional reasoning | AO3 | — | 1 | Medium–hard |
| 3 | Paper 1A | SL | Infrared absorption by greenhouse gases (resonance model) | AO1 | — | 1 | Easy |
| 4 | Paper 1A | SL | Determining albedo from the energy balance | AO2 | — | 1 | Medium |
| 5 | Paper 2 | SL | The S/4 average; equilibrium temperature; mechanism of the greenhouse effect; emissivity | AO2–AO3 | Explain, Show that, Determine | 9 | Medium–hard |

This set does not cover all of B.2. Not covered: names of the main greenhouse gases and their natural / anthropogenic sources; absorption using the molecular energy
level model; causes of the enhanced greenhouse effect; direct calculation of emissivity from its definition; a two-layer energy balance
that treats the surface–atmosphere exchange separately; daily and seasonal variation of albedo.

Scope boundary check: the energy balance questions are at the single-layer level (Questions 1, 2, 4, 5b) or surface + effective emissivity (Question 5d);
they do not go beyond the surface–atmosphere exchange that the boundary allows. No derivatives or integrals.

---

## Question 1 — Paper 1A

A planet orbits a star. At the orbit of the planet, the intensity of the radiation from the star is 600 W m⁻². The albedo of the
planet is 0.30.

What is the mean power absorbed per unit area of the surface of the planet?

A. 45 W m⁻²
B. 105 W m⁻²
C. 150 W m⁻²
D. 420 W m⁻²

**Answer: B**

**Solution.** The planet intercepts the radiation over a cross-section π*R*², and the energy is spread over a surface 4π*R*²: the mean incident intensity is 600 / 4 = 150 W m⁻².
The absorbed fraction is 1 − 0.30 = 0.70. Mean absorbed intensity = 150 × 0.70 = 105 W m⁻².

| Option | Misconception |
|---|---|
| A | Albedo is taken to be the absorbed fraction (the reflected part is calculated): 600 × 0.30 / 4 = 45 |
| C | Albedo is not taken into account: 600 / 4 = 150 |
| D | The average over the surface is not taken (no division by 4): 600 × 0.70 = 420 |

---

## Question 2 — Paper 1A

A planet without an atmosphere radiates as a black body and has a uniform equilibrium surface temperature *T*. The planet is
moved to an orbit at **twice** the distance from its star. The albedo of the planet does not change.

What is the new equilibrium surface temperature of the planet?

A. *T* ⁄ 4
B. *T* ⁄ 2
C. *T* ⁄ √2
D. *T* ⁄ ⁴√2

**Answer: C**

**Solution.** The intensity of the star's radiation is inversely proportional to the square of the distance: the new intensity is *S*/4. Energy balance: (1 − α)*S*/4 = σ*T*⁴,
so *T* ∝ *S*<sup>1/4</sup>. New temperature = *T* × (1⁄4)<sup>1/4</sup> = *T* / √2 (≈ 0.71*T*).

| Option | Misconception |
|---|---|
| A | Temperature is taken as directly proportional to intensity (*T* ∝ *S*): *T* / 4 |
| B | Temperature is taken as inversely proportional to distance (*T* ∝ 1/*d*): *T* / 2 |
| D | Intensity is taken as inversely proportional to the distance rather than the distance squared (*S* ∝ 1/*d*): *T* × (1⁄2)<sup>1/4</sup> ≈ 0.84*T* |

---

## Question 3 — Paper 1A

Carbon dioxide in the atmosphere absorbs infrared radiation emitted by the surface of the Earth.

What is the reason that carbon dioxide molecules absorb this radiation strongly?

A. The frequency of the radiation matches a natural frequency of vibration of the molecules.
B. The photons of the radiation have enough energy to ionize the molecules.
C. The photons of the radiation have more energy than photons of visible light.
D. The molecules reflect the radiation back towards the surface.

**Answer: A**

**Solution.** Resonance model: the energy transfer is greatest when the frequency of the infrared radiation is close to the natural vibration frequency of the molecule;
the molecule absorbs the radiation and then re-emits it in all directions.

| Option | Misconception |
|---|---|
| B | Absorption is confused with ionization; the energy of an infrared photon is far too small for ionization |
| C | The photon energies of infrared and visible light are put in the wrong order (the frequency of infrared is lower) |
| D | The "greenhouse gases reflect heat" misconception; the process is absorption and re-emission in all directions, not reflection |

---

## Question 4 — Paper 1A

The mean intensity of the radiation from a star that is incident on a planet, averaged over the whole surface of the planet, is
340 W m⁻². The planet is in thermal equilibrium and radiates a mean intensity of 238 W m⁻² into space.

What is the albedo of the planet?

A. 0.18
B. 0.30
C. 0.43
D. 0.70

**Answer: B**

**Solution.** In equilibrium the absorbed intensity equals the emitted intensity: 238 W m⁻². Reflected (scattered) intensity = 340 − 238 = 102 W m⁻².
Albedo = reflected / incident = 102 / 340 = 0.30.

| Option | Misconception |
|---|---|
| A | The reflected power is divided by the sum of the incident and emitted intensities: 102 / (340 + 238) = 0.18 |
| C | The reflected power is divided by the absorbed power instead of the incident power: 102 / 238 = 0.43 |
| D | The absorbed fraction is taken to be the albedo: 238 / 340 = 0.70 |

---

## Question 5 — Paper 2 (9 marks)

A planet orbits a star. At the orbit of the planet, the intensity of the radiation from the star is 880 W m⁻². The albedo of the
planet is 0.28.

Stefan-Boltzmann constant σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴

**(a)** Explain why the mean intensity of the radiation from the star, averaged over the whole surface of the planet, is
220 W m⁻². [2]

**(b)** Show that, if the planet had no atmosphere and radiated as a black body, its equilibrium surface temperature would be
about 230 K. [3]

The planet has an atmosphere that contains carbon dioxide. The measured mean surface temperature of the planet is 260 K.

**(c)** Explain how the carbon dioxide in the atmosphere causes the surface temperature to be higher than the value in (b). [2]

In a simple model, the planet together with its atmosphere radiates into space as a body of temperature 260 K and emissivity *e*.

**(d)** Determine *e*. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | the planet intercepts the radiation over «its cross-sectional» area π*R*² ✓<br>this power is averaged over the «whole» surface area 4π*R*², «so the mean intensity is 880 / 4» ✓ | *OWTTE*<br>*Do not award marks for "880 / 4 = 220" without a reason.* | 2 |
| 5. | b | | absorbed intensity = 0.72 × 220 «= 158 W m⁻²» ✓<br>158.4 = 5.67 × 10⁻⁸ × *T*⁴ **OR** *T* = (158.4 / 5.67 × 10⁻⁸)<sup>1/4</sup> ✓<br>*T* = 229.9 «K» ✓ | *Answer 230 K is given; award the third mark only if 229.9 or the complete substitution is seen.* | 3 |
| 5. | c | | carbon dioxide absorbs «some of» the infrared radiation emitted by the surface ✓<br>and re-emits it in all directions, so part of it returns to the surface ✓<br>the surface receives more power «than from the star alone» and must be at a higher temperature to radiate enough for equilibrium ✓ | *OWTTE*<br>*Do not accept "reflects" or "traps heat" for the second mark.* | 2 max |
| 5. | d | | *e* × 5.67 × 10⁻⁸ × 260⁴ = 158 **OR** *e* = (230 / 260)⁴ ✓<br>*e* = 0.61 ✓ | *Allow ECF from (b).*<br>*Both routes give 0.61. Accept 0.62 from the absorbed intensity rounded to 160 W m⁻².*<br>*Do not award marks for e = 1 − albedo = 0.72.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `S = 880 W/m^2`, `albedo = 0.28`, `T_s = 260 K`; constant `sigma = 5.67e-8 W/(m^2 K^4)` | |
| `I_mean` | `S/4` | 220 W m⁻² |
| `I_abs` | `(1 - albedo)*I_mean` | 158.4 W m⁻² |
| `T_eq` | `(I_abs/sigma)**0.25` | 229.9 K |
| `I_bb` | `sigma*T_s**4` | 259.1 W m⁻² |
| `e` | `I_abs/I_bb` | 0.611 (the `(230/T_s)**4` route gives 0.612) |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one under another | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Question 1 ascending; Question 2 ascending (0.25*T*, 0.50*T*, 0.71*T*, 0.84*T*); Question 4 ascending; Question 3 has sentence options (a minority format in the profile) |
| 1A: negation / key word in bold | Question 2 ("twice") conforms; no negative stem |
| 1A: position of the correct answer balanced | B, C, A, B (no D; a result of the distractor change in Question 4, see "Independent check" below) |
| 1A: solvable without a figure | Questions 1–4 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 3, 2, 2; total 9) |
| Paper 2: at least one AO3 part; "Show that" pattern | Question 5 conforms: (a), (c) Explain; (b) Show that; (d) Determine |
| Markscheme: four-column table, ✓, « », OR, max, ECF, OWTTE | Question 5 conforms; (c) "2 max" (two of three points) |
| Value–unit notation (W m⁻²), 2–3 significant figures | Conforms |
| Paper 2: figure | For Question 5(a) a diagram of the cross-sectional area / sphere surface would be useful but is not required; not produced |
| Paper 2: answer box, dotted lines | Not in this draft; will be added in the publication template |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver independent of its author, without seeing the answers; all answer keys and
markscheme results were reproduced independently (no CRITICAL findings). Detail: [review/b2-review.md](review/b2-review.md).
This check does not replace expert review.

Changes made as a result of the review (every changed number was recalculated with `python3`):

- **Question 5, MEDIUM-1 and MEDIUM-2:** the data were redesigned: albedo 0.25 → 0.28, measured surface temperature 250 K → 260 K. Results:
  absorbed intensity 165 → 158.4 W m⁻²; (b) 232.3 K → 229.9 K ("about 230 K" is now nearly exact); (d) 0.745 / 0.716 (depending on the route) →
  0.61 by both routes (0.611 and 0.612). The wrong method "e = 1 − albedo" now gives 0.72 and no longer coincides with the correct answer; this is stated explicitly in the markscheme
  note. The 0.72–0.75 accept range was removed. (a) unchanged.
- **Question 4, LOW-1:** the physically impossible distractor 1.4 was replaced by 0.18 (102 / 578 = 0.176). The options were put in
  ascending order (0.18, 0.30, 0.43, 0.70); the correct answer changed from D to B. There is a single correct option; no two options are equal after rounding.
  Side effect: the positions of the correct answers in the file changed from B, C, A, D to B, C, A, B.
- **LOW-2 (9 marks in an SL short question) and LOW-3 (agreement of the effective emissivity model with the guide):** no change made; both are
  records awaiting expert confirmation.
