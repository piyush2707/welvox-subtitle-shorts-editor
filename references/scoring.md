# Scoring (max ~100)

| Signal | Points | Rule |
|---|---|---|
| Hook | 0-30 | first cue has a question (+12), a number (+8), a hook word like why/how/never/mistake (+10), or is short (+5) |
| Clean start | 0-25 | starts capitalised and not with and/but/so/because (-15 if it does) |
| Clean ending | 15 | last cue ends in . ! or ? |
| Pace | 0-10 | 2.3-3.8 words/sec best |
| Questions / numbers / "!" | up to 6 / 6 / 3 | energy cues |
| Length sweet spot | 5 | 25-40 seconds |
| Filler penalty | up to -10 | um, uh, like, basically, you know... |

Windows are built from whole cues (20-45s by default), scored, then picked greedily with no overlap. `min_score` defaults to 30; lower it in `pick()` for flat content.

To tune: edit `HOOK_WORDS`, `FILLERS` and the weights in `scripts/find_moments.py`, then run the tests.

Limits: text-only. It cannot hear energy, laughter or music, and it cannot see the video. Treat the ranking as a shortlist.
