#!/usr/bin/env bash
# Wait for the SonarQube analysis task, then fail unless the quality gate is OK.
# Needs: SONAR_HOST_URL, SONAR_TOKEN, and .scannerwork/report-task.txt from the scanner run.
set -euo pipefail
: "${SONAR_HOST_URL:?}" "${SONAR_TOKEN:?}"
task_url="$(grep '^ceTaskUrl=' .scannerwork/report-task.txt | cut -d= -f2-)"
json() { python3 -c "import sys,json; d=json.load(sys.stdin); print($1)"; }

status=""
for _ in $(seq 60); do
  status="$(curl -fsS -u "${SONAR_TOKEN}:" "$task_url" | json "d['task']['status']")"
  case "$status" in
    SUCCESS) break ;;
    FAILED|CANCELED) echo "SonarQube analysis task ${status}"; exit 1 ;;
  esac
  sleep 5
done
[ "$status" = "SUCCESS" ] || { echo "Timed out waiting for SonarQube"; exit 1; }

analysis="$(curl -fsS -u "${SONAR_TOKEN}:" "$task_url" | json "d['task']['analysisId']")"
gate="$(curl -fsS -u "${SONAR_TOKEN}:" "${SONAR_HOST_URL}/api/qualitygates/project_status?analysisId=${analysis}" \
        | json "d['projectStatus']['status']")"
echo "SonarQube quality gate: ${gate}   (${SONAR_HOST_URL}/dashboard?id=aceest-fitness-gym)"
[ "$gate" = "OK" ]
