# How El Niño Forms: production package

A complete, deterministic pipeline for a **6:25 animated explainer** (1920x1080, 16:9, 30 fps),
built only with free and open-source tools:

| Step | Tool | What it makes |
|---|---|---|
| Narration | `config/scenes.json` | Script and fixed scene slots (single source of truth) |
| Voice | **Phonon 31M** (primary, offline) / **edge-tts** / **Piper** (fallbacks) | `audio/s01.wav` … `audio/s10.wav` |
| Subtitles | `tools/build_srt.py` | `subtitles/elnino.srt` |
| 3D scenes | **Three.js** (one HTML file) | `scene/index.html`, everything driven by a time `t` |
| Frames | **Puppeteer + headless Chrome** | `frames/f_00000.png` … `f_11549.png` |
| Assembly | **FFmpeg** | `output/how_el_nino_forms.mp4` (subtitles burned in) |

## Assumptions

1. **Voice:** Phonon 31M (`gradium/phonon-31m-en`, Apache 2.0), voice **Hadley**, one sentence at a time with 0.3 s gaps. That measures about 149 wpm while speaking. Fallbacks: edge-tts `en-US-AriaNeural` at `-6%`, then Piper `en_US-lessac-medium` at `length_scale 1.25`. To change the voice, edit `tts.phonon.voice` in `config/scenes.json` (narrator-friendly options: Hadley, Preston, Spencer, Miles, Everly).
2. **Fixed timing:** each scene has a fixed length (`duration` in `config/scenes.json`). Each scene's audio is padded with silence to exactly that length, so the picture never depends on how fast the voice speaks. The total is **385 s = 6:25**.
3. **`[PAUSE]` timing:** each `[PAUSE]` becomes 0.8 s of silence, and every scene starts with 0.5 s of silence.
4. **Cross-section view:** the 3D "Pacific box" follows the classic NOAA-style diagram. The top is the sea surface from 22°N to 15°S and 100°E to 60°W. The front face is a schematic **equatorial** cross-section, with depth hugely exaggerated (an on-screen note says so).
5. **Illustrative data:** sea-surface temperature, thermocline depth, winds and waves are illustrative, smooth analytic fields, not observational data. The ENSO-index chart in scene 9 is labelled "schematic, illustrative only: not real data".
6. **Impacts:** the global-effects scene shows typical El Niño *tendencies*, mostly for boreal winter, and the narration says they are not guarantees.
7. **Subtitles:** they are burned in and also included as a soft (toggleable) track. The burned-in font is DejaVu Sans.
8. **Music:** there is none. Drop a track into the FFmpeg filter if you want one.
9. **Platform:** tested on Linux. macOS works the same way. On Windows, run the shell steps in WSL or Git Bash.

## Required tool versions

| Tool | Version used / pinned | Notes |
|---|---|---|
| Node.js | ≥ 20 (tested 22.23) | runs Puppeteer |
| npm | ≥ 9 (tested 10.9) | `npm ci` uses the committed `package-lock.json` |
| puppeteer | **25.18.1** (pinned) | pins **chrome-headless-shell 157.0.8103.78** |
| three | **0.187.0** (pinned) | loaded from `node_modules` (no CDN at render time) |
| @fontsource/inter | **5.3.0** (pinned) | on-screen typography, loaded locally |
| Python | ≥ 3.9 (tested 3.13.18) | TTS and subtitle scripts |
| ptts (Phonon runtime) | **0.7.1** (pinned) | Phonon 31M, Apache 2.0, CPU, only needs numpy; model (~65 MB) downloads on first use |
| edge-tts | **7.3.1** (pinned) | needs internet, no API key |
| piper-tts | **1.8.0** (pinned) | offline, pulls onnxruntime (tested 1.32.0) |
| FFmpeg | ≥ 6.0 (tested 6.1.1) | must include `libx264` and `libass` (standard builds do) |
| DejaVu Sans font | any | subtitle font (`fonts-dejavu-core` on Debian/Ubuntu) |

## Folder layout

```
elnino-video/
├── config/scenes.json          # narration text, scene slots, voices, pronunciations
├── docs/01_narration_script.md # deliverable 1 (generated from scenes.json)
├── docs/02_storyboard.md       # deliverable 2
├── tools/tts.py                # deliverable 3: Phonon -> edge-tts -> Piper, one WAV per scene
├── scene/index.html            # deliverable 4: Three.js scene + camera keyframes
├── render/serve.mjs            # local static server (preview + capture)
├── render/capture.mjs          # deliverable 5a: deterministic frame capture
├── tools/assemble.sh           # deliverable 5b: FFmpeg mux + burned-in subtitles
├── subtitles/elnino.srt        # deliverable 6 (built by tools/build_srt.py)
├── tools/build_srt.py          # SRT from the measured audio timings
├── tools/make_script_doc.py    # regenerates docs/01_narration_script.md
├── package.json / package-lock.json / requirements.txt
└── (generated) audio/ voices/ frames/ renders/ output/
```

## Step by step

All commands run from the `elnino-video/` folder.

### 0. Install system tools

```bash
# Debian / Ubuntu
sudo apt-get update && sudo apt-get install -y ffmpeg python3 python3-venv fonts-dejavu-core
# Node.js 20+ from https://nodejs.org (or: nvm install 22)

# macOS (Homebrew)
brew install ffmpeg python node
brew install --cask font-dejavu
```

### 1. Python dependencies (TTS)

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # ptts==0.7.1, edge-tts==7.3.1, piper-tts==1.8.0
```

### 2. Node dependencies (Three.js, Puppeteer and its pinned Chrome)

```bash
npm ci                                              # exact versions from package-lock.json
npx puppeteer browsers install chrome-headless-shell # Chrome build pinned by puppeteer 25.18.1
```

If `npm ci` skipped the browser download because `PUPPETEER_SKIP_DOWNLOAD` or
`PUPPETEER_EXECUTABLE_PATH` is set, the second command installs it. Unset
`PUPPETEER_EXECUTABLE_PATH` so the pinned build is used.

### 3. Generate the narration audio (one file per scene)

```bash
python tools/tts.py                  # Phonon; if it fails, edge-tts, then Piper (ALL scenes re-made each time)
python tools/tts.py --engine phonon  # force Phonon 31M (voice Hadley; ~1 min on CPU for the whole film)
python tools/tts.py --engine edge    # force edge-tts (voice en-US-AriaNeural, rate -6%)
python tools/tts.py --engine piper   # force Piper (offline; downloads en_US-lessac-medium to voices/ once)
```

The output is `audio/s01.wav` … `audio/s10.wav` (48 kHz mono PCM, each exactly its slot length),
plus `audio/timings.json` and `audio/manifest.json` (SHA-256 of every file). Results are
cached: a re-run only re-synthesizes scenes whose text or settings changed. Use `--force` to redo
everything. If a scene's speech doesn't fit its slot, the script stops and tells you the minimum
`duration` to set.

Phonon downloads its model and voice into the Hugging Face cache (`~/.cache/huggingface`) the first time it runs.
To pre-download the Piper voice yourself: `python -m piper.download_voices --download-dir voices en_US-lessac-medium`.

### 4. Subtitles and script document

```bash
python tools/build_srt.py            # subtitles/elnino.srt, timed to the audio you just made
python tools/make_script_doc.py      # docs/01_narration_script.md (adds measured wpm)
```

The committed `subtitles/elnino.srt` was built from a reference Phonon run. Re-run
`build_srt.py` after step 3, because each TTS run can differ by a few hundredths of a second.

### 5. (Optional) Preview in a browser

```bash
npm run preview                      # then open http://127.0.0.1:8080/scene/index.html?preview=1
```

This gives you a scrubber, play/pause and narration playback. Use `?t=95` for a single still at 95 s.

### 6. (Optional) Render test stills

```bash
npm run render:test                  # 35 stills, one per storyboard beat -> renders/test/
node render/capture.mjs --test --times 12,95.5,250   # specific times
```

### 7. Render all frames (1920x1080, 30 fps)

```bash
node render/capture.mjs --workers 3  # 11,550 PNGs -> frames/  (about 3 GB)
```

* **Speed (measured):** with software WebGL, a 4-core machine with `--workers 3` renders about
  6.5 frames/s, so the whole film takes about **30 minutes**. With `--workers 1` it renders about
  3.3 frames/s, which is about 60 minutes.
* **Resume:** if it's interrupted, run it again with `--resume` to skip frames already on disk.
* **Split across machines:** use `--start N --end M` to render part of the frame range.
* **GPU:** `--gpu` uses your real GPU (faster), but the pixels can then differ between drivers.
  Keep the default SwiftShader for byte-identical output.

### 8. Assemble the final video

```bash
bash tools/assemble.sh
```

This runs the following FFmpeg command (written out here so you can also run it by hand):

```bash
ffmpeg -hide_banner -y \
  -framerate 30 -start_number 0 -i frames/f_%05d.png \
  -i audio/s01.wav -i audio/s02.wav -i audio/s03.wav -i audio/s04.wav -i audio/s05.wav \
  -i audio/s06.wav -i audio/s07.wav -i audio/s08.wav -i audio/s09.wav -i audio/s10.wav \
  -i subtitles/elnino.srt \
  -filter_complex "[1:a][2:a][3:a][4:a][5:a][6:a][7:a][8:a][9:a][10:a]concat=n=10:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout];[0:v]subtitles=subtitles/elnino.srt:force_style='FontName=DejaVu Sans,FontSize=12,Bold=0,PrimaryColour=&H00FFFFFF,OutlineColour=&H00442A0F,BackColour=&H99442A0F,BorderStyle=1,Outline=1.3,Shadow=0.5,MarginV=20,Alignment=2',format=yuv420p[vout]" \
  -map "[vout]" -map "[aout]" -map 11:s \
  -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -r 30 -g 60 -x264-params threads=8 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -c:s mov_text -metadata:s:s:0 language=eng \
  -t 385 -movflags +faststart -map_metadata -1 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
  output/how_el_nino_forms.mp4
```

### Expected result

`output/how_el_nino_forms.mp4` should be:

* **6:25 (385.0 s)** long, with 11,550 frames
* H.264 High, 1920x1080, 30 fps, yuv420p
* AAC 48 kHz stereo, loudness-normalized to −16 LUFS
* subtitles burned in, plus a soft `mov_text` track
* about 90 MB (the reference build was 90,056,798 bytes)

## Determinism (how re-renders stay identical)

* **Pure-function frames:** every frame is computed from `t = frame / 30` alone. Camera keyframes, state tracks
  (wind, ENSO phase, cloud and Walker visibility), particle positions and label fades are all closed-form
  or tabulated from `t`. Nothing reads the clock and there is no `Math.random()`. Layouts come from a
  seeded PRNG (mulberry32).
* **Order-independent frames:** a frame rendered alone matches the same frame rendered mid-sequence, so
  frames can be rendered in any order, in parallel, or resumed.
* **Pinned renderer:** WebGL runs on SwiftShader inside the Chrome build pinned by Puppeteer, with fonts
  and Three.js served from `node_modules`.
* **Encoding:** FFmpeg uses `+bitexact` flags, strips metadata and pins the x264 thread count.
* **Audio:** Phonon runs with a fixed seed on one CPU thread. Re-runs give identical timings to the
  millisecond. At most a few dozen samples per scene differ by 1/32768 (about −115 dB, inaudible), because
  of floating-point rounding in the runtime. edge-tts is a cloud service and its bytes vary slightly per run.
  Either way the audio is generated once and cached, with SHA-256 hashes in `audio/manifest.json`. Keep
  `audio/` with your project to reproduce a cut exactly. Piper is run with zero noise and is byte-for-byte
  reproducible.
  Pass `--piper-natural` for a livelier but non-reproducible Piper voice.
* **Timing:** the video timeline never depends on the audio, because scene slots are fixed.

## Editing the video

1. Edit text or `duration` in `config/scenes.json`.
2. Run `python tools/tts.py`. Only the changed scenes are re-synthesized, and it tells you if a slot is too short.
3. Run `python tools/build_srt.py && python tools/make_script_doc.py`.
4. Adjust visual beats in `scene/index.html` if needed (search for `at("s05", …)`). All beats are scene-relative,
   so changing one scene's duration shifts every later scene's visuals automatically.
5. Run `npm run render:test`, then the full render, then assembly.

## Troubleshooting

* **Phonon can't download its model:** it needs access to `huggingface.co` the first time. Behind a
  TLS proxy, set `SSL_CERT_FILE` to your CA bundle. Otherwise run `--engine edge` or `--engine piper`.
* **`edge-tts` gives `NoAudioReceived` or SSL errors:** edge-tts needs internet access to
  `speech.platform.bing.com`. Behind a corporate TLS proxy, add the proxy CA to certifi's bundle
  (`python -c "import certifi; print(certifi.where())"`). Otherwise use `--engine piper`.
* **Chrome fails to launch on Linux:** run `npx puppeteer browsers install chrome-headless-shell`.
  If libraries are missing: `sudo apt-get install -y libnss3 libatk-bridge2.0-0 libgbm1 libasound2 libxkbcommon0 libxdamage1 libxrandr2`.
* **Black or empty frames:** check that `--use-angle=swiftshader --enable-unsafe-swiftshader` is not blocked by
  your Chrome policy. Try `npm run render:test` and look at the console output.
* **Subtitles render in a fallback font:** install DejaVu Sans, or change `FontName=` in `tools/assemble.sh`.
* **Wrong number of frames:** `assemble.sh` checks for 11,550 frames. Re-run `node render/capture.mjs --resume`.

## Science notes

The script follows mainstream descriptions of ENSO. It covers the trade winds and the Walker circulation,
the tilted thermocline and upwelling, and the Bjerknes (1969) feedback. It shows westerly wind bursts and
downwelling Kelvin waves (about 2 months to cross the basin) as the trigger. It shows decay through
Rossby-wave reflection (the "delayed oscillator") and heat discharge away from the equator
("recharge–discharge"). It gives a recurrence of roughly 2–7 years and events of about 9–12 months.

It states clearly that ENSO is natural, and that climate change modulates its impacts while future ENSO
behaviour is still being researched. Global impacts are phrased as tendencies. Further reading:
NOAA Climate.gov ENSO resources (climate.gov/enso), NOAA PMEL El Niño theme page (pmel.noaa.gov/elnino),
and IPCC AR6 WGI, Chapters 2, 4 and 8.
