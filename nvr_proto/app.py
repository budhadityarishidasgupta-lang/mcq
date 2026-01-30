import streamlit as st
from render_svg import main

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

# --- SESSION STATE ---
if "question" not in st.session_state:
    st.session_state.question = main()

question = st.session_state.question

# --- QUESTION TEXT ---
if question["type"] == "sequence":
    st.subheader("Which option comes next?")
    st.image("stem.svg")

elif question["type"] == "odd_one_out":
    st.subheader("Which option is different?")

# --- OPTIONS ---
st.subheader("Options")

letters = ["a", "b", "c", "d"]
cols = st.columns(4)

selected = None

for i, col in enumerate(cols):
    with col:
        st.image(f"opt_{letters[i]}.svg")
        if st.button(f"Option {letters[i].upper()}", key=f"opt_{i}"):
            selected = i

# --- FEEDBACK ---
if selected is not None:
    if selected == question["correct_index"]:
        st.success("✅ Correct!")
    else:
        st.error("❌ Not quite. Try again.")

# --- NEXT QUESTION ---
st.markdown("---")

if st.button("Next Question ▶️"):
    st.session_state.question = main()
    st.experimental_rerun()
