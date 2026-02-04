# nvr_proto/render_svg.py
import math
from typing import Optional, List, Any, Dict


# =========================
# Core SVG helpers
# =========================
def _svg_wrap(inner: str, w: int = 920, h: int = 420) -> str:
    return f"""
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {w} {h}"
     width="100%"
     height="auto"
     preserveAspectRatio="xMidYMid meet">
  <rect x="0" y="0" width="{w}" height="{h}" rx="18" fill="#0f1117"/>
  {inner}
</svg>
""".strip()


def _tile(
    x: int,
    y: int,
    w: int,
    h: int,
    inner: str,
    selected: bool = False,
) -> str:
    stroke = "#58a6ff" if selected else "rgba(255,255,255,.18)"
    stroke_w = 4 if selected else 2
    fill = "#1f2937" if selected else "#161b22"
    return f"""
<g>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16"
        fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"/>
  {inner}
</g>
""".strip()


def _text(x: Any, y: Any, s: str, size: int = 18, color: str = "#e6edf3", anchor: str = "start") -> str:
    # x/y can be numbers or "50%" strings
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-family="Inter, system-ui, Arial" text-anchor="{anchor}">{s}</text>'
    )


def _rotate_point(px: float, py: float, cx: float, cy: float, deg: float):
    ang = math.radians(deg)
    dx, dy = px - cx, py - cy
    rx = dx * math.cos(ang) - dy * math.sin(ang)
    ry = dx * math.sin(ang) + dy * math.cos(ang)
    return cx + rx, cy + ry


def _triangle(cx: int, cy: int, size: int = 34, rot: int = 0,
              fill: str = "none", stroke: str = "#e6edf3", stroke_w: int = 3) -> str:
    pts = [
        (cx, cy - size),
        (cx - size, cy + size),
        (cx + size, cy + size),
    ]
    pts2 = [_rotate_point(x, y, cx, cy, rot) for x, y in pts]
    pts_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts2])
    return f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'


def _circle(cx: int, cy: int, r: int = 20, fill: str = "none", stroke: str = "#e6edf3", stroke_w: int = 3) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'


def _square(cx: int, cy: int, size: int = 36, fill: str = "none", stroke: str = "#e6edf3", stroke_w: int = 3) -> str:
    x = cx - size // 2
    y = cy - size // 2
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" />'


def _lines(lines: List, ox: int, oy: int, stroke: str = "#e6edf3", stroke_w: int = 3) -> str:
    out = ""
    for (x1, y1), (x2, y2) in lines:
        out += f'<line x1="{x1+ox}" y1="{y1+oy}" x2="{x2+ox}" y2="{y2+oy}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linecap="round" />'
    return out


def _render_option_tiles_rotations(options: List[Dict[str, Any]], y: int, selected_label: Optional[str], show_labels: bool = True) -> str:
    labels = ["A", "B", "C", "D"]
    tile_w, tile_h = 200, 140
    gap = 24
    x0 = 24
    out = ""
    sel = (selected_label or "").upper() if selected_label else None

    for i in range(min(4, len(options))):
        x = x0 + i * (tile_w + gap)
        rot = options[i]["rotation"]
        inner = ""
        if show_labels:
            inner += _text(x + 16, y + 34, labels[i], size=18, color="#9aa4b2")
        inner += _triangle(x + tile_w // 2, y + 92, size=32, rot=rot)
        out += _tile(x, y, tile_w, tile_h, inner, selected=(labels[i] == sel))
    return out


# =========================
# Public API
# =========================
def render_question_svg(
    question: Dict,
    selected_option: Optional[str] = None,
    show_options: bool = False,
) -> str:
    """
    Returns ONE SVG containing the question prompt (and optionally option tiles).
    Contract expected from generator:
      - question["pattern_family"] in {"SEQUENCE","ODD_ONE_OUT","MATRIX","ANALOGY","COMPOSITION"}
      - question["stem"] dict
      - question["options"] list (len 4)
      - question["correct_index"] int
    """
    assert "pattern_family" in question
    assert "stem" in question
    assert "options" in question
    assert isinstance(question["options"], list)
    assert len(question["options"]) == 4
    assert isinstance(question["correct_index"], int)

    family = question["pattern_family"]
    stem = question["stem"] or {}
    options = question["options"] or []

    if family == "SEQUENCE":
        return _render_sequence(stem, options, selected_option, show_options)

    if family == "ODD_ONE_OUT":
        return _render_odd_one_out(stem, options, selected_option, show_options)

    if family == "MATRIX":
        return _render_matrix(stem, options, selected_option, show_options)

    # fallback
    inner = _text(24, 44, f"{family or 'QUESTION'}", size=22)
    inner += _text(24, 78, "Renderer not implemented for this pattern_family.", size=16, color="#9aa4b2")
    if show_options and options:
        inner += _render_option_tiles_rotations(options, y=230, selected_label=selected_option)
    return _svg_wrap(inner, 920, 420)


# =========================
# Renderers
# =========================
def _render_sequence(stem: Dict, options: List[Dict[str, Any]], selected: Optional[str], show_options: bool) -> str:
    seq = stem.get("items") or []
    inner = """
<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7"
          refX="10" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#6ea8fe"/>
  </marker>
</defs>
""".strip()
    inner += _text(24, 44, "Sequence", size=22)

    def _arrow(x1: int, y: int, x2: int) -> str:
        return (
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
            'stroke="#6ea8fe" stroke-width="2" marker-end="url(#arrowhead)" />'
        )

    start_x = 140
    gap = 140
    y = 140
    for i, item in enumerate(seq[:4]):
        x = start_x + i * gap
        inner += _triangle(x, y, size=34, rot=item.get("rotation", 0))
        if i < len(seq[:4]) - 1:
            inner += _arrow(x + 40, y, x + gap - 40)

    qx = start_x + len(seq[:4]) * gap
    inner += (
        f'<text x="{qx}" y="{y + 12}" text-anchor="middle" '
        'font-size="44" font-weight="600" fill="#6ea8fe">?</text>'
    )

    if show_options and options:
        inner += _render_option_tiles_rotations(options, y=230, selected_label=selected)
    return _svg_wrap(inner, 920, 420)


def _render_odd_one_out(stem: Dict, options: List[Dict[str, Any]], selected: Optional[str], show_options: bool) -> str:
    inner = _text(24, 44, "Odd one out", size=22)
    items = stem.get("items") or []
    labels = ["A", "B", "C", "D"]
    selected_ref_index = None
    if selected:
        selected_label = selected.upper()
        if selected_label in labels:
            sel_index = labels.index(selected_label)
            selected_ref_index = options[sel_index].get("ref_index", sel_index)

    tile_w, tile_h = 160, 140
    gap = 24
    x0 = 84
    y = 110
    for i, item in enumerate(items[:4]):
        x = x0 + i * (tile_w + gap)
        rot = item.get("rotation", 0)
        inner_tile = ""
        if show_options:
            inner_tile += _text(x + 16, y + 34, labels[i], size=18, color="#9aa4b2")
        inner_tile += _triangle(x + tile_w // 2, y + 92, size=32, rot=rot)
        inner += _tile(x, y, tile_w, tile_h, inner_tile, selected=(selected_ref_index == i))
    return _svg_wrap(inner, 920, 420)


def _render_matrix(stem: Dict, options: List[Dict[str, Any]], selected: Optional[str], show_options: bool) -> str:
    m = stem.get("items") or []
    inner = _text("50%", 40, "Matrix", size=22, anchor="middle")

    grid = 3
    cell = 84
    gap = 18
    total = grid * cell + (grid - 1) * gap

    cx, cy = 460, 155
    start_x = int(cx - total / 2)
    start_y = int(cy - total / 2)

    for r in range(min(3, len(m))):
        row = m[r] or []
        for c in range(min(3, len(row))):
            v = row[c]
            x = start_x + c * (cell + gap)
            y = start_y + r * (cell + gap)
            # cell outline
            inner += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="12" fill="none" stroke="rgba(255,255,255,.16)" />'
            if v is None:
                inner += _text(x + cell / 2, y + cell / 2 + 8, "?", size=26, color="#9aa4b2", anchor="middle")
            else:
                inner += _triangle(x + cell // 2, y + cell // 2, size=30, rot=int(v.get("rotation", 0)))

    if show_options and options:
        inner += _render_option_tiles_rotations(options, y=250, selected_label=selected)
    return _svg_wrap(inner, 920, 440)


def _render_structure_match(prompt: Dict, selected: Optional[str], show_options: bool) -> str:
    # prompt is whatever generator gives; we just show a clear placeholder stem
    inner = _text(24, 44, "Structure match", size=22)
    inner += _text(24, 78, "Match the same connection structure.", size=16, color="#9aa4b2")

    # simple stem: circle -> square -> circle
    inner += _circle(260, 170, r=18)
    inner += _square(360, 170, size=38)
    inner += _circle(460, 170, r=18)
    inner += '<line x1="278" y1="170" x2="340" y2="170" stroke="#e6edf3" stroke-width="3" stroke-linecap="round"/>'
    inner += '<line x1="380" y1="170" x2="442" y2="170" stroke="#e6edf3" stroke-width="3" stroke-linecap="round"/>'

    # options are complex structures; for now we display prompt only (no options in SVG)
    # Streamlit will show A/B/C/D buttons.
    return _svg_wrap(inner, 920, 380)


def _render_hidden_shape(prompt: Dict, selected: Optional[str], show_options: bool) -> str:
    inner = _text(24, 44, "Hidden shape", size=22)
    inner += _text(24, 78, "Find the option that contains the target lines.", size=16, color="#9aa4b2")

    # draw a small target "L" on the left as stem
    target = prompt.get("target") or [((0, 0), (40, 0)), ((0, 0), (0, 40))]
    inner += _tile(80, 120, 180, 180, _lines(target, ox=120, oy=160), selected=False)

    return _svg_wrap(inner, 920, 380)
