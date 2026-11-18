# streamlit-a2ui

Open-source Python package that renders Google's A2UI protocol inside Streamlit apps by wrapping the official web renderer in a Streamlit Components v2 component.

Personal open-source project. Never add employer code, names, hostnames or data. License: Apache-2.0.

## Current milestone: M4 — 0.1.0 public

Roadmap to 0.1.0: docs/release-plan.md. Work only on the current milestone.

**Status:** M0 complete (`docs/history/spike-report.md`). M1 merged to `master` on 2026-11-17 (`docs/history/m1-report.md`). M2 merged on 2026-11-17 as PR #4 (`docs/history/m2-report.md`). M3 merged on 2026-11-18 as PRs #10–#15 (`docs/history/m3-report.md`). M4 is defined in `docs/history/handoff-m4.md`. Where a handoff and this file disagree, the handoff wins and this file is brought in line.

Push or open a pull request only when the owner asks. Push with an explicit refspec (`git push origin <branch>`), never a bare `git push`: a branch cut from a remote branch tracks it.

**Branches: gitflow (owner's decision, 2026-11-18; details in `CONTRIBUTING.md`).** `master` holds released code only, and every `v*` tag is on a `master` merge commit. `develop` is the integration branch. Name branches by kind:
- `feature/<topic>`: cut from `develop`, pull request into `develop`. All ordinary work, docs included.
- `release/<version>` (for example `release/0.1.0`): cut from `develop`; only the version bump, the dated CHANGELOG section and release fixes; pull request into `master`; after the tag, `master` is merged back into `develop` by pull request.
- `hotfix/<version>` (for example `hotfix/0.1.1`): cut from `master`; the fix with its test, the version bump and the CHANGELOG section; pull request into `master`; after the tag, merged back into `develop`.

Every merge goes through a pull request with the four CI checks green; no direct pushes to `master` or `develop`.

**Publishing.** M4 publishes `0.1.0` (and, during the watch week, bug-fix `0.1.x` releases), and it happens only one way: `release.yml`, triggered by a `v*` tag that the owner creates and pushes, publishing after the owner approves the `pypi` environment. Claude Code never creates or pushes a tag, never uploads to PyPI or TestPyPI, never runs `twine upload` or `uv publish`, and never runs `release.yml` except as a `workflow_dispatch` dry run the owner asks for.

**Public actions.** Claude Code drafts the GitHub release notes, the listing pull requests and the posts; the owner creates, opens and publishes them. Claude Code creates a GitHub release, opens a pull request in another repository, or posts on the Streamlit forum or GitHub Discussions only when the owner explicitly asks for that action in the same session, and never signs an agreement (such as Google's CLA) for the owner.

**Owner decisions, 2026-11-18.** The owner signed Google's CLA as an individual, for the A2UI listing; the GitHub release carries no assets; no ADK example in this repository, and a separate example repository, the owner's, may follow after `0.1.0` (not M4).

M4 publishes `0.1.0`, gets the package listed and announced, and adds no features. It passes when all eleven hold:

1. The first-load delay was tried at least twice in brand-new venvs from PyPI, with a Streamlit-only control. The report records the steps, versions and timings, and the cause or "not reproduced". If it is Streamlit's or the machine's first-run cost, the README says so in one sentence; if it is the package's, it is fixed with a test before `0.1.0`.
2. Milestone handoffs, reports, `findings.md` and `notes-m1.md` are in `docs/history/` with a short index. `git grep` finds no link or path to their old locations, and no file linked from the `0.1.0rc1` README moved. The command list is in `CONTRIBUTING.md`; `CLAUDE.md` and `README.md` point to it, and CI still runs the same commands.
3. `streamlit-a2ui 0.1.0` is on PyPI, published by `release.yml` from tag `v0.1.0` after a `workflow_dispatch` dry run on the same commit. The owner pushed the tag and approved the `pypi` environment. The files on PyPI match the run's artifact by SHA-256. Its README installs with `pip install streamlit-a2ui`, states the pre-1.0 status without calling it a release candidate, and renders on PyPI with working absolute links. `CHANGELOG.md` has a dated `[0.1.0]` section.
4. In a fresh environment outside the checkout, `0.1.0` installed from PyPI imports from `site-packages`, a plain install picks `0.1.0`, and both examples pass playbook parts 3 and 4 in a browser, or are marked "needs owner verification".
5. A GitHub release `v0.1.0` exists, with notes drafted from the CHANGELOG that state A2UI 1.0 only, the Streamlit floor, the pinned 0.x renderer packages and overrides, the known limitations and the accepted risk. The owner created it, or Claude Code did at the owner's explicit request in that session.
6. Listing pull requests to `a2ui-project/a2ui` (community renderers table) and `streamlit/gallery` (component registry) are drafted against each repository's instructions as rechecked on the day, the gallery JSON validates against its schema, and each was opened by the owner or at the owner's request. The report records the URLs and their state, or "not opened" with the reason.
7. The Streamlit forum post and the A2UI GitHub Discussions post are drafted, published by the owner, and their URLs recorded.
8. The watch week ran for seven days after the posts; every package bug reported in it was fixed with a test and released as `0.1.x` through `release.yml`, and everything else went to the backlog. The report lists them, or says there were none.
9. Claude Code created no tag, uploaded nothing, created no GitHub release, opened no pull request outside this repository and published no post, except where the owner explicitly asked in that session; the report names each such request.
10. All tests and linters pass locally and in CI. Nothing in the Architecture or Security sections changed without an ADR and the owner's approval. The owner's decisions on the ADK example, the CLA and release assets are recorded.
11. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/security.md`, `docs/testing-playbook.md`, `docs/release-plan.md`, `docs/upstream-issues.md`, `docs/history/README.md`, `docs/history/m4-drafts.md` and `docs/history/m4-report.md` exist and agree with each other.

Work in other repositories (listing drafts, schema checks) happens in scratch clones outside this repository. The result goes in `docs/history/m4-report.md`; stop for the owner's review once `0.1.0` is out and the drafts are done, and append the watch-week result at its end.

### M3 — release candidate and real-agent check (done)

M3 published `0.1.0rc1` to PyPI through `release.yml` from tag `v0.1.0rc1` on `388f2a7` (owner-pushed and owner-approved; files byte-identical to the run's artifact, PEP 740 attestations), and checked the package against a real Google ADK agent on `a2ui-agent-sdk` 0.12.0 outside the repository: an action round trip and a streamed response worked, with no package bugs. It filed the upstream issues (a2ui-project/a2ui#4278, #4279, a comment on #4059), made the renderer reject unknown component types and functions, measured the second-message limitation (a double click returns one action), and added the README GIF and PyPI install. All eight criteria passed. The result is in `docs/history/m3-report.md`, the handoff in `docs/history/handoff-m3.md`.

### M2 — release engineering (done)

M2 made the package releasable without releasing it: a two-leg CI matrix (Python 3.10 with Streamlit `1.59.*`, Python 3.13 with the latest), wheel and sdist built once with a Node-free sdist rebuild compared against the direct wheel, an installed-wheel browser test, the version single-sourced as `0.1.0rc1`, `release.yml` (written, never run), repository hygiene files, the per-surface error boundary, and a whitespace-stripped bundle. All ten criteria passed; criteria 1, 2, 3 and 9 on GitHub with PR #4, criterion 5 by review only. The result is in `docs/history/m2-report.md`, the handoff in `docs/history/handoff-m2.md`.

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
9. `CLAUDE.md`, `README.md`, `docs/security.md`, `docs/adr/0001`–`0009`, `docs/history/notes-m1.md` and `docs/history/m1-report.md` exist and agree with each other.

The result, and the owner's decisions on it, are in `docs/history/m1-report.md`.

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
| Streamlit | develop on 1.67.x; declare `streamlit>=1.59`, the lowest release CI passes (M2: 1.51–1.58 fail, see `docs/history/m2-report.md`) |
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
- A trigger fired inside `@st.fragment` reruns only the fragment; the returned message is visible only there (`docs/history/notes-m1.md`).
- The published README still shows v0.9 examples. Trust `node_modules/@a2ui/*/` type definitions and CHANGELOG over blog posts or memory; these packages had breaking changes in 0.13, 0.14 and 0.15.
- 1.0 wire format differs from 0.9: dynamic values use `@path`, `@call`, `@index`; naming is renderer/agent. The envelope is `{"version":"1.0","createSurface":{...}}`. Take sample payloads from the 1.0 spec (`node_modules/@a2ui/web_core/src/v1_0/schemas/`, including `catalogs/basic/examples/`), not from older tutorials.

## Repository facts (set up by the owner after M2; verified 2026-11-17)

Claude Code never changes these settings; they are the owner's.

| Thing | Value |
|---|---|
| Repository | `josechudev/streamlit-a2ui`, **public** (since M3, not M4: GitHub Free has no environment reviewers on private repositories; a full-history secret and employer-data scan was clean first) |
| `master` ruleset | no deletion or force-push; pull request required (0 approvals); required checks `Test (py3.10 / streamlit floor)`, `Test (py3.13 / streamlit latest)`, `Build wheel and sdist`, `Installed wheel smoke test`; no bypass |
| `develop` branch | created 2026-11-18 from `master` (`9cc0a23`) for gitflow. Not protected until the owner adds a `develop` ruleset matching `master`'s; until then, never push to it directly either |
| `release tag` ruleset | `refs/tags/v*`: no deletion, update or force-push; no bypass. To re-tag after a failed run that uploaded nothing, the owner disables it temporarily. Never re-tag a version already on PyPI |
| GitHub environment `pypi` | owner is the required reviewer; admins cannot bypass; deployments only from tags `v*` |
| PyPI | project `streamlit-a2ui`, created by the first Trusted Publishing upload (`0.1.0rc1`); publisher: repository `josechudev/streamlit-a2ui`, workflow `release.yml`, environment `pypi` |
| Security settings | private vulnerability reporting, secret scanning with push protection, Dependabot alerts and security updates, SHA pinning of actions required, read-only default workflow token, merged branches auto-deleted |
| Topics | `a2ui`, `python`, `streamlit`, `streamlit-component` |
| Dependabot | React, `react-dom` and their types grouped; React and `@types/node` majors held (React stays 18 until after 0.1.0); `@types/node` `^24`. The red "Dependabot Updates" runs for `zod` end in `security_update_not_possible`: expected, the accepted advisory in `docs/security.md` |
| Tags, releases | `v0.1.0rc1` (annotated, on `388f2a7`), published to PyPI on 2026-11-18 by release run 44248941528. `v0.1.0` (annotated, on `cd164e4`, the `release/0.1.0` merge), published to PyPI on 2026-11-18 by release run 44356056432 after dry run 44355836918. No GitHub release yet: the first is `v0.1.0`, created by the owner |

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

Use package name `streamlit-a2ui`, module `streamlit_a2ui`, component `a2ui_surface`. Read the generated README for the dev/build commands and record them in `CONTRIBUTING.md` ("Build and test") once confirmed; do not guess them.

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
docs/history/              milestone record: README.md (index), handoff-m1 … -m4, spike-report,
                           m1- … m4-report, findings.md (M0 evidence), notes-m1.md (fragment
                           trigger scope; page-wide color-scheme check), m4-drafts.md
docs/release-plan.md       milestones to 0.1.0
docs/testing-playbook.md   manual and automated test steps
docs/upstream-issues.md    drafts of issues to file upstream
```

## Commands

The command list (frontend, Python, browser test, wheel and sdist, installed wheel, Streamlit floor, install from PyPI) and the CI description are in `CONTRIBUTING.md` under "Build and test"; the release steps are under "Release process". Keep `CONTRIBUTING.md` and `.github/workflows/ci.yml` in step.

Local notes for Claude Code on the owner's machine:

- Node 24 is at `~/.nvm/versions/node/v24.15.0/bin`; the system Node is 23 and `nvm.sh` is missing. `export PATH=~/.nvm/versions/node/v24.15.0/bin:$PATH` before `npm`.
- Delete the setuptools cache `build/` at the repo root before building a wheel locally.
- After a rebuild, restart Streamlit and reload the page.
- Never name a workflow environment variable `STREAMLIT_*`: Streamlit reads those as config.
- Release dry run (the owner runs it, or asks for it): `gh workflow run release.yml --ref master`. It never publishes.
- Use your scratchpad, not `/tmp`, for the throwaway venvs in `CONTRIBUTING.md`.

## Conventions

- Version: defined once, in the root `pyproject.toml`. The component manifest and `package.json` have none (`tests/test_version.py`).
- Python: 3.10+, full type hints, `ruff` for lint and format, `pytest`. Public API is exactly what `__init__.py` exports.
- TypeScript: strict mode, no `any` in our code, function components only, except the one class component `ErrorBoundary` (`getDerivedStateFromError` + `componentDidCatch`, Streamlit's own pattern; React has no hook for it). No `react-error-boundary`. Keep the frontend to a handful of files; it is glue, not an app.
- Tests: pytest for the Python API and the built wheel's contents; one Playwright smoke test in `e2e/` (keep it to one; it guards against Streamlit breaking Components v2 behaviour); frontend unit tests for the cursor, replay, outbound wrapping and the error boundary. Python never parses message contents, so tests do not either.
- Commits: small, imperative subject, one concern each.
- Decisions: any change to the Architecture or Security sections needs `docs/adr/NNNN-title.md` with Context, Options, Decision, Consequences, and the owner's approval first. Accepted so far: 001 wrap official renderer · 002 Components v2 frameless · 003 message-pipe API · 004 log as source of truth · 005 A2UI 1.0 only · 006 basic catalog only · 007 streaming across reruns · 008 dependency overrides · 009 renderer errors stay in the browser. One file per ADR in `docs/adr/`.

## Subagents (local, optional)

The owner's machine has four project subagents in `.claude/agents/` of the main checkout. `.claude/` is local and never committed, so other contributors don't have them. Use them only when the owner asks for subagents; otherwise do the work inline.

| Agent | Model | Use for |
|---|---|---|
| `tester` | sonnet | Run checks and report exact failures: npm typecheck, Vitest, Prettier, build, pytest, ruff, e2e, wheel and sdist. Never edits code |
| `ts-dev` | sonnet | Any change under `streamlit_a2ui/frontend` (glue, tests, build config, theme CSS) |
| `python-dev` | sonnet | Packaging, workflows, release, pytest design: work that needs investigation |
| `python-dev-quick` | haiku | Small, fully specified Python or metadata edits in one or two files; no frontend |

Give a subagent the exact files, the change and the acceptance check. Review its diff and rerun the checks yourself before reporting a result.

## Out of scope — refuse or ask first

Geospatial or any custom catalog · agent adapters (ADK, LangChain, A2A, AG-UI) · A2UI 0.9.x/0.8 · persisting in-surface form state across remounts · typed message models in Python · multiple outbound triggers · a v1/iframe fallback · sending errors to Python or changing the return type · a streaming helper function · a docs site · publishing by any route other than `release.yml` on a `v*` tag the owner pushes and approves: Claude Code never creates or pushes tags, never uploads to PyPI, TestPyPI or npm, never runs `twine upload` or `uv publish` · running `release.yml` other than as a `workflow_dispatch` dry run the owner starts or asks for · creating a GitHub release, opening a pull request in another repository (listings), or posting on the Streamlit forum or GitHub Discussions, unless the owner explicitly asks for that action in the same session (Claude Code drafts them) · signing Google's CLA or any agreement for the owner · changing the repository's visibility, settings, rulesets or environments (the owner's) · an agent or ADK example in this repository (owner decided against it, 2026-11-18), or the separate example repository before `0.1.0` is out · upgrading `@a2ui/*`, `dompurify` or React, or dropping an override, even if upstream ships a fix during M4 · backlog items after 0.1.0 (`docs/release-plan.md`): returning a list of messages, React 19, custom catalogs · filing upstream issues (the owner does) · coverage badges, a multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish · pushing or opening a pull request unless the owner asks.

If a task seems to need one of these, stop and say so instead of building it.
