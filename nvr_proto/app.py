import random

import streamlit as st
import streamlit.components.v1 as components

from nvr_proto.db import init_nvr_tables
from nvr_proto.generator import generate_from_pattern, load_patterns
from nvr_proto.render_svg import render_question_svg

st.set_page_config(page_title="NVR Prototype", layout="centered")
st.title("🧠 NVR Prototype – Auto Generated Question")

init_nvr_tables()

st.markdown(
    """
    <style>
        .question-block {
            max-width: 860px;
            margin: 0 auto 1.5rem auto;
            text-align: center;
            padding: 0.5rem 0 1rem 0;
        }
        .question-block iframe {
            border: none;
        }
        .prompt-text {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        .submit-row {
            margin-top: 0.75rem;
        }
        .submit-row div[data-testid="stButton"] > button {
            padding: 1rem;
            border-radius: 12px;
            font-size: 1.2rem;
        }
        .submit-row div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
            background-color: #0ea5e9;
            border: 2px solid #0284c7;
            color: #ffffff;
            font-weight: 700;
        }
        .feedback-box {
            margin-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

email = st.sidebar.text_input("Email")
st.sidebar.text_input("Name (optional)")
if not email:
    st.stop()


def normalize_question(q):
    if "correct_option" in q:
        correct_option = q["correct_option"]
    elif "correct" in q:
        correct_option = q["correct"]
    elif "answer" in q:
        correct_option = q["answer"]
    elif "solution" in q:
        correct_option = q["solution"]
    elif "correct_index" in q:
        option_map = ["A", "B", "C", "D"]
        correct_option = option_map[q["correct_index"]]
    else:
        st.error(
            "Unable to determine correct option. Available keys: "
            f"{sorted(q.keys())}"
        )
        st.stop()

    return {**q, "correct_option": correct_option}


def extract_explanation(q):
    for key in ("explanation", "reason", "rule", "logic", "hint"):
        if q.get(key):
            return q[key]
    return "Explanation not available yet for this pattern."


# --- SESSION STATE ---
if "current_question" not in st.session_state:
    pattern = random.choice(load_patterns())
    st.session_state.current_question = generate_from_pattern(pattern)

question = normalize_question(st.session_state.current_question)
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

svg = render_question_svg(question, selected_option=st.session_state.selected_option)
svg_component = f"""
<div id="svg-container" style="width: 100%;">
  {svg}
</div>
<style>
  #svg-container svg {{
    width: 100%;
    height: auto;
  }}
  #svg-container .option-card {{
    cursor: pointer;
  }}
  #svg-container .option-card rect {{
    transition: stroke 0.15s ease, fill 0.15s ease;
  }}
  #svg-container .option-card.selected rect {{
    stroke: #58a6ff;
    stroke-width: 4;
    fill: #1f2937;
  }}
</style>
<script>
  const streamlit = window.parent.Streamlit;
  const root = document.getElementById("svg-container");
  const optionLetters = ["A", "B", "C", "D"];

  const clearSelection = () => {{
    root.querySelectorAll(".option-card").forEach((node) => {{
      node.classList.remove("selected");
    }});
  }};

  const setSelection = (letter) => {{
    clearSelection();
    const selected = root.querySelector(`#option-${{letter}}`);
    if (selected) {{
      selected.classList.add("selected");
    }}
  }};

  optionLetters.forEach((letter) => {{
    const el = root.querySelector(`#option-${{letter}}`);
    if (!el) {{
      return;
    }}
    el.addEventListener("click", () => {{
      setSelection(letter);
      if (streamlit) {{
        streamlit.setComponentValue(letter);
      }}
    }});
  }});

  if (streamlit) {{
    streamlit.setComponentReady();
    streamlit.setFrameHeight(420);
  }}
</script>
"""

with st.container():
    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        st.markdown('<div class="question-block">', unsafe_allow_html=True)
        if question.get("prompt"):
            st.markdown(
                f"<div class='prompt-text'>{question['prompt']}</div>",
                unsafe_allow_html=True,
            )
        selected = components.html(svg_component, height=420, key="svg-options")
        st.markdown("</div>", unsafe_allow_html=True)
        if selected and selected != st.session_state.selected_option:
            st.session_state.selected_option = selected
            st.rerun()

if st.session_state.last_result is None:
    st.markdown('<div class="submit-row">', unsafe_allow_html=True)
    if st.button(
        "Submit",
        disabled=st.session_state.selected_option is None,
        key="submit_button",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.last_result = (
            st.session_state.selected_option == question["correct_option"]
        )
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.last_result is not None:
    st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
    if st.session_state.last_result:
        st.success("Correct!")
    else:
        st.error("Incorrect")

    st.info(extract_explanation(question))
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Next Question", use_container_width=True):
        del st.session_state.current_question
        del st.session_state.selected_option
        del st.session_state.last_result
        st.rerun()
