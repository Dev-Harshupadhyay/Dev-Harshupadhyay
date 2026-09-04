#!/usr/bin/env python3
"""
Generates dh-ascii.svg — a monochrome ASCII banner that "types" itself in
row by row (SMIL clip-path wipe), then freezes. No loop.

This ships with a hand-authored placeholder banner (no photo required) so
the README works immediately. Once you have a real photo, follow the same
two-step pipeline described in prep_photo.py's docstring and swap the
GRID below for a photo-derived character grid.
"""

FILL = "#58a6ff"        # primary glyph color (readable on GitHub light + dark)
CURSOR = "#7ee787"      # wipe-edge cursor block
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
CHAR_W = 11
CHAR_H = 20
FONT_SIZE = 17

# --- 5x5 block font, just the letters we need for the banner -----------
FONT5 = {
    "H": ["#...#", "#...#", "#####", "#...#", "#...#"],
    "A": [".###.", "#...#", "#####", "#...#", "#...#"],
    "R": ["####.", "#...#", "####.", "#.#..", "#..#."],
    "S": [".####", "#....", ".###.", "....#", "####."],
    "U": ["#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "####.", "#....", "#...."],
    "D": ["####.", "#...#", "#...#", "#...#", "####."],
    "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#.."],
    " ": [".....", ".....", ".....", ".....", "....."],
}


def block_word(word, on="\u2588", off=" "):
    """Render a word using the 5x5 font, one row of text per font-row."""
    rows = ["" for _ in range(5)]
    for ch in word.upper():
        glyph = FONT5.get(ch, FONT5[" "])
        for r in range(5):
            rows[r] += glyph[r].replace("#", on).replace(".", off) + "  "
    return rows


def build_grid():
    banner = block_word("HARSH")
    lines = []
    lines.extend(banner)
    lines.append("")
    lines.append("┌────────────────────────────────────┐")
    lines.append("│  full-stack developer               │")
    lines.append("│  web apps · automation · AI tinkering│")
    lines.append("└────────────────────────────────────┘")
    width = max(len(l) for l in lines)
    return [l.ljust(width) for l in lines], width


def make_svg():
    grid, width = build_grid()
    n_rows = len(grid)
    svg_w = width * CHAR_W + 20
    svg_h = n_rows * CHAR_H + 20

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" font-family="{FONT}" font-size="{FONT_SIZE}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="transparent"/>')

    row_w = width * CHAR_W
    total_dur = 1.35
    step = total_dur / n_rows

    for i, line in enumerate(grid):
        y = 24 + i * CHAR_H
        begin = round(i * step, 3)
        dur = round(step * 1.6, 3)
        clip_id = f"clip{i}"

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'  <rect x="10" y="{y - CHAR_H + 6}" width="0" height="{CHAR_H}">')
        parts.append(
            f'    <animate attributeName="width" from="0" to="{row_w}" '
            f'begin="{begin}s" dur="{dur}s" fill="freeze" calcMode="spline" '
            f'keySplines="0.2 0 0.2 1"/>'
        )
        parts.append("  </rect>")
        parts.append("</clipPath>")

        safe_line = (
            line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'  <text x="10" y="{y}" fill="{FILL}" xml:space="preserve">{safe_line}</text>'
        )
        parts.append("</g>")

        # small cursor block riding the wipe edge for this row, then vanishes
        parts.append(
            f'<rect x="10" y="{y - CHAR_H + 6}" width="{CHAR_W - 2}" height="{CHAR_H - 4}" '
            f'fill="{CURSOR}" opacity="0">'
        )
        parts.append(
            f'  <animate attributeName="x" from="10" to="{10 + row_w}" '
            f'begin="{begin}s" dur="{dur}s" fill="freeze"/>'
        )
        parts.append(
            f'  <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.9;1" '
            f'begin="{begin}s" dur="{dur}s" fill="freeze"/>'
        )
        parts.append("</rect>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open("dh-ascii.svg", "w") as f:
        f.write(svg)
    print("wrote dh-ascii.svg")
  
