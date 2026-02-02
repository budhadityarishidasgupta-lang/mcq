import random
import streamlit as st
import streamlit.components.v1 as components

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
# Render QUESTION ONLY (no options in SVG)
# -------------------------------------------------
svg = render_question_svg(question, show_options=False)

_, center_col, _ = st.columns([1, 3, 1])
with center_col:
    components.html(svg, height=460)

# -------------------------------------------------
# Option selection — tight 2×2 grid
# -------------------------------------------------
labels = ["A", "B", "C", "D"]

row1 = st.columns(2, gap="small")
row2 = st.columns(2, gap="small")

option_cols = row1 + row2

for idx, col in enumerate(option_cols):
    is_selected = st.session_state.selected == idx
    with col:
        if st.button(
            labels[idx],
            key=f"opt_{idx}",
            type="primary" if is_selected else "secondary",
            use_container_width=True,
        ):
            st.session_state.selected = idx
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
