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
        .option-grid {
            margin-top: 1rem;
        }
        .option-grid div[data-testid="stButton"] > button {
            padding: 1.6rem 1rem;
            border-radius: 14px;
            border: 2px solid #1f2937;
            font-size: 1.4rem;
            font-weight: 600;
            min-height: 96px;
            transition: all 0.15s ease-in-out;
        }
        .option-grid div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
            background-color: #1f6feb;
            border: 3px solid #58a6ff;
            color: #ffffff;
            font-weight: 700;
        }
        .option-grid div[data-testid="stButton"] > button[data-testid="baseButton-secondary"] {
            background-color: #f8fafc;
        }
        .option-grid div[data-testid="stButton"] > button:hover {
            border-color: #2563eb;
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


def normalize_question(q):
    if "correct_option" in q:
        correct_option = q["correct_option"]
    elif "correct" in q:
        correct_option = q["correct"]
    elif "answer" in q:
        correct_option = q["answer"]
    elif "solution" in q:
        correct_option = q["solution"]
    elif "correct_index" in q:
        option_map = ["A", "B", "C", "D"]
        correct_option = option_map[q["correct_index"]]
    else:
        st.error(
            "Unable to determine correct option. Available keys: "
            f"{sorted(q.keys())}"
        )
        st.stop()

    return {**q, "correct_option": correct_option}


def extract_explanation(q):
    for key in ("explanation", "reason", "rule", "logic", "hint"):
        if q.get(key):
            return q[key]
    return "Explanation not available yet for this pattern."


# --- SESSION STATE ---
if "current_question" not in st.session_state:
    pattern = random.choice(load_patterns())
    st.session_state.current_question = generate_from_pattern(pattern)

question = normalize_question(st.session_state.current_question)
svg = render_question_svg(question)

with st.container():
    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        st.markdown('<div class="question-block">', unsafe_allow_html=True)
        if question.get("prompt"):
            st.markdown(
                f"<div class='prompt-text'>{question['prompt']}</div>",
                unsafe_allow_html=True,
            )
        components.html(svg, height=420)
        st.markdown("</div>", unsafe_allow_html=True)

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

options = ["A", "B", "C", "D"]
st.markdown('<div class="option-grid">', unsafe_allow_html=True)
for row in range(2):
    cols = st.columns(2)
    for col_index, col in enumerate(cols):
        opt_index = row * 2 + col_index
        opt = options[opt_index]
        is_selected = st.session_state.selected_option == opt
        button_type = "primary" if is_selected else "secondary"
        if col.button(
            opt,
            key=f"opt_{opt}",
            type=button_type,
            use_container_width=True,
        ):
            st.session_state.selected_option = opt
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.last_result is None:
    st.markdown('<div class="submit-row">', unsafe_allow_html=True)
    if st.button(
        "Submit",
        disabled=st.session_state.selected_option is None,
        key="submit_button",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.last_result = (
            st.session_state.selected_option == question["correct_option"]
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
        del st.session_state.current_question
        del st.session_state.selected_option
        del st.session_state.last_result
        st.rerun()
