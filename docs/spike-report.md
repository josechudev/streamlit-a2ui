# M0 spike report

Date: 2026-11-16. Everything was checked in `examples/spike_app.py`, running in a Chromium-based browser pane. The browser's DOM and console were inspected directly.

## Result

| # | Criterion | Result |
|---|---|---|
| 1 | v2 component mounts `@a2ui/react` in the default shadow root and renders a 1.0 basic-catalog surface (Column, Text, TextField, Button) | **Pass** |
| 2 | Button click returns a 1.0 `action` message with resolved context from `a2ui_surface` | **Pass** |
| 3 | Append + rerun updates in place; half-typed TextField keeps its content; `MessageProcessor` not recreated | **Pass** |
| 4 | Streaming by re-calling the keyed component inside one script run | **Fail**. `st.fragment(run_every=...)` **works** |
| 5 | Toggling Streamlit light/dark changes surface colors | **Pass** |

### 1. Mount and render: pass

The host is `data-testid="stBidiComponentIsolated"` with a `shadowRoot`. Inside it are `.a2ui-host > .a2ui-surface > a2ui-basic-column` and then `a2ui-basic-text`, `a2ui-basic-textfield` and `a2ui-basic-button`. The surface uses Streamlit's font, primary color, input background and border.

### 2. Action to Python: pass

After typing in the field and clicking **Submit**, `a2ui_surface` returned this value once, and `None` on the rerun that followed:

```json
{"version": "1.0",
 "action": {"name": "submit_name", "surfaceId": "form", "sourceComponentId": "submit",
            "timestamp": "2026-11-17T05:46:45.219Z", "context": {"name": "Ada Lovace"}}}
```

`context.name` is the `{"@path": "/name"}` binding resolved against the data model that the TextField wrote. The spike app then acts as the agent: it appends an `updateComponents` for the `status` Text, and the reply renders.

### 3. In-place update: pass

I typed `Ada Lov` and then clicked **Append update** twice. Each click appends an `updateComponents` message that replaces only the `status` Text, followed by `st.rerun()`. The status text changed, and the field still held `Ada Lov`. The console showed one `MessageProcessor constructed` line per component instance for the whole session: #1 for `main` and #2 for `stream`. The two appends, the action round trip and the theme toggle created no new processor.

### 4. Streaming: fails inside one run; `st.fragment` works

- **Re-calling inside one run.** The first call renders. The second call to `a2ui_surface(..., key="stream")` in the same run raises `streamlit.errors.StreamlitDuplicateElementKey: There are multiple elements with the same key='stream'`. Streamlit does not allow this pattern at all, even inside `st.empty()` containers. I did not work around it with per-step keys, because each new key would mount a new instance and a new processor.
- **`@st.fragment(run_every=0.5)`.** The fragment appends one message per tick and calls `a2ui_surface(frag_log, key="frag")`. DOM sampling every 50 ms showed the Text count go 0→1→2→3→4→5 at about 500 ms intervals (703, 1201, 1700, 2202 and 2750 ms). One processor (#3) handled the whole stream, and the `main` surface was not touched.

So streaming has to happen across reruns (a fragment timer, or `st.rerun()` per chunk), not inside a single run.

### 5. Theme: pass

These are computed colors inside the shadow root before and after switching from Dark to Light in Streamlit's menu. Nothing was remounted.

| Element | Dark | Light |
|---|---|---|
| input background | `rgb(45,43,39)` | `rgb(248,248,247)` |
| input text | `rgb(237,235,232)` | `rgb(47,45,43)` |
| input border | `rgb(74,71,66)` | `rgb(220,216,212)` |
| body text | `rgb(237,235,232)` | `rgb(47,45,43)` |
| button background | `rgb(207,66,80)` | `rgb(197,57,72)` |

The mapping is pure CSS in `frontend/src/theme.css` and is applied to `.a2ui-host`.

## Exact versions

| Thing | Version |
|---|---|
| Streamlit | 1.67.0 |
| Python | 3.13.13 |
| `@a2ui/react` / `@a2ui/web_core` | 0.15.0 / 0.15.0 (exact) |
| `@a2ui/markdown-it` | 0.2.2 (exact) |
| `@streamlit/component-v2-lib` | 0.2.0 |
| React / react-dom | 18.3.1 (template default) |
| zod (transitive) | 3.25.76 |
| lit (transitive) | 3.3.3 |
| Vite / TypeScript | 8.3.8 / 6.0.3 |
| Node / npm | 24.15.0 / 11.12.1 (via nvm; system node is 23.1.0) |
| uv | 0.11.14 |
| OS | macOS (Darwin 24.6.0) |

The production bundle is 951 kB (261 kB gzip) of JS plus 1.7 kB of CSS. The wheel contains only `__init__.py`, `pyproject.toml` and those two files, with no source maps. The bundle has no `fetch(` calls and no CDN or font URLs.

## Contradictions with CLAUDE.md and the handoff

1. **The pinned versions do not resolve with npm.** `@a2ui/markdown-it@0.2.2` declares the peer `@a2ui/web_core@^0.14.0`, which excludes 0.15.0, so `npm install` fails with `ERESOLVE`. `@a2ui/react@0.15.0` itself depends on `web_core ^0.15.0` and `markdown-it ^0.2.2`, so upstream ships this pair together anyway. I resolved it with an npm `overrides` entry in `package.json` (`@a2ui/markdown-it` → `@a2ui/web_core: $@a2ui/web_core`). That leaves one deduped copy of `web_core`. `--legacy-peer-deps` was not used. Owner: keep the override, or wait for a markdown-it release?
2. **The version string is `'1.0'`, not `'v1.0'`.** `ProtocolVersion` is `'v0.8' | 'v0.9' | 'v0.9.1' | '1.0'`, and `SpecVersion.V1_0 = "1.0"`. The docs say `'v1.0'` normalizes to the same value. I passed `'1.0'`.
3. **The `@` prefix is not on envelope keys.** In the 1.0 schemas the envelope is `{"version": "1.0", "createSurface": {...}}`, with no `@`. The `@` prefix is on dynamic values: `@path`, `@call` and `@index`.
4. **The action handler's argument is not a wire message.** The handler receives `ActionPayload`, which has `name`, `surfaceId`, `sourceComponentId`, `timestamp` and `context`, and may also carry `catalogId`, `userMessage` and `metadata`. web_core has no outbound formatter, so the frontend wraps the payload as `{"version": "1.0", "action": payload}`, following `renderer_to_agent.json`. The outbound listener's messages are already full envelopes and are sent unchanged.
5. **Node 24 is not the system default here.** The system node is 23.1.0. I used nvm's 24.15.0.

## Findings the owner should see

- **Security: `npm audit` reports a critical DOMPurify issue.** `@a2ui/markdown-it@0.2.2` pins `dompurify` to exactly `3.4.11`, which matches several advisories: GHSA-c2j3-45gr-mqc4, GHSA-55q2-fjhq-7xh7, GHSA-6688-9rhm-gjv2, GHSA-cg2g-xh64-v4q7, GHSA-mrv2-3pqr-j5jr and GHSA-c6gr-qvv4-5v3f. It is also high on `zod <4.6.6` (GHSA-mrhx-c7xc-m3w5, memory exhaustion on oversized collections). DOMPurify sanitizes agent markdown, and agent messages are untrusted, so this matters. I have not checked which advisories the way markdown-it calls DOMPurify can actually reach. I did not override it, because the pins are an owner decision. Options: an npm override to dompurify ≥3.4.17 (it is an exact dependency, so the override is the only route), or wait for upstream.
- **Style leak past `isolate_styles`.** `injectBasicCatalogStyles()` in web_core always adopts its token sheet onto the host page's `document` as well as the shadow root. After mount, `document.adoptedStyleSheets` holds `:where(:root){color-scheme: light dark}` plus the `--a2ui-*` defaults, and the page's computed `color-scheme` becomes `light dark`. Zero specificity limits the damage, but it is a page-wide side effect on Streamlit, and our code cannot opt out of it.
- **Streamlit has no color-scheme variable.** The catalog derives several tokens with `light-dark()` at `:root`, so `theme.css` redefines every derived color token from `--st-*` with `color-mix()`. Any new catalog token that uses `light-dark()` will follow the OS scheme, not Streamlit's theme, until it is mapped.
- **The renderer's `key` argument is Streamlit's internal id** (`st-bidi-component-<uuid>`), not the Python `key`. It is used only in the construction log line.
- **Processing errors are only logged.** `processMessagesWithErrors` returns `RendererErrorMessage`s, and the frontend sends them to `console.warn`, not to Python. Sending them to the agent is a 1.0 `error` message. With one trigger per rerun, they could collide with an action. This needs a decision.
- **Log replacement.** If the log gets shorter (the app replaced it), the frontend disposes the processor and replays from 0. This is the only time a new processor is created for a mounted key. The spike's **Reset log** button exercises it.
- **Production build keeps `console`.** The template's `dropConsole: true` would have removed the construction log, so `vite.config.ts` sets it to `false`.
- **`npm run dev` writes source maps into `build/`,** which is the publicly served `asset_dir`. Always run `npm run build` before packaging.
- **`renderer_capabilities()` is not implemented.** It appears in the target v0.1 API but none of the M0 criteria need it, and computing it needs the frontend processor or a static copy. It is left for after review.
- **The first pytest run failed after 32 s, and the second passed in 4 s.** The failure looked like a cold-start `AppTest` timeout (default 3 s), but I did not capture the error. The test now sets `default_timeout=60`, and it has passed on cold runs since.
- The generated `README.md` still describes the template's `streamlit_a2ui()` example. I left it for after M0, as planned.
