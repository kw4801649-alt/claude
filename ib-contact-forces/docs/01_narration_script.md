# Contact Forces, Derived — Narration script

_Generated from `config/scenes.json` by `tools/make_script_doc.py`; edit the JSON, not this file._

- Voice: Phonon 31M `Hadley`, words-per-minute measured while talking (fallbacks: edge-tts `en-US-AriaNeural` at `+4%`, then Piper `en_US-lessac-medium`)
- `[PAUSE]` = 0.8 s of silence so the visuals can breathe; sentences are 0.28 s apart; speech is time-stretched to 0.9x speed (pitch kept; below 1 is slower).
- Scene lengths come from the audio (`audio/timings.json`); every animation is keyed to the words.

## Scene 1 (s01) — Where does mg sin θ come from?

**0:00.0 – 0:40.8** (40.8 s) · 92 words · speech 36.1 s · 153 wpm · ends at 0:40.0

Every force problem in IB Physics comes down to two moves: draw the forces, then split them into components. So where does mg sin θ actually come from? Most people memorise it, and then put the sine and the cosine on the wrong sides. We're going to build it instead, so you never have to guess. **[PAUSE]** In the next few minutes we'll derive every contact force you need: the normal force, friction, tension, buoyancy and viscous drag. No springs, no circles, no kinematics. Just forces, triangles, and the trigonometry that connects them.

## Scene 2 (s02) — The one tool: resolving a force

**0:40.8 – 1:45.0** (64.1 s) · 160 words · speech 58.5 s · 164 wpm · ends at 1:44.2

First, the one tool we'll use over and over. A force is an arrow with a size and a direction, and any arrow can be replaced by two perpendicular arrows that add up to it. Splitting doesn't change the force. It just lets us deal with one direction at a time. **[PAUSE]** Make the force F the hypotenuse of a right-angled triangle, at angle θ to the horizontal. Cosine is adjacent over hypotenuse, so the side touching the angle is F cos θ. Sine is opposite over hypotenuse, so the side across from the angle is F sin θ. **[PAUSE]** Now swing the angle and watch: as one component grows, the other shrinks, but together they always rebuild F. **[PAUSE]** The rule to remember: cos goes with the side touching θ, sin goes with the side across from it. Try it with numbers. A ten newton force at thirty degrees has eight point seven newtons along the horizontal, and exactly five newtons across.

## Scene 3 (s03) — Normal force on a flat surface

**1:45.0 – 2:34.6** (49.6 s) · 125 words · speech 44.0 s · 170 wpm · ends at 2:33.7

Start simple: a block resting on a table. Its weight, mg, pulls straight down. The table pushes back up with the normal force, normal meaning perpendicular to the surface. **[PAUSE]** Nothing accelerates, so the vertical forces balance, and the normal force equals mg. **[PAUSE]** But these two are not a Newton's third law pair. Both act on the block. A third law pair is the same kind of force acting on two different objects. The partner of the weight is the block pulling the Earth upward. **[PAUSE]** Push down on the block with your hand, and the table pushes back harder. The normal force isn't fixed: it responds to whatever it has to hold up. It only equals mg here because nothing else is pushing up or down.

## Scene 4 (s04) — Pulled or pushed at an angle

**2:34.6 – 3:25.1** (50.6 s) · 125 words · speech 46.4 s · 162 wpm · ends at 3:24.3

Now pull the block with a rope at angle θ above the horizontal. Split the pull: F cos θ drags the block sideways, and F sin θ lifts it a little. **[PAUSE]** Vertically, everything still balances: the normal force plus F sin θ equals mg. So the normal force is mg minus F sin θ. Pull harder and the surface pushes back less, because the rope is carrying part of the weight. Pull hard enough and the normal force reaches zero: the block lifts off. **[PAUSE]** Push down at the same angle instead, and the vertical part adds to the weight: the normal force becomes mg plus F sin θ. Since friction is proportional to the normal force, pulling up reduces friction, and pushing down increases it.

## Scene 5 (s05) — Normal force in a lift

**3:25.1 – 4:10.7** (45.6 s) · 106 words · speech 41.2 s · 154 wpm · ends at 4:09.9

The normal force is also what you feel through your feet in a lift. Take up as positive. Accelerating upward, the floor must push harder than your weight. Newton's second law gives the normal force minus mg equals ma, so the normal force is m times g plus a. **[PAUSE]** Accelerating downward, it's m times g minus a. At constant speed there's no acceleration, and the floor pushes with exactly mg. Your weight never changes. Only the contact force does, and that's what the scales read. If the cable snapped, a would equal g, and the normal force would be zero. That's what feeling weightless really means.

## Scene 6 (s06) — The inclined plane: mg sin θ and mg cos θ

**4:10.7 – 5:52.3** (101.6 s) · 255 words · speech 92.0 s · 166 wpm · ends at 5:51.5

Now the classic: a block on a slope at angle θ. Gravity doesn't care about the slope, so the weight still points straight down. But the slope can only push perpendicular to itself. **[PAUSE]** So tilt your point of view to match the slope: one axis along it, one perpendicular to it. That way the normal force lands exactly on one axis. Now the weight is the only force that isn't lined up with an axis, so it's the one we split. **[PAUSE]** Here's the key geometry. Start with the slope flat: its perpendicular points straight down, right along the weight. Now tilt the slope by θ. Its perpendicular tilts by exactly the same θ. So the angle between the weight and the perpendicular is θ. **[PAUSE]** Read the triangle. The component touching θ, pressing into the slope, is mg cos θ. The component across from θ, pulling down the slope, is mg sin θ. Nothing moves into the slope, so the normal force equals mg cos θ. **[PAUSE]** A quick example. A two kilogram block on a thirty degree slope: down the slope is nine point eight newtons, and into the slope, seventeen. **[PAUSE]** Check the extremes. At zero degrees, sine is zero and cosine is one: no pull along the slope, and the full weight on the surface. At ninety degrees the slope is a wall: all of the weight acts along it, and none presses into it. So if you ever forget which is sine, tilt the slope almost flat, and ask which part should be small.

## Scene 7 (s07) — Friction on a slope: μs = tan θ

**5:52.3 – 7:03.7** (71.4 s) · 150 words · speech 65.5 s · 137 wpm · ends at 7:02.9

Add friction. Push a heavy box gently and it doesn't move, because friction pushes back exactly as hard as you push. Push harder, and friction rises to match, up to a limit: μs times the normal force. On the slope, static friction exactly matches the down-slope pull, mg sin θ. **[PAUSE]** Raise the angle. mg sin θ grows, while the maximum friction, μs mg cos θ, shrinks. They meet at the tipping point. **[PAUSE]** Set them equal: mg sin θ equals μs mg cos θ. The mass cancels, divide by cos θ, and μs equals tan θ, because sine over cosine is tangent. Measure the angle where a block just starts to slip, and you've measured μs. **[PAUSE]** Once it slides, friction drops to μd times the normal force, because moving surfaces grip less than stationary ones. So the resultant force down the slope is mg sin θ minus μd mg cos θ.

## Scene 8 (s08) — A horizontal push on a slope

**7:03.7 – 7:55.3** (51.6 s) · 129 words · speech 47.4 s · 163 wpm · ends at 7:54.5

Here's a trickier one. Hold a block on a smooth slope with a horizontal push F. Now F isn't lined up with either axis, so it gets split too. **[PAUSE]** The angle between F and the slope is also θ, because F is horizontal and the slope is tilted by θ from the horizontal. F is the hypotenuse, so F cos θ pushes up along the slope, and F sin θ presses into it. **[PAUSE]** Along the slope, F cos θ balances mg sin θ, so F equals mg tan θ, because sine over cosine is tangent. Perpendicular to the slope, the normal force must balance both: mg cos θ plus F sin θ. The push adds to the normal force, so it can even end up bigger than the weight.

## Scene 9 (s09) — Tension in strings at angles

**7:55.3 – 9:15.2** (79.9 s) · 183 words · speech 73.7 s · 149 wpm · ends at 9:14.4

Tension is the pull in a string, directed along the string and away from the object. A string can only pull, never push. Hang a mass from a single string and the tension equals mg. **[PAUSE]** Now hang a lamp from two strings, each at angle α to the horizontal. Split each tension: T cos α sideways, and T sin α upward. The sideways parts cancel. The upward parts share the weight: two T sin α equals mg, so T equals mg over two sin α. **[PAUSE]** Flatten the strings and watch: as α shrinks, sin α heads toward zero, and the tension shoots up. At thirty degrees each string carries exactly mg, and at five degrees, nearly six times mg. That's why you can never pull a washing line perfectly straight. **[PAUSE]** With unequal angles, balance each direction separately: sideways, T one cos α one equals T two cos α two; upward, T one sin α one plus T two sin α two equals mg. Two equations, two unknown tensions. Or slide the three forces nose to tail: in equilibrium, they close into a triangle.

## Scene 10 (s10) — Tension over a pulley

**9:15.2 – 10:15.5** (60.3 s) · 145 words · speech 55.2 s · 158 wpm · ends at 10:14.7

Over a light, smooth pulley, tension keeps its size and only changes direction. Tie a block on a table to a hanging mass. The same tension pulls the block sideways and holds the hanging mass up. **[PAUSE]** Call the hanging mass little m, and the block big M. For the hanging mass, mg minus T equals ma. For the block, T equals M a. The string links them, so they share the same acceleration. **[PAUSE]** Add the two equations and the tension cancels: mg equals big M plus little m, times a. So the acceleration equals mg over big M plus little m. Substitute that back into the block's equation, and T equals big M times little m times g, over big M plus little m. And while it accelerates, the tension is always less than the hanging weight, because the block has to be accelerated too.

## Scene 11 (s11) — Buoyancy: F_b = ρVg

**10:15.5 – 11:16.1** (60.6 s) · 159 words · speech 55.5 s · 172 wpm · ends at 11:15.3

Now put a block in a fluid. Fluid pressure grows with depth, so the bottom face is pushed up harder than the top face is pushed down. The pushes on the sides cancel. The difference is buoyancy. **[PAUSE]** The extra pressure across the block's height h is ρ g h. That's the weight of a column of fluid, per unit area. It acts on the face area A, so the buoyant force is ρ g h A, and since h times A is the volume, that's ρ V g. Here ρ is the fluid's density, not the block's, and V is the volume of fluid pushed aside. Picture that space filled with fluid instead. It would just sit there, so the fluid around it must be pushing up with exactly the weight of the fluid that fills it. **[PAUSE]** A floating object sinks until it pushes aside its own weight of fluid: ρ times the submerged volume times g equals mg.

## Scene 12 (s12) — Viscous drag and terminal speed

**11:16.1 – 12:34.5** (78.3 s) · 180 words · speech 71.2 s · 152 wpm · ends at 12:33.7

Move through a fluid, and it drags back. For a small sphere moving slowly through smooth, layered flow, Stokes' law gives the drag: six π η r v. Here η is the viscosity, how thick and sticky the fluid is, r is the radius, and v is the speed. It grows with speed. **[PAUSE]** Drop a ball bearing into oil. Weight pulls down; buoyancy and drag push up. As it speeds up, the drag grows, until the forces balance and the speed stops changing. That's terminal speed. **[PAUSE]** Write the balance: mg equals the buoyant force plus six π η r times the terminal speed. Replace each mass with density times four thirds π r cubed, and solve. Move the buoyant force across, cancel π and one r, and divide by six η. Four thirds divided by six is two ninths. The terminal speed is two r squared g, times the density difference, over nine η. **[PAUSE]** Read it like a recipe. Double the radius and the ball falls four times faster. Use oil twice as thick and it falls half as fast.

## Scene 13 (s13) — The recipe

**12:34.5 – 13:18.8** (44.3 s) · 94 words · speech 36.8 s · 153 wpm · ends at 13:15.6

Every contact force follows the same recipe. Isolate the object, and draw only the forces acting on it. Choose axes that match the surface. Split each force with its triangle: cos for the side touching the angle, sin for the side across. Then balance each direction. **[PAUSE]** Three slips to avoid. Never draw mass times acceleration as a force. For buoyancy, use the fluid's density, not the block's. And always ask which side of the triangle touches the angle. **[PAUSE]** So mg sin θ isn't a formula to memorise. It's just one side of a triangle.

---

**Total: 13:18.8 (799 s), 1903 words, 158 wpm while speaking.**

## Pronunciation overrides (sent to TTS only; subtitles keep the real spelling)

| Written | Spoken as |
|---|---|
| μs mg cos θ | mew S, em gee cos theta |
| μd mg cos θ | mew D, em gee cos theta |
| mg sin θ | em gee sine theta |
| mg cos θ | em gee cos theta |
| mg tan θ | em gee tan theta |
| F cos θ | F cos theta |
| F sin θ | F sine theta |
| sin θ | sine theta |
| cos θ | cos theta |
| tan θ | tan theta |
| sin α | sine alpha |
| cos α | cos alpha |
| π η r v | pie, eta, r, v |
| π η r | pie, eta, r, |
| nine η | nine, eta |
| area A | area, capital A |
| θ | theta |
| α | alpha |
| η | eta |
| ρ | rho |
| π | pie |
| μs | mew S |
| μd | mew D |
| mg | em gee |
| ma | little m a |
| M a | big M a |
| cos | co-sine |
| sin | sine |
| T | tee |
| g | gee |
| Stokes' | Stokes |
