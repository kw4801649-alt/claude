# Contact Forces, Derived — Narration script

_Generated from `config/scenes.json` by `tools/make_script_doc.py`; edit the JSON, not this file._

- Voice: Phonon 31M `Hadley`, words-per-minute measured while talking (fallbacks: edge-tts `en-US-AriaNeural` at `+4%`, then Piper `en_US-lessac-medium`)
- `[PAUSE]` = 0.55 s of silence so the visuals can breathe; sentences are 0.18 s apart; speech is time-stretched to 0.99x speed (pitch kept; below 1 is slower).
- Scene lengths come from the audio (`audio/timings.json`); every animation is keyed to the words.

## Scene 1 (s01) — Where does mg sin θ come from?

**0:00.0 – 0:36.6** (36.6 s) · 92 words · speech 32.8 s · 168 wpm · ends at 0:35.9

Every force problem in IB Physics comes down to two moves: draw the forces, then split them into components. So where does mg sin θ actually come from? Most people memorise it, and then put the sine and the cosine on the wrong sides. We're going to build it instead, so you never have to guess. **[PAUSE]** In the next few minutes we'll derive every contact force you need: the normal force, friction, tension, buoyancy and viscous drag. No springs, no circles, no kinematics. Just forces, triangles, and the trigonometry that connects them.

## Scene 2 (s02) — The one tool: resolving a force

**0:36.6 – 1:33.6** (57.0 s) · 160 words · speech 53.2 s · 180 wpm · ends at 1:32.9

First, the one tool we'll use over and over. A force is an arrow with a size and a direction, and any arrow can be replaced by two perpendicular arrows that add up to it. Splitting doesn't change the force. It just lets us deal with one direction at a time. **[PAUSE]** Make the force F the hypotenuse of a right-angled triangle, at angle θ to the horizontal. Cosine is adjacent over hypotenuse, so the side touching the angle is F cos θ. Sine is opposite over hypotenuse, so the side across from the angle is F sin θ. **[PAUSE]** Now swing the angle and watch: as one component grows, the other shrinks, but together they always rebuild F. **[PAUSE]** The rule to remember: cos goes with the side touching θ, sin goes with the side across from it. Try it with numbers. A ten newton force at thirty degrees has eight point seven newtons along the horizontal, and exactly five newtons across.

## Scene 3 (s03) — Normal force on a flat surface

**1:33.6 – 2:17.4** (43.8 s) · 125 words · speech 40.0 s · 188 wpm · ends at 2:16.7

Start simple: a block resting on a table. Its weight, mg, pulls straight down. The table pushes back up with the normal force, normal meaning perpendicular to the surface. **[PAUSE]** Nothing accelerates, so the vertical forces balance, and the normal force equals mg. **[PAUSE]** But these two are not a Newton's third law pair. Both act on the block. A third law pair is the same kind of force acting on two different objects. The partner of the weight is the block pulling the Earth upward. **[PAUSE]** Push down on the block with your hand, and the table pushes back harder. The normal force isn't fixed: it responds to whatever it has to hold up. It only equals mg here because nothing else is pushing up or down.

## Scene 4 (s04) — Pulled or pushed at an angle

**2:17.4 – 3:02.5** (45.1 s) · 125 words · speech 42.2 s · 178 wpm · ends at 3:01.8

Now pull the block with a rope at angle θ above the horizontal. Split the pull: F cos θ drags the block sideways, and F sin θ lifts it a little. **[PAUSE]** Vertically, everything still balances: the normal force plus F sin θ equals mg. So the normal force is mg minus F sin θ. Pull harder and the surface pushes back less, because the rope is carrying part of the weight. Pull hard enough and the normal force reaches zero: the block lifts off. **[PAUSE]** Push down at the same angle instead, and the vertical part adds to the weight: the normal force becomes mg plus F sin θ. Since friction is proportional to the normal force, pulling up reduces friction, and pushing down increases it.

## Scene 5 (x1) — Worked example: pulling a crate

**3:02.5 – 3:45.7** (43.2 s) · 111 words · speech 40.1 s · 166 wpm · ends at 3:45.0

Let's put numbers on it. A ten kilogram crate is pulled along the floor by a rope, with thirty newtons at thirty degrees above the horizontal. The coefficient of friction is point two. **[PAUSE]** Vertically, the normal force is mg minus F sin θ: ninety eight point one, minus fifteen, is eighty three point one newtons. **[PAUSE]** So the friction is point two times eighty three point one: sixteen point six newtons. **[PAUSE]** The rope pulls forward with F cos θ: twenty six newtons. The resultant is twenty six minus sixteen point six: nine point four newtons, so the acceleration is nine point four divided by ten: point nine four metres per second squared.

## Scene 6 (s05) — Normal force in a lift

**3:45.7 – 4:26.1** (40.4 s) · 106 words · speech 37.5 s · 170 wpm · ends at 4:25.3

The normal force is also what you feel through your feet in a lift. Take up as positive. Accelerating upward, the floor must push harder than your weight. Newton's second law gives the normal force minus mg equals ma, so the normal force is m times g plus a. **[PAUSE]** Accelerating downward, it's m times g minus a. At constant speed there's no acceleration, and the floor pushes with exactly mg. Your weight never changes. Only the contact force does, and that's what the scales read. If the cable snapped, a would equal g, and the normal force would be zero. That's what feeling weightless really means.

## Scene 7 (x2) — Worked example: weighing yourself in a lift

**4:26.1 – 5:03.0** (36.9 s) · 95 words · speech 34.1 s · 167 wpm · ends at 5:02.3

A seventy kilogram person stands on a set of scales in a lift. **[PAUSE]** At constant speed, the scales read the weight: seventy times nine point eight one is six hundred and eighty seven newtons. **[PAUSE]** Accelerating upward at one point two metres per second squared, the normal force is seventy times, nine point eight one plus one point two: seven hundred and seventy one newtons. **[PAUSE]** Accelerating downward at the same rate, it's seventy times, nine point eight one minus one point two: six hundred and three newtons. The person's weight never changed. Only the reading did.

## Scene 8 (s06) — The inclined plane: mg sin θ and mg cos θ

**5:03.0 – 6:32.9** (89.9 s) · 255 words · speech 83.6 s · 183 wpm · ends at 6:32.2

Now the classic: a block on a slope at angle θ. Gravity doesn't care about the slope, so the weight still points straight down. But the slope can only push perpendicular to itself. **[PAUSE]** So tilt your point of view to match the slope: one axis along it, one perpendicular to it. That way the normal force lands exactly on one axis. Now the weight is the only force that isn't lined up with an axis, so it's the one we split. **[PAUSE]** Here's the key geometry. Start with the slope flat: its perpendicular points straight down, right along the weight. Now tilt the slope by θ. Its perpendicular tilts by exactly the same θ. So the angle between the weight and the perpendicular is θ. **[PAUSE]** Read the triangle. The component touching θ, pressing into the slope, is mg cos θ. The component across from θ, pulling down the slope, is mg sin θ. Nothing moves into the slope, so the normal force equals mg cos θ. **[PAUSE]** A quick example. A two kilogram block on a thirty degree slope: down the slope is nine point eight newtons, and into the slope, seventeen. **[PAUSE]** Check the extremes. At zero degrees, sine is zero and cosine is one: no pull along the slope, and the full weight on the surface. At ninety degrees the slope is a wall: all of the weight acts along it, and none presses into it. So if you ever forget which is sine, tilt the slope almost flat, and ask which part should be small.

## Scene 9 (s07) — Friction on a slope: μs = tan θ

**6:32.9 – 7:36.4** (63.5 s) · 150 words · speech 59.5 s · 151 wpm · ends at 7:35.7

Add friction. Push a heavy box gently and it doesn't move, because friction pushes back exactly as hard as you push. Push harder, and friction rises to match, up to a limit: μs times the normal force. On the slope, static friction exactly matches the down-slope pull, mg sin θ. **[PAUSE]** Raise the angle. mg sin θ grows, while the maximum friction, μs mg cos θ, shrinks. They meet at the tipping point. **[PAUSE]** Set them equal: mg sin θ equals μs mg cos θ. The mass cancels, divide by cos θ, and μs equals tan θ, because sine over cosine is tangent. Measure the angle where a block just starts to slip, and you've measured μs. **[PAUSE]** Once it slides, friction drops to μd times the normal force, because moving surfaces grip less than stationary ones. So the resultant force down the slope is mg sin θ minus μd mg cos θ.

## Scene 10 (x3) — Worked example: when does it slip, and then how fast?

**7:36.4 – 8:20.2** (43.8 s) · 115 words · speech 41.0 s · 168 wpm · ends at 8:19.5

Tilt a board until a block just starts to slide. It slips at twenty eight degrees. Then the coefficient of static friction is tan twenty eight degrees: point five three. **[PAUSE]** Now a five kilogram block on a thirty five degree slope, with a sliding friction coefficient of point three. Down the slope, mg sin θ is five times nine point eight one times point five seven four: twenty eight point one newtons. Friction, μd mg cos θ, is point three times five times nine point eight one times point eight one nine: twelve newtons. **[PAUSE]** The resultant is sixteen point one newtons down the slope, so the acceleration is three point two metres per second squared.

## Scene 11 (s08) — A horizontal push on a slope

**8:20.2 – 9:06.2** (46.0 s) · 129 words · speech 43.1 s · 179 wpm · ends at 9:05.5

Here's a trickier one. Hold a block on a smooth slope with a horizontal push F. Now F isn't lined up with either axis, so it gets split too. **[PAUSE]** The angle between F and the slope is also θ, because F is horizontal and the slope is tilted by θ from the horizontal. F is the hypotenuse, so F cos θ pushes up along the slope, and F sin θ presses into it. **[PAUSE]** Along the slope, F cos θ balances mg sin θ, so F equals mg tan θ, because sine over cosine is tangent. Perpendicular to the slope, the normal force must balance both: mg cos θ plus F sin θ. The push adds to the normal force, so it can even end up bigger than the weight.

## Scene 12 (x4) — Worked example: a horizontal push on a ramp

**9:06.2 – 9:40.6** (34.4 s) · 84 words · speech 31.9 s · 158 wpm · ends at 9:39.9

A ten kilogram block is held on a smooth ramp, tilted at twenty five degrees, by a horizontal push. **[PAUSE]** Along the slope, F cos θ equals mg sin θ, so F equals mg tan θ. That's ninety eight point one times zero point four six six: forty five point seven newtons. **[PAUSE]** Perpendicular to the slope, the normal force is mg cos θ plus F sin θ. That's eighty eight point nine, plus nineteen point three: one hundred and eight newtons. Bigger than the weight.

## Scene 13 (s09) — Tension in strings at angles

**9:40.6 – 10:51.8** (71.2 s) · 183 words · speech 67.0 s · 164 wpm · ends at 10:51.1

Tension is the pull in a string, directed along the string and away from the object. A string can only pull, never push. Hang a mass from a single string and the tension equals mg. **[PAUSE]** Now hang a lamp from two strings, each at angle α to the horizontal. Split each tension: T cos α sideways, and T sin α upward. The sideways parts cancel. The upward parts share the weight: two T sin α equals mg, so T equals mg over two sin α. **[PAUSE]** Flatten the strings and watch: as α shrinks, sin α heads toward zero, and the tension shoots up. At thirty degrees each string carries exactly mg, and at five degrees, nearly six times mg. That's why you can never pull a washing line perfectly straight. **[PAUSE]** With unequal angles, balance each direction separately: sideways, T one cos α one equals T two cos α two; upward, T one sin α one plus T two sin α two equals mg. Two equations, two unknown tensions. Or slide the three forces nose to tail: in equilibrium, they close into a triangle.

## Scene 14 (x5) — Worked example: a sign on two cables

**10:51.8 – 11:28.8** (37.0 s) · 99 words · speech 33.9 s · 175 wpm · ends at 11:28.1

A ten kilogram sign hangs from two cables, one at thirty degrees to the horizontal, the other at sixty. **[PAUSE]** Sideways, T one cos thirty equals T two cos sixty, so T two is one point seven three times T one. **[PAUSE]** Upward, T one sin thirty plus T two sin sixty equals mg. Put T two in, and the left side becomes two times T one. So T one is half of ninety eight point one: forty nine newtons. **[PAUSE]** And T two is one point seven three times that: eighty five newtons. The steeper cable carries more of the load.

## Scene 15 (s10) — Tension over a pulley

**11:28.8 – 12:22.4** (53.6 s) · 145 words · speech 50.2 s · 173 wpm · ends at 12:21.7

Over a light, smooth pulley, tension keeps its size and only changes direction. Tie a block on a table to a hanging mass. The same tension pulls the block sideways and holds the hanging mass up. **[PAUSE]** Call the hanging mass little m, and the block big M. For the hanging mass, mg minus T equals ma. For the block, T equals M a. The string links them, so they share the same acceleration. **[PAUSE]** Add the two equations and the tension cancels: mg equals big M plus little m, times a. So the acceleration equals mg over big M plus little m. Substitute that back into the block's equation, and T equals big M times little m times g, over big M plus little m. And while it accelerates, the tension is always less than the hanging weight, because the block has to be accelerated too.

## Scene 16 (x6) — Worked example: numbers on a pulley

**12:22.4 – 13:02.0** (39.6 s) · 101 words · speech 36.6 s · 166 wpm · ends at 13:01.3

Take a three kilogram block on a smooth table, tied over a pulley to a two kilogram hanging mass. **[PAUSE]** The acceleration is the hanging weight divided by the total mass: nineteen point six two, over five. That's three point nine two metres per second squared. **[PAUSE]** The tension is the block's mass times the acceleration: three times three point nine two, which is eleven point eight newtons. **[PAUSE]** Check the hanging mass. Its weight, nineteen point six, minus the tension, eleven point eight, leaves seven point eight five newtons, and two times three point nine two is seven point eight five. It works.

## Scene 17 (s11) — Buoyancy: F_b = ρVg

**13:02.0 – 13:56.0** (53.9 s) · 159 words · speech 50.5 s · 189 wpm · ends at 13:55.2

Now put a block in a fluid. Fluid pressure grows with depth, so the bottom face is pushed up harder than the top face is pushed down. The pushes on the sides cancel. The difference is buoyancy. **[PAUSE]** The extra pressure across the block's height h is ρ g h. That's the weight of a column of fluid, per unit area. It acts on the face area A, so the buoyant force is ρ g h A, and since h times A is the volume, that's ρ V g. Here ρ is the fluid's density, not the block's, and V is the volume of fluid pushed aside. Picture that space filled with fluid instead. It would just sit there, so the fluid around it must be pushing up with exactly the weight of the fluid that fills it. **[PAUSE]** A floating object sinks until it pushes aside its own weight of fluid: ρ times the submerged volume times g equals mg.

## Scene 18 (x7) — Worked example: will it float?

**13:56.0 – 14:33.9** (37.9 s) · 103 words · speech 34.8 s · 177 wpm · ends at 14:33.2

A wooden block has a mass of point eight kilograms and a volume of one litre: one thousandth of a cubic metre. Will it float in water? **[PAUSE]** Fully submerged, the buoyant force is rho V g: a thousand, times point zero zero one, times nine point eight one. That's nine point eight one newtons. The weight is only seven point eight five newtons. So the buoyant force wins, and the block rises. **[PAUSE]** It floats when the buoyant force equals the weight. That needs a submerged volume of point eight kilograms divided by a thousand. So eighty percent of the block sits under water.

## Scene 19 (s12) — Viscous drag and terminal speed

**14:33.9 – 15:43.3** (69.4 s) · 180 words · speech 64.7 s · 167 wpm · ends at 15:42.6

Move through a fluid, and it drags back. For a small sphere moving slowly through smooth, layered flow, Stokes' law gives the drag: six π η r v. Here η is the viscosity, how thick and sticky the fluid is, r is the radius, and v is the speed. It grows with speed. **[PAUSE]** Drop a ball bearing into oil. Weight pulls down; buoyancy and drag push up. As it speeds up, the drag grows, until the forces balance and the speed stops changing. That's terminal speed. **[PAUSE]** Write the balance: mg equals the buoyant force plus six π η r times the terminal speed. Replace each mass with density times four thirds π r cubed, and solve. Move the buoyant force across, cancel π and one r, and divide by six η. Four thirds divided by six is two ninths. The terminal speed is two r squared g, times the density difference, over nine η. **[PAUSE]** Read it like a recipe. Double the radius and the ball falls four times faster. Use oil twice as thick and it falls half as fast.

## Scene 20 (x8) — Worked example: a steel ball in oil

**15:43.3 – 16:27.4** (44.1 s) · 108 words · speech 41.2 s · 157 wpm · ends at 16:26.7

Drop a steel ball bearing, two millimeters in radius, into oil. The steel's density is seven thousand eight hundred kilograms per cubic metre. The oil's is nine hundred, and its viscosity is point nine pascal seconds. **[PAUSE]** The terminal speed is two r squared g, times the density difference, over nine η. The radius squared is four times ten to the minus six. The density difference is six thousand nine hundred. **[PAUSE]** So two, times four times ten to the minus six, times nine point eight one, times six thousand nine hundred, divided by nine times point nine: point zero six seven metres per second. About seven centimetres per second.

## Scene 21 (s13) — The recipe

**16:27.4 – 17:06.8** (39.4 s) · 94 words · speech 33.5 s · 169 wpm · ends at 17:03.6

Every contact force follows the same recipe. Isolate the object, and draw only the forces acting on it. Choose axes that match the surface. Split each force with its triangle: cos for the side touching the angle, sin for the side across. Then balance each direction. **[PAUSE]** Three slips to avoid. Never draw mass times acceleration as a force. For buoyancy, use the fluid's density, not the block's. And always ask which side of the triangle touches the angle. **[PAUSE]** So mg sin θ isn't a formula to memorise. It's just one side of a triangle.

---

**Total: 17:06.8 (1027 s), 2719 words, 171 wpm while speaking.**

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
| metres | meters |
| metre | meter |
| millimetres | millimeters |
| centimetres | centimeters |
| litre | liter |
| litres | liters |
