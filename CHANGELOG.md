# Changelog

All notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [semantic versioning](https://semver.org/) with PEP 440 version numbers.

## [Unreleased]

### Fixed

- The first page load in a new environment no longer waits 20 seconds or more for the surface. Streamlit's check for dataframes in the component's data imported pandas and pyarrow on the first call; the message log is now passed in a form the check skips. Measured on macOS with Streamlit 1.67: from about 23 seconds to under 2 seconds for the first surface after a fresh install.

## [0.1.0rc1] - 2026-11-18

The first release candidate, and the first release on PyPI (`pip install --pre streamlit-a2ui`). Pre-1.0: the API and the supported versions may change before 1.0. A2UI 1.0 only, with the official basic catalog. Requires Python 3.10 or newer and Streamlit 1.59 or newer.

### Added

- `a2ui_surface(messages, *, key) -> dict | None`: renders an append-only log of A2UI 1.0 agent-to-renderer messages with the official web renderer (`@a2ui/react` and `@a2ui/web_core` 0.15.0) in a Streamlit Components v2 component, and returns at most one renderer-to-agent message per rerun.
- `renderer_capabilities() -> dict`: the renderer's A2UI capabilities, generated from `@a2ui/web_core` at build time.
- The browser processes only the part of the log it has not seen, and replays from the start when the log is shortened or rewritten.
- Streaming across reruns with `@st.fragment(run_every=...)`; see `examples/streaming_app.py`.
- Processing and rendering errors are shown as a plain-text notice inside the component and logged with `console.warn`; nothing is sent to Python.
- A component type or function the basic catalog does not define is rejected with a `VALIDATION_FAILED` notice, instead of being accepted and rendering nothing. Surfaces may still stream in out of order (children before the root, references to components that have not arrived yet).
- A per-surface error boundary: an exception while one surface renders shows a notice in its place and leaves the other surfaces rendered.
- Theming follows the Streamlit theme through CSS variables, in light and dark mode.
- `THIRD_PARTY_LICENSES.txt` with the licenses of the bundled JavaScript, shipped in the wheel.
- Examples: `examples/basic_app.py` (form and action round trip) and `examples/streaming_app.py`.
- README: install from PyPI, a GIF of the basic example, and a note on wiring a real agent. Checked with a minimal Google ADK agent built on `a2ui-agent-sdk` 0.12.0: `renderer_capabilities()` is accepted unchanged, and an action round trip and a streamed response work.

### Known limitations

- At most one renderer-to-agent message per rerun: in testing, a double or triple click returned one action to Python. Changing this changes the return type and is left for a later release.
- Renderer errors stay in the browser; your agent cannot see them yet.

### Security

- `dompurify` is overridden to 3.4.18 inside `@a2ui/markdown-it`, which pins a release with open advisories ([a2ui-project/a2ui#4278](https://github.com/a2ui-project/a2ui/issues/4278)). The `@a2ui/web_core` peer range of `@a2ui/markdown-it` is overridden too ([a2ui-project/a2ui#4059](https://github.com/a2ui-project/a2ui/issues/4059)). See `docs/security.md`.
- Known behaviour: `@a2ui/web_core` adds a page-wide stylesheet ([a2ui-project/a2ui#4279](https://github.com/a2ui-project/a2ui/issues/4279)).
- Known residual risk: the `zod` 3.x advisory GHSA-mrhx-c7xc-m3w5, which has no 3.x fix.

### Build and release

- CI on every pull request: Python 3.10 with the Streamlit floor and Python 3.13 with the latest Streamlit, each running the frontend build, unit tests, pytest, ruff, Prettier and a Playwright browser test.
- CI builds the wheel and the sdist once, checks them with `twine check`, rebuilds the wheel from the sdist without Node and compares the two, and runs the browser test against the installed wheel.
- A release workflow publishes a `v*` tag to PyPI through Trusted Publishing, after the maintainer approves the `pypi` environment. No API token is stored anywhere. This is its first release.
- The version is defined once, in `pyproject.toml`.

[0.1.0rc1]: https://github.com/josechudev/streamlit-a2ui/tree/v0.1.0rc1
