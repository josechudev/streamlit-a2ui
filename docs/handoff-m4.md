# Handoff: M4 — 0.1.0 public

Written 2026-11-18, from the M4 section of `docs/release-plan.md` and the open problems at the end of `docs/m3-report.md`.

## Context

`streamlit-a2ui` renders Google's A2UI 1.0 protocol in Streamlit by wrapping the official web renderer (`@a2ui/react` + `@a2ui/web_core` 0.15.0) in a Streamlit Components v2 component.

- **M3 is merged** (PRs #10–#15; `master` at `9cc0a23`). All eight M3 criteria pass (`docs/m3-report.md`).
- **`0.1.0rc1` is on PyPI,** published by `release.yml` from the annotated tag `v0.1.0rc1` on `388f2a7` (release run 44248941528). The owner pushed the tag and approved the `pypi` environment. Files match the run's artifact; PEP 740 attestations name this repository, `release.yml` and `pypi`. PyPI's Trusted Publisher is now an active publisher, no longer a pending one.
- **A real ADK agent drove a surface** (action round trip and streamed response) with no package bugs. The checked-in examples stay hand-written.
- **Already done for M4:**
  - The repository is public (flipped at the start of M3; a full-history scan for secrets and employer data was clean first).
  - Topics are set: `a2ui`, `python`, `streamlit`, `streamlit-component`. The last one is what `streamlit/gallery` asks for.
- **Known problems carried in:**
  - The README published with `0.1.0rc1` says a plain `pip install` finds nothing. Wrong: pip and uv pick the rc while no final release exists. Fixed on `master`; PyPI keeps the wrong sentence on the rc1 page forever.
  - In M3's PyPI check, the very first page load in a brand-new venv stayed on the title for over 45 seconds, with nothing in the server log or the console. A reload rendered it at once. Cause unknown.
  - A second renderer-to-agent message produced before a rerun replaces the first (a double click returns one action). Documented in the README; changing it is backlog item 2 and needs an ADR. Not in M4.
- **Upstream to watch:** a2ui-project/a2ui#4059 (peer range; fix proposed in pull request #4073, which does not change the DOMPurify pin), #4278 (DOMPurify pin) and #4279 (page-wide stylesheet). If one ships a fix during M4, record it; do not upgrade `@a2ui/*` or drop an override in M4.

M4 publishes `0.1.0`, gets the package listed, and lets people know. It adds no features.

Read these first: `CLAUDE.md`, `docs/release-plan.md` (M4 section), `docs/m3-report.md` (especially "Wrong in the handoff, `CLAUDE.md` or the release plan" and "Open problems and suggested next steps for M4"), `CONTRIBUTING.md` (release process), `CHANGELOG.md`, `README.md` and `docs/testing-playbook.md`. Where this file and `CLAUDE.md` disagree, this file wins, and `CLAUDE.md` is brought in line.

## Decisions (treat as settled)

- **Publishing happens only through `release.yml`,** on a `v*` tag that the owner pushes and then approves in the `pypi` environment. Claude Code never creates or pushes a tag, never uploads to PyPI or TestPyPI, never runs `twine upload` or `uv publish`, and never runs `release.yml` except when the owner asks for a `workflow_dispatch` dry run.
- **Public actions are the owner's.** Claude Code drafts; the owner creates the GitHub release, opens the listing pull requests and publishes the posts. Claude Code does one of these only when the owner explicitly asks for that specific action in the same session, and never signs an agreement (such as Google's CLA) for the owner.
- **Release `0.1.0` on the 0.x renderer packages** (`docs/release-plan.md`, decision 1). The `@a2ui/*`, `@a2ui/markdown-it` and `dompurify` pins and overrides stay; React stays 18.
- **`0.1.0` is `0.1.0rc1` plus documentation and bug fixes.** No new features, no API change, no dependency change. If a code change is needed (for example for the first-load delay), it lands with a test before the release commit, and the owner decides whether it needs `0.1.0rc2` first.
- **A published version is final.** PyPI never accepts the same file name twice. A problem found after the upload is fixed in `0.1.1`.
- **The README is frozen per version on PyPI.** Everything the `0.1.0` page should say lands before the tag.
- **Files linked from the `0.1.0rc1` README stay where they are:** `README.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `CHANGELOG.md`, `LICENSE`, `docs/security.md`, `docs/testing-playbook.md`, `docs/architecture.md`, `docs/adr/`, `docs/images/basic-example.gif`, `examples/basic_app.py` and `examples/streaming_app.py`. The rc1 page links them on `master` and can never be changed.
- **Milestone history moves to `docs/history/`:** the handoffs (`handoff-m1.md` … `handoff-m4.md`), the reports (`spike-report.md`, `m1-report.md` … `m3-report.md`), `findings.md` (M0 evidence) and `notes-m1.md`. `docs/m4-report.md` is written there directly, as `docs/history/m4-report.md`. Current documents (`architecture.md`, `security.md`, `release-plan.md`, `testing-playbook.md`, `upstream-issues.md`, `adr/`, `images/`) stay in `docs/`.
- **The command list lives in `CONTRIBUTING.md`.** `CLAUDE.md` points to it and keeps only what is specific to Claude Code (the local Node path, the setuptools cache, subagents).
- **The watch week fixes bugs only,** each with a test, released as `0.1.x` through the same tag-and-approve route. Feature requests go to the backlog in `docs/release-plan.md`.
- **Pending owner decisions,** asked at the start of M4 and recorded in the report:
  1. **ADK example.** *Decided by the owner on 2026-11-18:* no ADK example in this repository. After `0.1.0`, a separate example repository (owned and created by the owner, built from the M3 scratch app without its `.env`) may show one, and the README may link it then. Not part of M4. Reasons: it needs an API key that this repository's CI never has, model availability changed by the hour during the M3 check, and the agent glue is the app's code.
  2. **Google CLA.** *Signed by the owner as an individual on 2026-11-18.* The A2UI listing pull request needs it. The CLA check matches the commit author's e-mail, so the listing commit must use the e-mail the owner signed with. Nothing employer-related goes into it.
  3. **GitHub release assets.** *Decided by the owner on 2026-11-18:* no assets; the notes link the PyPI page and the release run, so PyPI stays the one source of files.

## Steps

Work on a branch cut from `master`, in small commits with one concern each. `master` is protected, so everything lands through a pull request with the four checks green. Push or open a pull request only when the owner asks; push with an explicit refspec (`git push origin <branch>`).

### (a) First-load delay

1. **Reproduce before announcing.** On macOS, at least twice, each time in a **brand-new** uv venv outside the checkout, created and installed with `--no-cache`:
   - **Package run:** install `streamlit-a2ui==0.1.0rc1` from PyPI, copy `examples/basic_app.py` from the tag into an empty folder, start it headless (`--server.headless true`) on a free port, and time from server start to the first rendered surface (the "Contact us" title and the form). Use the built-in browser pane or Playwright; note which.
   - **Control run:** a separate brand-new venv with only `streamlit` (the same version the package run resolved) and a one-line app (`st.title("hello")`). Time it the same way.
   - **Second load:** in each venv, restart the server and time a second first page load, to separate one-time costs (bytecode compilation, macOS scanning of newly installed native libraries) from per-run costs.
   - Optionally, a third venv installed with `uv pip install --compile-bytecode`, to see whether compiling up front removes the delay.
2. **Decide from the result:**
   - The control run shows the same delay, or the delay is gone on the second load in both: it is Streamlit's or the machine's one-time cost. Add one sentence to the README (Install section) and keep the playbook note, now with the measured numbers.
   - Only the package run shows it: investigate (server log with `--logger.level debug`, browser console and network panel, the time from page load to the component's first `data` render). Fix it with a test if it is in the package; record it and stop for the owner if it needs an Architecture or Security change.
   - Not reproduced in two tries: record the steps and numbers, keep the playbook note, and say so in the report. Do not add a README note for something not seen.
3. **Record** each run in the report: venv, Python, Streamlit and package versions, how timed, and the numbers.

### (b) Repository tidy-up

4. **Move milestone history** with `git mv` into `docs/history/` (list in Decisions), including this handoff. Then:
   - Fix every link and path mention. `git grep -nE "handoff-m|m[1-4]-report|spike-report|notes-m1|findings\.md"` must show only `docs/history/` paths afterwards. Known places: `CLAUDE.md`, `docs/release-plan.md`, `docs/architecture.md`, `docs/security.md`, `examples/streaming_app.py`, and the moved files' links to each other and to `docs/adr/` (now one level up: `../adr/`).
   - Add a short `docs/history/README.md`: one line per file, in milestone order.
   - Bring stale status lines in line: `docs/architecture.md` ("during M2", "on `m2-release`") and `docs/release-plan.md` (M3 done; M4 in progress). The playbook's R2 row still says the second-message case is "unmeasured"; M3 measured it.
5. **Move the command list into `CONTRIBUTING.md`.** Fold `CLAUDE.md`'s "Commands" block into `CONTRIBUTING.md` (it already has "Build and test"), keeping every command and comment that a contributor needs: the wheel and sdist, the Node-free sdist rebuild, the installed-wheel test, the floor leg, the dry run and the install from PyPI. Then:
   - `CLAUDE.md` keeps a short "Commands" section that points to `CONTRIBUTING.md` and keeps only Claude Code's local notes (Node path, delete the repo-root setuptools `build/`, restart Streamlit after a rebuild).
   - The `README.md` "Development" section points to `CONTRIBUTING.md` for the commands, not to `CLAUDE.md`.
   - The CI note ("keep the workflow in step with these commands") moves with the commands.
   - Update the PyPI-install commands for a final release: once `0.1.0` exists, `streamlit-a2ui==0.1.0` (or a plain install); the rc commands become an example of installing a pre-release with an exact pin.

### (c) `0.1.0`

6. **Release commit,** after (a) and (b) are merged or included:
   - `README.md`:
     - Install: `pip install streamlit-a2ui`. Replace the pre-release paragraph with one true sentence: a plain install gets the latest final release; `--pre` (pip), `--prerelease=allow` (uv) or an exact pin gets a release candidate.
     - Status: pre-1.0 (`0.1.0`), API and supported versions may change before 1.0. Drop "release candidate" from the text and the badge.
     - Keep every link and the GIF absolute; check them as in M3.
   - `CHANGELOG.md`: a `[0.1.0] - <date>` section above `[0.1.0rc1]` with what changed since rc1 (docs, the README fix, anything from (a)), and a `[0.1.0]` link to `https://github.com/josechudev/streamlit-a2ui/tree/v0.1.0`. Keep the rc1 section as it is.
   - `pyproject.toml`: `version = "0.1.0"`. Leave the `Development Status :: 4 - Beta` classifier unless the owner says otherwise.
   - Run everything locally (`CONTRIBUTING.md`), including `twine check --strict`, the Node-free sdist comparison, the installed-wheel test and the e2e test.
   - Open the pull request when the owner asks; the owner merges it once the four checks are green.
7. **Dry run (owner).** `gh workflow run release.yml --ref master` on the merge commit. Check: build and check succeeded, `identical: N files`, twine `PASSED`, `package version: 0.1.0`, Publish to PyPI skipped. Record the run link and the commit.
8. **Tag and approve (owner only).** Annotated tag `v0.1.0` on the commit the dry run built (`git tag -a v0.1.0 -m v0.1.0 <sha>`), pushed with `git push origin v0.1.0`; approve the `pypi` deployment on the web page. If the run fails before anything reaches PyPI, `CONTRIBUTING.md` says how the owner re-tags.
9. **Verify the publication:** release run link; SHA-256 of each file on PyPI equals the run's `dist` artifact; PEP 740 attestations name this repository, `release.yml` and `pypi`; the PyPI JSON API shows the new README with no relative links and every absolute link returning 200. PyPI's HTML page shows the built-in browser a bot check: do not bypass it; the owner looks at the page.
10. **Install from PyPI in a fresh environment,** as in M3 step 11: a brand-new venv outside the checkout, `--no-cache`, `streamlit-a2ui==0.1.0`; check that it imports from `site-packages`, the version is `0.1.0` and `renderer_capabilities()` works. Also check that a plain `uv pip install streamlit-a2ui` and `pip install --dry-run --report - streamlit-a2ui` now pick `0.1.0`. Copy both examples from the tag (`git show v0.1.0:examples/…`) into an empty folder and click through playbook parts 3 and 4 in a browser, or mark them "needs owner verification". Note whether the first-load delay from (a) shows up.

### (d) GitHub release

11. **Draft the release notes** from the `[0.1.0]` CHANGELOG section, with what a newcomer needs on one page:
    - what it is, and `pip install streamlit-a2ui`;
    - A2UI 1.0 only, basic catalog only;
    - Streamlit >= 1.59, Python >= 3.10;
    - the pinned 0.x renderer packages (`@a2ui/react` and `@a2ui/web_core` 0.15.0) and the two overrides, with the upstream issue links;
    - known limitations (one message per rerun, errors stay in the browser) and the accepted `zod` advisory;
    - links to the PyPI page, the release run and `docs/security.md`.

    Put the draft in `docs/history/m4-drafts.md`.
12. **The owner creates the release,** for example `gh release create v0.1.0 --verify-tag --title "streamlit-a2ui 0.1.0" --notes-file <file>`, with no assets (decision 3). Claude Code runs it only if the owner explicitly asks in that session. Record the URL.

### (e) Listings

13. **Recheck each repository's contribution instructions on the day,** and record what they said. As of 2026-11-18:
    - **A2UI community page:** `a2ui-project/a2ui`, file `docs/site/src/content/docs/ecosystem/renderers.mdx` (published as "Community Projects", https://a2ui.org/ecosystem/renderers/). Steps: fork, sign the Google CLA, add a row to the "Community renderers" table (columns: Renderer, Platform / Framework, Versions, Status, Description), open a pull request against `main` with a description and verification details or demo links, then share on GitHub Discussions. Listing criteria: open-source licence, documented protocol versions, core layout/text/input/action components, install instructions and a minimal runnable example, active maintenance. The repository formats Markdown with Prettier (`./scripts/fix_format.sh --check`); the table is column-aligned, so the new row must be too.
    - **Streamlit component gallery:** `streamlit/gallery`, one JSON file `components/registry/components/<slug>.json` per component, schema `components/registry/schemas/component.schema.json` (`schemaVersion: 1`, no extra keys, `links.pypi` is the project name not a URL, `links.github` must be the bare repository URL and unique across the registry, HTTPS only, stable image URL, at least one category from the README's list). CI validates it; locally `uv run python components/registry/scripts/validate.py` from that repository's root. The gallery refreshes weekly after a merge.
14. **Draft both** in `docs/history/m4-drafts.md`:
    - the A2UI table row: `josechudev/streamlit-a2ui` (`streamlit-a2ui` on PyPI), platform "Streamlit (Python, Web)", versions `v1.0`, status Active, a one-line description that says it wraps the official React renderer;
    - the gallery JSON: title, `author.github` `josechudev`, `links.pypi` `streamlit-a2ui`, `install.pip` `pip install streamlit-a2ui`, the GIF's raw URL as `media.image` if the validator accepts a GIF (check), categories (likely `LLMs` and `Integrations`; check the current list);
    - each pull request's title and description.

    Validate the JSON against the schema locally (a scratch clone outside this repository) before the owner opens anything.
15. **Open them only when the owner asks.** The owner opens them from their own fork (or asks Claude Code to, in that session). Record the pull request URLs and their state at the time of the report.

### (f) Posts

16. **Draft the posts** in `docs/history/m4-drafts.md`, for the owner to publish:
    - **Streamlit forum** (https://discuss.streamlit.io): check the current category on the day ("Custom Components" or "Show the Community!"). What it does, install, the GIF, the quickstart snippet, the "Using it with a real agent" pattern, limitations, link to the repository.
    - **A2UI GitHub Discussions** (`a2ui-project/a2ui`, category "Show and tell"): a Streamlit renderer for A2UI 1.0 built on the official `@a2ui/react`; the GIF as the short demo; what was checked (real ADK agent with `a2ui-agent-sdk`); links to the three upstream issues as context, not complaints.

    Short, factual, no marketing claims; nothing about anyone's employer.
17. **The owner publishes them.** Record the URLs.

### (g) One-week watch

18. **For seven days after the posts,** check the repository's issues, the listing pull requests and the two threads (the owner forwards what needs an answer; Claude Code reads public pages only). For each report:
    - a bug in the package: reproduce, fix with a test, and release as `0.1.x` through steps 6–10 (CHANGELOG section, version bump, dry run, owner tag and approval, fresh install);
    - anything else (a feature, a catalog, the second-message limitation): answer with the backlog and record it in `docs/release-plan.md`, without building it.
19. **Report.** Write `docs/history/m4-report.md` once `0.1.0` is on PyPI and the drafts are done, then stop for the owner's review. Append the watch-week result (issues, fixes, `0.1.x` releases or "none") as its last section at the end of the week.

## Acceptance criteria

1. The first-load delay was tried at least twice in brand-new venvs from PyPI, with a Streamlit-only control. The report records the steps, versions and timings, and the cause or "not reproduced". If it is Streamlit's or the machine's first-run cost, the README says so in one sentence; if it is the package's, it is fixed with a test before `0.1.0`.
2. Milestone handoffs, reports, `findings.md` and `notes-m1.md` are in `docs/history/` with a short index. `git grep` finds no link or path to their old locations, and no file linked from the `0.1.0rc1` README moved. The command list is in `CONTRIBUTING.md`; `CLAUDE.md` and `README.md` point to it, and CI still runs the same commands.
3. `streamlit-a2ui 0.1.0` is on PyPI, published by `release.yml` from tag `v0.1.0` after a `workflow_dispatch` dry run on the same commit. The owner pushed the tag and approved the `pypi` environment. The files on PyPI match the run's artifact by SHA-256. Its README installs with `pip install streamlit-a2ui`, states the pre-1.0 status without calling it a release candidate, and renders on PyPI with working absolute links. `CHANGELOG.md` has a dated `[0.1.0]` section.
4. In a fresh environment outside the checkout, `0.1.0` installed from PyPI imports from `site-packages`, a plain install picks `0.1.0`, and both examples pass playbook parts 3 and 4 in a browser, or are marked "needs owner verification".
5. A GitHub release `v0.1.0` exists, with notes drafted from the CHANGELOG that state A2UI 1.0 only, the Streamlit floor, the pinned 0.x renderer packages and overrides, the known limitations and the accepted risk. The owner created it, or Claude Code did at the owner's explicit request in that session.
6. Listing pull requests to `a2ui-project/a2ui` (community renderers table) and `streamlit/gallery` (component registry) are drafted against each repository's instructions as rechecked on the day, the gallery JSON validates against its schema, and each was opened by the owner or at the owner's request. The report records the URLs and their state, or "not opened" with the reason.
7. The Streamlit forum post and the A2UI GitHub Discussions post are drafted, published by the owner, and their URLs recorded.
8. The watch week ran for seven days after the posts; every package bug reported in it was fixed with a test and released as `0.1.x` through `release.yml`, and everything else went to the backlog. The report lists them, or says there were none.
9. Claude Code created no tag, uploaded nothing, created no GitHub release, opened no pull request outside this repository and published no post, except where the owner explicitly asked in that session; the report names each such request.
10. All tests and linters pass locally and in CI. Nothing in the Architecture or Security sections of `CLAUDE.md` changed without an ADR and the owner's approval. The owner's decisions on the ADK example, the CLA and release assets are recorded.
11. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/security.md`, `docs/testing-playbook.md`, `docs/release-plan.md`, `docs/upstream-issues.md`, `docs/history/README.md`, `docs/history/m4-drafts.md` and `docs/history/m4-report.md` exist and agree with each other.

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
- The package's dependencies stay `streamlit >= 1.59` only.
- No secrets, tokens or API keys anywhere. No employer names, code or data, in the repository, the drafts, the listings or the posts.
- GitHub Actions rules from M2 hold: least-privilege permissions, `persist-credentials: false`, actions pinned to SHAs, dev tools pinned, timeouts on every job.
- Work in other repositories (listing drafts, schema validation) happens in scratch clones outside this repository and is never pushed without the owner's request.

## Out of scope: do not build, ask first

- Pushing tags, uploading to PyPI or TestPyPI, `twine upload`, `uv publish`, creating GitHub releases, opening pull requests in other repositories, posting on the forum or GitHub Discussions, or running `release.yml` other than a dry run the owner asks for — unless the owner explicitly asks for that action in the session.
- Signing the Google CLA or any other agreement for the owner.
- An ADK or other agent example in this repository (decided: none), or the separate example repository (after `0.1.0`); any agent adapter, streaming helper, message parser or typed Python message models.
- Backlog items: returning a list of messages (ADR-003, ADR-009), React 19, custom or geospatial catalogs, A2UI 0.9.x or 0.8, persisting form state across remounts.
- Upgrading `@a2ui/*`, `dompurify` or React, or dropping an override, even if upstream ships a fix during M4 (record it for after 0.1.0).
- Changing the repository's visibility, settings, rulesets or environments.
- A docs site, coverage badges, a multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish.

## Things that are easy to get wrong

- **Once `0.1.0` exists, plain installs stop picking release candidates.** pip needs `--pre`, uv `--prerelease=allow`, or an exact pin. Before `0.1.0` they pick the rc (M3 got this backwards).
- **The rc1 README is frozen and links `master`.** Moving or renaming any file it links breaks the rc1 page for good. The history move must leave those files alone, and `CLAUDE.md` must keep existing.
- **Moved files link each other relatively.** After `git mv` into `docs/history/`, links to `docs/adr/…` become `../adr/…`, and links from the moved files to `README.md` or `CLAUDE.md` gain a `../`. Check with `git grep` and by opening a few on GitHub after the push.
- **A test install can quietly use the local build** (a cached wheel, or the checkout on `sys.path`). Install with no cache, run from an empty folder, check `__file__` and the version.
- **First-load timing needs a really new venv.** Reusing one, or a warm uv cache, hides one-time costs. Create each venv fresh, with `--no-cache`, and run the control the same way.
- **Tag the commit CI and the dry run passed.** Dependabot pull requests may merge in between; tag by SHA, not by branch name.
- **`release.yml` checks that the tag equals the version:** `v0.1.0` for `0.1.0`. A mismatch fails before publishing.
- **The `release tag` ruleset blocks moving `v*` tags,** and `v0.1.0rc1` can never move. Re-tagging is only for a run that uploaded nothing, and only the owner can disable the ruleset.
- **`gh` cannot approve a deployment on GitHub Free.** The owner approves on the web page.
- **PyPI's HTML page shows the built-in browser a bot check.** Never bypass it; use the JSON API and leave the visual check to the owner.
- **The A2UI listing table is Prettier-aligned.** A row with the wrong column widths fails its formatting check; run `./scripts/fix_format.sh --check` (or Prettier on that file) in the scratch clone.
- **The gallery's `links.github` must be unique across the registry,** and `links.pypi` is a project name. Search the registry for an existing `streamlit-a2ui` entry first.
- **The listing page has moved before** (`docs/release-plan.md` sources). Recheck its path on the day.
- **The red "Dependabot Updates" runs for `zod`** end in `security_update_not_possible`. Expected: the accepted advisory in `docs/security.md`.
- **Carried over from M2 and M3:**
  - Never name a workflow variable `STREAMLIT_*`.
  - Node 24 is at `~/.nvm/versions/node/v24.15.0/bin`; the system Node is 23.
  - Delete the setuptools `build/` cache at the repository root before building a wheel locally.
  - After a rebuild, restart Streamlit and reload the page.
  - `.claude/` is local and never committed.

## Deliverable: `docs/history/m4-report.md`

- Each acceptance criterion: pass, fail or needs owner verification, with how it was checked. Include the CI, dry-run and release run links, the PyPI URL, the GitHub release URL, the listing pull request URLs and the post URLs.
- The owner's decisions: ADK example, CLA, release assets.
- The first-load delay: steps, environments, timings, cause or "not reproduced", and what changed.
- The tidy-up: what moved, and the link check.
- The publication: tag commit, file hashes, attestations, and anything that differed from `CONTRIBUTING.md`'s release process.
- The PyPI install check: environment, commands, results.
- The listings: each repository's instructions as found on the day, what was submitted, and the state.
- Every public action Claude Code took at the owner's request, with the request.
- Anything in this handoff or `CLAUDE.md` that turned out to be wrong.
- The watch week, appended at its end: issues, fixes, `0.1.x` releases, backlog additions.
- Suggested next steps after `0.1.0`, kept separate from what was done.
