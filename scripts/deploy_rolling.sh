#!/usr/bin/env bash
# Jenkins CD step: roll the cluster to <version> with zero downtime; roll back on any failure.
#   IMAGE_REPO=<dockerhub-user>/aceest-fitness scripts/deploy_rolling.sh <version>
set -euo pipefail
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"; need_repo
version="${1:?usage: deploy_rolling.sh <version>}"
cd "$ROOT"

kubectl apply -f k8s/00-namespace.yaml
if ! kubectl -n "$NS" get deploy aceest-rolling >/dev/null 2>&1; then
  echo "first deployment: creating aceest-rolling at ${version}"
  STABLE="$version" render k8s/10-rolling.yaml | kubectl apply -f -
fi

rollback() {
  echo "!! deployment of ${version} failed - rolling back to the previous revision"
  kubectl -n "$NS" rollout undo deploy/aceest-rolling
  kubectl -n "$NS" rollout status deploy/aceest-rolling --timeout=180s
  exit 1
}

kubectl -n "$NS" set image deploy/aceest-rolling aceest="${IMAGE_REPO}:${version}"
kubectl -n "$NS" rollout status deploy/aceest-rolling --timeout=180s || rollback

# In-cluster smoke test of the new release.
kubectl -n "$NS" run "smoke-${RANDOM}" --rm -i --restart=Never --quiet --image=curlimages/curl:8.10.1 -- \
  sh -c "curl -fsS http://aceest-rolling/health && echo && curl -fsS http://aceest-rolling/version && echo" || rollback

kubectl -n "$NS" rollout history deploy/aceest-rolling
echo "deployed ${IMAGE_REPO}:${version}"
