"""Browser smoke test: the action round trip in ``examples/basic_app.py``.

One test only. It guards against a Streamlit or ``@a2ui/*`` release silently
breaking the Components v2 behaviour this package depends on: the bundle
loads, the surface renders, a click comes back to Python once, and the
agent's reply is drawn.

Not part of the default ``pytest`` run. Needs ``npm run build`` first, then::

    uv pip install pytest-playwright
    .venv/bin/playwright install chromium
    .venv/bin/pytest e2e
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Page, expect

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "basic_app.py"
STARTUP_SECONDS = 60
TIMEOUT_MS = 20_000


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_healthy(url: str, server: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + STARTUP_SECONDS
    while time.monotonic() < deadline:
        if server.poll() is not None:
            pytest.fail(f"streamlit exited with code {server.returncode}")
        try:
            with urllib.request.urlopen(f"{url}/_stcore/health", timeout=1) as resp:
                if resp.status == 200:
                    return
        except OSError:
            time.sleep(0.5)
    pytest.fail(f"streamlit did not become healthy within {STARTUP_SECONDS}s")


@pytest.fixture(scope="module")
def app_url() -> Iterator[str]:
    port = _free_port()
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(APP),
            "--server.port",
            str(port),
            "--server.address",
            "127.0.0.1",
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        _wait_healthy(url, server)
        yield url
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


def test_action_round_trip(page: Page, app_url: str) -> None:
    page.set_default_timeout(TIMEOUT_MS)
    page.goto(app_url)

    # Playwright's CSS and role locators pierce the component's open shadow root.
    surface = page.locator(".a2ui-surface")
    expect(surface.get_by_text("Contact us")).to_be_visible()
    expect(
        page.get_by_text("None yet. Fill in the form and press Send.")
    ).to_be_visible()

    # The basic catalog's labels are not linked to their inputs, so find the
    # fields by role and position within the surface: Name, then Message.
    fields = surface.get_by_role("textbox")
    expect(fields).to_have_count(2)
    fields.nth(0).fill("Ada")
    fields.nth(1).fill("Hello")
    surface.get_by_role("button", name="Send").click()

    # The scripted agent's reply is drawn in the surface ...
    expect(
        surface.get_by_text("Thanks, Ada! The agent got 5 characters.")
    ).to_be_visible()

    # ... and Python received the action with the form's context. The first
    # JSON block is the returned message; the second shows the capabilities.
    returned = page.get_by_test_id("stJson").first
    expect(returned).to_contain_text("send_message")
    expect(returned).to_contain_text("Ada")
    expect(returned).to_contain_text("Hello")
    expect(
        page.get_by_text("None yet. Fill in the form and press Send.")
    ).to_have_count(0)
