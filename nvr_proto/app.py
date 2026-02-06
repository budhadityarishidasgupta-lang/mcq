# nvr_proto/app.py
import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_question
from nvr_proto.render_svg import render_question_svg, render_option_svg

CURRENT_DIFFICULTY = "easy"


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="NVR Practice", layout="centered")
st.title("🧠 NVR Prototype – Pattern Reasoning")

init_nvr_tables()

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.6rem; max-width: 980px; }
      iframe { border: none; }
      .stem-zone {
        margin-bottom: 2.8rem;
      }
      .options-zone {
        margin-bottom: 2.8rem;
      }
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
    return normalize_question(generate_question(difficulty=CURRENT_DIFFICULTY))


def normalize_question(q: dict) -> dict:
    """
    Accepts BOTH schemas:
    - Canonical: {"pattern_family","stem","options","correct_index",...}
    - Legacy:   {"question_type","prompt","options","correct_index",...}
    Returns canonical.
    """
    if not isinstance(q, dict):
        return {}

    # already canonical
    if "pattern_family" in q and "stem" in q and "options" in q and "correct_index" in q:
        return q

    # legacy canonical
    if "question_type" in q and "prompt" in q and "options" in q and "correct_index" in q:
        pattern_family = q["question_type"]
        prompt = q.get("prompt") or {}
        stem = {"type": pattern_family.lower()}
        if isinstance(prompt, dict):
            stem.update(prompt)
        return {
            "pattern_family": pattern_family,
            "stem": stem,
            "options": q.get("options", []),
            "correct_index": int(q.get("correct_index", 0)),
            "difficulty": q.get("difficulty", "easy"),
            "explanation": q.get("explanation", "Apply the same rule shown in the question."),
        }

    # legacy
    if "type" not in q:
        return {}

    t = q.get("type")
    shape = q.get("shape", "triangle")
    options = q.get("options", [])
    correct_index = q.get("correct_index", None)
    explanation = q.get("explanation", "Apply the same rule shown in the question.")

    if t == "sequence":
        stem = {"type": "sequence", "shape": shape, "sequence": q.get("sequence", [])}
        return {
            "pattern_family": "SEQUENCE",
            "stem": stem,
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "difficulty": "easy",
            "explanation": explanation,
        }

    if t == "odd_one_out":
        stem = {"type": "odd_one_out", "shape": shape}
        return {
            "pattern_family": "ODD_ONE_OUT",
            "stem": stem,
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "difficulty": "easy",
            "explanation": explanation,
        }

    if t == "matrix":
        stem = {"type": "matrix", "shape": shape, "matrix": q.get("matrix", [])}
        return {
            "pattern_family": "MATRIX",
            "stem": stem,
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "difficulty": "easy",
            "explanation": explanation,
        }

    if t == "structure_match":
        return {
            "pattern_family": "ANALOGY",
            "stem": {"type": "structure_match", **q},
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "difficulty": "easy",
            "explanation": explanation,
        }

    if t == "hidden_shape":
        return {
            "pattern_family": "COMPOSITION",
            "stem": {"type": "hidden_shape", "target": q.get("target", [])},
            "options": options,
            "correct_index": int(correct_index) if correct_index is not None else 0,
            "difficulty": "easy",
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
    or "pattern_family" not in question
    or "stem" not in question
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

stem_svg = render_question_svg(
    question,
    selected_option=None,
    show_options=False,
)

# ===============================
# STEM SECTION
# ===============================
with st.container():
    st.markdown("## Question")
    components.html(
        stem_svg,
        height=240,
    )

st.markdown("---")

# ===============================
# OPTIONS SECTION
# ===============================
with st.container():
    st.markdown("## Choose the correct option")

    cols = st.columns(2)

    for i, opt in enumerate(question["options"]):
        with cols[i % 2]:
            is_selected = (st.session_state.selected == i)

            option_svg = render_option_svg(
                opt,
                question["pattern_family"],
            )

            border = "3px solid #22c55e" if is_selected else "2px solid #e5e7eb"
            bg = "rgba(34,197,94,0.08)" if is_selected else "rgba(255,255,255,0.02)"
            label = (
                "<div style='font-size:12px;color:#22c55e;text-align:center;'>Selected</div>"
                if is_selected else ""
            )

            components.html(
                f"""
                <div style="
                    border: {border};
                    border-radius: 12px;
                    padding: 10px;
                    height: 190px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    background: {bg};
                    transition: border 0.15s ease;
                ">
                    {option_svg}
                    {label}
                </div>
                """,
                height=210,
            )

            if st.button(
                f"Select {['A','B','C','D'][i]}",
                key=f"select_opt_{i}",
                use_container_width=True,
                disabled=st.session_state.submitted,
            ):
                st.session_state.selected = i
                st.rerun()

st.markdown("---")

submit_disabled = (
    st.session_state.selected is None
    or st.session_state.submitted
)

if st.button(
    "Submit",
    disabled=submit_disabled,
    use_container_width=True,
):
    st.session_state.submitted = True

if st.session_state.selected is None:
    st.caption("Select one option to continue.")

# -----------------------------
# 4) Feedback + next
# -----------------------------
if st.session_state.submitted:
    st.markdown("---")
    with st.container():
        if st.session_state.selected == question["correct_index"]:
            st.success("Correct ✅")
        else:
            st.error("Not quite ❌")

        st.caption(question["explanation"])

    if st.button("Next Question", use_container_width=True):
        st.session_state.question = new_question()
        st.session_state.selected = None
        st.session_state.submitted = False
        st.rerun()
