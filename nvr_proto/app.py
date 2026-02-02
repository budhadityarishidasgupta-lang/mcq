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

# --- SESSION STATE ---
if "current_question" not in st.session_state:
    pattern = random.choice(load_patterns())
    st.session_state.current_question = generate_from_pattern(pattern)

question = st.session_state.current_question
svg = render_question_svg(question)
components.html(svg, height=280)

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

cols = st.columns(4)
for i, opt in enumerate(["A", "B", "C", "D"]):
    if cols[i].button(opt):
        st.session_state.selected_option = opt

if st.session_state.selected_option and st.session_state.last_result is None:
    if st.button("Submit"):
        st.session_state.last_result = (
            st.session_state.selected_option == question["correct"]
        )

if st.session_state.last_result is not None:
    if st.session_state.last_result:
        st.success("Correct!")
    else:
        st.error("Incorrect")

    if st.button("Next Question"):
        del st.session_state.current_question
        del st.session_state.selected_option
        del st.session_state.last_result
        st.rerun()
