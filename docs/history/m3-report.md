# M3 report: release candidate and real-agent check

Dates: 2026-11-17 to 2026-11-18. The handoff is in `docs/history/handoff-m3.md`. M3 landed through PRs #10–#14 and the PR that adds this report, all on `master`.

**Result:** `streamlit-a2ui 0.1.0rc1` is on PyPI, published by `release.yml` from tag `v0.1.0rc1`, which the owner pushed and approved. A real Google ADK agent drove a surface. Installed from PyPI in a fresh environment, the package passes both example click-throughs. No package bugs turned up from the agent. One gap was fixed: unknown component types and functions are now rejected. Claude Code created no tag, uploaded nothing and created no GitHub release.

## Acceptance criteria

| # | Criterion | Result | How it was checked |
|---|---|---|---|
| 1 | Upstream reports as rechecked; URLs recorded and linked | **Pass** | The owner filed [a2ui-project/a2ui#4278](https://github.com/a2ui-project/a2ui/issues/4278) (DOMPurify pin) and [#4279](https://github.com/a2ui-project/a2ui/issues/4279) (page-wide stylesheet), and [commented](https://github.com/a2ui-project/a2ui/issues/4059#issuecomment-6963622021) on the existing [#4059](https://github.com/a2ui-project/a2ui/issues/4059) (peer range; fix open upstream as pull request #4073). Draft 4 was not filed: the package now passes a `validationConfig` that rejects unknown component types and functions (PR #12). URLs are in `docs/upstream-issues.md`, the `docs/security.md` overrides table and residual risk 5, ADR-008 and `CHANGELOG.md`. Both posted issue bodies were compared with the drafts: identical. |
| 2 | Minimal ADK agent with `a2ui-agent-sdk`, outside the repository, fed `renderer_capabilities()`, drove one action round trip and one streamed response in a browser; bugs fixed with tests; no adapter | **Pass** | See "Real-agent check". The package was unchanged by the agent work itself. The validation change (PR #12) came from the upstream recheck, and has 5 new tests. |
| 3 | Second renderer-to-agent message recorded; behaviour unchanged; README states the result | **Pass** | A double and a triple click each returned one action; see "Second message". The README Limitations and the CHANGELOG's Known limitations state it. |
| 4 | README: install from PyPI, pre-1.0 status, GIF, renders on PyPI with working absolute links; GIF in neither wheel nor sdist | **Pass, with one wording error found later; page look needs owner verification** | PR #13. `twine check --strict` passed on both artifacts. Through PyPI's JSON API, the published description has no relative links, and all 15 absolute links return 200, the GIF included. The GIF is absent from both artifacts. PyPI shows the built-in browser a bot-check page, so the rendered page itself needs the owner's look. Its sentence "a plain `pip install` finds nothing" is wrong (see "PyPI install"); fixed on `master` in this PR, but it stays in `0.1.0rc1`'s page. |
| 5 | `0.1.0rc1` on PyPI from `release.yml` and tag `v0.1.0rc1`; owner pushed and approved; files match the run's artifact; no tag, upload or release by Claude Code | **Pass** | See "Publication". Byte-identical files; provenance attestations name this repository, `release.yml` and `pypi`. |
| 6 | Fresh environment outside the checkout: PyPI install imports from `site-packages`; both examples pass playbook parts 3 and 4 in a browser | **Pass** (fresh venv; no container was available) | See "PyPI install". B1–B9 and S1–S5 pass. |
| 7 | All tests and linters pass locally and in CI; no Architecture or Security change without an ADR | **Pass** | PRs #10–#14: all four required checks green before each merge. CI on `master` at `388f2a7`: [run 44248061340](https://github.com/josechudev/streamlit-a2ui/actions/runs/44248061340). Locally for PR #12: Vitest 17, typecheck, Prettier, build, pytest 23, ruff, e2e. `CLAUDE.md`'s Architecture and Security sections did not change. |
| 8 | Listed documents exist and agree | **Pass** | This PR brings `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/security.md`, `docs/testing-playbook.md` and `docs/release-plan.md` in line with the release and with the findings below. `CHANGELOG.md`, `docs/architecture.md` and `docs/upstream-issues.md` needed no change. |

## Real-agent check

Built in `~/code/a2ui-adk-scratch`, outside the repository and never committed. The model API key stayed in a `.env` there (mode 600), and was never printed or copied.

**Versions:** Python 3.12.7, Streamlit 1.67.0, google-adk 2.14.1, a2ui-agent-sdk 0.12.0 (a2ui-core 0.7.0) and google-genai 2.34.0, against the Gemini API with model `gemini-flash-lite-latest`. The package was tested twice: as a wheel built from the branch, and as `0.1.0rc1` from PyPI. The browser was the Chromium-based pane of the Claude desktop app, on macOS. No other model could be used at the time of the check:
- `gemini-flash-latest` and `gemini-3.5`–`3.8-flash`: 503 or 504 errors;
- `gemini-pro-latest`: 429 (quota);
- `gemini-2.5-flash`: 404 (not available to new users).

**Shape of the agent:**
- **Agent.** An ADK `LlmAgent`, instructed with a short task plus `A2uiRequestProcessor.prompt_snippet` (the SDK's default Express format).
  - The instruction is a callable, because ADK templates `{…}` in string instructions and the SDK prompt contains JSON braces.
  - SSE streaming; each text chunk is fed to `processor.open_stream(state=…, after_rejected_block="continue")`.
  - One renderer state for the whole conversation.
  - The agent runs on its own event-loop thread and only appends message dicts to a list held in `st.session_state`.
- **App.** Draws the log with `a2ui_surface` inside `@st.fragment(run_every=0.5)`, and sends each returned message back to the agent as text.

**Results:**

1. **Capabilities: accepted unchanged.** `read_renderer_capabilities({"a2uiRendererCapabilities": renderer_capabilities()})` returns the dict as is. `A2uiGenerator.create_processor` resolves the basic 1.0 catalog from it.
2. **Rendering: no renderer notice from anything the agent sent.** The agent's messages included:
   - `createSurface` with inline `components` and `dataModel`;
   - `updateComponents`;
   - `TextField` bound with `@path`, `Card`, `Column`;
   - a `Button` with an event action whose context uses `@path`.

   Replaying the recorded messages through the new `validationConfig` gives no errors either.
3. **Action round trip: pass.** Name and message filled in, then Send:
   - Python received one `send_feedback` action with `{"name": "Ada", "message": "The real agent works"}`.
   - The agent's reply updated the same surface in place ("Thank you, Ada!").
   - The typed values stayed in the fields.
4. **Streamed response: pass, minimally.** In a fresh session the log went from 0 to 4 messages while the agent was busy, then to 5 when it finished; the page was sampled every 100 ms. Two things kept most turns from streaming visibly:
   - this model finishes a turn in 0.7–4.8 s, so most turns land within one or two fragment ticks;
   - it often sends a whole surface as a single `createSurface`, which cannot appear piece by piece.

   Without a browser, one turn delivered 5 messages over 7 SSE chunks.
5. **Agent-side errors, caught by the SDK.** The model re-sent `createSurface` for a surface that already existed. The SDK rejected the block ("Surface feedback already exists.") before it reached the log. Against the PyPI install this happened on every reply, even when the model was asked for an update only, so the reply was not shown in that run; the action itself reached Python with the right context, twice. Asked for one `updateComponents` per step, the model sent only the first message. None of this involves the package.
6. **Package bugs found: none.**

**Recommendation on shipping `examples/adk_agent_app.py`:** not in `0.1.0`. It needs an API key, and model availability changed by the hour during the check. The agent glue is the app's code, not the package's. The README's "Using it with a real agent" section describes the pattern. **Owner decision.**

## Second message

Same session, form rendered, the action handled inside a fragment with `run_every=0.5`:

| Clicks on the agent's Send button | Python received |
|---|---|
| 1 click, wait 8 s | +1 |
| double click | +1 |
| 1 click, wait 8 s | +1 |
| triple click | +1 |

The basic catalog's components in `@a2ui/web_core` 0.15.0 do not debounce, so every click dispatches an action. In both bursts, all but one message were lost: a second message produced before the rerun replaces the first. Which one survives was not determined. `callAgentFunction` was not exercised, because the agent defined no agent functions. The behaviour is unchanged. Changing it means returning a list, which revisits ADR-003 and ADR-009 (backlog item 2 in `docs/release-plan.md`).

## Unknown component types (upstream draft 4)

The upstream recheck showed that draft 4 was ours. `@a2ui/web_core` 0.15.0 rejects unknown component types and functions when the processor gets a `validationConfig`, and `session.ts` passed none.

PR #12 passes `{ ...RELAXED_VALIDATION, allowUnknownElements: false }`:
- **Relaxed**, so surfaces can stream in out of order.
- **Not `STRICT_VALIDATION`**, which rejects a surface whose root has not arrived yet.
- **Side effect:** passing a config also turns on `web_core`'s recursion-depth and path checks. Nothing tested tripped them.

Tests, Vitest 12 → 17:
- an unknown component type (this test fails without the fix);
- an unknown function call;
- an out-of-order streamed surface, checked after every message;
- two `web_core` 1.0 sample payloads.

## Publication

1. **Release commit:** PR #14 dated the CHANGELOG `[0.1.0rc1] - 2026-11-18`. Merge commit `388f2a7b7191cf12d3857705bd1c594bf18daff4`, CI [run 44248061340](https://github.com/josechudev/streamlit-a2ui/actions/runs/44248061340) green.
2. **Dry run (owner):** [run 44248281037](https://github.com/josechudev/streamlit-a2ui/actions/runs/44248281037), `workflow_dispatch` on `388f2a7`.
   - Build and check: success. Publish to PyPI: skipped.
   - The wheel rebuilt from the sdist matched: `identical: 12 files, same names and SHA-256 digests`.
   - twine `PASSED` on both.
   - The log printed `package version: 0.1.0rc1` and `dry run: not checking the tag (master)`.
3. **Tag (owner):** annotated `v0.1.0rc1` on `388f2a7`, pushed with `git push origin v0.1.0rc1`. Just before, PyPI returned 404 for the name and no tags existed.
4. **Release run:** [run 44248941528](https://github.com/josechudev/streamlit-a2ui/actions/runs/44248941528), event `push`, ref `v0.1.0rc1`. Build and check succeeded, which includes the tag check; Publish to PyPI succeeded after the owner approved `pypi`.
5. **PyPI:** https://pypi.org/project/streamlit-a2ui/0.1.0rc1/. Each file is byte-identical (`cmp`) to the release run's `dist` artifact:

   | File | SHA-256 | Bytes |
   |---|---|---|
   | `streamlit_a2ui-0.1.0rc1-py3-none-any.whl` | `e376a871eec012c22462c08966ad4a038170aa3d734f92e4ad63c9911a91738b` | 280,974 |
   | `streamlit_a2ui-0.1.0rc1.tar.gz` | `4c4f5c3d06513670b648e16f5a9bcf240c8f2c7f0cde989e7f4d08144ec0f995` | 270,370 |

6. **Attestations:** PyPI has PEP 740 publish attestations (`https://docs.pypi.org/attestations/publish/v1`) for both files. Each names publisher GitHub `josechudev/streamlit-a2ui`, workflow `release.yml`, environment `pypi`, and a subject digest equal to the SHA-256 above.
7. **Metadata:**
   - license Apache-2.0, `requires-python >=3.10`, depends on `streamlit>=1.59`;
   - Markdown README;
   - author `jose chu <jose.chu.dev@gmail.com>`, kept by the owner's decision;
   - the four project URLs.

**What differed from `CONTRIBUTING.md`:** nothing in the release steps. `gh` cannot approve the deployment on GitHub Free, so the approval is done on the web page.

## PyPI install

**Environment:** macOS, no Docker available. A new uv venv on Python 3.13, created outside the checkout in the session's scratch directory.

1. **Install:** `uv pip install --no-cache streamlit-a2ui==0.1.0rc1` installed streamlit-a2ui 0.1.0rc1 and Streamlit 1.67.0. It came from the index: there is no `direct_url.json`.
2. **Import:** `streamlit_a2ui.__file__` is in the venv's `site-packages`. The installed package directory is identical (`diff -r`) to the PyPI wheel's contents. `renderer_capabilities()` returns the basic 1.0 catalog.
3. **Plain install picks the rc.** While no final release exists, both installers pick `0.1.0rc1` without a pre-release flag:
   - pip 26.3: `pip install streamlit-a2ui` (dry-run report → `0.1.0rc1`);
   - uv 0.11.14: `uv pip install streamlit-a2ui`.

   This is standard pre-release handling: a pre-release is accepted when nothing else satisfies the requirement. The README, `CLAUDE.md`, `CONTRIBUTING.md` and the handoff said the opposite; all but the handoff are corrected in this PR.
4. **Examples:** taken from the tag (`git show v0.1.0rc1:examples/…`) into an empty folder, and run with that venv in the browser pane.
   - **Basic, playbook part 3:** B1–B9 pass.
     - B1: the very first page load in the brand-new venv stayed on the title for over 45 s, with nothing in the server log or the console; a reload rendered it at once. Cause not investigated; the playbook now mentions it.
     - B4: the title read "Contact us (3)". The counter counts every `updateComponents` in the log, B2–B3's replies included, so the playbook's "(1)" was wrong; corrected.
     - B5: plain-text notice and exactly one `console.warn`.
     - B8: checked by emulating light and dark.
   - **Streaming, playbook part 4:** S1–S5 pass.
     - S1: the log grew from 4 to 22 in steps about 0.5 s apart.
     - S2, on the restarted stream: "Acknowledged after 0 log lines", clicked before the first line arrived, and streaming carried on.
     - S4: "after 8 log lines", `actions received: 2`.
5. **Real agent on the PyPI package:** see "Real-agent check", item 5.

## Wrong in the handoff, `CLAUDE.md` or the release plan

1. **Pre-releases are not hidden while no final release exists.** pip and uv both install `0.1.0rc1` without a flag. Wrong in the handoff ("Things easy to get wrong", step 11), the README published with `0.1.0rc1`, `CLAUDE.md`'s commands and `CONTRIBUTING.md`. All but the handoff and the published README are corrected.
2. **Upstream draft 4 was a configuration gap in this package,** not an upstream bug (PR #12). Draft 1 already existed upstream as #4059.
3. **Playbook B4** expected "Contact us (1)"; the counter includes earlier replies.
4. **"Install on another machine or container"** (release plan): no container runtime was available. A fresh venv with no cache, outside the checkout, was used instead, and its installed files were compared with the PyPI wheel.
5. **The PyPI project page could not be checked in a browser.** PyPI shows the built-in browser a bot-check page, which is not to be bypassed. Its content was checked through the JSON API instead.

## Open problems and suggested next steps for M4

These are proposals, not work done.

1. **Owner checks:**
   - look at the PyPI page;
   - decide on the ADK example (recommendation: no);
   - review this report.
2. **`0.1.0`:**
   - date a `0.1.0` CHANGELOG entry;
   - set the version;
   - tag the commit after a dry run, then write the GitHub release from the CHANGELOG.

   The `0.1.0` README fixes the rc1 page's pre-release sentence.
3. **First-load delay in a brand-new venv.** Try to reproduce it before announcing. If it is Streamlit's first import, mention it in the README; if not, investigate.
4. **The second-message limitation** is the most likely user complaint. Backlog item 2 (return a list) needs an ADR.
5. **Listings and posts** as in `docs/release-plan.md`. Point at the README GIF and the "Using it with a real agent" section.
6. **Repository tidy-up before announcing:** move the milestone handoffs and reports into `docs/history/`, and move the command list from `CLAUDE.md` into `CONTRIBUTING.md`.
7. **Upstream:** watch #4059 (fix in pull request #4073, which does not change the DOMPurify pin), #4278 and #4279. Drop each override when upstream releases a fix.

## Pull requests

| PR | Merge | What |
|---|---|---|
| [#10](https://github.com/josechudev/streamlit-a2ui/pull/10) | `9fa15b7` | M3 handoff, `CLAUDE.md` for M3, M2 CI links |
| [#11](https://github.com/josechudev/streamlit-a2ui/pull/11) | `d6b0589` | Post-M2 docs, upstream recheck and issue links |
| [#12](https://github.com/josechudev/streamlit-a2ui/pull/12) | `f065900` | Reject unknown component types and functions; tests; subagent section in `CLAUDE.md` |
| [#13](https://github.com/josechudev/streamlit-a2ui/pull/13) | `2157106` | README pass and GIF |
| [#14](https://github.com/josechudev/streamlit-a2ui/pull/14) | `388f2a7` | CHANGELOG dated, the tagged commit |
| this PR | | Doc corrections from the PyPI install check, and this report |
