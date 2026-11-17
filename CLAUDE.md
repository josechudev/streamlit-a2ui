# streamlit-a2ui

Open-source Python package that renders Google's A2UI protocol inside Streamlit apps by wrapping the official web renderer in a Streamlit Components v2 component.

Personal open-source project. Never add employer code, names, hostnames or data. License: Apache-2.0.

## Current milestone: M0 — spike

Prove the architecture before building anything else. Do not add features, docs sites, CI matrices or abstractions during M0.

M0 passes when all five hold, each shown in `examples/spike_app.py`:

1. A packaged v2 component mounts `@a2ui/react` in the default shadow root and renders a hard-coded A2UI **1.0** surface from the basic catalog (Column, Text, TextField, Button).
2. Clicking the button delivers a 1.0 `action` message, with its resolved context, to Python as the return value of `a2ui_surface`.
3. Appending messages to the log and rerunning updates the surface in place: a half-typed TextField keeps its content and the `MessageProcessor` is not recreated (log its construction to prove it).
4. Streaming: re-calling the keyed component inside one script run, with a sleep between appended messages, repaints progressively. If it does not, say so, then try `st.fragment(run_every=...)` and report which works.
5. Toggling Streamlit light/dark changes the surface's colors.

When M0 is done, write `docs/spike-report.md`: each criterion pass/fail, exact versions used, anything that contradicted this file. Then stop and wait for review. If a criterion fails, do not work around it with a different architecture; report it.

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

Target public API for v0.1, nothing more:

```python
from streamlit_a2ui import a2ui_surface, renderer_capabilities

log = st.session_state.setdefault("a2ui_log", [])
event = a2ui_surface(log, key="main")
if event:
    log.extend(my_agent.send(event))
    st.rerun()
```

## Pinned facts (verified 2026-11-16; re-verify before changing)

| Thing | Value |
|---|---|
| A2UI spec | 1.0 only. 0.9.x is untested and unsupported |
| `@a2ui/react`, `@a2ui/web_core` | `0.15.0`, exact pins, no `^` |
| `@a2ui/markdown-it` | `0.2.2`, exact |
| Streamlit | develop on 1.67.x; declare `streamlit>=1.51` until M0 shows a higher floor is needed |
| React | 18 or 19 (peer range of `@a2ui/react`); use what the template ships |
| Basic catalog ID | `https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json` |

API notes that are easy to get wrong:

- Import `A2uiSurface` from the **root** of `@a2ui/react`. There is no `@a2ui/react/v1_0`. Do not import from `/v0_9` or `/v0_8`.
- Import `MessageProcessor` from `@a2ui/web_core` and the catalog from `@a2ui/web_core/catalogs/basic/v1`.
- `MessageProcessor`'s `version` option defaults to `'v0.9'`. Pass `'v1.0'`.
- Since 0.15.0 a surface renders nothing until its root component arrives. Render our own minimal waiting state.
- Basic catalog components are custom elements registered globally on the page. Guard against double registration; never load two versions of the bundle.
- The published README still shows v0.9 examples. Trust `node_modules/@a2ui/*/` type definitions and CHANGELOG over blog posts or memory; these packages had breaking changes in 0.13, 0.14 and 0.15.
- 1.0 wire format differs from 0.9 (`@`-prefixed envelope keys, renderer/agent naming). Take sample payloads from the 1.0 spec, not from older tutorials.

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

Use package name `streamlit-a2ui`, module `streamlit_a2ui`, component `a2ui_surface`. Read the generated README for the dev/build commands and record them in the Commands section below once confirmed; do not guess them.

Expected shape after generation (adjust to what the template actually produces):

```
streamlit_a2ui/            Python package: __init__.py with a2ui_surface(), renderer_capabilities()
streamlit_a2ui/frontend/   Vite + React + TS; build output is the asset_dir
examples/spike_app.py      M0 demo
tests/                     pytest
docs/adr/                  NNNN-title.md
docs/spike-report.md       written at the end of M0
```

## Commands

Prerequisites: uv, Node 24, npm.

_To be filled in from the generated template during M0 (frontend dev/build, editable install, run example, tests)._

## Conventions

- Python: 3.10+, full type hints, `ruff` for lint and format, `pytest`. Public API is exactly what `__init__.py` exports.
- TypeScript: strict mode, no `any` in our code, function components only. Keep the frontend to a handful of files; it is glue, not an app.
- Tests in M0: one pytest that the component registers and `a2ui_surface` returns `None` with no interaction. Real coverage comes after the spike.
- Commits: small, imperative subject, one concern each.
- Decisions: any change to the Architecture or Security sections needs `docs/adr/NNNN-title.md` with Context, Options, Decision, Consequences, and the owner's approval first. Accepted so far: 001 wrap official renderer · 002 Components v2 frameless · 003 message-pipe API · 004 log as source of truth · 005 A2UI 1.0 only · 006 basic catalog only.

## Out of scope — refuse or ask first

Geospatial or any custom catalog · agent adapters (ADK, LangChain, A2A, AG-UI) · A2UI 0.9.x/0.8 · persisting in-surface form state across remounts · typed message models in Python · multiple outbound triggers · a v1/iframe fallback · publishing to PyPI.

If a task seems to need one of these, stop and say so instead of building it.
