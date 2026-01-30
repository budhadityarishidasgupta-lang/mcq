import streamlit as st
from render_svg import main

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

# --- SESSION STATE ---
if "question" not in st.session_state:
    st.session_state.question = main()

question = st.session_state.question

# =========================================================
# STRUCTURE MATCH
# =========================================================
if question["type"] == "structure_match":
    st.subheader("Which option belongs with the group on the left?")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("**Examples**")
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.image(f"example_{i}.svg")

    with right:
        st.markdown("**Options**")
        letters = ["a", "b", "c", "d"]
        for i in range(4):
            st.image(f"opt_{letters[i]}.svg")
            if st.button(f"Option {letters[i].upper()}", key=f"opt_{i}"):
                st.session_state.selected = i

# =========================================================
# SEQUENCE
# =========================================================
elif question["type"] == "sequence":
    st.subheader("Which option comes next?")
    st.image("stem.svg")

    letters = ["a", "b", "c", "d"]
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            st.image(f"opt_{letters[i]}.svg")
            if st.button(f"Option {letters[i].upper()}", key=f"opt_{i}"):
                st.session_state.selected = i

# =========================================================
# ODD ONE OUT
# =========================================================
elif question["type"] == "odd_one_out":
    st.subheader("Which option is different?")
    letters = ["a", "b", "c", "d"]
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            st.image(f"opt_{letters[i]}.svg")
            if st.button(f"Option {letters[i].upper()}", key=f"opt_{i}"):
                st.session_state.selected = i

# =========================================================
# HIDDEN SHAPE
# =========================================================
elif question["type"] == "hidden_shape":
    st.subheader("In which option is the shape on the left hidden?")

    left, right = st.columns([1, 2])

    with left:
        st.markdown("**Target shape**")
        st.image("target.svg")

    with right:
        st.markdown("**Options**")
        letters = ["a", "b", "c", "d"]
        for i in range(4):
            st.image(f"opt_{letters[i]}.svg")
            if st.button(f"Option {letters[i].upper()}", key=f"opt_{i}"):
                st.session_state.selected = i


# =========================================================
# MATRIX / COMPLETE THE SQUARE
# =========================================================
elif question["type"] == "matrix":
    st.subheader("Which option completes the square?")

    st.image("matrix.svg")

    st.markdown("**Options**")
    letters = ["a", "b", "c", "d"]
    cols = st.columns(4)

    for i, col in enumerate(cols):
        with col:
            st.image(f"opt_{letters[i]}.svg")
            if st.button(f"Option {letters[i].upper()}", key=f"opt_{i}"):
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
