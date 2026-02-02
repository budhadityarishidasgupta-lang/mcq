import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.generator import generate_question
from nvr_proto.render_svg import render_question_svg

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

# --- SESSION STATE ---
if "question" not in st.session_state:
    st.session_state.question = generate_question()

question = st.session_state.question

svg = render_question_svg(question)
components.html(svg, height=280)

letters = ["A", "B", "C", "D"]
cols = st.columns(4)
for i, col in enumerate(cols):
    with col:
        if st.button(f"Option {letters[i]}", key=f"opt_{i}"):
            st.session_state.selected = i



# =========================================================
# FEEDBACK
# =========================================================
if "selected" in st.session_state:
    if st.session_state.selected == question["correct_index"]:
        st.success("✅ Correct!")
    else:
        st.error("❌ Not quite. Try again.")
    st.markdown("**Why?**")
    st.info(question["explanation"])

# =========================================================
# NEXT QUESTION
# =========================================================
st.markdown("---")
if st.button("Next Question ▶️"):
    st.session_state.clear()
    st.rerun()
