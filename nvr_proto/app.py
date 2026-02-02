import random

import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_from_pattern, load_patterns
from nvr_proto.render_svg import render_question_svg

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

init_nvr_tables()

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
        if question.get("prompt"):
            st.markdown(f"**{question['prompt']}**")
        components.html(svg, height=280)

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

cols = st.columns(4)
for i, opt in enumerate(["A", "B", "C", "D"]):
    if cols[i].button(opt, use_container_width=True):
        st.session_state.selected_option = opt

if st.session_state.last_result is None:
    if st.button(
        "Submit",
        disabled=st.session_state.selected_option is None,
        use_container_width=True,
    ):
        st.session_state.last_result = (
            st.session_state.selected_option == question["correct_option"]
        )

if st.session_state.last_result is not None:
    if st.session_state.last_result:
        st.success("Correct!")
    else:
        st.error("Incorrect")

    st.info(extract_explanation(question))

    if st.button("Next Question", use_container_width=True):
        del st.session_state.current_question
        del st.session_state.selected_option
        del st.session_state.last_result
        st.rerun()
