import streamlit as st
from nvr_proto.generator import generate_question
from nvr_proto.ui.pattern_grid import render_pattern_tile
from nvr_proto.db import init_nvr_tables

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Pattern Reasoning")

init_nvr_tables()

# -------------------------------------------------
# Sidebar identity (kept minimal)
# -------------------------------------------------
email = st.sidebar.text_input("Email")
if not email:
    st.stop()

# -------------------------------------------------
# Session bootstrap
# -------------------------------------------------
if "question" not in st.session_state:
    st.session_state.question = generate_question()
    st.session_state.answered = False
    st.session_state.result = None

q = st.session_state.question

# -------------------------------------------------
# Question header
# -------------------------------------------------
st.subheader("Click the correct pattern")

# -------------------------------------------------
# Pattern grid (CLICKABLE)
# -------------------------------------------------
cols = st.columns(4)

for idx, pattern in enumerate(q["patterns"]):
    with cols[idx % 4]:
        clicked, is_correct = render_pattern_tile(pattern, idx)

        if clicked and not st.session_state.answered:
            st.session_state.answered = True
            st.session_state.result = is_correct
            st.rerun()

# -------------------------------------------------
# Feedback
# -------------------------------------------------
if st.session_state.answered:
    if st.session_state.result:
        st.success("Correct ✓")
    else:
        st.error("Incorrect ✕")

    if q.get("explanation"):
        st.info(q["explanation"])

    if st.button("Next Question ▶️", use_container_width=True):
        for k in ("question", "answered", "result"):
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
