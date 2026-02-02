from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_COMPONENT_PATH = Path(__file__).parent / "svg_options_frontend"
_svg_options = components.declare_component(
    "svg_options",
    path=str(_COMPONENT_PATH),
)


def svg_options(svg_html: str, height: int = 420) -> str | None:
    return _svg_options(svg_html=svg_html, height=height)
