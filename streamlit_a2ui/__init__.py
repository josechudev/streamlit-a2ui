"""Render A2UI 1.0 surfaces inside Streamlit apps."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import streamlit as st

__all__ = ["a2ui_surface"]

_component = st.components.v2.component(
    "streamlit-a2ui.a2ui_surface",
    js="index-*.js",
    css="index-*.css",
    html='<div class="a2ui-host"></div>',
    isolate_styles=True,
)


def _ignore() -> None:
    """Trigger callback. The value is read from the return value instead."""


def a2ui_surface(
    messages: Sequence[dict[str, Any]], *, key: str
) -> dict[str, Any] | None:
    """Render an A2UI message log and return at most one renderer message.

    Parameters
    ----------
    messages
        The full, append-only log of agent-to-renderer A2UI 1.0 messages.
        Pass the whole log on every call; the frontend processes only the
        entries it has not seen yet.
    key
        Stable key for this surface instance. The frontend keeps its message
        processor for as long as the key stays mounted.

    Returns
    -------
    dict or None
        The renderer-to-agent message produced since the last rerun (for
        example ``{"version": "1.0", "action": {...}}``), or ``None``.
    """
    result = _component(
        key=key,
        data={"messages": list(messages)},
        on_renderer_message_change=_ignore,
    )
    value = result.get("renderer_message")
    return value if isinstance(value, dict) else None
