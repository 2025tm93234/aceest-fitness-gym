"""The image-build script must list exactly the releases defined in aceest/versions.py.

scripts/ is not copied into the Docker image, so this check only runs in a full checkout
(Jenkins and local runs); inside the container it is skipped.
"""
import re
from pathlib import Path

import pytest

from aceest import versions

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_push_all.sh"

pytestmark = pytest.mark.skipif(
    not SCRIPT.exists(), reason="scripts/ is not part of the container image"
)


def test_build_script_matches_release_catalogue():
    text = SCRIPT.read_text()
    releases = re.search(r"^RELEASES=\((.*?)\)", text, re.M).group(1).split()
    aliases = re.search(r"^ALIASES=\((.*?)\)", text, re.M).group(1).replace('"', "").split()
    latest = re.search(r'^LATEST="(.*?)"', text, re.M).group(1)
    assert releases == list(versions.RELEASES)
    assert dict(a.split(":") for a in aliases) == versions.ALIASES
    assert latest == versions.LATEST
