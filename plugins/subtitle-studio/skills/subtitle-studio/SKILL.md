---
name: subtitle-studio
description: Transcribe video/audio to subtitles locally with Whisper, then convert, resync, clean, translate, summarise, or burn in captions. Use whenever the user wants a transcript or subtitles from a media file, or wants to manipulate an existing subtitle file. All transcription runs on-device — no upload, no API key.
---

# subtitle-studio

Turn local video/audio into subtitles and transcripts, then shape them however
the user needs. Transcription runs entirely on the user's machine via Whisper
(`faster-whisper`) — nothing is uploaded and no credentials are required.

The MCP server does the deterministic heavy lifting (speech-to-text and
subtitle-file mechanics). **You** do the language work — translating into other
languages, summarising, writing chapter markers — by operating on the transcript
text the tools return.

**Keep transcripts out of git.** A transcript is the user's personal data (someone's speech). When you write a transcript or subtitle file to a path that sits inside a git repository, ensure it's `.gitignore`d (create or append `.gitignore` for that file/pattern) and never `git add`/commit it unless the user explicitly asks.

## Tools

| Tool | What it does |
|---|---|
| `probe_environment_tool` | Reports GPU/CPU, ffmpeg, SubtitleEdit, cached models |
| `transcribe` | Media → segments + SRT/VTT/ASS/TXT, on-device |
| `convert_subtitle` | Between subtitle formats |
| `shift_timing` | Nudge every cue earlier/later by N ms |
| `fix_common_errors` | Drop empty cues, fix overlaps/durations, tidy whitespace |
| `burn_in` | Hardcode subtitles into a video (needs ffmpeg) |

## Workflow

1. **On the first request in a session, call `probe_environment_tool`.** Use it to:
   - Tell the user whether transcription will use the GPU or CPU. If
     `gpu_count > 0` but you later see the result come back with `"device":
     "cpu"`, that's the automatic fallback kicking in because the CUDA runtime
     libraries aren't installed — mention it once; it still works, just slower.
   - Note whether `ffmpeg` is available (required only for `burn_in`).
   - `subtitle_edit` being present is informational only (see note below).

2. **Transcribe.** Call `transcribe` with the media path. Guidance:
   - `model_size`: default `base` is a good balance. Recommend `small` or
     `medium` when accuracy matters (names, jargon, accents); `tiny` only for a
     quick rough pass. `large-v3` is best but slow on CPU.
   - Leave `language` unset to auto-detect; set it (e.g. `"en"`) if the user
     knows it — it's faster and more accurate.
   - `task="translate"` transcribes **into English** regardless of source
     language. For any *other* target language, transcribe normally and then
     translate the text yourself (step 4).
   - Set `word_timestamps=true` only if the user wants karaoke/word-level timing.
   - `formats` defaults to `["srt","txt"]`. Add `"vtt"` for web, `"ass"` for
     styled subtitles.
   - Report the detected language, duration, where files were written, and offer
     the transcript text back.

3. **Shape the subtitle file** as asked: `convert_subtitle` (e.g. SRT→VTT),
   `shift_timing` (sync fixes), `fix_common_errors` (cleanup), `burn_in`
   (hardcode into the video).

4. **Language tasks are yours, not the server's.** When the user wants a
   translation into (say) Spanish, a summary, a bulleted digest, or chapter
   markers, work directly on the returned transcript text / segments and write
   the result. To produce a *translated subtitle file*, translate each segment's
   text yourself while preserving its timings, then hand the segments to a new
   SRT/VTT (you can build it by writing the file directly, or ask the user which
   format they want).

## Notes

- **Long media is slow on CPU.** A rough rule on CPU with `base`: transcription
  takes a noticeable fraction of real-time. For a long file, tell the user it
  will take a while, or suggest a smaller model. On a working GPU it's much
  faster.
- **SubtitleEdit is an optional accelerator, not a dependency.** If the user has
  a SubtitleEdit install that supports the batch CLI, `convert_subtitle` and
  `fix_common_errors` accept `engine="subtitle-edit"` to use it. It is *not* the
  default because several SubtitleEdit builds (notably the newer Avalonia GUI
  rewrite) ignore the CLI and just open a window; the tools detect a hang, kill
  it, and fall back to the built-in engine. Only reach for it if the user
  specifically asks and reports it working.
- **Paths**: pass real filesystem paths the server can see. On WSL that means a
  Linux path (`/home/...` or `/mnt/c/...`), not a Windows `C:\...` path.
