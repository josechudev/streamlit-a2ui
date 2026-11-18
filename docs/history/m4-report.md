# M4 report: 0.1.0 public

Date: 2026-11-18. The handoff is `docs/history/handoff-m4.md`. M4 landed through PRs #17–#22 and #24 and the PR that adds this report.

**Result:** `streamlit-a2ui 0.1.0` is on PyPI, published by `release.yml` from tag `v0.1.0`, which the owner pushed and approved. Checking the release candidate turned up a real bug, a 23-second first page load caused by the package, fixed in `0.1.0`. Installed from PyPI in a fresh environment, `0.1.0` passes both example click-throughs and shows its first surface in 0.9 s. The repository follows gitflow from M4 on. The GitHub release, the two listings and the two posts are drafted in `docs/history/m4-drafts.md` for the owner; the one-week watch starts once the posts are out and is appended here at its end.

## Acceptance criteria

| # | Criterion | Result | How it was checked |
|---|---|---|---|
| 1 | First-load delay tried in brand-new venvs with a Streamlit-only control; cause recorded; fixed with a test if it is the package's | **Pass** | Reproduced in two fresh venvs (23.0 s and 23.7 s to the surface), control 0.7 s. cProfile put it in the package's first `a2ui_surface` call. Fixed in PR #18 with a test that fails without the fix on both CI legs. See "First-load delay". |
| 2 | History in `docs/history/` with an index; no old paths; nothing linked from the rc1 README moved; commands in `CONTRIBUTING.md` | **Pass** | PR #19. `git grep` for the old paths finds only `docs/history/` ones. The files the rc1 README links are untouched. The old `CLAUDE.md` command block was compared line by line with `CONTRIBUTING.md`; only the rc-specific install (now `<version>`) and the dry run (now in the release steps) differ. |
| 3 | `0.1.0` on PyPI from `release.yml` and tag `v0.1.0` after a dry run on the same commit; owner pushed and approved; SHA-256 match; README right on PyPI; dated CHANGELOG | **Pass; the PyPI page's look needs owner verification** | See "Publication". PyPI shows the built-in browser a bot check, so the page was checked through the JSON API. |
| 4 | Fresh environment: imports from `site-packages`, a plain install picks `0.1.0`, playbook parts 3 and 4 pass | **Pass** | See "PyPI install". B1–B9 and S1–S5 pass. |
| 5 | GitHub release `v0.1.0` with notes from the CHANGELOG | **Open: drafted, not created** | Notes and the `gh release create` command in `docs/history/m4-drafts.md` §1. The owner creates the release. |
| 6 | Listing PRs to `a2ui-project/a2ui` and `streamlit/gallery`, drafted against the instructions as rechecked; gallery JSON validates | **Open: drafted and validated, not opened** | `docs/history/m4-drafts.md` §2 and §3. The A2UI row is a one-line diff that passes their Prettier check; the gallery JSON passes their schema. The owner opens both from forks. |
| 7 | Forum and A2UI Discussions posts drafted, published by the owner, URLs recorded | **Open: drafted, not published** | `docs/history/m4-drafts.md` §4 and §5. |
| 8 | One-week watch | **Not started** | Starts after the posts; appended below at its end. |
| 9 | No tag, upload, release, outside PR or post by Claude Code except at the owner's explicit request | **Pass** | See "Actions taken at the owner's request". The owner created and pushed both tags and approved `pypi`. |
| 10 | Tests and linters pass locally and in CI; no Architecture or Security change without an ADR; owner decisions recorded | **Pass** | Every PR merged with the four checks green; CI on `master` at `1c32025` ([run 44359538448](https://github.com/josechudev/streamlit-a2ui/actions/runs/44359538448)) and on `develop` at `47f5661` ([run 44360312761](https://github.com/josechudev/streamlit-a2ui/actions/runs/44360312761)) green. The first-load fix changes how the log is handed to Streamlit (a tuple), not what is passed, so ADR-004 holds. Decisions: see "Owner decisions". |
| 11 | Listed documents exist and agree | **Pass** | This PR adds `m4-drafts.md` and this report, and brings `CLAUDE.md` and `docs/release-plan.md` in line. |

## Owner decisions

- **ADK example:** not in this repository. Real-agent examples go to a separate repository, `josechudev/streamlit-a2ui-examples`, created by the owner on 2026-11-18. That work is M5 (`docs/release-plan.md`).
- **Google CLA:** signed by the owner as an individual, for the A2UI listing.
- **GitHub release assets:** none; the notes link PyPI and the release run.
- **Branching:** full gitflow with `develop` (2026-11-18). `develop` was created from `master` at `9cc0a23`; CI runs on pushes to it; Dependabot version updates target it; `CONTRIBUTING.md` documents `feature/*`, `release/*`, `hotfix/<version>` and docs-only `hotfix/<topic>`.
- **No `0.1.0rc2`:** after the first-load fix the owner chose to go straight to `0.1.0`.
- **GIF to `master` at once:** by a docs-only hotfix (PR #24), so the PyPI pages show it without a release.

## First-load delay

In M3 the first page load in a brand-new venv stayed on the title for over 45 seconds. M4 timed it before announcing.

**Setup:** macOS 15.7 (x86_64), uv 0.11.14, Python 3.13.13. Each venv brand-new with `uv pip install --no-cache`. The package venvs got `streamlit-a2ui==0.1.0rc1` from PyPI, with Streamlit 1.67.0. The control venv got Streamlit 1.67.0 only and ran `basic_app.py` with the component call removed. Timing: a script started the server headless and loaded the page in headless Chromium (Playwright 1.65.2, separate venv), timing from navigation to each text being visible. "After the call" is the subheader printed right after `a2ui_surface`.

| Run | Title | After the call | Surface ("Contact us") |
|---|---|---|---|
| rc1, venv 1, first run | 0.59 s | — | 22.97 s |
| rc1, venv 1, second run | 0.42 s | — | 3.22 s |
| Control, first run | 0.72 s | 0.74 s | n/a |
| Control, second run | 0.65 s | 0.67 s | n/a |
| rc1, venv 2, first run | 0.52 s | 23.44 s | 23.72 s |
| rc1, venv 2, second run | 0.50 s | 2.80 s | 2.81 s |
| rc1 patched (tuple), first run | 0.76 s | 0.79 s | 1.60 s |
| rc1 patched (tuple), second run | 0.53 s | 0.72 s | 0.82 s |
| **`0.1.0` from PyPI, first run** | 0.57 s | 0.76 s | **0.88 s** |
| `0.1.0` from PyPI, second run | 0.78 s | 1.08 s | 1.19 s |

**Cause:** cProfile around the first call (a third fresh venv) showed 26.3 s inside `a2ui_surface`. Nearly all of it, 25.0 s, was `import pandas` (pyarrow 4.2 s of that). The import was reached through Streamlit's Components v2 serializer: `serialize_mixed_data` → `_extract_dataframes_from_dict` → `dataframe_util.is_dataframe_like` on the `messages` list → `determine_data_format`. `is_dataframe_like` returns early for tuples, strings and numbers but not lists. A plain Streamlit app never loads pandas, which is why the control was fast. So this was the package's cost, not Streamlit's first import. On a warm machine the same import still cost about 2 s per server start.

**Fix** (PR #18): `data={"messages": tuple(messages)}`. JSON still sends an array, so the frontend is unchanged. `tests/test_component.py::test_a2ui_surface_does_not_import_pandas` runs an `AppTest` in a fresh interpreter and checks that `pandas` is not in `sys.modules`. It fails without the fix and passes with it on Python 3.13 with Streamlit 1.67.0 and on Python 3.10 with Streamlit 1.59.2. (`AppTest.from_function` cannot read source given with `-c` on 3.10, so the test uses `from_string`.) The playbook note and the e2e comment were updated; the CHANGELOG records it under `0.1.0` → Fixed.

## Tidy-up

- PR #19 moved `handoff-m1` … `-m4`, `spike-report`, `m1`–`m3-report`, `findings.md` and `notes-m1.md` with `git mv` into `docs/history/`, added `docs/history/README.md`, and updated every path. That includes `examples/streaming_app.py` and the moved files' references to each other. Stale status lines in `docs/architecture.md`, `docs/testing-playbook.md` (R2) and `docs/release-plan.md` were refreshed.
- The command list is now `CONTRIBUTING.md` "Build and test", in sections. `CLAUDE.md` keeps a pointer and Claude Code's local notes; the README and the playbook point to `CONTRIBUTING.md`.

## Publication

1. **Release branch:** `release/0.1.0` was cut from `develop` after #17–#19 (PR #20). Its release commit `def9f90` sets the version, dates the CHANGELOG and fixes the README's install text. Before the PR, the same tree passed locally:
   - Vitest 17, typecheck, Prettier and build;
   - pytest 24, ruff and e2e on both legs;
   - twine `PASSED` on `streamlit_a2ui-0.1.0` wheel and sdist;
   - Node-free sdist rebuild `identical: 12 files`;
   - installed-wheel e2e.

   Merge commit `cd164e40fb428aa2e73ea02f8152e055de366663`.
2. **Dry run:**
   - The owner's first one, [run 44355426510](https://github.com/josechudev/streamlit-a2ui/actions/runs/44355426510), started before PR #20 was merged, so it built the old `master` (`9cc0a23`, `0.1.0rc1`). It did not count.
   - After the merge, at the owner's request, Claude Code ran [run 44355836918](https://github.com/josechudev/streamlit-a2ui/actions/runs/44355836918) on `cd164e4`. Build and check succeeded and Publish was skipped. The log showed `package version: 0.1.0`, `identical: 12 files, same names and SHA-256 digests`, and twine `PASSED` on both files.
3. **Tag (owner):** annotated `v0.1.0` on `cd164e4`, pushed with `git push origin v0.1.0`. Before it, PyPI returned 404 for `0.1.0` and only `v0.1.0rc1` existed.
4. **Release run:** [run 44356056432](https://github.com/josechudev/streamlit-a2ui/actions/runs/44356056432), event `push`, ref `v0.1.0`. Build and check (including the tag check) succeeded; Publish to PyPI succeeded after the owner approved `pypi` on the web page.
5. **PyPI:** https://pypi.org/project/streamlit-a2ui/0.1.0/. Each file is identical by SHA-256 to the run's `dist` artifact and to PyPI's own digest:

   | File | SHA-256 | Bytes |
   |---|---|---|
   | `streamlit_a2ui-0.1.0-py3-none-any.whl` | `4f6988d27fe2522ec9e5c7e85abbd866a0e5b0e0a38366336a2feb367d584187` | 281,015 |
   | `streamlit_a2ui-0.1.0.tar.gz` | `fd34b1d36c31d3b26c59ec890ca6fbf92820faf58e32326a11939106d0f895d5` | 270,655 |

6. **Attestations:** PEP 740 publish attestations (`https://docs.pypi.org/attestations/publish/v1`) for both files. Each names GitHub `josechudev/streamlit-a2ui`, `release.yml` and environment `pypi`, and its subject digest equals the SHA-256 above.
7. **Metadata and README:**
   - Apache-2.0, `requires-python >=3.10`, `streamlit>=1.59`, Markdown description.
   - The description has no relative links, and all 14 absolute links return 200. Two refused a bare `HEAD` and returned 200 to a normal `GET`.
   - It installs with a plain `pip install streamlit-a2ui` and keeps the release-candidate advice as one correct sentence.

**What differed from `CONTRIBUTING.md`:** nothing in the release steps. The dry run must follow the merge; see "Wrong in the handoff".

## PyPI install

**Environment:** macOS, a new uv venv on Python 3.13 in the session's scratch directory, `--no-cache`.

1. **Install:** a `==0.1.0` install a few seconds after publishing failed: "there is no version of streamlit-a2ui==0.1.0", because the index had not caught up. A retry a minute later installed streamlit-a2ui 0.1.0 and Streamlit 1.67.0. There is no `direct_url.json`, so it came from the index.
2. **Import:** `streamlit_a2ui.__file__` is in the venv's `site-packages`, and the installed package is identical (`diff -r`) to the PyPI wheel. `renderer_capabilities()` returns the basic 1.0 catalog.
3. **A plain install picks `0.1.0`:** checked with uv 0.11.14 (`uv pip install --dry-run streamlit-a2ui`) and pip 26.3 (`pip install --dry-run --report - streamlit-a2ui`).
4. **Examples:** taken from `v0.1.0` into an empty folder and run with that venv in the built-in browser pane.
   - **Basic, playbook part 3:** B1–B9 pass.
     - B1: the surface was there on the first load.
     - B2: "Thanks, Ada! The agent got 11 characters."
     - B4: "Contact us (3)"; the unsent text was kept; the log went from 4 to 5.
     - B5: plain-text notice and exactly one `console.warn`; the JSON panel was unchanged.
     - B6: the reply counted 18 characters.
     - B7: the surface was rebuilt.
     - B8: light and dark checked by emulation.
     - B9: a reload started fresh.
   - **Streaming, playbook part 4:** S1–S5 pass.
     - S1: the log grew by one every 0.5 s, to 22, then "stream finished".
     - S5: the restart worked.
     - S2: "Acknowledged after 3 log lines", `actions received: 1`, and streaming went on.
     - S4: "Acknowledged after 8 log lines", `actions received: 2`.

## README GIF

The owner asked why the GIF seemed to show the returned message rather than a component. The form in it was the A2UI surface all along: `TextField`, `Button` and `Text` from the basic catalog, drawn by the official renderer and themed like Streamlit. But the GIF's longest frame (3 s) was scrolled to the returned JSON. The reply also appeared for 0.8 s as a small caption, because the updated `Text` kept the placeholder's `caption` look.

PR #24, a docs-only hotfix to `master`:
- The example now sends its reply with `variant: "body"`.
- The GIF was re-recorded with Playwright (light theme, 860×720, 13 frames, 90 KB). It ends with 4.2 s on the updated form, with the start of the JSON below.
- The README adds a caption naming the surface.

Because the README links the GIF on `master`, the PyPI pages for `0.1.0` and `0.1.0rc1` show the new one. The caption reaches PyPI with the next release. The GIF is in neither the wheel nor the sdist.

## Listings and posts

Drafted in `docs/history/m4-drafts.md`. The instructions were rechecked on 2026-11-18:
- **A2UI:** `docs/site/src/content/docs/ecosystem/renderers.mdx`, published as "Community Projects".
  - Fork, sign the Google CLA, add a row, open a pull request against `main`, then post in Discussions.
  - The repository formats with Prettier 3.8.4 and its `.prettierrc`. A first draft row longer than the description column re-padded the whole table (a 49-line diff), so the row was shortened to fit: a 1-line diff that passes `--check`.
  - Discussions categories include "Show and tell".
- **Streamlit gallery:** one JSON file per component in `components/registry/components/`, checked against `schemas/component.schema.json` by CI.
  - 216 entries; none mentions `streamlit-a2ui`.
  - Our file validates locally with `jsonschema` (Draft 2020-12, format checks).
  - Categories `LLMs` and `Integrations`.

None was opened or published by Claude Code.

## Actions taken at the owner's request

| Owner's words | Action |
|---|---|
| "Push and open PR" | pushed the M4 branch, opened #16 (closed when the branch was renamed for gitflow; replaced by #17) |
| "Full gitflow with develop" (question answer) | created `develop` from `master` (`9cc0a23`), renamed the branch, opened #17 |
| "ok lets go with ab c1" | branches and PRs #18, #19, #20 |
| "You merge them" | merged #18 and #19 into `develop` |
| "You merge it" | merged #20 into `master` |
| "You run it" | ran the `workflow_dispatch` dry run 44355836918 |
| "Yes, re-record it", "Now, via hotfix" | #23 (closed), hotfix #24 |
| "first: merge the pending prs in order" | merged #24, #21, #22 |

The owner created and pushed both tags and approved `pypi`.

## Wrong in the handoff, `CLAUDE.md` or the release plan

1. **The first-load delay was not Streamlit's first import.** Step (a) treated that as the likely case. It was the package's own call path, through Streamlit's dataframe detection. The e2e test's comment had blamed "Streamlit's dependencies (pandas, pyarrow)" since M2.
2. **A dry run before the release PR is merged builds the previous `master`.** Step 7 says "on the merge commit"; the first run happened before the merge. `CONTRIBUTING.md` now says "Dry run on the `master` merge commit".
3. **PyPI's index can lag the upload by a minute.** An exact-pin install right after publishing can fail; retry before suspecting the release.
4. **Renaming a pull request's head branch through the GitHub API closes the pull request** (#16). Push under the new name and open a new one.
5. **`gh pr checks --required` reports nothing for a PR into `develop`,** because `develop` has no ruleset yet. Use `gh pr checks` without `--required`.
6. **`hotfix/<version>` did not fit a docs-only fix.** `CONTRIBUTING.md` now allows `hotfix/<topic>` for files a published README links on `master`, with no version bump and no tag.

## Open problems and suggested next steps

These are proposals, not work done.

1. **Owner, to finish M4:**
   - create the GitHub release (§1 of the drafts);
   - open the two listing PRs (§2, §3);
   - publish the two posts (§4, §5; add the A2UI PR link to the Discussions post);
   - look at the PyPI page.
2. **Owner settings:** add a `develop` ruleset matching `master`'s; until then `develop` accepts direct pushes. Optionally make `develop` the default branch.
3. **Watch week:** seven days from the posts. Bugs are fixed on `hotfix/0.1.x`; everything else goes to the backlog.
4. **M5:** `streamlit-a2ui-examples` with a chat in which a real model writes the UI, and a README GIF from it. A session has started on it.
5. **Backlog unchanged:** returning a list of messages (the second-message limitation), React 19, custom catalogs, and dropping the overrides when upstream fixes ship (#4059 / pull request #4073, #4278, #4279).

## Pull requests

| PR | Merge | What |
|---|---|---|
| [#17](https://github.com/josechudev/streamlit-a2ui/pull/17) | `9ac8bf6` | M4 handoff, `CLAUDE.md` for M4, gitflow (`develop`, CI, Dependabot) |
| [#18](https://github.com/josechudev/streamlit-a2ui/pull/18) | `8b5449f` | First-load fix and its test |
| [#19](https://github.com/josechudev/streamlit-a2ui/pull/19) | `70e7bdf` | History to `docs/history/`, commands to `CONTRIBUTING.md` |
| [#20](https://github.com/josechudev/streamlit-a2ui/pull/20) | `cd164e4` | `release/0.1.0` into `master`, the tagged commit |
| [#21](https://github.com/josechudev/streamlit-a2ui/pull/21) | `1fbd5d1` | `master` back into `develop` |
| [#22](https://github.com/josechudev/streamlit-a2ui/pull/22) | `47f5661` | `0.1.0` recorded in `CLAUDE.md` and the release plan |
| [#24](https://github.com/josechudev/streamlit-a2ui/pull/24) | `1c32025` | Hotfix: the README GIF |
| this PR | | M4 drafts and this report; M5 in the release plan |

## Watch week

Appended at its end.
