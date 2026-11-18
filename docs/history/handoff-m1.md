# Handoff: M1 — harden the spike into v0.1

## Context

`streamlit-a2ui` renders Google's A2UI 1.0 protocol in Streamlit by wrapping the official web renderer (`@a2ui/react` + `@a2ui/web_core`) in a Streamlit Components v2 component. M0 (branch `m0-spike`, report in `docs/history/spike-report.md`) proved the architecture. The owner has reviewed it and made the decisions listed below.

M1 turns the spike into something a stranger could install from source and use. It is not a feature milestone. Everything in "Out of scope" stays out.

Read `CLAUDE.md` and `docs/history/spike-report.md` first. Where this file and `CLAUDE.md` disagree, this file wins, and step 1 is to bring `CLAUDE.md` in line.

## Decisions made since M0 (treat as settled)

- Streaming happens across reruns. A keyed component is called once per script run. The documented pattern is the component inside `@st.fragment(run_every=...)` reading a log that the agent's stream appends to. Never vary the key to repaint. No streaming helper is shipped; one example is.
- Dependency overrides are kept and pinned. Scoped npm `overrides`: (a) the `@a2ui/markdown-it` peer on `@a2ui/web_core` points at the root `web_core`; (b) `dompurify` is overridden to exactly `3.4.18`. The zod advisory (`<4.6.6`) has no fix in the 3.x line `web_core` requires: accept it and document it.
- The page-wide stylesheet from `web_core` is accepted. Do not patch it out.
- Renderer and processing errors stay in the browser. Show a plain-text notice inside the component. Do not send them to Python. The return type stays `dict | None`.
- The M0 corrections stand: processor version is `'1.0'`; the action handler's `ActionPayload` is wrapped as `{"version":"1.0","action":payload}`; outbound-listener messages are sent unchanged; `@` prefixes are on dynamic values (`@path`, `@call`, `@index`).

## Steps

Work on a new branch `m1-v0.1` created from `m0-spike`. Small commits, one concern each. Do not push, open a PR, or publish.

1. Update `CLAUDE.md`. Keep the Commands section you wrote. Change: current milestone to M1 with this file's acceptance criteria; the pins table (overrides, dompurify 3.4.18); the API notes (the corrections and decisions above); Node 24 via nvm; "package only from `npm run build`". Add ADR 007, 008, 009 to the accepted list. Remove `renderer_capabilities` being unimplemented once step 5 lands.
2. Record the decisions in the repo. Create `docs/adr/` with one short file per ADR (Context, Options, Decision, Consequences), using only the content in the "ADR content" section at the end of this file. Do not embellish.
3. Dependencies. Add the `dompurify` override. Confirm with `npm ls dompurify` that a single copy at 3.4.18 resolves, and that the built bundle contains that version. Run `npm audit` and record the remaining findings in `docs/security.md` (step 9).
4. Review and clean the spike frontend. It was written to answer questions. Read it as if reviewing someone else's PR and fix what you find: naming, dead code, effect cleanup on unmount, the log-shrink replay path, double registration of custom elements. Remove the processor-construction console log and restore the template's default for dropping `console` in production builds. Keep the frontend to a handful of files.
5. `renderer_capabilities()`. Returns the renderer's A2UI 1.0 capabilities as a dict, for the app author to pass to their agent. The content must come from `@a2ui/web_core`'s own capability generation, produced by a script at frontend build time and shipped as a JSON file inside the Python package. It must not be hand-written and must not be placed in the publicly served `asset_dir` unless there is no alternative. If `web_core` cannot generate capabilities outside a browser, stop and report the options; do not hand-write the JSON as a workaround.
6. Error notice. When the processor throws on a message or a surface reports an error, show a small notice inside the component: plain text set via text content, themed with existing variables, listing the error code and message. Keep the `console.warn`. Processing must continue with later messages where the processor allows it. A waiting state is shown until the first surface has a root.
7. Examples. Replace `examples/spike_app.py` with:
   - `examples/basic_app.py`: a form surface, the returned `action` displayed, and a scripted "agent" that answers by appending messages. No LLM, no network, no API keys.
   - `examples/streaming_app.py`: a scripted generator feeds the log over several seconds while the component, inside `@st.fragment(run_every=...)`, repaints. It must show an action fired from inside the fragment being received and handled. All sample payloads are A2UI 1.0, taken from the installed package's schemas.
8. Answer two open questions and write the answers into `docs/history/notes-m1.md`:
   - When a trigger fires from a component inside a fragment, does Streamlit rerun the fragment only or the whole script, and where is the returned message visible? State what the streaming example therefore has to do.
   - Does `web_core`'s page-wide `:root{color-scheme: light dark}` visibly change Streamlit's own widgets (inputs, selects, scrollbars) in light or dark theme? Compare a page with and without the component mounted.
9. Docs.
   - `README.md`: what it is and who it is for; status (pre-release, A2UI 1.0 only, Streamlit >= 1.51, developed on 1.67); install from source; a quickstart that matches `examples/basic_app.py`; the streaming pattern; the API (two functions); limitations; link to `docs/security.md`. Do not claim a PyPI release or show `pip install streamlit-a2ui`. Remove all template text.
   - `docs/security.md`: the model (basic catalog only, no HTML/CSS/JS parameters, sanitised markdown, assets in the wheel, no sandbox because Components v2 is frameless) and the known residual risks: renderer bugs run with app-page privileges; agent-chosen media URLs are fetched by the browser; a hostile agent can spoof UI; the zod advisory; the page-wide stylesheet; custom elements are global so two bundle versions on one page collide. State the dependency overrides and why.
   - `LICENSE` is Apache-2.0; add a `NOTICE` if the bundled dependencies' licenses require one. Check, don't assume.
10. Tests and guards.
    - pytest: `a2ui_surface([], key=...)` returns `None`; `renderer_capabilities()` returns a dict naming protocol version 1.0 and the basic catalog ID; the built wheel contains the frontend bundle and the capabilities JSON, and contains no `*.map` files, no `http(s)://` script or font URLs pointing at a CDN.
    - Frontend unit tests (the template's runner, or Vitest): the cursor processes only the unprocessed tail; a shorter log triggers dispose and replay; an `ActionPayload` is wrapped into the 1.0 wire shape; an outbound-listener message passes through unchanged.
    - A build check that fails if `asset_dir` contains source maps.
    - `ruff` clean; TypeScript strict with no errors and no `any` in our code.
11. Report. Write `docs/history/m1-report.md`, then stop and wait for review.

## Acceptance criteria

1. From a clean clone, the commands in `CLAUDE.md` build the frontend, install the package and run both examples without edits.
2. `examples/basic_app.py`: the surface renders, the action comes back once with its context, the scripted reply updates the surface in place, and typed-but-unsubmitted text survives the rerun.
3. `examples/streaming_app.py`: content appears progressively, and an action fired during or after streaming is received by Python.
4. A deliberately invalid message in the log produces the in-component notice, does not blank the surfaces already rendered, and returns nothing to Python.
5. `renderer_capabilities()` output is generated from `web_core`, not hand-written.
6. One `dompurify` at 3.4.18 in the lockfile and in the bundle.
7. The wheel has no source maps and no CDN references; the production bundle has no construction log.
8. All tests and linters pass. Criteria 2, 3 and 4 were exercised in a browser by you, not inferred from code. If you cannot drive a browser, write a click-through checklist for the owner instead and mark those criteria "needs owner verification".
9. `CLAUDE.md`, `README.md`, `docs/security.md`, `docs/adr/001`–`009`, `docs/history/notes-m1.md` and `docs/history/m1-report.md` exist and agree with each other.

## Constraints

- Streamlit Components v2 only; `isolate_styles=True`. No v1 API, no iframe.
- Official basic catalog only. No custom or inline catalogs.
- No parameter or prop accepts HTML, CSS or JS. No `dangerouslySetInnerHTML` in our code. Markdown only through `@a2ui/markdown-it`.
- No CDN or runtime fetching of code or fonts.
- One outbound trigger. Python does not parse or validate message contents.
- Public API is exactly `a2ui_surface(messages, *, key) -> dict | None` and `renderer_capabilities() -> dict`.
- Exact pins for every `@a2ui/*` package and for `dompurify`. Do not upgrade any `@a2ui/*` package in this milestone, even if a newer one is published; note it in the report instead.
- No employer names, code or data anywhere. No real API keys or LLM calls in examples.

## Out of scope: do not build, ask first

Geospatial or any custom catalog · agent adapters (ADK, LangChain, A2A, AG-UI) · A2UI 0.9.x/0.8 · sending errors to Python or changing the return type · a streaming helper function · typed Python message models · persisting form state across remounts · CI workflows · a docs site · publishing to PyPI or npm · pushing to a remote.

## Deliverable: `docs/history/m1-report.md`

- Each acceptance criterion: pass, fail, or needs owner verification, with how it was checked.
- What the code review in step 4 changed and why.
- Final dependency versions and the remaining `npm audit` output.
- Bundle size before and after.
- Anything in this handoff or `CLAUDE.md` that turned out to be wrong.
- Open problems and suggested next steps, clearly separated from what was done.

## ADR content (for step 2)

The text of each ADR is recorded in `docs/adr/0001`–`0009`.
