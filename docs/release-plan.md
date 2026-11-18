# streamlit-a2ui — Release plan to 0.1.0

Status: 2026-11-18. M1 and M2 merged to `master` (`docs/history/m1-report.md`, `docs/history/m2-report.md`). M3 merged on 2026-11-18 (`docs/history/m3-report.md`): `0.1.0rc1` is on PyPI. M4 is in progress, defined in `docs/history/handoff-m4.md`; milestone handoffs and reports are in `docs/history/`. The repository went public at the start of M3 (see M4).
Goal: `pip install streamlit-a2ui` works for a stranger, and the right people know it exists. Nothing else.

Rechecked 2026-11-17: `streamlit-a2ui` still free on PyPI; `@a2ui/react` still 0.15.0 and `@a2ui/markdown-it` still 0.2.2 (no 1.0-aligned release yet).

## Milestones

| | Milestone | Done when | Who |
|---|---|---|---|
| M1 | Harden spike into v0.1 | `docs/history/m1-report.md` reviewed; owner clicks through both examples; merged to `master` | Claude Code, then owner |
| M2 | Release engineering | CI green on a PR; a wheel built by CI installs and runs in a clean venv on the Streamlit floor and on latest | Claude Code |
| M3 | Release candidate + real-agent check | `0.1.0rc1` on PyPI; installed from PyPI in a fresh venv; one real ADK agent drove a surface end to end | Owner + Claude Code |
| M4 | 0.1.0 public | `0.1.0` on PyPI, GitHub release, listed on A2UI and Streamlit galleries | Owner |

Estimated effort with the owner's evenings: M2 one or two sessions; M3 one session plus fixes; M4 an hour plus waiting for listing PRs.

### M1 — Harden the spike (done, merged 2026-11-17)
Defined in `docs/history/handoff-m1.md`. Exit gate is the owner's review, including reading the frontend diff: it is the part most likely to hide spike-era shortcuts.

### M2 — Release engineering (done, merged 2026-11-17 as PR #4)
Handoff: `docs/history/handoff-m2.md`. Result: `docs/history/m2-report.md`.

- **CI (GitHub Actions):** *done: two test legs, a `package` job (wheel and sdist built once, sdist-without-Node comparison, `twine check`) and a `wheel-smoke` job (installed wheel, browser test).* ruff, TypeScript strict, frontend tests, pytest; build frontend then wheel and sdist; wheel-content guard (no `*.map`, no CDN URLs, bundle and capabilities JSON present); install the built wheel in a fresh venv and import it.
- **Version matrix, kept small:** Python 3.10 and latest; Streamlit at the declared floor and latest. *Done: 1.51–1.58 fail, so the floor is now `>=1.59` (`docs/history/m2-report.md`).* Raising the floor is fine; claiming one we haven't tested is not.
- **Browser smoke test:** *done (`e2e/test_basic_app.py`).* one Playwright test that starts `examples/basic_app.py`, clicks the button, and asserts the returned action appears. Only one; this is the guard against a Streamlit release silently breaking CCv2 behaviour we depend on.
- **Packaging metadata:** *done.* Single-sourced version, classifiers, project URLs, `LICENSE` and the generated `THIRD_PARTY_LICENSES.txt` in the wheel (no `NOTICE`: no bundled dependency ships one, see `docs/history/m1-report.md`), sdist that can rebuild the frontend (or a documented decision that it can't).
- **Release workflow:** *written (`.github/workflows/release.yml`), not run.* Tag `v*` → build in CI → publish with PyPI Trusted Publishing (OIDC, no API token stored). Configure the publisher as "pending" on PyPI so the first upload claims the name.
- **Repo hygiene, minimal:** *done.* `CHANGELOG.md`, short `CONTRIBUTING.md` (how to build, the out-of-scope list), `SECURITY.md` pointing to `docs/security.md` with a private reporting route, Dependabot for npm and pip with `@a2ui/*` excluded from auto-bumps (pins are deliberate).
- **Error boundary (owner decision after M1):** *done.* follow Streamlit's own pattern, one small class `ErrorBoundary` around each surface, so an exception while React renders one surface shows a plain-text notice (and the bound `console.warn`) instead of blanking the whole component. Needs a one-line exception to the "function components only" convention in `CLAUDE.md`. Add a Vitest or Playwright check that a throwing surface leaves the others rendered.
- **Bundle whitespace:** *done, kept: JS 955,724 → 764,458 bytes raw, 257,336 → 234,480 gzip.* Try `codegen.removeWhitespace` in the Vite build. Record raw and gzip size before and after; keep it only if the bundle still passes every test and the browser smoke test.
- **The M2 handoff must also:** *done. The publishing ban, kept for M2, was narrowed when M3 started: only `release.yml` on a `v*` tag the owner pushes and approves.* Refresh `docs/architecture.md` (it still describes the end of M0; fold in M1's findings and the ADRs); lift the `CLAUDE.md` out-of-scope ban that M3 needs (publishing to PyPI; the CI ban was lifted with the CI workflow); keep every other ban.

Not in M2: docs site, coverage badges, multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish.

### M3 — Release candidate and real-agent check
Handoff: `docs/history/handoff-m3.md`. Result: `docs/history/m3-report.md`. The handoff moves the README pass before the tag, because PyPI keeps the README uploaded with each version.

- **Upstream reports first** (so the README can link them): *done: a2ui-project/a2ui#4278, #4279, and a comment on the existing #4059; the unknown-type gap was ours and is fixed.* the `@a2ui/markdown-it` peer range and DOMPurify pin; `injectBasicCatalogStyles()` writing page-wide styles; `web_core` accepting unknown component types. Drafts in `docs/upstream-issues.md`. Link the issues from `docs/security.md` and ADR-008.
- **Real-agent check, outside the package.** *Done: action round trip and streamed response work with an ADK agent on `a2ui-agent-sdk` 0.12.0; no package bugs.* Every payload so far was hand-written. In a scratch repo (personal machine, no employer code), build a minimal Google ADK agent with `a2ui-agent-sdk`, feed it `renderer_capabilities()`, and drive a surface through one action round trip and one streamed response. Record what broke. Fix bugs in the package; do not add an adapter. Whether a cleaned version ships as `examples/adk_agent_app.py` (needs an API key) is a decision for then.
  - Also watch for a second renderer-to-agent message replacing the first before a rerun (two quick clicks, or an action during a `callAgentFunction`). Record whether it happens; fixing it changes the return type and needs an ADR, so do not fix it in M3. *It happens: a double or triple click returns one action.*
- **Publish `0.1.0rc1`** through the release workflow. *Done 2026-11-18, installed from PyPI in a fresh venv (no container available), both examples pass.* Install it from PyPI in a fresh venv on another machine or container and run both examples. This is the first time the wheel leaves the build machine.
- **README pass:** a GIF of the basic example, install from PyPI, status badge text that says pre-1.0. *Done, before the tag.*

### M4 — 0.1.0 public
Handoff: `docs/history/handoff-m4.md`. It adds, before the tag, a check of M3's first-load delay and a repository tidy-up (history to `docs/history/`, the command list to `CONTRIBUTING.md`), and records the owner's decision on the ADK example (decision 3 below).

- ~~Flip the repo to public.~~ *Done early, at the start of M3: GitHub Free has no environment reviewers on private repositories, and the `pypi` environment needs one. A full-history scan for secrets and employer data was clean first.*
- *Done 2026-11-18: `0.1.0` on PyPI from tag `v0.1.0` (release run 44356056432), with a fix for a 20-second first page load found while checking `0.1.0rc1`.* Tag `v0.1.0`; GitHub release notes from `CHANGELOG.md`, stating A2UI 1.0 only, the Streamlit floor, the known risks, and the pinned 0.x renderer packages.
- **Listings:**
  - A2UI ecosystem renderers page: PR adding a row (platform: Streamlit / Python; v1.0 only). Check the current repo's contribution instructions; the listing has moved between repos before.
  - Streamlit component gallery: PR to `streamlit/gallery` component registry; add the `streamlit-component` topic to the repo.
  - Posts: Streamlit forum (Custom Components), A2UI GitHub Discussions with a short demo.
- After the posts: watch issues for a week; fix only bugs as `0.1.x`.

## Decisions to make along the way
1. **Release on the 0.x renderer packages or wait for a 1.0-aligned `@a2ui/react`?** Recommendation: release; pins and overrides are documented, and waiting has no end date. When upstream ships, that is `0.1.x` or `0.2.0` depending on breakage.
2. **Streamlit floor:** decided by M2 CI, not by us. *Decided: `>=1.59`.*
3. **Ship an ADK example in the repo?** *Decided 2026-11-18: no.* It needs an API key CI never has, and the agent glue is the app's code. After `0.1.0`, a separate example repository (the owner's) may show one, linked from the README.
4. **Org or personal GitHub account** for the public repo. Personal is fine for 0.1; transferring later keeps redirects.

## After 0.1.0 (backlog, not milestones)
Ordered by what users are most likely to need; each needs its own ADR before work starts.
1. Track upstream: drop overrides when `@a2ui/*` releases fix them; adopt a 1.0-aligned renderer.
2. Return a list of outbound messages so errors reach the agent (revisits ADR-009; breaking change to the return type).
3. Geospatial catalog: needs a designed custom-catalog extension point first (ADR-006).
4. A2UI 0.9.1 support, only if users ask (ADR-005).

## Sources
- A2UI ecosystem renderers and submission note — https://a2ui.org/ecosystem/renderers/
- Streamlit component gallery registry — https://github.com/streamlit/gallery/tree/main/components/registry#readme
- Streamlit publishing guide — https://docs.streamlit.io/develop/concepts/custom-components/publish