#!/usr/bin/env bash
# Shared helpers: render a manifest template with the image repo and release tags.
NS="${NS:-aceest}"
STABLE="${STABLE:-3.1.2}"
NEW="${NEW:-3.2.4}"
# shellcheck disable=SC2034  # used by the scripts that source this file
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

need_repo() {
  : "${IMAGE_REPO:?Set IMAGE_REPO, e.g. export IMAGE_REPO=<dockerhub-user>/aceest-fitness}"
}

render() {  # render <manifest-file>
  need_repo
  sed -e "s|__IMAGE_REPO__|${IMAGE_REPO}|g" -e "s|__STABLE__|${STABLE}|g" -e "s|__NEW__|${NEW}|g" "$1"
}
