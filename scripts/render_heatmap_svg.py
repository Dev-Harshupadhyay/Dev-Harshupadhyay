#!/usr/bin/env python3
"""
render_heatmap_svg.py
----------------------
Reads contributions.json (produced by fetch_contributions.py) and renders
harsh-heatmap.svg: a dark, blue-themed contribution calendar matching the
rest of the profile's visual identity.

If contributions.json is missing or empty, a clearly-labelled placeholder
grid is generated instead, so the README never ships a broken image.

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "contributions.json"
OUT_PATH = ROOT / "harsh-heatmap.svg"

CELL = 11
GAP = 3
LEFT_PAD = 32
TOP_PAD = 40
WEEKS = 53
DAYS = 7

LEVEL_COLORS = ["#10141c", "#12233f", "#1c3c6e", "#2c5fa8", "#4f8fe8"]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_days():
    if DATA_PATH.exists():
        try:
            data = json.loads(DATA_PATH.read_text())
            days = data.get("days", [])
            if days:
                return days, False
        except Exception:
            pass
    # Placeholder fallback: an empty (level 0) grid, clearly not live data.
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=WEEKS * 7 - 1)
    placeholder = []
    d = start
    while d <= today:
        placeholder.append({"date": d.isoformat(), "count": 0, "level": 0})
        d += timedelta(days=1)
    return placeholder, True


def build_grid(days):
    by_date = {d["date"]: d for d in days}
    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    # Align the grid to end on the most recent Saturday, GitHub-style.
    end = last_date
    end_weekday = (end.weekday() + 1) % 7  # convert Mon=0 -> Sun=0 indexing
    end += timedelta(days=(6 - end_weekday))
    start = end - timedelta(days=WEEKS * DAYS - 1)

    grid = []
    cur = start
    for week in range(WEEKS):
        col = []
        for day in range(DAYS):
            key = cur.isoformat()
            entry = by_date.get(key, {"date": key, "count": 0, "level": 0})
            col.append((cur, entry))
            cur += timedelta(days=1)
        grid.append(col)
    return grid, start, end


def render(grid, start, end, is_placeholder):
    width = LEFT_PAD + WEEKS * (CELL + GAP) + 20
    height = TOP_PAD + DAYS * (CELL + GAP) + 30

    parts = []
    parts.append(
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Harsh Upadhyay contribution heatmap">'
    )
    parts.append(f"""
  <defs>
    <linearGradient id="hmbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1119"/>
      <stop offset="100%" stop-color="#080a0f"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="14" fill="url(#hmbg)" stroke="#1c2431" stroke-width="1.5"/>
  <text x="20" y="24" font-family="'Cascadia Code','Fira Code',Consolas,monospace" font-size="12" letter-spacing="3" fill="#5b8def">CONTRIBUTION HEATMAP</text>
""")

    # Month labels
    seen_months = set()
    for w, col in enumerate(grid):
        first_date = col[0][0]
        key = (first_date.year, first_date.month)
        if first_date.day <= 7 and key not in seen_months:
            seen_months.add(key)
            x = LEFT_PAD + w * (CELL + GAP)
            parts.append(
                f'<text x="{x}" y="{TOP_PAD-8}" font-family="Consolas, monospace" '
                f'font-size="9" fill="#586479">{MONTH_NAMES[first_date.month-1]}</text>'
            )

    # Cells (single group fade-in keeps the file lightweight instead of
    # animating each of the ~371 cells individually)
    parts.append('<g opacity="0">')
    parts.append('<animate attributeName="opacity" values="0;1" dur="0.8s" begin="0s" fill="freeze"/>')
    for w, col in enumerate(grid):
        x = LEFT_PAD + w * (CELL + GAP)
        for d, (date, entry) in enumerate(col):
            y = TOP_PAD + d * (CELL + GAP)
            level = entry.get("level", 0)
            color = LEVEL_COLORS[min(level, 4)]
            count = entry.get("count", 0)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}"><title>{count} contributions on {date.isoformat()}</title></rect>'
            )
    parts.append('</g>')

    legend_x = width - 20 - (5 * (CELL + 4)) - 60
    legend_y = height - 22
    parts.append(
        f'<text x="{legend_x - 30}" y="{legend_y+9}" font-family="Consolas, monospace" '
        f'font-size="9" fill="#586479">Less</text>'
    )
    for i, color in enumerate(LEVEL_COLORS):
        lx = legend_x + i * (CELL + 4)
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    parts.append(
        f'<text x="{legend_x + 5*(CELL+4) + 6}" y="{legend_y+9}" '
        f'font-family="Consolas, monospace" font-size="9" fill="#586479">More</text>'
    )

    if is_placeholder:
        parts.append(
            f'<text x="20" y="{height-10}" font-family="Consolas, monospace" '
            f'font-size="9" fill="#4a5568">placeholder — run scripts/fetch_contributions.py to load live data</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    days, is_placeholder = load_days()
    grid, start, end = build_grid(days)
    svg = render(grid, start, end, is_placeholder)
    OUT_PATH.write_text(svg)
    print(f"[render_heatmap_svg] wrote {OUT_PATH} (placeholder={is_placeholder})")


if __name__ == "__main__":
    main()
