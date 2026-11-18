# M1 notes: two open questions

Checked 2026-11-17 on Streamlit 1.67.0, `@a2ui/*` 0.15.0, in the Chromium-based browser pane of the Claude desktop app, on macOS. The probe apps were throwaway scripts outside the repository; what they did is described below so it can be repeated.

## 1. A trigger fired inside a fragment: what reruns, and where is the message?

**Answer: only the fragment reruns, and the message is visible only as the return value of the `a2ui_surface` call inside that fragment.**

Probe: a script that counts full-app runs at the top level, counts fragment runs inside an `@st.fragment` (no `run_every`), calls `a2ui_surface` inside the fragment with a one-button surface, and records in `st.session_state` every non-`None` return value. A line outside the fragment prints the recorded list.

| Step | App runs | Fragment runs | Recorded inside the fragment | Line outside the fragment |
|---|---|---|---|---|
| Page load | 1 | 1 | `[]` | `[]` |
| Click the surface button | 1 | 2 | `['fragment@app1/frag2']` | `[]` (stale) |
| Click again | 1 | 3 | two entries | `[]` (stale) |

Each click produced one fragment rerun and exactly one non-`None` return value. The script outside the fragment did not run, so anything it renders keeps its old output even though `st.session_state` changed.

What `examples/streaming_app.py` therefore does:

- It handles the returned message **inside the fragment**: records it, appends the scripted agent's reply to the log, and calls `st.rerun(scope="fragment")` so the reply is rendered on the next fragment run.
- Everything that shows the result (the caption and the last action's JSON) is rendered inside the fragment too.
- If the rest of the page had to change, the handler would call `st.rerun(scope="app")` instead. The example does this once, when the stream is exhausted, so that the full rerun re-evaluates `@st.fragment(run_every=...)` with `None` and the timer stops.
- Checked in the browser: an action fired mid-stream was received ("Acknowledged after 7 log lines") while the stream kept repainting, and a second action fired after the stream ended, with the timer off, was also received ("after 8 log lines", 2 actions in total).

## 2. Does `web_core`'s page-wide `color-scheme` visibly change Streamlit's own widgets?

**Answer: no visible change was found, in either mismatch between the browser's preferred scheme and Streamlit's theme.** The computed value changes on `html`, `body` and Streamlit's portals outside `.stApp`, but Streamlit sets an explicit `color-scheme`, background and `scrollbar-color` where it matters, so nothing rendered differently.

Probe: a page with `st.text_input`, `st.selectbox` (40 options, so its dropdown scrolls), `st.text_area`, `st.number_input`, `st.date_input` and a fixed-height scrolling container. A query parameter mounts a one-Text `a2ui_surface`. Each page was loaded fresh, once without the component and once with it, and compared by computed style and screenshot.

After mounting, `document.adoptedStyleSheets` holds `:where(:root) { color-scheme: light dark; }` and its `.a2ui-dark` / `.a2ui-light` variants.

| | Browser prefers dark, Streamlit theme light | Browser prefers light, Streamlit theme dark |
|---|---|---|
| `html` / `body` `color-scheme` | `normal` → `light dark` | `normal` → `light dark` |
| Elements inside `.stApp` (all 249) | `light` before and after | `dark` before and after |
| Select dropdown (portal, outside `.stApp`) | `normal` → `light dark` | `normal` → `light dark` |
| `body` background | explicit `rgb(255,255,255)` | explicit `rgb(23,22,20)` |
| Scrollbars (`stMain`, container, dropdown, root) | explicit `scrollbar-color`, overlay; unchanged | same |
| Screenshots with and without the component | identical, including the open dropdown | identical |

When the browser's scheme and Streamlit's theme agree (the default, "Use system setting"), `light dark` resolves to the same scheme Streamlit uses, so there is nothing to conflict.

Not covered: other browsers, platforms with classic (non-overlay) scrollbars such as Windows, and native form controls that Streamlit does not style (none were found on this page). A Streamlit widget that renders a portal with UA-default controls would pick up the OS scheme instead of the theme once the component has loaded; this is the residual risk recorded in `docs/security.md`.
