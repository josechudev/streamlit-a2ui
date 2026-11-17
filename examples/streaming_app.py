"""Streaming across reruns: a fragment repaints while a scripted stream fills the log.

Run with:  streamlit run examples/streaming_app.py

A keyed component can be called once per script run, so a surface cannot be
repainted in the middle of a run (ADR-007). Instead the component sits inside
``@st.fragment(run_every=...)``: each tick moves whatever the agent's stream
has produced into the log and re-renders the fragment.

The "agent" is a generator with no LLM and no network. Its messages are
adapted from the basic catalog example ``31_incremental-dashboard.json``
shipped with ``@a2ui/web_core`` 0.15.0
(``src/v1_0/schemas/catalogs/basic/examples/``).

A trigger fired by a component inside a fragment reruns only that fragment,
so the returned message is visible only inside it. The action is therefore
handled inside the fragment, and ``st.rerun(scope="app")`` is used when the
rest of the page has to change (see docs/notes-m1.md).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import streamlit as st

from streamlit_a2ui import a2ui_surface

Message = dict[str, Any]

BASIC_CATALOG = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"
SURFACE = "dashboard"
TICK_SECONDS = 0.5
LOG_LINES = [
    "System boot complete.",
    "Connected to the job queue.",
    "Loaded 3 workers.",
    "Worker 1 healthy.",
    "Worker 2 healthy.",
    "Worker 3 healthy.",
    "All services healthy.",
    "Waiting for user input.",
]


def update_components(components: list[Message]) -> Message:
    return {
        "version": "1.0",
        "updateComponents": {"surfaceId": SURFACE, "components": components},
    }


def update_data(path: str, value: Any) -> Message:
    return {
        "version": "1.0",
        "updateDataModel": {"surfaceId": SURFACE, "path": path, "value": value},
    }


def text(component_id: str, value: Any, variant: str | None = None) -> Message:
    component: Message = {"id": component_id, "component": "Text", "text": value}
    if variant:
        component["variant"] = variant
    return component


def scripted_stream() -> Iterator[Message]:
    """One A2UI message per step, as an agent's stream would deliver them."""
    yield {
        "version": "1.0",
        "createSurface": {"surfaceId": SURFACE, "catalogId": BASIC_CATALOG},
    }
    yield update_data("/", {"logs": [], "lineCount": 0})
    yield update_components(
        [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "ack_row", "content_grid"],
                "align": "stretch",
            },
            text("header", "## System dashboard"),
            {
                "id": "ack_row",
                "component": "Row",
                "children": ["ack_button", "ack_status"],
                "align": "center",
            },
            {
                "id": "ack_button",
                "component": "Button",
                "child": "ack_label",
                "variant": "primary",
                "action": {
                    "event": {
                        "name": "acknowledge",
                        "context": {"linesSeen": {"@path": "/lineCount"}},
                    }
                },
            },
            text("ack_label", "Acknowledge"),
            text("ack_status", "Not acknowledged yet.", "caption"),
            {
                "id": "content_grid",
                "component": "Row",
                "children": ["left_panel", "right_panel"],
            },
            {
                "id": "left_panel",
                "component": "Column",
                "children": ["panel_a_loading"],
                "weight": 1,
            },
            {
                "id": "right_panel",
                "component": "Column",
                "children": ["panel_b_loading"],
                "weight": 1,
            },
            text("panel_a_loading", "Loading analytics...", "caption"),
            text("panel_b_loading", "Loading logs...", "caption"),
        ]
    )
    yield update_components(
        [
            {
                "id": "left_panel",
                "component": "Column",
                "children": ["analytics_card"],
                "weight": 1,
            },
            {"id": "analytics_card", "component": "Card", "child": "analytics_text"},
            text("analytics_text", "Analytics are ready.", "body"),
        ]
    )
    yield update_components(
        [
            {
                "id": "right_panel",
                "component": "Column",
                "children": ["logs_list"],
                "weight": 1,
            },
            {
                "id": "logs_list",
                "component": "List",
                "children": {"path": "/logs", "componentId": "log_template"},
            },
            text("log_template", {"@path": "message"}, "caption"),
        ]
    )
    for index, line in enumerate(LOG_LINES):
        yield update_data(f"/logs/{index}", {"message": line})
        yield update_data("/lineCount", index + 1)
    yield update_components([text("header", "## System dashboard (stream complete)")])


def scripted_reply(event: Message) -> list[Message]:
    """The agent's answer to an action: replace the status text."""
    action = event.get("action")
    if not isinstance(action, dict) or action.get("name") != "acknowledge":
        return []
    seen = (action.get("context") or {}).get("linesSeen", 0)
    return [
        update_components(
            [text("ack_status", f"Acknowledged after {seen} log lines.", "caption")]
        )
    ]


def start_stream() -> None:
    st.session_state["log"] = []
    st.session_state["stream"] = scripted_stream()
    st.session_state["streaming"] = True
    st.session_state["events"] = []


st.set_page_config(page_title="streamlit-a2ui · streaming")
st.title("streamlit-a2ui · streaming")

if "stream" not in st.session_state:
    start_stream()

if st.button("Restart the stream"):
    start_stream()

streaming: bool = st.session_state["streaming"]


# The timer runs only while the stream has messages left. A full app rerun
# re-evaluates the decorator, which is how the timer is switched off.
@st.fragment(run_every=TICK_SECONDS if streaming else None)
def dashboard() -> None:
    log: list[Message] = st.session_state["log"]
    stream: Iterator[Message] = st.session_state["stream"]

    if st.session_state["streaming"]:
        message = next(stream, None)
        if message is None:
            st.session_state["streaming"] = False
            st.rerun(scope="app")  # switches the timer off
        else:
            log.append(message)

    event = a2ui_surface(log, key="dashboard")
    if event is not None:
        # Only this fragment reran, so the event must be handled here.
        st.session_state["events"].append(event)
        log.extend(scripted_reply(event))
        st.rerun(scope="fragment")

    events: list[Message] = st.session_state["events"]
    st.caption(
        f"Log length: {len(log)} · "
        f"{'streaming' if st.session_state['streaming'] else 'stream finished'} · "
        f"actions received: {len(events)}"
    )
    if events:
        st.json(events[-1], expanded=True)


dashboard()
