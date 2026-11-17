"""M0 spike: exercises the five criteria in CLAUDE.md.

Run with:  streamlit run examples/spike_app.py

Payload shapes follow node_modules/@a2ui/web_core/src/v1_0/schemas
(agent_to_renderer.json and catalogs/basic/examples/*.json).
"""

from __future__ import annotations

import time
from typing import Any

import streamlit as st

from streamlit_a2ui import a2ui_surface

CATALOG = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"
Message = dict[str, Any]


def create_surface(surface_id: str) -> Message:
    return {
        "version": "1.0",
        "createSurface": {"surfaceId": surface_id, "catalogId": CATALOG},
    }


def update_components(surface_id: str, components: list[Message]) -> Message:
    return {
        "version": "1.0",
        "updateComponents": {"surfaceId": surface_id, "components": components},
    }


def text(component_id: str, value: str) -> Message:
    return {"id": component_id, "component": "Text", "text": value}


def form_messages(surface_id: str) -> list[Message]:
    """Criterion 1: Column, Text, TextField, Button from the basic catalog."""
    return [
        create_surface(surface_id),
        update_components(
            surface_id,
            [
                {
                    "id": "root",
                    "component": "Column",
                    "children": ["title", "status", "name_field", "submit"],
                    "align": "stretch",
                },
                text("title", "## Hello from A2UI 1.0"),
                text("status", "Updates appended: 0"),
                {
                    "id": "name_field",
                    "component": "TextField",
                    "label": "Your name",
                    "value": {"@path": "/name"},
                    "variant": "shortText",
                },
                {
                    "id": "submit",
                    "component": "Button",
                    "child": "submit_label",
                    "variant": "primary",
                    "action": {
                        "event": {
                            "name": "submit_name",
                            "context": {"name": {"@path": "/name"}},
                        }
                    },
                },
                text("submit_label", "Submit"),
            ],
        ),
    ]


st.set_page_config(page_title="streamlit-a2ui M0 spike")
st.title("streamlit-a2ui · M0 spike")
st.caption(
    "Open the browser console to see `[streamlit-a2ui] MessageProcessor "
    "constructed #n` lines (criterion 3)."
)

# --- Criteria 1, 2, 3, 5 ---------------------------------------------------

st.header("1–3, 5 · Form surface")
log: list[Message] = st.session_state.setdefault("a2ui_log", form_messages("form"))
events: list[Message] = st.session_state.setdefault("a2ui_events", [])

event = a2ui_surface(log, key="main")
if event is not None:
    events.append(event)
    action = event.get("action", {})
    name = action.get("context", {}).get("name") or "stranger"
    # Play the agent: answer the action by replacing the status Text.
    log.append(update_components("form", [text("status", f"Agent says hi, {name}!")]))
    st.rerun()

left, right = st.columns(2)
if left.button("Append update (criterion 3)"):
    n = sum(1 for m in log if "updateComponents" in m)
    log.append(update_components("form", [text("status", f"Updates appended: {n}")]))
    st.rerun()
if right.button("Reset log"):
    st.session_state["a2ui_log"] = form_messages("form")
    st.session_state["a2ui_events"] = []
    st.rerun()

st.write(f"Log length: {len(log)}")
st.subheader("Renderer→agent messages received (criterion 2)")
st.json(events[-3:], expanded=True)

# --- Criterion 4 -----------------------------------------------------------

st.header("4 · Streaming")
STREAM_STEPS = 5
mode = st.radio(
    "Mode",
    ["Re-call keyed component in one run", "st.fragment(run_every=...)"],
    horizontal=True,
)


def stream_message(step: int) -> Message:
    if step == 0:
        return create_surface("stream")
    lines = [f"line_{i}" for i in range(1, step + 1)]
    return update_components(
        "stream",
        [
            {"id": "root", "component": "Column", "children": lines},
            *(text(f"line_{i}", f"Streamed line {i}") for i in range(1, step + 1)),
        ],
    )


if mode.startswith("Re-call"):
    stream_log: list[Message] = st.session_state.setdefault("stream_log", [])
    slot = st.empty()
    if st.button("Stream in this run"):
        stream_log.clear()
        for step in range(STREAM_STEPS + 1):
            stream_log.append(stream_message(step))
            with slot.container():
                a2ui_surface(stream_log, key="stream")
            time.sleep(0.5)
    else:
        with slot.container():
            a2ui_surface(stream_log, key="stream")
else:
    st.session_state.setdefault("frag_log", [])

    @st.fragment(run_every=0.5)
    def stream_fragment() -> None:
        frag_log: list[Message] = st.session_state["frag_log"]
        if len(frag_log) <= STREAM_STEPS:
            frag_log.append(stream_message(len(frag_log)))
        a2ui_surface(frag_log, key="frag")
        st.caption(f"Fragment log length: {len(frag_log)}")

    if st.button("Restart fragment stream"):
        st.session_state["frag_log"] = []
    stream_fragment()
