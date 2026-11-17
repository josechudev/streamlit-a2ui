# M1 report: harden the spike into v0.1

Date: 2026-11-17. Branch `m1-v0.1`, created from `m0-spike`, 18 commits, not pushed. Browser checks ran in the Chromium-based browser pane of the Claude desktop app, on macOS, with the DOM and console inspected directly. The handoff is in `docs/handoff-m1.md`.

## Acceptance criteria

| # | Criterion | Result | How it was checked |
|---|---|---|---|
| 1 | Clean clone builds, installs and runs both examples with the `CLAUDE.md` commands | **Pass** | `git clone` of `m1-v0.1` into a scratch directory, then exactly the Commands section: `npm install`, `npm run build`, `npm test` (9 passed), `npm run typecheck`, `uv venv`, `uv pip install -e . --force-reinstall`, `uv pip install pytest ruff`, `pytest -q` (17 passed), `ruff check` and `ruff format --check` (clean). Both examples started with `streamlit run` (`/_stcore/health` returned `ok`) and ran under `AppTest` with no exceptions. The clone produced the same bundle (`index-D0EihXIi.js`) that was tested in the browser |
| 2 | `basic_app.py`: renders; the action returns once with its context; the reply updates in place; unsent text survives | **Pass** | Browser. Typed "Ada Lovelace" and a message, pressed **Send**: `a2ui_surface` returned `{"version":"1.0","action":{"name":"send_message","surfaceId":"contact","sourceComponentId":"submit_button","timestamp":…,"context":{"name":"Ada Lovelace","message":"Hello from the test"}}}`; the log went from 2 to 3 entries (one reply, so one delivery); the reply text rendered in place. Then typed " DRAFT" into the name field without sending, read the field's value from the DOM, clicked **Agent: append an update**: the title changed to "Contact us (3)" and the field still held "Ada Lovelace DRAFT" |
| 3 | `streaming_app.py`: progressive content; an action during or after streaming reaches Python | **Pass** | Browser, sampling the DOM every 50 ms. After **Restart the stream**, the waiting state showed until the root arrived, then the log grew one message per ~500 ms (2, 3, …, 20) and rendered Text count rose 0 → 5 → … → 12. **Acknowledge** clicked mid-stream: received, reply "Acknowledged after 7 log lines" rendered while streaming continued. Clicked again after the stream finished and the timer was off: received, "after 8 log lines", 2 actions total |
| 4 | An invalid message shows the notice, keeps rendered surfaces, returns nothing | **Pass** | Browser. **Agent: append an invalid message** appends a `Text` without `text`. The component showed one notice, `VALIDATION_FAILED [contact]: Validation failed for component 'Text' (title): …`; the surface stayed rendered with the typed "Grace" intact; "Last message" stayed "None yet" and the log grew by exactly that one message (no reply appended). `console.warn` logged the error from the production bundle. Checked in dark and light theme |
| 5 | `renderer_capabilities()` is generated from `web_core` | **Pass** | `scripts/generate-capabilities.ts` builds a processor exactly like the frontend's (basic catalog, `version: "1.0"`) and writes `MessageProcessor.getRendererCapabilities({versions: ["1.0"]})` to `streamlit_a2ui/renderer_capabilities.json` during `npm run build`. The file is git-ignored and outside `asset_dir`. pytest checks its content and that the wheel ships the same file |
| 6 | One `dompurify` 3.4.18 in lockfile and bundle | **Pass** | `npm ls dompurify` → `dompurify@3.4.18 overridden`, single copy. `package-lock.json` resolves `node_modules/dompurify` to 3.4.18 (the `3.4.11` string left in it is `@a2ui/markdown-it`'s declared dependency). The bundle contains DOMPurify's `t.version = "3.4.18"` |
| 7 | Wheel has no source maps or CDN references; no construction log | **Pass** | pytest builds the wheel with `uv build` and asserts: no `*.map`, no `sourceMappingURL=`, no URL that would load remote scripts, stylesheets or fonts (the pattern is itself tested against positive and negative samples). `npm run build` fails if `build/` holds source maps (checked by planting a `.map` file: exit 1). `grep` finds no "MessageProcessor constructed" in the bundle |
| 8 | Tests and linters pass; 2, 3, 4 exercised in a browser | **Pass** | Vitest 9 passed, pytest 17 passed, `tsc --noEmit` clean, `ruff check` and `ruff format --check` clean, Prettier clean. No `any`, `@ts-` or `dangerouslySetInnerHTML` in our code. Criteria 2–4 as above |
| 9 | Docs exist and agree | **Pass** | `CLAUDE.md`, `README.md`, `docs/security.md`, `docs/adr/0001`–`0009`, `docs/notes-m1.md` and this report. The ADRs are named `NNNN-title.md` per `CLAUDE.md`, not `001`–`009` as the handoff lists them |

## What the step-4 review changed, and why

The spike's frontend was one renderer function that re-rendered the React tree on every rerun, plus a `Surfaces` component that subscribed to the processor itself.

- **State moved into `LogSession` (`src/session.ts`).** It owns the processor, the cursor, replay and error notices, and publishes an immutable snapshot. `Surfaces` reads it with `useSyncExternalStore`, and the React root is rendered once per mounted instance instead of on every rerun. This makes the cursor, replay and outbound wrapping unit-testable without a DOM.
- **Replay path.** The spike replayed only when the log got shorter. A log replaced by an equally long or longer one was processed as if appended. `LogSession` now also compares the entry just before the cursor (as JSON) with what it last processed, and replays if it changed. On replay, surfaces are keyed by a generation counter so React remounts them rather than reusing elements bound to disposed models, and old notices are cleared.
- **Effect cleanup.** The cleanup unmounts the root, disposes the processor and unsubscribes from its error events. It is idempotent.
- **Double registration.** `web_core` registration is idempotent within one bundle, but a second copy of the bundle (for example after a rebuild without a page reload) would throw a tag-name collision while rendering and blank the component. The first copy now claims the page through a global symbol, and a later copy renders a plain-text notice. Checked in the browser by importing the served bundle a second time under another URL and calling its renderer.
- **Errors (step 6).** Processing errors and surface errors are shown as a plain-text notice (the last five, with a count) and logged with `console.warn`. The spike only logged the return value of `processMessagesWithErrors`, which misses errors raised while rendering.
- **Waiting state.** Shown until any surface has its root component, computed from the processor instead of the CSS `:empty` trick.
- **Removed:** the `MessageProcessor constructed` log and its counter, the unused frontend `key` argument, and the `dropConsole: false` override (template default restored).
- **Python.** `renderer_capabilities()` added. The component is now registered on first call instead of at import (see "Wrong in the handoff or `CLAUDE.md`", item 4).
- **Bug found by testing, fixed:** the first version subscribed to both `surface.onError` and `model.onError`; the group re-emits surface errors, so each error was shown twice. There is now one subscription and a test that counts.

## Dependencies

| Package | Version |
|---|---|
| `@a2ui/react`, `@a2ui/web_core` | 0.15.0 (exact; still the latest on npm) |
| `@a2ui/markdown-it` | 0.2.2 (exact; still the latest) |
| `dompurify` | 3.4.18 (exact override; the latest) |
| `zod` | 3.25.76 (transitive) |
| `lit` | 3.3.3 (transitive) |
| `@streamlit/component-v2-lib` | 0.2.0 |
| React / react-dom | 18.3.1 |
| Vite / TypeScript / Vitest (new) / Prettier | 8.3.8 / 6.0.3 / 5.1.0 / 3.10.1 |
| Streamlit / Python | 1.67.0 / 3.13.13 |
| Node / npm / uv | 24.15.0 / 11.12.1 / 0.11.14 |

No `@a2ui/*` package has a newer release than the pinned one.

Remaining `npm audit`: one advisory, reported four times.

```
zod  <4.6.6
Severity: high
Zod can exhaust memory while validating oversized constrained collections - https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
No fix available
node_modules/zod
  @a2ui/react  *
  @a2ui/web_core  *
    @a2ui/markdown-it  *

4 high severity vulnerabilities
```

Before the `dompurify` override, the same command also reported DOMPurify 3.4.11 (one critical, others lower). Full output is in `docs/security.md`.

## Bundle size

| | JS | JS gzip | CSS |
|---|---|---|---|
| M0 (`m0-spike`) | 950.79 kB | 260.59 kB | 1.69 kB |
| M1 | 955.08 kB | 262.29 kB | 1.98 kB |

DOMPurify 3.4.18 accounts for about 3.5 kB of the increase; the rest is the session store, notice and guard.

## Licenses and NOTICE

None of the 32 production npm dependencies ships a `NOTICE` file, so Apache-2.0 §4(d) adds nothing and the package has no `NOTICE`. But the MIT, BSD-2/3-Clause, ISC and Python-2.0 licenses require their copyright and license text to accompany redistribution, and the minified bundle drops license comments. `npm run build` now writes `streamlit_a2ui/THIRD_PARTY_LICENSES.txt` from `package-lock.json` and the wheel ships it. This was not in the handoff; it is the smallest change that makes the wheel compliant.

## Wrong in the handoff or `CLAUDE.md`

1. **"Restore the template's `dropConsole`" conflicts with "keep the `console.warn`".** The template's `dropConsole: true` removes every `console.*` call, including ours. Resolved by restoring the default and calling `warn` through a reference bound in `session.ts`, which the minifier leaves in place (checked in the bundle and in the browser console). Side effect: `web_core`'s own console diagnostics are stripped from production builds. Owner decision (2026-11-17): keep `dropConsole: true` with the bound `warn`.
2. **"A deliberately invalid message"**: `@a2ui/web_core` 0.15.0 accepts unknown component types without an error, even when they are in the rendered tree. The example uses a `Text` without `text`, which fails validation.
3. **Surface errors are re-emitted on `model.onError`.** Subscribing to both reports each error twice.
4. **Import-time registration made the package unimportable outside `streamlit run`.** Streamlit resolves `asset_dir` only after its runtime starts, so `from streamlit_a2ui import renderer_capabilities` in a plain agent process raised `StreamlitAPIException`. Registration now happens on the first `a2ui_surface` call.
5. **ADR content for 003–006 has no Context or Options**, and 005 has no Context. Those sections say "Not recorded." rather than inventing text.
6. **ADR file names.** The handoff says `docs/adr/001`–`009`; `CLAUDE.md` says `NNNN-title.md`. Followed `CLAUDE.md`.
7. **"Node 24 via nvm"**: on this machine `~/.nvm/nvm.sh` is missing, so `nvm use` fails; Node 24.15.0 was run from `~/.nvm/versions/node/v24.15.0/bin` directly.
8. **pytest now needs `npm run build` and uv first**, because it builds and inspects the wheel. `CLAUDE.md` says so.
9. **"Sample payloads taken from the installed package's schemas"**: the examples' payloads are adapted from `00_simple-login-form.json` and `31_incremental-dashboard.json` (renamed IDs and text, added a `reply`, `ack_*` and `lineCount`), not copied verbatim. The frontend unit tests load the example files from `node_modules` unchanged.

## Not done or not verified

- Light/dark switching (M0 criterion 5) was not re-run as a toggle; the dark and light themes were each checked on fresh loads, including the error notice.
- The `color-scheme` check (`docs/notes-m1.md`) covers one Chromium-based browser on macOS with overlay scrollbars.
- `.claude/launch.json` (local preview configs) is untracked and was not committed.

## Open problems and suggested next steps

These are proposals, not work done.

1. **Report upstream:** the stale `web_core` peer range and the `dompurify` 3.4.11 pin in `@a2ui/markdown-it`; unknown component types passing validation in `web_core`. Remove each override when fixed.
2. **Render-time exceptions.** A processing error is contained, but an exception thrown while React renders a surface would unmount the whole root and blank the component. An error boundary needs a class component, which `CLAUDE.md` rules out. Owner decision.
3. **Second outbound message per rerun.** Two renderer messages before a rerun can overwrite each other on the single trigger. Not measured. Batching (ADR-009's likely answer) would fix it and change the return type.
4. **Bundle size.** Vite's library mode for ES output mangles but does not strip whitespace (26,839 lines). Setting `codegen.removeWhitespace` would shrink the raw file; gzip size would change little.
5. **Lazy registration** deviates from Streamlit's usual module-level pattern. It works under `streamlit run`, `AppTest` and plain imports; a Streamlit change to registration timing would surface here first.
6. **`docs/architecture.md`** still describes the state at the end of M0; fold M1's findings in when it is next revised.
7. **Next milestone candidates:** report errors to the agent (ADR-009 follow-up), a CI workflow, publishing. All out of scope for M1.
