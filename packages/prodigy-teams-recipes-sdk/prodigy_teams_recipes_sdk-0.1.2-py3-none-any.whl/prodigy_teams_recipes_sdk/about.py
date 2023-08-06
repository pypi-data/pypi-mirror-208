"""
This file originates in shared/shared_about.py, and
is copied verbatim into the different projects. It should
not be edited directly, edit the shared version and replicate
it everywhere.
"""

import json
from pathlib import Path

from .version.read_version import read_version

PWD = Path(__file__).parent


with (PWD / "about.json").open("r", encoding="utf8") as file_:
    _about_data = json.load(file_)


__name__ = _about_data["name"]
__title__ = _about_data.get("title", "")
__description__ = _about_data.get("description", "")
__summary__ = _about_data.get("summary", "")
__version__ = read_version(PWD / "version")
__prog__ = _about_data.get("prog", "")
