"""timeline.json (+ build/vo.json + build/sources_index.json) -> build/props.json + build/audio_plan.json.

Validates the edit and prints a report: total length, per-chapter length, share of screen time that
is real source footage vs. full-screen motion cards, reused ranges, clips running past their source.

Usage: python scripts/build_props.py <project> [--strict]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, project_dir, save_json  # noqa: E402

DEFAULT_STYLE = {"accent": "#E8B04B", "text": "#F5F1E8", "headingFont": "PlayfairDisplay", "bodyFont": "Inter", "grain": 0.35, "vignette": 0.5}
CARD_TYPES = {"title", "chapter", "quote", "map", "timeline", "color"}
FOOTAGE_TYPES = {"video", "image"}


def tsec(v) -> float:
    """12.5 | "12.5" | "01:02.5" | "1:02:03" -> seconds"""
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    parts = [float(p) for p in str(v).strip().split(":")]
    s = 0.0
    for p in parts:
        s = s * 60 + p
    return s


class Builder:
    def __init__(self, proj: Path):
        self.proj = proj
        self.tl = load_json(proj / "timeline.json")
        self.vo = load_json(proj / "build" / "vo.json", default={})
        self.idx = load_json(proj / "build" / "sources_index.json", default={})
        self.meta = self.tl.get("meta", {})
        self.fps = int(self.meta.get("fps", 30))
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.segments: list[dict] = []
        self.audio = {"vo": [], "source": [], "music": self.meta.get("music")}
        self.words: list[dict] = []
        self.chapter_marks: list[dict] = []
        self.used_ranges: dict[str, list[tuple[float, float, str]]] = {}
        self.footage_sec = 0.0
        self.card_sec = 0.0
        self.cursor = 0  # frames

    def f(self, sec: float) -> int:
        return int(round(sec * self.fps))

    # ---- visuals ----
    def source(self, sid: str) -> dict | None:
        s = self.idx.get(sid)
        if not s or "error" in s:
            self.errors.append(f"unknown or failed source '{sid}' (run fetch_sources.py?)")
            return None
        return s

    def resolve_visual(self, v: dict, seg_id: str, dur_sec: float, pre_roll_frames: int, track: bool = True) -> dict:
        t = v.get("type", "video")
        if t == "video":
            src = self.source(v.get("source", ""))
            path = src["path"] if src else v.get("src", "missing.mp4")
            rate = float(v.get("rate", 1))
            start = tsec(v.get("in", 0))
            if src and track:
                if start + dur_sec * rate > src["duration"] + 0.05:
                    self.warnings.append(f"{seg_id}: clip {v.get('source')} @{start:.1f}s + {dur_sec * rate:.1f}s runs past source end ({src['duration']:.1f}s) - last frame will freeze")
                self.used_ranges.setdefault(v["source"], []).append((start, start + dur_sec * rate, seg_id))
            return {
                "type": "video",
                "src": path,
                "trimBeforeFrames": max(0, self.f(start) - int(pre_roll_frames * rate)),
                "playbackRate": rate,
                "motion": v.get("motion", "drift"),
                "grade": v.get("grade", self.meta.get("grade", "cinematic")),
                "fit": v.get("fit", "cover" if not src or src.get("width", 16) / max(1, src.get("height", 9)) > 1.6 else "blur-fill"),
                "letterbox": bool(v.get("letterbox", False)),
            }
        if t == "image":
            p = self.proj / "media" / v["src"]
            if not p.exists():
                self.errors.append(f"{seg_id}: image not found media/{v['src']}")
            return {"type": "image", "src": v["src"], "motion": v.get("motion", "zoom-in"), "grade": v.get("grade", "none"), "fit": v.get("fit", "cover")}
        out = {k: val for k, val in v.items() if k not in ("bg", "dur")}
        if v.get("bg"):
            out["bg"] = self.resolve_visual(v["bg"], seg_id, dur_sec, pre_roll_frames, track=False)
        if t == "map":
            out["pins"] = [{**p, "atFrames": self.f(tsec(p["at"])) if "at" in p else None} for p in v.get("pins", [])]
            out["pins"] = [{k: val for k, val in p.items() if val is not None and k != "at"} for p in out["pins"]]
            if not (self.proj / "media" / v.get("src", "")).exists():
                self.errors.append(f"{seg_id}: map image not found media/{v.get('src')}")
        if t == "chapter" and "number" not in out:
            out["number"] = len(self.chapter_marks)
        return out

    def overlays(self, seg: dict, dur_frames: int, credit_text: str | None) -> list[dict]:
        res = []
        for o in seg.get("overlays", []):
            frm = self.f(tsec(o.get("at", 0)))
            d = self.f(tsec(o.get("dur", 4)))
            if frm >= dur_frames:
                self.warnings.append(f"{seg['_id']}: overlay {o.get('type')} starts after segment end - dropped")
                continue
            d = min(d, dur_frames - frm)
            item = {k: v for k, v in o.items() if k not in ("at", "dur")}
            item.update({"fromFrames": frm, "durationFrames": d})
            res.append(item)
            if o.get("type") in ("kinetic",) or (o.get("type") == "stat" and o.get("position", "center") == "center"):
                self.card_sec += d / self.fps
                self.footage_sec -= d / self.fps
        if credit_text and seg.get("credit", True) is not False:
            res.insert(0, {"type": "credit", "text": seg.get("credit") if isinstance(seg.get("credit"), str) else credit_text,
                           "fromFrames": min(6, dur_frames - 1), "durationFrames": max(1, min(dur_frames - 6, self.f(4)))})
        return res

    # ---- segments ----
    def add_segment(self, seg: dict, chapter_title: str) -> None:
        sid = seg["_id"]
        vo = self.vo.get(sid)
        if seg.get("vo") and not vo:
            self.errors.append(f"{sid}: has 'vo' text but no audio in build/vo.json (run tts.py)")
        vo_dur = vo["duration"] if vo else 0.0
        bite = seg.get("bite")
        bite_dur = 0.0
        if bite:
            bite_dur = tsec(bite["out"]) - tsec(bite["in"])
            if bite_dur <= 0:
                self.errors.append(f"{sid}: bite out <= in")
        pad = float(seg.get("pad", 0.35 if vo else 0.0))
        dur = max(tsec(seg.get("duration", 0)), vo_dur + pad + tsec(seg.get("voDelay", 0)), bite_dur)
        shots = seg.get("shots") or [seg.get("visual") or ({"type": "video", "source": bite["source"], "in": bite["in"]} if bite else {"type": "color"})]
        # split duration across shots: explicit 'dur' wins, rest shared equally
        fixed = sum(tsec(s.get("dur", 0)) for s in shots)
        free = [s for s in shots if "dur" not in s]
        share = max(0.0, dur - fixed) / len(free) if free else 0.0
        if not free and fixed < dur:
            shots[-1] = {**shots[-1], "dur": tsec(shots[-1]["dur"]) + dur - fixed}
        seg_start = self.cursor
        if seg.get("chapter_start"):
            self.chapter_marks.append({"frame": seg_start, "title": chapter_title})

        for k, shot in enumerate(shots):
            sdur = tsec(shot["dur"]) if "dur" in shot else share
            if sdur <= 0.05:
                continue
            df = max(1, self.f(sdur))
            trans = seg.get("transition", "fade" if k == 0 else "cut") if k == 0 else shot.get("transition", "cut")
            tdur = self.f(tsec(seg.get("transitionDur", 0.5) if k == 0 else shot.get("transitionDur", 0.3)))
            if trans == "cut" or self.cursor == 0:
                tdur = 0
            tdur = min(tdur, df // 2)
            visual = self.resolve_visual(shot, f"{sid}#{k}", sdur, tdur)
            credit = None
            if shot.get("type", "video") == "video":
                src = self.idx.get(shot.get("source", ""), {})
                credit = src.get("credit")
            if shot.get("type", "video") in FOOTAGE_TYPES:
                self.footage_sec += sdur
            else:
                self.card_sec += sdur
            ov = self.overlays({**seg, "_id": sid, "overlays": seg.get("overlays", []) if k == 0 else shot.get("overlays", [])}, df, credit if k == 0 or shot.get("source") != shots[k - 1].get("source") else None)
            self.segments.append({"id": f"{sid}_{k}", "startFrame": self.cursor, "durationFrames": df, "transition": trans, "transitionFrames": tdur, "visual": visual, "overlays": ov})
            self.cursor += df

        # audio
        if vo:
            delay = tsec(seg.get("voDelay", 0))
            self.audio["vo"].append({"file": vo["file"], "start": seg_start / self.fps + delay})
            for w in vo.get("words", []):
                self.words.append({"text": w["text"], "start": seg_start + self.f(w["start"] + delay), "end": seg_start + self.f(w["end"] + delay)})
        if bite:
            src = self.source(bite["source"])
            if src:
                self.audio["source"].append({"file": src["path"], "in": tsec(bite["in"]), "dur": bite_dur, "start": seg_start / self.fps, "volume": float(bite.get("volume", 1.0)), "bite": True})
                if bite.get("subtitle"):
                    words = bite["subtitle"].split()
                    step = bite_dur / max(1, len(words))
                    for i, w in enumerate(words):
                        self.words.append({"text": w, "start": seg_start + self.f(i * step), "end": seg_start + self.f((i + 1) * step) - 1})
        elif seg.get("sourceVolume"):
            # ambient original sound under the narration (each video shot)
            t = seg_start / self.fps
            for shot in shots:
                sdur = tsec(shot["dur"]) if "dur" in shot else share
                s = self.idx.get(shot.get("source", ""))
                if s and s.get("has_audio"):
                    self.audio["source"].append({"file": s["path"], "in": tsec(shot.get("in", 0)), "dur": sdur, "start": t, "volume": float(seg["sourceVolume"]), "bite": False})
                t += sdur

    def build(self) -> dict:
        n = 0
        for ci, ch in enumerate(self.tl.get("chapters", [])):
            for si, seg in enumerate(ch.get("segments", [])):
                n += 1
                seg["_id"] = seg.get("id") or f"c{ci}s{si}"
                seg["chapter_start"] = si == 0
                self.add_segment(seg, ch.get("title", f"Chapitre {ci}"))
        # overlapping reuse of the same source range
        for sid, rs in self.used_ranges.items():
            rs.sort()
            for (a0, a1, i0), (b0, b1, i1) in zip(rs, rs[1:]):
                if b0 < a1 - 0.5:
                    self.warnings.append(f"source '{sid}' range reused: {i0} and {i1} overlap ({b0:.1f}-{a1:.1f}s)")
        total_frames = self.cursor
        style = {**DEFAULT_STYLE, **self.meta.get("style", {})}
        props = {
            "fps": self.fps,
            "width": int(self.meta.get("width", 1920)),
            "height": int(self.meta.get("height", 1080)),
            "totalFrames": total_frames,
            "title": self.meta.get("title", self.proj.name),
            "style": style,
            "segments": self.segments,
            "captions": {"enabled": bool(self.meta.get("captions", True)), "words": sorted(self.words, key=lambda w: w["start"])},
            "chapterMarks": self.chapter_marks,
        }
        self.audio["totalSec"] = total_frames / self.fps
        return props


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    args = ap.parse_args()
    proj = project_dir(args.project)
    b = Builder(proj)
    props = b.build()
    save_json(proj / "build" / "props.json", props)
    save_json(proj / "build" / "audio_plan.json", b.audio)

    total = props["totalFrames"] / b.fps
    print(f"\n== {props['title']} ==  {total / 60:.1f} min ({len(props['segments'])} shots, {len(props['chapterMarks'])} chapters)")
    marks = props["chapterMarks"] + [{"frame": props["totalFrames"], "title": "END"}]
    for a, c in zip(marks, marks[1:]):
        print(f"  {a['frame'] / b.fps / 60:5.1f} min  {a['title']}  ({(c['frame'] - a['frame']) / b.fps:.0f}s)")
    tot = max(1e-6, b.footage_sec + b.card_sec)
    share = b.footage_sec / tot
    print(f"  source footage on screen: {share * 100:.0f}%   full-screen motion: {(1 - share) * 100:.0f}%")
    print(f"  narration clips: {len(b.audio['vo'])}   sound bites: {sum(1 for s in b.audio['source'] if s['bite'])}")
    if share < 0.7:
        b.warnings.append(f"only {share * 100:.0f}% of screen time is real footage - target >= 75% (replace some cards with source shots + overlays)")
    if not 600 <= total <= 900:
        b.warnings.append(f"length {total / 60:.1f} min is outside the 10-15 min target")
    for w in b.warnings:
        print("  WARN ", w)
    for e in b.errors:
        print("  ERROR", e)
    if b.errors or (args.strict and b.warnings):
        sys.exit(1)
    print(f"props -> {proj / 'build' / 'props.json'}")


if __name__ == "__main__":
    main()
