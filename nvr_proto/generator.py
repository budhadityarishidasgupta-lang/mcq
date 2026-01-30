def generate_sequence_question():
    """
    Very simple NVR question:
    A triangle rotates 90 degrees each time.
    We ask: which option comes next?
    """

    sequence = [0, 90, 180]   # rotations shown
    options = [0, 90, 180, 270]  # answer choices

    correct_rotation = 270
    correct_index = options.index(correct_rotation)

    return {
        "shape": "triangle",
        "sequence": sequence,
        "options": options,
        "correct_index": correct_index
    }
