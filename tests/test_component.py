from streamlit.testing.v1 import AppTest


def _app() -> None:
    import streamlit as st

    from streamlit_a2ui import a2ui_surface

    st.session_state["result"] = a2ui_surface([], key="main")


def test_a2ui_surface_returns_none_without_interaction() -> None:
    at = AppTest.from_function(_app, default_timeout=60).run()
    assert not at.exception
    assert at.session_state["result"] is None
