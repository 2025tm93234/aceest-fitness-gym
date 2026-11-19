#!/usr/bin/env bash
# Publish the cluster's ingress on a host port so it is reachable from outside the VM.
#   sudo -u jenkins -H scripts/expose.sh start|stop|status       (PORT defaults to 8088)
# Endpoints afterwards:  http://<host>:8088/{rolling,bluegreen,canary,shadow,ab}/version
set -euo pipefail
PORT="${PORT:-8088}"; PIDFILE="/tmp/aceest-portforward.pid"; LOG="/tmp/aceest-portforward.log"
case "${1:-status}" in
  start)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then echo "already running"; exit 0; fi
    nohup bash -c "while true; do kubectl -n ingress-nginx port-forward --address 0.0.0.0 svc/ingress-nginx-controller ${PORT}:80; sleep 2; done" >"$LOG" 2>&1 &
    echo $! > "$PIDFILE"; sleep 3
    echo "ingress published on port ${PORT} (pid $(cat "$PIDFILE"))"
    curl -s -o /dev/null -w "local check: HTTP %{http_code}\n" "http://localhost:${PORT}/rolling/health" || true ;;
  stop)
    if [ -f "$PIDFILE" ]; then pkill -P "$(cat "$PIDFILE")" || true; kill "$(cat "$PIDFILE")" 2>/dev/null || true; rm -f "$PIDFILE"; fi
    echo "stopped" ;;
  status)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then echo "running on port ${PORT}"; else echo "not running"; fi ;;
  *) echo "usage: $0 start|stop|status"; exit 1 ;;
esac
