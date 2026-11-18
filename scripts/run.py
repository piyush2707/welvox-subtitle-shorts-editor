#!/usr/bin/env python3
"""welvox-subtitle-shorts-editor: subtitles (+ video) -> ranked, captioned vertical shorts."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcript import load
from find_moments import pick
from captions import build_ass, clip_words
import cut

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("subs", help="SRT, VTT or faster-whisper JSON")
    ap.add_argument("--video", help="source video; omit to only plan clips")
    ap.add_argument("--out", default="shorts_out")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--min", type=float, default=20); ap.add_argument("--max", type=float, default=45)
    ap.add_argument("--style", default="welvox", choices=["welvox", "clean"])
    ap.add_argument("--dry-run", action="store_true", help="print ffmpeg commands, do not run")
    a = ap.parse_args()

    cues = load(a.subs)
    clips = pick(cues, a.top, a.min, a.max)
    os.makedirs(a.out, exist_ok=True)
    manifest = []
    for n, c in enumerate(clips, 1):
        base = f"clip_{n:02d}"
        ass = os.path.join(a.out, base + ".ass")
        open(ass, "w", encoding="utf-8").write(build_ass(clip_words(cues, c["start"], c["end"]), c["start"], a.style))
        entry = {"id": base, "start": c["start"], "end": c["end"], "duration": c["duration"],
                 "score": c["score"], "why": c["reasons"], "hook": c["text"].split(".")[0][:90],
                 "text": c["text"], "captions": ass}
        if a.video:
            mp4 = os.path.join(a.out, base + ".mp4")
            res = cut.run(cut.build_cmd(a.video, c["start"], c["end"], ass, mp4), a.dry_run)
            entry["video"] = mp4
            if a.dry_run: entry["ffmpeg"] = res
        manifest.append(entry)
    json.dump(manifest, open(os.path.join(a.out, "clips.json"), "w"), indent=2)
    for m in manifest:
        print(f"{m['id']}  {m['start']:.1f}-{m['end']:.1f}s  score {m['score']}  {', '.join(m['why'])}")
    print(f"\n{len(manifest)} clip(s) -> {a.out}/clips.json")

if __name__ == "__main__":
    main()
