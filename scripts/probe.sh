#!/usr/bin/env bash
# Count which release answers N requests:  probe.sh <url> [count] ["Header: value"]
# Example: probe.sh http://localhost:8088/canary/version 20
#          probe.sh http://localhost:8088/ab/version 5 "X-Experiment: B"
set -euo pipefail
url="${1:?usage: probe.sh <url> [count] [header]}"; n="${2:-20}"; header="${3:-}"
for _ in $(seq "$n"); do
  if [ -n "$header" ]; then
    curl -s -D - -o /dev/null -H "$header" "$url"
  else
    curl -s -D - -o /dev/null "$url"
  fi
done | tr -d '\r' \
  | awk -F': ' 'tolower($1)=="x-app-version"{c[$2]++} END{for(v in c) printf "  release %-8s answered %d request(s)\n", v, c[v]}' \
  | sort
