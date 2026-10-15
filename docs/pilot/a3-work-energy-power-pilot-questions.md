# Pilot question set: A.3 Work, energy and power

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written by hand according to the [authoring standard](AUTHORING_STANDARD.md) and with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node A.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam question, textbook question or internet source was used as input.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced with a separate calculation in `python3`
> (g = 9.8 m s⁻²; the data booklet value must be confirmed by an expert). The energy density of diesel in Question 5 is given in the question.
> **Not verified:** it passed an independent blind solver; it has not passed expert review; it has not been checked by an expert for resemblance
> to any known exam question; the energy density of diesel fuel (3.6 × 10¹⁰ J m⁻³) and the overall efficiency of the pump (12 %) are plausible values based on general knowledge,
> not confirmed from a source; it was not checked whether the guide defines "energy density" per volume (J m⁻³) or
> per mass (J kg⁻¹).

## Scope table

| # | Section | Level | Outcome (A.3) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Work = *Fs* cos *θ*; work done by one force vs net work | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Power = *Fv*; efficiency | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Mechanical energy and the work done by a non-conservative force (friction) | AO2 | — | 1 | Medium |
| 4 | Paper 1A | SL | Dependence of elastic potential energy on extension | AO3 | — | 1 | Medium–hard |
| 5 | Paper 2 | SL | Power, kinetic and gravitational potential energy; efficiency; energy density; Sankey diagram | AO1–AO3 | Show that, Determine, State, Explain | 9 | Medium |

This set does not cover all of A.3. Missing: direct application of the work–kinetic energy theorem, area under a force–displacement graph,
cases where mechanical energy is conserved (frictionless), drawing or reading a Sankey diagram, comparing the
energy densities of different fuels.

---

## Question 1 — Paper 1A

A traveller pulls a wheeled suitcase at constant speed along a level platform. The strap makes an angle of 60° with the horizontal and
the traveller exerts a force of 25 N along the strap. The suitcase moves a distance of 40 m.

What is the work done by the traveller on the suitcase?

A. 0 J
B. 500 J
C. 870 J
D. 1000 J

**Answer: B**

**Solution.** *W* = *Fs* cos *θ* = 25 × 40 × cos 60° = 500 J.

| Option | Misconception |
|---|---|
| A | Thinks "constant speed, so no work is done"; confuses net work (zero) with the work done by a single force |
| C | Uses the component perpendicular to the displacement: 25 × 40 × sin 60° = 866 J ≈ 870 J |
| D | Ignores the angle: 25 × 40 = 1000 J |

---

## Question 2 — Paper 1A

An electric winch raises a load of mass 150 kg vertically at a constant speed of 0.40 m s⁻¹. The electrical power supplied to the
winch is 840 W.

What is the efficiency of the winch?

A. 7.1 %
B. 30 %
C. 43 %
D. 70 %

**Answer: D**

**Solution.** Useful power = *Fv* = *mgv* = 150 × 9.8 × 0.40 = 588 W. Efficiency = 588 / 840 = 0.70 = 70 %.

| Option | Misconception |
|---|---|
| A | Uses mass instead of force (forgets *g*): 150 × 0.40 / 840 = 0.071 |
| B | Gives the fraction lost instead of the useful fraction: (840 − 588) / 840 = 0.30 |
| C | Takes efficiency to be the ratio of wasted power to useful power: 252 / 588 = 0.43 |

---

## Question 3 — Paper 1A

A parcel of mass 2.0 kg is released from rest at the top of a delivery chute. The chute is 5.0 m long and its top is 1.5 m vertically
above its bottom. The parcel reaches the bottom of the chute with a speed of 4.0 m s⁻¹.

What is the average friction force acting on the parcel as it slides down the chute?

A. 2.7 N
B. 3.2 N
C. 5.9 N
D. 8.9 N

**Answer: A**

**Solution.** Potential energy lost = 2.0 × 9.8 × 1.5 = 29.4 J. Kinetic energy gained = ½ × 2.0 × 4.0² = 16.0 J.
Work done against friction = 29.4 − 16.0 = 13.4 J. Friction acts along the chute (5.0 m): *f* = 13.4 / 5.0 = 2.7 N.

| Option | Misconception |
|---|---|
| B | Takes all of the kinetic energy to be the work done against friction: 16.0 / 5.0 = 3.2 N |
| C | Assumes all of the potential energy goes to friction: 29.4 / 5.0 = 5.9 N |
| D | Finds the energy loss correctly but uses the vertical height instead of the distance along the chute: 13.4 / 1.5 = 8.9 N |

---

## Question 4 — Paper 1A

A spring obeys Hooke's law. When the extension of the spring is *x*, the elastic potential energy stored in the spring is *E*. The
extension is then increased from *x* to 3*x*.

What is the **additional** work done on the spring?

A. 2*E*
B. 3*E*
C. 8*E*
D. 9*E*

**Answer: C**

**Solution.** Since *E*<sub>p</sub> = ½*kx*², the energy stored at extension 3*x* is 9*E*. Additional work = 9*E* − *E* = 8*E*.

| Option | Misconception |
|---|---|
| A | Thinks energy is directly proportional to extension and takes the additional extension (2*x*): 2*E* |
| B | Thinks energy is directly proportional to extension and gives the final value: 3*E* |
| D | Uses the quadratic relation correctly but gives the total energy in the final state instead of the additional work: 9*E* |

---

## Question 5 — Paper 2 (9 marks)

A diesel-powered pump raises water from a river to an irrigation tank. The water is raised through a vertical height of 18 m at a
rate of 2.5 kg s⁻¹ and leaves the outlet pipe at the top with a speed of 4.0 m s⁻¹. The speed of the water in the river is negligible.

**(a)** Show that the rate at which the pump transfers energy to the water is about 460 W. [3]

This rate of energy transfer is the useful power output of the pump.

The overall efficiency of the pump is 12 %. The energy density of diesel fuel is 3.6 × 10¹⁰ J m⁻³.

**(b)** Determine the volume of diesel fuel used by the pump in 1.0 hour. [3]

**(c)** A Sankey diagram is drawn for the pump. State the value of the ratio
(width of the useful output arrow) / (width of the input arrow). [1]

The outlet pipe is replaced by a narrower nozzle so that the water leaves with a greater speed. The useful power output of the pump
and the height are unchanged.

**(d)** Explain the effect of this change on the mass of water delivered to the tank per second. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | rate of gain of gravitational potential energy = 2.5 × 9.8 × 18 «= 441 W» ✓<br>rate of gain of kinetic energy = ½ × 2.5 × 4.0² «= 20 W» ✓<br>total = 461 «W» ✓ | *Third mark needs the sum shown or an answer to at least 3 s.f.*<br>*Award [1] max for 441 «W» with no kinetic energy term.* | 3 |
| 5. | b | | input power = 460 / 0.12 «= 3.8 × 10³ W» ✓<br>energy supplied in 1.0 h = 3.8 × 10³ × 3600 «= 1.4 × 10⁷ J» ✓<br>volume = 1.4 × 10⁷ / 3.6 × 10¹⁰ = 3.8 × 10⁻⁴ «m³» ✓ | *Allow use of 461 W.*<br>*Accept 0.38 litre / 380 cm³.*<br>*Award [2] max if efficiency is multiplied instead of divided (5.5 × 10⁻⁶ m³).* | 3 |
| 5. | c | | 0.12 **OR** 12 : 100 **OR** 3/25 ✓ | | 1 |
| 5. | d | | each kilogram of water now gains more «kinetic» energy / more energy is transferred per unit mass ✓<br>power is unchanged, so less mass is delivered per second ✓ | *OWTTE*<br>*Do not award the second mark for "less" without reference to constant power or energy per second.* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `mdot = 2.5 kg/s`, `H = 18 m`, `v = 4.0 m/s`, `eff = 0.12`, `rho_E = 3.6e10 J/m^3`, `t = 3600 s`, constant `g = 9.8 m/s^2` | |
| `P_g` | `mdot*g*H` | 441 W |
| `P_k` | `0.5*mdot*v**2` | 20 W |
| `P_out` | `P_g + P_k` | 461 W |
| `P_in` | `P_out/eff` | 3.84 × 10³ W |
| `E_in` | `P_in*t` | 1.38 × 10⁷ J |
| `V_fuel` | `E_in/rho_E` | 3.84 × 10⁻⁴ m³ |

The same chain with the "Show that" value (460 W): `P_in` = 3.83 × 10³ W, `V_fuel` = 3.83 × 10⁻⁴ m³; to two significant figures the result is the same
(3.8 × 10⁻⁴ m³).

---

## Format conformance

Questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + separate single question sentence ("What is …?") + A–D one below the other | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–3 conform (ascending; J, %, N); Question 4 is algebraic (multiples of *E*), ascending |
| 1A: balanced position of the correct answer | B, D, A, C |
| 1A: emphasised key word in bold | Question 4 ("additional") conforms |
| 1A: one- or two-step calculation | Questions 1–2 one to two steps; Question 3 three short steps (at the upper limit of the profile's "one or two steps" observation) |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (3, 3, 1, 2; total 9). Note: in the SL sample paper short questions of 4–6 marks were observed; 9 marks is the upper end of the HL range, expert confirmation is needed for SL |
| Paper 2: "Show that" pattern; a later part uses the given value | Question 5 (a) → (b) conforms |
| Markscheme: four-column table, ✓, « », OR, OWTTE | Question 5 conforms |
| Value–unit notation (m s⁻¹, kg s⁻¹, J m⁻³), 2 significant figures | Conforms |
| Figure | No question needs a figure; Question 5 (c) does not ask for a Sankey diagram to be drawn, only for the ratio (the drawing answer type does not exist yet) |
| Scope limits (A.3) | Gravitational potential energy only as *mg*Δ*h*; no derivatives/integrals |

## Independent check

Date: 2026-10-11. The blind solver solved the questions without seeing the answers and independently reproduced all answer keys and markscheme results; no CRITICAL or MEDIUM findings.
Details: [review/a3-review.md](review/a3-review.md). This check does not replace expert review.

Changes made in response to the findings:

- Question 5 (a): "the rate at which the pump transfers energy to the water" was written in place of "useful power output", and the fact that this is the useful power output of the pump was defined in a separate sentence; so it is clear that the kinetic energy at the outlet is included in the useful output. The numbers did not change (441 + 20 = 461 W).
- Question 5 (c) markscheme: "about 1/8" (0.125) was removed and the exactly equivalent "3/25" was written instead.
- The 9 marks of Question 5: already noted in the file; no further change was made.
