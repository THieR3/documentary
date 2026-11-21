"""Narration: every segment with a "vo" text in timeline.json -> media/vo/<id>.mp3 + word timings.

Engines (timeline.meta.voice.engine):
  edge        free Microsoft neural voices via edge-tts (default; e.g. fr-FR-HenriNeural, fr-FR-DeniseNeural,
              fr-FR-RemyMultilingualNeural, en-US-AndrewNeural). Needs outbound internet.
  elevenlabs  needs ELEVENLABS_API_KEY; meta.voice.name = voice id; model via meta.voice.model.
Cached by text+voice hash, so editing one paragraph only regenerates that one.
Writes build/vo.json: {segment_id: {file, duration, words:[{text,start,end}]}} (seconds, segment-relative)

Usage: python scripts/tts.py <project> [--force]
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, probe, project_dir, save_json  # noqa: E402


async def edge_tts(text: str, voice: str, rate: str, pitch: str, out: Path) -> list[dict]:
    import edge_tts  # type: ignore

    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(out, "wb") as fh:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                st = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": round(st, 3), "end": round(st + chunk["duration"] / 1e7, 3)})
    return words


def elevenlabs(text: str, voice: str, model: str, out: Path) -> list[dict]:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY not set")
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": model, "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.2}}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    out.write_bytes(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or {}
    chars, starts, ends = al.get("characters", []), al.get("character_start_times_seconds", []), al.get("character_end_times_seconds", [])
    words, cur, cs = [], "", None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append({"text": cur, "start": cs, "end": e})
            cur, cs = "", None
        else:
            cs = s if cs is None else cs
            cur += c
            last_e = e
    if cur:
        words.append({"text": cur, "start": cs, "end": last_e})
    return words


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    proj = project_dir(args.project)
    tl = load_json(proj / "timeline.json")
    voice = {"engine": "edge", "name": "fr-FR-HenriNeural", "rate": "-4%", "pitch": "+0Hz", **tl.get("meta", {}).get("voice", {})}
    vo_path = proj / "build" / "vo.json"
    cache = load_json(vo_path, default={})
    result = {}
    total = 0.0
    for ci, ch in enumerate(tl.get("chapters", [])):
        for si, seg in enumerate(ch.get("segments", [])):
            text = (seg.get("vo") or "").strip()
            if not text:
                continue
            sid = seg.get("id") or f"c{ci}s{si}"
            h = hashlib.sha1(json.dumps([text, voice], sort_keys=True).encode()).hexdigest()[:12]
            out = proj / "media" / "vo" / f"{sid}.mp3"
            prev = cache.get(sid)
            if prev and prev.get("hash") == h and out.exists() and not args.force:
                result[sid] = prev
                total += prev["duration"]
                continue
            print(f"[tts] {sid}: {text[:70]}...")
            if voice["engine"] == "elevenlabs":
                words = elevenlabs(text, voice["name"], voice.get("model", "eleven_multilingual_v2"), out)
            else:
                words = asyncio.run(edge_tts(text, voice["name"], voice["rate"], voice["pitch"], out))
            dur = probe(out)["duration"]
            result[sid] = {"file": f"vo/{sid}.mp3", "duration": round(dur, 3), "words": words, "hash": h}
            total += dur
            save_json(vo_path, {**cache, **result})
    save_json(vo_path, result)
    wc = sum(len((s.get("vo") or "").split()) for ch in tl.get("chapters", []) for s in ch.get("segments", []))
    print(f"narration: {len(result)} clips, {total / 60:.1f} min, {wc} words ({wc / max(1e-6, total / 60):.0f} wpm)")


if __name__ == "__main__":
    main()
