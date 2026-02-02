import random

import streamlit as st
import streamlit.components.v1 as components
from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_from_pattern, load_patterns
from nvr_proto.render_svg import render_question_svg

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

init_nvr_tables()

st.markdown(
    """
    <style>
        .question-block {
            max-width: 860px;
            margin: 0 auto 1.5rem auto;
            text-align: center;
            padding: 0.5rem 0 1rem 0;
        }
        .question-block iframe {
            border: none;
        }
        .prompt-text {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        .submit-row {
            margin-top: 0.75rem;
        }
        .submit-row div[data-testid="stButton"] > button {
            padding: 1rem;
            border-radius: 12px;
            font-size: 1.2rem;
        }
        .submit-row div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
            background-color: #0ea5e9;
            border: 2px solid #0284c7;
            color: #ffffff;
            font-weight: 700;
        }
        .feedback-box {
            margin-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

email = st.sidebar.text_input("Email")
st.sidebar.text_input("Name (optional)")
if not email:
    st.stop()


def extract_explanation(q):
    for key in ("explanation", "reason", "rule", "logic", "hint"):
        if q.get(key):
            return q[key]
    return "Explanation not available yet for this pattern."


# --- SESSION STATE ---
if "current_question" not in st.session_state:
    pattern = random.choice(load_patterns())
    st.session_state.current_question = generate_from_pattern(pattern)

question = st.session_state.current_question
if "selected" not in st.session_state:
    st.session_state.selected = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

labels = ["A", "B", "C", "D"]
selected_label = (
    labels[st.session_state.selected]
    if st.session_state.selected is not None
    else None
)
svg = render_question_svg(question, selected_option=selected_label)

with st.container():
    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        st.markdown('<div class="question-block">', unsafe_allow_html=True)
        components.html(svg, height=520)
        st.markdown("</div>", unsafe_allow_html=True)

        button_cols = st.columns(4)
        for idx, label in enumerate(labels):
            button_type = "primary" if st.session_state.selected == idx else "secondary"
            if button_cols[idx].button(
                label,
                key=f"option_{label}",
                type=button_type,
                use_container_width=True,
            ):
                st.session_state.selected = idx
                st.rerun()

if st.session_state.last_result is None:
    st.markdown('<div class="submit-row">', unsafe_allow_html=True)
    if st.button(
        "Submit",
        disabled=st.session_state.selected is None,
        key="submit_button",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.last_result = (
            st.session_state.selected == question["correct_index"]
        )
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.last_result is not None:
    st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
    if st.session_state.last_result:
        st.success("Correct!")
    else:
        st.error("Incorrect")

    st.info(extract_explanation(question))
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Next Question", use_container_width=True):
        for key in ("current_question", "selected", "last_result"):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
