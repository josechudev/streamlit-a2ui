# streamlit-a2ui — Architecture v0.2

Status: 2026-11-16. M0 spike complete: criteria 1, 2, 3, 5 pass; 4 fails as designed and passes with the fragment fallback (ADR-007). ADR-001 to 004 are confirmed. ADR-008 and ADR-009 accepted by owner 2026-11-17. Next: M1, harden the spike into v0.1 (`handoff-m1.md`).
Evidence for every factual claim is in `findings.md`. Working instructions for Claude Code are in `CLAUDE.md`.

## 1. Corrections to the project brief

| Brief said | Now |
|---|---|
| Custom component (iframe) | Streamlit Components v2, frameless, in a shadow root (ADR-002) |
| Returns the user's action | Returns one renderer→agent message; 1.0 has four kinds (ADR-003) |
| Target v1.0; decide on v0.9.1 | 1.0 only (ADR-005) |
| `@a2ui/react` renderer | Still correct, but the basic catalog widgets are shared custom elements from `@a2ui/web_core`; React is a thin layer |

## 2. Scope of v0.1

In: `a2ui_surface(messages, key=...)` rendering A2UI 1.0 with the official basic catalog; incremental rendering; Streamlit theme carried into the surface; a `renderer_capabilities()` helper.

Out, each a later decision: geospatial or any custom catalog · agent adapters · 0.9.x/0.8 · persisting in-surface form state across a remount · inline catalogs · typed Python message models.

## 3. Components

```
 Streamlit script (Python)                     Browser (app page, shadow root)
┌──────────────────────────────┐              ┌────────────────────────────────┐
│ agent (ADK/LangChain/…)      │              │ CCv2 frontend bundle           │
│   │ A2UI messages            │              │  ┌──────────────────────────┐  │
│   ▼                          │   data=      │  │ MessageProcessor         │  │
│ message log (session_state)  │ ───────────► │  │ (@a2ui/web_core, v1.0)   │  │
│   │                          │  full log    │  │   cursor = n processed   │  │
│   ▼                          │              │  └──────────┬───────────────┘  │
│ a2ui_surface(log, key)       │              │             ▼                  │
│   ▲                          │  trigger     │  <A2uiSurface> (@a2ui/react)   │
│   │ renderer→agent message   │ ◄─────────── │  basic catalog custom elements │
└──────────────────────────────┘  (rerun)     └────────────────────────────────┘
```

| Part | Responsibility | Not its job |
|---|---|---|
| `streamlit_a2ui` (Python) | Register and mount the component; expose capabilities | Talking to agents; interpreting messages |
| Frontend bundle (TS/Vite) | One `MessageProcessor` per instance; feed it unprocessed messages; render; forward outbound messages on one trigger; map theme variables | Business logic; HTML passthrough |
| App author's script | Agent calls and the message log | — |

## 4. Data flow

**Agent → UI.** The log in `st.session_state` is append-only and is the source of truth. Every call passes the full log as `data`; the frontend processes `log[cursor:]`. A new instance replays from 0, so rendered UI is a pure function of the log. A keyed component can be called only once per script run (a second call raises `StreamlitDuplicateElementKey`), so streaming happens across reruns: the component sits inside `@st.fragment(run_every=...)`, or the script calls `st.rerun()` per chunk, while the log fills from the agent's stream. The spike showed the fragment repainting every 500 ms with the same processor instance (ADR-007). If the app replaces the log with a shorter one, the frontend disposes the processor and replays from 0.

**UI → agent.** One trigger, `renderer_message`. Triggers reset after the rerun, giving once-only delivery. It carries `action` and whatever the processor's outbound listener emits (`callAgentFunction`, `rendererFunctionResponse`). `web_core` hands the action handler a bare `ActionPayload`, so the frontend wraps it as `{"version":"1.0","action":payload}` per `renderer_to_agent.json`; listener messages pass through unchanged. Processing errors are not sent to Python in v0.1 (ADR-009). The author forwards it to the agent and appends the reply to the log. Each round trip costs one Streamlit rerun. `callAgentFunction` has a 30 s default timeout in `web_core`, so the reply must be appended within that window.

**Capabilities.** `web_core` can generate renderer capabilities. The frontend build emits them as JSON; `renderer_capabilities()` returns that. Not hand-written.

## 5. Theming

1.0 removed `theme` from the wire. The basic catalog reads `--a2ui-*` CSS variables; Streamlit exposes `--st-*`. One CSS file maps one onto the other on the component host. Custom properties inherit through shadow roots. The mapping table is spike work.

## 6. Security

Kept by construction, not by a sandbox:
- Basic catalog only; capabilities advertise that catalog and no inline catalogs.
- No parameter accepts HTML, JS or CSS.
- Markdown, the one HTML sink, goes through `@a2ui/markdown-it` (DOMPurify) and is not swappable.
- Assets ship in the wheel; no CDN.

Accepted residual risks, to be documented in the README: frameless means a renderer bug runs with app-page privileges; agent-chosen media URLs are fetched by the user's browser; UI spoofing by a hostile agent is not something a renderer can prevent. Custom elements register globally, so two versions of the bundle on one page would collide. `web_core`'s `injectBasicCatalogStyles()` adopts a stylesheet onto the host document, setting `:root{color-scheme: light dark}` and `--a2ui-*` defaults page-wide; `isolate_styles` does not contain it and we cannot opt out. zod 3 has an open high-severity memory-exhaustion advisory with no 3.x fix, so a hostile agent could exhaust the browser tab.

## 7. M0 spike — criteria and results

Results (browser-verified by Claude Code, branch `m0-spike`, Streamlit 1.67.0, React 18.3.1, `@a2ui/*` 0.15.0): 1 pass · 2 pass · 3 pass, one processor per key for the whole session · 4 fail within a run, pass with `st.fragment(run_every=0.5)` · 5 pass, CSS only. Bundle 951 kB JS (261 kB gzip). None of the reopen conditions occurred.

Criteria as set:

1. Packaged v2 component renders a hard-coded 1.0 surface (Column, Text, TextField, Button) in the default shadow root.
2. Button click delivers a 1.0 `action` with context to Python.
3. Append + rerun updates in place; a half-typed field survives; the processor is not recreated.
4. Mid-run streaming repaints progressively, or the fragment fallback is shown to work.
5. Light/dark toggle changes the surface.

Reopen ADR-001/002 if: custom elements don't style inside the shadow root without `isolate_styles=False`; the component remounts every rerun; 0.15.0 can't read 1.0 payloads.

## 8. Decisions

**ADR-001 — Wrap the official renderer.** Accepted; confirmed by M0.
Context: the spec went 0.9 → 1.0 with wire renames in a year; 1.1 is already mentioned. Options: wrap `@a2ui/react` + `web_core`; reimplement with `st.*`; wrap `@a2ui/lit`. Decision: wrap React. Consequences: spec tracking and widgets are inherited; we carry a Node build; npm packages are pinned exactly because 0.13–0.15 each broke something. Lit is a cheap fallback because the widgets are the same custom elements.

**ADR-002 — Components v2, frameless.** Accepted 2026-11-16.
Context: the brief assumed an iframe; Streamlit's recommended API since 1.51 has none. Options: v2; v1 iframe. Decision: v2. Why: triggers give once-only delivery, keyed instances update in place, `--st-*` gives theming, and it is where Streamlit invests. Consequences: no browser sandbox, so section 6 carries the whole security argument; `streamlit>=1.51`.

**ADR-003 — The API is a message pipe.** Accepted; confirmed by M0.
Decision: agent→renderer messages in, at most one renderer→agent message out per rerun, uninterpreted. Consequences: function calls need no new API; spec changes rarely touch Python; authors handle raw protocol dicts for now.

**ADR-004 — Log in session_state is the source of truth.** Accepted; confirmed by M0.
Consequences: remounts are correct by construction; the full log is re-sent each rerun (fine at prototype scale, compaction later); unsent in-surface edits are lost on remount.

**ADR-005 — A2UI 1.0 only.** Accepted.
Options: 1.0; 1.0 + 0.9.1. Decision: 1.0. Consequences: half the test matrix; 0.9.1 users are told to upgrade; revisit only on a real request.

**ADR-006 — Basic catalog only, no passthrough.** Accepted.
Consequences: the geospatial catalog will need a designed extension point later.

**ADR-007 — Streaming happens across reruns.** Accepted (forced by M0).
Context: Streamlit allows one call per keyed element per script run, so a surface cannot be repainted mid-run. Options: fragment timer; `st.rerun()` per chunk; a new key per step (rejected: new key means new element, state resets, and it breaks ADR-004). Decision: the documented pattern is the component inside `@st.fragment(run_every=...)` reading a log that the agent's stream appends to. Consequences: the package ships no streaming helper in v0.1, only a documented example; the author owns how the stream is consumed between reruns; repaint granularity is the fragment interval, not per message. To check in M1: what a trigger fired inside a fragment reruns (fragment only, or the whole app) and where the returned message is visible.

**ADR-008 — Dependency overrides.** Accepted 2026-11-17.
Context: (a) `@a2ui/markdown-it@0.2.2` declares peer `@a2ui/web_core@^0.14.0` while `@a2ui/react@0.15.0` needs 0.15, so a plain install fails; (b) it pins `dompurify` to exactly 3.4.11, which `npm audit` flags (one critical, one high, others lower; all fixed by 3.4.17). The package calls `purify.sanitize(html)` with default options, and the advisories' titles concern `IN_PLACE`, `SAFE_FOR_TEMPLATES`, `CUSTOM_ELEMENT_HANDLING` and XHTML parsing, none of which that call uses; full advisory text not reviewed. (c) zod `<4.6.6` has a high memory-exhaustion advisory; `web_core` requires zod 3, so there is no in-range fix. Options: override; wait for upstream. Decision: scoped npm `overrides` for the `web_core` peer and for `dompurify` to the current patched release, pinned exactly; accept the zod advisory and list it as a residual risk. Consequences: we run a combination upstream has not released together, so each override is removed as soon as upstream ships a fix, and both are reported upstream. This is the package's only HTML sanitizer, so "probably unreachable" is not enough to leave it unpatched.

**ADR-009 — Renderer errors stay in the browser for v0.1.** Accepted 2026-11-17.
Context: only one message returns per rerun, so sending 1.0 `error` messages on the same trigger could displace an action. Options: (a) console only; (b) visible notice in the component, nothing to Python; (c) second trigger; (d) batch all outbound messages into a list, changing the return type. Decision: (b), rendered as plain text. Consequences: the developer sees a broken payload immediately; the agent cannot yet self-correct from validation errors, which is a real A2UI feature we are not delivering. (d) is the likely later answer and would be a breaking change to the return type, acceptable before 1.0 of this package.