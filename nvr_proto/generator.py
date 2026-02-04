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
    start = schema["start_values"]
    step = schema["transformations"][0]["step"]

    correct_value = apply_rotation(start[-1], step)

    options = schema["options"][:]
    random.shuffle(options)

    correct_index = options.index(correct_value)

    visible_items = [
        {
            "shape": schema["shape"],
            "rotation": v,
            "reflect": "none",
            "fill": "outline",
        }
        for v in start
    ]

    return {
        "pattern_family": "SEQUENCE",
        "stem": {
            "type": "sequence",
            "direction": "left_to_right",
            "items": visible_items,
            "missing_position": "end",
        },
        "options": [
            {
                "shape": schema["shape"],
                "rotation": v,
                "reflect": "none",
                "fill": "outline",
            }
            for v in options
        ],
        "correct_index": correct_index,
        "difficulty": "easy",
        "explanation": f"The shape rotates by {step}° each step."
    }


def _odd_one_out(schema):
    values = (
        [schema["common_value"]] * 3
        + [schema["odd_value"]]
    )
    random.shuffle(values)

    correct_index = values.index(schema["odd_value"])

    stem_items = [
        {
            "shape": schema["shape"],
            "rotation": v,
            "reflect": "none",
            "fill": "outline",
        }
        for v in values
    ]

    return {
        "pattern_family": "ODD_ONE_OUT",
        "stem": {
            "type": "odd_one_out",
            "items": stem_items,
        },
        "options": [{"ref_index": i} for i in range(4)],
        "correct_index": correct_index,
        "difficulty": "easy",
        "explanation": "Three patterns follow the same rule. One breaks it."
    }


def _matrix(schema):
    rule = schema["rule"]

    correct_value = apply_rotation(
        schema["matrix_template"][0][1],
        rule["step"]
    )

    options = schema["options"][:]
    random.shuffle(options)

    correct_index = options.index(correct_value)

    matrix_items = []
    for row in schema["matrix_template"]:
        matrix_row = []
        for cell in row:
            if cell is None:
                matrix_row.append(None)
            else:
                matrix_row.append(
                    {
                        "shape": schema["shape"],
                        "rotation": cell,
                        "reflect": "none",
                        "fill": "outline",
                    }
                )
        matrix_items.append(matrix_row)

    return {
        "pattern_family": "MATRIX",
        "stem": {
            "type": "matrix",
            "items": matrix_items,
        },
        "options": [
            {
                "shape": schema["shape"],
                "rotation": v,
                "reflect": "none",
                "fill": "outline",
            }
            for v in options
        ],
        "correct_index": correct_index,
        "difficulty": "easy",
        "explanation": f"The shape rotates by {rule['step']}° across the row."
    }
