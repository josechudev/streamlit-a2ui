# streamlit-a2ui

Open-source Python package that renders Google's A2UI protocol inside Streamlit apps by wrapping the official web renderer in a Streamlit Components v2 component.

Personal open-source project. Never add employer code, names, hostnames or data. License: Apache-2.0.

## Current milestone: M2 — release engineering

Roadmap to 0.1.0: docs/release-plan.md. Work only on the current milestone.

**Status:** M0 complete (`docs/spike-report.md`). M1 merged to `master` on 2026-11-17 (`docs/m1-report.md`; handoff `docs/handoff-m1.md`). M2's CI workflow and Playwright smoke test were added early at the owner's request (PR #3, merged). The rest of M2 is defined in `docs/handoff-m2.md`; work on branch `m2-release`. Where a handoff and this file disagree, the handoff wins and this file is brought in line.

Push or open a pull request only when the owner asks. Never publish: no tags, no GitHub releases, no upload to PyPI or TestPyPI. `m2-release` tracks `origin/master`, so never run a bare `git push` from it; push with an explicit `origin m2-release` refspec.

M2 makes the package releasable but does not release it. It passes when all ten hold:

1. CI runs the full job on Python 3.10 with the Streamlit floor and on Python 3.13 with the latest Streamlit, and both pass on a pull request. The declared floor in `pyproject.toml` and the README is one that CI actually ran.
2. CI builds the wheel and the sdist, installs the wheel into a fresh venv outside the checkout, imports it, and passes the e2e test against it.
3. A wheel built from the sdist without Node has the same contents as the direct wheel. `twine check` (or equivalent) passes on both.
4. The version is defined once. The package, the component manifest and `package.json` agree, and the version is `0.1.0rc1`.
5. `release.yml` exists, and every third-party action in it is pinned to a SHA. Only the publish job has `id-token: write`, and it is gated by the `pypi` environment. It refuses a tag that doesn't match the version. A `workflow_dispatch` dry run builds and stops before publishing. No tag was created and nothing was uploaded.
6. `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md` and `.github/dependabot.yml` exist. Dependabot ignores `@a2ui/*` and `dompurify`.
7. A throwing surface shows a plain-text notice and leaves the other surfaces and the notices list rendered, as shown by a test.
8. Bundle sizes are recorded before and after the whitespace change, with a keep or revert decision.
9. All tests and linters pass locally and in CI. The click-through in `docs/testing-playbook.md` (parts 3 and 4) still passes in a browser, or is marked "needs owner verification".
10. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `docs/architecture.md`, `docs/security.md`, `docs/testing-playbook.md`, `docs/release-plan.md` and `docs/m2-report.md` exist and agree with each other.

The result goes in `docs/m2-report.md`; then stop for the owner's review.

### M1 — harden the spike into v0.1 (done)

M1 made the spike something a stranger can install from source and use. It was not a feature milestone.

M1 passed when all nine held:

1. From a clean clone, the commands in the Commands section build the frontend, install the package and run both examples without edits.
2. `examples/basic_app.py`: the surface renders, the action comes back once with its context, the scripted reply updates the surface in place, and typed-but-unsubmitted text survives the rerun.
3. `examples/streaming_app.py`: content appears progressively, and an action fired during or after streaming is received by Python.
4. A deliberately invalid message in the log produces the in-component notice, does not blank the surfaces already rendered, and returns nothing to Python.
5. `renderer_capabilities()` output is generated from `web_core`, not hand-written.
6. One `dompurify` at 3.4.18 in the lockfile and in the bundle.
7. The wheel has no source maps and no CDN references; the production bundle has no construction log.
8. All tests and linters pass. Criteria 2, 3 and 4 were exercised in a browser, not inferred from code; otherwise they are marked "needs owner verification" with a click-through checklist.
9. `CLAUDE.md`, `README.md`, `docs/security.md`, `docs/adr/0001`–`0009`, `docs/notes-m1.md` and `docs/m1-report.md` exist and agree with each other.

The result, and the owner's decisions on it, are in `docs/m1-report.md`.

## Architecture (decided; change only via an ADR)

```
agent ──A2UI msgs──► log in st.session_state ──data=──► frontend: MessageProcessor ─► <A2uiSurface>
                          ▲                                        │
                          └──── return value ◄── trigger ◄─────────┘ renderer→agent message
```

- **Message pipe.** `a2ui_surface(messages, *, key)` takes agent→renderer messages and returns at most one renderer→agent message (`dict | None`) per rerun. Python never interprets message contents.
- **The log is the source of truth.** Append-only list in `st.session_state`. The full log is passed as `data` on every call. The frontend keeps a cursor and processes only `log[cursor:]`; a fresh instance replays from 0. Rendered UI must be a pure function of the log.
- **One outbound trigger**, `renderer_message`, set with `setTriggerValue`. Wire it to the processor's action handler and to its outbound renderer-message listener (needed for `callAgentFunction`). Do not use state values for outbound messages.
- **Frameless.** Streamlit Components v2, `isolate_styles=True`. No v1 API, no iframe, no `postMessage`, no `streamlit-component-lib`.
- **Theming** is CSS only: map `--st-*` variables onto `--a2ui-*` variables on the component's host element. No theme data crosses from Python.
- **Streaming across reruns** (ADR-007). One call per keyed component per script run. The documented pattern is the component inside `@st.fragment(run_every=...)` reading a log the agent's stream appends to. No streaming helper in v0.1.
- **Renderer errors stay in the browser** (ADR-009). Processing errors render as a plain-text notice inside the component (set via text content) and are logged with `console.warn`; nothing is sent to Python. The return type stays `dict | None`.

Target public API for v0.1, nothing more:

```python
from streamlit_a2ui import a2ui_surface, renderer_capabilities

log = st.session_state.setdefault("a2ui_log", [])
event = a2ui_surface(log, key="main")
if event:
    log.extend(my_agent.send(event))
    st.rerun()
```

## Pinned facts (verified 2026-11-17; re-verify before changing)

| Thing | Value |
|---|---|
| A2UI spec | 1.0 only. 0.9.x is untested and unsupported |
| `@a2ui/react`, `@a2ui/web_core` | `0.15.0`, exact pins, no `^`. Do not upgrade in M1, even if a newer release is published; note it in the report |
| `@a2ui/markdown-it` | `0.2.2`, exact. Its peer range (`web_core ^0.14.0`) is wrong for 0.15, so `package.json` carries a scoped npm `overrides` entry pointing it at the root `web_core`. Remove when upstream fixes it |
| `dompurify` (inside `@a2ui/markdown-it`) | `3.4.18`, exact, via a scoped npm `overrides` entry (ADR-008). Upstream pins 3.4.11, which has open advisories fixed by 3.4.17. Remove when upstream ships a fix |
| `zod` | 3.x required by `web_core`; open high advisory with no 3.x fix. Accepted residual risk (ADR-008) |
| Streamlit | develop on 1.67.x; declare `streamlit>=1.51` |
| Node | 24 (via nvm if the system Node is older) |
| React | 18 or 19 (peer range of `@a2ui/react`); use what the template ships |
| Basic catalog ID | `https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json` |

API notes that are easy to get wrong:

- Import `A2uiSurface` from the **root** of `@a2ui/react`. There is no `@a2ui/react/v1_0`. Do not import from `/v0_9` or `/v0_8`.
- Import `MessageProcessor` from `@a2ui/web_core` and the catalog from `@a2ui/web_core/catalogs/basic/v1`.
- `MessageProcessor`'s `version` option defaults to 0.9. Pass `'1.0'` (`SpecVersion.V1_0`), not `'v1.0'`.
- The action handler receives a bare `ActionPayload`. Wrap it as `{"version":"1.0","action":payload}` before sending. Messages from the outbound listener are already wire-format; send them unchanged.
- A keyed component can be called once per script run. Streaming is done across reruns, with the component inside `@st.fragment(run_every=...)`. Never vary the key to repaint.
- `web_core` injects a stylesheet onto the host document. Known, accepted, do not try to patch it out.
- The catalog derives colors with `light-dark()` and Streamlit exposes no color-scheme variable, so `theme.css` must redefine every derived `--a2ui-*` color token from `--st-*`, not only the base ones.
- Since 0.15.0 a surface renders nothing until its root component arrives. Render our own minimal waiting state.
- Basic catalog components are custom elements registered globally on the page. `web_core` registration is idempotent for one bundle but throws for a second copy, so `index.tsx` claims the page with a global symbol and a later copy renders a notice instead. Never load two versions of the bundle.
- Surface errors are re-emitted on `processor.model.onError`. Subscribe there only, or each error is reported twice.
- `@a2ui/web_core` 0.15.0 does not reject unknown component types; a `Text` without `text` is a reliable invalid message for tests.
- The production build sets `dropConsole: true` (template default). The one `console.warn` we keep goes through a reference bound in `session.ts`, which the minifier leaves alone.
- The component is registered on first call, not at import: Streamlit resolves `asset_dir` only once its runtime has started, so import-time registration breaks `import streamlit_a2ui` outside `streamlit run`.
- A trigger fired inside `@st.fragment` reruns only the fragment; the returned message is visible only there (`docs/notes-m1.md`).
- The published README still shows v0.9 examples. Trust `node_modules/@a2ui/*/` type definitions and CHANGELOG over blog posts or memory; these packages had breaking changes in 0.13, 0.14 and 0.15.
- 1.0 wire format differs from 0.9: dynamic values use `@path`, `@call`, `@index`; naming is renderer/agent. The envelope is `{"version":"1.0","createSurface":{...}}`. Take sample payloads from the 1.0 spec (`node_modules/@a2ui/web_core/src/v1_0/schemas/`, including `catalogs/basic/examples/`), not from older tutorials.

## Security rules (non-negotiable)

- Only the official basic catalog is registered. No inline catalogs, no custom catalog API yet.
- No function parameter, prop or option accepts HTML, CSS or JS from the app author or the agent. No `dangerouslySetInnerHTML` in our code.
- Markdown is rendered only through `@a2ui/markdown-it`. Do not make the renderer swappable.
- All frontend assets ship in the wheel. No CDN URLs, no runtime fetch of code or fonts.
- `asset_dir` is publicly served by Streamlit: build output only, no source maps with secrets, no fixtures.
- Treat every agent message as untrusted input. Never `eval`, never build selectors or URLs from it in our code.

## Repository

Generate from Streamlit's official v2 React template; do not hand-write the packaging:

```
uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v2
```

Use package name `streamlit-a2ui`, module `streamlit_a2ui`, component `a2ui_surface`. Read the generated README for the dev/build commands and record them in the Commands section below once confirmed; do not guess them.

Expected shape after generation (adjust to what the template actually produces):

```
streamlit_a2ui/            Python package: __init__.py with a2ui_surface(), renderer_capabilities()
streamlit_a2ui/frontend/   Vite + React + TS; build output is the asset_dir
  src/index.tsx            Streamlit glue: one LogSession and React root per mounted instance
  src/session.ts           LogSession: processor, cursor, replay, error notices; outbound wrapping
  src/Surfaces.tsx         surfaces, waiting state, error notice
  src/theme.css            --st-* → --a2ui-* mapping, notice styles
  scripts/                 build-time: capabilities, license texts, source-map check
examples/basic_app.py      form surface, action round trip, scripted agent
examples/streaming_app.py  fragment streaming plus an action from inside the fragment
tests/                     pytest (default run)
  src/ErrorBoundary.tsx    per-surface React error boundary (the one class component)
e2e/                       one Playwright browser smoke test (run with `pytest e2e`)
.github/workflows/ci.yml   CI: version matrix (build, tests, lint, e2e), wheel + sdist, installed-wheel smoke test
.github/workflows/release.yml  tag v* → build, check, publish to PyPI via Trusted Publishing (never run in M2)
.github/dependabot.yml     weekly npm, pip, github-actions; @a2ui/* and dompurify ignored
CHANGELOG.md               Keep a Changelog
CONTRIBUTING.md            build, test, scope, release process
SECURITY.md                private reporting route; points at docs/security.md
docs/architecture.md       current design, short
docs/adr/                  NNNN-title.md
docs/security.md           security model, overrides, residual risks, npm audit
docs/notes-m1.md           fragment trigger scope; page-wide color-scheme check
docs/spike-report.md       written at the end of M0
docs/m1-report.md          written at the end of M1
docs/m2-report.md          written at the end of M2
docs/release-plan.md       milestones to 0.1.0
docs/testing-playbook.md   manual and automated test steps
docs/upstream-issues.md    drafts of issues to file upstream
```

## Commands

Prerequisites: uv, Node 24 (via nvm if the system Node is older), npm. Package only from `npm run build`: `npm run dev` writes source maps into the publicly served `asset_dir`, and the build check fails on them.

```
# frontend (from streamlit_a2ui/frontend)
npm install
npm run build        # clean + tsc + vite build → build/ (the asset_dir), fail on source maps,
                     # then write ../renderer_capabilities.json and ../THIRD_PARTY_LICENSES.txt
npm run dev          # vite build --watch; emits source maps into build/
npm run typecheck
npm test             # Vitest unit tests (src/*.test.ts)
npm run format:check # Prettier, as CI runs it

# python (from repo root)
uv venv
uv pip install -e . --force-reinstall
uv pip install pytest ruff
.venv/bin/streamlit run examples/basic_app.py
.venv/bin/streamlit run examples/streaming_app.py
.venv/bin/pytest -q            # needs npm run build first: builds and inspects the wheel
.venv/bin/ruff check . && .venv/bin/ruff format --check .

# browser smoke test (e2e/, not in the default pytest run)
uv pip install pytest-playwright
.venv/bin/playwright install chromium
.venv/bin/pytest e2e -q          # starts examples/basic_app.py, clicks Send, checks the round trip

# wheel and sdist (after npm run build)
uv build                         # dist/*.whl and dist/*.tar.gz
uvx twine check --strict dist/*

# installed-wheel smoke test: the wheel, not the source tree (after uv build)
uv venv /tmp/a2ui-wheel
uv pip install --python /tmp/a2ui-wheel dist/*.whl pytest pytest-playwright
(cd /tmp && /tmp/a2ui-wheel/bin/python -c "import streamlit_a2ui; print(streamlit_a2ui.renderer_capabilities())")
/tmp/a2ui-wheel/bin/playwright install chromium
/tmp/a2ui-wheel/bin/pytest e2e -q

# version matrix, floor leg (CI runs this and the latest leg; see ci.yml for exact pins)
uv venv --python 3.10 .venv-floor
uv pip install --python .venv-floor -e . "streamlit==1.51.*" pytest ruff pytest-playwright
.venv-floor/bin/pytest -q && .venv-floor/bin/pytest e2e -q

# release dry run: builds and checks, never publishes (owner only; needs the branch pushed)
gh workflow run release.yml --ref <branch>
```

CI (`.github/workflows/ci.yml`) runs all of the above on every pull request and on pushes to `master`, with Node 24, on two legs: Python 3.10 with the Streamlit floor, and Python 3.13 with the latest Streamlit. Keep the workflow in step with these commands. Third-party actions are pinned to a commit SHA. `release.yml` publishes on a `v*` tag; only the owner creates tags.

If a `js=`/`css=` glob matches more than one file in `build/`, run `npm run clean` and rebuild. After a rebuild, restart Streamlit and reload the page: the first bundle loaded claims the page's custom elements, and a second copy only shows a notice.

`renderer_capabilities.json` and `THIRD_PARTY_LICENSES.txt` are generated, git-ignored and shipped in the wheel. Never hand-edit them.

## Conventions

- Python: 3.10+, full type hints, `ruff` for lint and format, `pytest`. Public API is exactly what `__init__.py` exports.
- TypeScript: strict mode, no `any` in our code, function components only, except the one class component `ErrorBoundary` (`getDerivedStateFromError` + `componentDidCatch`, Streamlit's own pattern; React has no hook for it). No `react-error-boundary`. Keep the frontend to a handful of files; it is glue, not an app.
- Tests: pytest for the Python API and the built wheel's contents; one Playwright smoke test in `e2e/` (keep it to one; it guards against Streamlit breaking Components v2 behaviour); frontend unit tests for the cursor, replay, outbound wrapping and the error boundary. Python never parses message contents, so tests do not either.
- Commits: small, imperative subject, one concern each.
- Decisions: any change to the Architecture or Security sections needs `docs/adr/NNNN-title.md` with Context, Options, Decision, Consequences, and the owner's approval first. Accepted so far: 001 wrap official renderer · 002 Components v2 frameless · 003 message-pipe API · 004 log as source of truth · 005 A2UI 1.0 only · 006 basic catalog only · 007 streaming across reruns · 008 dependency overrides · 009 renderer errors stay in the browser. One file per ADR in `docs/adr/`.

## Out of scope — refuse or ask first

Geospatial or any custom catalog · agent adapters (ADK, LangChain, A2A, AG-UI) · A2UI 0.9.x/0.8 · persisting in-surface form state across remounts · typed message models in Python · multiple outbound triggers · a v1/iframe fallback · sending errors to Python or changing the return type · a streaming helper function · a docs site · publishing to PyPI, TestPyPI or npm, creating tags or GitHub releases, changing the repository's visibility (M3/M4) · running `release.yml` other than as a `workflow_dispatch` dry run the owner starts · a real agent or ADK example (M3) · filing upstream issues (the owner does) · coverage badges, a multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish · pushing or opening a pull request unless the owner asks.

If a task seems to need one of these, stop and say so instead of building it.
