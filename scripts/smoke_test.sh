#!/usr/bin/env bash
# Start an image, check /health and that /version reports the expected release.
#   scripts/smoke_test.sh <image:tag> <expected-version>
set -euo pipefail
image="${1:?usage: smoke_test.sh <image> <expected-version>}"; expected="${2:?expected version}"
cid="$(docker run -d -P "$image")"
trap 'docker rm -f "$cid" >/dev/null 2>&1 || true' EXIT
port="$(docker port "$cid" 5000/tcp | head -1 | awk -F: '{print $NF}')"
for _ in $(seq 30); do curl -fs "http://localhost:${port}/health" >/dev/null && break; sleep 1; done
body="$(curl -fs "http://localhost:${port}/version")"
echo "$body"
python3 -c "import json,sys; d=json.loads(sys.argv[1]); assert d['version']==sys.argv[2], d; print('smoke test OK: ' + d['version'])" "$body" "$expected"
