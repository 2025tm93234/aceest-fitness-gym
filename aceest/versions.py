"""Release catalogue: which feature modules each ACEest version ships.

Every entry lists only the modules ADDED in that release; a version includes
everything from earlier releases (cumulative). The module sets are closed under
the code/table dependencies between modules, so every version starts cleanly.

Versions 2.1.2 and 3.0.1 are byte-identical to 2.0.1 and 2.2.4 in the original
ACEest source drop, so they are aliases (same image, extra Docker tag).
"""
from collections import OrderedDict

RELEASES = OrderedDict([
    ("1.0",   ["health", "programs"]),
    ("1.1",   ["clients"]),
    ("1.1.2", ["reports"]),
    ("2.0.1", ["progress"]),
    ("2.2.1", ["bmi"]),
    ("2.2.4", ["metrics", "workouts", "dashboard"]),
    ("3.1.2", ["auth", "membership", "program_generator"]),
    ("3.2.4", ["analytics"]),
])

ALIASES = {"2.1.2": "2.0.1", "3.0.1": "2.2.4"}
LATEST = "3.2.4"


def canonical(version):
    """Resolve an alias to its release; raise ValueError for unknown versions."""
    version = ALIASES.get(version, version)
    if version not in RELEASES:
        known = ", ".join(list(RELEASES) + list(ALIASES))
        raise ValueError(f"unknown ACEest version {version!r}; known: {known}")
    return version


def module_names(version):
    """Module names shipped by `version` (aliases allowed), in build order."""
    target = canonical(version)
    names = []
    for release, added in RELEASES.items():
        names.extend(added)
        if release == target:
            break
    return names
