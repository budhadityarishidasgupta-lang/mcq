import random
import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_from_pattern, load_patterns
from nvr_proto.render_svg import render_question_svg  # must support show_options True/False

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Pattern Reasoning")

init_nvr_tables()

# -------------------------------------------------
# Global styling
# -------------------------------------------------
st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; }
        iframe { border: none; }
        .submit-row button {
            height: 3.6rem;
            font-size: 1.2rem;
            font-weight: 700;
            border-radius: 14px;
        }
        .option-row button {
            height: 3.4rem;
            font-size: 1.05rem;
            border-radius: 12px;
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

def new_question():
    pattern = random.choice(load_patterns())
    return generate_from_pattern(pattern)

# -------------------------------------------------
# Session bootstrap (IMPORTANT: no auto-submit)
# -------------------------------------------------
if "current_question" not in st.session_state:
    st.session_state.current_question = new_question()

if "selected" not in st.session_state:
    st.session_state.selected = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "last_result" not in st.session_state:
    st.session_state.last_result = None

question = st.session_state.current_question

# -------------------------------------------------
# 1) Render QUESTION PROMPT (NO OPTIONS)
# -------------------------------------------------
# This MUST show the question area (sequence/matrix/etc.)
prompt_svg = render_question_svg(
    question,
    selected_option=None,
    show_options=False,   # <-- key change: prompt only
)

components.html(prompt_svg, height=340)

st.markdown("### Choose the correct answer")

# -------------------------------------------------
# 2) Render ANSWER OPTIONS (A/B/C/D)
# -------------------------------------------------
labels = ["A", "B", "C", "D"]
opt_cols = st.columns(4)

with st.container():
    st.markdown('<div class="option-row">', unsafe_allow_html=True)

    for i, col in enumerate(opt_cols):
        with col:
            # show a clean button; selection highlights via state
            is_selected = (st.session_state.selected == i)

            btn_label = f"{labels[i]}"
            if is_selected:
                btn_label = f"✅ {labels[i]}"

            if st.button(btn_label, key=f"opt_{i}", use_container_width=True):
                st.session_state.selected = i
                # selecting should NOT auto-submit
                st.session_state.submitted = False
                st.session_state.last_result = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 3) Submit (ONLY this sets result)
# -------------------------------------------------
st.markdown('<div class="submit-row">', unsafe_allow_html=True)
if st.button(
    "Submit",
    disabled=(st.session_state.selected is None),
    use_container_width=True,
    type="primary",
):
    st.session_state.submitted = True
    st.session_state.last_result = (
        st.session_state.selected == question["correct_index"]
    )
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 4) Feedback + explanation + next
# -------------------------------------------------
if st.session_state.submitted and st.session_state.last_result is not None:
    if st.session_state.last_result:
        st.success("Correct!")
    else:
        st.error("Incorrect")

    st.info(extract_explanation(question))

    if st.button("Next Question ▶️", use_container_width=True):
        st.session_state.current_question = new_question()
        st.session_state.selected = None
        st.session_state.submitted = False
        st.session_state.last_result = None
        st.rerun()
