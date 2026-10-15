# Pilot question set: E.5 Fusion and stars

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> Authoring criteria: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Structure example: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node E.5 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and general
> physics. No exam paper, markscheme, textbook or internet question was used as input; the stars and scenarios are fictional.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate `python3` calculation. Constants
> used: σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴, luminosity of the Sun L☉ = 3.83 × 10²⁶ W, 1 pc = 3.26 ly, 1 ly = 9.46 × 10¹⁵ m (data booklet
> values must be confirmed by an expert).
> **Not verified:**
> - Passed an independent blind solver; has not passed expert review (see "Independent check" at the end). It was not examined by an
>   expert for resemblance to any known exam question.
> - Astrophysics facts from memory: that the luminosity of a main-sequence star at a temperature of 20 000 K is thousands of times that of the Sun
>   (the basis for the single correct answer in Question 3); that a star of 1.2 solar masses follows the red giant → planetary nebula → white dwarf path
>   (Question 6 (d)); that the fictional star in Question 6 (M = 1.2 M☉, L ≈ 1.9 L☉, T = 6200 K, R ≈ 1.2 R☉) is realistic for the main sequence
>   (the approximate relation L ∝ M^3.5 and R☉ = 6.96 × 10⁸ m are from memory; they are not used in the question).
> - In Question 6 the apparent brightness and the relation b = L/4πd² appear in the syllabus under B.1; they were used on the assumption that they are needed
>   for the E.5 outcome "determining stellar radius" and were recorded as a secondary node in the scope table.
> - Question 5 tests only the balance of pressure and gravity; heating of the contracting core (not explicitly stated in the syllabus analysis) is not asked.
>   That the outward pressure decreases when the rate of fusion decreases is given in the stem.
> - Question 6 (d): it was not confirmed whether numerical thresholds for stellar mass (supernova limit, etc.) are in scope; the mass was chosen to be
>   far from these thresholds.

## Scope table

| # | Section | Level | Outcome (E.5) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Distance from parallax angle; parsec–light year conversion | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Determining stellar radius from luminosity and temperature (ratio) | AO3 | — | 1 | Medium |
| 3 | Paper 1A | SL | Regions of the HR diagram | AO2 | — | 1 | Medium |
| 4 | Paper 1A | SL | Conditions for fusion: reason for high temperature | AO2 | — | 1 | Easy |
| 5 | Paper 1A | SL | Stellar equilibrium: radiation pressure and gravity | AO3 | — | 1 | Medium |
| 6 | Paper 2 | SL | Parallax → distance; unit conversion; luminosity (secondary node: B.1, b = L/4πd²); radius; effect of mass on evolution | AO2–AO3 | Show, Calculate, Determine, Outline | 9 | Medium |

This set does not cover all of E.5. What is missing: calculation of the energy released in fusion from the mass difference, the high density (pressure)
condition, evolution of massive stars (supergiant, supernova, neutron star, black hole), drawing the evolutionary path on the HR diagram,
AU conversion, the limit of the parallax method (nearby stars only).

---

## Question 1 — Paper 1A

The parallax angle of a star measured from Earth is 0.040 arc-seconds. 1 pc = 3.26 ly.

What is the distance from Earth to the star?

A. 0.13 ly
B. 7.7 ly
C. 25 ly
D. 82 ly

**Answer: D**

**Solution.** d (pc) = 1 / p (arc-seconds) = 1 / 0.040 = 25 pc. 25 × 3.26 = 81.5 ≈ 82 ly.

| Option | Misconception |
|---|---|
| A | Takes the distance as directly proportional to the parallax angle: 0.040 × 3.26 = 0.13 |
| B | Does the conversion the wrong way round: 25 / 3.26 = 7.7 |
| C | Does not convert the value found in parsecs to light years: 25 |

---

## Question 2 — Paper 1A

Star X has four times the luminosity of the Sun. The surface temperature of star X is half the surface temperature of the Sun.
Both stars radiate as black bodies.

What is the ratio (radius of star X) / (radius of the Sun)?

A. 0.5
B. 4
C. 8
D. 64

**Answer: C**

**Solution.** L = σ(4πR²)T⁴ → R² ∝ L / T⁴. Ratio of R² = 4 / (½)⁴ = 64. Ratio of radii = √64 = 8.

| Option | Misconception |
|---|---|
| A | Does not invert the temperature ratio: R² = 4 × (½)⁴ = 0.25 → 0.5 |
| B | Uses the wrong power of temperature (R ∝ √L / T): 2 / 0.5 = 4 |
| D | Does not take the square root; gives the ratio of R²: 64 |

---

## Question 3 — Paper 1A

On a Hertzsprung–Russell (HR) diagram, luminosity is plotted on the vertical axis and surface temperature on the horizontal axis.
A star has a surface temperature of 20 000 K and a luminosity of 0.01 *L*☉, where *L*☉ is the luminosity of the Sun.

> **Figure:** HR diagram. Vertical axis: luminosity / L☉, logarithmic scale, from 10⁻⁴ to 10⁶. Horizontal axis: surface temperature / K,
> decreasing from left to right (from 40 000 K to 2500 K). The main sequence is a band running from upper left to lower right; red giants and supergiants are at upper right;
> white dwarfs are at lower left. The regions are not labelled in the figure. (The question can be solved without the figure.)

Which type of star is this?

A. White dwarf
B. Main-sequence star
C. Red giant
D. Supergiant

**Answer: A**

**Solution.** The star is much hotter than the Sun but much dimmer; it is in the lower left region of the diagram. A low luminosity
at a high temperature requires a very small surface area: a white dwarf.

| Option | Misconception |
|---|---|
| B | Thinks the main sequence passes through every part of the diagram; a main-sequence star at this temperature is much brighter than the Sun |
| C | Associates low luminosity with a "cool and large" star; red giants are cool and brighter than the Sun |
| D | Interprets high temperature alone as a "very large star"; supergiants have a very high luminosity |

---

## Question 4 — Paper 1A

Nuclear fusion of hydrogen takes place in the core of a main-sequence star, where the temperature is very high.

Why is a very high temperature needed for fusion?

A. To remove the electrons from the hydrogen atoms
B. To give nuclei enough kinetic energy to overcome their electric repulsion
C. To increase the binding energy per nucleon of the hydrogen nuclei
D. To produce enough radiation pressure to balance gravity

**Answer: B**

**Solution.** Nuclei are positively charged and repel each other. For them to approach close enough for the strong nuclear force to take effect,
their kinetic energy, that is the temperature, must be very high.

| Option | Misconception |
|---|---|
| A | Confuses ionization with the condition for fusion; ionization takes place at much lower temperatures |
| C | Thinks binding energy changes with temperature; it is a property of the nucleus independent of temperature |
| D | Confuses the result of fusion (radiation pressure) with the condition for fusion |

---

## Question 5 — Paper 1A

A main-sequence star is in equilibrium. The rate of fusion in the core of the star then decreases, so that the outward force due to
radiation pressure in the core decreases.

What happens to the core as a result?

A. It contracts, because the gravitational force is now greater than the outward force due to pressure.
B. It expands, because the gravitational force is now less than the outward force due to pressure.
C. It stays the same size, because the gravitational force does not depend on the rate of fusion.
D. It expands, because a lower rate of fusion reduces the gravitational force on the core.

**Answer: A**

**Solution.** At equilibrium the inward gravitational force and the outward force due to pressure are equal. When the rate of fusion decreases the outward force decreases, the gravitational
force does not change; the resultant force is inward and the core contracts.

| Option | Misconception |
|---|---|
| B | Sets up the force balance the wrong way round: thinks decreasing pressure leads to expansion |
| C | Concludes from the gravitational force not changing that the equilibrium does not change either; equilibrium is the equality of two effects |
| D | Thinks gravity is caused by fusion or changes with the rate of fusion; gravity depends on the mass of the star |

---

## Question 6 — Paper 2 (9 marks)

Star K is a main-sequence star. Observations of star K from Earth give the following data.

| Parallax angle / arc-second | Apparent brightness / W m⁻² | Surface temperature / K |
|---|---|---|
| 0.125 | 9.5 × 10⁻¹⁰ | 6200 |

1 pc = 3.26 ly; 1 ly = 9.46 × 10¹⁵ m; *σ* = 5.67 × 10⁻⁸ W m⁻² K⁻⁴.

**(a)** Show that the distance from Earth to star K is about 2.5 × 10¹⁷ m. [2]

**(b)** Calculate the luminosity of star K. [2]

**(c)** Determine the radius of star K. [3]

**(d)** The mass of star K is 1.2 times the mass of the Sun. Outline the evolution of star K after it leaves the main sequence. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | *d* = 1 / 0.125 = 8.0 «pc» ✓<br>*d* = 8.0 × 3.26 × 9.46 × 10¹⁵ = 2.47 × 10¹⁷ «m» ✓ | *Answer must be given to at least 3 s.f. for MP2.* | 2 |
| 6. | b | | *L* = 4π*d*²*b* = 4π × (2.47 × 10¹⁷)² × 9.5 × 10⁻¹⁰ ✓<br>*L* = 7.3 × 10²⁶ «W» ✓ | *Allow use of 2.5 × 10¹⁷ m, giving 7.5 × 10²⁶ W.* | 2 |
| 6. | c | | *L* = *σ*(4π*R*²)*T*⁴ rearranged **OR** *R* = √(*L* / 4π*σT*⁴) ✓<br>correct substitution: *R*² = 7.3 × 10²⁶ / (4π × 5.67 × 10⁻⁸ × 6200⁴) ✓<br>*R* = 8.3 × 10⁸ «m» ✓ | *Allow ECF from (b).*<br>*Accept answers in the range 8.2–8.5 × 10⁸ m.* | 3 |
| 6. | d | | «when hydrogen in the core is used up» it expands to become a red giant ✓<br>it ejects its outer layers / forms a planetary nebula AND the core remains as a white dwarf ✓ | *Do not accept supernova, neutron star or black hole.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `p = 0.125 arcsec`, `b = 9.5e-10 W/m^2`, `T = 6200 K`, constants `pc_ly = 3.26`, `ly_m = 9.46e15`, `sigma = 5.67e-8` | |
| `d_pc` | `1/p` | 8.00 pc |
| `d` | `d_pc*pc_ly*ly_m` | 2.467 × 10¹⁷ m |
| `L` | `4*pi*d**2*b` | 7.27 × 10²⁶ W (1.9 L☉) |
| `R` | `sqrt(L/(4*pi*sigma*T**4))` | 8.31 × 10⁸ m |
| Check | with `d = 2.5e17` | L = 7.46 × 10²⁶ W, R = 8.42 × 10⁸ m |
| Check | with the rounded values of (b), `L = 7.3e26` and `L = 7.5e26` | R = 8.33 × 10⁸ m and 8.44 × 10⁸ m (both within the acceptance range) |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?" / "Which …?" / "Why …?") + A–D listed vertically | Questions 1–5 conform; Question 4 uses a "Why …?" stem (outside the two patterns observed in the profile, expert confirmation needed) |
| 1A: four options of the same type, in the same unit, in order of magnitude | Questions 1–2 conform (ascending); Question 3 has single-word class names; Questions 4–5 have options in sentence form; in Question 5 all four options have the "result, because reason" structure |
| 1A: balanced position of the correct answer | D, C, A, B, A |
| 1A: solvable without the figure | In Question 3 the HR diagram is described; the question is solved using only the values in the text |
| Scope limit: no Cepheid variables | Do not appear in any question; distance only by parallax |
| Scope limit: on the HR diagram the vertical axis is luminosity, the horizontal axis is temperature | These axes are used in the Question 3 stem and in the figure description |
| Paper 2: sub-part at most 3 marks; short question 4–9 marks | Question 6 conforms (2, 2, 3, 2; total 9). **Caveat:** 9 marks is long for an SL short question (4–6 marks were observed in the SL sample paper); it may need to be split for SL |
| Paper 2: at least one AO3 part; "Show that" pattern | (a) Show that, (c) Determine |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, acceptance range | Question 6 conforms |
| Table heading "quantity / unit" | The Question 6 data table conforms: each column has a "quantity / unit" heading, only numbers in the cells |
| Value–unit notation, 2 significant figures | Conforms |
| Level label | All questions SL |

## Independent check

Date: 2026-10-11. A blind solver other than the author solved the questions without seeing the answers; it independently reproduced all
answer keys and recalculated the nuclear equations (conservation of nucleon number and charge) and the Paper 1B gradients (this file has no nuclear equation
and no 1B question; the check is limited to the numerical answers and distractors). Findings: [review/e5-review.md](review/e5-review.md).
No CRITICAL findings. This check does not replace expert review. After the changes below, Question 5 and Question 6 passed a second blind solver; the answers agreed
([review/recheck-2026-10-11.md](review/recheck-2026-10-11.md)).

Changes made in response to the findings (every changed number was recalculated with `python3`):

- **Question 5 (MEDIUM):** the question was rewritten. Temperature was removed from the options; "immediately afterwards" was removed from the stem and the fact that the outward pressure force
  decreases when the rate of fusion decreases was given in the stem. The options are now only along the contracts / expands / stays the same axis and
  all four have the "result, because reason" structure. Answer A (contracts) did not change; the old option C ("contracts and cools") was removed.
- **Question 6 (d) (MEDIUM):** stellar mass 1.5 M☉ → 1.2 M☉ (below the value of 1.4 M☉; a student who mistakenly applies the limit to the star's total mass
  also arrives at the white dwarf). To keep the star realistic for the main sequence the data were changed together: apparent brightness
  2.0 × 10⁻⁹ → 9.5 × 10⁻¹⁰ W m⁻², temperature 6900 → 6200 K. Resulting values: L 1.5 × 10²⁷ → 7.3 × 10²⁶ W (with 2.5 × 10¹⁷ m,
  1.6 × 10²⁷ → 7.5 × 10²⁶ W), R 9.7 × 10⁸ → 8.3 × 10⁸ m. Part (a) did not change.
- **Question 6 (c) (MEDIUM):** the acceptance range was set to 8.2–8.5 × 10⁸ m so as to cover the rounded values of (b) in the markscheme
  (7.3 and 7.5 × 10²⁶ W → 8.33 and 8.44 × 10⁸ m). The suggested range 9.6–10.0 × 10⁸ m belonged to the old data; the same criterion was
  applied to the new data.
- **Question 6 constants (LOW):** σ = 5.67 × 10⁻⁸ W m⁻² K⁻⁴ was added to the question.
- **Question 6 data table (LOW):** "Quantity / Value" → a one-row table with each column headed "quantity / unit".
- **Question 6 (b) (LOW):** B.1 was recorded as a secondary node in the scope table.
- **Question 6 length (LOW):** the caveat "9 marks is long for an SL short question" was emphasised in the "Format conformance" table; the question was not split.
