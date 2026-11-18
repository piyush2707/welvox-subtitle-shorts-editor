import os, sys, json, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from transcript import load
from find_moments import pick
from captions import build_ass, clip_words
import cut
SRT = os.path.join(ROOT, "examples", "sample.srt")

def test_parse():
    cues = load(SRT)
    assert len(cues) == 14 and cues[0].words and cues[0].start == 0

def test_picks_good_hook_and_skips_filler():
    clips = pick(load(SRT), top=3)
    assert clips and clips[0]["start"] == 0
    assert all("um so yeah" not in c["text"] for c in clips)
    assert all(20 <= c["duration"] <= 45 for c in clips)

def test_no_overlap_and_sentence_aligned():
    clips = pick(load(SRT), top=5, min_score=10)
    for a, b in zip(clips, clips[1:]):
        assert a["end"] <= b["start"]
    assert all(c["text"].rstrip()[-1] in ".!?" for c in clips if c["score"] >= 40)

def test_ass_times_relative_and_highlight():
    cues = load(SRT); c = pick(cues, 1)[0]
    ass = build_ass(clip_words(cues, c["start"], c["end"]), c["start"])
    assert "Dialogue: 0,0:00:0" in ass and "\\c&H0036A5FF&" in ass

def test_ffmpeg_cmd():
    cmd = cut.build_cmd("in.mp4", 1.5, 30, "c.ass", "o.mp4")
    assert "crop=ih*9/16:ih" in " ".join(cmd) and cmd[0] == "ffmpeg"

def test_cli_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "run.py"), SRT,
                            "--video", "x.mp4", "--dry-run", "--out", d], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        m = json.load(open(os.path.join(d, "clips.json")))
        assert m and "ffmpeg" in m[0] and os.path.exists(m[0]["captions"])
