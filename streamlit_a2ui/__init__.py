"""Render A2UI 1.0 surfaces inside Streamlit apps."""

from __future__ import annotations

import json
from collections.abc import Sequence
from functools import cache
from importlib.resources import files
from typing import TYPE_CHECKING, Any

import streamlit as st

if TYPE_CHECKING:
    from streamlit.components.v2.types import ComponentRenderer

__all__ = ["a2ui_surface", "renderer_capabilities"]


@cache
def _component() -> ComponentRenderer:
    """Register the component on first use.

    Streamlit resolves ``asset_dir`` from installed manifests only once its
    runtime has started, so registering at import time would make this
    package unimportable outside ``streamlit run`` (for example in an agent
    process that only needs :func:`renderer_capabilities`).
    """
    return st.components.v2.component(
        "streamlit-a2ui.a2ui_surface",
        js="index-*.js",
        css="index-*.css",
        html='<div class="a2ui-host"></div>',
        isolate_styles=True,
    )


def _ignore() -> None:
    """Trigger callback. The value is read from the return value instead."""


def renderer_capabilities() -> dict[str, Any]:
    """Return the A2UI capabilities of this renderer.

    Pass the result to your agent (for example as A2A metadata) so it knows
    which protocol versions and catalogs the surface can render. The content
    is generated from ``@a2ui/web_core`` when the frontend is built: protocol
    ``1.0`` and the basic catalog, with no inline catalogs.

    Returns
    -------
    dict
        A fresh copy on every call, shaped like the 1.0
        ``renderer_capabilities.json`` schema, for example
        ``{"1.0": {"supportedCatalogIds": ["https://a2ui.org/..."]}}``.
    """
    resource = files(__package__).joinpath("renderer_capabilities.json")
    try:
        text = resource.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            "renderer_capabilities.json is missing; build the frontend with "
            "`npm run build` in streamlit_a2ui/frontend"
        ) from None
    capabilities: dict[str, Any] = json.loads(text)
    return capabilities


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
    result = _component()(
        key=key,
        data={"messages": list(messages)},
        on_renderer_message_change=_ignore,
    )
    value = result.get("renderer_message")
    return value if isinstance(value, dict) else None
