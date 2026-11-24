# Contact Forces, Derived — Narration script

_Generated from `config/scenes.json` by `tools/make_script_doc.py`; edit the JSON, not this file._

- Voice: Phonon 31M `Hadley`, words-per-minute measured while talking (fallbacks: edge-tts `en-US-AriaNeural` at `+4%`, then Piper `en_US-lessac-medium`)
- `[PAUSE]` = 0.55 s of silence so the visuals can breathe; sentences are 0.14 s apart; speech is sped up 1.06x (pitch kept).
- Scene lengths come from the audio (`audio/timings.json`); every animation is keyed to the words.

## Scene 1 (s01) — Where does mg sin θ come from?

**0:00.0 – 0:26.7** (26.7 s) · 64 words · speech 23.5 s · 163 wpm · ends at 0:26.1

Every force problem in IB Physics comes down to two moves: draw the forces, then split them into components. So where does mg sin θ actually come from? **[PAUSE]** In the next few minutes we'll derive every contact force you need: the normal force, friction, tension, buoyancy and viscous drag. No springs, no circles, no kinematics. Just forces, triangles, and the trigonometry that connects them.

## Scene 2 (s02) — The one tool: resolving a force

**0:26.7 – 1:05.3** (38.6 s) · 119 words · speech 36.1 s · 198 wpm · ends at 1:04.7

First, the one tool we'll use over and over. A force is an arrow with a size and a direction, and any arrow can be replaced by two perpendicular arrows that add up to it. **[PAUSE]** Make the force F the hypotenuse of a right-angled triangle, at angle θ to the horizontal. Cosine is adjacent over hypotenuse, so the side touching the angle is F cos θ. Sine is opposite over hypotenuse, so the side across from the angle is F sin θ. **[PAUSE]** Swing the angle and watch: as one component grows, the other shrinks, but together they always rebuild F. The rule to remember: cos goes with the side touching θ, sin goes with the side across from it.

## Scene 3 (s03) — Normal force on a flat surface

**1:05.3 – 1:34.7** (29.5 s) · 85 words · speech 26.9 s · 190 wpm · ends at 1:34.1

Start simple: a block resting on a table. Its weight, mg, pulls straight down. The table pushes back up with the normal force, normal meaning perpendicular to the surface. **[PAUSE]** Nothing accelerates, so the vertical forces balance, and the normal force equals mg. **[PAUSE]** But these two are not a Newton's third law pair. Both act on the block. The partner of the weight is the block pulling the Earth upward. And the normal force only equals mg here because nothing else is pushing up or down.

## Scene 4 (s04) — Pulled or pushed at an angle

**1:34.7 – 2:10.5** (35.8 s) · 103 words · speech 33.3 s · 186 wpm · ends at 2:09.9

Now pull the block with a rope at angle θ above the horizontal. Split the pull: F cos θ drags the block sideways, and F sin θ lifts it a little. **[PAUSE]** Vertically, everything still balances: the normal force plus F sin θ equals mg. So the normal force is mg minus F sin θ. Pull harder and the surface pushes back less. **[PAUSE]** Push down at the same angle instead, and the vertical part adds to the weight: the normal force becomes mg plus F sin θ. Since friction is proportional to the normal force, pulling up reduces friction, and pushing down increases it.

## Scene 5 (s05) — Normal force in a lift

**2:10.5 – 2:34.8** (24.3 s) · 68 words · speech 22.4 s · 182 wpm · ends at 2:34.2

The normal force is also what you feel through your feet in a lift. Accelerating upward, the floor must push harder than your weight. Newton's second law gives the normal force minus mg equals ma, so the normal force is m times g plus a. **[PAUSE]** Accelerating downward, it's m times g minus a. Your weight never changes. Only the contact force does, and that's what the scales read.

## Scene 6 (s06) — The inclined plane: mg sin θ and mg cos θ

**2:34.8 – 3:40.2** (65.4 s) · 200 words · speech 60.8 s · 197 wpm · ends at 3:39.6

Now the classic: a block on a slope at angle θ. Gravity doesn't care about the slope, so the weight still points straight down. But the slope can only push perpendicular to itself. **[PAUSE]** So tilt your point of view to match the slope: one axis along it, one perpendicular to it. Now the weight is the only force that isn't lined up with an axis, so it's the one we split. **[PAUSE]** Here's the key geometry. Start with the slope flat: its perpendicular points straight down, right along the weight. Now tilt the slope by θ. Its perpendicular tilts by exactly the same θ. So the angle between the weight and the perpendicular is θ. **[PAUSE]** Read the triangle. The component touching θ, pressing into the slope, is mg cos θ. The component across from θ, pulling down the slope, is mg sin θ. Nothing moves into the slope, so the normal force equals mg cos θ. **[PAUSE]** Check the extremes. At zero degrees, sine is zero and cosine is one: no pull along the slope, and the full weight on the surface. At ninety degrees the slope is a wall: all of the weight acts along it, and none presses into it.

## Scene 7 (s07) — Friction on a slope: μs = tan θ

**3:40.2 – 4:25.9** (45.6 s) · 119 words · speech 42.4 s · 169 wpm · ends at 4:25.3

Add friction. Static friction only pushes as hard as it needs to, up to a limit: μs times the normal force. On the slope, it exactly matches the down-slope pull, mg sin θ. **[PAUSE]** Raise the angle. mg sin θ grows, while the maximum friction, μs mg cos θ, shrinks. They meet at the tipping point. **[PAUSE]** Set them equal: mg sin θ equals μs mg cos θ. The mass cancels, divide by cos θ, and μs equals tan θ. Measure the angle where a block just starts to slip, and you've measured μs. **[PAUSE]** Once it slides, friction drops to μd times the normal force, so the resultant force down the slope is mg sin θ minus μd mg cos θ.

## Scene 8 (s08) — A horizontal push on a slope

**4:25.9 – 5:00.4** (34.5 s) · 104 words · speech 31.9 s · 196 wpm · ends at 4:59.8

A trickier one. Hold a block on a smooth slope with a horizontal push F. Now F isn't lined up with either axis, so it gets split too. **[PAUSE]** The angle between F and the slope is also θ. So F cos θ pushes up along the slope, and F sin θ presses into it. **[PAUSE]** Along the slope, F cos θ balances mg sin θ, so F equals mg tan θ. Perpendicular to the slope, the normal force must balance both: mg cos θ plus F sin θ. The push adds to the normal force, so it can even end up bigger than the weight.

## Scene 9 (s09) — Tension in strings at angles

**5:00.4 – 5:56.5** (56.1 s) · 156 words · speech 52.7 s · 177 wpm · ends at 5:55.9

Tension is a pull along a string, directed away from the object. Hang a mass from a single string and the tension equals mg. **[PAUSE]** Now hang a lamp from two strings, each at angle α to the horizontal. Split each tension: T cos α sideways, and T sin α upward. The sideways parts cancel. The upward parts share the weight: two T sin α equals mg, so T equals mg over two sin α. **[PAUSE]** Flatten the strings and watch: as α shrinks, sin α heads toward zero, and the tension shoots up. That's why you can never pull a washing line perfectly straight. **[PAUSE]** With unequal angles, balance each direction separately: sideways, T one cos α one equals T two cos α two; upward, T one sin α one plus T two sin α two equals mg. Two equations, two unknown tensions. Or slide the three forces nose to tail: in equilibrium, they close into a triangle.

## Scene 10 (s10) — Tension over a pulley

**5:56.5 – 6:22.6** (26.1 s) · 75 words · speech 24.1 s · 187 wpm · ends at 6:22.0

Over a light, smooth pulley, tension keeps its size and only changes direction. Tie a block on a table to a hanging mass. The same tension pulls the block sideways and holds the hanging mass up. **[PAUSE]** For the hanging mass, mg minus T equals ma. For the block, T equals M a. The string links them, so they share the same acceleration. And while it accelerates, the tension is always less than the hanging weight.

## Scene 11 (s11) — Buoyancy: F_b = ρVg

**6:22.6 – 7:02.7** (40.2 s) · 126 words · speech 37.5 s · 202 wpm · ends at 7:02.1

Now put a block in a fluid. Fluid pressure grows with depth, so the bottom face is pushed up harder than the top face is pushed down. The pushes on the sides cancel. The difference is buoyancy. **[PAUSE]** The extra pressure across the block's height h is ρ g h, acting on the face area A. So the buoyant force is ρ g h A, and since h times A is the volume, that's ρ V g. Here ρ is the fluid's density, and V is the volume of fluid pushed aside. It's exactly the weight of the fluid that used to fill that space. **[PAUSE]** A floating object sinks until it pushes aside its own weight of fluid: ρ times the submerged volume times g equals mg.

## Scene 12 (s12) — Viscous drag and terminal speed

**7:02.7 – 7:43.0** (40.3 s) · 110 words · speech 37.4 s · 177 wpm · ends at 7:42.4

Move through a fluid, and it drags back. For a small sphere moving slowly through smooth, layered flow, Stokes' law gives the drag: six π η r v. It grows with speed. **[PAUSE]** Drop a ball bearing into oil. Weight pulls down; buoyancy and drag push up. As it speeds up, the drag grows, until the forces balance and the speed stops changing. That's terminal speed. **[PAUSE]** Write the balance: mg equals the buoyant force plus six π η r times the terminal speed. Replace each mass with density times four thirds π r cubed, and solve. The terminal speed is two r squared g, times the density difference, over nine η.

## Scene 13 (s13) — The recipe

**7:43.0 – 8:08.1** (25.1 s) · 62 words · speech 20.5 s · 182 wpm · ends at 8:04.9

Every contact force follows the same recipe. Isolate the object, and draw only the forces acting on it. Choose axes that match the surface. Split each force with its triangle: cos for the side touching the angle, sin for the side across. Then balance each direction. **[PAUSE]** So mg sin θ isn't a formula to memorise. It's just one side of a triangle.

---

**Total: 8:08.1 (488 s), 1391 words, 186 wpm while speaking.**

## Pronunciation overrides (sent to TTS only; subtitles keep the real spelling)

| Written | Spoken as |
|---|---|
| mg sin θ | m g sine theta |
| mg cos θ | m g cos theta |
| mg tan θ | m g tan theta |
| F cos θ | F cos theta |
| F sin θ | F sine theta |
| sin θ | sine theta |
| cos θ | cos theta |
| tan θ | tan theta |
| sin α | sine alpha |
| cos α | cos alpha |
| θ | theta |
| α | alpha |
| mg | m g |
| ma | m a |
| M a | big M a |
| μs | mew S |
| μd | mew D |
| ρ | rho |
| η | eta |
| π | pie |
