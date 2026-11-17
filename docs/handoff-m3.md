# Handoff: M3 — release candidate and real-agent check

Written 2026-11-17 at the owner's request, from the M3 section of `docs/release-plan.md` and the state after M2.

## Context

`streamlit-a2ui` renders Google's A2UI 1.0 protocol in Streamlit by wrapping the official web renderer (`@a2ui/react` + `@a2ui/web_core` 0.15.0) in a Streamlit Components v2 component.

- **M2 is merged** (PR #4). The package is releasable: version `0.1.0rc1`, defined once in the root `pyproject.toml`; Streamlit floor `>=1.59`; Python `>=3.10`. CI has two test legs plus a `package` job and a `wheel-smoke` job, all green on PR #4 and on `master` (`docs/m2-report.md`).
- **`release.yml` has never run.** A `v*` tag builds, checks and then publishes from a separate job in the `pypi` environment, with PyPI Trusted Publishing. `workflow_dispatch` is a dry run that stops before publishing.
- **The owner's one-time setup is done:**
  - PyPI pending publisher: project `streamlit-a2ui`, repository `josechudev/streamlit-a2ui`, workflow `release.yml`, environment `pypi`.
  - GitHub environment `pypi`: the owner is the required reviewer, admins cannot bypass, deployments only from tags matching `v*`.
  - Rulesets: `master` (no deletion or force-push, pull request required with 0 approvals, the four CI checks required, no bypass) and `release tag` on `refs/tags/v*` (no deletion, update or force-push, no bypass).
  - Private vulnerability reporting, secret scanning with push protection, Dependabot alerts and security updates, SHA pinning of actions required, read-only default workflow token, auto-delete of merged branches.
- **The repository is public.** It was made public in M3 rather than M4, because GitHub Free has no environment reviewers on private repositories. A full-history scan for secrets and employer data was clean before the switch.
- **`streamlit-a2ui` is not on PyPI yet** (the name was free on 2026-11-17). No tags or GitHub releases exist.
- **Every A2UI payload so far was hand-written.** No real agent has driven a surface.

M3 publishes the first release candidate and checks the package against a real agent. It does not publish `0.1.0` and does not add agent integrations to the package.

Read these first: `CLAUDE.md`, `docs/release-plan.md` (M3 section), `docs/m2-report.md`, `CONTRIBUTING.md` (release process), `docs/upstream-issues.md` and `docs/testing-playbook.md`. Where this file and `CLAUDE.md` disagree, this file wins, and `CLAUDE.md` is brought in line.

## Decisions (treat as settled)

- **Publishing happens only through `release.yml`,** on a `v*` tag that the owner pushes and then approves in the `pypi` environment. Claude Code never creates or pushes a tag, never uploads, never runs `twine upload` or `uv publish`, and never runs `release.yml` except when the owner asks for a `workflow_dispatch` dry run.
- **No API token, ever.** Trusted Publishing only, as in M2.
- **Release on the 0.x renderer packages** (`docs/release-plan.md`, decision 1). The `@a2ui/*` and `dompurify` pins stay. If a newer `@a2ui/*` release appears, note it in the report; do not upgrade.
- **The real-agent check lives outside this repository,** in a scratch folder on the owner's machine. The package gets bug fixes only: no adapter, no agent dependency, no helper that parses agent output.
- **The second renderer-to-agent message is observed, not fixed.** Fixing it changes the return type, which needs an ADR (it revisits ADR-003 and ADR-009).
- **Whether an ADK example ships in the repository** (`examples/adk_agent_app.py`, needing an API key) is the owner's decision after the check. Recommend one way in the report; do not add it without the owner's approval.
- **The README pass lands before the tag.** PyPI shows the README uploaded with each version and never changes it, so the `0.1.0rc1` page must already say how to install from PyPI, state the pre-1.0 status and show the GIF. The release plan lists the README pass after publishing; this ordering supersedes it.
- **A published version is final.** PyPI never accepts the same file name twice, even after a deletion. A problem found after the upload is fixed in `0.1.0rc2`; the owner decides whether to yank `rc1`.

### Still open: the owner decides before the tag

- **Author e-mail.** `authors` in `pyproject.toml` includes the owner's e-mail address. It becomes permanently public in the package metadata with `rc1`. Keep it, replace it, or drop the `email` field.

## Steps

Work on a branch cut from `master`, in small commits with one concern each. `master` is protected, so everything lands through a pull request with the four checks green. Push or open a pull request only when the owner asks; push with an explicit refspec (`git push origin <branch>`).

1. **Bring the docs in line with the post-M2 state.** `CLAUDE.md` (M3 milestone, narrowed publishing ban, repository facts) and `docs/m2-report.md` (the CI runs for PR #4; criteria 1, 2, 3 and 9 pass on GitHub, criterion 5 stays "not run") were updated together with this handoff. Still to do:
   - `docs/release-plan.md`: M2 done; the repository went public in M3; M4 no longer flips visibility.
   - `CONTRIBUTING.md`: the one-time setup is done; add the rulesets and how to re-tag after a failed run that uploaded nothing.
   - `docs/security.md`: status line (M3, repository public).
2. **Upstream issues.** The owner files them from `docs/upstream-issues.md`.
   - Before filing, if the owner asks: recheck each draft against the latest published `@a2ui/*` versions and the existing issues on `a2ui-project/a2ui`, and update the drafts.
   - Once the owner gives the URLs, record them in the table in `docs/upstream-issues.md`.
   - Link issues 1 and 2 from `docs/security.md` (the overrides table) and from ADR-008.
   - Link issue 3 from residual risk 5 in `docs/security.md`, and issue 4 from the README's Limitations.
   - `package.json` cannot carry comments, so the overrides are not annotated there.
3. **Real-agent check, outside the repository.**
   - Work in a scratch folder outside this repository and outside any worktree, for example `~/code/a2ui-adk-scratch`. It is not committed anywhere.
   - Use a fresh venv on Python 3.11 or newer (`google-adk` requires `>=3.11`).
   - Install `google-adk`, `a2ui-agent-sdk` and this package. Before `rc1` exists, install the wheel built from this branch. After the release, repeat step 11 against PyPI.
   - The model API key is the owner's. They put it in the environment or in a `.env` file in the scratch folder. Never print it, read it back, copy it into this repository, a note or the report, or pass it on a command line.
   - Build a minimal ADK agent with `a2ui-agent-sdk`:
     - configure it for A2UI 1.0 and the basic catalog;
     - give it `renderer_capabilities()` the way the SDK expects (in 1.0 the transport key is `a2uiRendererCapabilities`; check the shape the SDK validates against our version-keyed dict);
     - have it build one small form surface.
   - Build a Streamlit app in the scratch folder that:
     - appends the agent's messages to the log;
     - renders the log with `a2ui_surface`;
     - sends each returned renderer-to-agent message back to the agent.
     Extracting A2UI messages from the agent's output is the app's job, not the package's.
   - Drive it in a browser through:
     - one action round trip: submit the form, the agent receives the action with its context and answers with a surface update;
     - one streamed response: the agent's messages appear progressively through `@st.fragment(run_every=...)`, as in `examples/streaming_app.py`.
   - Record:
     - versions (Python, Streamlit, `google-adk`, `a2ui-agent-sdk`, the model);
     - every failure: messages the renderer rejected (with the notice text), actions that did not arrive, theme or layout problems;
     - for each, whether it is a package bug, an agent or SDK problem, or upstream spec drift between `a2ui-agent-sdk` and `web_core` 0.15.0.
   - Fix package bugs on the branch, each with a test. If a fix needs an Architecture or Security change, stop and ask.
   - Keep a few sanitised sample messages from the agent (no key, nothing personal) in the scratch folder. They can become hand-written test fixtures if a fix needs one.
4. **Second renderer-to-agent message.** With the real agent, and with `examples/basic_app.py` as a control:
   - Click Send twice quickly.
   - If the agent uses `callAgentFunction`, fire an action while a call is pending.
   - Record whether Python received both messages or only the last, how you could tell, and how often it happened.
   - Update the README Limitations entry with the measured result. Do not change the behaviour.
5. **README pass,** before the tag:
   - Install from PyPI: `pip install --pre streamlit-a2ui`, or `pip install streamlit-a2ui==0.1.0rc1`. Keep "Install from source" below it for contributors.
   - Status: a pre-1.0 release candidate; A2UI 1.0 only; the pinned 0.x renderer packages.
   - A GIF of `examples/basic_app.py`: fill the form, Send, see the reply. Store it under `docs/images/`, keep it small (aim under 2 MB), and check that it is in neither the wheel nor the sdist.
   - PyPI renders the README without the repository around it. Make every link and image absolute (`https://github.com/josechudev/streamlit-a2ui/blob/master/...` for pages, `https://raw.githubusercontent.com/josechudev/streamlit-a2ui/master/...` for the GIF). Check the result with `twine check --strict`.
6. **Prepare the release commit.**
   - The owner decides on the author e-mail.
   - `CHANGELOG.md`: date the `[0.1.0rc1]` section and add M3's fixes.
   - The version stays `0.1.0rc1`.
   - Open the pull request when the owner asks. The owner merges it once the four checks are green.
7. **Dry run (owner).** On the merge commit: `gh workflow run release.yml --ref master`. Check that it built, compared the wheels, passed `twine check` and skipped `Publish to PyPI`. Record the run link.
8. **Tag and approve (owner only).**
   - Confirm that `streamlit-a2ui` is still free on PyPI; a pending publisher does not reserve the name.
   - Create an annotated tag `v0.1.0rc1` on the commit the dry run built, and push it with `git push origin v0.1.0rc1`.
   - Approve the `pypi` deployment when the workflow asks.
   - If the run fails before the upload, the owner may temporarily disable the `release tag` ruleset, delete and re-create the tag on the fixed commit, and re-enable the ruleset. Once anything is on PyPI, never re-tag; go to `rc2`.
9. **Verify the publication.**
   - Record the release run link.
   - Check the PyPI project page: version, README, GIF, links, metadata.
   - Check that the SHA-256 of each file on PyPI equals the file in the run's `dist` artifact.
   - Check the provenance attestations shown on PyPI.
10. **No GitHub release.** The GitHub release is M4, for `0.1.0`. Do not create one for `rc1`.
11. **Install from PyPI in a fresh environment.**
    - Prefer a Linux container or another machine; otherwise use a fresh venv outside the checkout with no package cache (`uv pip install --no-cache`, or `pip --no-cache-dir`).
    - Install `streamlit-a2ui==0.1.0rc1`. Check that `pip install streamlit-a2ui` without `--pre` does not pick it.
    - Check that the package imports from `site-packages`, that its version is `0.1.0rc1`, and that `renderer_capabilities()` works.
    - Copy the two examples from the tag (`git show v0.1.0rc1:examples/basic_app.py`) into an empty folder; they are not in the wheel.
    - Run both from that folder and click through playbook parts 3 and 4 in a browser, or mark them "needs owner verification".
    - Repeat the real-agent round trip (step 3) against the PyPI install.
12. **Report.** Write `docs/m3-report.md`, then stop and wait for the owner's review.

## Acceptance criteria

1. The four upstream issues are filed by the owner, or the report says why one was not. Their URLs are in `docs/upstream-issues.md` and linked from `docs/security.md` and ADR-008 (issues 1 and 2), from `docs/security.md` (issue 3) and from the README (issue 4).
2. A minimal ADK agent built with `a2ui-agent-sdk`, outside this repository, received `renderer_capabilities()` and drove a surface rendered by `a2ui_surface` in a browser through one action round trip and one streamed response. The report lists the versions used and what broke. Each package bug found is fixed with a test. No adapter or agent dependency was added to the package.
3. The report records whether a second renderer-to-agent message replaced the first before a rerun, with the steps used. The behaviour is unchanged, and the README states the measured result.
4. The README says how to install from PyPI, states the pre-1.0 status, shows a GIF of the basic example, and renders correctly on PyPI with working absolute links. The GIF is in neither the wheel nor the sdist.
5. `streamlit-a2ui 0.1.0rc1` is on PyPI, published by `release.yml` from tag `v0.1.0rc1`. The owner pushed the tag and approved the `pypi` environment. The files on PyPI match the run's artifact by SHA-256. Claude Code created no tag, uploaded nothing and created no GitHub release.
6. In a fresh environment outside the checkout, `0.1.0rc1` installed from PyPI imports from `site-packages`, and both examples pass playbook parts 3 and 4 in a browser, or are marked "needs owner verification".
7. All tests and linters pass locally and in CI. Nothing in the Architecture or Security sections of `CLAUDE.md` changed without an ADR and the owner's approval.
8. `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/security.md`, `docs/testing-playbook.md`, `docs/release-plan.md`, `docs/upstream-issues.md` and `docs/m3-report.md` exist and agree with each other.

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
- No secrets, tokens or API keys anywhere: not in the repository, not in notes, not in the report, not in a command line that is logged. No employer names, code or data. The scratch agent runs on the owner's personal machine and account.
- GitHub Actions rules from M2 hold: least-privilege permissions, `persist-credentials: false`, actions pinned to SHAs, dev tools pinned, timeouts on every job.

## Out of scope: do not build, ask first

- Pushing tags, uploading to PyPI or TestPyPI, `twine upload`, `uv publish`, creating GitHub releases, or running `release.yml` other than a dry run the owner asks for.
- `0.1.0`, the GitHub release and the gallery listings and posts (M4).
- An agent adapter (ADK, LangChain, A2A, AG-UI), a streaming helper, a message parser, or typed Python message models in the package.
- An ADK example in the repository, unless the owner approves it after the check.
- Returning a list of messages, or any other change to ADR-003, ADR-009 or the return type.
- Upgrading `@a2ui/*`, `dompurify` or React.
- Geospatial or any custom catalog; A2UI 0.9.x or 0.8; persisting form state across remounts.
- Changing the repository's visibility, settings, rulesets or environments. These are the owner's.
- A docs site, coverage badges, a multi-OS matrix, pre-commit frameworks, release automation beyond tag-to-publish.

## Things that are easy to get wrong

- **Pre-releases are hidden by default.**
  - `pip install streamlit-a2ui` ignores `0.1.0rc1`; use `--pre` or `==0.1.0rc1`.
  - uv needs `--prerelease=allow` or the exact pin.
  - Until `0.1.0` exists, a plain install fails. That is expected; the README must say so.
- **A test install can quietly use the local build.** A cached wheel or the checkout on `sys.path` (`python -m streamlit` adds the working directory) can stand in for the PyPI package. Install with no cache, run from an empty folder, and check `__file__` and the version.
- **PyPI's README is frozen per version.** Relative links and images break on PyPI. Get the README right before the tag.
- **The wheel's URL test does not scan `METADATA`.** `tests/test_wheel.py` checks `.js`, `.css`, `.html` and `.json` files only, so README image links in the long description pass. Still, no README link may point at a script, stylesheet or font.
- **`google-adk` needs Python 3.11 or newer**, while the package supports 3.10. Use 3.11+ for the scratch venv.
- **`a2ui-agent-sdk` speaks several protocol versions** (0.8, 0.9 and 1.0; 0.12.0 on 2026-11-17). Select 1.0 explicitly; capabilities travel under `a2uiRendererCapabilities` in 1.0 and `a2uiClientCapabilities` in 0.8 and 0.9. Its 1.0 schemas may be newer than `web_core` 0.15.0's. A message our renderer rejects may be spec drift rather than a package bug; record it, do not upgrade the pins.
- **Trust installed code, not docs or memory.** Check the SDK's and ADK's installed sources for current APIs; these packages move fast.
- **Threads and Streamlit.** If the agent runs in a background thread, the thread may only append to a plain list held in `st.session_state`; it never calls `st.*`. The fragment drains the list on each tick (`examples/streaming_app.py`).
- **Fragment trigger scope.** An action fired inside `@st.fragment` reruns only the fragment, and the returned message is visible only there (`docs/notes-m1.md`).
- **`callAgentFunction` times out after 30 seconds** in `web_core`. A slow model can exceed it; record it if it happens.
- **Re-tagging.** The `release tag` ruleset blocks updating or deleting `v*` tags. Only the owner can disable it, and only before anything reaches PyPI.
- **The dry run never reaches the `pypi` environment.** The environment accepts only `v*` tags, and the publish job runs only on a tag push.
- **Tag the commit CI and the dry run passed.** Dependabot pull requests may merge in between.
- **A pending publisher does not reserve the name.** If someone registers `streamlit-a2ui` first, the pending publisher stops working.
- **The red "Dependabot Updates" runs for `zod`** end in `security_update_not_possible`. This is expected: it is the accepted advisory in `docs/security.md`.
- **Carried over from M2:**
  - Never name a workflow variable `STREAMLIT_*`.
  - Node 24 is at `~/.nvm/versions/node/v24.15.0/bin`; the system Node is 23, and `nvm.sh` is missing.
  - Delete the setuptools `build/` cache at the repository root before building a wheel locally.
  - After a rebuild, restart Streamlit and reload the page.
  - `.claude/` is local and never committed.

## Deliverable: `docs/m3-report.md`

- Each acceptance criterion: pass, fail or needs owner verification, with how it was checked. Include the CI, dry-run and release run links, and the PyPI URL.
- The upstream issue URLs.
- The real-agent check:
  - versions;
  - what worked;
  - what broke, and whose bug each problem was;
  - the fixes made;
  - a recommendation on shipping an ADK example.
- The second-message observation: steps, result and frequency.
- The publication: tag commit, file hashes, attestations, and anything that differed from `CONTRIBUTING.md`'s release process.
- The PyPI install check: environment, commands, results.
- Anything in this handoff or `CLAUDE.md` that turned out to be wrong.
- Open problems and suggested next steps for M4, kept separate from what was done.
