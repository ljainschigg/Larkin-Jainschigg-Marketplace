# subtitle-studio

A Claude Code plugin that turns local video and audio into subtitles and transcripts — entirely **on your machine**. Transcription runs through Whisper (`faster-whisper`); nothing is uploaded and no API key is required.

- Transcribes video/audio to SRT, WebVTT, ASS, or plain text, on-device
- Converts between subtitle formats
- Shifts/resyncs cue timing by any offset
- Fixes common subtitle errors (empty cues, overlaps, bad durations, whitespace)
- Burns subtitles into a video as hardcoded captions (needs ffmpeg)
- Hands the transcript back to Claude for the language work — translation into any language, summaries, and chapter markers

A Python MCP server does the deterministic heavy lifting (speech-to-text and subtitle-file mechanics); Claude does the language work on the transcript it gets back.

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** — the only hard requirement. It manages Python and installs the server's dependencies automatically on first run (no `pip install`).

Optional power-ups, auto-detected if present:

- **A CUDA GPU + CUDA runtime libraries** — a big speed-up. Without the CUDA libraries the server automatically falls back to CPU (still fully functional).
- **[ffmpeg](https://ffmpeg.org/)** — only needed for `burn_in`. Transcription does not need it; Whisper decodes media through its bundled PyAV.
- **[SubtitleEdit](https://www.nikse.dk/subtitleedit)** — an *optional* alternative engine for format conversion and error-fixing. Off by default (several builds ignore the batch CLI and open a window); the tools guard against a hang and fall back to the built-in engine, so it can only ever add capability, never block.

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install subtitle-studio@Larkin-Jainschigg-Marketplace
```

There is no separate setup step — `uv` installs the server's dependencies on first use, and the first transcription downloads the chosen Whisper model (cached thereafter).

## Use

Just ask, in plain language:

- *"Transcribe `~/videos/talk.mp4` and give me an SRT and a plain-text version."*
- *"Make Spanish subtitles for this interview."* (transcribes, then Claude translates)
- *"Convert these subtitles to WebVTT."*
- *"The captions are 2 seconds early — shift them."*
- *"Summarise this video from its transcript and give me chapter markers."*
- *"Burn the subtitles into the video."* (needs ffmpeg)

Claude checks your environment on the first request, picks sensible defaults, and tells you whether it's using the GPU or CPU.

### Diagnostics

You can run the server's self-test directly to see what your machine can do:

```
uv run <plugin-dir>/server/mcp_server.py --probe
uv run <plugin-dir>/server/mcp_server.py --transcribe path/to/media.mp4 tiny
```

## What works everywhere vs. power-ups

| Capability | Everywhere (uv only) | With a power-up |
|---|---|---|
| Transcription (SRT/VTT/ASS/TXT) | ✅ CPU | ⚡ Faster on a working CUDA GPU |
| Format conversion | ✅ pysubs2 | SubtitleEdit engine (opt-in) |
| Timing shift / resync | ✅ pysubs2 | — |
| Fix common errors | ✅ pysubs2 cleanup | SubtitleEdit `/fixcommonerrors` (opt-in) |
| Translate / summarise / chapter | ✅ Claude, on the transcript | — |
| Burn-in (hardcode captions) | — | ✅ Needs ffmpeg |

## How it works

On install, the MCP server starts alongside Claude Code (`uv run`, launched from `.mcp.json`). It exposes six tools:

| Tool | Purpose |
|---|---|
| `probe_environment_tool` | Report GPU/CPU, ffmpeg, SubtitleEdit, cached models |
| `transcribe` | Media → subtitles/transcript, on-device (faster-whisper) |
| `convert_subtitle` | Convert between subtitle formats |
| `shift_timing` | Offset every cue by N milliseconds |
| `fix_common_errors` | Tidy a subtitle file |
| `burn_in` | Hardcode subtitles into a video (ffmpeg) |

Dependencies (`mcp`, `faster-whisper`, `pysubs2`) are declared inline in the server script using [PEP 723](https://peps.python.org/pep-0723/) and installed automatically by `uv` on first run.

## Details

| | |
|---|---|
| **Version** | 0.2.7 |
| **Type** | skill (MCP-backed, credential-free, fully local) |
| **Runtime** | Python via `uv` |
| **Core dependencies** | `mcp`, `faster-whisper`, `pysubs2` |
| **Optional** | CUDA GPU, ffmpeg (burn-in), SubtitleEdit (opt-in engine) |
| **Maintained by** | Claude Plugins Marketplace |
