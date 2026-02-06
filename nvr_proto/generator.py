import json
import random
from pathlib import Path

PATTERNS_PATH = Path(__file__).with_name("patterns.json")
FAMILIES = ["SEQUENCE", "ODD_ONE_OUT", "MATRIX"]

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def apply_rotation(value, step):
    return (value + step) % 360


def _option_from_rotation(schema, rotation):
    return {
        "shape": schema["shape"],
        "rotation": rotation,
        "reflect": "none",
        "fill": "outline",
    }


def _cell(rotation):
    return {
        "shape": "triangle",
        "rotation": rotation,
    }


def _rotation_key(option):
    if "ref_index" in option:
        return ("ref", option["ref_index"])
    return (
        option.get("shape"),
        option.get("rotation"),
        option.get("reflect"),
        option.get("fill"),
    )


def _unique_options(options):
    seen = set()
    for option in options:
        key = _rotation_key(option)
        if key in seen:
            return False
        seen.add(key)
    return True


def _exactly_one_correct(options, correct_rotation):
    matches = [opt for opt in options if opt.get("rotation") == correct_rotation]
    return len(matches) == 1


def validate_question(question):
    assert len(question["options"]) == 4
    assert 0 <= question["correct_index"] <= 3
    assert _unique_options(question["options"])

    family = question["pattern_family"]
    if family == "SEQUENCE":
        rotations = [item["rotation"] for item in question["stem"]["items"]]
        step = (rotations[1] - rotations[0]) % 360
        correct_rotation = apply_rotation(rotations[-1], step)
        assert _exactly_one_correct(question["options"], correct_rotation)
    elif family == "ODD_ONE_OUT":
        stem_items = question["stem"]["items"]
        odd_rotation = stem_items[question["correct_index"]]["rotation"]
        matches = 0
        for option in question["options"]:
            ref_index = option["ref_index"]
            if stem_items[ref_index]["rotation"] == odd_rotation:
                matches += 1
        assert matches == 1
    elif family == "MATRIX":
        matrix_items = question["stem"].get("cells") or question["stem"]["items"]
        missing_row = None
        missing_col = None
        for r_index, row in enumerate(matrix_items):
            for c_index, cell in enumerate(row):
                if cell is None:
                    missing_row = r_index
                    missing_col = c_index
                    break
            if missing_row is not None:
                break
        assert missing_row is not None
        row_vals = [
            cell["rotation"]
            for cell in matrix_items[missing_row]
            if cell is not None
        ]
        step = (row_vals[1] - row_vals[0]) % 360
        row_based = apply_rotation(row_vals[-1], step)

        col_vals = []
        for row in matrix_items:
            if row[missing_col] is not None:
                col_vals.append(row[missing_col]["rotation"])
        col_step = 0
        if len(col_vals) >= 2:
            col_step = (col_vals[1] - col_vals[0]) % 360
        column_based = apply_rotation(col_vals[0], -col_step) if col_vals else row_based

        if row_based != column_based:
            assert False, "Matrix rules disagree"
        assert _exactly_one_correct(question["options"], row_based)
    else:
        raise AssertionError(f"Unknown pattern_family: {family}")


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
    patterns_by_type = {}
    for schema in patterns:
        patterns_by_type.setdefault(schema["question_type"], []).append(schema)

    for _ in range(20):
        qtype = random.choice(FAMILIES)

        if qtype == "SEQUENCE":
            schema = random.choice(patterns_by_type[qtype])
            question = _sequence(schema)
        elif qtype == "ODD_ONE_OUT":
            schema = random.choice(patterns_by_type[qtype])
            question = _odd_one_out(schema)
        elif qtype == "MATRIX":
            question = generate_matrix_question()
        else:
            raise ValueError(f"Unsupported question_type: {qtype}")

        if question is None:
            continue

        try:
            validate_question(question)
        except AssertionError:
            continue

        return question

    raise RuntimeError("Failed to generate a valid question after multiple attempts.")


# -------------------------------------------------
# QUESTION BUILDERS (UI CONTRACT)
# -------------------------------------------------

def _sequence(schema):
    start = schema["start_values"]
    step = schema["transformations"][0]["step"]

    correct_value = apply_rotation(start[-1], step)

    wrong_step = apply_rotation(correct_value, 180)
    wrong_direction = apply_rotation(start[-1], -step)
    repeat_last = start[-1]

    candidate_rotations = [wrong_step, wrong_direction, repeat_last]
    fallback_rotations = [
        apply_rotation(start[-1], step * 2),
        apply_rotation(start[-1], -step * 2),
        apply_rotation(start[-1], step * 3),
    ]

    distractors = []
    used = {correct_value}
    for rotation in candidate_rotations + fallback_rotations:
        if rotation in used:
            continue
        distractors.append(rotation)
        used.add(rotation)
        if len(distractors) == 3:
            break

    if len(distractors) != 3:
        return None

    options_rotations = [correct_value] + distractors
    options = [_option_from_rotation(schema, rot) for rot in options_rotations]
    correct_index = 0

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
        "options": options,
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

    if values.count(schema["odd_value"]) != 1:
        return None

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

    row_step = rule["step"]
    row_based = apply_rotation(schema["matrix_template"][0][1], row_step)

    col_vals = []
    for row in schema["matrix_template"]:
        if row[2] is not None:
            col_vals.append(row[2])
    col_step = 0
    if len(col_vals) >= 2:
        col_step = (col_vals[1] - col_vals[0]) % 360
    column_based = apply_rotation(col_vals[0], -col_step) if col_vals else row_based

    if row_based != column_based:
        return None

    return None


def generate_matrix_question():
    """
    Generate a 3x3 MATRIX question with one missing cell.
    Rule: rotation across rows (+90° clockwise).
    """
    # base rotations for first row
    row0 = [0, 90, None]
    row1 = [270, 180, 270]
    row2 = [0, 270, 0]

    cells = [
        [_cell(0), _cell(90), None],
        [_cell(270), _cell(180), _cell(270)],
        [_cell(0), _cell(270), _cell(0)],
    ]

    # correct answer for missing cell
    correct = _cell(180)

    # distractors (Step 3 compliant)
    d_row_only = _cell(0)          # row-only distractor
    d_col_only = _cell(90)         # column rule ok, row wrong
    d_near_miss = _cell(270)       # looks right, violates both subtly

    options = [correct, d_row_only, d_col_only, d_near_miss]
    correct_index = 0

    random.shuffle(options)
    correct_index = options.index(correct)

    return {
        "pattern_family": "MATRIX",
        "stem": {
            "type": "matrix",
            "grid_size": [3, 3],
            "cells": cells,
            "missing_cell": [0, 2],
        },
        "options": options,
        "correct_index": correct_index,
        "difficulty": "easy",
        "explanation": "The shape rotates 90° clockwise across each row.",
    }
