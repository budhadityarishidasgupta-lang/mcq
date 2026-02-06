import json
import random
from pathlib import Path

PATTERNS_PATH = Path(__file__).with_name("patterns.json")
FAMILIES = ["SEQUENCE", "ODD_ONE_OUT", "MATRIX", "ANALOGY", "COMPOSITION"]
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
PATTERN_WEIGHTS = {
    "easy": {
        "SEQUENCE": 4,
        "ODD_ONE_OUT": 3,
        "MATRIX": 2,
        "ANALOGY": 2,
        "COMPOSITION": 1,
    },
    "medium": {
        "SEQUENCE": 3,
        "ODD_ONE_OUT": 2,
        "MATRIX": 3,
        "ANALOGY": 2,
        "COMPOSITION": 2,
    },
    "hard": {
        "SEQUENCE": 2,
        "ODD_ONE_OUT": 2,
        "MATRIX": 3,
        "ANALOGY": 3,
        "COMPOSITION": 3,
    },
}
SUPPORTED_PATTERN_FAMILIES = {
    "SEQUENCE",
    "ODD_ONE_OUT",
    "MATRIX",
    "ANALOGY",
    "COMPOSITION",
}

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
    if option.get("type") == "composite":
        items = option.get("items", [])
        normalized_items = tuple(
            (item.get("shape"), item.get("rotation"))
            for item in items
        )
        return ("composite", normalized_items)
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


def all_options_unique(options):
    return len({str(option) for option in options}) == 4


def _exactly_one_correct(options, correct_rotation):
    matches = [opt for opt in options if opt.get("rotation") == correct_rotation]
    return len(matches) == 1


def _exactly_one_composition_match(options, correct_items):
    correct_key = tuple((item.get("shape"), item.get("rotation")) for item in correct_items)
    matches = 0
    for option in options:
        if option.get("type") != "composite":
            continue
        option_key = tuple((item.get("shape"), item.get("rotation")) for item in option.get("items", []))
        if option_key == correct_key:
            matches += 1
    return matches == 1


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
        odd_item = stem_items[question["correct_index"]]
        odd_signature = (
            odd_item.get("shape"),
            odd_item.get("rotation"),
            odd_item.get("reflect"),
            odd_item.get("fill"),
        )
        matches = 0
        for option in question["options"]:
            ref_index = option["ref_index"]
            item = stem_items[ref_index]
            signature = (
                item.get("shape"),
                item.get("rotation"),
                item.get("reflect"),
                item.get("fill"),
            )
            if signature == odd_signature:
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
    elif family == "ANALOGY":
        stem = question["stem"]
        a_rot = stem["A"]["rotation"]
        b_rot = stem["B"]["rotation"]
        c_rot = stem["C"]["rotation"]
        step = (b_rot - a_rot) % 360
        correct_rotation = apply_rotation(c_rot, step)
        assert _exactly_one_correct(question["options"], correct_rotation)
    elif family == "COMPOSITION":
        stem = question["stem"]
        assert stem.get("operation") == "UNION"
        assert isinstance(stem.get("inputs"), list)
        assert len(stem["inputs"]) == 2
        assert _exactly_one_composition_match(question["options"], stem["inputs"])
    else:
        raise AssertionError(f"Unknown pattern_family: {family}")


def validate_question_quality(question):
    assert len(question["options"]) == 4
    assert 0 <= question["correct_index"] <= 3
    assert len({str(option) for option in question["options"]}) == 4


def load_patterns():
    with PATTERNS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# -------------------------------------------------
# PUBLIC API (USED BY UI / STREAMLIT)
# -------------------------------------------------

def generate_question(difficulty="easy"):
    """
    Canonical NVR generator output.
    Returns ONLY clickable patterns (no MCQ).
    """

    assert difficulty in DIFFICULTY_LEVELS

    patterns = load_patterns()
    patterns_by_type = {}
    for schema in patterns:
        patterns_by_type.setdefault(schema["question_type"], []).append(schema)

    for _ in range(20):
        qtype = choose_pattern_family(difficulty)
        question = generate_question_for_family(
            qtype,
            patterns_by_type=patterns_by_type,
            difficulty=difficulty,
        )

        if question is None:
            continue

        try:
            validate_question_quality(question)
            validate_question(question)
        except AssertionError:
            continue

        assert question["pattern_family"] in SUPPORTED_PATTERN_FAMILIES, (
            f"Unsupported pattern family emitted: {question['pattern_family']}"
        )

        return question

    raise RuntimeError("Failed to generate a valid question after multiple attempts.")


def generate_question_for_family(qtype, patterns_by_type=None, difficulty="easy"):
    assert difficulty in DIFFICULTY_LEVELS

    if qtype == "SEQUENCE":
        if patterns_by_type is None:
            patterns = load_patterns()
            patterns_by_type = {}
            for schema in patterns:
                patterns_by_type.setdefault(schema["question_type"], []).append(schema)
        schema = random.choice(patterns_by_type[qtype])
        question = _sequence(schema, difficulty=difficulty)
    elif qtype == "ODD_ONE_OUT":
        if patterns_by_type is None:
            patterns = load_patterns()
            patterns_by_type = {}
            for schema in patterns:
                patterns_by_type.setdefault(schema["question_type"], []).append(schema)
        schema = random.choice(patterns_by_type[qtype])
        question = _odd_one_out(schema, difficulty=difficulty)
    elif qtype == "MATRIX":
        question = generate_matrix_question(difficulty=difficulty)
    elif qtype == "ANALOGY":
        question = generate_analogy_question(difficulty=difficulty)
    elif qtype == "COMPOSITION":
        question = generate_composition_question(difficulty=difficulty)
    else:
        raise ValueError(f"Unsupported question_type: {qtype}")

    if question is not None:
        validate_question_quality(question)
        assert question["pattern_family"] in SUPPORTED_PATTERN_FAMILIES, (
            f"Unsupported pattern family emitted: {question['pattern_family']}"
        )

    return question


def dev_smoke_test():
    families = ["SEQUENCE", "ODD_ONE_OUT", "MATRIX", "ANALOGY", "COMPOSITION"]
    patterns = load_patterns()
    patterns_by_type = {}
    for schema in patterns:
        patterns_by_type.setdefault(schema["question_type"], []).append(schema)

    for family in families:
        question = generate_question_for_family(family, patterns_by_type, difficulty="easy")
        assert question is not None
        assert question["pattern_family"] == family


def generate_question_for_mix(allowed_families, difficulty="easy"):
    weights = PATTERN_WEIGHTS[difficulty]
    families = [family for family in allowed_families if family in weights]
    if not families:
        families = allowed_families
    probs = [weights.get(family, 1) for family in families]
    family = random.choices(families, weights=probs, k=1)[0]
    return generate_question_for_family(family, difficulty=difficulty)


def choose_pattern_family(difficulty):
    weights = PATTERN_WEIGHTS[difficulty]
    families = list(weights.keys())
    probs = list(weights.values())
    return random.choices(families, weights=probs, k=1)[0]


# -------------------------------------------------
# QUESTION BUILDERS (UI CONTRACT)
# -------------------------------------------------

def _sequence(schema, difficulty="easy"):
    start = schema["start_values"]
    if difficulty == "easy":
        step = 90
        distractor_order = ["wrong_direction", "repeat_last", "wrong_step"]
    elif difficulty == "medium":
        step = 90
        distractor_order = ["wrong_direction", "near_miss", "repeat_last"]
    else:
        step = 45
        distractor_order = ["wrong_direction", "near_miss", "wrong_step"]

    correct_value = apply_rotation(start[-1], step)

    distractor_pool = {
        "wrong_direction": apply_rotation(start[-1], -step),
        "repeat_last": start[-1],
        "wrong_step": apply_rotation(start[-1], step * 2),
        "near_miss": apply_rotation(correct_value, -45),
    }

    candidate_rotations = [distractor_pool[name] for name in distractor_order]
    fallback_rotations = [
        apply_rotation(correct_value, 45),
        apply_rotation(correct_value, 135),
        apply_rotation(correct_value, 180),
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
        "difficulty": difficulty,
        "explanation": f"The shape rotates by {step}° each step."
    }


def _odd_one_out(schema, difficulty="easy"):
    if difficulty == "easy":
        invariant = "rotation"
        common = {"rotation": 90, "fill": "outline"}
        odd = {"rotation": 180, "fill": "outline"}
    elif difficulty == "medium":
        invariant = "fill"
        common = {"rotation": 90, "fill": "outline"}
        odd = {"rotation": 90, "fill": "solid"}
    else:
        invariant = "parity"
        common = {"rotation": 0, "fill": "outline"}
        odd = {"rotation": 45, "fill": "outline"}

    stem_items = [
        {"shape": schema["shape"], "reflect": "none", **common}
        for _ in range(3)
    ]
    stem_items.append({"shape": schema["shape"], "reflect": "none", **odd})
    random.shuffle(stem_items)

    correct_index = stem_items.index(next(item for item in stem_items if item["fill"] == odd["fill"] and item["rotation"] == odd["rotation"]))

    return {
        "pattern_family": "ODD_ONE_OUT",
        "stem": {
            "type": "odd_one_out",
            "items": stem_items,
        },
        "options": [{"ref_index": i} for i in range(4)],
        "correct_index": correct_index,
        "difficulty": difficulty,
        "explanation": f"Three patterns share one invariant ({invariant}). One breaks it."
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


def generate_matrix_question(difficulty="easy"):
    """
    Generate a 3x3 MATRIX question with one missing cell.
    Rule: rotation across rows (+90° clockwise).
    """
    assert difficulty in DIFFICULTY_LEVELS

    if difficulty == "easy":
        rules = ["row_only"]
        cells = [
            [_cell(0), _cell(90), None],
            [_cell(90), _cell(180), _cell(270)],
            [_cell(180), _cell(270), _cell(0)],
        ]
        correct = _cell(180)
        distractors = [_cell(270), _cell(90), _cell(0)]
        explanation = "The shape rotates 90° clockwise across each row."
    elif difficulty == "medium":
        rules = ["row", "column"]
        cells = [
            [_cell(0), _cell(90), None],
            [_cell(270), _cell(180), _cell(270)],
            [_cell(0), _cell(270), _cell(0)],
        ]
        correct = _cell(180)
        distractors = [_cell(0), _cell(90), _cell(315)]
        explanation = "Use both row and column rotation rules to find the missing cell."
    else:
        rules = ["row", "column"]
        cells = [
            [_cell(0), _cell(90), None],
            [_cell(270), _cell(180), _cell(270)],
            [_cell(0), _cell(270), _cell(0)],
        ]
        correct = _cell(180)
        distractors = [_cell(135), _cell(225), _cell(270)]
        explanation = "Both row and column rules apply; distractors are near-miss rotations."

    options = [correct] + distractors
    if not all_options_unique(options):
        return None

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
        "difficulty": difficulty,
        "explanation": explanation,
        "rules": rules,
    }


def generate_analogy_question(difficulty="easy"):
    """
    A : B :: C : ?
    Rule: rotate +90° clockwise
    """
    if difficulty == "easy":
        transformation = "rotate_90"
        A = {"shape": "triangle", "rotation": 0}
        B = {"shape": "triangle", "rotation": 90}
        C = {"shape": "triangle", "rotation": 180}
        correct = {"shape": "triangle", "rotation": 270}
        distractors = [
            {"shape": "triangle", "rotation": 90},
            {"shape": "triangle", "rotation": 180},
            {"shape": "triangle", "rotation": 0},
        ]
    elif difficulty == "medium":
        transformation = "rotate_90"
        A = {"shape": "triangle", "rotation": 45}
        B = {"shape": "triangle", "rotation": 135}
        C = {"shape": "triangle", "rotation": 225}
        correct = {"shape": "triangle", "rotation": 315}
        distractors = [
            {"shape": "triangle", "rotation": 135},
            {"shape": "triangle", "rotation": 270},
            {"shape": "triangle", "rotation": 225},
        ]
    else:
        transformation = "rotate_45"
        A = {"shape": "triangle", "rotation": 0}
        B = {"shape": "triangle", "rotation": 45}
        C = {"shape": "triangle", "rotation": 180}
        correct = {"shape": "triangle", "rotation": 225}
        distractors = [
            {"shape": "triangle", "rotation": 180},
            {"shape": "triangle", "rotation": 135},
            {"shape": "triangle", "rotation": 270},
        ]

    options = [correct] + distractors
    random.shuffle(options)
    correct_index = options.index(correct)

    return {
        "pattern_family": "ANALOGY",
        "stem": {
            "type": "analogy",
            "A": A,
            "B": B,
            "C": C,
            "missing": True,
        },
        "options": options,
        "correct_index": correct_index,
        "difficulty": difficulty,
        "explanation": f"Apply the same transformation ({transformation}) from A→B and C→?.",
    }


def generate_composition_question(difficulty="easy"):
    """
    Composition rule: UNION (overlay) of two inputs.
    """
    A = {"shape": "triangle", "rotation": 0}
    B = {"shape": "triangle", "rotation": 180}

    correct = {
        "type": "composite",
        "items": [A, B],
    }

    if difficulty == "easy":
        distractors = [
            {"type": "composite", "items": [A]},
            {"type": "composite", "items": [B]},
            {"type": "composite", "items": [{"shape": "triangle", "rotation": 90}, B]},
        ]
    elif difficulty == "medium":
        distractors = [
            {"type": "composite", "items": [A]},
            {"type": "composite", "items": [A, B, {"shape": "triangle", "rotation": 90}]},
            {"type": "composite", "items": [{"shape": "triangle", "rotation": 0}, {"shape": "triangle", "rotation": 90}]},
        ]
    else:
        distractors = [
            {"type": "composite", "items": [{"shape": "triangle", "rotation": 0}, {"shape": "triangle", "rotation": 135}]},
            {"type": "composite", "items": [A, B, {"shape": "triangle", "rotation": 45}]},
            {"type": "composite", "items": [{"shape": "triangle", "rotation": 45}, B]},
        ]

    options = [correct] + distractors
    random.shuffle(options)
    correct_index = options.index(correct)

    return {
        "pattern_family": "COMPOSITION",
        "stem": {
            "type": "composition",
            "operation": "UNION",
            "inputs": [A, B],
        },
        "options": options,
        "correct_index": correct_index,
        "difficulty": difficulty,
        "explanation": "The answer is the visual union (overlay) of both shapes.",
    }
