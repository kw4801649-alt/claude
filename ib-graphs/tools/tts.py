#!/usr/bin/env python3
"""
tools/tts.py -- Generate one narration WAV per scene for "Reading Motion and Momentum Graphs".

Primary engine : Phonon 31M via `ptts` (Apache-2.0 open weights, offline, CPU)
Fallback 1     : edge-tts (free Microsoft Edge online voices, no API key)
Fallback 2     : Piper TTS (fully offline, open source)

Output (all paths relative to the project root):
    audio/s01.wav ... audio/s10.wav   48 kHz, mono, 16-bit PCM, one per scene.
    audio/timings.json                THE TIMELINE: every scene's length ("slot") and the
                                      start/end of every spoken sentence. The 3D scene, the
                                      frame capture, the subtitles and the FFmpeg assembly
                                      all read this file, so pictures, words and captions
                                      stay locked to the voice.
    audio/manifest.json               engine, voice, settings, cache key, SHA-256 per file

Each scene is built as:
    [lead-in] sentence [gap] sentence ... [PAUSE] sentence ... [tail]
A scene's length is its speech plus the tail, rounded up to a whole video frame, unless
config/scenes.json gives a fixed number of seconds in "duration".

Usage:
    python tools/tts.py                    # auto: Phonon, then edge-tts, then Piper
    python tools/tts.py --engine phonon    # Phonon only (offline after the first model download)
    python tools/tts.py --engine edge      # edge-tts only
    python tools/tts.py --engine piper     # Piper only (offline)
    python tools/tts.py --force            # ignore the cache and regenerate everything
    python tools/tts.py --only s03,s04     # regenerate only some scenes

Requires: Python >= 3.9, ffmpeg on PATH, `pip install -r requirements.txt`.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.json"
AUDIO_DIR = ROOT / "audio"
VOICES_DIR = ROOT / "voices"
PAUSE_TOKEN = "[PAUSE]"
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class TTSError(RuntimeError):
    pass


# --------------------------------------------------------------------------- text helpers
def load_config(path: Path = CONFIG) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def split_segments(narration: str) -> list[str]:
    return [p.strip() for p in narration.split(PAUSE_TOKEN) if p.strip()]


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]


def apply_pronunciations(text: str, pron: dict[str, str]) -> str:
    """Replace display spellings with TTS-friendly spellings (whole words only).
    Applied per sentence, AFTER splitting, so respellings like "U.S." never create new sentences."""
    for key in sorted(pron, key=len, reverse=True):
        text = re.sub(r"(?<![\w])" + re.escape(key) + r"(?![\w])", pron[key], text)
    return text


# --------------------------------------------------------------------------- audio helpers
def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise TTSError(f"Command failed: {' '.join(cmd)}\n{proc.stderr[-2000:]}")


def to_pcm(src: Path, dst: Path, sample_rate: int, trim: bool, tempo: float) -> None:
    """Decode to mono 16-bit PCM at sample_rate. Optionally trim the engine's leading and
    trailing silence, and optionally speed speech up/down without changing pitch (atempo)."""
    filters = []
    if trim:
        filters.append("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse,"
                       "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse")
    if abs(tempo - 1.0) > 1e-6:
        filters.append(f"atempo={tempo:.4f}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    if filters:
        cmd += ["-af", ",".join(filters)]
    cmd += ["-ac", "1", "-ar", str(sample_rate), "-c:a", "pcm_s16le",
            "-fflags", "+bitexact", "-flags:a", "+bitexact", str(dst)]
    run(cmd)


def read_pcm(path: Path) -> tuple[bytes, int]:
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise TTSError(f"{path} is not mono 16-bit PCM")
        return w.readframes(w.getnframes()), w.getframerate()


def write_pcm(path: Path, data: bytes, sr: int) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data)


def silence(seconds: float, sample_rate: int) -> bytes:
    return b"\x00\x00" * int(round(seconds * sample_rate))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def join_sentences(chunks: list[bytes], sr: int, gap_s: float, out_path: Path) -> list[tuple[float, float]]:
    """Trim each sentence's own leading/trailing silence, join them with a fixed gap, write a
    WAV and return each sentence's (start, end) in seconds within that file."""
    import numpy as np
    gap = np.zeros(int(round(gap_s * sr)), np.int16)
    pad = int(0.02 * sr)
    parts, spans, cursor = [], [], 0
    for i, raw in enumerate(chunks):
        a = np.frombuffer(raw, np.int16)
        loud = np.nonzero(np.abs(a.astype(np.int32)) > 120)[0]          # about -48 dBFS
        if len(loud):
            a = a[max(0, loud[0] - pad): min(len(a), loud[-1] + pad)]
        parts.append(a)
        spans.append((cursor / sr, (cursor + len(a)) / sr))
        cursor += len(a)
        if i < len(chunks) - 1:
            parts.append(gap)
            cursor += len(gap)
    write_pcm(out_path, np.concatenate(parts).tobytes(), sr)
    return spans


# --------------------------------------------------------------------------- engines
# Every engine: synth(sentences: list[str], out_path) -> list[(start, end)] or None.
# Returning spans means the engine already trimmed silence and knows where each sentence is.
class PhononEngine:
    """Phonon 31M (gradium/phonon-31m-en) on the `ptts` runtime. One sentence at a time with a
    fixed seed on one CPU thread: timings are identical on every run (at most a few samples
    per scene differ by one least-significant bit, about -115 dB)."""
    name = "phonon"

    def __init__(self, cfg: dict):
        try:
            import ptts
        except ImportError as exc:
            raise TTSError("ptts is not installed: pip install -r requirements.txt") from exc
        self.model_id, self.quant, self.voice = cfg["model"], cfg["quant"], cfg["voice"]
        self.seed = int(cfg["seed"])
        self.temperature = cfg.get("temperature")
        self.gap = float(cfg["sentence_silence"])
        self.threads = int(cfg.get("threads", 1))
        if self.threads > 0:
            ptts.set_num_threads(self.threads)
        try:  # first use downloads the model (~65 MB) and the voice into the Hugging Face cache
            self.tts = ptts.TTS(self.model_id, lang="en", quant=self.quant)
        except Exception as exc:
            raise TTSError(f"could not load {self.model_id}: {exc}") from exc
        self.version = getattr(ptts, "__version__", "unknown")

    def settings(self) -> dict:
        return {"engine": self.name, "model": self.model_id, "quant": self.quant, "voice": self.voice,
                "seed": self.seed, "temperature": self.temperature, "sentence_silence": self.gap,
                "threads": self.threads, "ptts": self.version}

    def synth(self, sentences: list[str], out_path: Path):
        chunks = []
        with tempfile.TemporaryDirectory(prefix="phonon_") as td:
            part = Path(td) / "s.wav"
            for sentence in sentences:
                kw = {"voice": self.voice, "seed": self.seed}
                if self.temperature is not None:
                    kw["temperature"] = float(self.temperature)
                try:
                    self.tts.save(str(part), sentence, **kw)
                except Exception as exc:
                    raise TTSError(f"phonon failed on {sentence!r}: {exc}") from exc
                data, sr = read_pcm(part)
                chunks.append(data)
        return join_sentences(chunks, self.tts.sample_rate, self.gap, out_path)


class EdgeEngine:
    name = "edge-tts"

    def __init__(self, cfg: dict):
        try:
            import edge_tts  # noqa: F401
        except ImportError as exc:
            raise TTSError("edge-tts is not installed: pip install -r requirements.txt") from exc
        self.voice, self.rate, self.pitch, self.volume = cfg["voice"], cfg["rate"], cfg["pitch"], cfg["volume"]

    def settings(self) -> dict:
        return {"engine": self.name, "voice": self.voice, "rate": self.rate, "pitch": self.pitch, "volume": self.volume}

    def synth(self, sentences: list[str], out_path: Path):
        import edge_tts
        text = " ".join(sentences)

        async def _go() -> None:
            comm = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch, volume=self.volume)
            await comm.save(str(out_path))

        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                asyncio.run(_go())
                if out_path.exists() and out_path.stat().st_size > 1000:
                    return None          # whole-segment audio: sentence times are estimated later
                raise TTSError("edge-tts returned an empty file")
            except Exception as exc:  # network errors, NoAudioReceived, ...
                last_exc = exc
                if attempt == 3:
                    break
                wait = 2 ** attempt
                print(f"    edge-tts attempt {attempt + 1} failed ({exc.__class__.__name__}); retrying in {wait}s",
                      file=sys.stderr)
                time.sleep(wait)
        raise TTSError(f"edge-tts failed after 4 attempts: {last_exc}")


class PiperEngine:
    name = "piper"

    def __init__(self, cfg: dict, natural: bool, model_path: str | None):
        try:
            from piper import PiperVoice, SynthesisConfig  # noqa: F401
        except ImportError as exc:
            raise TTSError("piper-tts is not installed: pip install -r requirements.txt") from exc
        self.voice_name = cfg["voice"]
        self.length_scale = float(cfg["length_scale"])
        self.gap = float(cfg["sentence_silence"])
        self.natural = natural
        model = Path(model_path) if model_path else VOICES_DIR / f"{self.voice_name}.onnx"
        if not model.exists():
            print(f"  Piper voice not found at {model}; downloading {self.voice_name} ...")
            VOICES_DIR.mkdir(parents=True, exist_ok=True)
            run([sys.executable, "-m", "piper.download_voices", "--download-dir", str(VOICES_DIR), self.voice_name])
            model = VOICES_DIR / f"{self.voice_name}.onnx"
        if not model.exists():
            raise TTSError(f"Piper model missing: {model}")
        from piper import PiperVoice
        self.model = model
        self.voice = PiperVoice.load(str(model))

    def settings(self) -> dict:
        return {"engine": self.name, "voice": self.voice_name, "model_file": self.model.name,
                "model_sha256": sha256(self.model), "length_scale": self.length_scale, "sentence_silence": self.gap,
                "noise": "model-default (non-deterministic)" if self.natural else "0 (bit-exact)"}

    def synth(self, sentences: list[str], out_path: Path):
        from piper import SynthesisConfig
        cfg = (SynthesisConfig(length_scale=self.length_scale) if self.natural else
               SynthesisConfig(length_scale=self.length_scale, noise_scale=0.0, noise_w_scale=0.0))
        chunks = [b"".join(c.audio_int16_bytes for c in self.voice.synthesize(s, syn_config=cfg)) for s in sentences]
        return join_sentences(chunks, self.voice.config.sample_rate, self.gap, out_path)


def make_engine(kind: str, cfg: dict, args):
    if kind == "phonon":
        return PhononEngine(cfg["tts"]["phonon"])
    if kind == "edge":
        return EdgeEngine(cfg["tts"]["edge"])
    return PiperEngine(cfg["tts"]["piper"], args.piper_natural, args.piper_model)


# --------------------------------------------------------------------------- scene build
def cache_key(scene: dict, engine_settings: dict, audio_cfg: dict, pron: dict) -> str:
    blob = json.dumps({"scene": scene, "engine": engine_settings, "audio": audio_cfg, "pron": pron},
                      sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_scene(scene: dict, engine, cfg: dict, tmp: Path) -> dict:
    audio_cfg = cfg["audio"]
    sr = int(audio_cfg["sample_rate"])
    fps = int(cfg["video"]["fps"])
    lead = float(scene.get("lead_in_s", audio_cfg["lead_in_s"]))
    tail = float(scene.get("tail_s", audio_cfg["tail_s"]))
    pause = float(audio_cfg["pause_s"])
    tempo = float(audio_cfg.get("tempo", 1.0))
    pron = cfg.get("pronunciations", {})

    pcm = bytearray(silence(lead, sr))
    cursor = lead
    seg_timings = []
    segments = split_segments(scene["narration"])
    for i, seg_text in enumerate(segments):
        display = split_sentences(seg_text)
        spoken = [apply_pronunciations(s, pron) for s in display]
        raw, clean = tmp / f"{scene['id']}_{i:02d}.raw", tmp / f"{scene['id']}_{i:02d}.wav"
        spans = engine.synth(spoken, raw)
        to_pcm(raw, clean, sr, trim=spans is None, tempo=tempo)
        data, rate = read_pcm(clean)
        dur = len(data) / 2 / sr
        if spans is None:   # estimate sentence boundaries by character count
            total_chars = sum(len(s) for s in display)
            spans, acc = [], 0.0
            for s in display:
                d = dur * len(s) / total_chars
                spans.append((acc, acc + d))
                acc += d
            estimated = True
        else:
            spans = [(a / tempo, b / tempo) for a, b in spans]
            estimated = False
        seg_timings.append({
            "index": i, "start": round(cursor, 3), "end": round(cursor + dur, 3), "text": seg_text,
            "sentences": [{"start": round(cursor + a, 3), "end": round(cursor + b, 3), "text": s}
                          for (a, b), s in zip(spans, display)],
            "estimated": estimated})
        pcm += data
        cursor += dur
        if i < len(segments) - 1:
            pcm += silence(pause, sr)
            cursor += pause

    speech_end = cursor
    fixed = scene.get("duration", "auto")
    if fixed == "auto":
        slot = math.ceil((speech_end + tail) * fps - 1e-6) / fps   # whole video frames
    else:
        slot = float(fixed)
        if speech_end + 0.2 > slot:
            raise TTSError(f"Scene {scene['id']}: narration needs {speech_end + 0.2:.2f}s but the slot is {slot:.2f}s. "
                           f"Set 'duration' for {scene['id']} to \"auto\" or at least {int(speech_end + 0.2) + 1}.")
    total_samples = int(round(slot * sr))
    pcm += b"\x00\x00" * max(0, total_samples - len(pcm) // 2)
    write_pcm(AUDIO_DIR / f"{scene['id']}.wav", bytes(pcm[: total_samples * 2]), sr)
    return {"segments": seg_timings, "speech_end": round(speech_end, 3), "slot": round(slot, 6),
            "headroom_s": round(slot - speech_end, 3)}


def write_timeline(cfg: dict, timings: dict, path: Path) -> None:
    start = 0.0
    for s in cfg["scenes"]:
        t = timings[s["id"]]
        t["start"] = round(start, 6)
        start += t["slot"]
    out = {"title": cfg["title"], "fps": cfg["video"]["fps"], "total": round(start, 6),
           "scenes": {s["id"]: timings[s["id"]] for s in cfg["scenes"]}}
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), "utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["auto", "phonon", "edge", "piper"], default="auto")
    ap.add_argument("--force", action="store_true", help="regenerate even if cached")
    ap.add_argument("--only", default="", help="comma-separated scene ids, e.g. s03,s04")
    ap.add_argument("--config", default=str(CONFIG), help="scene config (default config/scenes.json)")
    ap.add_argument("--piper-model", default=None, help="path to a Piper .onnx voice")
    ap.add_argument("--piper-natural", action="store_true",
                    help="use Piper's default noise (more natural, NOT bit-reproducible)")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found on PATH", file=sys.stderr)
        return 1
    cfg = load_config(Path(args.config))
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    scenes = [s for s in cfg["scenes"] if not only or s["id"] in only]

    timings_path, manifest_path = AUDIO_DIR / "timings.json", AUDIO_DIR / "manifest.json"
    old = json.loads(timings_path.read_text("utf-8")) if timings_path.exists() else {}
    timings = dict(old.get("scenes", {}))
    manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {"scenes": {}}

    order = cfg["tts"].get("engine_order", ["phonon", "edge", "piper"]) if args.engine == "auto" else [args.engine]
    last_error: Exception | None = None
    for kind in order:
        try:
            engine = make_engine(kind, cfg, args)
        except TTSError as exc:
            print(f"[{kind}] unavailable: {exc}", file=sys.stderr)
            last_error = exc
            continue
        settings = engine.settings()
        print(f"Engine: {settings}")
        try:
            with tempfile.TemporaryDirectory(prefix="tts_") as td:
                for scene in scenes:
                    key = cache_key(scene, settings, {**cfg["audio"], "fps": cfg["video"]["fps"]}, cfg.get("pronunciations", {}))
                    out = AUDIO_DIR / f"{scene['id']}.wav"
                    prev = manifest["scenes"].get(scene["id"], {})
                    if (not args.force and out.exists() and prev.get("cache_key") == key
                            and prev.get("sha256") == sha256(out) and scene["id"] in timings):
                        print(f"  {scene['id']}: cached ({prev['sha256'][:12]})")
                        continue
                    print(f"  {scene['id']}: synthesizing ...")
                    timings[scene["id"]] = build_scene(scene, engine, cfg, Path(td))
                    manifest["scenes"][scene["id"]] = {"file": f"audio/{scene['id']}.wav", "cache_key": key,
                                                       "sha256": sha256(out), "engine": settings}
                    t = timings[scene["id"]]
                    words = len(scene["narration"].replace(PAUSE_TOKEN, " ").split())
                    talk = sum(x["end"] - x["start"] for g in t["segments"] for x in g["sentences"])
                    print(f"    speech ends {t['speech_end']:.2f}s, slot {t['slot']:.2f}s, "
                          f"{words / talk * 60:.0f} wpm while talking")
            missing = [s["id"] for s in cfg["scenes"] if s["id"] not in timings]
            if missing:
                print(f"NOTE: no audio yet for {missing}; run without --only to make the full timeline.")
                return 0
            write_timeline(cfg, timings, timings_path)
            manifest["title"] = cfg["title"]
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), "utf-8")
            total = sum(timings[s["id"]]["slot"] for s in cfg["scenes"])
            print(f"Done. {len(cfg['scenes'])} scenes, total {total:.2f}s ({int(total // 60)}:{total % 60:05.2f}).")
            return 0
        except TTSError as exc:
            last_error = exc
            if "slot is" in str(exc):  # timing problem: falling back would not help
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
            print(f"[{kind}] failed: {exc}", file=sys.stderr)
            if kind != order[-1]:
                print("Falling back to the next engine and regenerating ALL scenes so the voice is consistent.",
                      file=sys.stderr)
                scenes = cfg["scenes"]
                args.force = True
    print(f"ERROR: no TTS engine succeeded: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
