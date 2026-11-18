"""A form surface, its action returned to Python, and a scripted agent reply.

Run with:  streamlit run examples/basic_app.py

There is no LLM and no network: ``scripted_agent`` stands in for an agent
and answers each action by appending A2UI 1.0 messages to the log. The
payload shapes are adapted from the basic catalog example
``00_simple-login-form.json`` shipped with ``@a2ui/web_core`` 0.15.0
(``src/v1_0/schemas/catalogs/basic/examples/``).
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from streamlit_a2ui import a2ui_surface, renderer_capabilities

Message = dict[str, Any]

BASIC_CATALOG = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"
SURFACE = "contact"


def text(component_id: str, value: str, variant: str | None = None) -> Message:
    component: Message = {"id": component_id, "component": "Text", "text": value}
    if variant:
        component["variant"] = variant
    return component


def update_components(components: list[Message]) -> Message:
    return {
        "version": "1.0",
        "updateComponents": {"surfaceId": SURFACE, "components": components},
    }


def initial_messages() -> list[Message]:
    """What the agent sends first: a surface with a two-field form."""
    return [
        {
            "version": "1.0",
            "createSurface": {"surfaceId": SURFACE, "catalogId": BASIC_CATALOG},
        },
        update_components(
            [
                {
                    "id": "root",
                    "component": "Column",
                    "children": [
                        "title",
                        "name_field",
                        "message_field",
                        "submit_button",
                        "reply",
                    ],
                    "justify": "start",
                    "align": "stretch",
                },
                text("title", "## Contact us"),
                {
                    "id": "name_field",
                    "component": "TextField",
                    "label": "Name",
                    "value": {"@path": "/name"},
                    "variant": "shortText",
                },
                {
                    "id": "message_field",
                    "component": "TextField",
                    "label": "Message",
                    "value": {"@path": "/message"},
                    "variant": "longText",
                },
                {
                    "id": "submit_button",
                    "component": "Button",
                    "child": "submit_label",
                    "variant": "primary",
                    "action": {
                        "event": {
                            "name": "send_message",
                            "context": {
                                "name": {"@path": "/name"},
                                "message": {"@path": "/message"},
                            },
                        }
                    },
                },
                text("submit_label", "Send"),
                text("reply", "The agent's reply will appear here.", "caption"),
            ]
        ),
    ]


def scripted_agent(event: Message) -> list[Message]:
    """Answer a renderer message the way an agent would: with more messages."""
    action = event.get("action")
    if not isinstance(action, dict) or action.get("name") != "send_message":
        return []
    context = action.get("context") or {}
    name = str(context.get("name") or "there").strip()
    length = len(str(context.get("message") or ""))
    return [
        update_components(
            # "body" explicitly: the placeholder was a caption, and the reply should
            # stand out as the agent's answer.
            [
                text(
                    "reply",
                    f"Thanks, {name}! The agent got {length} characters.",
                    "body",
                )
            ]
        )
    ]


st.set_page_config(page_title="streamlit-a2ui · basic")
st.title("streamlit-a2ui · basic")

log: list[Message] = st.session_state.setdefault("a2ui_log", initial_messages())

event = a2ui_surface(log, key="contact")
if event is not None:
    st.session_state["last_event"] = event
    log.extend(scripted_agent(event))
    st.rerun()

st.subheader("Last message returned by `a2ui_surface`")
last_event = st.session_state.get("last_event")
if last_event is None:
    st.caption("None yet. Fill in the form and press Send.")
else:
    st.json(last_event, expanded=True)

with st.expander("Try more"):
    st.write(
        "Type in the form without sending, then use these buttons: what you "
        "typed stays, because the surface is updated in place."
    )
    updates = sum(1 for m in log if "updateComponents" in m)
    if st.button("Agent: append an update"):
        log.append(update_components([text("title", f"## Contact us ({updates})")]))
        st.rerun()
    if st.button("Agent: append an invalid message"):
        # A Text without its required `text`: the renderer rejects this
        # message, shows a notice inside the component, keeps what it already
        # rendered, and returns nothing to Python.
        log.append(update_components([{"id": "title", "component": "Text"}]))
        st.rerun()
    if st.button("Replace the log"):
        st.session_state["a2ui_log"] = initial_messages()
        st.session_state.pop("last_event", None)
        st.rerun()
    st.caption(f"Log length: {len(log)}")
    st.write("Renderer capabilities to send to your agent:")
    st.json(renderer_capabilities())
