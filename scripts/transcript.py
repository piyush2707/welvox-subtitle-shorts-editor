"""Parse SRT/VTT (or faster-whisper JSON) into cues with word-level timing."""
import json, re
from dataclasses import dataclass, field

@dataclass
class Cue:
    start: float
    end: float
    text: str
    words: list = field(default_factory=list)  # [(word, start, end)]

_TS = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{1,3})")

def _sec(ts):
    h, mi, s, ms = _TS.search(ts).groups()
    return int(h) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000

def spread_words(text, start, end):
    """No word timestamps? Spread words across the cue by character length."""
    toks = text.split()
    if not toks:
        return []
    total = sum(len(t) for t in toks) or 1
    out, t = [], start
    for tok in toks:
        d = (end - start) * len(tok) / total
        out.append((tok, t, t + d))
        t += d
    return out

def parse_subtitles(path):
    raw = open(path, encoding="utf-8-sig").read().replace("\r", "")
    cues = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        ts_i = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if ts_i is None:
            continue
        a, b = lines[ts_i].split("-->")
        text = re.sub(r"<[^>]+>", "", " ".join(lines[ts_i + 1:])).strip()
        if not text:
            continue
        s, e = _sec(a), _sec(b)
        cues.append(Cue(s, e, text, spread_words(text, s, e)))
    return cues

def parse_whisper_json(path):
    """faster-whisper style: {"segments":[{"start","end","text","words":[{"word","start","end"}]}]}"""
    data = json.load(open(path, encoding="utf-8"))
    cues = []
    for seg in data["segments"]:
        words = [(w["word"].strip(), w["start"], w["end"]) for w in seg.get("words", [])]
        text = seg["text"].strip()
        if not words:
            words = spread_words(text, seg["start"], seg["end"])
        cues.append(Cue(seg["start"], seg["end"], text, words))
    return cues

def load(path):
    return parse_whisper_json(path) if path.lower().endswith(".json") else parse_subtitles(path)
