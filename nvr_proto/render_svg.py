import random
import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables



# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Pattern Reasoning")

init_nvr_tables()

# -------------------------------------------------
# Global styles
# -------------------------------------------------
st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; }
        iframe { border: none; }
        .option-btn button {
            height: 4.2rem;
            font-size: 1.4rem;
            border-radius: 14px;
        }
        .submit-btn button {
            height: 4.6rem;
            font-size: 1.5rem;
            font-weight: 700;
            border-radius: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Sidebar identity (minimal)
# -------------------------------------------------
email = st.sidebar.text_input("Email")
if not email:
    st.stop()

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def extract_explanation(q: dict) -> str:
    for key in ("explanation", "reason", "rule", "logic", "hint"):
        if q.get(key):
            return q[key]
    return "Apply the same rule shown in the question."

# -------------------------------------------------
# Session bootstrap
# -------------------------------------------------
if "question" not in st.session_state:
    pattern = random.choice(load_patterns())
    st.session_state.question = generate_from_pattern(pattern)

if "selected" not in st.session_state:
    st.session_state.selected = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

question = st.session_state.question

# -------------------------------------------------
# SAFETY GUARD
# -------------------------------------------------
if not question or "question_type" not in question:
    st.error("Invalid question schema")
    st.stop()

# -------------------------------------------------
# Render QUESTION (SVG — VISUAL ONLY)
# -------------------------------------------------
labels = ["A", "B", "C", "D"]

selected_label = (
    labels[st.session_state.selected]
    if st.session_state.selected is not None
    else None
)

svg = render_question_svg(
    question,
    selected_option=selected_label,
    show_options=False,  # IMPORTANT: options handled by Streamlit, not SVG
)

_, center_col, _ = st.columns([1, 4, 1])
with center_col:
    components.html(svg, height=440)

# -------------------------------------------------
# Option buttons (ONLY interaction layer)
# -------------------------------------------------
st.markdown("### Click the correct pattern")

cols = st.columns(4)
for i, col in enumerate(cols):
    with col:
        if st.button(
            labels[i],
            key=f"opt_{i}",
            use_container_width=True,
            disabled=st.session_state.submitted,
        ):
            st.session_state.selected = i

# -------------------------------------------------
# Submit
# -------------------------------------------------
st.markdown('<div class="submit-btn">', unsafe_allow_html=True)
if st.button(
    "Submit",
    use_container_width=True,
    disabled=st.session_state.selected is None or st.session_state.submitted,
    type="primary",
):
    st.session_state.submitted = True
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Feedback
# -------------------------------------------------
if st.session_state.submitted:
    correct = question["correct_index"]

    if st.session_state.selected == correct:
        st.success("✅ Correct")
    else:
        st.error("❌ Incorrect")

    st.info(extract_explanation(question))

    if st.button("Next Question ▶️", use_container_width=True):
        for k in ("question", "selected", "submitted"):
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
