#!/usr/bin/env python3
"""
tools/make_script_doc.py -- Write docs/01_narration_script.md from config/scenes.json.

The narration lives in ONE place (config/scenes.json); this keeps the human-readable
script in sync with what the TTS and subtitle tools actually use. If audio/timings.json
exists, the measured speech length and words-per-minute of each scene are included.

Usage: python tools/make_script_doc.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "config" / "scenes.json").read_text("utf-8"))
tpath = ROOT / "audio" / "timings.json"
timings = json.loads(tpath.read_text("utf-8")) if tpath.exists() else {}


def tc(sec: float) -> str:
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


lines = [
    f"# {cfg['title']} — Narration script",
    "",
    "_Generated from `config/scenes.json` by `tools/make_script_doc.py`; edit the JSON, not this file._",
    "",
    "- Voice: edge-tts `{voice}` at rate `{rate}` (fallback: Piper `{pv}`)".format(
        voice=cfg["tts"]["edge"]["voice"], rate=cfg["tts"]["edge"]["rate"], pv=cfg["tts"]["piper"]["voice"]),
    f"- `[PAUSE]` = {cfg['audio']['pause_s']} s of silence so the visuals can breathe; "
    f"each scene starts with {cfg['audio']['lead_in_s']} s of silence.",
    "- Scene slots are fixed: audio is padded to the slot, so the picture never depends on speaking speed.",
    "",
]
start = 0.0
tot_words = tot_speech = 0.0
for i, s in enumerate(cfg["scenes"], 1):
    end = start + s["duration"]
    words = len(s["narration"].replace("[PAUSE]", " ").split())
    tot_words += words
    meta = f"{words} words"
    if s["id"] in timings:
        segs = timings[s["id"]]["segments"]
        speech = sum(g["end"] - g["start"] for g in segs)
        tot_speech += speech
        meta += f" · speech {speech:.1f} s · {words / speech * 60:.0f} wpm · ends at {tc(start + timings[s['id']]['speech_end'])}"
    lines += [f"## Scene {i} ({s['id']}) — {s['title']}", "",
              f"**{tc(start)} – {tc(end)}** ({s['duration']} s) · {meta}", "",
              s["narration"].replace("[PAUSE]", "**[PAUSE]**"), ""]
    start = end
lines += ["---", "", f"**Total: {tc(start)} ({start:.0f} s), {int(tot_words)} words"
          + (f", {tot_words / tot_speech * 60:.0f} wpm while speaking.**" if tot_speech else ".**"), ""]
lines += ["## Pronunciation overrides (sent to TTS only; subtitles keep the real spelling)", "",
          "| Written | Spoken as |", "|---|---|"]
lines += [f"| {k} | {v} |" for k, v in cfg["pronunciations"].items()]
lines.append("")
out = ROOT / "docs" / "01_narration_script.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines), "utf-8")
print(f"Wrote {out.relative_to(ROOT)}")
