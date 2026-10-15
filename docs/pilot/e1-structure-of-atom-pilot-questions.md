# Pilot question set: E.1 Structure of the atom

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> Authoring criteria: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Structure example: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node E.1 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and general
> physics. No exam paper, markscheme, textbook or internet question was used as input; the scenarios are original inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3`. Constants
> used: h = 6.63 × 10⁻³⁴ J s, c = 3.00 × 10⁸ m s⁻¹, e = 1.60 × 10⁻¹⁹ C, k = 8.99 × 10⁹ N m² C⁻², R₀ = 1.20 × 10⁻¹⁵ m
> (the data booklet values should be confirmed by an expert).
> **Not verified:**
> - Passed an independent blind solver; has not passed expert review (see "Independent check" at the end). No expert check was made for similarity
>   to any known exam question.
> - Values written from memory: R₀ = 1.20 × 10⁻¹⁵ m (Question 6), Z = 50 for tin-120 (Question 6), and that an alpha energy of 5.5 MeV is realistic for a typical alpha
>   source. The energy levels in Question 2 do not belong to a real element; they are fictional and no atom name is given in the question.
> - That cool sodium vapour gives an absorption line in the visible region in Question 3 (a transition from the ground level) is based on general knowledge.
> - The "deviation threshold" estimate in Question 6 (c)(ii) ignores the radius of the alpha particle itself and the range of the strong force; the real
>   threshold is lower (about 18 MeV if the alpha radius is added). This assumption is now stated explicitly in the question stem and the part is asked with "Estimate";
>   an expert should confirm that this simplification is acceptable.

## Scope table

| # | Section | Level | Outcome (E.1) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Qualitative interpretation of the Geiger–Marsden–Rutherford experiment | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Discrete energy levels; photon energy E = hf = hc/λ | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Formation of an absorption spectrum; composition from a spectrum | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | R = R₀A^(1/3); nuclear density independent of A | AO3 | — | 1 | Medium |
| 5 | Paper 1A | HL | Bohr model: E = −13.6/n² eV; transition energies | AO2 | — | 1 | Medium |
| 6 | Paper 2 | HL | Distance of closest approach; nuclear radius; deviation from Rutherford scattering at high energy | AO2–AO3 | Show, Calculate, Explain, Estimate | 8 | Medium–hard |

This set does not cover all of E.1. Not covered: nuclear notation (proton, neutron, nucleon number), how an emission spectrum is obtained
experimentally, a quantitative example of determining composition from spectral lines, quantization of angular momentum in the Bohr model (mvr = nh/2π), numerical calculation of nuclear
density.

---

## Question 1 — Paper 1A

In the Geiger–Marsden–Rutherford experiment, alpha particles are directed at a thin gold foil. A few alpha particles are deflected
through angles greater than 90°.

Which feature of the atom is needed to explain these large deflections?

A. Most of the volume of the atom is empty space.
B. The positive charge is spread uniformly throughout the atom.
C. The electrons occupy discrete energy levels.
D. The positive charge and most of the mass are concentrated in a very small region.

**Answer: D**

**Solution.** A very large repulsive force is needed for an alpha particle to be scattered backwards. This can be explained only if the positive charge is concentrated in a small region
(a very strong field at close approach) and this region has a much greater mass than the alpha particle.

| Option | Misconception |
|---|---|
| A | Confused with the other observation of the experiment (most particles pass through undeflected); empty space does not explain large-angle deflection |
| B | Uses the uniformly distributed charge model (the pre-nucleus model); this model gives only very small deflections |
| C | Confuses the evidence from spectra with the evidence from scattering; energy levels are not a result of the scattering experiment |

---

## Question 2 — Paper 1A

The diagram shows three energy levels of an atom.

> **Figure:** An energy level diagram made of three horizontal lines. The lowest line is labelled −5.80 eV, the middle one −3.30 eV and the top one −1.20 eV.
> The diagram is not to scale. (The question can be solved without the figure, using these three values given in the text.)

The energies of the levels are −5.80 eV, −3.30 eV and −1.20 eV. Electron transitions take place between these levels.

What is the longest wavelength of the photons emitted in these transitions?

A. 270 nm
B. 497 nm
C. 592 nm
D. 1040 nm

**Answer: C**

**Solution.** The longest wavelength corresponds to the smallest energy difference. The differences are 2.50 eV, 2.10 eV, 4.60 eV. The smallest is 2.10 eV.
λ = hc / E = (6.63 × 10⁻³⁴ × 3.00 × 10⁸) / (2.10 × 1.60 × 10⁻¹⁹) = 5.92 × 10⁻⁷ m = 592 nm.

| Option | Misconception |
|---|---|
| A | Chooses the largest energy difference for the longest wavelength: 4.60 eV → 270 nm (misses that λ and E are inversely proportional) |
| B | Considers only the transition between the lowest two levels: 2.50 eV → 497 nm |
| D | Uses the magnitude of the energy of the top level instead of an energy difference: 1.20 eV → 1036 nm ≈ 1040 nm |

---

## Question 3 — Paper 1A

White light from a hot filament passes through cool, low-pressure sodium vapour. The transmitted light is then dispersed by a
diffraction grating and viewed on a screen.

What is observed on the screen?

A. A continuous spectrum crossed by dark lines at certain wavelengths that sodium can emit
B. Bright lines on a dark background at certain wavelengths that sodium can emit
C. A continuous spectrum with no lines
D. A continuous spectrum with brighter lines at certain wavelengths that sodium can emit

**Answer: A**

**Solution.** The atoms in the vapour absorb only photons whose energy equals the differences between energy levels; these are among the wavelengths the atom can emit
(in a cool vapour only transitions starting from the ground level). Because the absorbed energy is re-emitted in all directions, the intensity at these wavelengths is reduced in the direction of observation: dark lines
on a continuous spectrum (an absorption spectrum).

| Option | Misconception |
|---|---|
| B | Confuses an absorption spectrum with an emission spectrum; this picture is the spectrum given by hot vapour on its own |
| C | Thinks a low-pressure gas is completely transparent to light and does not interact with photons |
| D | Thinks the vapour "adds" its own lines to the transmitted light; misses that re-emission is in all directions |

---

## Question 4 — Paper 1A

Nucleus X has nucleon number 27 and nucleus Y has nucleon number 216.

What is the ratio (density of nucleus Y) / (density of nucleus X)?

A. 1/64
B. 1
C. 2
D. 8

**Answer: B**

**Solution.** Since R = R₀A^(1/3), volume ∝ R³ ∝ A. Mass is also ∝ A. Density = mass / volume is independent of A; the ratio is 1.

| Option | Misconception |
|---|---|
| A | Takes R ∝ A: mass ratio 8, volume ratio 8³ = 512; 8 / 512 = 1/64 |
| C | Divides by surface area instead of volume: radius ratio 2, area ratio 4; 8 / 4 = 2 |
| D | Treats the volumes of the two nuclei as equal; takes only the mass ratio: 216 / 27 = 8 |

---

## Question 5 — Paper 1A

In the Bohr model of the hydrogen atom, the energy of the level with quantum number *n* is −13.6 / *n*² eV. Photon P is emitted in
the transition from *n* = 3 to *n* = 2. Photon Q is emitted in the transition from *n* = 2 to *n* = 1.

What is the ratio (energy of photon P) / (energy of photon Q)?

A. 5/27
B. 1/3
C. 4/9
D. 1

**Answer: A**

**Solution.** E<sub>P</sub> = 13.6 (1/4 − 1/9) = 13.6 × 5/36 = 1.89 eV. E<sub>Q</sub> = 13.6 (1 − 1/4) = 13.6 × 3/4 = 10.2 eV.
Ratio = (5/36) / (3/4) = 5/27 ≈ 0.19.

| Option | Misconception |
|---|---|
| B | Takes the level energy as proportional to 1/n: (1/2 − 1/3) / (1 − 1/2) = 1/3 |
| C | Takes the ratio of level energies instead of photon energies: E₃ / E₂ = (1/9) / (1/4) = 4/9 |
| D | Thinks the levels are equally spaced; two successive transitions give the same energy |

---

## Question 6 — Paper 2 (8 marks)

Alpha particles of kinetic energy 5.5 MeV are directed at a thin tin foil. One alpha particle approaches a nucleus of tin-120
(¹²⁰₅₀Sn) head-on and comes to rest momentarily before returning along its original path. The recoil of the tin nucleus is negligible.

Coulomb constant *k* = 8.99 × 10⁹ N m² C⁻²; *R*₀ = 1.20 × 10⁻¹⁵ m.

**(a)** Show that the distance of closest approach of this alpha particle to the centre of the tin nucleus is about 2.6 × 10⁻¹⁴ m. [3]

**(b)** Calculate the radius of a tin-120 nucleus. [1]

The kinetic energy of the alpha particles is now increased. Above a certain energy, the number of alpha particles scattered at
large angles is different from that predicted by Rutherford scattering.

**(c)** (i) Explain why deviations from Rutherford scattering occur at high alpha particle energies. [2]

 (ii) Assume that the deviations begin when the distance of closest approach is equal to the radius of the tin-120 nucleus and
 that the alpha particle can be treated as a point. Estimate, in MeV, the alpha particle energy at which the deviations begin. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | «at closest approach» initial kinetic energy = electric potential energy **OR** *E*<sub>k</sub> = *k*(2*e*)(50*e*) / *d* ✓<br>*E*<sub>k</sub> = 5.5 × 10⁶ × 1.60 × 10⁻¹⁹ «= 8.8 × 10⁻¹³ J» ✓<br>*d* = 8.99 × 10⁹ × 100 × (1.60 × 10⁻¹⁹)² / 8.8 × 10⁻¹³ = 2.62 × 10⁻¹⁴ «m» ✓ | *Charges 2e and 50e must be seen or implied for MP1.*<br>*Answer must be given to at least 3 s.f. for MP3.* | 3 |
| 6. | b | | *R* = 1.20 × 10⁻¹⁵ × 120^(1/3) = 5.92 × 10⁻¹⁵ «m» ✓ | *Accept 5.9 × 10⁻¹⁵ m.* | 1 |
| 6. | c | i | alpha particle gets close enough to the nucleus for the strong nuclear force to act «on it» ✓<br>so the force is no longer only electric repulsion / the alpha particle may be attracted or absorbed, «changing the scattering pattern» ✓ | *OWTTE* | 2 |
| 6. | c | ii | use of *E* ∝ 1/*d* with *d* = *R* **OR** *E* = *k*(2*e*)(50*e*) / *R* ✓<br>*E* = 5.5 × (2.62 × 10⁻¹⁴ / 5.92 × 10⁻¹⁵) ≈ 24 «MeV» ✓ | *Allow ECF from (b).*<br>*Accept answers in the range 23–25 MeV.*<br>*The stem fixes the criterion d = R(Sn); do not award MP2 for 18 MeV obtained with R(Sn) + R(α).* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `E_MeV = 5.5`, `Z = 50`, `A = 120`, constants `k = 8.99e9`, `e = 1.60e-19`, `R0 = 1.20e-15` | |
| `E_k` | `E_MeV*1e6*e` | 8.80 × 10⁻¹³ J |
| `d` | `k*2*Z*e**2/E_k` | 2.615 × 10⁻¹⁴ m |
| `R` | `R0*A**(1/3)` | 5.92 × 10⁻¹⁵ m |
| `E_dev` | `E_MeV*d/R` | 24.3 MeV |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?" / "Which …?") + A–D listed vertically | Questions 1–5 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 2, 4, 5 conform (ascending); Questions 1 and 3 have sentence-form options (a minority format in the profile) |
| 1A: balanced position of the correct answer | D, C, A, B, A |
| 1A: solvable without the figure | Question 2: the figure is described; the values are also given in the text |
| Scope limit: at SL the experiment is only qualitative | Question 1 is qualitative; quantitative scattering is only in Question 6, labelled HL |
| Scope limit: only electrical repulsion in scattering | Question 6 (a) and (c)(ii) use only Coulomb potential energy; the strong force is only qualitative in (c)(i) |
| Scope limit: chemical symbols are not memorized | In Question 6 the symbol, Z and A are given in the question; in Question 3 the element name is written out |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 6 conforms (3, 1, 2, 2; total 8) |
| Paper 2: at least one AO3 part; "Show that" pattern | (a) Show that, (c)(i) Explain; (c)(ii) uses the given approximate value and the threshold criterion is written in the stem as an assumption |
| Markscheme: four-column table, ✓, « », OR, ECF, OWTTE | Question 6 conforms |
| Value–unit notation, significant figures | Conforms; in Question 2 the data are to 3 significant figures and the answer to 3 significant figures |
| Level label | Questions 1–3 SL; Questions 4–6 HL (additional HL content) |

## Independent check

Date: 2026-10-11. A blind solver other than the author solved the questions without seeing the answers; reproduced all answer keys independently,
recalculated the nuclear equations (conservation of nucleon number and charge) and the Paper 1B gradients. Findings:
[review/e1-review.md](review/e1-review.md). No CRITICAL findings. This check does not replace expert review.

Changes made in response to the findings (every changed number was recalculated with `python3`):

- **Question 6 (c)(ii) (MEDIUM):** the threshold criterion was added to the stem ("distance of closest approach is equal to the radius of the tin-120 nucleus … alpha particle … treated as a point"). The answer of 24 MeV and the 23–25 MeV range did not change; the markscheme note now says that, because the criterion is given in the stem, 18 MeV obtained with R(Sn) + R(α) does not score the final mark.
- **Question 6 (b) (LOW):** answer 5.9 × 10⁻¹⁵ m → 5.92 × 10⁻¹⁵ m; the note "Accept 5.9 × 10⁻¹⁵ m" was added. The (c)(ii) row was written with 2.62 × 10⁻¹⁴ / 5.92 × 10⁻¹⁵ (24.3 MeV).
- **Question 3 (LOW):** in options A, B and D, "at wavelengths that sodium emits" → "at certain wavelengths that sodium can emit"; the solution text was corrected accordingly. Answer A did not change.
