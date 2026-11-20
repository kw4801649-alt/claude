#!/usr/bin/env python3
"""
tools/build_srt.py -- Build subtitles/elnino.srt from config/scenes.json.

If audio/timings.json exists (written by tools/tts.py), cue times follow the real
speech segments of the generated audio. Each [PAUSE]-delimited segment is split into
readable cues (max 2 lines x 42 characters) and the segment's duration is shared
between its cues in proportion to their character count.

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


def estimate_segments(scene: dict, audio: dict, wpm: float) -> list[dict]:
    t = float(audio["lead_in_s"])
    out = []
    for text in segments_of(scene["narration"]):
        dur = len(text.split()) / wpm * 60.0
        out.append({"start": t, "end": t + dur, "text": text})
        t += dur + float(audio["pause_s"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimate", action="store_true", help="ignore audio/timings.json")
    ap.add_argument("--wpm", type=float, default=148.0)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text("utf-8"))
    timings = {}
    if TIMINGS.exists() and not args.estimate:
        timings = json.loads(TIMINGS.read_text("utf-8"))
        print(f"Using measured timings from {TIMINGS.relative_to(ROOT)}")
    else:
        print(f"Estimating timings at {args.wpm:.0f} wpm")

    entries = []
    scene_start = 0.0
    for scene in cfg["scenes"]:
        if scene["id"] in timings:
            segs = timings[scene["id"]]["segments"]
            if len(segs) != len(segments_of(scene["narration"])):
                print(f"ERROR: {scene['id']} narration changed since audio was generated; "
                      f"re-run tools/tts.py", file=sys.stderr)
                return 1
        else:
            segs = estimate_segments(scene, cfg["audio"], args.wpm)
        for seg in segs:
            cues = cues_for_segment(seg["text"])
            total_chars = sum(len(c) for c in cues)
            seg_dur = float(seg["end"]) - float(seg["start"])
            t = scene_start + float(seg["start"])
            for c in cues:
                d = seg_dur * len(c) / total_chars
                entries.append((t, t + d, wrap(c)))
                t += d
        scene_start += float(scene["duration"])

    # small gap between consecutive cues so players never show two at once
    lines = []
    for i, (a, b, text) in enumerate(entries, start=1):
        end = b - 0.04 if i < len(entries) and entries[i][0] - b < 0.04 else b
        lines.append(f"{i}\n{ts(a)} --> {ts(end)}\n{text}\n")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(entries)} cues to {out} (video length {scene_start:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
