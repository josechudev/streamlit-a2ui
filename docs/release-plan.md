# streamlit-a2ui — Release plan to 0.1.0

Status: 2026-11-17. M1 (harden the spike into v0.1) is complete on branch `m1-v0.1` and awaiting owner review (`docs/m1-report.md`).
Goal: `pip install streamlit-a2ui` works for a stranger, and the right people know it exists. Nothing else.

Rechecked 2026-11-17: `streamlit-a2ui` still free on PyPI; `@a2ui/react` still 0.15.0 and `@a2ui/markdown-it` still 0.2.2 (no 1.0-aligned release yet).

## Milestones

| | Milestone | Done when | Who |
|---|---|---|---|
| M1 | Harden spike into v0.1 | `docs/m1-report.md` reviewed; owner clicks through both examples; merged to `master` | Claude Code, then owner |
| M2 | Release engineering | CI green on a PR; a wheel built by CI installs and runs in a clean venv on the Streamlit floor and on latest | Claude Code |
| M3 | Release candidate + real-agent check | `0.1.0rc1` on PyPI; installed from PyPI in a fresh venv; one real ADK agent drove a surface end to end | Owner + Claude Code |
| M4 | 0.1.0 public | Repo public, `0.1.0` on PyPI, GitHub release, listed on A2UI and Streamlit galleries | Owner |

Estimated effort with the owner's evenings: M2 one or two sessions; M3 one session plus fixes; M4 an hour plus waiting for listing PRs.

### M1 — Harden the spike (awaiting review)
Defined in `handoff-m1.md`. Exit gate is the owner's review, including reading the frontend diff: it is the part most likely to hide spike-era shortcuts.

### M2 — Release engineering
Handoff to write after M1 is merged.

- **CI (GitHub Actions):** ruff, TypeScript strict, frontend tests, pytest; build frontend then wheel and sdist; wheel-content guard (no `*.map`, no CDN URLs, bundle and capabilities JSON present); install the built wheel in a fresh venv and import it.
- **Version matrix, kept small:** Python 3.10 and latest; Streamlit at the declared floor and latest. The floor `>=1.51` has never been run. CI either proves it or raises it. Raising the floor is fine; claiming one we haven't tested is not.
- **Browser smoke test:** one Playwright test that starts `examples/basic_app.py`, clicks the button, and asserts the returned action appears. Only one; this is the guard against a Streamlit release silently breaking CCv2 behaviour we depend on.
- **Packaging metadata:** single-sourced version, classifiers, project URLs, `LICENSE` and the generated `THIRD_PARTY_LICENSES.txt` in the wheel (no `NOTICE`: no bundled dependency ships one, see `docs/m1-report.md`), sdist that can rebuild the frontend (or a documented decision that it can't).
- **Release workflow:** tag `v*` → build in CI → publish with PyPI Trusted Publishing (OIDC, no API token stored). Configure the publisher as "pending" on PyPI so the first upload claims the name.
- **Repo hygiene, minimal:** `CHANGELOG.md`, short `CONTRIBUTING.md` (how to build, the out-of-scope list), `SECURITY.md` pointing to `docs/security.md` with a private reporting route, Dependabot for npm and pip with `@a2ui/*` excluded from auto-bumps (pins are deliberate).
- **Error boundary (owner decision after M1):** follow Streamlit's own pattern, one small class `ErrorBoundary` around each surface, so an exception while React renders one surface shows a plain-text notice (and the bound `console.warn`) instead of blanking the whole component. Needs a one-line exception to the "function components only" convention in `CLAUDE.md`. Add a Vitest or Playwright check that a throwing surface leaves the others rendered.
- **Bundle whitespace:** try `codegen.removeWhitespace` in the Vite build. Record raw and gzip size before and after; keep it only if the bundle still passes every test and the browser smoke test.
- **The M2 handoff must also:** refresh `docs/architecture.md` (it still describes the end of M0; fold in M1's findings and the ADRs); lift the `CLAUDE.md` out-of-scope bans that M2 and M3 need (CI workflows, publishing to PyPI); keep every other ban.

Not in M2: docs site, coverage badges, multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish.

### M3 — Release candidate and real-agent check
- **Upstream reports first** (so the README can link them): the `@a2ui/markdown-it` peer range and DOMPurify pin; `injectBasicCatalogStyles()` writing page-wide styles; `web_core` accepting unknown component types. Drafts in `docs/upstream-issues.md`. Link the issues from `docs/security.md` and ADR-008.
- **Real-agent check, outside the package.** Every payload so far was hand-written. In a scratch repo (personal machine, no employer code), build a minimal Google ADK agent with `a2ui-agent-sdk`, feed it `renderer_capabilities()`, and drive a surface through one action round trip and one streamed response. Record what broke. Fix bugs in the package; do not add an adapter. Whether a cleaned version ships as `examples/adk_agent_app.py` (needs an API key) is a decision for then.
  - Also watch for a second renderer-to-agent message replacing the first before a rerun (two quick clicks, or an action during a `callAgentFunction`). Record whether it happens; fixing it changes the return type and needs an ADR, so do not fix it in M3.
- **Publish `0.1.0rc1`** through the release workflow. Install it from PyPI in a fresh venv on another machine or container and run both examples. This is the first time the wheel leaves the build machine.
- **README pass:** a GIF of the basic example, install from PyPI, status badge text that says pre-1.0.

### M4 — 0.1.0 public
- Flip the repo to public (only now: the history then contains a working package, not a half-built spike).
- Tag `v0.1.0`; GitHub release notes from `CHANGELOG.md`, stating A2UI 1.0 only, the Streamlit floor, the known risks, and the pinned 0.x renderer packages.
- **Listings:**
  - A2UI ecosystem renderers page: PR adding a row (platform: Streamlit / Python; v1.0 only). Check the current repo's contribution instructions; the listing has moved between repos before.
  - Streamlit component gallery: PR to `streamlit/gallery` component registry; add the `streamlit-component` topic to the repo.
  - Posts: Streamlit forum (Custom Components), A2UI GitHub Discussions with a short demo.
- After the posts: watch issues for a week; fix only bugs as `0.1.x`.

## Decisions to make along the way
1. **Release on the 0.x renderer packages or wait for a 1.0-aligned `@a2ui/react`?** Recommendation: release; pins and overrides are documented, and waiting has no end date. When upstream ships, that is `0.1.x` or `0.2.0` depending on breakage.
2. **Streamlit floor:** decided by M2 CI, not by us.
3. **Ship an ADK example in the repo?** Decide after M3's real-agent check.
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