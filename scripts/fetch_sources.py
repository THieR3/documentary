"""Download + index the source footage listed in <project>/sources.json.

For every source it produces (in <project>/media/sources/ and <project>/build/sources/):
  <id>.mp4                 the footage (H.264 preferred, <=1080p)
  <id>.transcript.txt      "[mm:ss - mm:ss] text" lines (from the video's subtitles, else faster-whisper)
  <id>.shots.json          detected shot changes (seconds)
  <id>.sheet_XX.jpg        contact sheets (one thumbnail per shot, timestamp on each cell)
and build/sources_index.json summarising everything.

Usage: python scripts/fetch_sources.py <project> [--only id1,id2] [--no-transcribe] [--whisper-model base]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, need, probe, project_dir, run, save_json  # noqa: E402

SCENE_THRESHOLD = 0.32
MAX_THUMBS = 96


def download(src: dict, dest: Path, subs_dir: Path) -> None:
    need("yt-dlp")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-S", "res:1080,vcodec:h264,acodec:m4a",
        "--merge-output-format", "mp4",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", src.get("subLangs", "fr.*,en.*"),
        "--convert-subs", "srt",
        "-o", str(dest.with_suffix("")) + ".%(ext)s",
        "-P", f"subtitle:{subs_dir}",
        # record what was actually downloaded (essential for "ytsearch1:" candidates and for the credits)
        "--print-to-file", "%(webpage_url)s\t%(title)s\t%(channel)s\t%(upload_date)s\t%(duration)s", str(subs_dir / f"{dest.stem}.resolved.tsv"),
    ]
    if src.get("section"):
        sec = src["section"]
        cmd += ["--download-sections", f"*{sec.get('start', '0')}-{sec.get('end', 'inf')}", "--force-keyframes-at-cuts"]
    if os.environ.get("YTDLP_COOKIES"):
        cmd += ["--cookies", os.environ["YTDLP_COOKIES"]]
    cmd.append(src["url"])
    run(cmd)


def normalise(path: Path) -> Path:
    """Re-encode to H.264/AAC mp4 if the codec is something Chrome/Remotion seeks badly (e.g. AV1, HEVC in odd containers)."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0", path], capture=True).stdout.strip()
    if out in ("h264", "vp8", "vp9") and path.suffix == ".mp4":
        return path
    tmp = path.with_name(path.stem + ".norm.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", path, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
         "-vf", "scale='min(1920,iw)':-2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp])
    final = path.with_suffix(".mp4")
    if path != final and path.exists():
        path.unlink()
    tmp.replace(final)
    return final


def detect_shots(path: Path) -> list[float]:
    res = run(
        ["ffmpeg", "-hide_banner", "-i", path, "-an", "-vf", f"scale=320:-2,select='gt(scene,{SCENE_THRESHOLD})',showinfo", "-f", "null", "-"],
        capture=True, check=False,
    )
    times = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", res.stderr)]
    return [0.0] + [t for t in times if t > 0.5]


def contact_sheets(path: Path, sid: str, shots: list[float], duration: float, out_dir: Path) -> list[dict]:
    # one thumb per shot (middle of the shot); if too many, sample evenly
    bounds = shots + [duration]
    mids = [(a + b) / 2 for a, b in zip(bounds[:-1], bounds[1:]) if b - a > 0.4]
    if len(mids) > MAX_THUMBS:
        step = len(mids) / MAX_THUMBS
        mids = [mids[int(i * step)] for i in range(MAX_THUMBS)]
    if not mids:
        mids = [duration / 2]
    tdir = out_dir / f"{sid}_thumbs"
    if tdir.exists():
        shutil.rmtree(tdir)
    tdir.mkdir(parents=True)
    for i, t in enumerate(mids):
        label = f"{int(t // 60):02d}\\:{int(t % 60):02d}"
        vf = (
            "scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,"
            f"drawtext=text='#{i} {label}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6"
        )
        dst = tdir / f"{i:04d}.jpg"
        r = run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", vf, dst], check=False)
        if r.returncode != 0:  # no font available -> plain thumb
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", vf.split(",drawtext")[0], dst], check=False)
    sheets = []
    per = 48  # 6 x 8
    files = sorted(tdir.glob("*.jpg"))
    for s in range(0, len(files), per):
        batch = files[s : s + per]
        lst = tdir / f"sheet{s // per}.txt"
        lst.write_text("".join(f"file '{f.as_posix()}'\n" for f in batch), encoding="utf-8")
        sheet = out_dir / f"{sid}.sheet_{s // per:02d}.jpg"
        rows = (len(batch) + 5) // 6
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", f"tile=6x{rows}:padding=4:color=black", "-frames:v", "1", "-q:v", "3", sheet])
        sheets.append({"file": str(sheet), "cells": [{"cell": s + j, "time": round(mids[s + j], 2)} for j in range(len(batch))]})
    shutil.rmtree(tdir, ignore_errors=True)
    return sheets


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    segs = []
    for block in re.split(r"\n\s*\n", text):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", block)
        if not m:
            continue
        g = list(map(int, m.groups()))
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        rows = block.splitlines()
        arrow = next(i for i, ln in enumerate(rows) if "-->" in ln)
        lines = rows[arrow + 1 :]
        txt = re.sub(r"<[^>]+>", "", " ".join(lines)).strip()
        if txt and (not segs or segs[-1]["text"] != txt):
            segs.append({"start": round(start, 2), "end": round(end, 2), "text": txt})
    return segs


def whisper(path: Path, model: str, lang: str | None) -> list[dict]:
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        print("  faster-whisper not installed -> no transcript")
        return []
    wm = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = wm.transcribe(str(path), language=lang, vad_filter=True)
    return [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segments]


def mmss(t: float) -> str:
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only", default="")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--whisper-model", default=os.environ.get("WHISPER_MODEL", "base"))
    args = ap.parse_args()

    need("ffmpeg")
    proj = project_dir(args.project)
    sources = load_json(proj / "sources.json")
    only = set(filter(None, args.only.split(",")))
    media = proj / "media" / "sources"
    bdir = proj / "build" / "sources"
    bdir.mkdir(parents=True, exist_ok=True)
    index_path = proj / "build" / "sources_index.json"
    index = load_json(index_path, default={})

    for src in sources:
        sid = src["id"]
        if only and sid not in only:
            continue
        print(f"\n=== {sid} ===")
        dest = media / f"{sid}.mp4"
        if not dest.exists():
            local = src.get("file")
            if local:
                lp = (proj / local) if not Path(local).is_absolute() else Path(local)
                if lp.resolve() != dest.resolve():
                    shutil.copy2(lp, dest)
            elif src.get("url"):
                try:
                    download(src, dest, bdir)
                except Exception as e:  # keep going with the other sources
                    print(f"  !! download failed for {sid}: {e}")
                    index[sid] = {"error": str(e), **src}
                    continue
            else:
                print("  !! no url/file")
                continue
            # yt-dlp may produce .mkv/.webm when merging fails
            if not dest.exists():
                cand = next(iter(sorted(media.glob(f"{sid}.*"))), None)
                if cand is None:
                    print("  !! nothing downloaded")
                    continue
                dest = cand
            dest = normalise(dest)
        meta = probe(dest)
        print(f"  {meta['width']}x{meta['height']} {meta['fps']}fps {meta['duration']:.1f}s audio={meta['has_audio']}")

        shots = detect_shots(dest)
        save_json(bdir / f"{sid}.shots.json", shots)
        sheets = contact_sheets(dest, sid, shots, meta["duration"], bdir)

        transcript: list[dict] = []
        srts = sorted(bdir.glob(f"{sid}*.srt"))
        pref = [s for s in srts if ".fr" in s.name] + [s for s in srts if ".fr" not in s.name]
        if pref:
            transcript = parse_srt(pref[0])
            print(f"  transcript from subtitles {pref[0].name}: {len(transcript)} lines")
        elif not args.no_transcribe and meta["has_audio"]:
            print(f"  transcribing with faster-whisper ({args.whisper_model}) ...")
            transcript = whisper(dest, args.whisper_model, src.get("lang"))
        (bdir / f"{sid}.transcript.txt").write_text(
            "".join(f"[{mmss(s['start'])} - {mmss(s['end'])}] {s['text']}\n" for s in transcript), encoding="utf-8"
        )
        save_json(bdir / f"{sid}.transcript.json", transcript)

        resolved = {}
        rf = bdir / f"{sid}.resolved.tsv"
        if rf.exists():
            parts = rf.read_text(encoding="utf-8").strip().splitlines()[-1].split("\t")
            resolved = dict(zip(["resolvedUrl", "resolvedTitle", "resolvedChannel", "uploadDate", "sourceDuration"], parts))
            print(f"  -> {resolved.get('resolvedTitle')} | {resolved.get('resolvedChannel')} | {resolved.get('resolvedUrl')}")
        index[sid] = {
            **{k: v for k, v in src.items() if k not in ("file",)},
            **resolved,
            "path": f"sources/{dest.name}",
            **meta,
            "shots": len(shots),
            "sheets": sheets,
            "transcript": str(bdir / f"{sid}.transcript.txt"),
            "transcriptLines": len(transcript),
        }
        save_json(index_path, index)

    total = sum(v.get("duration", 0) for v in index.values())
    print(f"\nindexed {len(index)} sources, {total / 60:.1f} min of footage -> {index_path}")
    for sid, v in index.items():
        if "error" in v:
            print(f"  FAILED {sid}: {v['error'][:120]}")
        else:
            print(f"  {sid}: {v['duration'] / 60:.1f} min, {v['shots']} shots, {v['transcriptLines']} transcript lines, sheets: {len(v['sheets'])}")


if __name__ == "__main__":
    main()
