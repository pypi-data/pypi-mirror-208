#!/usr/bin/env python
"""
This file originates in shared/shared_about.py, and
is copied verbatim into the different projects. It should
not be edited directly, edit the shared version and replicate
it everywhere.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from setuptools import find_packages, setup

PWD = Path(__file__).parent


def read_about(path: Path) -> Dict[str, Any]:
    with (path / "about.json").open("r", encoding="utf8") as file_:
        data = json.loads(file_.read())
    return data


def read_requirements(path: Path) -> List[str]:
    # Read in requirements and split into packages and URLs
    requirements_path = path / "requirements.in"
    with requirements_path.open("r", encoding="utf8") as f:
        requirements = [line.strip() for line in f]
    return requirements


def read_version(path: Path) -> str:
    # Execute the 'read_version.py' script from within the package.
    # We do this as a subprocess to avoid importing the package, which
    # would require us to have the package's install requirements as setup
    # requirements.
    r = subprocess.run(
        [
            sys.executable,
            str(path / "version" / "read_version.py"),
            str(path / "version"),
        ],
        capture_output=True,
        check=True,
        encoding="utf8",
    )
    return r.stdout


def setup_package():
    root = PWD.resolve()
    packages = [
        p for p in find_packages() if not p.startswith("tests") and p != "migrations"
    ]
    package_name = packages[0]
    package_path = root / package_name
    about = read_about(root / package_name)
    requirements = read_requirements(root)
    version = read_version(root / package_name)
    package_data = about.get("package_data", [])
    package_data_dirs = about.get("package_data_dirs", [])
    if "version" not in package_data_dirs:
        package_data_dirs.append("version")
    for directory in package_data_dirs:
        # Package data doesn't properly support recursive globs, so we fix them.
        package_data.extend(
            [
                str(path.relative_to(package_path.absolute()))
                for path in (package_path / directory).glob("**/*")
                if path.parent != ".pyc" and "__pycache__" not in path.parts
            ]
        )
    # Ensure the about.json is packaged
    if "about.json" not in package_data:
        package_data.append("about.json")
    setup(
        author=about.get("author", "ExplosionAI GmbH"),
        author_email=about.get("email", "contact@explosion.ai"),
        url=about.get("uri", "https://github.com/explosion/prodigy-teams"),
        license=about.get("license", "All rights reserved"),
        name=about["name"],
        description=about["summary"],
        version=version,
        packages=packages,
        package_data={package_name: package_data},
        entry_points=about.get("entry_points", {}),
        install_requires=requirements,
        scripts=[],
        zip_safe=False,
    )


if __name__ == "__main__":
    setup_package()
