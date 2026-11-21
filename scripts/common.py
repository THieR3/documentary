"""Shared helpers for the documentary pipeline (stdlib only)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REMOTION = ROOT / "remotion"
PROJECTS = ROOT / "projects"


def project_dir(slug_or_path: str) -> Path:
    p = Path(slug_or_path)
    if not p.is_absolute() and not p.exists():
        p = PROJECTS / slug_or_path
    p = p.resolve()
    if not p.exists():
        sys.exit(f"project not found: {p}")
    for sub in ("media/sources", "media/assets", "media/music", "media/vo", "build", "out"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: Path, default=None):
    if not path.exists():
        if default is not None:
            return default
        sys.exit(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run(cmd: list[str], check: bool = True, capture: bool = False, cwd: Path | None = None) -> subprocess.CompletedProcess:
    print("$", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd], check=check, cwd=cwd, text=True, capture_output=capture)


def need(binary: str) -> str:
    path = shutil.which(binary)
    if not path:
        sys.exit(f"'{binary}' not found on PATH - run scripts/setup.sh first")
    return path


def probe(path: Path) -> dict:
    """Return duration (s), width, height, fps, has_audio for a media file."""
    out = run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
        capture=True,
    ).stdout
    info = json.loads(out)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    fps = 0.0
    if v and v.get("avg_frame_rate", "0/0") != "0/0":
        n, d = v["avg_frame_rate"].split("/")
        fps = float(n) / float(d) if float(d) else 0.0
    return {
        "duration": float(info.get("format", {}).get("duration", 0) or 0),
        "width": int(v["width"]) if v else 0,
        "height": int(v["height"]) if v else 0,
        "fps": round(fps, 3),
        "has_audio": a is not None,
    }


def ts(sec: float) -> str:
    sec = max(0.0, sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
