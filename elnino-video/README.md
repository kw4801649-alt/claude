# How El Niño Forms: “The Pacific, seen in heat”

A ~5-minute animated explainer (1920×1080, 16:9, 30 fps), built only with free and open-source tools.

It uses one continuous camera move over a dark, infrared dot-matrix planet. There's no interface chrome: no
title bars, chapter chips, label pills or definition cards.
- **Temperature** is colour.
- **Winds and currents** are streaks of light.
- **The thermocline** is a glowing net.
- **Words** live inside the physics: *trade winds* blows away, *warm pool* drops onto the water,
  *upwelling* rises from the deep, *Kelvin wave* rides the wave, *drought* crumbles and *floods* drips.

Every animation is triggered by the moment its words are spoken.

| Step | Tool | Output |
|---|---|---|
| Script | `config/scenes.json` | narration, pronunciations, voice settings |
| Voice | **Phonon 31M** (primary, offline) → edge-tts → Piper | `audio/s01.wav` … `s10.wav` + **`audio/timings.json`** (the timeline) |
| Subtitles | `tools/build_srt.py` | `subtitles/elnino.srt`, sentence-accurate |
| 3D | **Three.js** (one HTML file) | `scene/index.html`, a pure function of time `t` |
| Frames | **Puppeteer + headless Chrome** | `frames/f_00000.png` … |
| Video | **FFmpeg** | `output/how_el_nino_forms.mp4` |

## Assumptions

1. **Voice:** Phonon 31M (`gradium/phonon-31m-en`, Apache 2.0), voice **Hadley**.
   - It speaks one sentence at a time, with 0.12 s between sentences and 0.45 s per `[PAUSE]`.
   - The speech is sped up 1.08× with the pitch kept (`audio.tempo`). That's about **180 words per minute** while talking.
   - To change any of this, edit `tts.phonon` or `audio` in `config/scenes.json`.
2. **Timing comes from the narration.** Scene lengths are the speech plus a short tail (`"duration": "auto"`), rounded to whole frames.
   - The scene reads `audio/timings.json` and fires each beat on a spoken phrase.
   - So **run the TTS before rendering.**
3. **Schematic science.** Temperatures, thermocline depth, winds and waves are smooth illustrative fields, not
   observations. The ENSO heartbeat line in scene 9 is schematic, not real index data.
   The global impacts are typical El Niño tendencies, and the narration says so.
4. **Subtitles** are a soft, switchable track by default. Burned-in captions would bring the bottom bar back.
   Run `BURN_SUBS=1 bash tools/assemble.sh` if you need them burned in.
5. **Music:** none.
6. **Platform:** Linux and macOS. On Windows, use WSL for the shell steps.

## Tool versions

| Tool | Version | Notes |
|---|---|---|
| Node.js | ≥ 20 (tested 22.23) | |
| puppeteer | **25.18.1** (pinned) | pins chrome-headless-shell **157.0.8103.78** |
| three | **0.187.0** (pinned) | incl. `UnrealBloomPass`; loaded from `node_modules` |
| @fontsource/fraunces, @fontsource/jetbrains-mono, @fontsource/inter | **5.3.0** (pinned) | fonts loaded locally |
| Python | ≥ 3.9 (tested 3.13.18) | |
| ptts (Phonon runtime) | **0.7.1** (pinned) | Phonon 31M on CPU; only needs numpy; model (~65 MB) downloads on first run |
| edge-tts | **7.3.1** (pinned) | fallback 1 (needs internet) |
| piper-tts | **1.8.0** (pinned) | fallback 2 (offline) |
| FFmpeg | ≥ 6.0 (tested 6.1.1) | with libx264 (libass only if you burn subtitles) |

## Folder layout

```
elnino-video/
├── config/scenes.json            narration (single source of truth), voices, pacing
├── docs/01_narration_script.md   deliverable 1 (generated: tools/make_script_doc.py)
├── docs/02_storyboard.md         deliverable 2 (generated: tools/make_storyboard.py)
├── tools/tts.py                  deliverable 3: Phonon -> edge-tts -> Piper; writes audio/timings.json
├── scene/index.html              deliverable 4: the whole film as a function of t
├── render/capture.mjs            deliverable 5a: deterministic frame capture
├── render/serve.mjs              local static server (preview + capture)
├── tools/assemble.sh             deliverable 5b: FFmpeg mux
├── subtitles/elnino.srt          deliverable 6 (generated: tools/build_srt.py)
├── samples/                      22 s voice samples for choosing a voice
└── (generated) audio/ frames/ renders/ output/ voices/
```

## Step by step

All commands run from `elnino-video/`.

**0. System tools**

```bash
sudo apt-get install -y ffmpeg python3 python3-venv     # macOS: brew install ffmpeg python node
# Node.js 20+ from https://nodejs.org
```

**1. Python and Node dependencies**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt                          # ptts, edge-tts, piper-tts
npm ci
npx puppeteer browsers install chrome-headless-shell     # the Chrome build pinned by puppeteer
```

**2. Narration, which also defines the timeline**

```bash
python tools/tts.py                   # Phonon (falls back to edge-tts, then Piper); about 1-2 min on CPU
python tools/tts.py --engine edge     # or force an engine
```

It prints each scene's length and words per minute, and writes `audio/timings.json`.

**3. Subtitles and documents (optional)**

```bash
python tools/build_srt.py && python tools/make_script_doc.py && python tools/make_storyboard.py
```

**4. Preview and test stills (optional)**

```bash
npm run preview          # open http://127.0.0.1:8080/scene/index.html?preview=1 (scrub + narration)
npm run render:test      # 30 stills (15/50/85% of each scene) -> renders/test/
```

**5. Render every frame**

```bash
node render/capture.mjs --workers 3   # ≈ 9,200 PNGs (≈ 2.5 GB)
```

With software WebGL, a 4-core machine renders about 4 frames per second with 3 workers, so this takes
about **40 minutes**. Use `--resume` to continue an interrupted render. Use `--start/--end` to split the
work across machines. `--gpu` is faster, but pixels may then differ between drivers.

**6. Assemble**

```bash
bash tools/assemble.sh                # soft subtitles
BURN_SUBS=1 bash tools/assemble.sh    # burned-in subtitles
```

The underlying FFmpeg command (the script fills in the scene list and the length from `audio/timings.json`):

```bash
ffmpeg -y -framerate 30 -start_number 0 -i frames/f_%05d.png \
  -i audio/s01.wav -i audio/s02.wav -i audio/s03.wav -i audio/s04.wav -i audio/s05.wav \
  -i audio/s06.wav -i audio/s07.wav -i audio/s08.wav -i audio/s09.wav -i audio/s10.wav \
  -i subtitles/elnino.srt \
  -filter_complex "[1:a][2:a][3:a][4:a][5:a][6:a][7:a][8:a][9:a][10:a]concat=n=10:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout];[0:v]format=yuv420p[vout]" \
  -map "[vout]" -map "[aout]" -map 11:s \
  -c:v libx264 -preset slow -crf 22 -profile:v high -pix_fmt yuv420p -r 30 -g 60 -x264-params threads=8 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -c:s mov_text -metadata:s:s:0 language=eng \
  -t <total from audio/timings.json> -movflags +faststart -map_metadata -1 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
  output/how_el_nino_forms.mp4
```

**Expected result:** about **5:06** (305.7 s with the reference voice) and about 9,171 frames. H.264 High
1920×1080 30 fps, AAC 48 kHz stereo at about −16 LUFS, with a soft English subtitle track.

## Determinism

* **Pure-function frames.** Each frame is a function of `t = frame / 30` only: no clock and no
  `Math.random()` (a seeded PRNG is used instead). Frames render identically in any order, in parallel,
  or resumed. Rendering uses SwiftShader inside the pinned Chrome, and fonts and Three.js come from `node_modules`.
* **Audio.** Phonon runs with a fixed seed on one CPU thread. Re-runs give identical timings to the
  millisecond, with at most a few dozen samples per scene differing by one bit (about −115 dB). Audio is
  generated once and checksummed in `audio/manifest.json`; keep `audio/` to reproduce a cut exactly.
  Piper (zero noise) is byte-exact. edge-tts varies slightly per run.
* **Encode.** FFmpeg uses `+bitexact`, strips metadata and pins the x264 thread count.

## Editing

1. Change the text in `config/scenes.json`, then run `python tools/tts.py`. Only changed scenes are re-voiced.
2. Visual beats are keyed to phrases with `cue("s05", "sloshes east")` in `scene/index.html`.
   If you reword a phrase that a beat uses, the page tells you which cue is missing.
3. Re-run `build_srt.py` and `make_storyboard.py`, then render and assemble.

## Troubleshooting

* **“audio/timings.json not found” on screen or at capture:** run `python tools/tts.py` first.
* **Phonon download fails:** it needs `huggingface.co` once. Behind a TLS proxy, set `SSL_CERT_FILE`.
  Otherwise use `--engine edge` or `--engine piper`.
* **edge-tts `NoAudioReceived` or SSL errors:** use `--engine phonon` or `--engine piper`.
* **Chrome won't start:** run `npx puppeteer browsers install chrome-headless-shell`, and unset `PUPPETEER_EXECUTABLE_PATH`.
* **Wrong frame count at assembly:** re-run `node render/capture.mjs --resume`. A new TTS run changes the length.

## Science notes

The film covers:
- trade winds and the Walker circulation
- the tilted thermocline, upwelling and the cold tongue
- the Bjerknes feedback
- westerly wind bursts and Kelvin waves (about 2 months to cross the Pacific)
- reversal of the feedback and the eastward shift of convection
- jet-stream and storm-track changes
- typical teleconnections, with a global mean warming of about 0.1–0.2 °C
- decay by Rossby-wave reflection and heat discharge, then La Niña
- a 2–7 year recurrence, with events lasting about 9–12 months

ENSO is presented as natural. Climate change is said to modulate its impacts, and future ENSO behaviour
is described as still being researched.

Further reading: NOAA Climate.gov ENSO (climate.gov/enso), NOAA PMEL (pmel.noaa.gov/elnino), and IPCC AR6 WGI.
