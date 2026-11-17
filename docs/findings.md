# streamlit-a2ui — Findings (2026-11-16)

What was checked, where, and what it means for the design. Decisions live in `architecture.md`.
First-hand = read from the registry, the published tarball, or the vendor's own docs/repo today.

## 1. Is anyone already doing this?

| Where | Query | Result |
|---|---|---|
| GitHub repo search | `a2ui streamlit` | 1 repo (`emivlp/cloudspec-ai`): an app that uses both, not a renderer |
| GitHub repo search | `a2ui gradio`, `a2ui chainlit` | 0 |
| GitHub repo search | `a2ui nicegui` | 2 app repos, no renderer package |
| GitHub code search | `a2ui` + `streamlit` in `.py` | ~10 hits, all application code. Looked at three: `ppijbb/sparkleforge` regex-detects A2UI JSON in agent output and hand-maps it for its own Streamlit app; `manaplatform/mana-agent` and `phenobarbital/ai-parrot` only mention both |
| PyPI | `streamlit-a2ui`, `a2ui-streamlit`, `st-a2ui` | all 404 — names are free |
| a2ui.org community renderers | — | 22 renderers, none for a Python UI framework |

Conclusion: no reusable Streamlit renderer exists. The app-level hits are evidence of demand: people are hand-rolling it.
Not checked: issue trackers of `a2ui-project/a2ui` and `streamlit/streamlit` for a pending official effort (GitHub issue search was not reachable from this session). Worth a two-minute manual look before announcing.

## 2. A2UI — spec

- 1.0 released 2026-11-11, status Current. 0.9.1 and 0.9 Previous, 0.8 Deprecated. A 1.1 is mentioned in the repo.
- 0.9 → 1.0: `callFunction` → `callRendererFunction`; new `callAgentFunction`, `rendererFunctionResponse`, `agentFunctionResponse`; client/server → renderer/agent; `theme` removed from `createSurface`; envelope keys take an `@` prefix; MIME type `application/a2ui+json`; a surface can mix catalogs; catalogs can declare `allowedParents` / `allowedChildren`.
- Basic catalog ID: `https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json`.

## 3. A2UI — published packages (first-hand, npm registry + tarballs)

| Package | Version | Published |
|---|---|---|
| `@a2ui/react` | 0.15.0 | 2026-11-02 |
| `@a2ui/web_core` | 0.15.0 | 2026-11-02 |
| `@a2ui/lit` | 0.15.0 | 2026-11-02 |
| `@a2ui/markdown-it` | 0.2.2 | 2026-10-17 |
| `a2ui-agent-sdk` (PyPI) | 0.11.0 | — |

Note the packages predate the 1.0 announcement by nine days. Expect a release soon; pin exactly.

What the 0.15.0 tarballs show:

- **1.0 support is in the published build.** `@a2ui/web_core` exports `./v1_0`, `./catalogs/basic/v1` and `./rpc`. `@a2ui/react` exports the root (version-agnostic `A2uiSurface`), `./v0_9`, `./v0_8`. There is no `@a2ui/react/v1_0`; use the root.
- **The processor defaults to v0.9.** `new MessageProcessor(catalogs, actionHandler?, options?)`; `options.version` defaults to `'v0.9'`, so we must pass `'v1.0'` explicitly.
- **Function calls are there.** `MessageProcessor.callAgentFunction(surfaceId, call, options)` returns a Promise with a default 30 s timeout, and needs an options listener for outbound renderer messages. That listener is the single outbound hook our trigger should be wired to. Implication: an `agentFunctionResponse` must come back through Streamlit within 30 s or the call rejects; the timeout is configurable.
- **Capabilities are generated for us.** `getRendererCapabilities({versions})` exists; Python should receive capabilities from the frontend build (or a JSON emitted at build time), not hand-write them.
- **Basic catalog components are W3C custom elements**, shared by all web renderers; React wraps each in `<a2ui-react-<name>>`. Custom element registration is global to the page. In frameless Streamlit that means: one definition per page, and two different bundle versions on one page would collide. Also why "React vs Lit" matters less than expected — the widgets are the same elements either way.
- **Theming hooks are CSS variables**: `--a2ui-color-primary`, `--a2ui-color-background`, `--a2ui-color-surface`, `--a2ui-color-on-background`, `--a2ui-color-border`, `--a2ui-spacing-{xs,s,m,l}`, `--a2ui-font-size-{xs,s,m,l,xl}`, `--a2ui-border-radius`, plus per-component ones (`--a2ui-textfield-*`, `--a2ui-checkbox-*`). CSS custom properties inherit through shadow roots, so a `--st-*` → `--a2ui-*` mapping on our host element should reach them. The exact mapping table is spike work.
- **Markdown is the one HTML sink.** `Text` renders Markdown through a renderer the host supplies (`MarkdownContext` = function returning HTML, or `MarkdownComponentContext` = React component). We supply `@a2ui/markdown-it` (markdown-it + DOMPurify) and expose no way to swap it.
- **No built-in loading state since 0.15.0.** A surface renders nothing until its root arrives; errors go to the surface's `onError`. We render our own "waiting" state and decide what to do with errors.
- **Churn is real.** 0.13, 0.14 and 0.15 each carry breaking changes in the changelog. Peer deps: `react ^18 || ^19`, `zod ^3.25.76`. `web_core` depends on `lit ^3.3.3`, so Lit ships in our bundle regardless.
- **Upstream's own security note** (React README): treat agent output as untrusted; risks named are UI spoofing, XSS via property values, and layout DoS.

## 4. Streamlit (first-hand, docs + PyPI + template README)

- Current Streamlit: **1.67.0**. Components v2 arrived in 1.51 (late 2025). `@streamlit/component-v2-lib` is at 0.2.0.
- v2 is frameless; default mount is inside a shadow root, which the docs say is not a security boundary. v1 (iframe) is "still supported for components that already use it"; the template README says new components should use v2.
- Python → JS: `data=` (JSON, Arrow, bytes). JS → Python: `setStateValue` (persists) and `setTriggerValue` (resets after the rerun); both cause a rerun. Callbacks are `on_<name>_change`.
- With a `key`, Streamlit updates the existing frontend element when parameters change; without one it creates a new element and state resets.
- Theme is exposed as `--st-*` CSS custom properties.
- Packaging: inner `pyproject.toml` with `[[tool.streamlit.component.components]]` + `asset_dir`; register as `"<package>.<component>"`; `js=`/`css=` globs relative to `asset_dir`. Everything in `asset_dir` is publicly served.
- Official scaffold: `uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v2` (React variant at `templates/v2/template/`). Template prerequisites: uv, Node 24, npm.

## 5. Still open — the spike answers these

1. Does re-calling a keyed v2 component *within one script run* repaint progressively, or only between reruns?
2. Is the JS renderer function re-invoked with new `data` on rerun, and does our processor instance survive it?
3. Do the custom elements style correctly inside Streamlit's shadow root with `isolate_styles=True`?
4. Does the 0.15.0 build read real 1.0 payloads end to end (create surface → update → action out)?
5. Exact `--st-*` → `--a2ui-*` mapping, light and dark.

## 6. M0 spike results and corrections (2026-11-16)

Answers to section 5: (1) no, a second call to a keyed component in one run raises `StreamlitDuplicateElementKey`; `st.fragment(run_every=0.5)` streams correctly. (2) yes, one processor per key for the whole session. (3) yes, with `isolate_styles=True`. (4) yes. (5) done in `frontend/src/theme.css`.

Corrections to earlier sections, found by installing and running the packages:

- The pins do not install as written: `@a2ui/markdown-it@0.2.2` declares peer `web_core@^0.14.0`. Needs an npm `overrides` entry. Reproduced.
- The processor's version value is `'1.0'`; `'v1.0'` is accepted and normalised to it.
- Section 2's "envelope keys take an `@` prefix" was misleading. The message envelope is `{"version":"1.0","createSurface":{...}}`. The `@` prefix is on dynamic values (`@path`, `@call`, `@index`). The evolution guide also lists `@`-prefixed component-level keys such as `@catalogId`; not checked against the package.
- The action handler receives an `ActionPayload`, not a wire message; `web_core` has no outbound formatter, so the frontend wraps it.
- `injectBasicCatalogStyles()` always adopts a stylesheet onto the host document (page-wide `color-scheme` and `--a2ui-*` defaults).
- The frontend `key` argument is Streamlit's internal id, not the Python key.
- `npm run dev` writes source maps into the served `asset_dir`; package only from `npm run build`.

Security audit, reproduced independently with `npm audit` on the pinned set: 1 critical, 4 high.
- `dompurify` 3.4.11 (exact pin inside `@a2ui/markdown-it`): six advisories, worst critical (GHSA-cg2g-xh64-v4q7, `SAFE_FOR_TEMPLATES`), one high (GHSA-mrv2-3pqr-j5jr, `IN_PLACE`); all fixed by 3.4.17; latest is 3.4.18. `@a2ui/markdown-it`'s `sanitizer.js` calls `purify.sanitize(html)` with default options and no hooks, so by their titles none of these modes is in use. Advisory bodies not read.
- `zod` `<4.6.6`: high, memory exhaustion on oversized constrained collections (GHSA-mrhx-c7xc-m3w5). Latest zod 3 is 3.25.76; no fix in the 3.x line that `web_core` requires.
- 0.2.2 is the latest `@a2ui/markdown-it`; there is no upstream release to move to yet.

Measured: bundle 951 kB JS (261 kB gzip) + 1.7 kB CSS. Python 3.13.13, Vite 8.3.8, TypeScript 6.0.3, Node 24.15.0.

## Sources
- npm registry and tarballs for `@a2ui/react@0.15.0`, `@a2ui/web_core@0.15.0` (README, CHANGELOG, `package.json` exports, `message-processor.d.ts`)
- PyPI JSON API: `streamlit`, `a2ui-agent-sdk`, name-availability checks
- GitHub repository and code search; raw files from the repos named above
- https://a2ui.org/specification/v1.0-evolution-guide/ · https://a2ui.org/roadmap/ · https://a2ui.org/ecosystem/renderers/
- https://developers.googleblog.com/a2ui-10-build-delightful-fast-reliable-agentic-experiences/
- https://docs.streamlit.io/develop/concepts/custom-components/overview
- https://docs.streamlit.io/develop/concepts/custom-components/components-v2/mount
- https://docs.streamlit.io/develop/concepts/custom-components/components-v2/register
- https://docs.streamlit.io/develop/concepts/custom-components/components-v2/package-based
- https://github.com/streamlit/component-template (README)