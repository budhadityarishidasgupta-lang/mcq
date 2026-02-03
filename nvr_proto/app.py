import random
import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.generator import generate_question
from nvr_proto.ui.pattern_grid import render_pattern_tile

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_from_pattern, load_patterns
from nvr_proto.render_svg import render_question_svg

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

init_nvr_tables()

# -------------------------------------------------
# Global spacing + button styling
# -------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
        }
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0.5rem;
        }
        iframe {
            border: none;
        }
        .option-row button {
            height: 4.5rem;
            font-size: 1.4rem;
            border-radius: 14px;
        }
        .submit-row button {
            height: 4.5rem;
            font-size: 1.5rem;
            font-weight: 700;
            border-radius: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Sidebar identity
# -------------------------------------------------
email = st.sidebar.text_input("Email")
st.sidebar.text_input("Name (optional)")
if not email:
    st.stop()

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def extract_explanation(q):
    for key in ("explanation", "reason", "rule", "logic", "hint"):
        if q.get(key):
            return q[key]
    return "Explanation not available yet for this pattern."

# -------------------------------------------------
# Session bootstrap
# -------------------------------------------------
if "current_question" not in st.session_state:
    pattern = random.choice(load_patterns())
    st.session_state.current_question = generate_from_pattern(pattern)

if "selected" not in st.session_state:
    st.session_state.selected = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

question = st.session_state.current_question

# -------------------------------------------------
# Render QUESTION WITH OPTIONS in SVG
# -------------------------------------------------
labels = ["A", "B", "C", "D"]
selected_label = (
    labels[st.session_state.selected]
    if st.session_state.selected is not None
    else None
)
svg = render_question_svg(
    question,
    selected_option=selected_label,
    show_options=True,
)

_, center_col, _ = st.columns([1, 3, 1])
with center_col:
    components.html(svg, height=460)

# -------------------------------------------------
# Invisible click map for SVG options
# -------------------------------------------------
st.markdown(
    """
    <style>
    div[data-testid="stButton"] > button {
        background: transparent;
        border: none;
        height: 140px;
        margin-top: -160px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

click_cols = st.columns(4)
for i, col in enumerate(click_cols):
    with col:
        if st.button(
            labels[i],
            key=f"svg_opt_{i}",
            use_container_width=True,
        ):
            st.session_state.selected = i
            st.rerun()

# -------------------------------------------------
# Submit
# -------------------------------------------------
st.markdown('<div class="submit-row">', unsafe_allow_html=True)
if st.button(
    "Submit",
    disabled=st.session_state.selected is None,
    use_container_width=True,
    type="primary",
):
    st.session_state.last_result = (
        st.session_state.selected == question["correct_index"]
    )
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Feedback + explanation + next
# -------------------------------------------------
if st.session_state.last_result is not None:
    if st.session_state.last_result:
        st.success("Correct!")
    else:
        st.error("Incorrect")

    st.info(extract_explanation(question))

    if st.button("Next Question ▶️", use_container_width=True):
        for k in ("current_question", "selected", "last_result"):
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
