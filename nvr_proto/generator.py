import random


def generate_sequence_question():
    sequence = [0, 90, 180]
    options = [0, 90, 180, 270]
    correct_rotation = 270
    correct_index = options.index(correct_rotation)

    return {
        "type": "sequence",
        "shape": "triangle",
        "sequence": sequence,
        "options": options,
        "correct_index": correct_index,
        "explanation": "The triangle rotates by 90° each time. The next shape must follow the same rotation."
    }


def generate_odd_one_out_question():
    """
    Three triangles point up (0°),
    one points down (180°)
    """

    options = [0, 0, 0, 180]
    random.shuffle(options)
    correct_index = options.index(180)

    return {
        "type": "odd_one_out",
        "shape": "triangle",
        "options": options,
        "correct_index": correct_index,
        "explanation": "Three triangles point up, but one points down. The odd one out is the one facing the opposite way."
    }


def generate_question():
    return random.choice([
        generate_sequence_question(),
        generate_odd_one_out_question(),
        generate_structure_match_question(),
        generate_hidden_shape_question(),
        generate_matrix_question()
    ])


def generate_structure_match_question():
    """
    Structure Match:
    Circle -> Square -> Circle
    """

    structure = {
        "nodes": [
            {"id": 1, "type": "circle"},
            {"id": 2, "type": "square"},
            {"id": 3, "type": "circle"},
        ],
        "edges": [
            (1, 2),
            (2, 3),
        ]
    }

    # Correct option follows same structure
    correct_structure = structure

    # Wrong options (break one rule each)
    wrong_structures = [
        # wrong middle
        {
            "nodes": [
                {"id": 1, "type": "circle"},
                {"id": 2, "type": "circle"},
                {"id": 3, "type": "square"},
            ],
            "edges": [(1, 2), (2, 3)]
        },
        # missing node
        {
            "nodes": [
                {"id": 1, "type": "circle"},
                {"id": 2, "type": "square"},
            ],
            "edges": [(1, 2)]
        },
        # extra node
        {
            "nodes": [
                {"id": 1, "type": "circle"},
                {"id": 2, "type": "square"},
                {"id": 3, "type": "circle"},
                {"id": 4, "type": "triangle"},
            ],
            "edges": [(1, 2), (2, 3), (3, 4)]
        }
    ]

    options = [correct_structure] + wrong_structures
    random.shuffle(options)

    correct_index = options.index(correct_structure)

    return {
        "type": "structure_match",
        "examples": [structure, structure, structure],
        "options": options,
        "correct_index": correct_index,
        "explanation": "The correct option keeps the same structure: a square connected between two circles."
    }

def generate_hidden_shape_question():
    """
    Hidden Shape:
    Target is an L-shape made of 2 lines
    """

    # Target shape definition (relative coordinates)
    target_shape = [
        ((0, 0), (40, 0)),   # horizontal line
        ((0, 0), (0, 40)),   # vertical line
    ]

    # Correct container includes target exactly
    correct_container = {
        "lines": target_shape + [
            ((40, 0), (40, 40)),
            ((0, 40), (40, 40)),
        ]
    }

    # Wrong containers (almost but not exact)
    wrong_containers = [
        # Missing one line
        {
            "lines": [
                ((0, 0), (40, 0)),
                ((40, 0), (40, 40)),
            ]
        },
        # Rotated target (doesn't match)
        {
            "lines": [
                ((0, 0), (0, 40)),
                ((0, 40), (40, 40)),
            ]
        },
        # Extra misleading lines but missing target
        {
            "lines": [
                ((10, 0), (10, 40)),
                ((0, 10), (40, 10)),
            ]
        }
    ]

    options = [correct_container] + wrong_containers
    random.shuffle(options)

    correct_index = options.index(correct_container)

    return {
        "type": "hidden_shape",
        "target": target_shape,
        "options": options,
        "correct_index": correct_index,
        "explanation": "The correct option contains all the lines of the target L-shape in the same arrangement."
    }
def generate_matrix_question():
    """
    Matrix / Complete the square
    Rule: rotate triangle by 90 degrees across the row
    """

    # Matrix values (rotations)
    matrix = [
        [0, 90, None],
        [0, 90, 180],
        [0, 90, 180],
    ]

    correct_value = 180

    # Options (rotations)
    options = [180, 0, 90, 270]
    correct_index = options.index(correct_value)

    return {
        "type": "matrix",
        "matrix": matrix,
        "options": options,
        "correct_index": correct_index,
        "explanation": "Across each row, the triangle rotates by 90°. The missing square must follow the same rotation."
    }
