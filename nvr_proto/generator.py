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
