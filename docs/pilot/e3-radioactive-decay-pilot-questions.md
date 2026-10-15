# Pilot question set: E.3 Radioactive decay

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> Authoring criteria: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Structure example: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node E.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and general
> physics. No exam paper, markscheme, textbook or internet question was used as input; the scenarios are original inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate `python3` calculation. Constant
> used: 1 u = 931.5 MeV c⁻² (the data booklet value must be confirmed by an expert). In the decay equations, conservation of nucleon number and charge
> was checked by hand (Question 2: 22 = 22, 11 = 10 + 1; Question 6: 131 = 131, 53 = 54 − 1).
> **Not verified:**
> - Passed an independent blind solver; has not passed expert review (see "Independent check" at the end). It was not examined by an
>   expert for resemblance to any known exam question.
> - **Nuclear data written from memory (to be confirmed from a source):** lithium-7 nuclear mass 7.01436 u (obtained by subtracting
>   three electron masses from the atomic mass 7.01600 u), proton 1.00728 u, neutron 1.00866 u (Question 3); that sodium-22 decays to neon-22 by β⁺ and the Z
>   values (Na 11, Ne 10, Mg 12) (Question 2); the half-life of iodine-131 of 8.0 days, that it decays to xenon-131 by β⁻, and the Z values (I 53, Xe 54)
>   (Question 6). The result of Question 3 (5.6 MeV) agrees with the known binding energy per nucleon for lithium-7, but this too is from memory.
> - The sources in Question 1 and Question 4 are unnamed; the half-lives are fictional.
> - In Question 6 the gamma emission accompanying the decay of iodine-131 is not asked about; part (d) was written by restricting it to decays
>   that go to a given energy level of the product nucleus.

## Scope table

| # | Section | Level | Outcome (E.3) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Count rate, background radiation, half-life (whole number of half-lives) | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | β⁺ decay equation; neutrino | AO2 | — | 1 | Easy |
| 3 | Paper 1A | SL | Mass defect; binding energy; binding energy per nucleon | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Decay constant; T½ = ln 2/λ; A = λN | AO2 | — | 1 | Medium |
| 5 | Paper 1A | HL | Evidence for discrete nuclear energy levels | AO2 | — | 1 | Easy |
| 6 | Paper 2 | HL | λ and A = λN; arbitrary time interval using N = N₀e^(−λt); continuous β spectrum | AO2–AO3 | Show, Calculate, Determine, Explain | 9 | Medium–hard |

This set does not cover all of E.3. What is missing: the concept of isotopes, interpretation of the binding energy per nucleon curve, properties of the strong nuclear
force, the random and spontaneous nature of decay, α and γ equations, comparison of penetrating power and ionizing power,
calculation of decay energy using E = mc², neutron/proton ratio and stability (HL). There is no structured (Paper 2) question at SL level in this set.

---

## Question 1 — Paper 1A

A detector is placed at a fixed distance from a radioactive source and records a count rate of 180 min⁻¹. When the source is
removed, the detector records a background count rate of 20 min⁻¹. The half-life of the source is 3.0 hours.

What count rate does the detector record, with the source in place, 6.0 hours later?

A. 20 min⁻¹
B. 40 min⁻¹
C. 45 min⁻¹
D. 60 min⁻¹

**Answer: D**

**Solution.** Count rate due to the source = 180 − 20 = 160 min⁻¹. 6.0 hours = 2 half-lives → 160 / 4 = 40 min⁻¹. With the background included the detector
records 40 + 20 = 60 min⁻¹.

| Option | Misconception |
|---|---|
| A | Thinks decay is linear: assumes the source is completely used up in two half-lives and only the background remains |
| B | Subtracts the background but does not add it back to the result: 160 / 4 = 40 |
| C | Does not account for the background at all: 180 / 4 = 45 |

---

## Question 2 — Paper 1A

A nucleus of sodium-22 (²²₁₁Na) decays by β⁺ (positron) emission. The symbols for neon and magnesium are Ne and Mg.

Which are the other two products of this decay?

A. ²²₁₂Mg and an antineutrino
B. ²²₁₂Mg and a neutrino
C. ²²₁₀Ne and a neutrino
D. ²²₁₀Ne and an antineutrino

**Answer: C**

**Solution.** In β⁺ decay a proton changes into a neutron: the proton number decreases by 1 (11 → 10), the nucleon number does not change (22). A neutrino
is emitted together with the positron: ²²₁₁Na → ²²₁₀Ne + e⁺ + ν.

| Option | Misconception |
|---|---|
| A | Writes the products of β⁻ decay (Z increases, antineutrino) |
| B | Applies charge conservation incorrectly: thinks Z increases when a positron is emitted |
| D | Nucleus correct, but takes the accompanying particle to be an antineutrino as in β⁻ decay |

---

## Question 3 — Paper 1A

The mass of a lithium-7 nucleus (⁷₃Li) is 7.01436 u. The mass of a proton is 1.00728 u and the mass of a neutron is 1.00866 u.
1 u is equivalent to 931.5 MeV.

What is the binding energy per nucleon of lithium-7?

A. 5.6 MeV
B. 9.8 MeV
C. 13 MeV
D. 39 MeV

**Answer: A**

**Solution.** Mass defect = 3 × 1.00728 + 4 × 1.00866 − 7.01436 = 0.04212 u. Binding energy = 0.04212 × 931.5 = 39.2 MeV.
Per nucleon = 39.2 / 7 = 5.6 MeV.

| Option | Misconception |
|---|---|
| B | Divides by the number of neutrons instead of the number of nucleons: 39.2 / 4 = 9.8 MeV |
| C | Divides by the number of protons instead of the number of nucleons: 39.2 / 3 = 13.1 MeV |
| D | Gives the total binding energy; does not divide by the number of nucleons: 39.2 MeV |

---

## Question 4 — Paper 1A

A freshly prepared sample contains 4.0 × 10¹² nuclei of a radioactive nuclide. The half-life of the nuclide is 20 minutes.

What is the initial activity of the sample?

A. 1.7 × 10⁹ Bq
B. 2.3 × 10⁹ Bq
C. 3.3 × 10⁹ Bq
D. 1.4 × 10¹¹ Bq

**Answer: B**

**Solution.** T½ = 20 × 60 = 1200 s. λ = ln 2 / T½ = 5.78 × 10⁻⁴ s⁻¹. A = λN = 5.78 × 10⁻⁴ × 4.0 × 10¹² = 2.3 × 10⁹ Bq.

| Option | Misconception |
|---|---|
| A | Takes the average activity over one half-life: (N/2) / T½ = 2.0 × 10¹² / 1200 = 1.7 × 10⁹ |
| C | Forgets the factor ln 2 (λ = 1/T½): 4.0 × 10¹² / 1200 = 3.3 × 10⁹ |
| D | Does not convert the half-life to seconds: (ln 2 / 20) × 4.0 × 10¹² = 1.4 × 10¹¹ (decays per minute, not Bq) |

---

## Question 5 — Paper 1A

Several observations are made about the decay of a particular radioactive nuclide.

Which observation provides evidence that nuclei have discrete energy levels?

A. The beta particles emitted have a continuous range of energies.
B. The activity of a sample decreases exponentially with time.
C. The gamma photons emitted have only certain specific energies.
D. The moment at which an individual nucleus decays cannot be predicted.

**Answer: C**

**Solution.** A gamma photon is emitted in a transition of the nucleus between two energy levels; that the photons have only certain energies
shows that the levels are discrete (similar to the lines in atomic spectra).

| Option | Misconception |
|---|---|
| A | Takes the continuous β spectrum as evidence for levels; this observation shows that the energy is shared with a third particle (neutrino) |
| B | Relates exponential decrease to levels; this is a consequence of the decay probability being constant |
| D | Confuses randomness with quantization; unpredictability gives no information about energy levels |

---

## Question 6 — Paper 2 (9 marks)

A hospital stores a sealed sample of iodine-131. Iodine-131 decays by beta-minus emission to xenon-131:

¹³¹₅₃I → ¹³¹₅₄Xe + e⁻ + ν̄

The half-life of iodine-131 is 8.0 days. When the sample is delivered, the activity of the iodine-131 is 3.2 × 10⁵ Bq.

**(a)** Show that the decay constant of iodine-131 is about 1.0 × 10⁻⁶ s⁻¹. [2]

**(b)** Calculate the number of iodine-131 nuclei in the sample when it is delivered. [2]

The sample may be treated as ordinary waste when its activity has fallen to 5.0 × 10⁴ Bq.

**(c)** Determine, in days, the time after delivery at which the sample may be treated as ordinary waste. [3]

**(d)** For decays to a given energy level of the xenon-131 nucleus, the energy released is the same, but the beta particles are
emitted with a continuous range of kinetic energies. Explain this observation. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *T*½ = 8.0 × 24 × 3600 «= 6.91 × 10⁵ s» ✓<br>*λ* = ln 2 / 6.91 × 10⁵ = 1.00 × 10⁻⁶ «s⁻¹» ✓ | *Answer must be given to at least 3 s.f. (1.00 × 10⁻⁶) from a visible substitution for MP2.* | 2 |
| 6. | b | | *N* = *A* / *λ* **OR** 3.2 × 10⁵ / 1.0 × 10⁻⁶ ✓<br>*N* = 3.2 × 10¹¹ ✓ | | 2 |
| 6. | c | | 5.0 × 10⁴ = 3.2 × 10⁵ e^(−*λt*) **OR** number of half-lives = ln 6.4 / ln 2 «= 2.68» ✓<br>*t* = ln 6.4 / 1.0 × 10⁻⁶ «= 1.86 × 10⁶ s» ✓<br>*t* = 21 «days» ✓ | *Accept answers in the range 21–22 days.*<br>*Award [1 max] for "between 2 and 3 half-lives / between 16 and 24 days" with no further working.* | 3 |
| 6. | d | | an antineutrino is also emitted «in each decay» ✓<br>the energy released is shared between the beta particle and the antineutrino «and the recoiling nucleus» in varying proportions ✓ | *OWTTE*<br>*Accept "neutrino" for "antineutrino".* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `T_days = 8.0`, `A0 = 3.2e5 Bq`, `A1 = 5.0e4 Bq` | |
| `T` | `T_days*24*3600` | 6.912 × 10⁵ s |
| `lam` | `ln(2)/T` | 1.003 × 10⁻⁶ s⁻¹ |
| `N0` | `A0/lam` | 3.19 × 10¹¹ (3.2 × 10¹¹ with λ = 1.0 × 10⁻⁶ s⁻¹) |
| `t` | `ln(A0/A1)/lam` | 1.851 × 10⁶ s |
| `t_days` | `t/86400` | 21.4 days (21.5 days with λ = 1.0 × 10⁻⁶ s⁻¹) |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?" / "Which …?") + A–D listed vertically | Questions 1–5 conform |
| 1A: four options of the same type, in the same unit, in order of magnitude | Questions 1, 3, 4 conform (ascending); Question 2 is nucleus + particle pairs; Question 5 has options in sentence form |
| 1A: balanced position of the correct answer | D, C, A, B, C |
| 1A: table-style options could not be verified in the example | Question 2 gives two pieces of information in a one-line option ("… and a neutrino"); no table was used |
| Scope limit: only whole numbers of half-lives at SL | Question 1 (SL) is exactly 2 half-lives; an arbitrary time only in the HL-labelled Question 6 (c) |
| Scope limit: weak nuclear force is not in scope | No question or markscheme point refers to the weak force |
| Scope limit: no derivatives or integrals | Questions 4 and 6 use only A = λN and exponentials/logarithms |
| Chemical symbols are not to be memorised | In Questions 2, 3 and 6 the symbols and Z values are given in the question |
| Paper 2: sub-part at most 3 marks; short question 4–9 marks | Question 6 conforms (2, 2, 3, 2; total 9) |
| Paper 2: at least one AO3 part; "Show that" pattern | (a) Show that, (c) Determine, (d) Explain; (b) and (c) use the given approximate value |
| Markscheme: four-column table, ✓, « », OR, OWTTE, acceptance range | Question 6 conforms |
| Value–unit notation, 2 significant figures | Conforms; in Question 3 the masses are to 6 significant figures (needed for the mass defect), the answer to 2 significant figures |
| Level label | Questions 1–3 SL; Questions 4–6 HL (additional HL content) |

## Independent check

Date: 2026-10-11. A blind solver other than the author solved the questions without seeing the answers; it independently reproduced all
answer keys and recalculated the nuclear equations (conservation of nucleon number and charge) and the Paper 1B gradients. Findings:
[review/e3-review.md](review/e3-review.md). No CRITICAL findings. This check does not replace expert review.

Changes made in response to the findings (every changed number was recalculated with `python3`):

- **Question 6 (a) (LOW):** "Show that" note "at least 2 s.f." → "at least 3 s.f. (1.00 × 10⁻⁶)".
- **Question 6 (d) (LOW):** stem "The energy released in each decay is the same, but …" → "For decays to a given energy level of the xenon-131 nucleus, the energy released is the same, but …". The markscheme was not changed.
- **No SL Paper 2 question (LOW):** not implemented in this round. The finding is a request for a new question, not a correction; it remains in the list of gaps below the scope table and was left to the next authoring round.
