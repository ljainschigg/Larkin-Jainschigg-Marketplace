---
name: setup
description: One-time setup check for subtitle-studio. Run this after installing the plugin.
---

Run the following checks in order. Report the result of each step clearly. Stop and report if a required step fails — do not proceed past it. Optional power-ups that are missing are not failures; just note them.

## Step 1 — Check `uv`

!`uv --version 2>&1 || true`

`uv` is the only hard requirement — it manages Python and installs the server's dependencies automatically on first run. If not found, stop and tell the user to install it from https://docs.astral.sh/uv/ before continuing.

## Step 2 — Probe the environment

Call the `probe_environment_tool` MCP tool (no arguments). This is the server's own self-test — it reports GPU/CUDA availability, whether `ffmpeg` is on PATH, whether SubtitleEdit is detected, and which Whisper models are already cached.

If the tool responds, report its findings to the user in plain language: which engine transcription will use (GPU or CPU), whether burn-in is available (needs `ffmpeg`), and whether the optional SubtitleEdit engine was detected.

If the tool is not available at all (not just an empty/error result), tell the user:

> The subtitle-studio MCP server is not responding. It's configured in `.mcp.json` and starts automatically when Claude Code loads the plugin. Try restarting Claude Code. If it still fails, check that `uv` is on your PATH and that Step 1 passed.

## Done

If Step 1 passed, tell the user:

> Setup complete. Transcription will run on **[GPU/CPU, from the probe]**. Burn-in is **[available/unavailable — needs ffmpeg]**. SubtitleEdit power-ups are **[on/off]**.
>
> Just describe what you want in plain language, e.g.: "Transcribe ~/videos/talk.mp4 and give me an SRT."
