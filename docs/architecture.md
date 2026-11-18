# streamlit-a2ui — Architecture

Status: 2026-11-18, during M4 (0.1.0 public). Describes the code released as `0.1.0rc1`. The decisions behind it are the ADRs in `docs/adr/`; the evidence is in `docs/history/` (index: `docs/history/README.md`), mainly `findings.md` (M0), `m1-report.md` and `notes-m1.md` (M1), `m2-report.md` (M2) and `m3-report.md` (M3). Working rules for Claude Code are in `CLAUDE.md`.

## 1. What it is

A Python package with one Streamlit Components v2 component. The app author passes it an append-only log of A2UI 1.0 agent-to-renderer messages; the browser renders them with the official web renderer (`@a2ui/react` and `@a2ui/web_core` 0.15.0, basic catalog) and sends back at most one renderer-to-agent message per rerun. Python never interprets message contents (ADR-001, ADR-003, ADR-005, ADR-006).

```
 Streamlit script (Python)                     Browser (app page, no iframe)
┌──────────────────────────────┐              ┌────────────────────────────────────┐
│ agent (app author's code)    │              │ bundle: index.tsx                  │
│   │ A2UI messages            │              │   one LogSession + React root      │
│   ▼                          │   data=      │   per mounted instance             │
│ log in st.session_state      │ ───────────► │   LogSession.sync(log)             │
│   │                          │  full log    │     MessageProcessor (web_core 1.0)│
│   ▼                          │              │     cursor, replay, notices        │
│ a2ui_surface(log, key=...)   │              │   Surfaces.tsx                     │
│   ▲                          │  trigger     │     ErrorBoundary ─► <A2uiSurface> │
│   │ renderer→agent message   │ ◄─────────── │     notices, waiting state         │
└──────────────────────────────┘  (rerun)     └────────────────────────────────────┘
```

## 2. Python side (`streamlit_a2ui/__init__.py`)

- **Public API:** `a2ui_surface(messages, *, key) -> dict | None` and `renderer_capabilities() -> dict`. Nothing else is exported.
- **Lazy registration.** The component is registered with `st.components.v2.component(..., isolate_styles=True)` on the first `a2ui_surface` call, not at import. Streamlit resolves `asset_dir` from installed manifests only once its runtime has started, so import-time registration made the package unimportable in a plain agent process (M1). CI runs on the Streamlit floor and on the latest release, which would catch a change in registration timing.
- **Manifest.** `streamlit_a2ui/pyproject.toml` declares the component and its `asset_dir` (`frontend/build`). It has no version of its own; Streamlit falls back to the installed distribution's version, which is defined once in the root `pyproject.toml`.
- **Capabilities.** `renderer_capabilities()` returns `renderer_capabilities.json`, which `npm run build` generates from `web_core` (`MessageProcessor.getRendererCapabilities`). It is not hand-written.

## 3. Data flow

**Agent → UI (ADR-004).** The log in `st.session_state` is the source of truth. Every call passes the full log as `data`. `LogSession` keeps a cursor and hands the processor only `log[cursor:]`. If the log no longer extends what was processed (it got shorter, or the entry before the cursor changed, compared as JSON), the session disposes the processor, replays from zero and bumps a generation counter; surfaces are keyed by generation, so React remounts them. A fresh instance replays from zero. Rendered UI is therefore a pure function of the log.

**Streaming (ADR-007).** A keyed component can be called once per script run, so streaming happens across reruns: the component sits in `@st.fragment(run_every=...)` and reads a log the agent's stream appends to. A trigger fired inside a fragment reruns only the fragment, and the returned message is visible only there (`docs/history/notes-m1.md`). There is no streaming helper.

**UI → agent (ADR-003).** One trigger, `renderer_message`, set with `setTriggerValue`; triggers reset after the rerun, which gives once-only delivery. The processor's action handler receives a bare `ActionPayload`, which the frontend wraps as `{"version":"1.0","action":...}`; messages from the outbound listener (`callAgentFunction` and others) are already wire-format and pass through. A second message before the rerun replaces the first: in M3 a double or triple click returned one action. Fixing it changes the return type (ADR-003, ADR-009) and is on the backlog.

## 4. Frontend (`streamlit_a2ui/frontend/src`)

| File | Role |
|---|---|
| `index.tsx` | Streamlit glue. One `LogSession` and React root per mounted instance (a `WeakMap` keyed by the parent element), the latest trigger setter, cleanup that unmounts and disposes. Claims the page for this bundle. |
| `session.ts` | `LogSession`: processor, cursor, replay, error notices, immutable snapshot for `useSyncExternalStore`. Outbound wrapping. The bound `warn`. |
| `Surfaces.tsx` | Renders each surface inside an `ErrorBoundary`, the waiting state, and the notices list. |
| `ErrorBoundary.tsx` | The one class component: `getDerivedStateFromError` + `componentDidCatch`, Streamlit's own pattern. |
| `theme.css` | Maps `--st-*` onto every `--a2ui-*` token, including the ones the catalog derives with `light-dark()`. Notice styles. |

**Bundle claim.** The basic catalog registers custom elements page-wide. A second copy of the bundle (a rebuild loaded without a page reload) would collide while rendering, so the first copy claims the page through a global symbol and any later copy renders a plain-text notice instead.

**Errors (ADR-009).** Nothing about errors reaches Python, and the return type stays `dict | None`.

- The processor gets a `validationConfig` (`RELAXED_VALIDATION` with `allowUnknownElements: false`, M3): surfaces may stream in out of order, but a component type or function the basic catalog does not define is rejected.
- Processing and surface errors arrive once each on `processor.model.onError` (the surface group re-emits surface errors there). The session keeps the last five with a count, shows them as a plain-text notice list and logs each through the bound `warn`.
- An exception while React renders one surface is caught by that surface's `ErrorBoundary`, which renders a plain-text notice in its place and logs through `warn`. The other surfaces and the notices list stay rendered. A replay resets the boundary (new generation key).
- Notices are React text, never HTML.

**Build.** Vite library mode, ES output, Oxc minifier with `dropConsole: true`. Our one `console.warn` goes through a reference bound in `session.ts`, which the minifier leaves alone. `npm run build` fails if `build/` holds source maps, then writes `renderer_capabilities.json` and `THIRD_PARTY_LICENSES.txt` (licenses of the bundled JavaScript, from `package-lock.json`). Both are git-ignored and shipped in the wheel.

## 5. Theming

CSS only. The component host maps Streamlit's `--st-*` variables onto `--a2ui-*`; custom properties inherit into the component. No theme data crosses from Python. `web_core` also adopts a page-wide stylesheet (`color-scheme: light dark` and `--a2ui-*` defaults); `isolate_styles` does not contain it and it cannot be turned off. No visible effect on Streamlit's widgets was found (`docs/history/notes-m1.md`).

## 6. Security

Kept by construction, not by a sandbox, because Components v2 runs in the app page (ADR-002). Basic catalog only; no parameter accepts HTML, CSS or JS; markdown only through `@a2ui/markdown-it` (DOMPurify); every asset ships in the wheel; agent messages are untrusted input. `dompurify` and the `web_core` peer are held by scoped npm overrides (ADR-008). Residual risks, including the `zod` 3 advisory, are in `docs/security.md`.

## 7. Packaging, CI and release

- **Wheel and sdist.** Both ship the prebuilt frontend (`build/`, `renderer_capabilities.json`, `THIRD_PARTY_LICENSES.txt`); frontend sources are not in the sdist. Building a wheel from the sdist needs no Node, and CI checks that it equals the direct wheel (`scripts/compare_wheels.py`, file names and SHA-256). `tests/test_wheel.py` checks the wheel ships the bundle and licenses and has no source maps or remote code.
- **CI** (`.github/workflows/ci.yml`, every non-draft pull request and push to `master`; a docs-only change skips the build and tests, with the required checks still reporting): the full job (frontend build, Vitest, Prettier, pytest, ruff, Playwright smoke test) on Python 3.10 with the Streamlit floor (1.59; 1.51–1.58 failed) and on Python 3.13 with the latest Streamlit; a packaging job that builds the wheel and sdist once and checks them; and a job that installs that wheel into a fresh venv and runs the smoke test against it, so the source tree is not on `sys.path`.
- **Release** (`.github/workflows/release.yml`): a `v*` tag rebuilds from scratch, refuses a tag that does not match the package version, and publishes through PyPI Trusted Publishing from a separate job gated by the `pypi` environment, the only job with `id-token: write`. `workflow_dispatch` is a dry run that stops before publishing. No token is stored anywhere. The owner creates tags; `0.1.0rc1` was the first release (M3).
