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
        "correct_index": correct_index
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
        "correct_index": correct_index
    }


def generate_question():
    """
    Randomly choose question type
    """
    return random.choice([
        generate_sequence_question(),
        generate_odd_one_out_question()
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
        "correct_index": correct_index
    }

