from streamlit.testing.v1 import AppTest

from streamlit_a2ui import renderer_capabilities

BASIC_CATALOG = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"


def _app() -> None:
    import streamlit as st

    from streamlit_a2ui import a2ui_surface

    st.session_state["result"] = a2ui_surface([], key="main")


def test_a2ui_surface_returns_none_without_interaction() -> None:
    at = AppTest.from_function(_app, default_timeout=60).run()
    assert not at.exception
    assert at.session_state["result"] is None


def test_renderer_capabilities_names_1_0_and_the_basic_catalog() -> None:
    capabilities = renderer_capabilities()
    assert isinstance(capabilities, dict)
    assert list(capabilities) == ["1.0"]
    assert capabilities["1.0"]["supportedCatalogIds"] == [BASIC_CATALOG]
    assert "inlineCatalogs" not in capabilities["1.0"]


def test_renderer_capabilities_returns_a_fresh_copy() -> None:
    renderer_capabilities()["1.0"]["supportedCatalogIds"].append("mutated")
    assert renderer_capabilities()["1.0"]["supportedCatalogIds"] == [BASIC_CATALOG]
