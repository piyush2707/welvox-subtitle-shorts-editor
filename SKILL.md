---
name: welvox-subtitle-shorts-editor
description: Turn a long video or transcript into ranked, captioned vertical (9:16) shorts for Reels, TikTok and YouTube Shorts. Finds the best 20-45 second moments from an SRT/VTT/Whisper transcript, cuts them on sentence boundaries with ffmpeg, and burns in word-by-word highlighted captions. Use this skill whenever the user mentions shorts, reels, clips, cutting a long video, finding viral moments, auto-captions, burned-in subtitles, repurposing a podcast, interview, webinar or YouTube video, or has an SRT/VTT file and wants clips, even if they never say "shorts editor".
---

# Welvox Subtitle Shorts Editor

Subtitles in, ranked vertical clips out. Everything runs locally with Python and ffmpeg. No API keys, no subscription.

## Workflow

1. **Get a transcript.** Accept SRT, VTT, or faster-whisper JSON (with word timestamps, for best caption sync).
   - No transcript and `faster-whisper` is installed: transcribe, then export SRT/JSON.
   - No transcript and nothing to transcribe with: ask the user for one. Do not invent timestamps.
2. **Plan clips (no video needed):**
   `python scripts/run.py transcript.srt --top 5 --out shorts_out`
   This writes `clips.json` plus one `.ass` caption file per clip and prints each clip's score and reasons.
3. **Review the picks with the user.** Show start/end, hook line and why each was chosen. The script ranks; the user (and you) make the final call. Read `references/scoring.md` if they want to tune it.
4. **Render:**
   `python scripts/run.py transcript.srt --video input.mp4 --top 5 --out shorts_out`
   Use `--dry-run` to print the ffmpeg commands without running them.
5. **Deliver** the MP4s and `clips.json` (hook, score, reasons). Offer a caption and hashtags per clip from the clip text.

## Options

| Flag | Default | Notes |
|---|---|---|
| `--top` | 5 | number of clips |
| `--min` / `--max` | 20 / 45 | clip length in seconds |
| `--style` | welvox | `welvox` (orange highlight) or `clean` (yellow) |
| `--dry-run` | off | print ffmpeg commands only |

## Rules

- Clips start and end on whole subtitle cues, so they never cut mid-sentence. If the transcript has no sentence-level cues (one giant block), tell the user and ask for a better transcript.
- Scoring is heuristic: hook strength, clean start, clean ending, pace, questions/numbers, filler penalty. Say so, and do not claim a clip "will go viral".
- Needs `ffmpeg` with libass for caption burn-in. If missing, plan clips with `--dry-run`/no video and tell the user to install ffmpeg.
- Default crop is a centered 9:16. For speakers off-centre, say the crop is centered and offer to adjust `crop=` in `scripts/cut.py`.
- Never overwrite the user's source video. Outputs go to `--out`.
- Fast-moving topics change; do not state platform specs (max length, caption safe zones) from memory. Check current platform docs first.

## Files

- `scripts/run.py`: entry point (plan + render)
- `scripts/find_moments.py`: scoring and non-overlapping selection
- `scripts/captions.py`: word-by-word ASS captions
- `scripts/cut.py`: ffmpeg trim, 9:16 crop, caption burn-in
- `scripts/transcript.py`: SRT/VTT/Whisper JSON parsing
- `references/scoring.md`: how clips are scored and how to tune weights
- `examples/sample.srt`: test transcript; `tests/test_all.py`: run `python -m pytest tests`
