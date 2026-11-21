"""Render the documentary.

  python scripts/render.py <project> --stills            # QA frames (one per shot) -> build/stills/*.jpg
  python scripts/render.py <project> --preview [--sec 90] # quick low-res check of the start -> out/<slug>_preview.mp4
  python scripts/render.py <project>                      # full render -> out/<slug>.mp4 (+ .srt, chapters, credits, thumbnail)

Video is rendered by Remotion in resumable chunks (muted); audio (narration, sound bites from the
sources, ambient source sound, music with sidechain ducking, loudness -14 LUFS) is mixed by ffmpeg.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REMOTION, load_json, need, project_dir, run, save_json  # noqa: E402


def node_render(mode: str, proj: Path, out_dir: Path, extra: list[str]) -> None:
    need("node")
    if not (REMOTION / "node_modules").exists():
        run(["npm", "ci" if (REMOTION / "package-lock.json").exists() else "install", "--no-audit", "--no-fund"], cwd=REMOTION)
    run(["node", REMOTION / "render.mjs", mode, proj / "build" / "props.json", proj / "media", out_dir, *extra], cwd=REMOTION)


def concat(chunk_dir: Path, out: Path) -> None:
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", chunk_dir / "list.txt", "-c", "copy", out])


def mix_audio(proj: Path, plan: dict, total: float, out: Path) -> None:
    media = proj / "media"
    # input 0 = silence of the exact film length: amix(duration=first) then yields exactly `total`
    # (apad/atrim after amix truncates the mix on recent ffmpeg builds)
    inputs: list[str] = ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    chains: list[str] = []
    dialog: list[str] = ["[0:a]"]
    n = 1

    def ms(t: float) -> int:
        return max(0, int(round(t * 1000)))

    for v in plan.get("vo", []):
        if v["start"] >= total:
            continue
        inputs += ["-i", str(media / v["file"])]
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=delays={ms(v['start'])}:all=1[a{n}]")
        dialog.append(f"[a{n}]")
        n += 1
    for s in plan.get("source", []):
        if s["start"] >= total:
            continue
        d = min(s["dur"], total - s["start"])
        inputs += ["-ss", f"{s['in']:.3f}", "-t", f"{d:.3f}", "-i", str(media / s["file"])]
        fo = max(0.0, d - 0.25)
        chains.append(
            f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.12,afade=t=out:st={fo:.3f}:d=0.25,"
            f"volume={s['volume']},adelay=delays={ms(s['start'])}:all=1[a{n}]"
        )
        dialog.append(f"[a{n}]")
        n += 1
    chains.append(f"{''.join(dialog)}amix=inputs={len(dialog)}:normalize=0:duration=first[dlg]")

    music = plan.get("music")
    if music and (media / music["src"]).exists():
        inputs += ["-stream_loop", "-1", "-i", str(media / music["src"])]
        vol = float(music.get("volume", 0.25))
        chains.append("[dlg]asplit=2[dlg1][key]")
        chains.append(
            f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={total:.3f},volume={vol},"
            f"afade=t=in:d=2,afade=t=out:st={max(0, total - 5):.3f}:d=5[mus]"
        )
        chains.append("[mus][key]sidechaincompress=threshold=0.02:ratio=12:attack=20:release=600:makeup=1[musd]")
        chains.append("[dlg1][musd]amix=inputs=2:normalize=0:duration=first[mix]")
        n += 1
    else:
        if music:
            print(f"WARN music file not found: media/{music['src']}")
        chains.append("[dlg]anull[mix]")
    chains.append("[mix]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]")

    script = proj / "build" / "audio_filter.txt"
    script.write_text(";\n".join(chains), encoding="utf-8")
    # ffmpeg >= 7 reads a filter graph from a file with "-/filter_complex"; older builds use -filter_complex_script
    tail = ["-map", "[out]", "-c:a", "pcm_s16le", out]
    r = run(["ffmpeg", "-y", "-v", "error", *inputs, "-/filter_complex", script, *tail], check=False)
    if r.returncode != 0:
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex_script", script, *tail])


def mux(video: Path, audio: Path, out: Path) -> None:
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out])


def srt_time(frame: int, fps: int) -> str:
    ms = int(round(frame / fps * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_extras(proj: Path, props: dict) -> None:
    fps = props["fps"]
    slug = proj.name
    out = proj / "out"
    # subtitles: same grouping as the burned captions
    words = props["captions"]["words"]
    groups, cur = [], []
    for i, w in enumerate(words):
        prev = words[i - 1] if i else None
        if cur and (len(cur) >= 7 or (prev and w["start"] - prev["end"] > 12) or (prev and prev["text"][-1:] in ".!?")):
            groups.append(cur)
            cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    (out / f"{slug}.srt").write_text(
        "\n".join(f"{i + 1}\n{srt_time(g[0]['start'], fps)} --> {srt_time(g[-1]['end'] + 4, fps)}\n{' '.join(w['text'] for w in g)}\n" for i, g in enumerate(groups)),
        encoding="utf-8",
    )
    # YouTube chapters (first must be 0:00)
    marks = props["chapterMarks"] or [{"frame": 0, "title": props["title"]}]
    lines = []
    for i, m in enumerate(marks):
        t = 0 if i == 0 else m["frame"] / fps
        lines.append(f"{int(t // 60)}:{int(t % 60):02d} {m['title']}")
    (out / "chapters.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # credits / sources for the description
    idx = load_json(proj / "build" / "sources_index.json", default={})
    used = {s["visual"].get("src") for s in props["segments"] if s["visual"].get("type") == "video"}
    cred = ["Sources et images d'archives :"]
    for v in idx.values():
        if v.get("path") in used:
            cred.append(f"- {v.get('title', v.get('id'))} — {v.get('credit', '')} ({v.get('license', 'licence à vérifier')}) {v.get('url', '')}".rstrip())
    (out / "credits.txt").write_text("\n".join(cred) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--frames", default="", help="with --stills: comma separated frame numbers")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--sec", type=float, default=90)
    ap.add_argument("--chunk-sec", type=float, default=60)
    ap.add_argument("--concurrency", default="")
    ap.add_argument("--audio-only", action="store_true")
    args = ap.parse_args()

    need("ffmpeg")
    proj = project_dir(args.project)
    props_path = proj / "build" / "props.json"
    props = load_json(props_path)
    plan = load_json(proj / "build" / "audio_plan.json")
    fps = props["fps"]
    slug = proj.name
    conc = ["--concurrency", args.concurrency] if args.concurrency else []

    if args.stills:
        d = proj / "build" / "stills"
        shutil.rmtree(d, ignore_errors=True)
        node_render("stills", proj, d, ["--scale", "0.5", *(["--frames", args.frames] if args.frames else []), *conc])
        print(f"stills -> {d}  (open them to review framing, text, credits)")
        return

    if args.preview:
        total = min(args.sec, props["totalFrames"] / fps)
        cdir = proj / "build" / "chunks_preview"
        shutil.rmtree(cdir, ignore_errors=True)
        node_render("chunks", proj, cdir, ["--scale", "0.5", "--chunk-sec", str(args.chunk_sec), "--max-frames", str(int(total * fps)), "--crf", "26", *conc])
        video, audio = proj / "build" / "preview_video.mp4", proj / "build" / "preview_mix.wav"
        concat(cdir, video)
        mix_audio(proj, plan, total, audio)
        final = proj / "out" / f"{slug}_preview.mp4"
        mux(video, audio, final)
        print(f"preview -> {final}")
        return

    total = props["totalFrames"] / fps
    audio = proj / "build" / "mix.wav"
    mix_audio(proj, plan, total, audio)
    if args.audio_only:
        print(f"audio -> {audio}")
        return
    cdir = proj / "build" / "chunks"
    # chunks are resumable; invalidate them if props changed since last render
    stamp = cdir / "props.stamp"
    cur = props_path.read_text(encoding="utf-8")
    if stamp.exists() and stamp.read_text(encoding="utf-8") != cur:
        print("props changed -> re-rendering all chunks")
        shutil.rmtree(cdir, ignore_errors=True)
    cdir.mkdir(parents=True, exist_ok=True)
    stamp.write_text(cur, encoding="utf-8")
    node_render("chunks", proj, cdir, ["--chunk-sec", str(args.chunk_sec), *conc])
    video = proj / "build" / "video.mp4"
    concat(cdir, video)
    final = proj / "out" / f"{slug}.mp4"
    mux(video, audio, final)
    write_extras(proj, props)
    # thumbnail candidate: middle of the first shot, full res
    tdir = proj / "build" / "thumb"
    first = props["segments"][0]
    node_render("stills", proj, tdir, ["--scale", "1", "--frames", str(first["startFrame"] + first["durationFrames"] // 2)])
    jpgs = sorted(tdir.glob("*.jpg"))
    if jpgs:
        shutil.copy2(jpgs[0], proj / "out" / "thumbnail.jpg")
    save_json(proj / "out" / "render_info.json", {"durationSec": total, "shots": len(props["segments"]), "file": final.name})
    print(f"\nDONE -> {final}  ({total / 60:.1f} min)")


if __name__ == "__main__":
    main()
