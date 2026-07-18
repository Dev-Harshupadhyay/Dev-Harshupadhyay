#!/usr/bin/env python3
"""
Generates info-card.svg — a neofetch-style panel that fades/slides in
line by line next to the ASCII banner.

Set STATIC=1 to emit a frozen (already-revealed) frame, useful for a
local Quick Look preview where SMIL/CSS animation won't play.
"""
import os

W, H = 490, 300
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
LABEL_COLOR = "#7ee787"   # neofetch-green keys
VALUE_COLOR = "#c9d1d9"   # light gray values
DIM_COLOR = "#8b949e"
TITLE_COLOR = "#58a6ff"

ROWS = [
    ("os", "Harsh Upadhyay OS"),
    ("host", "BCA Student · Full-Stack Dev"),
    ("now", "Cinevood — movie review platform"),
    ("also", "Weather App — live forecast tracker"),
    ("automation", "@TIMEPASSQ_BOT — Telegram task bot"),
    ("stack", "JS/TS · Node.js · Python · MongoDB"),
    ("focus", "AI-driven automation"),
]

STATIC = os.environ.get("STATIC") == "1"


def make_svg():
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="15">'
    )
    if not STATIC:
        parts.append("<style>")
        parts.append(
            "@keyframes fadeSlide {"
            "0%{opacity:0; transform:translateX(-8px);}"
            "100%{opacity:1; transform:translateX(0);}"
            "}"
        )
        parts.append("</style>")

    parts.append(f'<rect width="100%" height="100%" fill="transparent"/>')

    # title bar: three "traffic light" dots + prompt
    parts.append('<circle cx="18" cy="18" r="6" fill="#ff5f56"/>')
    parts.append('<circle cx="38" cy="18" r="6" fill="#ffbd2e"/>')
    parts.append('<circle cx="58" cy="18" r="6" fill="#27c93f"/>')
    parts.append(
        f'<text x="80" y="23" fill="{TITLE_COLOR}">harsh@github ~ % neofetch</text>'
    )
    parts.append(f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="#30363d" stroke-width="1"/>')

    row_h = 32
    start_y = 70
    for i, (key, val) in enumerate(ROWS):
        y = start_y + i * row_h
        g_attrs = "" if STATIC else (
            f' style="opacity:0; animation:fadeSlide 0.45s ease-out forwards; '
            f'animation-delay:{0.25 + i * 0.18:.2f}s"'
        )
        parts.append(f"<g{g_attrs}>")
        parts.append(f'<text x="24" y="{y}" fill="{LABEL_COLOR}">{key}</text>')
        parts.append(f'<text x="130" y="{y}" fill="{DIM_COLOR}">:</text>')
        safe_val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(f'<text x="148" y="{y}" fill="{VALUE_COLOR}">{safe_val}</text>')
        parts.append("</g>")

    # color swatch strip at the bottom, neofetch-signature touch
    swatch_y = start_y + len(ROWS) * row_h + 14
    palette = ["#0e4429", "#006d32", "#26a641", "#39d353", "#58a6ff", "#7ee787"]
    for i, c in enumerate(palette):
        x = 24 + i * 26
        g_attrs = "" if STATIC else (
            f' style="opacity:0; animation:fadeSlide 0.35s ease-out forwards; '
            f'animation-delay:{0.25 + len(ROWS) * 0.18 + i * 0.05:.2f}s"'
        )
        parts.append(f'<g{g_attrs}><rect x="{x}" y="{swatch_y}" width="20" height="20" rx="4" fill="{c}"/></g>')

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open("info-card.svg", "w") as f:
        f.write(svg)
    print("wrote info-card.svg" + (" (static frame)" if STATIC else ""))
