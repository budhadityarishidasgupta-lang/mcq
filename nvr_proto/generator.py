import json
import random
from pathlib import Path

PATTERNS_PATH = Path(__file__).with_name("patterns.json")

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def apply_rotation(value, step):
    return (value + step) % 360


def load_patterns():
    with PATTERNS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# -------------------------------------------------
# PUBLIC API (USED BY UI / STREAMLIT)
# -------------------------------------------------

def generate_question():
    """
    Canonical NVR generator output.
    Returns ONLY clickable patterns (no MCQ).
    """

    patterns = load_patterns()
    schema = random.choice(patterns)

    qtype = schema["question_type"]

    if qtype == "SEQUENCE":
        return _sequence(schema)

    if qtype == "ODD_ONE_OUT":
        return _odd_one_out(schema)

    if qtype == "MATRIX":
        return _matrix(schema)

    # fallback (safe)
    raise ValueError(f"Unsupported question_type: {qtype}")


# -------------------------------------------------
# QUESTION BUILDERS (UI CONTRACT)
# -------------------------------------------------

def _sequence(schema):
    start = schema["start_values"][:]
    step = schema["transformations"][0]["step"]

    next_val = apply_rotation(start[-1], step)

    tiles = []
    for v in schema["options"]:
        tiles.append({
            "shape": schema["shape"],
            "rotation": v,
            "reflect": "none",
            "fill": "outline",
            "correct": v == next_val
        })

    random.shuffle(tiles)

    return {
        "question_type": "SEQUENCE",
        "patterns": tiles,
        "explanation": f"The shape rotates by {step}° each step."
    }


def _odd_one_out(schema):
    values = (
        [schema["common_value"]] * 3
        + [schema["odd_value"]]
    )
    random.shuffle(values)

    tiles = []
    for v in values:
        tiles.append({
            "shape": schema["shape"],
            "rotation": v,
            "reflect": "none",
            "fill": "outline",
            "correct": v == schema["odd_value"]
        })

    return {
        "question_type": "ODD_ONE_OUT",
        "patterns": tiles,
        "explanation": "Three patterns follow the same rule. One breaks it."
    }


def _matrix(schema):
    rule = schema["rule"]
    options = schema["options"]

    correct = apply_rotation(
        schema["matrix_template"][0][1],
        rule["step"]
    )

    tiles = []
    for v in options:
        tiles.append({
            "shape": schema["shape"],
            "rotation": v,
            "reflect": "none",
            "fill": "outline",
            "correct": v == correct
        })

    random.shuffle(tiles)

    return {
        "question_type": "MATRIX",
        "patterns": tiles,
        "explanation": f"The shape rotates by {rule['step']}° across the row."
    }
