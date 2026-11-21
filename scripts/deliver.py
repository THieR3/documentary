"""Get the finished video out of the cloud session.

1. If GH_TOKEN or GITHUB_TOKEN is set and the repo has a GitHub remote: create a release
   "<slug>-<date>" and upload the full mp4 + srt + thumbnail + texts as release assets (2 GB limit/file).
2. Otherwise (or with --git): write a size-capped copy (<95 MB, 720p) to delivery/<slug>/ so it can be
   committed and pushed with the session branch, alongside srt/chapters/credits/thumbnail.

Usage: python scripts/deliver.py <project> [--git]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, probe, project_dir, run  # noqa: E402

EXTRAS = ["{slug}.srt", "chapters.txt", "credits.txt", "thumbnail.jpg"]


def gh_repo() -> str | None:
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    return m.group(1) if m else None


def api(method: str, url: str, token: str, data: bytes | None = None, ctype: str = "application/json") -> dict:
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=3600) as r:
        return json.loads(r.read() or b"{}")


def release(proj: Path, repo: str, token: str) -> None:
    slug = proj.name
    tag = f"{slug}-{dt.datetime.now():%Y%m%d-%H%M}"
    rel = api("POST", f"https://api.github.com/repos/{repo}/releases", token, json.dumps({"tag_name": tag, "name": f"Documentaire : {slug}", "body": (proj / "out" / "chapters.txt").read_text(encoding="utf-8") if (proj / "out" / "chapters.txt").exists() else "", "draft": False}).encode())
    upload = rel["upload_url"].split("{")[0]
    for name in [f"{slug}.mp4", *[e.format(slug=slug) for e in EXTRAS]]:
        f = proj / "out" / name
        if not f.exists():
            continue
        ctype = "video/mp4" if name.endswith(".mp4") else "image/jpeg" if name.endswith(".jpg") else "text/plain"
        print(f"uploading {name} ({f.stat().st_size / 1e6:.0f} MB)")
        api("POST", f"{upload}?name={name}", token, f.read_bytes(), ctype)
    print(f"\nRELEASE: {rel['html_url']}")


def git_copy(proj: Path) -> None:
    slug = proj.name
    src = proj / "out" / f"{slug}.mp4"
    dst_dir = ROOT / "delivery" / slug
    dst_dir.mkdir(parents=True, exist_ok=True)
    dur = probe(src)["duration"]
    kbps = int(95 * 8 * 1024 / max(1, dur)) - 160  # leave room for 128k audio + container
    out = dst_dir / f"{slug}_720p.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "medium", "-b:v", f"{max(400, kbps)}k", "-maxrate", f"{max(400, kbps) * 2}k", "-bufsize", f"{max(400, kbps) * 2}k", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
    for e in EXTRAS:
        f = proj / "out" / e.format(slug=slug)
        if f.exists():
            shutil.copy2(f, dst_dir / f.name)
    print(f"delivery copy -> {out} ({out.stat().st_size / 1e6:.0f} MB). Commit + push 'delivery/{slug}/' with the session branch.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--git", action="store_true")
    args = ap.parse_args()
    proj = project_dir(args.project)
    if not (proj / "out" / f"{proj.name}.mp4").exists():
        sys.exit("render first: python scripts/render.py " + args.project)
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = gh_repo()
    if token and repo and not args.git:
        try:
            release(proj, repo, token)
            return
        except Exception as e:
            print(f"release upload failed ({e}) -> falling back to git copy")
    git_copy(proj)


if __name__ == "__main__":
    main()
