import streamlit as st

def render_pattern_tile(p, idx):
    size = 96
    icon = 48

    svg = f"""
    <svg width="{icon}" height="{icon}" viewBox="0 0 48 48">
      <g transform="translate(24,24) rotate({p['rotation']}) translate(-24,-24)">
        {shape_svg(p['shape'], p.get('fill', 'outline'))}
      </g>
    </svg>
    """

    clicked = st.button(
        svg,
        key=f"pattern_{idx}",
        use_container_width=False,
    )

    return clicked, p["correct"]


def shape_svg(shape, fill):
    style = (
        'fill="none" stroke="white" stroke-width="3"'
        if fill == "outline"
        else 'fill="white"'
    )

    if shape == "square":
        return f'<rect x="10" y="10" width="28" height="28" {style}/>'
    if shape == "circle":
        return f'<circle cx="24" cy="24" r="14" {style}/>'
    if shape == "arrow":
        return f'<polygon points="10,24 30,10 30,18 38,18 38,30 30,30 30,38" {style}/>'
    return f'<polygon points="24,6 42,40 6,40" {style}/>'  # triangle
