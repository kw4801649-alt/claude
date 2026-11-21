#!/usr/bin/env python3
"""
tools/tts.py -- Generate one narration WAV per scene for "How El Niño Forms".

Primary engine : Phonon 31M via `ptts` (Apache-2.0 open weights, offline, CPU, seeded = bit-exact)
Fallback 1     : edge-tts (free Microsoft Edge online voices, no API key)
Fallback 2     : Piper TTS (fully offline, open source)

Output (all paths relative to the project root):
    audio/s01.wav ... audio/s10.wav   48 kHz, mono, 16-bit PCM. Each file is padded
                                      with silence to EXACTLY its scene's slot length
                                      from config/scenes.json, so the video timeline
                                      never depends on how fast the voice speaks.
    audio/timings.json                speech-segment start/end times per scene
                                      (used by tools/build_srt.py)
    audio/manifest.json               engine, voice, settings, cache key, SHA-256

Every scene is built as:
    [lead-in silence] segment 1 [pause] segment 2 [pause] ... [silence to slot end]
where segments are the narration split at each [PAUSE] marker.

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


class TTSError(RuntimeError):
    pass


# --------------------------------------------------------------------------- helpers
def load_config(path: Path = CONFIG) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def split_segments(narration: str) -> list[str]:
    parts = [p.strip() for p in narration.split(PAUSE_TOKEN)]
    return [p for p in parts if p]


def apply_pronunciations(text: str, pron: dict[str, str]) -> str:
    """Replace display spellings with TTS-friendly spellings (whole words only)."""
    for key in sorted(pron, key=len, reverse=True):
        pattern = r"(?<![\w])" + re.escape(key) + r"(?![\w])"
        text = re.sub(pattern, pron[key], text)
    return text


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise TTSError(f"Command failed: {' '.join(cmd)}\n{proc.stderr[-2000:]}")


def to_clean_pcm(src: Path, dst: Path, sample_rate: int) -> None:
    """Decode any audio file to mono 16-bit PCM WAV at sample_rate and trim the
    leading/trailing silence the TTS engine adds, so pauses are fully controlled."""
    trim = (
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,"
        "areverse,"
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,"
        "areverse"
    )
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
        "-af", trim, "-ac", "1", "-ar", str(sample_rate), "-c:a", "pcm_s16le",
        "-fflags", "+bitexact", "-flags:a", "+bitexact", str(dst),
    ])


def read_pcm(path: Path) -> tuple[bytes, int]:
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise TTSError(f"{path} is not mono 16-bit PCM")
        return w.readframes(w.getnframes()), w.getframerate()


def silence(seconds: float, sample_rate: int) -> bytes:
    return b"\x00\x00" * int(round(seconds * sample_rate))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- engines
class EdgeEngine:
    name = "edge-tts"

    def __init__(self, cfg: dict):
        try:
            import edge_tts  # noqa: F401
        except ImportError as exc:
            raise TTSError("edge-tts is not installed: pip install -r requirements.txt") from exc
        self.voice = cfg["voice"]
        self.rate = cfg["rate"]
        self.pitch = cfg["pitch"]
        self.volume = cfg["volume"]

    def settings(self) -> dict:
        return {"engine": self.name, "voice": self.voice, "rate": self.rate,
                "pitch": self.pitch, "volume": self.volume}

    def synth(self, text: str, out_path: Path) -> None:
        import edge_tts

        async def _go() -> None:
            comm = edge_tts.Communicate(text, self.voice, rate=self.rate,
                                        pitch=self.pitch, volume=self.volume)
            await comm.save(str(out_path))

        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                asyncio.run(_go())
                if out_path.exists() and out_path.stat().st_size > 1000:
                    return
                raise TTSError("edge-tts returned an empty file")
            except Exception as exc:  # network errors, NoAudioReceived, ...
                last_exc = exc
                if attempt == 3:
                    break
                wait = 2 ** attempt
                print(f"    edge-tts attempt {attempt + 1} failed ({exc.__class__.__name__}); "
                      f"retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
        raise TTSError(f"edge-tts failed after 4 attempts: {last_exc}")


class PhononEngine:
    """Phonon 31M (gradium/phonon-31m-en), run by the `ptts` runtime.

    Each sentence is synthesized separately with a fixed seed and joined with a fixed
    gap, which gives a calm documentary pace. With a fixed seed and one CPU thread the
    output is byte-identical on every run.
    """
    name = "phonon"

    def __init__(self, cfg: dict):
        try:
            import ptts
        except ImportError as exc:
            raise TTSError("ptts is not installed: pip install -r requirements.txt") from exc
        self.model_id = cfg["model"]
        self.quant = cfg["quant"]
        self.voice = cfg["voice"]
        self.seed = int(cfg["seed"])
        self.temperature = cfg.get("temperature")
        self.sentence_silence = float(cfg["sentence_silence"])
        # Multi-threaded float reductions change the last bits between runs; one thread
        # makes Phonon byte-for-byte reproducible (the whole narration still takes ~2 min).
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
                "seed": self.seed, "temperature": self.temperature,
                "sentence_silence": self.sentence_silence, "threads": self.threads, "ptts": self.version}

    def synth(self, text: str, out_path: Path) -> None:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        sr = self.tts.sample_rate
        gap = b"\x00\x00" * int(round(self.sentence_silence * sr))
        frames = bytearray()
        with tempfile.TemporaryDirectory(prefix="phonon_") as td:
            part = Path(td) / "s.wav"
            for i, sentence in enumerate(sentences):
                kw = {"voice": self.voice, "seed": self.seed}
                if self.temperature is not None:
                    kw["temperature"] = float(self.temperature)
                try:
                    self.tts.save(str(part), sentence, **kw)
                except Exception as exc:
                    raise TTSError(f"phonon failed on {sentence!r}: {exc}") from exc
                with wave.open(str(part), "rb") as w:
                    if w.getframerate() != sr or w.getsampwidth() != 2 or w.getnchannels() != 1:
                        raise TTSError("unexpected WAV format from ptts")
                    frames += w.readframes(w.getnframes())
                if i < len(sentences) - 1:
                    frames += gap
        with wave.open(str(out_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(bytes(frames))


class PiperEngine:
    name = "piper"

    def __init__(self, cfg: dict, natural: bool, model_path: str | None):
        try:
            from piper import PiperVoice, SynthesisConfig  # noqa: F401
        except ImportError as exc:
            raise TTSError("piper-tts is not installed: pip install -r requirements.txt") from exc
        self.voice_name = cfg["voice"]
        self.length_scale = float(cfg["length_scale"])
        self.sentence_silence = float(cfg["sentence_silence"])
        self.natural = natural
        model = Path(model_path) if model_path else VOICES_DIR / f"{self.voice_name}.onnx"
        if not model.exists():
            print(f"  Piper voice not found at {model}; downloading {self.voice_name} ...")
            VOICES_DIR.mkdir(parents=True, exist_ok=True)
            run([sys.executable, "-m", "piper.download_voices",
                 "--download-dir", str(VOICES_DIR), self.voice_name])
            model = VOICES_DIR / f"{self.voice_name}.onnx"
        if not model.exists():
            raise TTSError(f"Piper model missing: {model}")
        from piper import PiperVoice
        self.model = model
        self.voice = PiperVoice.load(str(model))

    def settings(self) -> dict:
        return {"engine": self.name, "voice": self.voice_name, "model_file": self.model.name,
                "model_sha256": sha256(self.model), "length_scale": self.length_scale,
                "sentence_silence": self.sentence_silence,
                "noise": "model-default (non-deterministic)" if self.natural else "0 (bit-exact)"}

    def synth(self, text: str, out_path: Path) -> None:
        from piper import SynthesisConfig
        if self.natural:
            cfg = SynthesisConfig(length_scale=self.length_scale)
        else:
            # noise_scale = noise_w_scale = 0 makes Piper bit-for-bit reproducible.
            cfg = SynthesisConfig(length_scale=self.length_scale, noise_scale=0.0, noise_w_scale=0.0)
        sr = self.voice.config.sample_rate
        gap = b"\x00\x00" * int(round(self.sentence_silence * sr))
        frames = bytearray()
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        for i, sentence in enumerate(sentences):
            for chunk in self.voice.synthesize(sentence, syn_config=cfg):
                frames += chunk.audio_int16_bytes
            if i < len(sentences) - 1:
                frames += gap
        with wave.open(str(out_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(bytes(frames))


# --------------------------------------------------------------------------- main build
def cache_key(scene: dict, engine_settings: dict, audio_cfg: dict, pron: dict) -> str:
    blob = json.dumps({"scene": scene, "engine": engine_settings, "audio": audio_cfg,
                       "pron": pron}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_scene(scene: dict, engine, cfg: dict, tmp: Path) -> dict:
    audio_cfg = cfg["audio"]
    sr = int(audio_cfg["sample_rate"])
    lead = float(audio_cfg["lead_in_s"])
    pause = float(audio_cfg["pause_s"])
    min_tail = float(audio_cfg["min_tail_s"])
    slot = float(scene["duration"])

    segments = split_segments(scene["narration"])
    pcm = bytearray(silence(lead, sr))
    cursor = lead
    seg_timings = []
    for i, seg_text in enumerate(segments):
        spoken = apply_pronunciations(seg_text, cfg.get("pronunciations", {}))
        raw = tmp / f"{scene['id']}_{i:02d}.raw"
        clean = tmp / f"{scene['id']}_{i:02d}.wav"
        engine.synth(spoken, raw)
        to_clean_pcm(raw, clean, sr)
        data, rate = read_pcm(clean)
        assert rate == sr
        dur = len(data) / 2 / sr
        seg_timings.append({"index": i, "start": round(cursor, 3),
                            "end": round(cursor + dur, 3), "text": seg_text})
        pcm += data
        cursor += dur
        if i < len(segments) - 1:
            pcm += silence(pause, sr)
            cursor += pause

    speech_end = cursor
    if speech_end + min_tail > slot:
        need = speech_end + min_tail
        raise TTSError(
            f"Scene {scene['id']}: narration needs {need:.2f}s but the slot is {slot:.2f}s. "
            f"Increase 'duration' for {scene['id']} in config/scenes.json to at least "
            f"{int(need) + 1} (or use a faster rate).")
    total_samples = int(round(slot * sr))
    pcm += b"\x00\x00" * (total_samples - len(pcm) // 2)
    pcm = pcm[: total_samples * 2]

    out = AUDIO_DIR / f"{scene['id']}.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(pcm))
    return {"segments": seg_timings, "speech_end": round(speech_end, 3),
            "slot": slot, "headroom_s": round(slot - speech_end, 3)}


def make_engine(kind: str, cfg: dict, args):
    if kind == "phonon":
        return PhononEngine(cfg["tts"]["phonon"])
    if kind == "edge":
        return EdgeEngine(cfg["tts"]["edge"])
    return PiperEngine(cfg["tts"]["piper"], args.piper_natural, args.piper_model)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["auto", "phonon", "edge", "piper"], default="auto")
    ap.add_argument("--force", action="store_true", help="regenerate even if cached")
    ap.add_argument("--only", default="", help="comma-separated scene ids, e.g. s03,s04")
    ap.add_argument("--piper-model", default=None, help="path to a Piper .onnx voice")
    ap.add_argument("--config", default=str(CONFIG), help="scene config (default config/scenes.json)")
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

    timings_path = AUDIO_DIR / "timings.json"
    manifest_path = AUDIO_DIR / "manifest.json"
    timings = json.loads(timings_path.read_text("utf-8")) if timings_path.exists() else {}
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
            with tempfile.TemporaryDirectory(prefix="elnino_tts_") as td:
                for scene in scenes:
                    key = cache_key(scene, settings, cfg["audio"], cfg.get("pronunciations", {}))
                    out = AUDIO_DIR / f"{scene['id']}.wav"
                    prev = manifest["scenes"].get(scene["id"], {})
                    if (not args.force and out.exists() and prev.get("cache_key") == key
                            and prev.get("sha256") == sha256(out) and scene["id"] in timings):
                        print(f"  {scene['id']}: cached ({prev['sha256'][:12]})")
                        continue
                    print(f"  {scene['id']}: synthesizing ...")
                    timings[scene["id"]] = build_scene(scene, engine, cfg, Path(td))
                    manifest["scenes"][scene["id"]] = {
                        "file": f"audio/{scene['id']}.wav", "cache_key": key,
                        "sha256": sha256(out), "engine": settings}
                    t = timings[scene["id"]]
                    print(f"    speech {t['speech_end']:.2f}s / slot {t['slot']:.0f}s "
                          f"(headroom {t['headroom_s']:.2f}s)")
            timings_path.write_text(json.dumps(timings, indent=2, ensure_ascii=False), "utf-8")
            manifest["title"] = cfg["title"]
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), "utf-8")
            total = sum(s["duration"] for s in cfg["scenes"])
            print(f"Done. {len(cfg['scenes'])} scene slots, total {total}s "
                  f"({int(total // 60)}:{int(total % 60):02d}).")
            return 0
        except TTSError as exc:
            last_error = exc
            if "slot is" in str(exc):  # timing problem: falling back would not help
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
            print(f"[{kind}] failed: {exc}", file=sys.stderr)
            if kind != order[-1]:
                print("Falling back to the next engine and regenerating ALL scenes so the voice "
                      "is consistent.", file=sys.stderr)
                scenes = cfg["scenes"]
                args.force = True
    print(f"ERROR: no TTS engine succeeded: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
