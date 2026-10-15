# Pilot question set: E.4 Fission

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> Authoring criteria: [AUTHORING_STANDARD.md](AUTHORING_STANDARD.md). Structure example: [a1-kinematics-pilot-questions.md](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node E.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and general
> physics. No exam paper, markscheme, textbook or internet question was used as input; the scenarios are original inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate `python3` calculation. Constants
> used: 1 u = 1.661 × 10⁻²⁷ kg = 931.5 MeV c⁻², e = 1.60 × 10⁻¹⁹ C (data booklet values must be confirmed by an expert). In the reaction in Question 5,
> conservation of nucleon number (1 + 235 = 140 + 94 + 2) and charge (92 = 54 + 38) was checked by hand.
> **Not verified:**
> - Passed an independent blind solver; has not passed expert review (see "Independent check" at the end). It was not examined by an
>   expert for resemblance to any known exam question.
> - **Nuclear data written from memory (to be confirmed from a source):** atomic masses uranium-235 235.04393 u, xenon-140 139.92165 u,
>   strontium-94 93.91536 u, neutron 1.008665 u; Z values (U 92, Xe 54, Sr 38) (Question 5). The 185 MeV found with these masses is consistent with the
>   typical value per fission (about 200 MeV, including the later decays of the products); however, the individual masses were not confirmed.
>   U-235 + n → Xe-140 + Sr-94 + 2n is a real fission channel and a frequently used textbook example; the question text and context are original.
> - The binding energies per nucleon in Question 1 (7.6 and 8.5 MeV) are round, realistic values taken from memory from the binding energy curve;
>   they are not attributed to a specific nucleus.
> - The value "2.5 neutrons per fission on average" in Question 3 is an approximate value for U-235 from memory.
> - Question 5 (c): 185 MeV per reaction belongs to a single fission channel only; in a real reactor the average is different. The question gives this
>   as an assumption using "assume".

## Scope table

| # | Section | Level | Outcome (E.4) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Energy released in fission from binding energy per nucleon | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Function of the moderator; distinguishing it from the control rod, heat exchanger and shielding | AO2 | — | 1 | Easy |
| 3 | Paper 1A | SL | Chain reaction; condition for operation at constant power | AO3 | — | 1 | Medium |
| 4 | Paper 1A | SL | Management of fission products | AO2 | — | 1 | Easy |
| 5 | Paper 2 | SL | Neutron-induced fission; energy from mass difference; power–fuel consumption; reason for slowing neutrons | AO1–AO3 | State, Show, Determine, Explain | 9 | Medium–hard |

This set does not cover all of E.4. What is missing: spontaneous fission, detail of the role of control rods in adjusting power, the function of the heat
exchanger, the reason for shielding, long-term storage of fission products and its relation to half-life, the concept of critical mass
(deliberately left out because it does not appear explicitly in the syllabus analysis).

---

## Question 1 — Paper 1A

A nucleus of nucleon number 240 has a binding energy per nucleon of 7.6 MeV. It undergoes fission into two nuclei, each of nucleon
number 120 and binding energy per nucleon 8.5 MeV. No neutrons are released.

What is the energy released in this fission?

A. 2040 MeV
B. 216 MeV
C. 108 MeV
D. 0.90 MeV

**Answer: B**

**Solution.** Total binding energy of the products = 2 × 120 × 8.5 = 2040 MeV. That of the initial nucleus = 240 × 7.6 = 1824 MeV.
Energy released = 2040 − 1824 = 216 MeV (= 240 × 0.90).

| Option | Misconception |
|---|---|
| A | Takes the total binding energy of the products to be the energy released: 240 × 8.5 = 2040 MeV |
| C | Only one product nucleus is taken into account: 120 × 0.90 = 108 MeV |
| D | Gives the difference per nucleon; does not multiply by the number of nucleons: 8.5 − 7.6 = 0.90 MeV |

---

## Question 2 — Paper 1A

An engineer is choosing a material for the moderator of a thermal fission reactor.

Which property is the most important for this material?

A. Its nuclei absorb neutrons readily.
B. It has a high thermal conductivity so that energy is transferred quickly to the coolant.
C. It has a high density so that gamma radiation is absorbed.
D. Its nuclei have a small mass and slow neutrons down without absorbing them.

**Answer: D**

**Solution.** The job of the moderator is to slow down the fast neutrons from fission by collisions. The energy transferred per collision
is greatest when the mass of the target nucleus is close to that of the neutron; the neutrons must also not be absorbed.

| Option | Misconception |
|---|---|
| A | Confuses the moderator with the control rod; absorbing neutrons is the job of the control rod |
| B | Confuses the moderator with the heat exchanger / coolant |
| C | Confuses the moderator with the shielding |

---

## Question 3 — Paper 1A

In a fission reactor, each fission of a uranium-235 nucleus releases 2.5 neutrons on average. The reactor operates at a constant
power output.

What is the average number of neutrons from each fission that go on to cause a further fission?

A. 2.5
B. 1.5
C. 1
D. 0

**Answer: C**

**Solution.** If the power is constant the number of fissions per second is constant; for this, each fission must lead on average to exactly one new fission. The remaining
1.5 neutrons on average are absorbed in the control rods and in other nuclei or escape from the reactor.

| Option | Misconception |
|---|---|
| A | Thinks all the neutrons released start a new fission; in that case the reaction rate would increase exponentially |
| B | Confuses the number of neutrons absorbed or escaping (2.5 − 1) with what is asked |
| D | Interprets "constant power" as meaning that the chain reaction has stopped |

---

## Question 4 — Paper 1A

Fuel rods removed from a fission reactor are stored under several metres of water for a number of years.

What are the purposes of the water?

A. To remove the thermal energy released by the decay of fission products and to absorb radiation
B. To slow down neutrons and to keep the chain reaction going in the rods
C. To absorb neutrons and to make the fission products stable
D. To dissolve the fission products and to dilute them

**Answer: A**

**Solution.** The fission products in spent fuel are radioactive; their decays both produce heat and emit ionizing radiation. The water
removes the heat and acts as a shield by absorbing the radiation.

| Option | Misconception |
|---|---|
| B | Confuses the water in the pool with the moderator in the reactor; the aim of storage is not to keep the reaction going |
| C | Thinks radioactive decay can be stopped by an external influence (by absorbing neutrons) |
| D | Thinks the products inside the solid fuel rods are removed by dissolving in the water |

---

## Question 5 — Paper 2 (9 marks)

One possible fission reaction in a nuclear reactor is

¹₀n + ²³⁵₉₂U → ¹⁴⁰₅₄Xe + ⁹⁴₃₈Sr + 2 ¹₀n

The following data are available. The masses given for uranium, xenon and strontium are atomic masses.

| Particle | Mass / u |
|---|---|
| uranium-235 | 235.04393 |
| xenon-140 | 139.92165 |
| strontium-94 | 93.91536 |
| neutron | 1.008665 |

1 u is equivalent to 931.5 MeV.

**(a)** State what is meant by neutron-induced fission. [1]

**(b)** Show that the energy released in this reaction is about 185 MeV. [3]

The reactor produces thermal power of 2.4 GW. Assume that each fission releases 185 MeV and that the mass of a uranium-235 atom is
235 u, where 1 u = 1.661 × 10⁻²⁷ kg.

**(c)** Determine the mass of uranium-235 that undergoes fission in the reactor in one day. [3]

**(d)** The neutrons released in the reaction have high kinetic energies. Explain why these neutrons must be slowed down for the
chain reaction to be sustained. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | a «heavy» nucleus absorbs a neutron and splits into two «smaller» nuclei «and neutrons» ✓ | *Both the absorption of a neutron and the splitting are required.* | 1 |
| 5. | b | | mass difference = 235.04393 + 1.008665 − 139.92165 − 93.91536 − 2 × 1.008665 ✓<br>= 0.19826 «u» ✓<br>energy = 0.19826 × 931.5 = 184.7 «MeV» ✓ | *Allow MP1 for a correct mass difference using one net neutron.*<br>*Answer must be given to at least 3 s.f. for MP3.* | 3 |
| 5. | c | | energy per fission = 185 × 10⁶ × 1.60 × 10⁻¹⁹ «= 2.96 × 10⁻¹¹ J» ✓<br>fissions per day = 2.4 × 10⁹ × 86 400 / 2.96 × 10⁻¹¹ «= 7.0 × 10²⁴» ✓<br>mass = 7.0 × 10²⁴ × 235 × 1.661 × 10⁻²⁷ = 2.7 «kg» ✓ | *Allow ECF from (b) if a value other than 185 MeV is used.* | 3 |
| 5. | d | | the probability of a neutron causing fission of uranium-235 is much greater for slow / thermal neutrons ✓<br>«without slowing» too few neutrons cause further fissions / fewer than one neutron per fission causes another fission «so the reaction dies away» ✓ | *OWTTE*<br>*Accept "fast neutrons are more likely to escape or be absorbed without causing fission" for MP2.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `m_U = 235.04393`, `m_Xe = 139.92165`, `m_Sr = 93.91536`, `m_n = 1.008665` (u); `P = 2.4e9 W`; `E_f = 185 MeV`; constants `u_MeV = 931.5`, `e = 1.60e-19`, `u_kg = 1.661e-27` | |
| `dm` | `m_U + m_n - m_Xe - m_Sr - 2*m_n` | 0.198255 u |
| `E` | `dm*u_MeV` | 184.7 MeV |
| `E_J` | `E_f*1e6*e` | 2.96 × 10⁻¹¹ J |
| `rate` | `P/E_J` | 8.11 × 10¹⁹ s⁻¹ |
| `n_day` | `rate*86400` | 7.01 × 10²⁴ |
| `mass` | `n_day*235*u_kg` | 2.73 kg |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?" / "Which …?") + A–D listed vertically | Questions 1–4 conform |
| 1A: four options of the same type, in the same unit, in order of magnitude | Questions 1 and 3 conform (descending); Questions 2 and 4 have options in sentence form (a minority form in the profile); in Question 4 all four options have two parts ("To … and to …") |
| 1A: balanced position of the correct answer | B, D, C, A |
| Scope: no explicit limit for E.4 | Questions were kept to the "assessed core" statements of the syllabus analysis; critical mass and enrichment were not asked |
| Paper 2: sub-part at most 3 marks; short question 4–9 marks | Question 5 conforms (1, 3, 3, 2; total 9). **Caveat:** 9 marks is long for an SL short question (4–6 marks were observed in the SL sample paper). The option of splitting it in two for the SL pool as (a)+(b) [4] and (c)+(d) [5] was left to the expert's decision |
| Paper 2: at least one AO3 part; "Show that" pattern | (b) Show that, (c) Determine, (d) Explain; (c) uses the given approximate value |
| Markscheme: four-column table, ✓, « », ECF, OWTTE | Question 5 conforms |
| Table heading "quantity / unit" | The mass table in Question 5 conforms ("Mass / u"); that the masses are atomic masses is stated above the table |
| Value–unit notation, 2 significant figures | Conforms; the masses are given to the number of figures needed for the mass difference |
| Level label | All questions SL |

## Independent check

Date: 2026-10-11. A blind solver other than the author solved the questions without seeing the answers; it independently reproduced all
answer keys and recalculated the nuclear equations (conservation of nucleon number and charge) and the Paper 1B gradients. Findings:
[review/e4-review.md](review/e4-review.md). No CRITICAL findings. This check does not replace expert review.

Changes made in response to the findings (every changed number was recalculated with `python3`):

- **Question 5 data table (LOW):** "The masses given for uranium, xenon and strontium are atomic masses." was added above the table. The heading stayed "Mass / u" because the table also contains the neutron. The numbers did not change (Δm = 0.198255 u, 184.7 MeV, 2.73 kg recalculated).
- **Question 5 length (LOW):** the note in the "Format conformance" table was strengthened: 9 marks is long for an SL short question; the option of splitting as (a)+(b) [4] and (c)+(d) [5] was written down. The question was not split; the expert's decision is pending.
- **Question 4 (LOW):** options B, C and D were brought into the same two-part form as A ("so that" → "and to"); the structural difference no longer gives away the correct answer. Answer A and the distractor misconceptions did not change.
