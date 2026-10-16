# Pilot question set: E.2 Quantum physics

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> Authoring criteria: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Structure example: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
> This file also contains the single Paper 1B question requested for theme E (Question 6).
>
> **Source:** only syllabus node E.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and general
> physics. No exam paper, markscheme, textbook or internet question was used as input; the scenarios are original inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate `python3` calculation. Constants
> used: h = 6.63 × 10⁻³⁴ J s, c = 3.00 × 10⁸ m s⁻¹, e = 1.60 × 10⁻¹⁹ C, electron mass 9.11 × 10⁻³¹ kg, Compton constant
> h/m<sub>e</sub>c = 2.43 × 10⁻¹² m (data booklet values must be confirmed by an expert).
> **Not verified:**
> - Passed an independent blind solver; has not passed expert review (see "Independent check" at the end). It was not examined by an
>   expert for resemblance to any known exam question.
> - The work functions in Question 1 and Question 6 (2.9 eV, about 2.1 eV) are not attributed to a specific metal; that they are of a
>   realistic size for alkali and alkaline earth metals is general knowledge from memory.
> - The data table in Question 6 is not a real measurement: a scatter of ±0.01–0.02 V was added by hand to theoretical values generated with φ = 2.1 eV and h = 6.63 × 10⁻³⁴ J s.
>   The gradient and intercept values were calculated from this table by code (see Figure note).
> - In Question 5 a non-relativistic calculation was used for the electron accelerated through 150 V (v ≈ 0.024c; the correction is negligible). That a ring
>   pattern forms with a graphite film is general knowledge; the numerical values of the ring diameters are not asked.
> - It was not confirmed in which form the data booklet gives the Compton formula and the value of h/m<sub>e</sub>c; in Question 3 both are given in the question.

## Scope table

| # | Section | Level | Outcome (E.2) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | HL | Photoelectric equation; work function; maximum kinetic energy | AO2 | — | 1 | Easy |
| 2 | Paper 1A | HL | de Broglie wavelength; combining λ = h/p with kinetic energy | AO3 | — | 1 | Medium |
| 3 | Paper 1A | HL | Compton scattering; wavelength shift | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Photoelectric observation not explained by the wave model; threshold frequency | AO2 | — | 1 | Medium |
| 5 | Paper 2 | HL | Particle diffraction; de Broglie wavelength; wave–particle duality | AO2–AO3 | Show, Outline, Predict, Calculate | 9 | Medium |
| 6 | Paper 1B | HL | h and work function from stopping potential–frequency data; uncertainty; systematic error | AO2–AO3 | Outline, Calculate, Determine, Explain | 10 | Medium–hard |

This set does not cover all of E.2. What is missing: quantitative interpretation of the effect of intensity on photocurrent, direct
calculation of the threshold frequency, interpretation of Compton scattering as evidence for the particle nature of light (energy and
momentum loss of the scattered photon), and treatment of the angle dependence of the Compton shift in a structured question.

---

## Question 1 — Paper 1A

Light of wavelength 310 nm is incident on a clean metal surface in a vacuum. The work function of the metal is 2.9 eV.

What is the maximum kinetic energy of the electrons emitted from the surface?

A. 1.1 eV
B. 2.9 eV
C. 4.0 eV
D. 6.9 eV

**Answer: A**

**Solution.** Photon energy = hc / λ = (6.63 × 10⁻³⁴ × 3.00 × 10⁸) / (310 × 10⁻⁹) = 6.42 × 10⁻¹⁹ J = 4.0 eV.
E<sub>max</sub> = hf − Φ = 4.0 − 2.9 = 1.1 eV.

| Option | Misconception |
|---|---|
| B | Thinks the work function is the energy the electron receives |
| C | Does not subtract the work function; takes the whole photon energy as kinetic energy: 4.0 eV |
| D | Adds the work function instead of subtracting it: 4.0 + 2.9 = 6.9 eV |

---

## Question 2 — Paper 1A

An alpha particle and a proton have the same kinetic energy. Both move at speeds much less than the speed of light. The mass of the
alpha particle is four times the mass of the proton.

What is the ratio (de Broglie wavelength of the alpha particle) / (de Broglie wavelength of the proton)?

A. 1/4
B. 1/2
C. 1
D. 2

**Answer: B**

**Solution.** E<sub>k</sub> = p² / 2m → p = √(2mE<sub>k</sub>). λ = h / p ∝ 1 / √m (for the same E<sub>k</sub>).
Oran = √(m<sub>p</sub> / m<sub>α</sub>) = √(1/4) = 1/2.

| Option | Misconception |
|---|---|
| A | Takes λ ∝ 1/m (assumes the speeds are equal): 1/4 |
| C | Thinks particles with equal kinetic energy have equal wavelengths (applies a relation valid for photons to matter) |
| D | Inverts the ratio: √(m<sub>α</sub> / m<sub>p</sub>) = 2 |

---

## Question 3 — Paper 1A

A photon of wavelength 3.00 pm is scattered by an electron that is initially at rest. The photon is scattered through an angle of
180°. The change in wavelength of a photon scattered through an angle *θ* is

Δ*λ* = (*h* / *m*<sub>e</sub>*c*)(1 − cos *θ*)

where *h* / *m*<sub>e</sub>*c* = 2.43 pm.

What is the wavelength of the scattered photon?

A. 3.00 pm
B. 4.86 pm
C. 5.43 pm
D. 7.86 pm

**Answer: D**

**Solution.** Δλ = 2.43 × (1 − cos 180°) = 2.43 × 2 = 4.86 pm. The wavelength of the scattered photon = 3.00 + 4.86 = 7.86 pm.

| Option | Misconception |
|---|---|
| A | Takes cos 180° = +1; the shift comes out as zero |
| B | Takes the wavelength shift to be the wavelength of the scattered photon: 4.86 pm |
| C | Takes the factor (1 − cos θ) as 1 (the value for 90°): 3.00 + 2.43 = 5.43 pm |

---

## Question 4 — Paper 1A

Monochromatic light is incident on a metal surface and the emission of photoelectrons is investigated.

Which observation **cannot** be explained by the wave model of light?

A. The photoelectric current is proportional to the intensity of the light.
B. Energy is transferred from the light to electrons in the metal.
C. No electrons are emitted below a certain frequency, however intense the light.
D. The emitted electrons have a range of kinetic energies.

**Answer: C**

**Solution.** In the wave model energy is transferred continuously; light that is intense enough (or lasts long enough) should be able to
release electrons whatever its frequency. A threshold frequency independent of intensity can only be explained by photons of energy hf.

| Option | Misconception |
|---|---|
| A | Thinks every prediction of the photon model contradicts the wave model; more electrons being emitted as intensity increases is also consistent with the wave model |
| B | Thinks energy transfer is specific to the particle model; waves also carry energy |
| D | Thinks a range of kinetic energies is evidence for photons; electrons being at different depths and binding energies in the metal gives a range in both models |

---

## Question 5 — Paper 2 (9 marks)

Electrons are accelerated from rest through a potential difference of 150 V in a vacuum tube. The electron beam passes through a
thin film of graphite and then strikes a fluorescent screen. A pattern of bright concentric rings is seen on the screen.

> **Figure:** Evacuated glass tube. Electron gun on the left (150 V between cathode and anode), a thin graphite film in the middle, a
> fluorescent screen on the right. On the screen, concentric bright rings around the central bright spot. Diagram not to scale.

**(a)** Show that the de Broglie wavelength of the electrons is about 1.0 × 10⁻¹⁰ m. [3]

**(b)** Outline how the pattern on the screen provides evidence for the wave nature of electrons. [2]

The accelerating potential difference is increased.

**(c)** Predict, with a reason, the change in the diameters of the rings. [2]

**(d)** Calculate, in eV, the energy of a photon that has the same wavelength as the electrons in (a). [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | kinetic energy = *eV* = 1.60 × 10⁻¹⁹ × 150 «= 2.4 × 10⁻¹⁷ J» ✓<br>*p* = √(2*m*<sub>e</sub>*E*<sub>k</sub>) = √(2 × 9.11 × 10⁻³¹ × 2.4 × 10⁻¹⁷) «= 6.6 × 10⁻²⁴ kg m s⁻¹» **OR** *v* = 7.3 × 10⁶ «m s⁻¹» ✓<br>*λ* = 6.63 × 10⁻³⁴ / 6.61 × 10⁻²⁴ = 1.00 × 10⁻¹⁰ «m» ✓ | *Answer must be given to at least 3 s.f. (1.00 × 10⁻¹⁰) from a visible substitution for MP3.* | 3 |
| 5. | b | | the rings are a diffraction / interference pattern ✓<br>diffraction / interference is a property of waves **OR** particles alone would give a single spot / no rings ✓ | *OWTTE*<br>*Accept reference to the spacing of atoms in graphite being comparable to the wavelength for MP2.* | 2 |
| 5. | c | | «greater speed / momentum so» the de Broglie wavelength decreases ✓<br>diffraction angles are smaller so the diameters decrease ✓ | *MP2 requires the direction of the change in diameter.* | 2 |
| 5. | d | | *E* = *hc* / *λ* = 6.63 × 10⁻³⁴ × 3.00 × 10⁸ / 1.0 × 10⁻¹⁰ «= 1.99 × 10⁻¹⁵ J» ✓<br>= 1.2 × 10⁴ «eV» ✓ | *Allow ECF from (a).* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `V = 150 V`, constants `e = 1.60e-19`, `m_e = 9.11e-31`, `h = 6.63e-34`, `c = 3.00e8` | |
| `E_k` | `e*V` | 2.40 × 10⁻¹⁷ J |
| `p` | `sqrt(2*m_e*E_k)` | 6.61 × 10⁻²⁴ kg m s⁻¹ |
| `lambda` | `h/p` | 1.003 × 10⁻¹⁰ m |
| `E_photon` | `h*c/lambda/e` | 1.240 × 10⁴ eV (1.243 × 10⁴ eV with λ = 1.0 × 10⁻¹⁰ m) |

---

## Question 6 — Paper 1B (10 marks)

A student investigates the photoelectric effect using a vacuum photocell. Light from one of five light-emitting diodes (LEDs), each
emitting light of a different frequency *f*, is incident on the metal cathode of the photocell. A variable potential difference is
applied so that the anode is negative with respect to the cathode. For each LED the student increases the potential difference
until the photoelectric current just falls to zero and records this stopping potential *V*<sub>s</sub>.

> **Figure:** Circuit diagram. A photocell (cathode and anode), a sensitive ammeter connected in series with it, a voltmeter connected in
> parallel with the photocell, and a direct-current supply connected through a potentiometer; the anode is connected to the negative terminal of the supply. The LED illuminates the cathode.

| *f* / 10¹⁴ Hz | *V*<sub>s</sub> / V ± 0.04 V |
|---|---|
| 6.0 | 0.38 |
| 6.5 | 0.60 |
| 7.0 | 0.79 |
| 7.5 | 1.02 |
| 8.0 | 1.21 |

The uncertainty in *f* is negligible.

**(a)** Outline why a graph of *V*<sub>s</sub> against *f* is expected to be a straight line. [2]

**(b)** Calculate the percentage uncertainty in *V*<sub>s</sub> for the lowest frequency. [1]

The student plots *V*<sub>s</sub> against *f* with uncertainty bars. The gradient of the line of best fit is 4.16 × 10⁻¹⁵ V s. The
lines of maximum and minimum gradient have gradients of 4.55 × 10⁻¹⁵ V s and 3.75 × 10⁻¹⁵ V s. The line of best fit crosses the
*f*-axis at 5.08 × 10¹⁴ Hz.

**(c)** Determine the value of the Planck constant given by this experiment, with its absolute uncertainty. [3]

**(d)** Determine, in eV, the work function of the cathode using the line of best fit. [2]

**(e)** The student later finds that the voltmeter reads 0.05 V when the potential difference across it is zero. Explain the effect
of this error on the value of the Planck constant obtained in (c). [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *eV*<sub>s</sub> = *hf* − *Φ* **OR** maximum kinetic energy = *eV*<sub>s</sub> AND *E*<sub>max</sub> = *hf* − *Φ* ✓<br>*V*<sub>s</sub> = (*h*/*e*)*f* − *Φ*/*e* so the gradient *h*/*e* is constant / this has the form *y* = *mx* + *c* ✓ | | 2 |
| 6. | b | | «0.04 / 0.38 × 100 =» 11 «%» ✓ | *Accept 10 % or 10.5 %.* | 1 |
| 6. | c | | *h* = *e* × gradient = 1.60 × 10⁻¹⁹ × 4.16 × 10⁻¹⁵ «= 6.66 × 10⁻³⁴ J s» ✓<br>uncertainty in gradient = (4.55 − 3.75) × 10⁻¹⁵ / 2 = 0.40 × 10⁻¹⁵ «V s» ✓<br>*h* = (6.7 ± 0.6) × 10⁻³⁴ «J s» ✓ | *MP3: uncertainty to 1 s.f. and value to the same decimal place.*<br>*Allow (6.66 ± 0.64) × 10⁻³⁴ for MP1 and MP2 only.* | 3 |
| 6. | d | | *Φ* = *hf*₀ **OR** *Φ*/*e* = gradient × intercept on the *f*-axis ✓<br>«4.16 × 10⁻¹⁵ × 5.08 × 10¹⁴ =» 2.1 «eV» ✓ | *Allow ECF from (c).*<br>*Allow use of h = 6.63 × 10⁻³⁴ J s, also giving 2.1 eV.* | 2 |
| 6. | e | | every reading of *V*<sub>s</sub> is too large by the same amount / the line is shifted «upwards» parallel to itself / systematic error ✓<br>the gradient is unchanged so the value of *h* is not affected ✓ | *OWTTE*<br>*Do not award MP2 for "h is too large".* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `grad = 4.16e-15`, `grad_max = 4.55e-15`, `grad_min = 3.75e-15`, `f0 = 5.08e14`, `dV = 0.04`, `V1 = 0.38`, constant `e = 1.60e-19` | |
| `pct` | `dV/V1*100` | 10.5 % |
| `h` | `e*grad` | 6.66 × 10⁻³⁴ J s |
| `d_grad` | `(grad_max - grad_min)/2` | 0.40 × 10⁻¹⁵ V s |
| `d_h` | `e*d_grad` | 0.64 × 10⁻³⁴ J s |
| `phi_eV` | `grad*f0` | 2.11 eV |

### Figure note

The version shown to the student includes, together with the table, a *V*<sub>s</sub>–*f* graph with uncertainty bars. The graph is generated
by code from the same data (D-14). The least-squares gradient calculated from the data in the table is 4.16 × 10⁻¹⁵ V s, the vertical intercept is −2.11 V and the *f*-axis intercept is
5.08 × 10¹⁴ Hz. The gradients of the lines through the ends of the uncertainty bars of the first and last points are 4.55 × 10⁻¹⁵ and 3.75 × 10⁻¹⁵ V s.
These are the values given in the question. The value found, h = (6.7 ± 0.6) × 10⁻³⁴ J s, is consistent with the accepted value (6.63 × 10⁻³⁴ J s).

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?" / "Which …?") + A–D listed vertically | Questions 1–4 conform |
| 1A: four options of the same type, in the same unit, in order of magnitude | Questions 1–3 conform (ascending); Question 4 has options in sentence form (a minority form in the profile) |
| 1A: negative word in bold | Question 4 ("cannot") conforms |
| 1A: balanced position of the correct answer | A, B, D, C |
| Scope limit: no derivation of the Compton formula | In Question 3 the formula and constant are given in the question; only application is asked |
| Paper 2: sub-part at most 3 marks; short question 4–9 marks | Question 5 conforms (3, 2, 2, 2; total 9) |
| Paper 2: at least one AO3 part; "Show that" pattern | (a) Show that, (c) Predict; (d) uses the given approximate value |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE | Questions 5 and 6 conform |
| 1B: experiment question of about 10 marks, sub-parts 1–3 marks | Question 6 conforms (2, 1, 3, 2, 2; total 10) |
| 1B: table heading "quantity / unit ± uncertainty" | Question 6 conforms |
| 1B: student draws the line of best fit on the given graph and finds the gradient themselves | **Question 6 does not conform:** because the graph could not be generated, the gradients and axis intercept are given in the text. Once the graph template is ready, (c) and (d) must be rewritten |
| 1B: apparatus diagram | Described in text only; no drawing was produced |
| Value–unit notation, significant figures | Conforms; in 1B the gradients are given to 3 significant figures, the result is rounded according to the uncertainty |
| Level label | All questions HL (E.2 is an HL-only node); Question 6 does not enter the SL Paper 1B pool |

## Independent check

Date: 2026-10-11. A blind solver other than the author solved the questions without seeing the answers; it independently reproduced all
answer keys and recalculated the nuclear equations (conservation of nucleon number and charge) and the Paper 1B gradients. Findings:
[review/e2-review.md](review/e2-review.md). No CRITICAL findings. This check does not replace expert review.

Changes made in response to the findings (every changed number was recalculated with `python3`):

- **Question 5 (a) (LOW):** "Show that" note "at least 2 s.f." → "at least 3 s.f. (1.00 × 10⁻¹⁰)".
- **Question 5 (d) (LOW):** the last row of the formula chain was split: 1.240 × 10⁴ eV (exact λ) and 1.243 × 10⁴ eV (λ = 1.0 × 10⁻¹⁰ m). The markscheme answer 1.2 × 10⁴ eV was not changed.
- **Question 6 (c)–(d) (LOW):** no change made; that the gradients are given in the text is already recorded as "does not conform" in the "Format conformance" table and depends on the graph template.
- **Question 4:** the solver confirmed the single correct answer (C) and recommended that option D not be changed; it was not changed.
