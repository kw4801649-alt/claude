# Research: motion and momentum graphs in IB Physics SL (first assessment 2025)

**Scope of the video:** every graph used in **A.1 Kinematics** and **A.2 Forces and momentum**, and the two moves
that read them (gradient and area). Work, energy and power graphs (A.3) are not included, and neither are
elastic-force (Hooke) graphs or circular motion.

## 1. The two moves, and the units trick

| Graph | Gradient means | Area means | Check by units |
|---|---|---|---|
| displacement–time (s–t) | velocity (m s⁻¹) | not used | m ÷ s |
| velocity–time (v–t) | acceleration (m s⁻²) | **signed** displacement (m) | m s⁻¹ × s |
| acceleration–time (a–t) | not used at this level | change in velocity (m s⁻¹) | m s⁻² × s |
| momentum–time (p–t) | **resultant force** (N) | not used | kg m s⁻¹ ÷ s = N |
| force–time (F–t) | not used | **impulse** = change in momentum (N s) | N × s = kg m s⁻¹ |

Rule: the gradient is vertical ÷ horizontal, the area is vertical × horizontal, so the units say what they mean.

## 2. A.1 Kinematics: the graph content

1. **Constant velocity.** s–t is a straight line; steeper means faster; flat means at rest; sloping down means negative velocity.
   v–t is horizontal and the rectangle under it is the displacement. a–t is zero.
2. **Constant acceleration.** a–t is a flat line; the area under it is Δv. v–t is a straight line with gradient *a*.
   s–t is a parabola whose tangent gradient at each moment equals the height of the v–t graph.
3. **The equations of constant acceleration all come from the v–t graph.**
   * v = u + at: the gradient of the line.
   * s = ut + ½at²: the rectangle (ut) plus the triangle (½·t·at).
   * s = ½(u + v)t: the whole trapezoid, average height × width.
   * v² = u² + 2as: eliminate t between the first and third.
4. **Average and instantaneous velocity.** The chord between two points on an s–t curve gives the average velocity.
   Letting one point approach the other turns the chord into the tangent; the tangent's gradient is the instantaneous velocity.
   Common mistake: use two points on the *tangent* (not on the curve) to find an instantaneous value.
5. **Signs.** Signed area above the axis is positive displacement, below is negative. Displacement is the net signed area;
   distance is the sum of the magnitudes (and is the area of a *speed*–time graph).
   The acceleration is a single negative number all through a ball's flight, including at the top where v = 0.
6. **Non-uniform acceleration (fluid resistance).** v–t is a curve that levels off at terminal speed.
   The acceleration (tangent gradient) falls to zero, but zero acceleration is **not** zero velocity.
   The s–t graph ends as a straight line. The area under a curved v–t is estimated by counting squares.
   The constant-acceleration equations no longer apply.
7. **Projectile motion (no drag).** Horizontal and vertical motions are independent:
   x–t is straight, vₓ–t is flat, aₓ = 0; y–t is a parabola, v_y–t is a straight line through zero at the top with gradient −g.
   At the top v_y = 0 but vₓ ≠ 0.
8. **Measuring g.** Plot s against t² (release from rest): a straight line through the origin with gradient g/2.
   Or take the gradient of a v–t graph from a motion sensor. (Mentioned in the notes; not animated.)

## 3. A.2 Forces and momentum: the graph content

1. **Momentum** p = mv, so a p–t graph is the v–t graph scaled by the mass.
2. **Newton's second law in momentum form**: F = Δp/Δt, so the **gradient of a p–t graph is the resultant force**.
   Steeper means a larger force; flat means zero resultant force; sloping down means the force is opposite.
3. **Impulse** J = FΔt = Δp. On an F–t graph the **signed area** is the impulse and equals the change in momentum.
   Below the axis counts as negative. Constant force: a rectangle. Varying force: split into shapes, or count squares.
   Average force = impulse ÷ contact time.
4. **Worked examples** (from the source notes):
   * Triangular pulse, base 10 ms, height 6000 N: area = ½ × 0.010 × 6000 = **30 N s**, so Δp = +30 kg m s⁻¹.
   * 0.15 kg ball, +20 m s⁻¹ to −10 m s⁻¹, contact 0.010 s: p goes +3.0 → −1.5 kg m s⁻¹;
     impulse **−4.5 N s**; average force **−450 N**.
5. **Chaining the graphs.** F–t → p–t is the running area (p–t is the integral of F–t); p–t ÷ m is v–t.
   So *force is to momentum what velocity is to displacement*.
6. **Contact time.** The same Δp from a short contact (tall spike) or a long contact (low hill): equal areas, different peak force.
   Airbags, crumple zones, bending knees. A rebound at the same speed reverses the momentum, so Δp (and the area) is double that of stopping.
7. **Collisions.** Newton's third law: during contact the two forces are equal and opposite for the same time, so the
   two F–t graphs are mirror images and the impulses are equal and opposite. One p–t graph rises as the other falls and
   their sum is constant (conservation of momentum, isolated system).

## 4. Misconceptions the video must address

* Zero velocity at the top of a throw does **not** mean zero acceleration.
* Zero acceleration at terminal speed does **not** mean zero velocity.
* Displacement is the *signed* area; distance is the *unsigned* total.
* Average velocity (chord) is not instantaneous velocity (tangent); take the tangent's two points from the tangent line.
* A projectile at its highest point has stopped vertically, not horizontally.
* Impulse is the area under **force**–time, not under momentum–time; momentum–time gives force by its gradient.
* The constant-acceleration equations need constant acceleration (a straight v–t line).

## Sources

* Clastify, IB Physics notes *A.1 Kinematics*: https://www.clastify.com/subjects/physics/notes/space-time-and-motion/kinematics
* Clastify, IB Physics notes *A.2 Forces and momentum*: https://www.clastify.com/subjects/physics/notes/space-time-and-motion/forces-and-momentum
* TES, *IB DP Physics (2025) A2.7 Momentum, Impulse and F = Δp/Δt*: https://www.tes.com/en-ie/teaching-resource/ib-dp-physics-2025-a2-7-momentum-impulse-and-f-equals-p-t-13587515
* Megalecture, *A.2 Forces and Momentum*: https://megalecture.com/library/ib-physics-a-2-forces-and-momentum/
* RevisionDojo, *IB Physics Forces and Momentum Explained*: https://www.revisiondojo.com/blog/ib-physics-forces-momentum-explained

Caveat: the official IB guide was not directly accessible; the content list was cross-checked across the sources above.
