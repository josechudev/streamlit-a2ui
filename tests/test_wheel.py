"""Guards on the built wheel: what ships, and what must never ship.

Builds the wheel with ``uv build`` from the current tree, so run
``npm run build`` in ``streamlit_a2ui/frontend`` first.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from collections.abc import Iterator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD = "streamlit_a2ui/frontend/build/"
CAPABILITIES = "streamlit_a2ui/renderer_capabilities.json"

# A URL that the browser would load as code, a stylesheet or a font.
REMOTE_ASSET = re.compile(
    r"""(?:src\s*=|import\s*\(|import\s+[^;'"]*from|url\s*\(|@import)\s*["']?https?://"""
    r"""|https?://[^\s"'`)]+\.(?:m?js|css|woff2?|ttf|otf)\b"""
    r"""|\b(?:cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|esm\.sh"""
    r"""|cdn\.skypack\.dev|fonts\.googleapis\.com|fonts\.gstatic\.com)\b""",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Iterator[zipfile.ZipFile]:
    if not (ROOT / CAPABILITIES).is_file() or not (ROOT / BUILD).is_dir():
        pytest.fail(
            "frontend not built: run `npm run build` in streamlit_a2ui/frontend"
        )
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv is required to build the wheel")
    out = tmp_path_factory.mktemp("dist")
    build = subprocess.run(
        [uv, "build", "--wheel", "--out-dir", str(out), str(ROOT)],
        check=False,
        capture_output=True,
        text=True,
    )
    if build.returncode != 0:
        pytest.fail(f"uv build failed:\n{build.stderr[-4000:]}")
    (path,) = out.glob("*.whl")
    with zipfile.ZipFile(path) as archive:
        yield archive


def test_wheel_ships_the_frontend_bundle(wheel: zipfile.ZipFile) -> None:
    names = wheel.namelist()
    assert [n for n in names if re.fullmatch(rf"{BUILD}index-[^/]+\.js", n)]
    assert [n for n in names if re.fullmatch(rf"{BUILD}index-[^/]+\.css", n)]
    assert "streamlit_a2ui/pyproject.toml" in names


def test_wheel_ships_the_generated_capabilities(wheel: zipfile.ZipFile) -> None:
    shipped = json.loads(wheel.read(CAPABILITIES))
    assert shipped == json.loads((ROOT / CAPABILITIES).read_text(encoding="utf-8"))
    assert not [n for n in wheel.namelist() if n.startswith(BUILD) and "capabilit" in n]


def test_wheel_ships_third_party_licenses(wheel: zipfile.ZipFile) -> None:
    text = wheel.read("streamlit_a2ui/THIRD_PARTY_LICENSES.txt").decode("utf-8")
    for package in ("@a2ui/web_core@0.15.0", "dompurify@3.4.18", "react@", "lit@"):
        assert package in text


def test_wheel_has_no_source_maps(wheel: zipfile.ZipFile) -> None:
    assert not [n for n in wheel.namelist() if n.endswith(".map")]
    for name in wheel.namelist():
        if name.startswith(BUILD):
            assert b"sourceMappingURL=" not in wheel.read(name), name


def test_wheel_loads_no_remote_code_or_fonts(wheel: zipfile.ZipFile) -> None:
    for name in wheel.namelist():
        if name.endswith((".js", ".css", ".html", ".json")):
            text = wheel.read(name).decode("utf-8")
            match = REMOTE_ASSET.search(text)
            assert match is None, f"{name}: {match and match.group(0)}"


@pytest.mark.parametrize(
    "text",
    [
        '<script src="https://cdn.example.org/x.js">',
        'import("https://esm.sh/react")',
        "@import url(https://fonts.googleapis.com/css2?family=Inter);",
        "src: url('https://example.org/font.woff2')",
        "https://unpkg.com/lit",
    ],
)
def test_remote_asset_pattern_catches(text: str) -> None:
    assert REMOTE_ASSET.search(text)


@pytest.mark.parametrize(
    "text",
    [
        '"https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"',
        '"http://www.w3.org/2000/svg"',
        "`http://${e.url}`",
        '"https://example.com/poodle.jpg"',
    ],
)
def test_remote_asset_pattern_allows(text: str) -> None:
    assert REMOTE_ASSET.search(text) is None
