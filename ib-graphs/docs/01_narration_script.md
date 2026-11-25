# Reading Motion and Momentum Graphs — Narration script

_Generated from `config/scenes.json` by `tools/make_script_doc.py`; edit the JSON, not this file._

- Voice: Phonon 31M `Hadley`, words-per-minute measured while talking (fallbacks: edge-tts `en-US-AriaNeural` at `+4%`, then Piper `en_US-lessac-medium`)
- `[PAUSE]` = 0.55 s of silence so the visuals can breathe; sentences are 0.18 s apart; speech is time-stretched to 0.99x speed (pitch kept; below 1 is slower).
- Scene lengths come from the audio (`audio/timings.json`); every animation is keyed to the words.

## Scene 1 (s01) — Two moves: gradient and area

**0:00.0 – 0:35.3** (35.3 s) · 86 words · speech 31.0 s · 166 wpm · ends at 0:34.6

Motion graphs look like a zoo of curves. But every one of them is read with just two moves: take the gradient, or take the area. **[PAUSE]** Watch a cart speed up, cruise, and brake. Its displacement, velocity and acceleration graphs are drawn together, and they are really one story told three ways. Gradient takes you down the ladder, from displacement to velocity to acceleration. Area takes you back up. **[PAUSE]** Then we'll use the same two moves on forces: momentum, force and impulse. Same ladder, different quantities.

## Scene 2 (s02) — What gradient and area mean

**0:35.3 – 1:14.7** (39.4 s) · 101 words · speech 35.9 s · 169 wpm · ends at 1:14.0

First, what do gradient and area actually mean? The gradient is rise over run: how much the vertical quantity changes for each unit of the horizontal one. The area is the vertical quantity times the horizontal quantity. **[PAUSE]** Here's a trick that never fails: read the units. On a displacement-time graph, the gradient is metres per second. That's velocity. On a velocity-time graph, the area is metres per second, times seconds. That's metres, so displacement. **[PAUSE]** So whenever you meet a new graph, ask: what are the axes? The gradient is one divided by the other. The area is one times the other.

## Scene 3 (s03) — Constant velocity

**1:14.7 – 1:50.3** (35.6 s) · 81 words · speech 32.7 s · 149 wpm · ends at 1:49.6

Start with the simplest motion: constant velocity. On the displacement-time graph that's a straight line, and its gradient is the velocity. A steeper line means a faster object. **[PAUSE]** Flat means stationary. A line sloping down means moving backwards: a negative velocity. **[PAUSE]** Underneath, the velocity-time graph is a horizontal line at each of those values. The area under it, a rectangle, is velocity times time, which is exactly the displacement. And the acceleration-time graph sits on zero, because the velocity never changes.

## Scene 4 (s04) — Constant acceleration

**1:50.3 – 2:30.6** (40.3 s) · 99 words · speech 37.1 s · 160 wpm · ends at 2:29.9

Now let the velocity change steadily: constant acceleration. The acceleration-time graph is a flat line, and the area under it, acceleration times time, is the change in velocity. **[PAUSE]** That makes the velocity-time graph a straight line, sloping up. Its gradient is the acceleration. **[PAUSE]** And on the displacement-time graph, the gradient keeps growing, so the line curves up into a parabola. At every moment, the slope of the tangent is the height of the velocity graph. A gentle slope early on, a steep slope later. **[PAUSE]** Check it with the units: metres per second squared, times seconds, gives metres per second.

## Scene 5 (s05) — The equations from one graph

**2:30.6 – 3:42.4** (71.8 s) · 173 words · speech 67.1 s · 155 wpm · ends at 3:41.7

The velocity-time graph hands you the equations of constant acceleration for free. Start at the initial velocity, and finish at the final velocity after a time t. **[PAUSE]** The gradient is the acceleration, so the change in velocity divided by the time is the acceleration. Rearrange it: final velocity equals initial velocity plus acceleration times time. **[PAUSE]** Now the displacement is the area under the line. Split it into a rectangle and a triangle. The rectangle is the initial velocity times the time. The triangle is a half, times the base, times the height, and the height is acceleration times time. Add them: displacement equals initial velocity times time, plus a half, acceleration times time squared. **[PAUSE]** Or treat the whole shape as one trapezoid: average height times width. Displacement equals the average of the initial and final velocity, times the time. **[PAUSE]** Finally, eliminate the time. Put the time from the first equation into the trapezoid, and final velocity squared equals initial velocity squared plus two times acceleration times displacement. Four equations, all from one picture.

## Scene 6 (s06) — Average and instantaneous velocity

**3:42.4 – 4:16.3** (33.9 s) · 94 words · speech 31.0 s · 182 wpm · ends at 4:15.6

Back on the displacement-time graph, a curve has a different gradient at every point. Pick two points on the curve and join them. The gradient of that chord is the average velocity between them. **[PAUSE]** Now slide one point toward the other. The chord swings round, and in the limit it becomes the tangent. The gradient of the tangent is the instantaneous velocity. **[PAUSE]** A common mistake: to find an instantaneous value, use two points on the tangent line, not two points on the curve. Two points on the curve only ever give you an average.

## Scene 7 (s07) — A ball thrown up: signs, displacement and distance

**4:16.3 – 5:07.7** (51.4 s) · 137 words · speech 47.7 s · 172 wpm · ends at 5:07.0

Throw a ball straight up, and take upward as positive. The velocity starts positive, shrinks to zero at the top, then becomes negative as the ball comes back down. So the velocity-time graph is a straight line sloping down. Its gradient is minus nine point eight one: the acceleration is the same negative number the whole way, even at the top, where the velocity is zero. **[PAUSE]** Now the displacement-time graph. It rises, flattens at the top, where the gradient is zero, and then falls. **[PAUSE]** Look at the areas. The area above the axis is positive displacement. The area below is negative. They cancel, so the ball ends where it started: the displacement is zero. But the distance travelled adds up the sizes of the areas, ignoring the signs. Up and down, that's thirty nine point two metres.

## Scene 8 (s08) — Non-uniform acceleration and terminal velocity

**5:07.7 – 5:59.3** (51.6 s) · 122 words · speech 48.2 s · 152 wpm · ends at 5:58.6

Real motion rarely has constant acceleration. Drop a ball into oil, or let a skydiver fall. At first the acceleration is close to nine point eight one. As the speed grows, the drag grows, so the acceleration shrinks. **[PAUSE]** The velocity-time graph curves over and levels off. Its gradient, the acceleration, falls toward zero: that's terminal velocity. Zero acceleration does not mean zero velocity: the object is still falling, at a steady speed. **[PAUSE]** Displacement is still the area under the velocity-time graph, and acceleration is still the gradient of the tangent. But the constant acceleration equations no longer apply. For a curve, estimate the area by counting squares. And the displacement-time graph ends up a straight line, because the velocity has become constant.

## Scene 9 (s09) — Projectile motion

**5:59.3 – 6:32.0** (32.7 s) · 91 words · speech 30.5 s · 179 wpm · ends at 6:31.3

A projectile is two motions at once. Horizontally there is no force, so the horizontal velocity is constant: a flat velocity graph and a straight displacement graph. Vertically there is only gravity, so it's the thrown ball again: a velocity line sloping down through zero at the top, and a parabola for the height. **[PAUSE]** At the top, the vertical velocity is zero, but the horizontal velocity is not, so the ball has not stopped. And the two sets of graphs never mix. Time is the only thing the two motions share.

## Scene 10 (s10) — Momentum-time graphs and force

**6:32.0 – 7:11.2** (39.2 s) · 99 words · speech 36.1 s · 165 wpm · ends at 7:10.5

Now forces and momentum. Momentum is mass times velocity, so a momentum-time graph is just the velocity-time graph, scaled by the mass. **[PAUSE]** Newton's second law, in its general form, says the resultant force is the rate of change of momentum. That's a gradient. So the gradient of a momentum-time graph is the resultant force. **[PAUSE]** Check the units: kilogram metres per second, divided by seconds, is kilogram metres per second squared, which is a newton. A steep line means a big force. A flat line means no resultant force. A line sloping down means the force points the other way.

## Scene 11 (s11) — Force-time graphs and impulse

**7:11.2 – 8:20.2** (69.0 s) · 183 words · speech 64.5 s · 170 wpm · ends at 8:19.5

Now flip it round. If force is the gradient of momentum, then the area under a force-time graph must be the change in momentum. That area is called the impulse. **[PAUSE]** Check the units. Newtons times seconds, and a newton second is the same unit as a kilogram metre per second. For a constant force the area is a rectangle: force times time. For a varying force, split the area into shapes, or count squares. **[PAUSE]** Take a triangular pulse, six thousand newtons high and ten milliseconds wide. The area is a half, times six thousand, times point zero one: thirty newton seconds. So the momentum changes by thirty. **[PAUSE]** Area below the axis counts as negative. A ball of mass point one five kilograms hits a wall at twenty metres per second and rebounds at ten. Take the first direction as positive. The momentum goes from plus three to minus one point five, so the impulse is minus four point five newton seconds. If the contact lasts ten milliseconds, the average force, the impulse divided by the time, is minus four hundred and fifty newtons.

## Scene 12 (s12) — From force to momentum to velocity

**8:20.2 – 8:55.6** (35.4 s) · 97 words · speech 32.5 s · 179 wpm · ends at 8:54.9

Now chain them together. Start with a force-time graph: a push that builds up, holds steady, and fades away. The momentum-time graph is the running total of that area. While the force is growing, the momentum climbs faster and faster. While the force is steady, it climbs in a straight line. When the force fades to zero, the momentum levels off. **[PAUSE]** Divide by the mass, and the same shape is the velocity-time graph. And notice the pattern. Force is to momentum what velocity is to displacement. The gradient goes one way, and the area goes the other.

## Scene 13 (s13) — Contact time and rebounds

**8:55.6 – 9:33.3** (37.7 s) · 112 words · speech 35.2 s · 191 wpm · ends at 9:32.6

The same impulse can come from very different graphs. Drop an egg on concrete, and it stops in a thousandth of a second: a tall, narrow spike. Drop it on a pillow, and it stops over a tenth of a second: a low, wide hill. The areas are equal, because the change in momentum is the same, so the pillow's peak force is far smaller. That's the idea behind airbags, crumple zones and bending your knees. **[PAUSE]** And a bounce hits harder than a stop. Stopping removes the momentum: call that one unit of area. Bouncing back at the same speed reverses it, so the change is double, and so is the area.

## Scene 14 (s14) — Collisions on graphs

**9:33.3 – 10:11.7** (38.3 s) · 98 words · speech 35.2 s · 167 wpm · ends at 10:11.0

Finally, a collision between two carts. During the contact, cart one pushes cart two, and cart two pushes back on cart one with the same force, for the same time. That's Newton's third law. So the two force-time graphs are mirror images: equal height, opposite sign. **[PAUSE]** Their areas are therefore equal and opposite, so the impulses are equal and opposite. One cart gains exactly the momentum the other loses. **[PAUSE]** Now plot the momentum of each cart, and the total. One line rises, the other falls, and the sum stays flat. That's conservation of momentum, seen on a graph.

## Scene 15 (s15) — The ladders and three questions

**10:11.7 – 10:45.4** (33.7 s) · 80 words · speech 28.7 s · 167 wpm · ends at 10:42.2

So here are the two ladders. Displacement, velocity, acceleration: gradients go down, and areas go up. Momentum and force: the gradient of momentum is force, and the area under force is the change in momentum. **[PAUSE]** Whenever a graph appears, ask three questions. What are the axes? So what do the gradient and the area mean, by their units? And does the graph go below zero, so that signs matter? Answer those, and you can read any graph in the course.

---

**Total: 10:45.4 (645 s), 1653 words, 167 wpm while speaking.**

## Pronunciation overrides (sent to TTS only; subtitles keep the real spelling)

| Written | Spoken as |
|---|---|
| Newton's | Newton's |
| kg | kilograms |
