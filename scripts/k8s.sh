#!/usr/bin/env bash
# Deployment-strategy helper for the ACEest cluster (Minikube).
#   export IMAGE_REPO=<dockerhub-user>/aceest-fitness    # STABLE / NEW default to 3.1.2 / 3.2.4
#   scripts/k8s.sh apply all|rolling|bluegreen|canary|shadow|ab
#   scripts/k8s.sh status
#   scripts/k8s.sh rolling-update <version>      scripts/k8s.sh rollback
#   scripts/k8s.sh bluegreen-switch blue|green   scripts/k8s.sh canary-weight <0-100>
#   scripts/k8s.sh delete all|<strategy>
set -euo pipefail
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"

manifest_for() {
  case "$1" in
    rolling)   echo "$ROOT/k8s/10-rolling.yaml" ;;
    bluegreen) echo "$ROOT/k8s/20-bluegreen.yaml" ;;
    canary)    echo "$ROOT/k8s/30-canary.yaml" ;;
    shadow)    echo "$ROOT/k8s/40-shadow.yaml" ;;
    ab)        echo "$ROOT/k8s/50-abtest.yaml" ;;
    *) echo "unknown strategy: $1 (rolling|bluegreen|canary|shadow|ab|all)" >&2; return 1 ;;
  esac
}
ALL="rolling bluegreen canary shadow ab"

cmd="${1:-help}"; shift || true
case "$cmd" in
  apply)
    kubectl apply -f "$ROOT/k8s/00-namespace.yaml"
    for s in $([ "${1:-all}" = all ] && echo "$ALL" || echo "$1"); do
      render "$(manifest_for "$s")" | kubectl apply -f -
    done ;;
  delete)
    for s in $([ "${1:-all}" = all ] && echo "$ALL" || echo "$1"); do
      render "$(manifest_for "$s")" | kubectl delete --ignore-not-found -f -
    done ;;
  status)
    kubectl -n "$NS" get deploy,svc,ingress -o wide
    kubectl -n "$NS" get pods -L app ;;
  rolling-update)
    need_repo
    version="${1:?usage: rolling-update <version>}"
    kubectl -n "$NS" set image deploy/aceest-rolling aceest="${IMAGE_REPO}:${version}"
    kubectl -n "$NS" rollout status deploy/aceest-rolling --timeout=180s
    kubectl -n "$NS" rollout history deploy/aceest-rolling ;;
  rollback)
    kubectl -n "$NS" rollout undo deploy/aceest-rolling
    kubectl -n "$NS" rollout status deploy/aceest-rolling --timeout=180s
    kubectl -n "$NS" get deploy aceest-rolling -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}' ;;
  bluegreen-switch)
    slot="${1:?usage: bluegreen-switch blue|green}"
    kubectl -n "$NS" patch svc aceest-bluegreen \
      -p "{\"spec\":{\"selector\":{\"app\":\"aceest-bluegreen\",\"slot\":\"${slot}\"}}}"
    kubectl -n "$NS" get svc aceest-bluegreen -o jsonpath='{.spec.selector}{"\n"}' ;;
  canary-weight)
    weight="${1:?usage: canary-weight <0-100>}"
    kubectl -n "$NS" annotate ingress aceest-canary-weighted --overwrite \
      "nginx.ingress.kubernetes.io/canary-weight=${weight}"
    echo "canary weight is now ${weight}%" ;;
  *)
    sed -n '2,9p' "$0" ;;
esac
