#!/usr/bin/env bash
# Optional fallback when inbound ports are blocked: a free Cloudflare quick tunnel
# (outbound-only) publishes http://localhost:8088 on a public https://*.trycloudflare.com URL.
# The URL changes every run; keep this terminal open while the endpoint is being checked.
set -euo pipefail
BIN="$HOME/bin"; mkdir -p "$BIN"
if [ ! -x "$BIN/cloudflared" ]; then
  curl -fsSL -o "$BIN/cloudflared" \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  chmod +x "$BIN/cloudflared"
fi
exec "$BIN/cloudflared" tunnel --no-autoupdate --url "http://localhost:${PORT:-8088}"
