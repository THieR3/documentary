"""Monte des Shorts verticaux (1080x1920) à partir de passages du film rendus SANS sous-titres.

Entrées : build/props.json (mots des sous-titres), out/dieselgate.mp4 (audio mixé),
          <raw_dir>/raw_<id>/c0000.mp4 (vidéo 16:9 du passage, rendue avec captions désactivées).
Usage : python3 projects/dieselgate/make_shorts.py <raw_dir> <out_dir>
"""
import json
import subprocess
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
ACCENT = "E8B04B"

SHORTS = [
    {"id": "a", "start": 0, "end": 1641, "title": ["« ON A COMPLÈTEMENT", "MERDÉ »"],
     "subtitle": "Le patron de Volkswagen avoue"},
    {"id": "b", "start": 8340, "end": 10019, "title": ["35 FOIS", "LA LIMITE"],
     "subtitle": "Ce que 3 chercheurs ont découvert"},
    {"id": "c", "start": 11635, "end": 12816, "title": ["LA VOITURE", "SAVAIT"],
     "subtitle": "qu'elle était testée"},
]
FPS = 30
VIDEO_Y = 600          # haut de la vidéo 16:9 (1080x608) dans le cadre vertical
CAPTION_Y = 1250       # haut des sous-titres


def ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    h, m, s = int(sec // 3600), int(sec % 3600 // 60), sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def lines_of(words: list[dict]) -> list[list[dict]]:
    """Coupe en lignes courtes (≤ 22 caractères), en privilégiant la ponctuation."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        n = len(" ".join(x["text"] for x in cur))
        if n >= 16 and w["text"][-1] in ".,:;?!»" or n >= 22:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def make_ass(words: list[dict], start: int, end: int, path: Path) -> None:
    ws = [w for w in words if w["start"] >= start and w["start"] < end]
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,84,&H00F5F1E8,&H00F5F1E8,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,2,8,60,60,{CAPTION_Y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hl = "{\\c&H" + ACCENT[4:6] + ACCENT[2:4] + ACCENT[0:2] + "&}"
    ev = []
    for line in lines_of(ws):
        for i, w in enumerate(line):
            a = (w["start"] - start) / FPS
            nxt = line[i + 1]["start"] if i + 1 < len(line) else line[-1]["end"] + 6
            b = (min(nxt, end) - start) / FPS
            txt = " ".join((hl + x["text"].upper() + "{\\r}") if x is w else x["text"].upper() for x in line)
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{txt}")
    path.write_text(hdr + "\n".join(ev) + "\n", encoding="utf-8")


def esc(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def build(short: dict, raw_dir: Path, out_dir: Path, words: list[dict]) -> Path:
    sid, a, b = short["id"], short["start"], short["end"]
    dur = (b - a) / FPS
    work = out_dir / f"work_{sid}"
    work.mkdir(parents=True, exist_ok=True)
    make_ass(words, a, b, work / "caps.ass")
    texts = {"t1": short["title"][0], "t2": short["title"][1], "st": short["subtitle"],
             "cta": "DOCUMENTAIRE COMPLET SUR LA CHAÎNE"}
    for k, v in texts.items():
        (work / f"{k}.txt").write_text(v, encoding="utf-8")
    fade = 0.35
    fc = (
        f"[0:v]split[bgs][fgs];"
        f"[bgs]scale=-2:1920,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.28:saturation=0.8[bg];"
        f"[fgs]scale=1080:608[fg];"
        f"[bg][fg]overlay=0:{VIDEO_Y}[v0];"
        f"[v0]drawbox=x=0:y={VIDEO_Y - 4}:w=1080:h=4:color=0x{ACCENT}:t=fill,"
        f"drawbox=x=0:y={VIDEO_Y + 608}:w=1080:h=4:color=0x{ACCENT}:t=fill,"
        f"drawtext=fontfile={FONT_BLACK}:textfile='{esc(work / 't1.txt')}':fontsize=96:fontcolor=0xF5F1E8:"
        f"borderw=5:bordercolor=black:x=(w-tw)/2:y=250,"
        f"drawtext=fontfile={FONT_BLACK}:textfile='{esc(work / 't2.txt')}':fontsize=96:fontcolor=0x{ACCENT}:"
        f"borderw=5:bordercolor=black:x=(w-tw)/2:y=360,"
        f"drawtext=fontfile={FONT_BOLD}:textfile='{esc(work / 'st.txt')}':fontsize=46:fontcolor=0xF5F1E8:"
        f"borderw=3:bordercolor=black:x=(w-tw)/2:y=490,"
        f"ass='{esc(work / 'caps.ass')}',"
        f"drawtext=fontfile={FONT_BOLD}:textfile='{esc(work / 'cta.txt')}':fontsize=34:fontcolor=0xF5F1E8@0.85:"
        f"box=1:boxcolor=black@0.45:boxborderw=18:x=(w-tw)/2:y=1700,"
        f"fade=t=in:st=0:d={fade},fade=t=out:st={dur - fade:.3f}:d={fade}[v]"
    )
    out = out_dir / f"short_{sid}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_dir / f"raw_{sid}" / "c0000.mp4"),
        "-ss", f"{a / FPS:.3f}", "-t", f"{dur:.3f}", "-i", str(PROJ / "out" / "dieselgate.mp4"),
        "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
        "-af", f"afade=t=in:st=0:d={fade},afade=t=out:st={dur - fade:.3f}:d={fade}",
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out),
    ], check=True)
    return out


def main() -> None:
    raw_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    words = json.loads((PROJ / "build" / "props.json").read_text())["captions"]["words"]
    for s in SHORTS:
        print("->", build(s, raw_dir, out_dir, words))


if __name__ == "__main__":
    main()
