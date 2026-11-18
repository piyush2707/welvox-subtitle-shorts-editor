"""Score sentence-aligned windows and pick the best non-overlapping shorts."""
import argparse, json, re, sys
from transcript import load

FILLERS = {"um", "uh", "like", "basically", "actually", "you", "know", "sort", "kind"}
BAD_START = ("and ", "but ", "so ", "because ", "which ", "that ", "or ")
HOOK_WORDS = {"why", "how", "stop", "never", "secret", "mistake", "nobody", "everyone",
              "biggest", "truth", "worst", "best", "free", "new", "just", "imagine", "what"}

def score_window(cues):
    text = " ".join(c.text for c in cues)
    dur = cues[-1].end - cues[0].start
    first = cues[0].text.strip()
    first_words = re.findall(r"[a-z']+", first.lower())
    words = re.findall(r"[A-Za-z0-9']+", text)
    reasons, s = [], 0.0

    hook = 0  # 0-30: opening line asks, claims or surprises
    if "?" in first: hook += 12
    if re.search(r"\d", first): hook += 8
    if set(first_words[:8]) & HOOK_WORDS: hook += 10
    if len(first_words) <= 14: hook += 5
    hook = min(hook, 30); s += hook
    if hook >= 15: reasons.append("strong opening hook")

    sc = 25  # 0-25: self-contained start
    if first.lower().startswith(BAD_START): sc -= 15; reasons.append("starts mid-thought")
    elif first[:1].isupper(): reasons.append("starts clean")
    if not first[:1].isupper(): sc -= 5
    s += max(sc, 0)

    if cues[-1].text.strip().endswith((".", "!", "?")):  # 0-15: clean ending
        s += 15; reasons.append("ends on a full sentence")

    wps = len(words) / dur if dur else 0  # 0-25: energy
    pace = 10 if 2.3 <= wps <= 3.8 else 5 if (1.8 <= wps < 2.3 or 3.8 < wps <= 4.5) else 0
    s += pace + min(text.count("?") * 3, 6) + min(len(re.findall(r"\d", text)) // 2 * 2, 6) \
         + min(text.count("!") * 1.5, 3)
    if pace == 10: reasons.append("good speaking pace")

    fl = sum(1 for w in words if w.lower() in FILLERS) / max(len(words), 1)
    s -= min(fl * 60, 10)  # filler penalty
    if 25 <= dur <= 40: s += 5
    return round(max(s, 0), 1), reasons, dur

def candidates(cues, min_s, max_s):
    out = []
    for i in range(len(cues)):
        for j in range(i, len(cues)):
            dur = cues[j].end - cues[i].start
            if dur > max_s: break
            if dur >= min_s:
                sc, why, d = score_window(cues[i:j + 1])
                out.append({"start": round(cues[i].start, 3), "end": round(cues[j].end, 3),
                            "duration": round(d, 1), "score": sc, "reasons": why,
                            "text": " ".join(c.text for c in cues[i:j + 1])})
    return out

def pick(cues, top=5, min_s=20, max_s=45, min_score=30):
    chosen = []
    for c in sorted(candidates(cues, min_s, max_s), key=lambda x: -x["score"]):
        if c["score"] < min_score: break
        if all(c["end"] <= k["start"] or c["start"] >= k["end"] for k in chosen):
            chosen.append(c)
        if len(chosen) == top: break
    return sorted(chosen, key=lambda x: x["start"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("subs"); ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--min", type=float, default=20); ap.add_argument("--max", type=float, default=45)
    a = ap.parse_args()
    json.dump(pick(load(a.subs), a.top, a.min, a.max), sys.stdout, indent=2)
