# Handoff: M2 — release engineering

Written 2026-11-17 at the owner's request. The decisions below are the owner's, taken during the M1 review (`docs/m1-report.md`, "Owner decisions after the report").

## Context

`streamlit-a2ui` renders Google's A2UI 1.0 protocol in Streamlit by wrapping the official web renderer (`@a2ui/react` + `@a2ui/web_core`) in a Streamlit Components v2 component.

- **M1 is merged** to `master`. It hardened the spike into v0.1 (`docs/m1-report.md`).
- **Part of M2 is merged too**, started early at the owner's request:
  - `.github/workflows/ci.yml`: one job on Python 3.13 and Streamlit 1.67, covering the build, Vitest, pytest with the wheel checks, ruff and Prettier.
  - One Playwright smoke test, `e2e/test_basic_app.py`.
  - Small code cleanups.
- CI is green on `master`.

M2 makes the package releasable, but does not release it. When M2 ends, a tag *could* publish `0.1.0rc1` to PyPI through a reviewed workflow, but nobody has created a tag and nothing has been uploaded. Publishing the release candidate is M3 (`docs/release-plan.md`).

Read these first: `CLAUDE.md`, `docs/release-plan.md` (M2 section), `docs/m1-report.md` and `docs/testing-playbook.md`. Where this file and `CLAUDE.md` disagree, this file wins, and step 1 brings `CLAUDE.md` in line.

## Decisions (treat as settled)

- **Error boundary.** Follow Streamlit's own pattern: one small class component, `ErrorBoundary`, using `getDerivedStateFromError` and `componentDidCatch`, around each surface. Streamlit's version is `frontend/lib/src/components/shared/ErrorBoundary/ErrorBoundary.tsx`; React's documentation recommends the same. This is the one allowed exception to "function components only"; record it in `CLAUDE.md`. Do not add `react-error-boundary`.
- **`THIRD_PARTY_LICENSES.txt` stays** in the wheel. There is no `NOTICE`, because no bundled dependency ships one.
- **Lazy component registration stays.** The CI matrix guards it against Streamlit changing when registration happens.
- **`dropConsole` stays on,** with our one `console.warn` going through the reference bound in `session.ts`.
- **The Streamlit floor is decided by CI, not by us.** If `1.51` fails, raise the floor to the lowest version that passes. Don't add compatibility code for older versions without asking.
- **Publishing uses PyPI Trusted Publishing (OIDC).** No API token is ever stored in the repository or in GitHub secrets.
- **`@a2ui/*` and `dompurify` pins are deliberate.** Dependabot must not bump them.
- **The second outbound message per rerun is not M2 work.** It's watched during M3's real-agent check.
- **The sdist ships the prebuilt frontend** (`build/`, `renderer_capabilities.json`, `THIRD_PARTY_LICENSES.txt`), as it does today. Building a wheel from the sdist must not need Node. Document this and verify it (step 5); do not add frontend sources to the sdist.

## Steps

Work on branch `m2-release`, which already exists and was cut from `master` after PR #3. Make small commits, one concern each. Push or open a pull request only when the owner asks. Never create a tag or a GitHub release, and never upload anything to PyPI or TestPyPI.

1. **Update `CLAUDE.md`.**
   - Set the current milestone to M2, with this file's acceptance criteria.
   - Add the error-boundary exception to Conventions.
   - Add the new commands: matrix, wheel smoke test, release dry run.
   - Add the new files to the layout.
   - Keep M1's criteria as a record.
   - Keep every out-of-scope item except those this handoff lifts. Publishing stays banned in M2.
2. **Version matrix in CI.** Extend `ci.yml` to two combinations: Python 3.10 with the Streamlit floor (`1.51.*`), and Python 3.13 with the latest Streamlit (unpinned, or `>=1.67`).
   - Run the full job, including the e2e test, on both.
   - Keep the existing pins for pytest, ruff and Playwright.
   - If the floor fails, find the lowest Streamlit release that passes. Raise `requires-python`/`dependencies` and the README to match, and record the failure in the report.
   - Watch out: Streamlit reads any `STREAMLIT_<OPTION>` environment variable as a CLI option, so never name a workflow variable `STREAMLIT_*`. The current pin is `PIN_STREAMLIT` for this reason.
3. **Installed-wheel smoke test in CI.**
   - Build the wheel and the sdist once, and upload both as workflow artifacts.
   - In a separate step or job, create a fresh venv and install the wheel (not editable).
   - From a directory outside the checkout, import the package and call `renderer_capabilities()`.
   - Run `pytest e2e` against the installed wheel.
   - This must prove the wheel works without the source tree on `sys.path`.
4. **Single-source the version.** The version is in three places today: `pyproject.toml` (`0.0.1`), `streamlit_a2ui/pyproject.toml` (the component manifest Streamlit reads, `0.0.1`), and `streamlit_a2ui/frontend/package.json` (`0.1.0`).
   - Pick one source; the root `pyproject.toml` is the obvious one.
   - Make the others follow it, or check that they match.
   - Check whether Streamlit reads the manifest's `version` at all before deciding. Record what you found.
   - Set the version to `0.1.0rc1` for M3.
5. **Packaging metadata.**
   - Add classifiers (license, Python versions, `Framework :: Streamlit` if PyPI accepts it, development status "4 - Beta" or lower), keywords, and `[project.urls]` (Homepage, Source, Issues, Changelog). The repository is `https://github.com/josechudev/streamlit-a2ui` and is still private.
   - Include `THIRD_PARTY_LICENSES.txt` in `license-files` next to `LICENSE`, if setuptools allows it for a generated file. Otherwise record why not.
   - Verify that `uv build --sdist`, followed by building a wheel from that sdist with Node absent from `PATH`, produces a wheel equal in content to the direct one. Add this as a CI step.
   - Run `twine check` (or `uv publish --dry-run` if it exists) on both artifacts in CI.
6. **Release workflow, written but not run.** Add `.github/workflows/release.yml`:
   - Triggered on tags `v*`, with `workflow_dispatch` for a dry run that builds and stops before publishing.
   - It rebuilds from scratch with the same steps as CI, checks that the tag equals the package version, uploads the artifacts, then publishes in a separate job.
   - The publish job uses `environment: pypi`, `permissions: id-token: write` and nothing else, and `pypa/gh-action-pypi-publish` pinned to a commit SHA.
   - Pin every third-party action to a commit SHA, with the release in a comment, as `ci.yml` does.
   - Write down the owner's one-time setup in the report and in `CONTRIBUTING.md`. You must not do any of it:
     - configure a pending publisher on PyPI (project `streamlit-a2ui`, this repository, workflow `release.yml`, environment `pypi`);
     - create the `pypi` environment in GitHub with the owner as required reviewer.
7. **Repository hygiene, kept minimal.**
   - `CHANGELOG.md` in Keep a Changelog style, with an `[0.1.0rc1] - Unreleased` section summarising M1 and M2.
   - A short `CONTRIBUTING.md`: prerequisites, the build and test commands, the testing playbook, the out-of-scope list, the release process.
   - `SECURITY.md` pointing at `docs/security.md`, with a private reporting route (GitHub private vulnerability reporting).
   - `.github/dependabot.yml` covering npm in `streamlit_a2ui/frontend`, pip at the root, and `github-actions`, weekly. Ignore `@a2ui/*` and `dompurify` in npm.
8. **Error boundary** (see Decisions).
   - Wrap each surface in `ErrorBoundary`. On error it renders a plain-text notice in the existing `.a2ui-notice` style, through React text and never HTML, and logs through the bound `warn`.
   - The other surfaces and the notices list stay rendered.
   - The boundary resets when the session replays (new generation key).
   - Test it: a surface whose render throws leaves its sibling rendered and shows the notice. If no A2UI message can make a basic-catalog component throw, test the boundary directly with a throwing child. A DOM test environment such as `jsdom` as a Vitest dev dependency is acceptable.
   - Keep the frontend to a handful of files.
9. **Bundle whitespace.** Try the Rolldown/Oxc option that removes whitespace from the ES output; find its current name in the installed `vite`/`rolldown` documentation or types, not from memory.
   - Record raw and gzip sizes before and after.
   - Keep it only if every test, including e2e, still passes.
   - The license-comment and `dropConsole` behaviour must not change.
10. **Refresh `docs/architecture.md`.** It still describes the end of M0. Bring it to the current state: Components v2, the log and cursor, `LogSession`, the bundle claim, error notices and the boundary, lazy registration, CI and release. Use the ADRs and M1's findings, and keep it short. Any change to the Architecture or Security sections of `CLAUDE.md` still needs an ADR and the owner's approval. M2 should need none; if it does, stop and ask.
11. **Report.** Write `docs/m2-report.md`, then stop and wait for review.

## Acceptance criteria

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

## Constraints

- Everything in `CLAUDE.md`'s Architecture and Security sections still holds:
  - Components v2 with `isolate_styles=True`;
  - the basic catalog only;
  - no HTML, CSS or JS parameters, and no `dangerouslySetInnerHTML`;
  - markdown only through `@a2ui/markdown-it`;
  - no CDN or runtime fetching;
  - one outbound trigger;
  - Python does not parse messages.
- The public API is unchanged: `a2ui_surface(messages, *, key) -> dict | None` and `renderer_capabilities() -> dict`.
- The `@a2ui/*` and `dompurify` pins are unchanged. If a newer `@a2ui/*` release exists, note it in the report and don't upgrade.
- GitHub Actions:
  - least-privilege `permissions` (default `contents: read`);
  - `persist-credentials: false` on checkout;
  - third-party actions pinned to commit SHAs;
  - dev tool versions pinned;
  - timeouts on every job.
  - Keep CI minutes modest, because the repository is private: two matrix legs, not more.
- No secrets, tokens or API keys anywhere. No employer names, code or data.
- Push or open a pull request only when the owner asks. Never create tags or releases, never upload.

## Out of scope: do not build, ask first

- Publishing to PyPI or TestPyPI, creating tags or GitHub releases, or changing the repository's visibility. These are M3 and M4.
- A real agent or an ADK example (M3).
- Filing the upstream issues. The owner does it; drafts are in `docs/upstream-issues.md`.
- Returning a list of messages, or any other change to ADR-009 or the return type.
- Geospatial or any custom catalog; agent adapters; A2UI 0.9.x or 0.8.
- A streaming helper; typed Python message models; persisting form state across remounts.
- A docs site, coverage badges, a multi-OS matrix, pre-commit frameworks, or release automation beyond tag-to-publish.

## Things that are easy to get wrong

- **`STREAMLIT_*` environment variables** become Streamlit CLI options; see step 2. This broke CI once already.
- **Node:** on the owner's machine `~/.nvm/nvm.sh` is missing. Use `export PATH=~/.nvm/versions/node/v24.15.0/bin:$PATH`. The system Node is 23.
- **The e2e test is outside the default pytest run** (`testpaths = ["tests"]`). Run it with `pytest e2e` after `playwright install chromium`.
- **Basic-catalog text-field labels are not linked to their inputs,** so the e2e test finds fields by role and position within `.a2ui-surface`.
- **After `npm run build`,** restart Streamlit and reload the page. A second bundle copy only shows a notice.
- **`renderer_capabilities.json` and `THIRD_PARTY_LICENSES.txt` are generated and git-ignored.** Never hand-edit them; CI must run `npm run build` before packaging.
- **`.claude/` is local and untracked.** Do not commit it.

## Deliverable: `docs/m2-report.md`

- Each acceptance criterion: pass, fail or needs owner verification, with how it was checked, including links to the CI runs if you were asked to push.
- The Streamlit floor that CI proved, and what failed below it, if anything.
- How the version is single-sourced, and what Streamlit does with the manifest's version.
- The owner's one-time setup for Trusted Publishing, step by step.
- Bundle size before and after, and the whitespace decision.
- Anything in this handoff or `CLAUDE.md` that turned out to be wrong.
- Open problems and suggested next steps for M3, kept separate from what was done.
