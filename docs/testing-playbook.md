# Testing playbook

How to check `streamlit-a2ui` by hand and with the automated suite. Use it to review a branch, before merging, and after upgrading Streamlit or any `@a2ui/*` package. Allow about 30 minutes for everything, or 10 for parts 1 and 3 only.

No API key is needed. Both examples use scripted agents; nothing calls an LLM.

Record results in the PR or the milestone report as **pass**, **fail** (what you saw) or **skipped** (why).

## 0. Setup

From the repo root. If the system Node is older than 24, put Node 24 on the `PATH` first, for example:

```bash
export PATH=~/.nvm/versions/node/v24.15.0/bin:$PATH
```

```bash
cd streamlit_a2ui/frontend && npm install && npm run build && cd ../..
```

```bash
uv venv && uv pip install -e . --force-reinstall && uv pip install pytest ruff
```

Rebuild the frontend before installing, and again after any frontend change. After a rebuild, restart Streamlit and reload the page.

## 1. Automated suite (about 5 minutes)

| # | Command | Expected |
|---|---|---|
| A1 | `cd streamlit_a2ui/frontend && npm test` | 9 tests pass (cursor, replay, error reporting, waiting state, action wrapping, outbound passthrough) |
| A2 | `cd streamlit_a2ui/frontend && npm run typecheck` | No errors |
| A3 | `.venv/bin/pytest -q` | 17 tests pass. Builds a wheel and checks its contents, so it needs A0's `npm run build` |
| A4 | `.venv/bin/ruff check . && .venv/bin/ruff format --check .` | No findings |
| A5 | `cd streamlit_a2ui/frontend && npm run format:check` | "All matched files use Prettier code style!" |
| A6 | `uv pip install pytest-playwright && .venv/bin/playwright install chromium && .venv/bin/pytest e2e -q` | 1 test passes: starts `examples/basic_app.py`, fills the form, presses Send, sees the reply and the returned action |

CI (`.github/workflows/ci.yml`) runs A1–A6 on every pull request. On a failure, the run's `e2e-results` artifact holds a Playwright trace; open it with `.venv/bin/playwright show-trace <file>.zip`.

## 2. Build and packaging guards (about 5 minutes)

| # | Check | How | Expected |
|---|---|---|---|
| G1 | One DOMPurify, patched | `cd streamlit_a2ui/frontend && npm ls dompurify` | Exactly one `dompurify@3.4.18 overridden` |
| G2 | Patched DOMPurify is in the bundle | `grep -o '3\.4\.1[0-9]' streamlit_a2ui/frontend/build/*.js \| sort -u` | Includes `3.4.18`, not `3.4.11` |
| G3 | Audit | `cd streamlit_a2ui/frontend && npm audit` | Only the zod advisory (GHSA-mrhx-c7xc-m3w5), as recorded in `docs/security.md` |
| G4 | Source-map guard fails when it should | `cd streamlit_a2ui/frontend && touch build/planted.map && node scripts/check-build.ts; echo "exit $?"; rm build/planted.map` | Error naming `planted.map`, `exit 1` |
| G5 | Wheel contents | `uv build --wheel && unzip -l dist/streamlit_a2ui-*.whl` | Contains `index-*.js`, `index-*.css`, `renderer_capabilities.json`, `THIRD_PARTY_LICENSES.txt`; no `.map` files |
| G6 | Import outside `streamlit run` | `.venv/bin/python -c "from streamlit_a2ui import renderer_capabilities; print(renderer_capabilities())"` | Prints the `1.0` capabilities with the basic catalog ID; no `StreamlitAPIException` |

## 3. Manual click-through: basic example (about 5 minutes)

```bash
.venv/bin/streamlit run examples/basic_app.py
```

Open the URL it prints. Keep the browser's developer console open on the Console tab.

| # | Do | Expected |
|---|---|---|
| B1 | Load the page | A "Contact us" form: Name, Message, a **Send** button, the caption "The agent's reply will appear here." Under "Last message returned by `a2ui_surface`": "None yet. Fill in the form and press Send." |
| B2 | Type a name and a message, press **Send** | The JSON panel shows one message: `"version": "1.0"`, `action.name` `send_message`, `context` with your name and message. The reply reads "Thanks, *name*! The agent got *N* characters." |
| B3 | Press **Send** again without changing anything | A new action with a new `timestamp`. Exactly one per click |
| B4 | Type new text into Message, don't send. Open **Try more**, press **Agent: append an update** | Title becomes "Contact us (1)". The unsent text is still in the field. Log length goes up by 1 |
| B5 | Press **Agent: append an invalid message** | A red plain-text notice inside the component, starting `VALIDATION_FAILED [contact]`. The form stays visible with your text. The JSON panel does not change. The console shows one `[streamlit-a2ui] A2UI error` warning |
| B6 | Press **Send** after B5 | Still works: a new action arrives and the reply updates |
| B7 | Press **Replace the log** | The surface rebuilds from scratch: fields empty, notice gone, title back to "Contact us" |
| B8 | ⋮ menu → Settings → Theme: switch between Light and Dark | The surface, the notice (repeat B5 if needed) and the waiting text follow the theme. Text stays readable in both |
| B9 | Reload the browser tab | The surface is rebuilt from the log (title updates kept). Unsent typed text is lost; that is expected and documented |

## 4. Manual click-through: streaming example (about 5 minutes)

Stop the first app (Ctrl+C), then:

```bash
.venv/bin/streamlit run examples/streaming_app.py
```

| # | Do | Expected |
|---|---|---|
| S1 | Load the page | "Waiting for the agent…" briefly, then a dashboard appears piece by piece, about every 0.5 s: loading captions, then the analytics card, then log lines one at a time. The caption under it says `streaming` and the log length grows |
| S2 | Press **Acknowledge** while lines are still arriving | Streaming continues. The dashboard shows "Acknowledged after *N* log lines." with N below 8. The caption says `actions received: 1`, and the action JSON appears |
| S3 | Wait until all 8 lines are in | The caption changes to `stream finished`; the log length stops growing |
| S4 | Press **Acknowledge** again | "Acknowledged after 8 log lines.", `actions received: 2` |
| S5 | Press **Restart the stream** | The dashboard starts again from empty and streams as in S1 |

## 5. Robustness checks (optional, about 5 minutes)

| # | Do | Expected |
|---|---|---|
| R1 | With an example open, rebuild the frontend (`npm run build`) and restart Streamlit **without** reloading the tab | The component shows "Another build of streamlit-a2ui is already loaded on this page. Reload the page." Reloading fixes it. No blank component, no uncaught exception |
| R2 | In the basic example, click **Send** twice very fast | Record how many actions arrive. A second action can replace the first (known, unmeasured; see the M3 item in `docs/release-plan.md`). Do not file it as a new bug |
| R3 | Open the page in a second browser (Firefox or Safari) and repeat B1–B5 | Same results. Record the browser; M1 checked only a Chromium-based one |

## 6. Clean clone (criterion 1, about 10 minutes)

Proves the README's commands work with nothing left over from your checkout. `git clone .` checks out the branch you are on; commit first, because uncommitted changes are not cloned.

```bash
git clone . /tmp/a2ui-clean
```

Then run parts 0 and 1 inside `/tmp/a2ui-clean`, and start each example once (B1 and S1). Delete the folder afterwards.

## Not covered by this playbook

- A real agent. Every payload is scripted; M3 adds a Google ADK check.
- The declared Streamlit floor (`>=1.51`); only 1.67 has been run, locally and in CI. M2's version matrix will cover it.
- Windows, Linux, and classic (non-overlay) scrollbars.
- An exception thrown while React renders a surface: it would blank the component. The error boundary is planned for M2.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Another build of streamlit-a2ui is already loaded" | Reload the page after restarting Streamlit |
| `npm install` fails with `ERESOLVE` | `package.json` overrides are missing or changed; see `docs/security.md` |
| A `js=` or `css=` pattern matches more than one file | `npm run clean`, then `npm run build` |
| `renderer_capabilities()` raises `FileNotFoundError` | Run `npm run build`; the JSON file is generated, not committed |
| pytest fails building the wheel | Run `npm run build` first |
| Port 8501 in use | `.venv/bin/streamlit run examples/basic_app.py --server.port 8502` |
