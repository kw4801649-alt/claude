# Contact Forces, Derived (IB Physics SL · A.2)

An 8-minute animated derivation of every contact force in the IB Physics SL syllabus (first assessment 2025).
It shows where each term on a free-body diagram comes from, with the trigonometry made visible.
It excludes elastic forces, circular motion and kinematics.

**Covered:**
- resolving a force
- the normal force: on a flat surface, with angled pulls and pushes, and in a lift
- the inclined plane: **mg sin θ** and **mg cos θ**, with a moving proof that the angle between mg and the slope normal is θ
- friction on a slope and the slip angle **μs = tan θ**, then sliding friction
- a horizontal push on a slope (giving F_N = mg / cos θ)
- tension: a single string, two strings at angles (T = mg / 2 sin α) with the closed triangle of forces, and a pulley
- buoyancy derived from the pressure difference (F_b = ρVg), and floating
- Stokes' drag and terminal speed (v_t = 2r²g(ρs − ρf) / 9η)

**Look:** one long sheet of graph paper. The camera glides from diagram to diagram, and once rotates the paper
so the slope lies level.
- **Vectors** are pen-drawn with a fixed colour code: weight orange, normal teal, friction raspberry, tension green,
  applied force blue, buoyancy sky-blue, drag violet.
- **Motion** carries the explanations: angles move, blocks slip, strings flatten and lifts accelerate.
- **Equations** (KaTeX) write themselves exactly as they are spoken.
- **No interface chrome.** The ending zooms out over the finished worksheet.

The background research is in `docs/00_research.md`, including the syllabus list, every scenario and the sources.

## Pipeline

| Step | Tool | Output |
|---|---|---|
| Script | `config/scenes.json` | narration, pronunciations (θ → "theta", μs → "mew S"…) |
| Voice | **Phonon 31M** (offline, Apache 2.0) → edge-tts → Piper | `audio/s01.wav`…`s13.wav` + `audio/timings.json` (sentence-level timeline) |
| Subtitles | `tools/build_srt.py` | `subtitles/contact_forces.srt` |
| Scene | **SVG + KaTeX** in one HTML file | `scene/index.html`, a pure function of time `t` |
| Frames | Puppeteer + headless Chrome | `frames/f_00000.png`… (≈14,600 frames) |
| Video | FFmpeg | `output/contact_forces_derived.mp4` |

## Versions

| Tool | Version |
|---|---|
| Node.js | ≥ 20 (tested 22.23) |
| puppeteer | 25.18.1 (Chrome headless shell 157.0.8103.78) |
| katex | 0.19.1 |
| @fontsource/caveat, @fontsource/fraunces | 5.3.0 |
| Python | ≥ 3.9 (tested 3.13) |
| ptts / edge-tts / piper-tts | 0.7.1 / 7.3.1 / 1.8.0 |
| FFmpeg | ≥ 6.0 with libx264 |

All versions are pinned in `package.json`, `package-lock.json` and `requirements.txt`.

## Run everything

```bash
cd ib-contact-forces
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
npm ci && npx puppeteer browsers install chrome-headless-shell
python tools/tts.py                       # narration + audio/timings.json (≈1–2 min on CPU)
python tools/build_srt.py                 # subtitles
python tools/make_script_doc.py && python tools/make_storyboard.py   # docs (optional)
npm run render:test                       # 39 review stills -> renders/test/ (optional)
node render/capture.mjs --workers 3       # all frames (≈10 min on 4 cores: SVG renders fast)
bash tools/assemble.sh                    # output/contact_forces_derived.mp4 (soft subtitles)
BURN_SUBS=1 bash tools/assemble.sh        # …or with subtitles burned in
```

`npm run preview` serves `http://127.0.0.1:8080/scene/index.html?preview=1`, which gives a scrubber with narration playback.

**Expected result:** **8:08** (488.1 s), 14,643 frames, H.264 1920×1080 30 fps, AAC 48 kHz at about −16 LUFS,
with an English subtitle track.

## How the timing works

`tools/tts.py` records when every sentence is spoken. In `scene/index.html`, each beat is written as
`cue("s06", "Read the triangle")`: the moment that phrase is spoken.

- **Changing the script or voice:** re-run the TTS and the animation re-syncs.
- **Rewording a cued phrase:** the page names the missing cue.

Frames are deterministic: no clock, no randomness, and they render in any order.

## Editing

| What | Where |
|---|---|
| Narration text | `config/scenes.json` |
| Diagrams | one `section("sNN", …)` block per scene in `scene/index.html` |
| Equation lines | `eqs()` lists of `{tex, t: cue(...)}` |
| Camera path | the `CAM` keys near the end of `scene/index.html` |
