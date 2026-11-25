# Reading Motion and Momentum Graphs (IB Physics SL · A.1 and A.2)

An 11-minute animated guide to every graph in IB Physics SL kinematics and forces & momentum, built around two moves:
**take the gradient, or take the area**. It excludes elastic forces, circular motion, and work/energy graphs.

**Covered:**
- displacement–, velocity– and acceleration–time graphs, and how each is the gradient or area of its neighbour
- constant velocity and constant acceleration, with the equations of motion derived from the v–t graph
  (v = u + at, s = ut + ½at², s = ½(u + v)t, v² = u² + 2as)
- average velocity (chord) turning into instantaneous velocity (tangent), and the "two points on the tangent" mistake
- a ball thrown up: signs, displacement versus distance, zero velocity at the top but not zero acceleration
- non-uniform acceleration and terminal velocity (curved v–t, counting squares, why the equations stop working)
- projectile motion as two independent sets of graphs
- momentum–time graphs (gradient = force) and force–time graphs (area = impulse = change in momentum), with the
  worked examples 30 N s and −4.5 N s / −450 N
- F → p → v chained together, contact time (airbags), rebounds, and collisions seen as mirror-image force graphs

**Look:** one long blueprint-style sheet. The camera glides and swoops from graph to graph.
- **Colour means quantity:** displacement cyan, velocity amber, acceleration pink, force coral, momentum lime.
  A shaded area takes the colour of what it produces (the area under v–t is cyan: displacement).
- **Every curve is drawn live** while a cart, ball, projectile, egg or collision plays out beside it.
- **Tangents, chords, guides and shaded areas** show what the gradient and area mean at that moment.
- **Equations** (KaTeX) write themselves exactly as they are spoken. No interface bars, chips or cards.

The research (syllabus content, worked examples, misconceptions, sources) is in `docs/00_research.md`.

## Pipeline

| Step | Tool | Output |
|---|---|---|
| Script | `config/scenes.json` | narration, pronunciations |
| Voice | **Phonon 31M** (offline, Apache 2.0) → edge-tts → Piper | `audio/s01.wav`…`s15.wav` + `audio/timings.json` |
| Subtitles | `tools/build_srt.py` | `subtitles/motion_graphs.srt` |
| Scene | **SVG + KaTeX** in one HTML file | `scene/index.html`, a pure function of time `t` |
| Frames | Puppeteer + headless Chrome | `frames/f_00000.png`… (≈19,400 frames) |
| Video | FFmpeg | `output/motion_graphs_decoded.mp4` |

## Versions

| Tool | Version |
|---|---|
| Node.js | ≥ 20 (tested 22.23) |
| puppeteer | 25.18.1 (Chrome headless shell 157.0.8103.78) |
| katex | 0.19.1 |
| @fontsource/caveat | 5.3.0 |
| Python | ≥ 3.9 (tested 3.13) |
| ptts / edge-tts / piper-tts | 0.7.1 / 7.3.1 / 1.8.0 |
| FFmpeg | ≥ 6.0 with libx264 |

All versions are pinned in `package.json`, `package-lock.json` and `requirements.txt`.

## Run everything

```bash
cd ib-graphs
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
npm ci && npx puppeteer browsers install chrome-headless-shell
python tools/tts.py                       # narration + audio/timings.json (≈3 min on CPU)
python tools/build_srt.py                 # subtitles
python tools/make_script_doc.py && python tools/make_storyboard.py   # docs (optional)
npm run render:test                       # review stills -> renders/test/ (optional)
node render/capture.mjs --workers 3       # all frames (≈15 min on 4 cores)
bash tools/assemble.sh                    # output/motion_graphs_decoded.mp4 (soft subtitles)
BURN_SUBS=1 bash tools/assemble.sh        # …or with subtitles burned in
```

`npm run preview` serves `http://127.0.0.1:8080/scene/index.html?preview=1`, which gives a scrubber with narration playback.

**Expected result:** about **10:45** (645.0 s), 19,349 frames, H.264 1920×1080 30 fps, AAC 48 kHz at about −16 LUFS,
with an English subtitle track.

## Pace and pronunciation

- **Pace:** about 160 words per minute overall. It is set by `audio.tempo` (0.99), `audio.pause_s` (0.55 s per `[PAUSE]`) and
  `tts.phonon.sentence_silence` (0.18 s). Lower `tempo` to slow it down, then re-run `python tools/tts.py`.
- **Pronunciation:** the narration uses words ("initial velocity", "newton seconds") instead of bare symbols, because the voice
  garbles single letters. The equations appear on screen instead. `pronunciations` in `config/scenes.json` covers the rest.

## How the timing works

`tools/tts.py` records when every sentence is spoken. In `scene/index.html`, each beat is written as
`cue("s05", "Add them")`: the moment that phrase is spoken.

- **Changing the script or voice:** re-run the TTS and the animation re-syncs.
- **Rewording a cued phrase:** the page names the missing cue.

Frames are deterministic: no clock, no randomness, and they render in any order.

## Editing

| What | Where |
|---|---|
| Narration text | `config/scenes.json` |
| One scene | one `section("sNN", …)` block in `scene/index.html` |
| Graph toolkit | `Graph(...)` (plots, bands, tangents, labels), `demo(...)` (cart), `ladder(...)` near the top of the script |
| Equation lines | `eqs()` lists of `{tex, t: cue(...)}` |
| Camera path | the `CAM` keys at the end of the scene script |
