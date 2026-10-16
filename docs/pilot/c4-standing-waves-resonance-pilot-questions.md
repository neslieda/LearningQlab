# Pilot question set: C.4 Standing waves and resonance

> **Status: UNREVIEWED DRAFT.** Date: 2026-10-11. Not shown to students without physics expert approval (CLAUDE.md rule 13).
> This set was written to the [authoring standard](AUTHORING_STANDARD.md), with the same structure as the [A.1 example](a1-kinematics-pilot-questions.md).
>
> **Source:** only syllabus node C.4 ([dp-physics-2025-analysis.md](../syllabus/dp-physics-2025-analysis.md)), the format profile and
> general physics. No exam paper, textbook or internet question was used as input; the scenarios are original.
> **Numerical check:** all numerical answers and all numerical distractors were recomputed with `python3` (standard library only).
> Constants: speed of sound in air 340 m s⁻¹ (given in the question). The wave speeds on the wire (120 and 260 m s⁻¹) are given in the question.
> **Not verified:** (1) it was solved by an independent blind solver; it has not been through expert review; (2) it has not been checked by an expert
> for similarity to a known exam question; (3) the naming of harmonics in a pipe closed at one end (odd harmonics only: first, third, fifth)
> was not confirmed from the guide, so Question 2 was asked without using a harmonic number; (4) the statement in Question 4 that "as damping increases, the frequency at which the maximum amplitude
> occurs falls slightly" is correct for amplitude resonance; how far the guide expects this detail was not confirmed;
> (5) the qualitative questions (Question 3, 4 and Question 5 a, d, e) cannot be verified by code.

## Scope table

| # | Section | Level | Outcome (C.4) | Objective | Command terms | Marks | Difficulty |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Wavelength and frequency of the nth harmonic on a string fixed at both ends | AO2 | — | 1 | Easy |
| 2 | Paper 1A | SL | Allowed standing wave patterns in a pipe closed at one end | AO3 | — | 1 | Medium |
| 3 | Paper 1A | SL | Phase in a standing wave: points on either side of a node | AO2 | — | 1 | Medium |
| 4 | Paper 1A | SL | Qualitative effect of damping on the maximum amplitude and the resonant frequency | AO2 | — | 1 | Medium |
| 5 | Paper 2 | SL | Formation of a standing wave; first harmonic; node–antinode pattern; resonance; damping | AO1–AO3 | Outline, Show that, State, Calculate, Explain | 9 | Medium |

This set does not cover all of C.4. Not covered: patterns in a pipe open at both ends; the variation of amplitude with position in a standing wave; comparing a standing wave
with a travelling wave; interpreting the relationship between natural frequency and driving frequency from a graph; the displacement–time behaviour of light, critical and heavy damping;
useful and harmful examples of resonance.

Terminology check: only "first harmonic" and "third harmonic" are used in the set; the "fundamental / overtone" equivalents that the guide asks to avoid appear in no question text or markscheme. There is no end correction,
pressure node or superposition of more than two waves.

---

## Question 1 — Paper 1A

A string of length 0.75 m is fixed at both ends. The speed of waves on the string is 120 m s⁻¹.

What is the frequency of the third harmonic of the string?

A. 80 Hz
B. 160 Hz
C. 240 Hz
D. 480 Hz

**Answer: C**

**Solution.** In the third harmonic there are three half-wavelengths on the string: λ = 2L / 3 = 0.50 m. f = v / λ = 120 / 0.50 = 240 Hz.

| Option | Misconception |
|---|---|
| A | Gives the frequency of the first harmonic: λ = 2L = 1.5 m → 120 / 1.5 = 80 Hz |
| B | Takes the wavelength to be equal to the length of the string (second harmonic): 120 / 0.75 = 160 Hz |
| D | Takes λ = L / 3 in the third harmonic (confuses half a wavelength with a full wavelength): 120 / 0.25 = 480 Hz |

---

## Question 2 — Paper 1A

A tube of length 0.17 m is closed at one end and open at the other end. The air in the tube vibrates in its first harmonic at a
frequency of 500 Hz. The speed of sound in air is 340 m s⁻¹.

What is the next higher frequency at which a standing wave can be formed in the tube?

A. 1000 Hz
B. 1500 Hz
C. 2500 Hz
D. 3000 Hz

**Answer: B**

**Solution.** There is a displacement node at the closed end and an antinode at the open end. First harmonic: L = λ/4 → f₁ = 340 / (4 × 0.17) = 500 Hz. The
next allowed pattern: L = 3λ/4 → λ = 0.227 m → f = 3 × 500 = 1500 Hz.

| Option | Misconception |
|---|---|
| A | Assumes that all whole-number multiples of the first harmonic also occur in a pipe closed at one end: 2 × 500 = 1000 Hz (this pattern does not satisfy the node condition at the closed end) |
| C | Skips an allowed pattern (L = 5λ/4): 5 × 500 = 2500 Hz; a standing wave forms at this frequency but it is not the "next" one |
| D | Uses the relation for a pipe open at both ends for the third harmonic: 3 × 340 / (2 × 0.17) = 3000 Hz |

---

## Question 3 — Paper 1A

A standing wave of wavelength 0.80 m is formed on a string. Point X on the string is 0.10 m to the left of a node. Point Y on the
string is 0.10 m to the right of the same node.

What is the phase difference between the oscillations of X and Y?

A. 0
B. π/4 rad
C. π/2 rad
D. π rad

**Answer: D**

**Solution.** The separation of adjacent nodes is λ/2 = 0.40 m; X and Y are in neighbouring loops on either side of the same node. In a standing wave all the points within one loop
are in phase; points in the neighbouring loop are in antiphase. The phase difference is π rad.

| Option | Misconception |
|---|---|
| A | Assumes all points in a standing wave are in phase (true only within the same loop) |
| B | Uses the travelling-wave relation with the distance of one point from the node: 2π × 0.10 / 0.80 = π/4 |
| C | Uses the travelling-wave relation with the distance X–Y: 2π × 0.20 / 0.80 = π/2 |

---

## Question 4 — Paper 1A

A lightly damped system is driven by a periodic force. The frequency of the driving force is varied and the amplitude of the
system is measured. The damping of the system is then increased, but the damping remains light.

What is the effect of the increased damping on the maximum amplitude and on the frequency at which the maximum amplitude occurs?

A. The maximum amplitude decreases and it occurs at a slightly lower frequency.
B. The maximum amplitude decreases and it occurs at a slightly higher frequency.
C. The maximum amplitude increases and it occurs at a slightly lower frequency.
D. The maximum amplitude increases and it occurs at a slightly higher frequency.

**Answer: A**

**Solution.** As damping increases, the system loses more energy in each oscillation; the maximum amplitude at resonance decreases and the resonance curve
broadens. The frequency at which the maximum amplitude occurs shifts slightly below the natural frequency.

| Option | Misconception |
|---|---|
| B | Gets the amplitude effect right but takes the frequency shift to be in the opposite direction ("damping stiffens the system") |
| C | Gets the frequency effect right; assumes damping "sharpens and raises" the resonance peak |
| D | Takes both effects to be the other way round |

Note: the options are in sentence form; according to the format profile this type is in the minority but is used. Because two quantities are asked together, sentences were preferred to
table-style options (the table style could not be verified).

---

## Question 5 — Paper 2 (9 marks)

A steel wire is stretched between two fixed supports that are 0.65 m apart. A vibrator attached to the wire close to one support
is connected to a signal generator. The speed of waves on the wire is 260 m s⁻¹.

> **Figure:** A horizontal wire stretched between two fixed supports on a bench; the distance between the supports is marked as 0.65 m; close to the left support
> is a vibrator attached to the wire, connected to a signal generator. "diagram not to scale". The question can be solved without the figure.

**(a)** Outline how a standing wave is formed on the wire. [2]

**(b)** Show that the frequency of the first harmonic of the wire is 200 Hz. [2]

The frequency of the signal generator is set to 600 Hz and a standing wave is observed on the wire.

**(c)** (i) State the number of antinodes on the wire. [1]

 (ii) Calculate the distance between adjacent nodes. [1]

The frequency of the signal generator is now increased slowly from 150 Hz to 250 Hz.

**(d)** Explain why the amplitude of vibration at the centre of the wire becomes very large at one frequency in this range. [2]

**(e)** The damping of the wire is increased. State the effect of this on the maximum amplitude observed in (d). [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 5. | a | | waves «from the vibrator» travel along the wire and are reflected at the fixed end(s) ✓<br>the incident and reflected waves / waves travelling in opposite directions superpose ✓ | *OWTTE*<br>*Accept "interfere" for "superpose".* | 2 |
| 5. | b | | *λ* = 2 × 0.65 = 1.3 «m» ✓<br>*f* = 260 / 1.3 «= 200 Hz» ✓ | *Both the wavelength and the substitution must be shown; the answer alone scores [0] because it is given.* | 2 |
| 5. | c | i | 3 ✓ | | 1 |
| 5. | c | ii | 0.65 / 3 = 0.22 «m» ✓ | *Allow ECF from (c)(i).*<br>*Accept* λ/2 = 260 / (2 × 600) = 0.22 «m». | 1 |
| 5. | d | | the driving frequency equals the natural frequency / first harmonic frequency of the wire «about 200 Hz» ✓<br>resonance occurs **OR** energy is transferred to the wire at the maximum rate, «so the amplitude is a maximum» ✓ | *OWTTE*<br>*Accept "the centre of the wire is an antinode of the first harmonic" as supporting detail, not as a marking point.* | 2 |
| 5. | e | | the maximum amplitude decreases ✓ | | 1 |

### Formula chain (solution model)

| Step | Expression | Result |
|---|---|---|
| Parameters | `L = 0.65 m`, `v = 260 m/s`, `f_gen = 600 Hz` | |
| `lam_1` | `2*L` | 1.30 m |
| `f_1` | `v/lam_1` | 200 Hz |
| `n` | `f_gen/f_1` | 3 → 3 antinodes, 4 nodes (including the ends) |
| `node_sep` | `L/n` | 0.217 m |
| Check | `v/f_gen/2` | 0.217 m |

---

## Format conformance

The questions were reviewed against the [format profile](../formats/dp-physics-2025-format-profile.md) (2026-10-11).

| Rule | Status |
|---|---|
| 1A: context + a separate single question sentence ("What is …?") + A–D listed one below the other | Questions 1–4 conform |
| 1A: four options of the same type, same unit, in order of magnitude | Questions 1–3 conform (ascending); Question 4 is in sentence form, the four options in the same pattern |
| 1A: correct-answer letters balanced | C, B, D, A |
| 1A: solvable without a figure | Questions 1–4 need no figure |
| Paper 2: sub-part marks at most 3; short question 4–9 marks | Question 5 conforms (2, 2, 1, 1, 2, 1; total 9). On an SL paper short questions of 4–6 marks were observed; for an SL paper (c) or (e) can be removed |
| Paper 2: "Show that" pattern and at least one AO3 part | Question 5 (b) Show that ("about" was not used because the result is exactly 200 Hz), (d) Explain |
| Markscheme: four-column table, ✓, « », OR, ECF, OWTTE | Question 5 conforms |
| Paper 2: drawing part (Draw / Sketch) | **Missing:** no part asking for a standing wave pattern to be drawn was written; it requires a figure template |
| Syllabus limit: "first harmonic"; no end correction; displacement nodes only; damping qualitative | Conforms; the effect of damping is only qualitative in Question 4 and 5(e) |
| Value–unit notation (m s⁻¹), 2 significant figures | Conforms; frequency options are whole numbers of Hz |

## Independent check

Date: 2026-10-11. This file was solved by an independent blind solver who did not see the answers; the solver independently reproduced all answer
keys and markscheme results (no CRITICAL findings). Findings:
[review/c4-review.md](review/c4-review.md). This does not replace expert review.

Changes made in response to the findings (every changed number was rechecked with `python3` against the final text of the file):

- **Question 5 (b) (LOW):** because the calculation gives exactly 200 Hz, "about" was removed from the stem ("… is about 200 Hz" → "… is 200 Hz"); the second point in the markscheme was written so as to require the substitution. The data were not changed, because if the speed changed, 600 Hz would no longer coincide exactly with the third harmonic and (c) would break.
- **Question 5 (LOW):** the note that 9 marks is long for SL was already in the "Format conformance" table; the question was not split. The decision to split should be made when the exam paper is assembled.
- **Not applied:** writing the phase difference in Question 3 in degrees or in words instead of radians. The review says "no change is needed until an expert confirms"; the C.4 row of the syllabus analysis lists "phase" as an SL outcome and the distractors (π/4, π/2) are based on calculable misconceptions. Left for expert confirmation.
