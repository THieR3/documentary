"""Create projects/_test with synthetic 'source footage' (ffmpeg test patterns + tones) and a short
timeline exercising every visual/overlay type. Used to smoke-test the pipeline without downloads:

  python scripts/make_test_project.py
  python scripts/fetch_sources.py _test --no-transcribe
  python scripts/build_props.py _test        # (no tts needed: the test timeline has no 'vo')
  python scripts/render.py _test --stills
  python scripts/render.py _test --preview --sec 30
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROJECTS, run, save_json  # noqa: E402

p = PROJECTS / "_test"
for sub in ("media/sources", "media/assets", "media/music"):
    (p / sub).mkdir(parents=True, exist_ok=True)

run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30:duration=40", "-f", "lavfi", "-i", "sine=frequency=330:duration=40",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", p / "media/sources/raw_a.mp4"])
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "mandelbrot=size=1440x1080:rate=30", "-f", "lavfi", "-i", "sine=frequency=520:duration=30",
     "-t", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", p / "media/sources/raw_b.mp4"])
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "gradients=size=1920x1080:n=4:seed=3", "-frames:v", "1", p / "media/assets/map.jpg"])
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=110:duration=60", "-af", "volume=0.4", p / "media/music/test.mp3"])

save_json(p / "sources.json", [
    {"id": "arch_a", "file": "media/sources/raw_a.mp4", "title": "Test pattern A", "credit": "Archives : Test A", "license": "test"},
    {"id": "arch_b", "file": "media/sources/raw_b.mp4", "title": "Test pattern B (4:3)", "credit": "Extrait : Doc B (1998)", "license": "test"},
])
save_json(p / "timeline.json", {
    "meta": {"title": "Test", "fps": 30, "width": 1920, "height": 1080, "captions": True, "music": {"src": "music/test.mp3", "volume": 0.2}},
    "chapters": [
        {"title": "Ouverture", "segments": [
            {"duration": 4, "visual": {"type": "title", "title": "Le Titre", "subtitle": "Un documentaire test", "bg": {"type": "video", "source": "arch_a", "in": 2}}},
            {"duration": 6, "shots": [{"type": "video", "source": "arch_a", "in": 5, "motion": "zoom-in", "dur": 3},
                                      {"type": "video", "source": "arch_b", "in": 3, "motion": "pan-left", "grade": "archive"}],
             "overlays": [{"type": "lowerThird", "at": 0.5, "dur": 2.5, "title": "Jean Dupont", "subtitle": "Historien"}]},
            {"bite": {"source": "arch_b", "in": 10, "out": 15, "subtitle": "Ceci est une citation originale traduite."},
             "overlays": [{"type": "highlight", "at": 0.3, "dur": 3, "box": [30, 25, 30, 40], "label": "Le détail", "shape": "circle"}]},
        ]},
        {"title": "Chapitre un", "segments": [
            {"duration": 3.5, "visual": {"type": "chapter", "number": 1, "title": "Les débuts", "bg": {"type": "video", "source": "arch_a", "in": 20}}, "transition": "dip"},
            {"duration": 5, "visual": {"type": "video", "source": "arch_a", "in": 22, "motion": "drift", "grade": "bw", "letterbox": True},
             "overlays": [{"type": "stat", "at": 0.4, "dur": 4, "value": 1250000, "suffix": " km", "label": "parcourus", "position": "left"},
                          {"type": "date", "at": 0, "dur": 3, "text": "1969"}]},
            {"duration": 5, "visual": {"type": "map", "src": "assets/map.jpg", "pins": [{"x": 40, "y": 45, "label": "Paris"}, {"x": 62, "y": 58, "label": "Lyon", "at": 1.5}]}},
            {"duration": 5, "visual": {"type": "timeline", "events": [{"year": "1957", "label": "Spoutnik"}, {"year": "1961", "label": "Gagarine"}, {"year": "1969", "label": "Apollo 11"}], "active": 2}},
            {"duration": 4, "visual": {"type": "quote", "text": "Un petit pas pour l'homme", "author": "N. Armstrong"}, "transition": "whip"},
            {"duration": 4, "visual": {"type": "video", "source": "arch_b", "in": 20}, "sourceVolume": 0.3,
             "overlays": [{"type": "kinetic", "at": 0.3, "dur": 3.4, "lines": ["Une", "course", "folle"]}]},
        ]},
    ],
})
print(f"test project -> {p}")
