# Pilot question set: D.2 Electric and magnetic fields

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node D.2 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; the scenarios are the author's inventions.
> **Numerical check:** all numerical answers and all numerical distractors were reproduced by a separate calculation in `python3` (standard library only)
> and matched the values in the file. Constants used: k = 8.99 × 10⁹ N m² C⁻², e = 1.60 × 10⁻¹⁹ C,
> proton mass 1.67 × 10⁻²⁷ kg (the data booklet values should be confirmed by an expert).
> **Independent check:** passed an independent blind solver; has not passed expert review (see end of file).
> **Not verified:** (1) no expert review was done; (2) the field directions in Question 3 were checked by hand with the right-hand grip rule and
> also with the vector product (B ∝ I × r), not by code; (3) Question 3 asks for the qualitative superposition of the fields of two
> wires — it was assumed to fall within the "straight wire" pattern limit in the syllabus analysis, to be confirmed by an expert; (4) in Question 5
> the fact that the charged sphere behaves as a point charge outside it is given in the question as an assumption; for a 2.5 μC charge on a sphere of radius 0.15 m the surface field is
> 1.0 × 10⁶ N C⁻¹ (below the breakdown field of air, but the question is set in a vacuum); (5) no expert check was made for
> similarity to any known exam question.

## Scope table

| # | Section | Level | Outcome (D.2) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Millikan experiment: equilibrium of a charged drop in a uniform field; quantization of charge | AO2 | — | 1 | Medium |
| 2 | Paper 1A | SL | Field strength between parallel plates (E = V/d) and the force on a charge | AO2 | — | 1 | Easy–medium |
| 3 | Paper 1A | SL | Magnetic field pattern and direction for a current-carrying straight wire | AO2 | — | 1 | Medium |
| 4 | Paper 1A | HL | Electric potential of point charges (scalar sum) | AO2 | — | 1 | Medium |
| 5 | Paper 2 | HL | Potential and field strength; W = qΔV; equipotential surfaces | AO2–AO3 | Show that, Calculate, Determine, Explain | 9 | Medium–hard |

This set does not cover all of D.2. Not covered: force calculation with Coulomb's law, conservation of charge, charging by friction / induction / contact
and earthing, electric field lines and line density, bar magnet / circular loop / solenoid field patterns,
calculation with E = −ΔV/Δr (potential gradient), drawing equipotential patterns.

Scope limit check: the magnetic field pattern is only for a straight wire (Question 3); potential questions involve at most two point charges (Question 4);
no derivatives or integrals.

---

## Question 1 — Paper 1A

A small oil drop carries 3 excess electrons. The drop is held stationary in a vacuum between two horizontal parallel plates when the
potential difference between the plates is 600 V. The drop then gains 2 more electrons. The change in the mass of the drop is negligible.

What is the potential difference between the plates that holds the drop stationary now?

A. 200 V
B. 360 V
C. 600 V
D. 1000 V

**Answer: B**

**Solution.** Equilibrium: qV/d = mg, so V ∝ 1/q (m, g, d constant). The charge increases from 3e to 5e: V = 600 × 3/5 = 360 V.

| Option | Misconception |
|---|---|
| A | Reduces the potential difference by the fraction (added charge / initial charge): 600 × (1 − 2/3) = 200 V |
| C | Thinks the required voltage is unchanged because the weight of the drop is unchanged |
| D | Inverts the ratio (V ∝ q): 600 × 5/3 = 1000 V |

---

## Question 2 — Paper 1A

Two parallel metal plates are 15 mm apart in a vacuum. The potential difference between the plates is 3.0 kV. An alpha particle
(charge +2*e*) is at a point midway between the plates.

*e* = 1.60 × 10⁻¹⁹ C

What is the magnitude of the electric force on the alpha particle?

A. 1.4 × 10⁻¹⁷ N
B. 6.4 × 10⁻¹⁷ N
C. 3.2 × 10⁻¹⁴ N
D. 6.4 × 10⁻¹⁴ N

**Answer: D**

**Solution.** E = V/d = 3.0 × 10³ / 0.015 = 2.0 × 10⁵ V m⁻¹ (the same everywhere between the plates). F = qE = 2 × 1.60 × 10⁻¹⁹ × 2.0 × 10⁵
= 6.4 × 10⁻¹⁴ N.

| Option | Misconception |
|---|---|
| A | Uses E = V × d: 3.0 × 10³ × 0.015 = 45; F = 3.2 × 10⁻¹⁹ × 45 = 1.4 × 10⁻¹⁷ N |
| B | Does not convert the distance to metres: E = 3.0 × 10³ / 15 = 200; F = 3.2 × 10⁻¹⁹ × 200 = 6.4 × 10⁻¹⁷ N |
| C | Takes the charge of the alpha particle as e: 1.60 × 10⁻¹⁹ × 2.0 × 10⁵ = 3.2 × 10⁻¹⁴ N |

---

## Question 3 — Paper 1A

Two long straight parallel wires X and Y are perpendicular to the page. Wire X is to the left of wire Y. The wires carry currents of
equal magnitude. The current in X is directed **into** the page and the current in Y is directed **out of** the page. Point P is
midway between the wires. The line XY is horizontal on the page.

> **Figure:** On a horizontal line in the plane of the page, from left to right: wire X, point P, wire Y. X is perpendicular to the page and its current is into the page
> (⊗ symbol); Y is perpendicular to the page and its current is out of the page (⊙ symbol). P is exactly midway between X and Y. The "top of the page" and
> "bottom of the page" directions are perpendicular to the line XY. Diagram not to scale.

What is the direction of the resultant magnetic field at P?

A. no direction (zero resultant field)
B. towards the top of the page
C. towards the bottom of the page
D. towards wire Y

**Answer: C**

**Solution.** Rule used: the right-hand grip rule (thumb along the current, fingers curling in the direction of the field lines).
X (current into the page): the field lines are clockwise circles as seen by an observer looking at the page; at P, to the right of X, the field is towards the
bottom of the page. Y (current out of the page): the field lines are anticlockwise; at P, to the left of Y, the field is again towards the bottom
of the page. The two fields are in the same direction and add: the resultant is towards the bottom of the page.
Vector check (x to the right, y to the top of the page, z out of the page; B ∝ I × r): for X, (−z) × (+x) = −y; for Y, (+z) × (−x) = −y.

| Option | Misconception |
|---|---|
| A | Thinks "the fields of equal currents in opposite directions cancel"; ignores that P is on opposite sides of the two wires |
| B | Applies the grip rule the wrong way round (left hand, or reversed sense of circulation) |
| D | Thinks the magnetic field points from one wire to the other, like "positive to negative" in an electric field (does not know the field forms circles around the wire) |

---

## Question 4 — Paper 1A (HL)

Two point charges are 0.30 m apart in a vacuum. One charge is +6.0 nC and the other is −4.0 nC. Point P is on the line joining the
charges, midway between them.

*k* = 8.99 × 10⁹ N m² C⁻²

What is the electric potential at P?

A. 120 V
B. 600 V
C. 800 V
D. 4000 V

**Answer: A**

**Solution.** Potential is a scalar and is added with its sign; P is 0.15 m from each charge.
V = k(q₁ + q₂)/r = 8.99 × 10⁹ × (6.0 − 4.0) × 10⁻⁹ / 0.15 = 120 V.

| Option | Misconception |
|---|---|
| B | Ignores the signs of the charges and adds the magnitudes: 8.99 × 10⁹ × 10.0 × 10⁻⁹ / 0.15 = 600 V |
| C | Uses 1/r² for potential (signed sum): 8.99 × 10⁹ × 2.0 × 10⁻⁹ / 0.15² = 800 |
| D | Calculates field strength instead of potential (the fields are in the same direction and add): 8.99 × 10⁹ × 10.0 × 10⁻⁹ / 0.15² = 4000 |

Note: the wrong routes tried do not land on the correct answer (120 V): first charge only and 0.30 m → 180 V; first charge only and 0.15 m → 360 V; ignoring signs and taking 0.30 m → 300 V; signed sum and 0.30 m → 60 V; magnitude of the second charge only → 240 V.

---

## Question 5 — Paper 2 (HL, 9 marks)

An isolated metal sphere of radius 0.15 m is in a vacuum. The sphere carries a charge of +2.5 μC. For points on or outside its
surface, the sphere behaves as a point charge at its centre.

*k* = 8.99 × 10⁹ N m² C⁻²

**(a)** Show that the electric potential at the surface of the sphere is about 1.5 × 10⁵ V. [2]

**(b)** Calculate the electric field strength at the surface of the sphere. [2]

A proton is released from rest at the surface of the sphere.

charge of proton = 1.60 × 10⁻¹⁹ C
mass of proton = 1.67 × 10⁻²⁷ kg

**(c)** Determine the speed of the proton when it is 0.45 m from the centre of the sphere. [3]

A second proton is moved slowly around the sphere along a path that stays on one equipotential surface.

**(d)** Explain why the electric field does no work on this proton. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *V* = *kQ*/*r* = 8.99 × 10⁹ × 2.5 × 10⁻⁶ / 0.15 ✓<br>*V* = 1.498 × 10⁵ «V» **OR** 1.50 × 10⁵ «V» ✓ | *Answer must be given to at least 3 s.f. or the full substitution shown.* | 2 |
| 5. | b | | *E* = *kQ*/*r*² = 8.99 × 10⁹ × 2.5 × 10⁻⁶ / 0.15² **OR** *E* = *V*/*r* = 1.5 × 10⁵ / 0.15 ✓<br>*E* = 1.0 × 10⁶ «N C⁻¹ **OR** V m⁻¹» ✓ | | 2 |
| 5. | c | | potential at 0.45 m = «1.5 × 10⁵ / 3 =» 5.0 × 10⁴ «V» **OR** Δ*V* = 1.0 × 10⁵ «V» ✓<br>*q*Δ*V* = ½*mv*² **OR** 1.60 × 10⁻¹⁹ × 1.0 × 10⁵ = ½ × 1.67 × 10⁻²⁷ × *v*² ✓<br>*v* = 4.4 × 10⁶ «m s⁻¹» ✓ | *Allow ECF from (a).*<br>*Award [2] max if the potential at the surface «1.5 × 10⁵ V» is used as ΔV, giving* 5.4 × 10⁶ m s⁻¹. | 3 |
| 5. | d | | the potential is the same at all points of the path / Δ*V* = 0 ✓<br>*W* = *q*Δ*V* so *W* = 0 ✓ | *OWTTE*<br>**OR** *electric force «field» is perpendicular to the equipotential surface / to the displacement ✓ so the force has no component along the displacement ✓* | 2 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `Q = 2.5e-6 C`, `R = 0.15 m`, `r2 = 0.45 m`, `q = 1.60e-19 C`, `m = 1.67e-27 kg`, constant `k = 8.99e9` | |
| `V_s` | `k*Q/R` | 1.498 × 10⁵ V |
| `E_s` | `k*Q/R**2` | 9.99 × 10⁵ N C⁻¹ ≈ 1.0 × 10⁶ N C⁻¹ |
| `V_2` | `k*Q/r2` | 4.99 × 10⁴ V |
| `dV` | `V_s - V_2` | 9.99 × 10⁴ V |
| `v` | `sqrt(2*q*dV/m)` | 4.37 × 10⁶ m s⁻¹ (4.38 × 10⁶ m s⁻¹ with ΔV = 1.0 × 10⁵ V) |
| Distractor route (c) | `sqrt(2*q*V_s/m)` | 5.36 × 10⁶ m s⁻¹ |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed vertically | Questions 1–4 conform |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1, 2, 4 conform (ascending); Question 3 has four short verbal statements |
| 1A: critical word in bold | Question 3 ("into", "out of") |
| 1A: balanced position of the correct answer | B, D, C, A |
| 1A: options are distinct after rounding | Checked (python) |
| Figure | Question 3: described in text (current directions ⊗ / ⊙ and in words); the positions of the wires (X on the left) are also written in the English stem, so the question can be solved without the figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 3, 2; total 9) |
| Paper 2: "Show that" pattern; the next part may use the given value | Question 5(a) → (b), (c) conform |
| Paper 2: at least one AO3 part | Question 5(a) Show that, (c) Determine, (d) Explain |
| Markscheme: four-column table, ✓, « », OR, ECF, OWTTE | Question 5 conforms |
| Giving constants | k, e and the proton mass are given in the question text where needed |
| Value–unit notation (N C⁻¹, m s⁻¹), 2 significant figures | Conforms |
| Paper 1B | Not in this file; the 1B question for theme D is [in the D.3 file](d3-motion-in-em-fields-pilot-questions.md) |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver other than its author, without seeing the answers; all answer keys,
distractor values and the field direction in Question 3 were independently reproduced and matched. No CRITICAL or MEDIUM findings. Details:
[review/d2-review.md](review/d2-review.md). This check does not replace expert review.

Changes made in response to the review:

- **Question 3 (stem):** "Wire X is to the left of wire Y" and "The line XY is horizontal on the page" were added; the question is now unambiguous
  even without the figure description. The corresponding row in the "Format conformance" table was corrected.
- **Question 3 (option A):** full sentence "The resultant field is zero." → short phrase "no direction (zero resultant field)"; the four options are
  in the same form.
- **Question 4:** second charge −2.0 nC → −3.0 nC. With the old numbers the double error "signs ignored + r = 0.30 m" gave the correct answer (240 V);
  with the new numbers it gives 270 V and does not coincide with any option. Options 240 / 480 / 1600 / 3200 V → 180 / 540 / 1200 /
  3600 V; the correct answer is still A. All options were recalculated with `python3` (179.8, 539.4, 1198.7, 3596.0).
- **Question 4, second check (recheck-2026-10-11):** with −3.0 nC the wrong calculation "first charge only and 0.30 m" gave the correct answer (180 V)
  The second charge was changed to −4.0 nC; options 120 / 600 / 800 / 4000 V, the correct answer is still A (119.9, 599.3, 799.1, 3995.6).
  This final version has not passed the independent solver; the numbers were only recalculated.
