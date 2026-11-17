"""The version is defined once, in the root pyproject.toml.

The component manifest and ``package.json`` carry no version of their own:
Streamlit falls back to the installed distribution's version for the
manifest, and the frontend package is private and never published.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_LINE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def test_root_pyproject_has_a_static_version() -> None:
    # A regex, not tomllib: tomllib is not in Python 3.10.
    match = VERSION_LINE.search((ROOT / "pyproject.toml").read_text("utf-8"))
    assert match is not None


def test_component_manifest_has_no_version_of_its_own() -> None:
    manifest = (ROOT / "streamlit_a2ui" / "pyproject.toml").read_text("utf-8")
    assert VERSION_LINE.search(manifest) is None


def test_package_json_has_no_version() -> None:
    package = ROOT / "streamlit_a2ui" / "frontend" / "package.json"
    assert "version" not in json.loads(package.read_text("utf-8"))
