# Research: contact forces in IB Physics SL (first assessment 2025)

**Scope of the video:** how every contact force is drawn and derived on a free-body diagram,
with the trigonometry made visible.

**Excluded, as requested:** elastic (Hooke's law) forces, circular motion, and kinematics (suvat).
Newton's second law (ΣF = ma) is used only where a force itself is being found, as in lifts and pulleys.

## 1. Where it sits in the syllabus

The topic is **A.2 Forces and momentum** (SL and HL; the SL content is the same). The guide lists these
contact forces, with the data-booklet forms below:

| Force | IB symbol | Relation | Notes |
|---|---|---|---|
| Normal (reaction) force | F_N | none: found from equilibrium or ΣF = ma | always perpendicular to the surface |
| Static friction | F_f | **F_f ≤ μs F_N** | an inequality: it only grows as large as needed |
| Dynamic friction | F_f | **F_f = μd F_N** | μd < μs; independent of contact area |
| Tension | F_T (often T) | none | along the string, away from the body; same throughout a light string; a light smooth pulley changes its direction, not its size |
| Viscous drag | F_d | **F_d = 6πηrv** (Stokes) | small, smooth, slow sphere in laminar flow only |
| Buoyancy (upthrust) | F_b | **F_b = ρVg** | ρ is the **fluid's** density; V is the volume of fluid displaced |
| Elastic | F_H = −kx | *excluded* | |

Weight (F_g = mg) is a field force, not a contact force. It appears in every diagram because
mg sin θ and mg cos θ are its components.

## 2. The standard free-body-diagram scenarios

| # | Scenario | Key result | Trig step |
|---|---|---|---|
| 1 | Block at rest on a level surface | F_N = mg | none: a single vertical balance |
| 2 | Block pulled by a rope at θ **above** the horizontal | F_N = mg − F sin θ; friction μ(mg − F sin θ) | F → F cos θ (horizontal), F sin θ (vertical) |
| 3 | Block pushed at θ **below** the horizontal | F_N = mg + F sin θ | as above, with the vertical part pressing down |
| 4 | Person in a lift accelerating up or down | F_N = m(g + a) or F_N = m(g − a); weight unchanged | none |
| 5 | Block on a smooth incline | F_N = mg cos θ; down-slope component mg sin θ | weight resolved along/perpendicular to the slope; the angle between mg and the slope normal equals θ |
| 6 | Block on a rough incline, at rest | F_f = mg sin θ (≤ μs mg cos θ) | as in 5 |
| 7 | On the point of slipping (angle of repose) | **μs = tan θ** (mass cancels) | sin θ / cos θ = tan θ |
| 8 | Sliding on a rough incline | resultant = mg sin θ − μd mg cos θ | as in 5 |
| 9 | Block held on a smooth incline by a **horizontal** force | F = mg tan θ; F_N = mg cos θ + F sin θ (can exceed mg) | F also resolved: the angle between F and the slope is θ |
| 10 | Mass hanging from one string | T = mg | none |
| 11 | Lamp on two strings at α to the horizontal (symmetric) | T = mg / (2 sin α), which grows without limit as α → 0 | T → T cos α, T sin α |
| 12 | Lamp on two strings at α₁, α₂ (asymmetric) | T₁ cos α₁ = T₂ cos α₂; T₁ sin α₁ + T₂ sin α₂ = mg | two-direction balance, or a closed triangle of forces |
| 13 | Block on a table tied over a pulley to a hanging mass | T = Ma; mg − T = ma (same T, same a) | none |
| 14 | Floating or submerged block | F_b = ρ_f V g; floating: ρ_f V_sub g = mg | pressure difference between the top and bottom faces |
| 15 | Sphere falling through oil at terminal speed | mg = F_b + 6πηr v_t → v_t = 2r²g(ρ_s − ρ_f) / 9η | none: an algebraic force balance |

## 3. Misconceptions the video must address

* Normal force ≠ mg in general. It changes with angled pulls and pushes, with acceleration in a lift, and on slopes.
* Weight and normal force are **not** a Newton's third-law pair: both act on the same body. The partner of weight
  is the body pulling the Earth.
* Static friction is an **inequality**. It equals μs F_N only at the point of slipping.
* Buoyancy uses the **fluid** density.
* Stokes' law only applies to small, slow spheres in laminar flow.
* Only draw forces exerted *on* the body by something you can name. Never draw "ma" as a force.
* Choose axes along and perpendicular to the surface: then the normal force appears directly.
* Trig rule: *the component next to the angle takes cos; the one opposite takes sin.*
  Limit checks: θ = 0 gives (mg, 0); θ = 90° gives (0, mg).

## 4. Why the angle between mg and the slope normal is θ (the key proof)

The proof follows the visual:

1. Start the slope flat. Its perpendicular is vertical and lies exactly along mg.
2. Tilt the slope by θ. Everything attached to it, including its perpendicular, turns by the same θ.
3. So the angle from vertical (mg) to the slope's perpendicular is θ.
4. Equivalent geometric argument: in the right triangle formed by the slope and the horizontal, the angle between
   mg and the slope is 90° − θ. The perpendicular is 90° from the slope, so the angle between mg and the
   perpendicular is 90° − (90° − θ) = θ.

## Sources

* TutorChase, IB Physics 2025, *1.2.2 Contact Forces*: https://www.tutorchase.com/notes/ib/physics-2025/1-2-2-contact-forces
* The Prof Sir, *A.2 Forces and Momentum* (IB notes, worked examples, misconceptions): https://theprofsir.com/ib/a2-forces-and-momentum/
* GradePod, *IB Physics A.2 Forces and Momentum*: https://gradepod.com/topics/a2-forces-and-momentum/
* TutorChase IBDP Physics SL cheat sheet, A.2: https://www.tutorchase.com/cheat-sheets/ib/physics-2025/ibdp-physics-sl-cheat-sheet---a-2-forces-and-momentum
* Save My Exams, upthrust (F_b = ρVg): https://savemyexams.com/dp/physics/hl/25/revision-notes/space-time-and-motion/forces-and-momentum/upthrust
* IB Physics data booklet (first assessment 2025), as reproduced by schools, e.g. https://tuhsphysics.ttsd.k12.or.us/DocumentsAndLectures/Documents/IB_Physics_II/00BeginningOfYear/DataBooklet2025.pdf

Caveat: the official IBO guide was not directly accessible; the content list was cross-checked across the sources above.
