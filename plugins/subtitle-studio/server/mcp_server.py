# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mcp",
#   "faster-whisper>=1.0",
#   "pysubs2>=1.6",
# ]
# ///
"""subtitle-studio MCP server.

Local, credential-free subtitle tooling:

  * transcribe        video/audio -> subtitles, entirely on-device (faster-whisper)
  * convert_subtitle  between formats (SRT / VTT / ASS / ...)
  * shift_timing      nudge every cue earlier/later
  * fix_common_errors tidy a subtitle file
  * burn_in           hardcode subtitles into a video (needs ffmpeg)
  * probe_environment report what is available on this machine

Design notes
------------
* The heavy, deterministic work lives here. Language work (translating,
  summarising, chaptering the transcript) is left to the model that calls
  these tools — that is what the accompanying skill does.
* Nothing here needs the network or any credential. Whisper runs locally;
  faster-whisper decodes media through its bundled PyAV, so a plain
  ``uv``-only machine (no system ffmpeg) can still transcribe.
* SubtitleEdit is an *optional* power-up. When it is found (including a
  Windows install reached from WSL) it is used for the jobs it does best;
  otherwise pure-Python fallbacks cover the same ground.

The core operations are plain functions so they can be unit-tested without a
running MCP transport. Run ``uv run mcp_server.py --probe`` for a diagnostic,
or ``uv run mcp_server.py --transcribe path/to/media`` for a quick check.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

# --------------------------------------------------------------------------- #
# Environment detection                                                       #
# --------------------------------------------------------------------------- #

# Common install locations for SubtitleEdit's console-capable executable.
# On WSL the Windows Program Files trees are mounted under /mnt/<drive>.
_SE_GLOBS = [
    "/mnt/c/Program Files/Subtitle Edit/SubtitleEdit.exe",
    "/mnt/c/Program Files*/Subtitle Edit*/SubtitleEdit.exe",
    "/mnt/*/Program Files*/Subtitle Edit*/SubtitleEdit.exe",
]


def _is_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        with open("/proc/version", encoding="utf-8", errors="ignore") as fh:
            return "microsoft" in fh.read().lower()
    except OSError:
        return False


def find_subtitle_edit() -> Optional[str]:
    """Return a usable SubtitleEdit path, or None.

    Honours the SUBTITLE_EDIT_PATH override first, then a native `SubtitleEdit`
    on PATH (Linux/mono builds), then well-known Windows locations (WSL).
    """
    override = os.environ.get("SUBTITLE_EDIT_PATH")
    if override and os.path.isfile(override):
        return override

    for name in ("SubtitleEdit", "subtitleedit", "seconv"):
        found = shutil.which(name)
        if found:
            return found

    for pattern in _SE_GLOBS:
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def find_ffmpeg() -> Optional[str]:
    override = os.environ.get("FFMPEG_PATH")
    if override and os.path.isfile(override):
        return override
    found = shutil.which("ffmpeg")
    if found:
        return found
    # SubtitleEdit downloads its own ffmpeg on Windows; reachable from WSL.
    for pat in (
        "/mnt/*/Users/*/AppData/Roaming/Subtitle Edit/ffmpeg/ffmpeg.exe",
        "/mnt/c/ffmpeg/bin/ffmpeg.exe",
    ):
        matches = sorted(glob.glob(pat))
        if matches:
            return matches[0]
    return None


def cuda_device_count() -> int:
    """GPU count via CTranslate2 (a faster-whisper dependency). 0 on any error."""
    try:
        import ctranslate2  # type: ignore

        return int(ctranslate2.get_cuda_device_count())
    except Exception:
        return 0


def _to_windows_path(path: str) -> str:
    """Best-effort POSIX->Windows path for handing files to a Windows .exe."""
    try:
        out = subprocess.run(
            ["wslpath", "-w", path], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except Exception:
        return path


def _se_is_windows_exe(se_path: str) -> bool:
    return se_path.lower().endswith(".exe")


def probe_environment() -> dict[str, Any]:
    """Report what this machine can do, for setup guidance and tool routing."""
    se = find_subtitle_edit()
    ff = find_ffmpeg()
    gpus = cuda_device_count()
    try:
        import faster_whisper  # noqa: F401

        fw_ok = True
    except Exception as exc:  # pragma: no cover - only if deps failed to install
        fw_ok = False
        fw_err = str(exc)
    else:
        fw_err = None

    return {
        "faster_whisper_available": fw_ok,
        "faster_whisper_error": fw_err,
        "gpu_count": gpus,
        "recommended_device": "cuda" if gpus else "cpu",
        "recommended_compute_type": "float16" if gpus else "int8",
        "ffmpeg": ff,
        "ffmpeg_available": ff is not None,
        "subtitle_edit": se,
        "subtitle_edit_available": se is not None,
        "is_wsl": _is_wsl(),
        "cached_models": _cached_models(),
    }


def _cached_models() -> list[str]:
    """Whisper model ids already downloaded into the HF cache (best effort)."""
    home = os.path.expanduser("~")
    hub = os.path.join(home, ".cache", "huggingface", "hub")
    if not os.path.isdir(hub):
        return []
    out = []
    for name in os.listdir(hub):
        if "faster-whisper" in name or "whisper" in name.lower():
            out.append(name.replace("models--", "").replace("--", "/"))
    return sorted(out)


# --------------------------------------------------------------------------- #
# Subtitle building blocks (pysubs2)                                          #
# --------------------------------------------------------------------------- #


def _segments_to_ssa(segments: list[dict], include_words: bool = False):
    import pysubs2

    subs = pysubs2.SSAFile()
    for seg in segments:
        line = pysubs2.SSAEvent(
            start=int(round(seg["start"] * 1000)),
            end=int(round(seg["end"] * 1000)),
            text=seg["text"].strip(),
        )
        subs.append(line)
    return subs


def _write_outputs(
    segments: list[dict],
    base_no_ext: str,
    formats: list[str],
    full_text: str,
) -> dict[str, str]:
    """Write requested output files; return {format: path}."""
    written: dict[str, str] = {}
    subs = _segments_to_ssa(segments)
    for fmt in formats:
        fmt = fmt.lower().lstrip(".")
        if fmt in ("txt", "text"):
            path = f"{base_no_ext}.txt"
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(full_text.strip() + "\n")
            written["txt"] = path
        else:
            # pysubs2 knows srt, vtt, ass, ssa, sub, ... by extension.
            path = f"{base_no_ext}.{fmt}"
            subs.save(path)
            written[fmt] = path
    return written


# --------------------------------------------------------------------------- #
# Core operations                                                             #
# --------------------------------------------------------------------------- #


@dataclass
class TranscribeResult:
    source: str
    language: str
    language_probability: float
    duration: float
    device: str
    compute_type: str
    text: str
    segments: list[dict] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)


def do_transcribe(
    media_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
    task: str = "transcribe",
    word_timestamps: bool = False,
    formats: Optional[list[str]] = None,
    output_dir: Optional[str] = None,
    device: Optional[str] = None,
    compute_type: Optional[str] = None,
    vad_filter: bool = True,
) -> TranscribeResult:
    """Transcribe (or translate-to-English) media locally with faster-whisper."""
    from faster_whisper import WhisperModel

    if not os.path.isfile(media_path):
        raise FileNotFoundError(f"media not found: {media_path}")
    if task not in ("transcribe", "translate"):
        raise ValueError("task must be 'transcribe' or 'translate'")

    formats = formats or ["srt", "txt"]

    auto_device = device is None
    if device is None:
        device = "cuda" if cuda_device_count() else "cpu"
    if compute_type is None:
        compute_type = "float16" if device == "cuda" else "int8"

    def _run(dev: str, ctype: str):
        model = WhisperModel(model_size, device=dev, compute_type=ctype)
        seg_iter, info = model.transcribe(
            media_path,
            language=language,
            task=task,
            word_timestamps=word_timestamps,
            vad_filter=vad_filter,
        )
        # Force evaluation of the lazy generator here so that a CUDA runtime
        # failure surfaces now (while we can still fall back), not later.
        return list(seg_iter), info

    try:
        seg_list, info = _run(device, compute_type)
    except (RuntimeError, OSError) as exc:
        msg = str(exc).lower()
        cuda_lib_missing = any(
            tok in msg for tok in ("cublas", "cudnn", "cuda", "libcu", "gpu")
        )
        if device == "cuda" and auto_device and cuda_lib_missing:
            # The machine advertised a GPU but the CUDA runtime libraries are
            # absent — retry on CPU so transcription still works everywhere.
            device, compute_type = "cpu", "int8"
            seg_list, info = _run(device, compute_type)
        else:
            raise

    seg_iter = seg_list
    segments: list[dict] = []
    text_parts: list[str] = []
    for s in seg_iter:
        entry: dict[str, Any] = {
            "start": round(s.start, 3),
            "end": round(s.end, 3),
            "text": s.text.strip(),
        }
        if word_timestamps and s.words:
            entry["words"] = [
                {"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word}
                for w in s.words
            ]
        segments.append(entry)
        text_parts.append(s.text.strip())

    full_text = " ".join(text_parts).strip()

    out_dir = output_dir or os.path.dirname(os.path.abspath(media_path))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(media_path))[0]
    base_no_ext = os.path.join(out_dir, stem)
    outputs = _write_outputs(segments, base_no_ext, formats, full_text)

    return TranscribeResult(
        source=media_path,
        language=info.language,
        language_probability=round(info.language_probability, 3),
        duration=round(info.duration, 2),
        device=device,
        compute_type=compute_type,
        text=full_text,
        segments=segments,
        outputs=outputs,
    )


# How long to wait on the (experimental) SubtitleEdit CLI before giving up and
# falling back. Kept short: some SubtitleEdit builds (the Avalonia/Skia GUI
# rewrite) ignore the batch CLI and just open a window, which never returns.
_SE_TIMEOUT = 25
_SE_FMT = {
    "srt": "subrip",
    "vtt": "webvtt",
    "ass": "advancedsubstationalpha",
    "ssa": "substationalpha",
}


def _try_subtitle_edit(args: list[str], out: str) -> Optional[dict]:
    """Run a SubtitleEdit /convert-style command, returning a result dict on
    success or None if SubtitleEdit is unavailable / hangs / produces nothing.

    SubtitleEdit is treated as a best-effort optional accelerator only. It is
    never allowed to block: on timeout we kill it and let the caller fall back.
    """
    se = find_subtitle_edit()
    if not (se and _se_is_windows_exe(se)):
        return None
    try:
        proc = subprocess.run([se] + args, capture_output=True, text=True, timeout=_SE_TIMEOUT)
    except subprocess.TimeoutExpired:
        # GUI-only build: it opened a window instead of converting. Reap it.
        try:
            subprocess.run(
                ["/mnt/c/Windows/System32/cmd.exe", "/c", "taskkill", "/F", "/IM", "SubtitleEdit.exe"],
                capture_output=True,
                timeout=10,
            )
        except Exception:
            pass
        return None
    if os.path.isfile(out):
        return {"output": out, "engine": "subtitle-edit", "stderr": proc.stderr[-300:]}
    return None


def do_convert(
    input_path: str,
    to_format: str,
    output_path: Optional[str] = None,
    engine: str = "auto",
) -> dict:
    """Convert a subtitle file to another format.

    engine="auto"/"pysubs2" (default) uses pysubs2 — fast, reliable, and
    cross-platform, covering srt/vtt/ass/ssa/sub/... . engine="subtitle-edit"
    tries SubtitleEdit first (widest format support) and silently falls back to
    pysubs2 if it is missing or does not respond.
    """
    import pysubs2

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"subtitle not found: {input_path}")
    to_format = to_format.lower().lstrip(".")
    out = output_path or f"{os.path.splitext(input_path)[0]}.{to_format}"

    if engine == "subtitle-edit":
        result = _try_subtitle_edit(
            [
                "/convert",
                _to_windows_path(input_path),
                _SE_FMT.get(to_format, to_format),
                f"/outputfilename:{_to_windows_path(out)}",
            ],
            out,
        )
        if result:
            return result

    subs = pysubs2.load(input_path)
    subs.save(out)
    return {"output": out, "engine": "pysubs2"}


def do_shift(input_path: str, ms: int, output_path: Optional[str] = None) -> dict:
    """Shift every cue by `ms` milliseconds (positive = later)."""
    import pysubs2

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"subtitle not found: {input_path}")
    subs = pysubs2.load(input_path)
    subs.shift(ms=ms)
    out = output_path or input_path
    subs.save(out)
    return {"output": out, "shifted_ms": ms, "cues": len(subs)}


def do_fix_common_errors(
    input_path: str, output_path: Optional[str] = None, engine: str = "auto"
) -> dict:
    """Tidy a subtitle file.

    engine="auto" (default) applies a conservative pysubs2 cleanup: drop empty
    cues, fix zero/negative durations and overlaps, collapse internal
    whitespace. engine="subtitle-edit" tries SubtitleEdit's richer
    /fixcommonerrors pass first, falling back to the pysubs2 cleanup if it is
    missing or unresponsive.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"subtitle not found: {input_path}")
    out = output_path or input_path

    if engine == "subtitle-edit":
        ext = os.path.splitext(input_path)[1].lstrip(".") or "srt"
        result = _try_subtitle_edit(
            [
                "/convert",
                _to_windows_path(input_path),
                _SE_FMT.get(ext, "subrip"),
                "/fixcommonerrors",
                f"/outputfilename:{_to_windows_path(out)}",
            ],
            out,
        )
        if result:
            return result

    import pysubs2

    subs = pysubs2.load(input_path)
    cleaned = pysubs2.SSAFile()
    cleaned.styles = subs.styles
    prev_end = None
    dropped = 0
    for ev in sorted(subs, key=lambda e: e.start):
        text = " ".join(ev.text.split())
        if not text.strip():
            dropped += 1
            continue
        ev.text = text
        if ev.end <= ev.start:
            ev.end = ev.start + 1000  # 1s minimum
        if prev_end is not None and ev.start < prev_end:
            ev.start = prev_end
            if ev.end <= ev.start:
                ev.end = ev.start + 500
        prev_end = ev.end
        cleaned.append(ev)
    cleaned.save(out)
    return {"output": out, "engine": "pysubs2", "dropped_empty": dropped, "cues": len(cleaned)}


def do_burn_in(video_path: str, subtitle_path: str, output_path: Optional[str] = None) -> dict:
    """Hardcode subtitles into a video (requires ffmpeg)."""
    ff = find_ffmpeg()
    if not ff:
        raise RuntimeError(
            "burn_in needs ffmpeg, which was not found. Install ffmpeg or set FFMPEG_PATH."
        )
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"video not found: {video_path}")
    if not os.path.isfile(subtitle_path):
        raise FileNotFoundError(f"subtitle not found: {subtitle_path}")
    stem, ext = os.path.splitext(video_path)
    out = output_path or f"{stem}.subtitled{ext or '.mp4'}"
    # Escape the subtitle path for ffmpeg's filter argument.
    sub_arg = subtitle_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    cmd = [ff, "-y", "-i", video_path, "-vf", f"subtitles='{sub_arg}'", "-c:a", "copy", out]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.isfile(out):
        raise RuntimeError(f"ffmpeg failed: {proc.stderr[-800:]}")
    return {"output": out, "engine": "ffmpeg"}


# --------------------------------------------------------------------------- #
# MCP surface                                                                 #
# --------------------------------------------------------------------------- #


def _build_mcp():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("subtitle-studio")

    @mcp.tool()
    def probe_environment_tool() -> str:
        """Report local capabilities: GPU, ffmpeg, SubtitleEdit, cached Whisper models.

        Call this first on a new machine to decide model size / device and to
        tell the user what optional power-ups are available."""
        return json.dumps(probe_environment(), indent=2)

    @mcp.tool()
    def transcribe(
        media_path: str,
        model_size: str = "base",
        language: Optional[str] = None,
        task: str = "transcribe",
        word_timestamps: bool = False,
        formats: Optional[list[str]] = None,
        output_dir: Optional[str] = None,
    ) -> str:
        """Transcribe a local video/audio file to subtitles, entirely on-device.

        model_size: tiny|base|small|medium|large-v3 (bigger = better + slower).
        language:   ISO code (e.g. "en", "es") or None to auto-detect.
        task:       "transcribe" (same language) or "translate" (to English).
        word_timestamps: include per-word timings in the returned segments.
        formats:    subset of ["srt","vtt","ass","txt"] to write (default srt+txt).
        output_dir: where to write files (default: next to the source).

        Returns JSON with detected language, duration, the full text, segments,
        and the paths of the files written. Do language work (translation to
        other languages, summaries, chapters) yourself on the returned text."""
        res = do_transcribe(
            media_path=media_path,
            model_size=model_size,
            language=language,
            task=task,
            word_timestamps=word_timestamps,
            formats=formats,
            output_dir=output_dir,
        )
        return json.dumps(res.__dict__, indent=2)

    @mcp.tool()
    def convert_subtitle(
        input_path: str,
        to_format: str,
        output_path: Optional[str] = None,
        engine: str = "auto",
    ) -> str:
        """Convert a subtitle file to another format (srt/vtt/ass/ssa/...).

        engine="auto" (default) uses the built-in pysubs2 engine — reliable and
        cross-platform. engine="subtitle-edit" tries a detected SubtitleEdit
        install first (widest format coverage) and falls back automatically."""
        return json.dumps(do_convert(input_path, to_format, output_path, engine), indent=2)

    @mcp.tool()
    def shift_timing(input_path: str, ms: int, output_path: Optional[str] = None) -> str:
        """Shift every cue by `ms` milliseconds (positive = later, negative = earlier)."""
        return json.dumps(do_shift(input_path, ms, output_path), indent=2)

    @mcp.tool()
    def fix_common_errors(
        input_path: str, output_path: Optional[str] = None, engine: str = "auto"
    ) -> str:
        """Clean up a subtitle file: drop empty cues, fix overlaps/durations, tidy whitespace.

        engine="auto" (default) uses the built-in pysubs2 cleanup.
        engine="subtitle-edit" tries SubtitleEdit's richer pass first, then falls back."""
        return json.dumps(do_fix_common_errors(input_path, output_path, engine), indent=2)

    @mcp.tool()
    def burn_in(video_path: str, subtitle_path: str, output_path: Optional[str] = None) -> str:
        """Hardcode (burn) subtitles into a video. Requires ffmpeg."""
        return json.dumps(do_burn_in(video_path, subtitle_path, output_path), indent=2)

    return mcp


# --------------------------------------------------------------------------- #
# Entry point / self-test CLI                                                 #
# --------------------------------------------------------------------------- #


def _cli(argv: list[str]) -> int:
    if "--probe" in argv:
        print(json.dumps(probe_environment(), indent=2))
        return 0
    if "--transcribe" in argv:
        i = argv.index("--transcribe")
        try:
            media = argv[i + 1]
        except IndexError:
            print("usage: mcp_server.py --transcribe <media> [model_size]", file=sys.stderr)
            return 2
        model = argv[i + 2] if len(argv) > i + 2 and not argv[i + 2].startswith("-") else "tiny"
        res = do_transcribe(media, model_size=model, formats=["srt", "txt"])
        print(json.dumps(res.__dict__, indent=2))
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].startswith("--"):
        raise SystemExit(_cli(sys.argv[1:]))
    _build_mcp().run()
