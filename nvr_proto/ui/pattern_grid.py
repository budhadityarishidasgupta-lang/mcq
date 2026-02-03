import streamlit as st

TILE_SIZE = 96
ICON_SIZE = 48

def render_pattern_tile(p, idx):
    col = st.container()

    with col:
        # 1. Render SVG (visual only)
        st.markdown(
            f"""
            <div style="
                width:{TILE_SIZE}px;
                height:{TILE_SIZE}px;
                border-radius:16px;
                border:1px solid rgba(255,255,255,0.25);
                display:flex;
                align-items:center;
                justify-content:center;
                margin-bottom:6px;
            ">
              <svg width="{ICON_SIZE}" height="{ICON_SIZE}" viewBox="0 0 48 48">
                <g transform="translate(24,24) rotate({p['rotation']}) translate(-24,-24)">
                  {shape_svg(p['shape'], p.get('fill','outline'))}
                </g>
              </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Real Streamlit button (click logic)
        clicked = st.button(
            "Select",
            key=f"pattern_btn_{idx}",
            use_container_width=True,
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
    return f'<polygon points="24,6 42,40 6,40" {style}/>'
