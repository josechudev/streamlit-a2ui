# streamlit-a2ui

Open-source Python package that renders Google's A2UI protocol inside Streamlit apps by wrapping the official web renderer in a Streamlit Components v2 component.

Personal open-source project. Never add employer code, names, hostnames or data. License: Apache-2.0.

## Current milestone: M3 — release candidate and real-agent check

Roadmap to 0.1.0: docs/release-plan.md. Work only on the current milestone.

**Status:** M0 complete (`docs/spike-report.md`). M1 merged to `master` on 2026-11-17 (`docs/m1-report.md`). M2 merged on 2026-11-17 as PR #4 (`docs/m2-report.md`). M3 is defined in `docs/handoff-m3.md`. Where a handoff and this file disagree, the handoff wins and this file is brought in line.

Push or open a pull request only when the owner asks. Work on a branch cut from `master`; `master` is protected, so changes land through a pull request with the four CI checks green. Push with an explicit refspec (`git push origin <branch>`), never a bare `git push`: a branch cut from `origin/master` tracks it.

**Publishing.** M3 publishes `0.1.0rc1`, and it happens only one way: `release.yml`, triggered by a `v*` tag that the owner creates and pushes, publishing after the owner approves the `pypi` environment. Claude Code never creates or pushes a tag, never uploads to PyPI or TestPyPI, never runs `twine upload` or `uv publish`, never creates a GitHub release, and never runs `release.yml` except as a `workflow_dispatch` dry run the owner asks for.

M3 publishes the first release candidate and checks the package against a real agent. It passes when all eight hold:

1. Upstream reports, as rechecked on 2026-11-17 (`docs/upstream-issues.md`): issues 2 and 3 are filed by the owner; issue 1 is the existing [#4059](https://github.com/a2ui-project/a2ui/issues/4059), which the owner comments on instead; issue 4 is not filed, and the report records whether the package now passes a `validationConfig` that rejects unknown component types. The URLs are in `docs/upstream-issues.md` and linked from `docs/security.md` and ADR-008 (issues 1 and 2) and from `docs/security.md` (issue 3).
2. A minimal ADK agent built with `a2ui-agent-sdk`, outside this repository, received `renderer_capabilities()` and drove a surface rendered by `a2ui_surface` in a browser through one action round trip and one streamed response. The report lists the versions used and what broke. Each package bug found is fixed with a test. No adapter or agent dependency was added to the package.
3. The report records whether a second renderer-to-agent message replaced the first before a rerun, with the steps used. The behaviour is unchanged, and the README states the measured result.
4. The README says how to install from PyPI, states the pre-1.0 status, shows a GIF of the basic example, and renders correctly on PyPI with working absolute links. The GIF is in neither the wheel nor the sdist.
5. `streamlit-a2ui 0.1.0rc1` is on PyPI, published by `release.yml` from tag `v0.1.0rc1`. The owner pushed the tag and approved the `pypi` environment. The files on PyPI match the run's artifact by SHA-256. Claude Code created no tag, uploaded nothing and created no GitHub release.
6. In a fresh environment outside the checkout, `0.1.0rc1` installed from PyPI imports from `site-packages`, and both examples pass playbook parts 3 and 4 in a browser, or are marked "needs owner verification".
7. All tests and linters pass locally and in CI. Nothing in the Architecture or Security sections changed without an ADR and the owner's approval.
8. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/security.md`, `docs/testing-playbook.md`, `docs/release-plan.md`, `docs/upstream-issues.md` and `docs/m3-report.md` exist and agree with each other.

The real-agent check runs in a scratch folder outside this repository; the model API key is the owner's and never enters the repository, a note, the report or a logged command line. The author e-mail in `pyproject.toml`'s `authors` stays as it is (owner's decision, 2026-11-17); it becomes public in the package metadata with `rc1`.

The result goes in `docs/m3-report.md`; then stop for the owner's review.

### M2 — release engineering (done)

M2 made the package releasable without releasing it: a two-leg CI matrix (Python 3.10 with Streamlit `1.59.*`, Python 3.13 with the latest), wheel and sdist built once with a Node-free sdist rebuild compared against the direct wheel, an installed-wheel browser test, the version single-sourced as `0.1.0rc1`, `release.yml` (written, never run), repository hygiene files, the per-surface error boundary, and a whitespace-stripped bundle. All ten criteria passed; criteria 1, 2, 3 and 9 on GitHub with PR #4, criterion 5 by review only. The result is in `docs/m2-report.md`, the handoff in `docs/handoff-m2.md`.

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
| `@a2ui/react`, `@a2ui/web_core` | `0.15.0`, exact pins, no `^`. Do not upgrade before 0.1.0, even if a newer release is published; note it in the report |
| `@a2ui/markdown-it` | `0.2.2`, exact. Its peer range (`web_core ^0.14.0`) is wrong for 0.15, so `package.json` carries a scoped npm `overrides` entry pointing it at the root `web_core`. Remove when upstream fixes it |
| `dompurify` (inside `@a2ui/markdown-it`) | `3.4.18`, exact, via a scoped npm `overrides` entry (ADR-008). Upstream pins 3.4.11, which has open advisories fixed by 3.4.17. Remove when upstream ships a fix |
| `zod` | 3.x required by `web_core`; open high advisory with no 3.x fix. Accepted residual risk (ADR-008) |
| Streamlit | develop on 1.67.x; declare `streamlit>=1.59`, the lowest release CI passes (M2: 1.51–1.58 fail, see `docs/m2-report.md`) |
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
- `@a2ui/web_core` 0.15.0 rejects unknown component types only when the processor has a `validationConfig`. `session.ts` passes `VALIDATION` (`RELAXED_VALIDATION` with `allowUnknownElements: false`): relaxed so surfaces can stream in out of order, strict about types. Never pass `STRICT_VALIDATION`: it rejects a surface whose root has not arrived yet. A `Text` without `text`, or an unknown component type, is a reliable invalid message for tests.
- The production build sets `dropConsole: true` (template default). The one `console.warn` we keep goes through a reference bound in `session.ts`, which the minifier leaves alone.
- The component is registered on first call, not at import: Streamlit resolves `asset_dir` only once its runtime has started, so import-time registration breaks `import streamlit_a2ui` outside `streamlit run`.
- A trigger fired inside `@st.fragment` reruns only the fragment; the returned message is visible only there (`docs/notes-m1.md`).
- The published README still shows v0.9 examples. Trust `node_modules/@a2ui/*/` type definitions and CHANGELOG over blog posts or memory; these packages had breaking changes in 0.13, 0.14 and 0.15.
- 1.0 wire format differs from 0.9: dynamic values use `@path`, `@call`, `@index`; naming is renderer/agent. The envelope is `{"version":"1.0","createSurface":{...}}`. Take sample payloads from the 1.0 spec (`node_modules/@a2ui/web_core/src/v1_0/schemas/`, including `catalogs/basic/examples/`), not from older tutorials.

## Repository facts (set up by the owner after M2; verified 2026-11-17)

Claude Code never changes these settings; they are the owner's.

| Thing | Value |
|---|---|
| Repository | `josechudev/streamlit-a2ui`, **public** (since M3, not M4: GitHub Free has no environment reviewers on private repositories; a full-history secret and employer-data scan was clean first) |
| `master` ruleset | no deletion or force-push; pull request required (0 approvals); required checks `Test (py3.10 / streamlit floor)`, `Test (py3.13 / streamlit latest)`, `Build wheel and sdist`, `Installed wheel smoke test`; no bypass |
| `release tag` ruleset | `refs/tags/v*`: no deletion, update or force-push; no bypass. To re-tag after a failed run that uploaded nothing, the owner disables it temporarily. Never re-tag a version already on PyPI |
| GitHub environment `pypi` | owner is the required reviewer; admins cannot bypass; deployments only from tags `v*` |
| PyPI | pending Trusted Publisher: project `streamlit-a2ui`, repository `josechudev/streamlit-a2ui`, workflow `release.yml`, environment `pypi`. The project does not exist yet; a pending publisher does not reserve the name |
| Security settings | private vulnerability reporting, secret scanning with push protection, Dependabot alerts and security updates, SHA pinning of actions required, read-only default workflow token, merged branches auto-deleted |
| Topics | `a2ui`, `python`, `streamlit`, `streamlit-component` |
| Dependabot | React, `react-dom` and their types grouped; React and `@types/node` majors held (React stays 18 until after 0.1.0); `@types/node` `^24`. The red "Dependabot Updates" runs for `zod` end in `security_update_not_possible`: expected, the accepted advisory in `docs/security.md` |
| Tags, releases | none yet. `streamlit-a2ui` is not on PyPI |

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
scripts/compare_wheels.py  compares two wheels by file name and SHA-256 (CI, release)
tests/                     pytest (default run): API, version single source, built wheel contents
  src/ErrorBoundary.tsx    per-surface React error boundary (the one class component)
e2e/                       one Playwright browser smoke test (run with `pytest e2e`)
.github/workflows/ci.yml   CI: version matrix (build, tests, lint, e2e), wheel + sdist, installed-wheel smoke test
.github/workflows/release.yml  tag v* → build, check, publish to PyPI via Trusted Publishing (first run in M3)
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
docs/handoff-m1.md … -m3.md  one handoff per milestone: decisions, steps, acceptance criteria
docs/m3-report.md          written at the end of M3
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

# wheel and sdist (after npm run build). Build them separately: a bare `uv build`
# makes the wheel from the sdist, leaving nothing to compare.
uv build --sdist --out-dir dist
uv build --wheel --out-dir dist
uvx twine@7.0.0 check --strict dist/*
# the sdist must rebuild the same wheel without Node (CI runs this with a PATH that has no node)
uv build --wheel --out-dir /tmp/from-sdist dist/*.tar.gz
python3 scripts/compare_wheels.py dist/*.whl /tmp/from-sdist/*.whl

# installed-wheel smoke test: the wheel, not the source tree (the e2e server runs from a temp dir)
uv venv --python 3.13 /tmp/a2ui-wheel
uv pip install --python /tmp/a2ui-wheel dist/*.whl pytest==9.2.0 pytest-playwright==0.10.0 playwright==1.65.2
(cd /tmp && /tmp/a2ui-wheel/bin/python -c "import streamlit_a2ui; print(streamlit_a2ui.__file__, streamlit_a2ui.renderer_capabilities())")
/tmp/a2ui-wheel/bin/playwright install chromium
/tmp/a2ui-wheel/bin/pytest e2e -q

# version matrix, floor leg (CI's other leg is Python 3.13 with the latest Streamlit)
uv venv --python 3.10 .venv-floor
uv pip install --python .venv-floor -e . "streamlit==1.59.*" pytest==9.2.0 ruff==0.17.5 pytest-playwright==0.10.0 playwright==1.65.2
.venv-floor/bin/pytest -q && .venv-floor/bin/pytest e2e -q

# release dry run: builds and checks, never publishes (the owner runs it, or asks for it; needs the branch pushed)
gh workflow run release.yml --ref <branch>

# install a published release candidate from PyPI (M3): fresh venv, no cache, outside the checkout.
# Pre-releases need --pre or an exact pin with pip, --prerelease=allow or an exact pin with uv.
uv venv --python 3.13 /tmp/a2ui-pypi
uv pip install --python /tmp/a2ui-pypi --no-cache "streamlit-a2ui==0.1.0rc1"
(cd /tmp && /tmp/a2ui-pypi/bin/python -c "import streamlit_a2ui, importlib.metadata as m; print(streamlit_a2ui.__file__, m.version('streamlit-a2ui'))")
# the examples are not in the wheel: take them from the tag into an empty folder and run them there
mkdir -p /tmp/a2ui-pypi-examples && git show v0.1.0rc1:examples/basic_app.py > /tmp/a2ui-pypi-examples/basic_app.py
(cd /tmp/a2ui-pypi-examples && /tmp/a2ui-pypi/bin/streamlit run basic_app.py)
```

CI (`.github/workflows/ci.yml`) runs all of the above on every pull request and on pushes to `master`, with Node 24, on two legs: Python 3.10 with the Streamlit floor (`1.59.*`), and Python 3.13 with the latest Streamlit (`>=1.67`). A `package` job builds the wheel and sdist once, rebuilds the wheel from the sdist without Node and compares them, runs `twine check`, and uploads `dist`; `wheel-smoke` installs that wheel into a fresh venv and runs the e2e test against it. Keep the workflow in step with these commands. Third-party actions are pinned to a commit SHA. `release.yml` publishes on a `v*` tag, after the owner approves the `pypi` environment; only the owner creates and pushes tags.

If a `js=`/`css=` glob matches more than one file in `build/`, run `npm run clean` and rebuild. Before building a wheel locally, delete the setuptools cache `build/` at the repo root: it keeps old bundles and setuptools ships them (CI checkouts are clean; `tests/test_wheel.py` fails on a second bundle). After a rebuild, restart Streamlit and reload the page: the first bundle loaded claims the page's custom elements, and a second copy only shows a notice.

`renderer_capabilities.json` and `THIRD_PARTY_LICENSES.txt` are generated, git-ignored and shipped in the wheel. Never hand-edit them.

## Conventions

- Version: defined once, in the root `pyproject.toml`. The component manifest and `package.json` have none (`tests/test_version.py`).
- Python: 3.10+, full type hints, `ruff` for lint and format, `pytest`. Public API is exactly what `__init__.py` exports.
- TypeScript: strict mode, no `any` in our code, function components only, except the one class component `ErrorBoundary` (`getDerivedStateFromError` + `componentDidCatch`, Streamlit's own pattern; React has no hook for it). No `react-error-boundary`. Keep the frontend to a handful of files; it is glue, not an app.
- Tests: pytest for the Python API and the built wheel's contents; one Playwright smoke test in `e2e/` (keep it to one; it guards against Streamlit breaking Components v2 behaviour); frontend unit tests for the cursor, replay, outbound wrapping and the error boundary. Python never parses message contents, so tests do not either.
- Commits: small, imperative subject, one concern each.
- Decisions: any change to the Architecture or Security sections needs `docs/adr/NNNN-title.md` with Context, Options, Decision, Consequences, and the owner's approval first. Accepted so far: 001 wrap official renderer · 002 Components v2 frameless · 003 message-pipe API · 004 log as source of truth · 005 A2UI 1.0 only · 006 basic catalog only · 007 streaming across reruns · 008 dependency overrides · 009 renderer errors stay in the browser. One file per ADR in `docs/adr/`.

## Out of scope — refuse or ask first

Geospatial or any custom catalog · agent adapters (ADK, LangChain, A2A, AG-UI) · A2UI 0.9.x/0.8 · persisting in-surface form state across remounts · typed message models in Python · multiple outbound triggers · a v1/iframe fallback · sending errors to Python or changing the return type · a streaming helper function · a docs site · publishing by any route other than `release.yml` on a `v*` tag the owner pushes and approves: Claude Code never creates or pushes tags, never uploads to PyPI, TestPyPI or npm, never runs `twine upload` or `uv publish`, never creates GitHub releases · running `release.yml` other than as a `workflow_dispatch` dry run the owner starts or asks for · `0.1.0`, the GitHub release, gallery listings and posts (M4) · changing the repository's visibility, settings, rulesets or environments (the owner's) · an agent or ADK example in this repository without the owner's approval after M3's real-agent check (the check itself runs in a scratch folder outside the repository) · upgrading `@a2ui/*`, `dompurify` or React · filing upstream issues (the owner does) · coverage badges, a multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish · pushing or opening a pull request unless the owner asks.

If a task seems to need one of these, stop and say so instead of building it.
