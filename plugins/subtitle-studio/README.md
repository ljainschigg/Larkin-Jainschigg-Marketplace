# subtitle-studio

Transcribe video and audio to subtitles **locally** with Whisper, then convert,
resync, clean up, translate, summarise, or burn captions into the video —
straight from a Claude Code session. Transcription runs entirely on your
machine: no upload, no API key, no cloud.

A Python MCP server does the deterministic heavy lifting (speech-to-text and
subtitle-file mechanics); Claude handles the language work (translating into any
language, summaries, chapter markers) on the transcript it gets back.

---

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** — the only hard requirement. It manages
  Python and installs the server's dependencies automatically on first run (no
  `pip install`).

Optional power-ups, auto-detected if present:

- **A CUDA GPU + CUDA runtime libraries** — big speed-up. Without the CUDA
  libraries the server automatically falls back to CPU (still fully functional).
- **[ffmpeg](https://ffmpeg.org/)** — only needed for `burn_in` (hardcoding
  subtitles into a video). Not needed for transcription: Whisper decodes media
  through its bundled PyAV.
- **[SubtitleEdit](https://www.nikse.dk/subtitleedit)** — an *optional*
  alternative engine for format conversion and error-fixing. See the note below.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install subtitle-studio@lj-marketplace
```

After installing, run setup to confirm `uv` is present and see what your machine can do:

```
/setup
```

---

## Use

Just ask, in plain language:

- *"Transcribe `~/videos/talk.mp4` and give me an SRT and a plain-text version."*
- *"Make Spanish subtitles for this interview."* (transcribes, then Claude translates)
- *"Convert these subtitles to WebVTT."*
- *"The captions are 2 seconds early — shift them."*
- *"Summarise this video from its transcript and give me chapter markers."*
- *"Burn the subtitles into the video."* (needs ffmpeg)

Claude checks your environment on the first request, picks sensible defaults,
and tells you whether it's using the GPU or CPU.

### Diagnostics

You can run the server's self-test directly to see what your machine can do:

```
uv run <plugin-dir>/server/mcp_server.py --probe
uv run <plugin-dir>/server/mcp_server.py --transcribe path/to/media.mp4 tiny
```

---

## What works everywhere vs. power-ups

| Capability | Everywhere (uv only) | With a power-up |
|---|---|---|
| Transcription (SRT/VTT/ASS/TXT) | ✅ CPU | ⚡ Faster on a working CUDA GPU |
| Format conversion | ✅ pysubs2 | SubtitleEdit engine (opt-in) |
| Timing shift / resync | ✅ pysubs2 | — |
| Fix common errors | ✅ pysubs2 cleanup | SubtitleEdit `/fixcommonerrors` (opt-in) |
| Translate / summarise / chapter | ✅ Claude, on the transcript | — |
| Burn-in (hardcode captions) | — | ✅ Needs ffmpeg |

### A note on SubtitleEdit

The plugin detects SubtitleEdit and can use it for conversion and error-fixing
via `engine="subtitle-edit"`, but this is **off by default**. Several
SubtitleEdit builds — notably the newer Avalonia/Skia GUI rewrite — ignore the
batch command line and simply open a window, which would hang a headless call.
The tools guard against that (short timeout → fall back to the built-in engine),
so SubtitleEdit can only ever *add* capability, never block. The built-in
`pysubs2`/`ffmpeg` engines cover the common needs reliably and cross-platform.

---

## How it works

On install, the MCP server starts alongside Claude Code (`uv run`, launched from
`.mcp.json`). It exposes six tools:

| Tool | Purpose |
|---|---|
| `probe_environment_tool` | Report GPU/CPU, ffmpeg, SubtitleEdit, cached models |
| `transcribe` | Media → subtitles/transcript, on-device (faster-whisper) |
| `convert_subtitle` | Convert between subtitle formats |
| `shift_timing` | Offset every cue by N milliseconds |
| `fix_common_errors` | Tidy a subtitle file |
| `burn_in` | Hardcode subtitles into a video (ffmpeg) |

Dependencies (`mcp`, `faster-whisper`, `pysubs2`) are declared inline in the
server script using [PEP 723](https://peps.python.org/pep-0723/) and installed
automatically by `uv` on first run. The first transcription also downloads the
chosen Whisper model (cached thereafter).

---

## Details

| | |
|---|---|
| **Version** | 0.2.6 |
| **Type** | skill (MCP-backed, credential-free, fully local) |
| **Runtime** | Python via `uv` |
| **Core dependencies** | `mcp`, `faster-whisper`, `pysubs2` |
| **Optional** | CUDA GPU, ffmpeg (burn-in), SubtitleEdit (opt-in engine) |
| **Maintained by** | Claude Plugins Marketplace |
