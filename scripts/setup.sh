#!/usr/bin/env bash
# Idempotent environment setup for Claude Code cloud sessions (Ubuntu). Safe to re-run.
set -uo pipefail
cd "$(dirname "$0")/.."

log() { echo "[setup] $*"; }
SUDO=""; [ "$(id -u)" != "0" ] && command -v sudo >/dev/null && SUDO="sudo"

if ! command -v ffmpeg >/dev/null; then
  log "installing ffmpeg + Chrome headless deps"
  $SUDO apt-get update -qq || true
  $SUDO apt-get install -y -qq ffmpeg fonts-dejavu-core libnss3 libdbus-1-3 libatk1.0-0 libgbm1 libasound2t64 \
    libxrandr2 libxkbcommon0 libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2 \
    >/dev/null 2>&1 || $SUDO apt-get install -y -qq ffmpeg fonts-dejavu-core libnss3 libgbm1 libasound2 libxkbcommon0 \
    libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2 libxcomposite1 libxdamage1 libxrandr2 >/dev/null 2>&1 || true
fi

if ! python3 -c "import edge_tts, yt_dlp" 2>/dev/null; then
  log "pip install requirements"
  python3 -m pip install -q -r requirements.txt 2>/dev/null || python3 -m pip install -q --break-system-packages -r requirements.txt || true
fi
# yt-dlp breaks often against YouTube: keep it fresh
python3 -m pip install -q -U yt-dlp 2>/dev/null || python3 -m pip install -q -U --break-system-packages yt-dlp 2>/dev/null || true

if [ ! -d remotion/node_modules ]; then
  log "npm install (remotion)"
  (cd remotion && (npm ci --no-audit --no-fund || npm install --no-audit --no-fund)) >/dev/null 2>&1 || log "npm install failed"
fi
(cd remotion && npx --yes remotion browser ensure >/dev/null 2>&1) || log "chrome-headless-shell download failed (will retry at render)"

for b in ffmpeg ffprobe node python3 yt-dlp; do
  command -v "$b" >/dev/null && log "ok  $b" || log "MISSING $b"
done
exit 0
