"""The image-build script must list exactly the releases defined in aceest/versions.py."""
import re
from pathlib import Path

from aceest import versions

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_push_all.sh"


def test_build_script_matches_release_catalogue():
    text = SCRIPT.read_text()
    releases = re.search(r"^RELEASES=\((.*?)\)", text, re.M).group(1).split()
    aliases = re.search(r"^ALIASES=\((.*?)\)", text, re.M).group(1).replace('"', "").split()
    latest = re.search(r'^LATEST="(.*?)"', text, re.M).group(1)
    assert releases == list(versions.RELEASES)
    assert dict(a.split(":") for a in aliases) == versions.ALIASES
    assert latest == versions.LATEST
