#!/usr/bin/env bash
# tools/assemble.sh — mux rendered frames + per-scene narration (+ subtitles) into
# output/contact_forces_derived.mp4 (1920x1080, 30 fps, H.264 + AAC).
#
#   bash tools/assemble.sh               # subtitles as a soft, switchable track (no caption bar on screen)
#   BURN_SUBS=1 bash tools/assemble.sh   # also burn the subtitles into the picture
#
# Inputs : frames/f_%05d.png, audio/s01.wav ... audio/s10.wav, audio/timings.json, subtitles/contact_forces.srt
# Determinism: -fflags/-flags +bitexact, no metadata, fixed x264 thread count.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f audio/timings.json ] || { echo "ERROR: audio/timings.json missing. Run: python tools/tts.py" >&2; exit 1; }
FPS=$(python3 -c "import json;print(json.load(open('config/scenes.json'))['video']['fps'])")
TOTAL=$(python3 -c "import json;print(json.load(open('audio/timings.json'))['total'])")
SCENES=$(python3 -c "import json;print(' '.join(s['id'] for s in json.load(open('config/scenes.json'))['scenes']))")
FRAMES_EXPECTED=$(python3 -c "print(round($TOTAL * $FPS))")
EXT=png; [ -f frames/f_00000.jpg ] && EXT=jpg
FRAMES_FOUND=$(find frames -maxdepth 1 -name "f_*.${EXT}" | wc -l)
if [ "$FRAMES_FOUND" -ne "$FRAMES_EXPECTED" ]; then
  echo "ERROR: expected $FRAMES_EXPECTED frames in frames/, found $FRAMES_FOUND. Run: node render/capture.mjs" >&2
  exit 1
fi
for id in $SCENES; do [ -f "audio/$id.wav" ] || { echo "ERROR: audio/$id.wav missing. Run: python tools/tts.py" >&2; exit 1; }; done
[ -f subtitles/contact_forces.srt ] || { echo "ERROR: subtitles/contact_forces.srt missing. Run: python tools/build_srt.py" >&2; exit 1; }
mkdir -p output

AUDIO_INPUTS=(); CONCAT=""; i=1
for id in $SCENES; do AUDIO_INPUTS+=(-i "audio/$id.wav"); CONCAT+="[$i:a]"; i=$((i+1)); done
N=$((i-1))

VIDEO_FILTER="format=yuv420p"
if [ "${BURN_SUBS:-0}" = "1" ]; then
  # ASS colours are &HAABBGGRR; libass renders SRT on a 384x288 canvas, so FontSize=12 is ~45 px at 1080p.
  STYLE="FontName=DejaVu Sans,FontSize=12,Bold=0,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.2,Shadow=0,MarginV=20,Alignment=2"
  VIDEO_FILTER="subtitles=subtitles/contact_forces.srt:force_style='${STYLE}',format=yuv420p"
fi

set -x
ffmpeg -hide_banner -y \
  -framerate "$FPS" -start_number 0 -i "frames/f_%05d.${EXT}" \
  "${AUDIO_INPUTS[@]}" \
  -i subtitles/contact_forces.srt \
  -filter_complex "${CONCAT}concat=n=${N}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout];[0:v]${VIDEO_FILTER}[vout]" \
  -map "[vout]" -map "[aout]" -map "$((N+1)):s" \
  -c:v libx264 -preset slow -crf 22 -profile:v high -pix_fmt yuv420p -r "$FPS" -g $((FPS*2)) -x264-params threads=8 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -c:s mov_text -metadata:s:s:0 language=eng \
  -t "$TOTAL" -movflags +faststart -map_metadata -1 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
  output/contact_forces_derived.mp4
set +x

ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of default=nw=1 output/contact_forces_derived.mp4
echo "Wrote output/contact_forces_derived.mp4 (expected duration ${TOTAL}s)"
