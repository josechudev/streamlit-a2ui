# Changelog

All notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [semantic versioning](https://semver.org/) with PEP 440 version numbers.

## [0.1.0rc1] - Unreleased

The first release candidate. A2UI 1.0 only, with the official basic catalog. Requires Python 3.10 or newer and Streamlit 1.59 or newer.

### Added

- `a2ui_surface(messages, *, key) -> dict | None`: renders an append-only log of A2UI 1.0 agent-to-renderer messages with the official web renderer (`@a2ui/react` and `@a2ui/web_core` 0.15.0) in a Streamlit Components v2 component, and returns at most one renderer-to-agent message per rerun.
- `renderer_capabilities() -> dict`: the renderer's A2UI capabilities, generated from `@a2ui/web_core` at build time.
- The browser processes only the part of the log it has not seen, and replays from the start when the log is shortened or rewritten.
- Streaming across reruns with `@st.fragment(run_every=...)`; see `examples/streaming_app.py`.
- Processing and rendering errors are shown as a plain-text notice inside the component and logged with `console.warn`; nothing is sent to Python.
- A per-surface error boundary: an exception while one surface renders shows a notice in its place and leaves the other surfaces rendered.
- Theming follows the Streamlit theme through CSS variables, in light and dark mode.
- `THIRD_PARTY_LICENSES.txt` with the licenses of the bundled JavaScript, shipped in the wheel.
- Examples: `examples/basic_app.py` (form and action round trip) and `examples/streaming_app.py`.

### Security

- `dompurify` is overridden to 3.4.18 inside `@a2ui/markdown-it`, which pins a release with open advisories. See `docs/security.md`.
- Known residual risk: the `zod` 3.x advisory GHSA-mrhx-c7xc-m3w5, which has no 3.x fix.

### Build and release

- CI on every pull request: Python 3.10 with the Streamlit floor and Python 3.13 with the latest Streamlit, each running the frontend build, unit tests, pytest, ruff, Prettier and a Playwright browser test.
- CI builds the wheel and the sdist once, checks them with `twine check`, rebuilds the wheel from the sdist without Node and compares the two, and runs the browser test against the installed wheel.
- A release workflow publishes a `v*` tag to PyPI through Trusted Publishing. It has not been run.
- The version is defined once, in `pyproject.toml`.

[0.1.0rc1]: https://github.com/josechudev/streamlit-a2ui/commits/master
