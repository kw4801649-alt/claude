#!/usr/bin/env python3
"""
tools/build_srt.py -- Build subtitles/elnino.srt from config/scenes.json.

If audio/timings.json exists (written by tools/tts.py), every cue starts and ends with the
real spoken sentence. Long sentences are split into readable cues (max 2 lines x 42
characters) and the sentence's duration is shared between them by character count.

If audio/timings.json does not exist, times are estimated at --wpm words per minute,
with the same lead-in and pause lengths tools/tts.py uses.

Usage:
    python tools/build_srt.py                 # use audio/timings.json if present
    python tools/build_srt.py --estimate      # ignore timings, estimate from WPM
    python tools/build_srt.py --out subtitles/elnino.srt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.json"
TIMINGS = ROOT / "audio" / "timings.json"
DEFAULT_OUT = ROOT / "subtitles" / "elnino.srt"
LINE = 42
MAX_CUE = 80


def segments_of(narration: str) -> list[str]:
    return [p.strip() for p in narration.split("[PAUSE]") if p.strip()]


def split_long(sentence: str) -> list[str]:
    """Split a sentence into chunks <= MAX_CUE chars, preferring clause boundaries."""
    if len(sentence) <= MAX_CUE:
        return [sentence]
    # candidate break points after , ; : or a dash
    pieces = re.split(r"(?<=[,;:])\s+|\s+(?=–)", sentence)
    chunks: list[str] = []
    cur = ""
    for piece in pieces:
        cand = f"{cur} {piece}".strip()
        if len(cand) <= MAX_CUE:
            cur = cand
        else:
            if cur:
                chunks.append(cur)
            cur = piece
    if cur:
        chunks.append(cur)
    out: list[str] = []
    for c in chunks:  # still too long (no punctuation): split on words near the middle
        while len(c) > MAX_CUE:
            words = c.split()
            half, acc = [], 0
            for w in words:
                if acc + len(w) + 1 > len(c) / 2 and half:
                    break
                half.append(w)
                acc += len(w) + 1
            out.append(" ".join(half))
            c = " ".join(words[len(half):])
        out.append(c)
    return out


def cues_for_segment(text: str) -> list[str]:
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
    cues: list[str] = []
    for s in sentences:
        cues.extend(split_long(s))
    # merge very short neighbours (< 28 chars) when they fit together
    merged: list[str] = []
    for c in cues:
        if merged and (len(merged[-1]) < 28 or len(c) < 20) and len(merged[-1]) + 1 + len(c) <= MAX_CUE:
            merged[-1] = f"{merged[-1]} {c}"
        else:
            merged.append(c)
    return merged


def wrap(text: str) -> str:
    """One line if it fits, otherwise two lines balanced as evenly as possible."""
    if len(text) <= LINE:
        return text
    words = text.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, a, b)
    return f"{best[1]}\n{best[2]}"


def ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def estimate_scene(scene: dict, audio: dict, wpm: float) -> dict:
    t = float(scene.get("lead_in_s", audio["lead_in_s"]))
    segs = []
    for text in segments_of(scene["narration"]):
        sents = []
        for sent in re.split(r"(?<=[.!?])\s+", text):
            d = len(sent.split()) / wpm * 60.0
            sents.append({"start": t, "end": t + d, "text": sent})
            t += d + 0.12
        segs.append({"sentences": sents})
        t += float(audio["pause_s"])
    return {"segments": segs, "slot": t + float(scene.get("tail_s", audio["tail_s"]))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimate", action="store_true", help="ignore audio/timings.json")
    ap.add_argument("--wpm", type=float, default=175.0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text("utf-8"))
    timeline = {}
    if TIMINGS.exists() and not args.estimate:
        timeline = json.loads(TIMINGS.read_text("utf-8")).get("scenes", {})
        print(f"Using measured sentence timings from {TIMINGS.relative_to(ROOT)}")
    else:
        print(f"Estimating timings at {args.wpm:.0f} wpm")

    entries = []
    scene_start = 0.0
    for scene in cfg["scenes"]:
        t = timeline.get(scene["id"]) or estimate_scene(scene, cfg["audio"], args.wpm)
        if len(t["segments"]) != len(segments_of(scene["narration"])):
            print(f"ERROR: {scene['id']} narration changed since audio was generated; re-run tools/tts.py",
                  file=sys.stderr)
            return 1
        for seg in t["segments"]:
            for sent in seg["sentences"]:
                cues = cues_for_segment(sent["text"])          # long sentences -> several cues
                total_chars = sum(len(c) for c in cues)
                a = scene_start + float(sent["start"])
                dur = float(sent["end"]) - float(sent["start"])
                for c in cues:
                    d = dur * len(c) / total_chars
                    entries.append((a, a + d, wrap(c)))
                    a += d
        scene_start += float(t["slot"])

    lines = []
    for i, (a, b, text) in enumerate(entries, start=1):
        # hold each cue until the next one starts (max 0.6 s extra), never overlapping
        nxt = entries[i][0] if i < len(entries) else b + 0.6
        end = min(max(b, a + 0.8), nxt - 0.04, b + 0.6)
        lines.append(f"{i}\n{ts(a)} --> {ts(end)}\n{text}\n")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(entries)} cues to {out} (video length {scene_start:.2f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
