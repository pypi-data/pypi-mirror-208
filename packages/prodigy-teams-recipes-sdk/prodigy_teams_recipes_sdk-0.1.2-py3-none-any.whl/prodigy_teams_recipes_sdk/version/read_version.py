"""Script and module to interpret version.txt

N.B.

Make sure this file doesn't have any Python
dependencies and doesn't import from the rest of the library
at all. That way it can be invoked:

* As an import within the about.py of the different modules
* In a subprocess during the setup.py
* As a script in CI actions.

We want to make sure you can run like:

    python prodigy_teams_pam/versioning.py

N.B. 2:

This script is defined in shared/, and copied into the
different packages by:

    pdcli dev sync-shared

Don't modify the copies in the libraries.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Tuple


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, string: str):
        # It's a bit tricky to import packaging here, as we'd need to set it in
        # the setup_requires and stuff. We're not supporting alpha versions and
        # stuff anyway, so just assume we can parse it as three ints.
        # We need to interpret the version as ints, not a str, otherwise it won't
        # sort correctly.
        version = [int(piece) for piece in string.split(".")]
        while len(version) < 3:
            version.append(0)
        return cls(*version)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass
class VersionIncrement:
    version: Version
    increment: Literal["", "major", "minor", "patch"]

    @classmethod
    def from_string(cls, string: str) -> "VersionIncrement":
        pieces = string.split("_")
        if len(pieces) != 4:
            raise ValueError(f"Cannot parse version increment: {string}")
        version_str, _, instruction, _2 = pieces
        assert instruction in ("", "major", "minor", "patch")
        return cls(Version.from_string(version_str), instruction)

    @property
    def sort_key(self) -> Tuple[int, int, int, int]:
        increment_priority = {"": 4, "major": 3, "minor": 2, "patch": 1}
        return (
            self.version.major,
            self.version.minor,
            self.version.patch,
            increment_priority[self.increment],
        )

    def compute(self, current: Optional[Version]) -> Version:
        if current is None:
            current = self.version
        if self.increment == "":
            return current
        elif self.increment == "major":
            return Version(current.major + 1, 0, 0)
        elif self.increment == "minor":
            return Version(current.major, current.minor + 1, 0)
        elif self.increment == "patch":
            return Version(current.major, current.minor, current.patch + 1)
        else:
            raise ValueError(f"Cannot parse version instruction: {self.increment}")


def read_version(path: Path) -> str:
    version_incs = [
        VersionIncrement.from_string(p.name)
        for p in path.iterdir()
        if p.suffix != ".py" and not p.is_dir()
    ]
    version_incs.sort(key=lambda v: v.sort_key)
    current_version = None
    for version_inc in version_incs:
        current_version = version_inc.compute(current_version)
    return str(current_version)


if __name__ == "__main__":
    import argparse

    P = argparse.ArgumentParser(
        description="Interpret a version.txt and print the version"
    )
    P.add_argument("path", type=Path, help="Path to the version.txt")
    A = P.parse_args()
    print(read_version(A.path))
