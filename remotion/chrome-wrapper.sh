#!/usr/bin/env bash
# Launches a local Chrome for Remotion. Remotion forces --no-proxy-server; in sandboxes where
# outbound HTTPS must go through HTTPS_PROXY (e.g. Claude Code cloud), strip those flags and use the proxy.
real="${REMOTION_REAL_BROWSER:?}"
args=()
for a in "$@"; do
  case "$a" in
    --no-proxy-server|--proxy-server=*|--proxy-bypass-list=*) [ -n "$HTTPS_PROXY" ] || args+=("$a") ;;
    *) args+=("$a") ;;
  esac
done
[ -n "$HTTPS_PROXY" ] && args+=("--proxy-server=$HTTPS_PROXY" "--proxy-bypass-list=localhost;127.0.0.1;[::1]")
exec "$real" "${args[@]}"
