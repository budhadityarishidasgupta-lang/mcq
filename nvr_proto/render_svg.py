import math
import svgwrite
from generator import generate_question


def draw_triangle(dwg, cx, cy, size, rotation):
    points = [
        (0, -size),
        (size, size),
        (-size, size),
    ]

    rad = math.radians(rotation)
    rotated = []

    for x, y in points:
        rx = x * math.cos(rad) - y * math.sin(rad)
        ry = x * math.sin(rad) + y * math.cos(rad)
        rotated.append((cx + rx, cy + ry))

    dwg.add(
        dwg.polygon(
            rotated,
            fill="none",
            stroke="black",
            stroke_width=4
        )
    )


def save_svg(filename, rotation):
    dwg = svgwrite.Drawing(filename, size=("200px", "200px"))
    draw_triangle(dwg, 100, 100, 40, rotation)
    dwg.save()

def draw_structure_svg(structure, filename):
    """
    Draws a simple structure like:
    circle -> square -> circle
    """

    dwg = svgwrite.Drawing(filename, size=("300px", "200px"))

    # Fixed layout for now (simple + deterministic)
    positions = {
        1: (80, 100),
        2: (150, 100),
        3: (220, 100),
        4: (290, 100),
    }

    # Draw edges (connections)
    for start, end in structure["edges"]:
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        dwg.add(dwg.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke="black",
            stroke_width=2
        ))

    # Draw nodes (shapes)
    for node in structure["nodes"]:
        x, y = positions[node["id"]]

        if node["type"] == "circle":
            dwg.add(dwg.circle(
                center=(x, y),
                r=18,
                fill="none",
                stroke="black",
                stroke_width=3
            ))

        elif node["type"] == "square":
            dwg.add(dwg.rect(
                insert=(x - 18, y - 18),
                size=(36, 36),
                fill="none",
                stroke="black",
                stroke_width=3
            ))

    dwg.save()


def render_question(question):
    # If sequence, draw stem
    if question["type"] == "sequence":
        save_svg("stem.svg", question["sequence"][-1])

    # Draw options
    letters = ["a", "b", "c", "d"]
    for i, rot in enumerate(question["options"]):
        save_svg(f"opt_{letters[i]}.svg", rot)


def main():
    question = generate_question()
    render_question(question)
    return question
