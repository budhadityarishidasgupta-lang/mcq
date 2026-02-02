import random
import time

import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_from_pattern, load_patterns
from nvr_proto.render_svg import render_question_svg
from nvr_proto.repository.progress_repo import (
    get_or_create_user,
    get_unlocked_level,
    record_attempt,
)

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

init_nvr_tables()

email = st.sidebar.text_input("Email")
name = st.sidebar.text_input("Name (optional)")
if not email:
    st.stop()
user_id = get_or_create_user(
    email=email.strip().lower(),
    name=name.strip() if name else None,
)

# --- SESSION STATE ---
def _select_pattern(user_id_value):
    patterns = load_patterns()
    unlocked_by_family = {}
    for pattern in patterns:
        family = pattern["family"]
        if family not in unlocked_by_family:
            unlocked_by_family[family] = get_unlocked_level(user_id_value, family)
    eligible = [
        pattern
        for pattern in patterns
        if pattern["level"] <= unlocked_by_family[pattern["family"]]
    ]
    if not eligible:
        eligible = patterns
    return random.choice(eligible)


def _ensure_question():
    if "question" not in st.session_state or "pattern" not in st.session_state:
        pattern = _select_pattern(user_id)
        st.session_state.pattern = pattern
        st.session_state.question = generate_from_pattern(pattern)
        st.session_state.q_start = time.time()
        st.session_state.attempt_recorded = False


_ensure_question()

question = st.session_state.question
pattern = st.session_state.pattern

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
    is_correct = st.session_state.selected == question["correct_index"]
    if is_correct:
        st.success("✅ Correct!")
    else:
        st.error("❌ Not quite. Try again.")
    st.markdown("**Why?**")
    st.info(question["explanation"])
    if not st.session_state.get("attempt_recorded"):
        duration_ms = int((time.time() - st.session_state.q_start) * 1000)
        record_attempt(
            user_id=user_id,
            pattern_id=question["pattern_id"],
            family=pattern["family"],
            level=int(pattern["level"]),
            is_correct=is_correct,
            duration_ms=duration_ms,
        )
        st.session_state.attempt_recorded = True

# =========================================================
# NEXT QUESTION
# =========================================================
st.markdown("---")
if st.button("Next Question ▶️"):
    st.session_state.clear()
    st.rerun()
