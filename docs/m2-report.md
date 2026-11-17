# M2 report: release engineering

Date: 2026-11-17. Branch `m2-release`, cut from `master` after PR #3. It holds the handoff commit plus the M2 commits listed at the end. Nothing has been pushed, and no tag, GitHub release or upload was made. The handoff is in `docs/handoff-m2.md`.

**The workflows have not run on GitHub.** The branch is not pushed, so criteria 1, 2, 3, 5 and 9 depend on CI and are checked only by running each job's steps locally, on macOS. They pass locally. They become "pass" once the owner pushes the branch, opens a pull request and CI goes green.

**Update after the review (2026-11-17):** the owner pushed `m2-release` and opened PR #4. CI passed on it, so criteria 1, 2, 3 and 9 now pass on GitHub; see "CI on GitHub". Criterion 5 is unchanged: `release.yml` has not run. PR #4 was merged as `25b370f`.

## Acceptance criteria

| # | Criterion | Result | How it was checked |
|---|---|---|---|
| 1 | CI runs the full job on Python 3.10 with the floor and on 3.13 with the latest Streamlit, both pass on a PR; the declared floor is one CI ran | **Pass** (GitHub: PR #4, both `Test` jobs) | `ci.yml` `test` job is a two-leg matrix: `{3.10, streamlit==1.59.*}` and `{3.13, streamlit>=1.67}`, each running the frontend build, Vitest, Prettier, ruff, pytest and the e2e test. Both legs were run locally with the same pins (see "Streamlit floor"). `pyproject.toml` and the README declare `>=1.59`, the floor leg's version. |
| 2 | CI builds the wheel and sdist, installs the wheel in a fresh venv outside the checkout, imports it and passes e2e | **Pass** (GitHub: PR #4, `Build wheel and sdist` and `Installed wheel smoke test`) | `package` job builds both once and uploads `dist`; `wheel-smoke` downloads it, installs the wheel (not editable) into a fresh venv, imports it from `$RUNNER_TEMP` and asserts `__file__` is in `site-packages` and not under the checkout, then runs `pytest e2e` with that venv. The e2e server now starts from a temporary directory: `python -m` puts the working directory on `sys.path`, which would have let the checkout shadow the wheel. Negative control: in a venv with Streamlit but no wheel, e2e fails with `ModuleNotFoundError: No module named 'streamlit_a2ui'`. |
| 3 | A wheel built from the sdist without Node equals the direct wheel; `twine check` passes on both | **Pass** (GitHub: PR #4, `Build wheel and sdist`) | `uv build --sdist` and `uv build --wheel` separately, then a wheel from the sdist with `PATH` reduced to uv's directory plus `/usr/bin:/bin`, after asserting `command -v node` finds nothing. `scripts/compare_wheels.py` compares every member by name and SHA-256, RECORD and METADATA included: identical. `twine check --strict` (7.0.0) passes on both. |
| 4 | Version defined once; package, manifest and `package.json` agree; version is `0.1.0rc1` | **Pass** | Root `pyproject.toml` is the only source, `0.1.0rc1`. The component manifest and `package.json` carry no version (see "Version"), which `tests/test_version.py` enforces; `tests/test_wheel.py` checks the wheel's METADATA version equals `pyproject.toml`. The installed package reports `0.1.0rc1`. |
| 5 | `release.yml` exists, actions SHA-pinned, only publish has `id-token: write` and is gated by `pypi`, refuses a mismatched tag, `workflow_dispatch` dry run stops before publishing; no tag, no upload | **Pass (by review and local simulation); not run** | Triggers: `push: tags: ["v*"]` and `workflow_dispatch`. Top-level `permissions: contents: read`. `build` repeats CI's package steps, then compares the tag (without `v`) to `pyproject.toml`'s version and checks the built file names. `publish` has `if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')`, `environment: pypi`, `permissions: id-token: write` only, and `pypa/gh-action-pypi-publish` pinned to `7245906f…` (v1.14.3, annotated tag dereferenced). Every action is pinned to a SHA with its release in a comment. `actionlint` reports nothing on either workflow. The tag check was run locally: `v0.1.0rc1` passes, `v0.1.0` fails. No tag created, nothing uploaded, the workflow never ran. |
| 6 | `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/dependabot.yml` exist; Dependabot ignores `@a2ui/*` and `dompurify` | **Pass** | All four exist. Dependabot: npm in `/streamlit_a2ui/frontend` (ignores `@a2ui/*` and `dompurify`), pip at `/` (`increase-if-necessary`, so it does not raise the floor while new releases are in range), `github-actions`, all weekly. |
| 7 | A throwing surface shows a plain-text notice and leaves the other surfaces and the notices list rendered, shown by a test | **Pass** | `src/ErrorBoundary.test.tsx` (jsdom) renders the real `Surfaces` with `A2uiSurface` mocked to throw for one surface: the boundary's text notice for it, the other surface, and the notices list ("1 A2UI error" with its item) are all rendered, and the bound `warn` is called. A second test shows a new generation key resets the boundary. No A2UI message was found that makes a basic-catalog component throw while rendering, so a browser check was not possible. |
| 8 | Bundle sizes before and after the whitespace change, keep or revert | **Pass: kept** | See "Bundle size". |
| 9 | All tests and linters pass locally and in CI; playbook parts 3 and 4 pass in a browser or are marked | **Pass** (GitHub: all four checks on PR #4). Click-through **pass**, with B9's expectation corrected | See "Test results" and "Click-through". |
| 10 | `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `docs/architecture.md`, `docs/security.md`, `docs/testing-playbook.md`, `docs/release-plan.md` and this report exist and agree | **Pass** | All updated for the 1.59 floor, the error boundary, the version rule, the packaging commands and the release process. `git grep` finds no remaining `1.51` floor claim outside the M0/M1 records and the handoff. ADR-002 mentions 1.51 only as the release that introduced Components v2, which is still true. |

## CI on GitHub

Added after the review. The owner pushed `m2-release` and opened [PR #4](https://github.com/josechudev/streamlit-a2ui/pull/4). CI [run 44181204551](https://github.com/josechudev/streamlit-a2ui/actions/runs/44181204551) on the PR head `2c39184` passed all four checks:

| Check | Criteria | Result |
|---|---|---|
| [Test (py3.10 / streamlit floor)](https://github.com/josechudev/streamlit-a2ui/actions/runs/44181204551/job/134385682090) | 1, 9 | success |
| [Test (py3.13 / streamlit latest)](https://github.com/josechudev/streamlit-a2ui/actions/runs/44181204551/job/134385682873) | 1, 9 | success |
| [Build wheel and sdist](https://github.com/josechudev/streamlit-a2ui/actions/runs/44181204551/job/134385682649) | 2, 3, 9 | success |
| [Installed wheel smoke test](https://github.com/josechudev/streamlit-a2ui/actions/runs/44181204551/job/134386036414) | 2, 9 | success |

PR #4 was merged as `25b370f`. The push to `master` passed too ([run 44183027275](https://github.com/josechudev/streamlit-a2ui/actions/runs/44183027275)). `release.yml` has not run, so criterion 5 still rests on review and local simulation.

## Streamlit floor: 1.59

`1.51` failed, so the floor was raised to the lowest release that passes the full job on Python 3.10.20 with the CI pins (pytest 9.2.0, ruff 0.17.5, pytest-playwright 0.10.0, playwright 1.65.2):

| Streamlit | pytest | e2e | What failed |
|---|---|---|---|
| 1.51.0 | fail | fail | `TypeError: component() got an unexpected keyword argument 'isolate_styles'` |
| 1.52.2 | — | — | `isolate_styles` still absent from `st.components.v2.component` (signature check only) |
| 1.53.0, 1.56.0 | fail | fail | e2e: the page renders its title but the component never mounts, with no console or server error. pytest: the `AppTest` failure below |
| 1.57.0, 1.58.0 | fail | **pass** | pytest only: `StreamlitComponentRegistryError: No files found matching pattern 'index-*.css' in package root <MagicMock …>` (`AppTest` mocks the component registry) |
| **1.59.0** | pass | pass | — |
| 1.60.0 | pass | pass | — |
| 1.67.0 (latest leg, Python 3.13) | pass | pass | — |

Not run: 1.54 and 1.53.1 (only the `isolate_styles` check), 1.55, and 1.59.x patch releases after 1.59.0. 1.53.0 and 1.56.0 both fail the same way, so 1.54–1.55 were not run in full.

1.57 and 1.58 render and round-trip correctly in the browser; only `tests/test_component.py`'s `AppTest` fails there. The handoff says the floor is the lowest version CI passes, without compatibility code, so it is 1.59. The owner could lower it to 1.57 by changing that test, not the package.

## Version

- **Source:** `version` in the root `pyproject.toml`, now `0.1.0rc1`.
- **The component manifest** (`streamlit_a2ui/pyproject.toml`) no longer has a version. In Streamlit 1.67, `components/v2/manifest_scanner.py:481` reads `[project] version` and falls back to the installed distribution's version, then `"0.0.0"`; the only use is a debug log line (`component_manager.py:371`). `[project] name` is used (`component_manifest_handler.py:58`, as the base of registered component names) and stays `streamlit-a2ui`. The manifest is found through the installed distribution's file list (`manifest_scanner.py:226-305`), which is why it is package data.
- **`package.json`** is private and never published, and npm accepts a private package without a version, so the field was removed (with its two lockfile entries). npm would need `0.1.0-rc.1`, not the PEP 440 form, so a copy would have to be translated as well as kept in sync.
- **Checks:** `tests/test_version.py` (no version in the manifest or `package.json`) and `tests/test_wheel.py` (wheel METADATA version equals `pyproject.toml`).

## Packaging metadata

- **Classifiers** were checked against the `trove-classifiers` package. `Framework :: Streamlit` does not exist there, so it is omitted. `License :: OSI Approved :: Apache Software License` is omitted because setuptools refuses to build with a license classifier next to a PEP 639 `license = "Apache-2.0"` expression ("License classifiers have been superseded by license expressions"). Used: Development Status 4 - Beta, Python 3.10–3.13 (the versions CI covers at the ends), Intended Audience, OS Independent, Topic.
- **`license-files`** lists `LICENSE` and the generated `streamlit_a2ui/THIRD_PARTY_LICENSES.txt`. setuptools accepts the git-ignored file and ships it under `dist-info/licenses/`, but silently skips it if it is missing, so a test checks METADATA lists both.
- **`LICENSE` was a placeholder.** It held the component template's `YOUR LICENSE HERE`, so every wheel so far declared Apache-2.0 without its text. It now holds the unmodified Apache License 2.0 (sha256 `cfc7749b…523d30`, the canonical `LICENSE-2.0.txt`, copied from an installed package's dist-info), and a test checks the wheel ships it.
- **URLs:** Homepage, Source, Issues and Changelog point at `https://github.com/josechudev/streamlit-a2ui`, which is still private, so they 404 for others until M4.
- **The sdist** ships the prebuilt frontend, as decided; no frontend sources.

## Trusted Publishing: owner's one-time setup

Not done; nothing here was done by Claude Code. Also in `CONTRIBUTING.md`.

1. On PyPI (signed in as the owner): Account settings → Publishing → "Add a new pending publisher" → GitHub. Project name `streamlit-a2ui`, owner `josechudev`, repository `streamlit-a2ui`, workflow `release.yml`, environment `pypi`. The first successful publish creates the project and claims the name (still free on 2026-11-17).
2. On GitHub: Settings → Environments → New environment `pypi`. Add the owner as a required reviewer. Optionally limit deployment to tags matching `v*`.
3. On GitHub: Settings → Code security → enable private vulnerability reporting, which `SECURITY.md` points to.
4. Before tagging in M3: push `m2-release` with an explicit refspec (`git push origin m2-release`; the branch tracks `origin/master`), open the pull request, wait for CI, merge, then optionally run the release workflow by hand as a dry run.

## Bundle size

`codegen.removeWhitespace` under `build.rolldownOptions.output.minify` (Rolldown's `CodegenOptions.removeWhitespace`, `node_modules/rolldown/dist/shared/binding-*.d.mts`; documented as defaulting to true, but not in effect for Vite's library-mode ES output).

| | JS raw | JS gzip -9 | Lines | CSS |
|---|---|---|---|---|
| M1 | 955.08 kB (Vite) | 262.29 kB (Vite) | — | 1.98 kB |
| M2 before (with the error boundary) | 955,724 B | 257,336 B | 26,917 | 1,981 B |
| M2 after | 764,458 B | 234,480 B | 1,012 | 1,981 B |

20.0% smaller raw, 8.9% smaller gzipped. Unchanged: no license comments (none before either; the licenses are in `THIRD_PARTY_LICENSES.txt`), no `console.log`/`debug`/`info`, the one bound `console.warn` survives, DOMPurify `3.4.18` present. All tests, including e2e and the click-through, pass on the new bundle. **Kept.**

## Test results

Local run of every CI job's steps on macOS, Node 24.15.0, uv 0.11.14, pytest 9.2.0, ruff 0.17.5, pytest-playwright 0.10.0, playwright 1.65.2.

| Check | Latest leg (Python 3.13.13, Streamlit 1.67.0) | Floor leg (Python 3.10.20, Streamlit 1.59.2) |
|---|---|---|
| `npm ci`, `format:check`, `typecheck`, `npm run build` | pass (no source maps; 32 license entries) | same build |
| Vitest | 12 passed | — |
| ruff check, ruff format --check | pass | pass |
| pytest | 23 passed | 23 passed |
| e2e | 1 passed | 1 passed |

| `package` / `wheel-smoke` / release check | Result |
|---|---|
| `uv build --sdist`, `uv build --wheel` | `streamlit_a2ui-0.1.0rc1.tar.gz`, `streamlit_a2ui-0.1.0rc1-py3-none-any.whl` |
| Wheel from the sdist with no `node` on `PATH`, compared | `identical: 12 files, same names and SHA-256 digests` (from a clean tree; see below) |
| `twine check --strict` | PASSED, both |
| sdist contents | prebuilt `frontend/build/`, `renderer_capabilities.json`, `THIRD_PARTY_LICENSES.txt`; no `src/`, no `node_modules` |
| Installed wheel imported from outside the checkout | `__file__` in the venv's `site-packages`; capabilities returned |
| e2e against the installed wheel, fresh venvs | pass, twice in a row (about 35 s each), after the fix below |
| Release tag check | `v0.1.0rc1` accepted, `v0.1.0` rejected |

Two problems found by this run, both fixed:

- **Stale bundles in local wheels.** A setuptools cache, `build/` at the repo root (git-ignored, left from earlier local builds), still held two old `index-*.js` files, and setuptools copied them into every wheel built in this checkout, where the component's `js=` glob would have failed on more than one match. `tests/test_wheel.py` only checked that a bundle existed, so it passed. The test now requires exactly one JS and one CSS file, the stale cache was deleted, and `CLAUDE.md` and the playbook say to clear it before a local wheel build. CI checkouts never have it.
- **e2e flake in a fresh venv.** Playwright's `expect` waits 5 s by default and ignores `page.set_default_timeout`. In a brand-new venv the first script run imports pandas and pyarrow for the first time and took over 30 s on this Mac, so the installed-wheel run failed intermittently. Assertions now get 20 s, and the first render 90 s.

## Click-through (playbook parts 3 and 4)

In the Chromium-based browser pane of the Claude desktop app, macOS, Streamlit 1.67.0, on the whitespace-stripped bundle.

| # | Result | Notes |
|---|---|---|
| B1 | pass | Form, Send, caption, "None yet" |
| B2 | pass | One `send_message` action with `{"name":"Ada","message":"Hello there"}`; reply "Thanks, Ada! The agent got 11 characters." |
| B3 | pass | New action, new timestamp |
| B4 | pass | Title updated, unsent " DRAFT" text still in the field (read from the DOM), log length +1 |
| B5 | pass | Red plain-text `VALIDATION_FAILED [contact]` notice, form and text kept, JSON panel unchanged, one `[streamlit-a2ui] A2UI error` warning in the console |
| B6 | pass | Send after B5 returns a new action |
| B7 | pass | Surface rebuilt from scratch, notice gone |
| B8 | pass | With the browser switched to dark (Streamlit's "Use system setting"), the surface and the notice followed without a reload. The ⋮ → Settings route was not clicked |
| B9 | pass, **expectation corrected** | A reload starts a new Streamlit session, so the log starts over; the playbook said title updates would be kept. Corrected in the playbook |
| S1 | pass | Element count grew in steps every ~0.5 s while the caption said `streaming` |
| S2 | pass | "Acknowledged after 4 log lines", streaming continued, `actions received: 1` |
| S3 | pass | `stream finished`, log length stopped growing |
| S4 | pass | "Acknowledged after 8 log lines", `actions received: 2` |
| S5 | pass | Restart streamed again from empty |

## Wrong in the handoff or `CLAUDE.md`

1. **The 1.51 floor** in the handoff, `CLAUDE.md`, the README, the playbook, the release plan and the old `docs/architecture.md`: Streamlit 1.51 introduced Components v2 but has no `isolate_styles`, and nothing below 1.59 passes CI.
2. **"Add classifiers (license, …)"**: setuptools forbids a license classifier alongside a PEP 639 license expression. `Framework :: Streamlit` does not exist.
3. **`uv build` in `CLAUDE.md`** builds the wheel from the sdist, so it cannot be used for the comparison; the commands now build them separately.
4. **`LICENSE`** was the template placeholder, not the Apache-2.0 text, since M0.
5. **Playbook B9** expected a reload to keep the log; a reload is a new session.
6. **ADR-002** needed no change: it says Components v2 arrived in 1.51, not that 1.51 is enough for this package.
7. **Agent worktrees** (used for the CI work) were cut from `master`, not `m2-release`; the commits were cherry-picked onto `m2-release`.
8. **The wheel test's bundle check** passed on a wheel with three bundles; it now requires exactly one (see "Test results").

## Dependencies

No `@a2ui/*` release newer than the pins: `@a2ui/react` and `@a2ui/web_core` 0.15.0, `@a2ui/markdown-it` 0.2.2, `dompurify` 3.4.18 (all still the latest on npm). New dev dependency: `jsdom` ^31.0.1, for the boundary test. `npm audit` now also reports picomatch GHSA-fc5q-39xc-vjpf (ReDoS), published after M1, reached only through Vite and Vitest with our own globs and not in the bundle; recorded in `docs/security.md`.

## Open problems and suggested next steps for M3

These are proposals, not work done.

1. **Push and run CI.** Criteria 1, 2, 3, 5 and 9 need a green pull request. Nothing has run on Linux yet; watch the `wheel-smoke` job's first-render time and the Node-free sdist step (it relies on `/usr/bin/python3` or a uv-managed Python under the reduced `PATH`).
2. **Owner setup for Trusted Publishing** (above), then lift the publishing ban in `CLAUDE.md` for M3.
3. **Floor 1.57?** Only `AppTest` fails on 1.57–1.58. If a lower floor matters, replace that test's `AppTest` check rather than adding package code.
4. **1.53–1.56 fail silently in the browser** (no mount, no error). Not investigated, since they are below the floor; worth knowing if a user reports a blank component on an old Streamlit.
5. **CSS file name.** The bundle's stylesheet is literally `index-_hash_.css` (Vite library mode does not substitute `[hash]` for CSS). The JS name is content-hashed; the CSS name never changes across releases. Harmless today; check how Streamlit caches component assets before relying on it.
6. **Dependabot does not see CI's dev-tool pins** (pytest, ruff, Playwright, twine are pinned inline in workflow `run:` lines). Bump them by hand, or move them to a requirements file Dependabot can read.
7. **Classifier for 3.14** once CI covers it; the matrix has two legs by design.
8. **The second outbound message per rerun** stays an M3 observation item, as decided.

## Commits

Oldest first, after the handoff commit `5cfb1b6`, plus this report:

```
3e44708 Bring CLAUDE.md in line with the M2 handoff
7ae091b Add Dependabot for npm, pip and GitHub Actions
ed9ffb4 Add SECURITY.md with a private reporting route
372011f Define the version once, in pyproject.toml, as 0.1.0rc1
e2c412e Wrap each surface in an error boundary
681fa8b Strip whitespace from the production bundle
89f0879 Run CI on a Python 3.10 / Streamlit floor leg and a 3.13 / latest leg
47f895c Build the wheel and sdist once and smoke-test the installed wheel
bd8d4c6 Add PyPI metadata: classifiers, keywords, URLs, bundled licenses
9e944a6 Check the sdist rebuilds the same wheel without Node, and twine-check both
5df7225 Add a tag-triggered release workflow using Trusted Publishing
77d2108 Replace the template's placeholder LICENSE with the Apache-2.0 text
31f78b0 Check the wheel's license text and version
2aef0c4 Record the Streamlit 1.59 floor and the packaging commands in CLAUDE.md
6ca5d28 Add a changelog with the 0.1.0rc1 entry
669a4db Add CONTRIBUTING.md with build, test, scope and release steps
b4fce35 Bring docs/architecture.md up to the current design
95db268 Bring the README, security, playbook and plan in line with M2
327ab8a Give the smoke test's first render time to import cold dependencies
2880e4a Require exactly one JS and one CSS bundle in the wheel
00c8b36 Document the stale setuptools build/ cache and how to clear it
```
