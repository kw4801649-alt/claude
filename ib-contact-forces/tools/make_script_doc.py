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
timings = json.loads(tpath.read_text("utf-8")).get("scenes", {}) if tpath.exists() else {}


def tc(sec: float) -> str:
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


lines = [
    f"# {cfg['title']} — Narration script",
    "",
    "_Generated from `config/scenes.json` by `tools/make_script_doc.py`; edit the JSON, not this file._",
    "",
    "- Voice: Phonon 31M `{ph}`, words-per-minute measured while talking (fallbacks: edge-tts `{voice}` at `{rate}`, then Piper `{pv}`)".format(
        ph=cfg["tts"]["phonon"]["voice"], voice=cfg["tts"]["edge"]["voice"], rate=cfg["tts"]["edge"]["rate"],
        pv=cfg["tts"]["piper"]["voice"]),
    f"- `[PAUSE]` = {cfg['audio']['pause_s']} s of silence so the visuals can breathe; "
    f"sentences are {cfg['tts']['phonon']['sentence_silence']} s apart; speech is time-stretched to {cfg['audio'].get('tempo', 1.0)}x speed (pitch kept; below 1 is slower).",
    "- Scene lengths come from the audio (`audio/timings.json`); every animation is keyed to the words.",
    "",
]
start = 0.0
tot_words = tot_speech = 0.0
for i, s in enumerate(cfg["scenes"], 1):
    slot = timings[s["id"]]["slot"] if s["id"] in timings else 0.0
    end = start + slot
    words = len(s["narration"].replace("[PAUSE]", " ").split())
    tot_words += words
    meta = f"{words} words"
    if s["id"] in timings:
        segs = timings[s["id"]]["segments"]
        speech = sum(x["end"] - x["start"] for g in segs for x in g["sentences"])
        tot_speech += speech
        meta += f" · speech {speech:.1f} s · {words / speech * 60:.0f} wpm · ends at {tc(start + timings[s['id']]['speech_end'])}"
    lines += [f"## Scene {i} ({s['id']}) — {s['title']}", "",
              f"**{tc(start)} – {tc(end)}** ({slot:.1f} s) · {meta}", "",
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
