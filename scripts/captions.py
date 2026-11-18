"""Build word-by-word ASS captions (active word highlighted) for a clip."""
STYLES = {  # ASS colours are &HBBGGRR&
    "welvox": {"font": "Arial", "size": 78, "primary": "&H00FFFFFF&", "active": "&H0036A5FF&", "outline": 5},
    "clean":  {"font": "Arial", "size": 70, "primary": "&H00FFFFFF&", "active": "&H0000FFFF&", "outline": 4},
}

def _t(sec):
    sec = max(sec, 0)
    h, r = divmod(sec, 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

def build_ass(words, clip_start, style="welvox", group=3, w=1080, h=1920):
    """words: [(text, start, end)] in source time. Output times are clip-relative."""
    st = STYLES[style]
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\n\n"
            "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
            "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,"
            "MarginL,MarginR,MarginV,Encoding\n"
            f"Style: Cap,{st['font']},{st['size']},{st['primary']},&H000000FF&,&H00000000&,&H64000000&,"
            f"-1,0,0,0,100,100,0,0,1,{st['outline']},2,2,60,60,520,1\n\n"
            "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
    lines = []
    for g in range(0, len(words), group):
        chunk = words[g:g + group]
        for k, (_, ws, we) in enumerate(chunk):
            end = chunk[k + 1][1] if k + 1 < len(chunk) else we
            parts = []
            for n, (tx, _, _) in enumerate(chunk):
                tx = tx.upper().replace("{", "").replace("}", "")
                parts.append(f"{{\\c{st['active']}}}{tx}{{\\c{st['primary']}}}" if n == k else tx)
            lines.append(f"Dialogue: 0,{_t(ws - clip_start)},{_t(end - clip_start)},Cap,,0,0,0,,{' '.join(parts)}")
    return head + "\n".join(lines) + "\n"

def clip_words(cues, start, end):
    return [w for c in cues for w in c.words if w[1] >= start - 0.01 and w[2] <= end + 0.01]
