# nvr_proto/app.py
import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_question
from nvr_proto.render_svg import render_question_svg


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Pattern Reasoning")

init_nvr_tables()

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.6rem; max-width: 980px; }
      iframe { border: none; }
      .option-row button{
        height: 3.8rem;
        font-size: 1.2rem;
        border-radius: 14px;
      }
      .submit-row button{
        height: 4.2rem;
        font-size: 1.3rem;
        font-weight: 700;
        border-radius: 16px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Sidebar identity
# -----------------------------
email = st.sidebar.text_input("Email")
if not email:
    st.stop()

# -----------------------------
# Helpers
# -----------------------------
def extract_explanation(q: dict) -> str:
    for key in ("explanation", "reason", "rule", "logic", "hint"):
        if q.get(key):
            return q[key]
    return "Apply the same rule shown in the question."


def new_question() -> dict:
    return normalize_question(generate_question())
    
def normalize_question(q: dict) -> dict:
    """
    Accepts BOTH schemas:
    - Canonical: {"question_type","prompt","options","correct_index",...}
    - Legacy:   {"type","shape", ...}
    Returns canonical.
    """
    if not isinstance(q, dict):
        return {}

    # already canonical
    if "question_type" in q and "prompt" in q and "options" in q and "correct_index" in q:
        return q

    # legacy
    if "type" not in q:
        return {}

    t = q.get("type")
    shape = q.get("shape", "triangle")
    options = q.get("options", [])
    correct_index = q.get("correct_index", None)
    explanation = q.get("explanation", "Apply the same rule shown in the question.")

    if t == "sequence":
        prompt = {"shape": shape, "sequence": q.get("sequence", [])}
        return {
            "pattern_id": q.get("pattern_id", "legacy-sequence"),
            "question_type": "SEQUENCE",
            "prompt": prompt,
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "explanation": explanation,
        }

    if t == "odd_one_out":
        prompt = {"shape": shape}
        return {
            "pattern_id": q.get("pattern_id", "legacy-odd"),
            "question_type": "ODD_ONE_OUT",
            "prompt": prompt,
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "explanation": explanation,
        }

    if t == "matrix":
        prompt = {"shape": shape, "matrix": q.get("matrix", [])}
        return {
            "pattern_id": q.get("pattern_id", "legacy-matrix"),
            "question_type": "MATRIX",
            "prompt": prompt,
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "explanation": explanation,
        }

    if t == "structure_match":
        # renderer shows a generic stem; prompt holds legacy payload
        return {
            "pattern_id": q.get("pattern_id", "legacy-structure"),
            "question_type": "STRUCTURE_MATCH",
            "prompt": q,  # keep full legacy object
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "explanation": explanation,
        }

    if t == "hidden_shape":
        return {
            "pattern_id": q.get("pattern_id", "legacy-hidden"),
            "question_type": "HIDDEN_SHAPE",
            "prompt": {"target": q.get("target", [])},
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "explanation": explanation,
        }

    return {}

# -----------------------------
# Session state
# -----------------------------
if "question" not in st.session_state:
    st.session_state.question = new_question()

if "selected" not in st.session_state:
    st.session_state.selected = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

question = st.session_state.question


# -----------------------------
# SAFETY GUARD
# -----------------------------
if (
    not isinstance(question, dict)
    or "question_type" not in question
    or "options" not in question
    or "correct_index" not in question
):
    st.error(
        f"Invalid question schema from generator. "
        f"Keys received: {list((question or {}).keys())}"
    )
    st.stop()

if len(question["options"]) != 4:
    st.error(f"Expected 4 options, got {len(question['options'])}")
    st.stop()

labels = ["A", "B", "C", "D"]

# -----------------------------
# 1) Render QUESTION prompt (SVG only)
# -----------------------------
prompt_svg = render_question_svg(
    question,
    selected_option=None,
    show_options=False,  # IMPORTANT: options are NOT inside SVG
)

components.html(prompt_svg, height=420)

st.markdown("### Choose the correct option")

# -----------------------------
# 2) Option buttons (no auto-submit)
# -----------------------------
cols = st.columns(4)
for i, col in enumerate(cols):
    with col:
        is_sel = (st.session_state.selected == i)
        label = f"✅ {labels[i]}" if is_sel else labels[i]
        if st.button(
            label,
            key=f"opt_{i}",
            use_container_width=True,
            disabled=st.session_state.submitted,
        ):
            st.session_state.selected = i
            st.rerun()

# -----------------------------
# 3) Submit
# -----------------------------
st.markdown('<div class="submit-row">', unsafe_allow_html=True)
if st.button(
    "Submit",
    type="primary",
    use_container_width=True,
    disabled=(st.session_state.selected is None or st.session_state.submitted),
):
    st.session_state.submitted = True
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 4) Feedback + next
# -----------------------------
if st.session_state.submitted:
    correct = int(question["correct_index"])
    if st.session_state.selected == correct:
        st.success("✅ Correct")
    else:
        st.error("❌ Incorrect")

    st.info(extract_explanation(question))

    if st.button("Next Question ▶️", use_container_width=True):
        st.session_state.question = new_question()
        st.session_state.selected = None
        st.session_state.submitted = False
        st.rerun()
