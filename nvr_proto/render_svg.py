import math
import svgwrite
from nvr_proto.generator import generate_question


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

def draw_line_shape(lines, filename):
    """
    Draws a set of straight lines (hidden shape / container)
    """

    dwg = svgwrite.Drawing(filename, size=("200px", "200px"))

    # Center offset so shapes sit nicely
    offset_x = 80
    offset_y = 80

    for (x1, y1), (x2, y2) in lines:
        dwg.add(dwg.line(
            start=(x1 + offset_x, y1 + offset_y),
            end=(x2 + offset_x, y2 + offset_y),
            stroke="black",
            stroke_width=3
        ))

    dwg.save()

def draw_matrix(matrix, filename):
    """
    Draws a 3x3 matrix of triangles.
    One cell may be None (missing).
    """

    dwg = svgwrite.Drawing(filename, size=("300px", "300px"))

    cell_size = 80
    start_x = 40
    start_y = 40

    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            if value is None:
                continue

            cx = start_x + col_idx * cell_size
            cy = start_y + row_idx * cell_size

            # reuse triangle logic
            points = [
                (0, -20),
                (20, 20),
                (-20, 20),
            ]

            rad = math.radians(value)
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
                    stroke_width=3
                )
            )

    dwg.save()



def render_question(question):

    if question["type"] == "sequence":
        save_svg("stem.svg", question["sequence"][-1])
        letters = ["a", "b", "c", "d"]
        for i, rot in enumerate(question["options"]):
            save_svg(f"opt_{letters[i]}.svg", rot)

    elif question["type"] == "odd_one_out":
        letters = ["a", "b", "c", "d"]
        for i, rot in enumerate(question["options"]):
            save_svg(f"opt_{letters[i]}.svg", rot)

    elif question["type"] == "structure_match":
        # Draw example structures (left side)
        for i, example in enumerate(question["examples"]):
            draw_structure_svg(example, f"example_{i}.svg")

        # Draw options
        letters = ["a", "b", "c", "d"]
        for i, option in enumerate(question["options"]):
            draw_structure_svg(option, f"opt_{letters[i]}.svg")
   
    elif question["type"] == "hidden_shape":
        # Draw target shape
        draw_line_shape(question["target"], "target.svg")

        # Draw options
        letters = ["a", "b", "c", "d"]
        for i, option in enumerate(question["options"]):
            draw_line_shape(option["lines"], f"opt_{letters[i]}.svg")
    
    elif question["type"] == "matrix":
        # Draw the matrix grid
        draw_matrix(question["matrix"], "matrix.svg")

        # Draw answer options
        letters = ["a", "b", "c", "d"]
        for i, rot in enumerate(question["options"]):
            save_svg(f"opt_{letters[i]}.svg", rot)


def main():
    question = generate_question()
    render_question(question)


def _svg_wrap(inner: str, w: int = 760, h: int = 260) -> str:
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         viewBox="0 0 {w} {h}"
         width="100%"
         height="auto"
         preserveAspectRatio="xMidYMid meet">
      <rect x="0" y="0" width="{w}" height="{h}" rx="16" fill="#0f1117"/>
      {inner}
    </svg>
    """


def _triangle(cx: int, cy: int, size: int = 40, rot: int = 0, fill: str = "#e6edf3") -> str:
    # triangle pointing up at rot=0
    pts = [
        (cx, cy - size),
        (cx - size, cy + size),
        (cx + size, cy + size),
    ]
    # rotate points around center
    ang = math.radians(rot)

    def rotp(x, y):
        dx, dy = x - cx, y - cy
        rx = dx * math.cos(ang) - dy * math.sin(ang)
        ry = dx * math.sin(ang) + dy * math.cos(ang)
        return (cx + rx, cy + ry)

    pts2 = [rotp(x, y) for x, y in pts]
    pts_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts2])
    return f'<polygon points="{pts_str}" fill="{fill}" />'


def _tile(x: int, y: int, w: int, h: int, inner: str) -> str:
    return f"""
    <g>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#161b22" stroke="#2f3640"/>
      {inner}
    </g>
    """


def render_question_svg(question: dict) -> str:
    """
    Universal SVG renderer for schema-driven questions.
    Returns a single SVG string containing prompt + option tiles.
    """
    qtype = question.get("question_type")
    prompt = question.get("prompt", {})
    options = question.get("options", [])

    if qtype == "SEQUENCE":
        return _render_sequence(prompt, options)

    if qtype == "ODD_ONE_OUT":
        return _render_odd_one_out(prompt, options)

    if qtype == "MATRIX":
        return _render_matrix(prompt, options)

    # Fallback: show options as simple labels
    return _render_fallback(prompt, options, title=qtype or "QUESTION")


def _render_sequence(prompt: dict, options: list) -> str:
    # prompt: {"shape": "...", "sequence": [0,90,180]}
    seq = prompt.get("sequence", [])
    inner = '<text x="24" y="36" fill="#e6edf3" font-size="18" font-family="Inter,Arial">Sequence</text>'

    # draw sequence row
    x0 = 70
    for i, rot in enumerate(seq):
        inner += _triangle(x0 + i * 90, 90, size=22, rot=int(rot))
    inner += '<text x="340" y="96" fill="#9aa4b2" font-size="22" font-family="Inter,Arial">→</text>'
    inner += '<text x="370" y="96" fill="#9aa4b2" font-size="16" font-family="Inter,Arial">?</text>'

    # options tiles (A-D)
    inner += _render_option_tiles(options, y=130)
    return _svg_wrap(inner, w=760, h=260)


def _render_odd_one_out(prompt: dict, options: list) -> str:
    inner = '<text x="24" y="36" fill="#e6edf3" font-size="18" font-family="Inter,Arial">Odd one out</text>'
    # prompt stem: show 4 shapes (same as options conceptually)
    for i, rot in enumerate(options[:4]):
        inner += _triangle(90 + i * 120, 90, size=24, rot=int(rot))
    inner += _render_option_tiles(options, y=130)
    return _svg_wrap(inner, w=760, h=260)


def _render_matrix(prompt: dict, options: list) -> str:
    """
    Responsive 3x3 matrix renderer.
    """
    m = prompt.get("matrix", [])

    inner = """
    <text x="50%" y="28" fill="#e6edf3" font-size="18"
          font-family="Inter,Arial" text-anchor="middle">
        Matrix
    </text>
    """

    # Matrix layout (centered)
    grid_size = 3
    cell = 64
    gap = 14
    total = grid_size * cell + (grid_size - 1) * gap

    cx = 380        # SVG center
    cy = 120        # Matrix vertical center

    start_x = cx - total // 2
    start_y = cy - total // 2

    for r in range(len(m)):
        for c in range(len(m[r])):
            v = m[r][c]
            x = start_x + c * (cell + gap)
            y = start_y + r * (cell + gap)

            if v is None:
                inner += f'''
                <rect x="{x}" y="{y}" width="{cell}" height="{cell}"
                      rx="10" fill="#0f1117" stroke="#2f3640"/>
                <text x="{x + cell/2}" y="{y + cell/2 + 6}"
                      fill="#9aa4b2" font-size="22"
                      font-family="Inter,Arial" text-anchor="middle">?</text>
                '''
            else:
                inner += _triangle(
                    x + cell // 2,
                    y + cell // 2,
                    size=20,
                    rot=int(v)
                )

    # Options row (responsive)
    inner += _render_option_tiles(options, y=220)

    return _svg_wrap(inner, w=760, h=340)


def _render_option_tiles(options: list, y: int = 130) -> str:
    # render 4 option tiles as rotations (0/90/180/270)
    labels = ["A", "B", "C", "D"]
    tile_w, tile_h = 150, 100
    gap = 20
    x0 = 24
    out = ""
    for i in range(min(4, len(options))):
        x = x0 + i * (tile_w + gap)
        rot = options[i]
        inner = (
            f'<text x="{x + 14}" y="{y + 26}" fill="#9aa4b2" font-size="14" '
            f'font-family="Inter,Arial">{labels[i]}</text>'
        )
        inner += _triangle(x + tile_w // 2, y + 62, size=22, rot=int(rot))
        out += _tile(x, y, tile_w, tile_h, inner)
    return out


def _render_fallback(prompt: dict, options: list, title: str = "QUESTION") -> str:
    inner = (
        f'<text x="24" y="36" fill="#e6edf3" font-size="18" font-family="Inter,Arial">{title}</text>'
    )
    inner += (
        '<text x="24" y="64" fill="#9aa4b2" font-size="14" '
        'font-family="Inter,Arial">Renderer not implemented for this type yet.</text>'
    )
    inner += _render_option_tiles(options, y=130)
    return _svg_wrap(inner, w=760, h=260)
    return question
