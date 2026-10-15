# Pilot question set: D.3 Motion in electromagnetic fields

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written following the [authoring standard](AUTHORING_STANDARD.md), with the structure of the [A.1 example](a1-kinematics-pilot-questions.md).
> The single Paper 1B question requested for theme D is in this file (Question 6).
>
> **Source:** only syllabus node D.3 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook question or internet source was used as input; the scenarios are the author's inventions.
> **Numerical check:** all numerical answers, all numerical distractors and the best-fit / maximum / minimum gradients in Question 6 were reproduced by a separate calculation in `python3`
> (standard library only) and matched the values in the file. Constants used:
> e = 1.60 × 10⁻¹⁹ C, electron mass 9.11 × 10⁻³¹ kg, g = 9.8 m s⁻² (the data booklet values should be confirmed by an expert).
> **Independent check:** passed an independent blind solver; has not passed expert review. The blind solver found a CRITICAL physics error in Question 6(e);
> the part was replaced (see end of file).
> **Not verified:** (1) no expert review was done; the rewritten Question 6(e) and the changed Question 5 numbers passed a second blind solver and agreed (review/recheck-2026-10-11.md); (2) the force and field directions (Question 3, Question 5c) were checked by hand with the right-hand
> rule and also with the vector product (F = qv × B, F = IL × B), not by code; (3) the data of Question 6 were produced by the author
> for B = 0.080 T and L = 0.050 m with small scatter added; they are fictional data and do not come from a real experiment; (4) in Question 6
> it was not confirmed whether an uncertainty of ±0.04 g (fluctuation of the reading) is reasonable for a real balance; (5) no expert check was made for similarity to
> any known exam question — the velocity selector and the current balance are well-known experiment types, but the question texts are original.

## Scope table

| # | Section | Level | Outcome (D.3) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Circular motion in a uniform magnetic field; period independent of speed | AO2 | — | 1 | Medium–hard |
| 2 | Paper 1A | SL | Undeflected passage through perpendicular electric and magnetic fields (v = E/B) | AO2 | — | 1 | Medium |
| 3 | Paper 1A | SL | Direction of the force on a current-carrying conductor (F = BIL sin θ) | AO2 | — | 1 | Easy–medium |
| 4 | Paper 1A | SL | Motion of a charged particle in a uniform electric field | AO2 | — | 1 | Medium |
| 5 | Paper 2 | SL | Perpendicular fields; circular path in a uniform magnetic field; determining the charge-to-mass ratio | AO1–AO3 | Show that, Explain, Determine, State | 9 | Medium–hard |
| 6 | Paper 1B | SL | F = BIL experiment (current balance): uncertainty, determining B from the gradient, effect of a (systematic) zero error on the gradient and intercept | AO2–AO3 | Outline, Calculate, Determine, Comment, Explain, Suggest | 10 | Medium–hard |

This set does not cover all of D.3. Not covered: calculation with F = qvB sin θ for θ ≠ 90°, the force between parallel wires
(magnitude and direction), quantitative calculation of deflection in a uniform electric field, direction of the magnetic force on a charged particle (on its own).

Scope limit check: there is no explicit limit for D.3 in the guide. Accelerating a particle through a potential difference (W = qΔV) is additional HL content of D.2,
so it was deliberately not used in this SL file; in Question 5 the speed is found from the perpendicular-fields condition. No derivatives or integrals.

---

## Question 1 — Paper 1A

A charged particle moves at right angles to a uniform magnetic field in a vacuum. The particle moves in a circle with period *T*.
An identical particle enters the same field at right angles with **twice** the speed.

What is the period of the motion of the second particle?

A. *T*/2
B. *T*
C. 2*T*
D. 4*T*

**Answer: B**

**Solution.** qvB = mv²/r → r = mv/(qB). T = 2πr/v = 2πm/(qB): the period is independent of speed. When the speed doubles the radius also doubles;
the circumference and the speed increase in the same proportion, so the period does not change.

| Option | Misconception |
|---|---|
| A | Thinks the radius does not change; the same circle is traversed at twice the speed: T/2 |
| C | Sees that the radius doubles but forgets that the speed also increases (T ∝ r): 2T |
| D | Thinks the radius increases as v² (r ∝ v², a wrong deduction from the expression mv²/r) and forgets the increase in speed: 4T |

---

## Question 2 — Paper 1A

A beam of electrons passes between two parallel plates that are 2.0 cm apart. The potential difference between the plates is 600 V.
A uniform magnetic field of strength 1.5 mT is applied at right angles to both the electric field and the beam. The electrons pass
between the plates without being deflected.

What is the speed of the electrons?

A. 5.0 × 10⁻⁸ m s⁻¹
B. 2.0 × 10⁵ m s⁻¹
C. 4.0 × 10⁵ m s⁻¹
D. 2.0 × 10⁷ m s⁻¹

**Answer: D**

**Solution.** E = V/d = 600 / 0.020 = 3.0 × 10⁴ V m⁻¹. No-deflection condition: eE = evB → v = E/B = 3.0 × 10⁴ / 1.5 × 10⁻³ = 2.0 × 10⁷ m s⁻¹.

| Option | Misconception |
|---|---|
| A | Inverts the ratio (v = B/E): 1.5 × 10⁻³ / 3.0 × 10⁴ = 5.0 × 10⁻⁸ |
| B | Does not convert the plate separation to metres: E = 600 / 2.0 = 300; 300 / 1.5 × 10⁻³ = 2.0 × 10⁵ |
| C | Uses the potential difference instead of the field strength (v = V/B): 600 / 1.5 × 10⁻³ = 4.0 × 10⁵ |

---

## Question 3 — Paper 1A

A straight horizontal wire lies in the plane of the page and carries a current directed towards the right of the page. The wire is in
a uniform magnetic field that is directed **into** the page.

> **Figure:** A horizontal wire in the plane of the page, running from left to right, with a current arrow (*I*) pointing right along it. The region around the wire is filled with ⊗ symbols
> showing a uniform magnetic field into the page. The "top of the page" is perpendicular to the wire and in the plane of the page. Diagram not to scale.

What is the direction of the magnetic force on the wire?

A. towards the top of the page
B. towards the bottom of the page
C. out of the page
D. into the page

**Answer: A**

**Solution.** Rule used: the right-hand rule, F = IL × B (conventional current direction). Axes: x to the right, y to the top of the page, z out of
the page. Current +x, field −z: (+x) × (−z) = +y. The force is towards the top of the page. (Fleming's left-hand rule gives the same result: forefinger
= field = into the page, middle finger = current = to the right, thumb = force = up.)

| Option | Misconception |
|---|---|
| B | Applies the rule with the wrong hand, or takes the direction of electron flow instead of the current direction |
| C | Thinks the force is in the direction opposite to the field |
| D | Thinks the force is in the direction of the field (confusion with F = qE in an electric field) |

---

## Question 4 — Paper 1A

An electron enters a region of uniform electric field in a vacuum. The initial velocity of the electron is at right angles to the
electric field lines. There is no magnetic field.

Which describes the path of the electron in the field and the speed of the electron?

A. The path is a circular arc and the speed is constant.
B. The path is a circular arc and the speed increases.
C. The path is a parabola and the speed increases.
D. The path is a parabola and the speed is constant.

**Answer: C**

**Solution.** The electric force is constant in magnitude and direction (parallel to the field lines, opposite to the field). The velocity component perpendicular
to the field is unchanged and the component along the field increases uniformly: the path is a parabola (like horizontal projectile motion). The force has a component along the
direction of motion, so it does work; the speed increases.

| Option | Misconception |
|---|---|
| A | Confuses the electric field with a magnetic field (thinks the force is always perpendicular to the velocity) |
| B | Thinks the path is a circle as in a magnetic field, but correctly thinks that the field transfers energy |
| D | Path correct; but considers only the velocity component perpendicular to the field, or says "the force is initially perpendicular to the velocity, so it does no work" |

---

## Question 5 — Paper 2 (9 marks)

A beam of electrons travels in a vacuum from left to right between two horizontal parallel plates. The plates are 2.5 cm apart and
the potential difference between them is 460 V. The upper plate is positive. A uniform magnetic field of strength 0.80 mT is applied
in the region between the plates, at right angles to the beam and to the electric field. The beam passes between the plates without
being deflected.

> **Figure:** Two horizontal parallel plates in the plane of the page; the upper one is marked "+" and the lower one "−"; the separation between them is labelled 2.5 cm.
> The electron beam is shown by a horizontal arrow midway between the plates, from left to right. Electric field lines run from the upper plate
> to the lower plate (towards the bottom of the page). The direction of the magnetic field is **not shown** in the figure; it is perpendicular to the plane of the page. Diagram not to scale.

**(a)** Show that the speed of the electrons is about 2.3 × 10⁷ m s⁻¹. [2]

**(b)** State the direction of the magnetic field. [1]

The potential difference between the plates is now reduced to zero. The magnetic field is unchanged. The beam follows a circular arc
of radius 0.16 m.

**(c)** Explain why the path of the electrons in the magnetic field is circular. [2]

**(d)** Determine the charge-to-mass ratio of the electron given by these measurements. [2]

The potential difference of 460 V is restored. The electrons are replaced by protons that enter the region with the same velocity as
the electrons.

**(e)** Explain whether the protons are deflected. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | *E* = *V*/*d* = 460 / 0.025 «= 1.84 × 10⁴ V m⁻¹» ✓<br>«*eE* = *evB* so» *v* = *E*/*B* = 1.84 × 10⁴ / 0.80 × 10⁻³ = 2.30 × 10⁷ «m s⁻¹» ✓ | *The full substitution or the answer to 3 s.f. must be shown.* | 2 |
| 5. | b | | into the «plane of the» page ✓ | | 1 |
| 5. | c | | the «magnetic» force is always perpendicular to the velocity ✓<br>so the speed is constant / no work is done **AND** the force «of constant magnitude» acts as a centripetal force ✓ | *OWTTE* | 2 |
| 5. | d | | *evB* = *mv*²/*r* **OR** *e*/*m* = *v*/(*Br*) ✓<br>*e*/*m* = 2.3 × 10⁷ / (0.80 × 10⁻³ × 0.16) = 1.8 × 10¹¹ «C kg⁻¹» ✓ | *Allow ECF from (a).* | 2 |
| 5. | e | | both the electric force and the magnetic force reverse direction «as the charge has opposite sign» **OR** both forces have the same magnitude as before «same *E*, *v*, *B* and magnitude of charge» **AND** are still in opposite directions ✓<br>the forces still balance / *v* = *E*/*B* does not depend on charge or mass, so the protons are not deflected ✓ | *OWTTE*<br>*Award [0] for "not deflected" without reasoning.* | 2 |

**Direction solution (b).** Axes: x to the right (velocity), y to the top of the page, z out of the page. The E field is −y (from the positive plate to the negative plate). The electric force on the electron
(q = −e) is +y (towards the positive plate). For no deflection the magnetic force must be −y: F = qv × B = (−e)(v x̂ × B).
For B = −z (into the page), x̂ × (−ẑ) = +ŷ, and multiplying by (−e) gives −ŷ. Hence the field is into the page. Check with the right-hand rule:
for a positive charge with v to the right and B into the page the force is up; for the electron it is reversed, that is down. ✓

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `V = 460 V`, `d = 0.025 m`, `B = 0.80e-3 T`, `r = 0.16 m` | |
| `E` | `V/d` | 1.84 × 10⁴ V m⁻¹ |
| `v` | `E/B` | 2.30 × 10⁷ m s⁻¹ |
| `e_over_m` | `v/(B*r)` | 1.80 × 10¹¹ C kg⁻¹ |
| Consistency check | `m_e*v/(e*B)` (e = 1.60e-19, m_e = 9.11e-31) | r = 0.164 m; the question gives 0.16 m to two significant figures, so the e/m found is about 2 % larger than the accepted value (1.76 × 10¹¹ C kg⁻¹) |

---

## Question 6 — Paper 1B (10 marks)

A student investigates the force on a current-carrying wire in a magnetic field. Two flat magnets are fixed to a steel yoke so that
there is an approximately uniform horizontal magnetic field between them. The yoke is placed on an electronic balance. A stiff
straight horizontal wire is clamped so that it passes between the magnets at right angles to the field. The wire does not touch the
magnets or the balance. The balance is set to zero when there is no current in the wire.

> **Figure:** Apparatus diagram. A U-shaped steel yoke on the pan of an electronic balance; on the two inner faces of the yoke, facing each other,
> flat magnets (labelled N and S), with a horizontal field between them. A stiff horizontal wire passes between the magnets at right angles to the field; the wire is clamped
> at both sides to a separate stand that does not touch the balance and is connected in series with a power supply and an ammeter. The length of the wire in the field
> is labelled *L* (the length of the magnets). Diagram not to scale.

The student varies the current *I* in the wire and records the change in the balance reading Δ*m*. The direction of the current is
chosen so that the balance reading increases.

| *I* / A | Δ*m* / g ± 0.04 g |
|---|---|
| 1.0 | 0.41 |
| 2.0 | 0.83 |
| 3.0 | 1.21 |
| 4.0 | 1.64 |
| 5.0 | 2.05 |

The uncertainty in *I* is negligible. The length of the wire in the field is *L* = (5.0 ± 0.1) cm.

**(a)** Outline why the balance reading changes when there is a current in the wire. [2]

**(b)** Calculate the percentage uncertainty in Δ*m* for *I* = 1.0 A. [1]

The student plots Δ*m* against *I* with uncertainty bars. The gradient of the line of best fit is 0.41 g A⁻¹. The lines of maximum
and minimum gradient have gradients of 0.43 g A⁻¹ and 0.39 g A⁻¹. Theory predicts that Δ*m* = *BIL*/*g*, where *B* is the magnetic
field strength between the magnets and *g* = 9.8 m s⁻².

**(c)** Determine *B*, with its absolute uncertainty. [3]

**(d)** The manufacturer states that the magnetic field strength between the magnets is 0.083 T. Comment on whether the result of
the experiment is consistent with this value. [1]

**(e)** A second student repeats the experiment but does **not** set the balance to zero. With no current in the wire the balance
reads a constant 0.15 g. This student plots the balance reading against *I* and determines *B* from the gradient of the graph.
Explain the effect of this on the value of *B* obtained. [2]

**(f)** Suggest **one** change to the experiment that would reduce the percentage uncertainty in *B*. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 6. | a | | the magnetic field exerts a «vertical» force on the current-carrying wire ✓<br>the wire exerts an equal and opposite force on the magnets «Newton's third law», which changes the force on the balance ✓ | *OWTTE* | 2 |
| 6. | b | | «0.04 / 0.41 × 100 =» 10 «%» ✓ | *Accept 9.8 %.* | 1 |
| 6. | c | | *B* = gradient × *g* / *L* = 0.41 × 10⁻³ × 9.8 / 0.050 = 0.080 «T» ✓<br>fractional uncertainty = 0.02/0.41 + 0.1/5.0 «= 0.049 + 0.020 = 0.069» ✓<br>*B* = (0.080 ± 0.006) «T» ✓ | *MP2: uncertainty in gradient is (0.43 − 0.39)/2 = 0.02 g A⁻¹.*<br>*Award [2] max if the gradient is not converted to kg A⁻¹ «80 T».* | 3 |
| 6. | d | | consistent, as 0.083 T lies within the range 0.074 T to 0.086 T ✓ | *Allow ECF from (c): the conclusion must follow from the candidate's own range.*<br>*Reasoning using the range is required.* | 1 |
| 6. | e | | every reading is larger by the same amount «0.15 g» / the line is shifted upwards / the intercept is no longer zero «systematic / zero error» ✓<br>the gradient is unchanged, so the value of *B* obtained is not affected ✓ | *OWTTE*<br>*Do not award MP2 for "no effect" without reference to the gradient.* | 2 |
| 6. | f | | use larger currents **OR** a longer length of wire in the field / longer magnets **OR** several turns of wire through the field «so that Δ*m* is larger» **OR** a balance with smaller uncertainty **OR** measure *L* with a more precise instrument ✓ | *Do not accept "repeat readings" without stating that a mean is taken.* | 1 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `grad = 0.41e-3 kg/A`, `grad_max = 0.43e-3`, `grad_min = 0.39e-3`, `L = 0.050 m`, `dL = 0.001 m`, `u_dm = 0.04 g`, constant `g = 9.8` | |
| `pct_dm` | `100*0.04/0.41` | 9.8 % ≈ 10 % |
| `B` | `grad*g/L` | 0.0804 T |
| `u_grad` | `(grad_max - grad_min)/2` | 0.02 × 10⁻³ kg A⁻¹ |
| `frac` | `u_grad/grad + dL/L` | 0.0488 + 0.0200 = 0.0688 |
| `u_B` | `B*frac` | 0.0055 T ≈ 0.006 T |
| Range | `B*(1-frac)`, `B*(1+frac)` | 0.0748 T – 0.0859 T (0.074–0.086 T with rounded values) |
| (d) robustness | 0.083 T; ranges for uncertainties ±0.004, ±0.005, ±0.0055, ±0.006 T | 0.076–0.084, 0.075–0.085, 0.0749–0.0859, 0.074–0.086 T: inside in all of them |
| (e) zero error | add 0.15 g to all readings and recalculate the least-squares line | gradient 0.409 g A⁻¹ (unchanged), intercept 0.151 g |

### Figure note

In the version shown to the student, a Δ*m*–*I* graph with uncertainty bars accompanies the table. The graph is generated by code from the same data
(D-14). The least-squares gradient calculated from the data in the table is 0.409 g A⁻¹ (intercept 0.001 g); the lines through the ends of the uncertainty
bars of the first and last points have gradients of 0.430 and 0.390 g A⁻¹, and these two lines pass through the uncertainty
bars of all five points (checked with python). The values 0.41, 0.43 and 0.39 given in the question are these rounded
to two significant figures.

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence + A–D listed vertically | Questions 1–3 "What is …?"; Question 4 "Which …?" (rarer in the profile but valid) |
| 1A: four options of the same kind, in the same unit, in order of magnitude | Questions 1–2 conform (ascending); Question 3 direction statements; Question 4 four sentences in the same pattern (sentence-form options are a minority in the profile) |
| 1A: critical word in bold | Question 1 ("twice"), Question 3 ("into") |
| 1A: table-option format could not be verified in the example | Question 4 was therefore written with sentence options instead of a two-column table |
| 1A: balanced position of the correct answer | B, D, A, C |
| 1A: options are distinct after rounding | Checked (python) |
| Figure | Questions 3, 5, 6: described in text; the field and current directions are also given in words. In Question 5(b) the magnetic field direction is deliberately not shown (that is what is asked) |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 1, 2, 2, 2; total 9). In the SL sample paper short questions are 4–6 marks; 9 marks is the upper end of the HL range — for an SL paper it can be split into two questions |
| Paper 2: "Show that" pattern; the next part may use the given value | Question 5(a) → (d) conform |
| Paper 2: at least one AO3 part | Question 5(a) Show that, (c) and (e) Explain, (d) Determine |
| Markscheme: four-column table, ✓, « », OR, AND, ECF, OWTTE | Questions 5 and 6 conform |
| 1B: experiment question of about 10 marks, sub-parts 1–3 marks | Question 6 conforms (2, 1, 3, 1, 2, 1; total 10); part (e) was replaced, its marks and the total stayed the same |
| 1B: table heading "quantity / unit ± uncertainty" | Question 6 conforms |
| 1B: command terms | Outline, Calculate, Determine, Explain, Suggest are in the profile; "Comment" is not in the profile list (kept because it is used in the A.1 example) — expert confirmation needed |
| 1B: the student draws the line of best fit on a given graph and finds the gradient | **Question 6 does not conform:** because the graph could not be generated, the gradients are given in the text. When the graph template is ready, part (c) should be rewritten |
| Value–unit notation (m s⁻¹, g A⁻¹, C kg⁻¹), 2 significant figures | Conforms |

## Independent check

Date: 2026-10-11. This file was solved by a blind solver other than its author, without seeing the answers. All answer keys other than Question 6(e),
distractor values, direction solutions (Questions 3, 5b) and the gradients in Question 6 were independently reproduced and matched.
**Question 6(e) did not match and was replaced.** Details: [review/d3-review.md](review/d3-review.md). This check does not replace expert review;
the replaced parts did not pass a second blind solution.

Changes made in response to the review:

- **Question 6(e) — CRITICAL, part replaced.** The old part asked about "the effect on B if the wire is not exactly perpendicular to the field", and the key said "the force and gradient
  decrease, so B is found to be smaller". The author redid the derivation and reached the same conclusion as the reviewer: the wire is straight and crosses the field region of length *L*
  from end to end; if it makes an angle θ with the field, its length in the field is *L*/sin θ and
  F = BI(*L*/sin θ) sin θ = BIL is unchanged (even if the wire is tilted in the vertical plane, the vertical component of the force is still BIL). The old key was wrong;
  a student who reasoned correctly would have scored zero. New part: the balance has not been zeroed and reads a constant 0.15 g with no current; the student explains that the intercept
  shifts but the gradient, and therefore B, is unchanged (2 marks, AO3). The scope table was updated; the total of marks
  stayed at 10. `python3`: when 0.15 g is added to all readings the gradient is 0.409 g A⁻¹ (the same), the intercept 0.151 g.
- **Question 6(d) — MEDIUM.** Manufacturer value 0.085 T → 0.083 T. The old value was on the boundary of the result range and the judgement reached depended on how the uncertainty
  was rounded. `python3`: 0.083 T is inside the range for all of ±0.004, ±0.005, ±0.0055 and ±0.006 T. The note
  "the conclusion must follow from the candidate's own range" was added; the "Allow ± 0.005 T" note in 6(c) was removed.
- **Question 5(a):** potential difference between the plates 450 V → 460 V. The old speed 2.25 × 10⁷ m s⁻¹ was on a rounding boundary for the "about 2.3 × 10⁷" target;
  the new value is exactly 2.30 × 10⁷ m s⁻¹. Accordingly the result of (d) 1.76 × 10¹¹ → 1.80 × 10¹¹ C kg⁻¹ (the key is still
  1.8 × 10¹¹), the acceptance-range note was reduced to an ECF note, and the formula chain was updated.
- **Question 5(e) markscheme:** the second alternative of MP1 now also requires the directions ("… **AND** are still in opposite directions").
- **Not changed:** Question 5 being a 9-mark SL short question (within the requested 4–9 range; it is noted in the "Format conformance" table that it can be
  split) and the command term "Comment" in Question 6(d) (consistent with the A.1 example). Both await an expert decision.
