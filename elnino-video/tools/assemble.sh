#!/usr/bin/env bash
# tools/assemble.sh — mux rendered frames + per-scene narration + burned-in subtitles
# into output/how_el_nino_forms.mp4 (1920x1080, 30 fps, H.264 + AAC).
#
# Run from anywhere:  bash tools/assemble.sh
# Inputs : frames/f_%05d.png, audio/s01.wav ... audio/s10.wav, subtitles/elnino.srt
# Output : output/how_el_nino_forms.mp4  (burned-in subtitles + a soft subtitle track)
#
# Determinism: -fflags/-flags +bitexact, no metadata, fixed x264 thread count.
# The same inputs and the same FFmpeg build give a byte-identical file.
set -euo pipefail
cd "$(dirname "$0")/.."

FPS=$(python3 -c "import json;print(json.load(open('config/scenes.json'))['video']['fps'])")
TOTAL=$(python3 -c "import json;print(sum(s['duration'] for s in json.load(open('config/scenes.json'))['scenes']))")
SCENES=$(python3 -c "import json;print(' '.join(s['id'] for s in json.load(open('config/scenes.json'))['scenes']))")
FRAMES_EXPECTED=$(( TOTAL * FPS ))
EXT=png; [ -f frames/f_00000.jpg ] && EXT=jpg
FRAMES_FOUND=$(find frames -maxdepth 1 -name "f_*.${EXT}" | wc -l)

if [ "$FRAMES_FOUND" -ne "$FRAMES_EXPECTED" ]; then
  echo "ERROR: expected $FRAMES_EXPECTED frames in frames/, found $FRAMES_FOUND. Run: npm run render" >&2
  exit 1
fi
for id in $SCENES; do [ -f "audio/$id.wav" ] || { echo "ERROR: audio/$id.wav missing. Run: python tools/tts.py" >&2; exit 1; }; done
[ -f subtitles/elnino.srt ] || { echo "ERROR: subtitles/elnino.srt missing. Run: python tools/build_srt.py" >&2; exit 1; }
mkdir -p output

# Build the input list and the audio concat filter from the scene order in config/scenes.json
AUDIO_INPUTS=(); CONCAT=""; i=1
for id in $SCENES; do AUDIO_INPUTS+=(-i "audio/$id.wav"); CONCAT+="[$i:a]"; i=$((i+1)); done
N=$((i-1))

# Subtitle style (ASS colours are &HAABBGGRR). SRT is rendered on a 384x288 canvas by libass,
# so FontSize=12 is roughly 45 px at 1080p.
STYLE="FontName=DejaVu Sans,FontSize=12,Bold=0,PrimaryColour=&H00FFFFFF,OutlineColour=&H00442A0F,BackColour=&H99442A0F,BorderStyle=1,Outline=1.3,Shadow=0.5,MarginV=20,Alignment=2"

set -x
ffmpeg -hide_banner -y \
  -framerate "$FPS" -start_number 0 -i "frames/f_%05d.${EXT}" \
  "${AUDIO_INPUTS[@]}" \
  -i subtitles/elnino.srt \
  -filter_complex "${CONCAT}concat=n=${N}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout];[0:v]subtitles=subtitles/elnino.srt:force_style='${STYLE}',format=yuv420p[vout]" \
  -map "[vout]" -map "[aout]" -map "$((N+1)):s" \
  -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -r "$FPS" -g $((FPS*2)) -x264-params threads=8 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -c:s mov_text -metadata:s:s:0 language=eng \
  -t "$TOTAL" -movflags +faststart -map_metadata -1 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
  output/how_el_nino_forms.mp4
set +x

ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of default=nw=1 output/how_el_nino_forms.mp4
echo "Wrote output/how_el_nino_forms.mp4 (expected duration ${TOTAL}s)"
