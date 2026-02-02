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
