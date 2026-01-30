import math
import svgwrite
from generator import generate_sequence_question


def draw_triangle(dwg, center_x, center_y, size, rotation):
    """
    Draws one triangle rotated by 'rotation' degrees
    """

    points = [
        (0, -size),
        (size, size),
        (-size, size),
    ]

    rad = math.radians(rotation)
    rotated_points = []

    for x, y in points:
        rx = x * math.cos(rad) - y * math.sin(rad)
        ry = x * math.sin(rad) + y * math.cos(rad)
        rotated_points.append((center_x + rx, center_y + ry))

    dwg.add(
        dwg.polygon(
            rotated_points,
            fill="none",
            stroke="black",
            stroke_width=4
        )
    )


def save_svg(filename, rotation):
    dwg = svgwrite.Drawing(filename, size=("200px", "200px"))
    draw_triangle(dwg, 100, 100, 40, rotation)
    dwg.save()


def main():
    q = generate_sequence_question()

    # stem image (last shown rotation)
    save_svg("stem.svg", q["sequence"][-1])

    # answer options
    letters = ["a", "b", "c", "d"]
    for i, rot in enumerate(q["options"]):
        save_svg(f"opt_{letters[i]}.svg", rot)

    print("Correct option is:", letters[q["correct_index"]])


if __name__ == "__main__":
    main()
