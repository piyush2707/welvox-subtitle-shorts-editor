# Welvox-subtitle-shorts-editor

**Turn long videos into ranked, captioned vertical shorts. Locally, with Python and ffmpeg.**

<p align="center">
  <img src="assets/edit.png" 
    </p>

An agent skill for Claude Code, Codex and other `SKILL.md`-compatible agents. Give it a transcript (and optionally the video) and it finds the strongest 20 to 45 second moments, cuts them on sentence boundaries, crops to 9:16 and burns in word-by-word highlighted captions.

No API keys. No subscription. Your video never leaves your machine.

---

## What it does

1. **Reads a transcript:** SRT, VTT, or faster-whisper JSON with word timestamps.
2. **Finds the best moments:** scores every sentence-aligned window and picks the top non-overlapping clips.
3. **Explains its picks:** every clip comes with a score and the reasons it was chosen.
4. **Cuts and reframes:** trims with ffmpeg and crops to a centered 9:16 at 1080x1920.
5. **Burns in captions:** three-word groups with the active word highlighted.
6. **Writes a manifest:** `clips.json` with start, end, hook, score, reasons, text and file paths.

## Why it exists

Most clipping tools are paid, upload your footage to a server, or give you a ranking you can't inspect. This skill is free, runs locally, and uses a transparent scoring system you can read and tune.

## Quick start

Requirements:
- Python 3.9 or newer
- ffmpeg with libass (only needed for rendering video)

```bash
git clone https://github.com/YOUR-USERNAME/welvox-subtitle-shorts-editor
cd welvox-subtitle-shorts-editor

# 1. Plan clips only (no video needed)
python scripts/run.py examples/sample.srt --top 3 --out out

# 2. Render real clips
python scripts/run.py talk.srt --video talk.mp4 --top 5 --out out
```

Example planning output:

```
clip_01  0.0-27.0s  score 85.0  strong opening hook, starts clean, ends on a full sentence
```

## Use it as an agent skill

Copy the folder into your agent's skills directory:

| Agent | Location |
|---|---|
| Claude Code | `~/.claude/skills/welvox-subtitle-shorts-editor` |
| Codex | `~/.codex/skills/welvox-subtitle-shorts-editor` |

Then ask your agent things like:
- "Cut this podcast into 5 shorts with captions."
- "Find the best moments in this SRT."
- "Make Reels clips from this interview."

The skill's description triggers on shorts, reels, clips, burned-in subtitles, repurposing long videos and similar requests.

## Command line options

| Flag | Default | Description |
|---|---|---|
| `subs` | required | Transcript file (`.srt`, `.vtt` or `.json`) |
| `--video` | none | Source video. Leave out to plan clips only |
| `--out` | `shorts_out` | Output folder |
| `--top` | `5` | Number of clips to pick |
| `--min` | `20` | Minimum clip length in seconds |
| `--max` | `45` | Maximum clip length in seconds |
| `--style` | `welvox` | Caption style: `welvox` (orange highlight) or `clean` (yellow highlight) |
| `--dry-run` | off | Print the ffmpeg commands without running them |

## Output

```
out/
├── clip_01.ass     # word-by-word captions
├── clip_01.mp4     # rendered short (only when --video is given)
├── clip_02.ass
├── ...
└── clips.json      # hook, score, reasons, timings, text
```

## How clips are scored

Windows are built from whole subtitle cues, scored on a roughly 100-point scale, then picked greedily with no overlap.

| Signal | Points | What it rewards |
|---|---|---|
| Opening hook | 0 to 30 | A question, a number, a hook word (why, how, never, mistake) or a short first line |
| Clean start | 0 to 25 | Starts capitalised and not mid-thought (and, but, so, because) |
| Clean ending | 15 | Last cue ends in `.` `!` or `?` |
| Pace | 0 to 10 | About 2.3 to 3.8 words per second |
| Energy cues | up to 15 | Questions, numbers and exclamations |
| Length sweet spot | 5 | 25 to 40 seconds |
| Filler penalty | up to -10 | um, uh, like, basically, you know |

Details and tuning notes are in [`references/scoring.md`](references/scoring.md).

## Transcript formats

- **SRT / VTT:** word timing is estimated by spreading words across each cue.
- **faster-whisper JSON:** uses real word timestamps for tighter caption sync:

```json
{"segments": [{"start": 0.0, "end": 4.0, "text": "Hello there",
  "words": [{"word": "Hello", "start": 0.0, "end": 0.5},
            {"word": "there", "start": 0.5, "end": 1.0}]}]}
```

## Tests

```bash
pip install pytest
python -m pytest tests
```

Six tests cover parsing, clip selection, overlap rules, caption timing, the ffmpeg command and the full CLI in dry-run mode.

## Project structure

```
welvox-subtitle-shorts-editor/
├── SKILL.md                 # agent instructions and trigger description
├── README.md
├── scripts/
│   ├── run.py               # entry point: plan + render
│   ├── transcript.py        # SRT / VTT / Whisper JSON parsing
│   ├── find_moments.py      # scoring and clip selection
│   ├── captions.py          # ASS caption generation
│   └── cut.py               # ffmpeg trim, crop, burn-in
├── references/scoring.md
├── examples/sample.srt
└── tests/test_all.py
```

## Limitations

- Scoring is text-only. It can't hear energy, laughter or music, and it can't see the video. Treat the ranking as a shortlist and review the picks.
- The crop is a centered 9:16. Speakers who sit off-centre may be cut off. You can adjust the `crop=` filter in `scripts/cut.py`.
- Clip quality depends on transcript quality. Transcripts without sentence-level cues give weaker results.
- Rendering needs ffmpeg built with libass.
- It does not transcribe audio by itself. Use faster-whisper or any tool that exports SRT, VTT or JSON.

## Roadmap

- [ ] Face-tracked reframing
- [ ] Built-in Whisper transcription step
- [ ] Custom caption themes
- [ ] Optional LLM re-rank of the top candidates

## Contributing

Issues and pull requests are welcome. Please run `python -m pytest tests` before submitting.

## License

Add a LICENSE file of your choice (MIT is a common default for open-source skills).

---

Built by [Welvox](https://welvox.in).
