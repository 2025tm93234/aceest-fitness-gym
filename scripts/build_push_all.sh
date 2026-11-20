#!/usr/bin/env bash
# Build every ACEest release as its own image and push all tags to Docker Hub.
#   export IMAGE_REPO=<dockerhub-user>/aceest-fitness ; docker login -u <dockerhub-user>
#   scripts/build_push_all.sh            # build + push      PUSH=false scripts/build_push_all.sh  # build only
# Keep RELEASES / ALIASES in step with aceest/versions.py (tests/test_release_script.py checks it).
set -euo pipefail
# shellcheck source=lib.sh
. "$(dirname "$0")/lib.sh"; need_repo
RELEASES=(1.0 1.1 1.1.2 2.0.1 2.2.1 2.2.4 3.1.2 3.2.4)
ALIASES=("2.1.2:2.0.1" "3.0.1:2.2.4")   # alias:release - identical code, same image, extra tag
LATEST="3.2.4"
cd "$ROOT"

for v in "${RELEASES[@]}"; do
  echo "== building ${IMAGE_REPO}:${v}"
  docker build --quiet --build-arg APP_VERSION="$v" -t "${IMAGE_REPO}:${v}" .
done
for pair in "${ALIASES[@]}"; do
  docker tag "${IMAGE_REPO}:${pair#*:}" "${IMAGE_REPO}:${pair%%:*}"
done
docker tag "${IMAGE_REPO}:${LATEST}" "${IMAGE_REPO}:latest"

tags=("${RELEASES[@]}" "${ALIASES[@]%%:*}" latest)
if [ "${PUSH:-true}" = "true" ]; then
  for t in "${tags[@]}"; do docker push "${IMAGE_REPO}:${t}"; done
fi
echo "tags: ${tags[*]}"
