#!/usr/bin/env python3
"""
render_heatmap_svg.py

Turns contribution day data (from fetch_contributions.py, piped in as JSON
on stdin or read from a file) into harsh-heatmap.svg, themed to match the
rest of the profile (dark background, blue intensity scale, rounded cells).

If no real data is available (first run, offline, GitHub markup changed),
it falls back to a deterministic placeholder pattern so the README never
ships a broken image.

Usage:
    python scripts/fetch_contributions.py Dev-Harshupadhyay | python scripts/render_heatmap_svg.py > harsh-heatmap.svg
"""
import json
import sys
from datetime import date, timedelta

LEVEL_COLORS = ["#141c26", "#1c3a52", "#2a5c80", "#3e88b8", "#7ec8ff"]
CELL = 10
GAP = 3
LEFT_PAD = 20
TOP_PAD = 40
WEEKS = 53


def load_input():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def synthetic_days():
    """Deterministic, non-random placeholder so a first run still looks intentional."""
    today = date.today()
    start = today - timedelta(weeks=WEEKS)
    days = []
    for i in range((today - start).days + 1):
        d = start + timedelta(days=i)
        # a calm, deterministic wave pattern rather than actual fake activity claims
        level = (i * 7) % 5
        days.append({"date": d.isoformat(), "level": level})
    return days


def build_grid(days):
    by_date = {d["date"]: d["level"] for d in days}
    if not by_date:
        by_date = {d["date"]: d["level"] for d in synthetic_days()}

    dates = sorted(by_date.keys())
    start = date.fromisoformat(dates[0])
    # align to the most recent Sunday on/before start
    start -= timedelta(days=(start.weekday() + 1) % 7)
    end = date.fromisoformat(dates[-1])

    cells = []
    cursor = start
    week = 0
    while cursor <= end:
        for dow in range(7):
            d = cursor + timedelta(days=dow)
            level = by_date.get(d.isoformat(), 0)
            cells.append((week, dow, level))
        cursor += timedelta(days=7)
        week += 1
    return cells, week


def render(cells, weeks):
    width = LEFT_PAD * 2 + weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + 40
    width = max(width, 400)

    parts = []
    parts.append(
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'fill="none" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Harsh Upadhyay contribution heatmap">'
    )
    parts.append(
        '<defs><linearGradient id="heatBg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0a0d13"/><stop offset="1" stop-color="#0d1420"/>'
        '</linearGradient></defs>'
    )
    parts.append(f'<rect width="{width}" height="{height}" rx="10" fill="url(#heatBg)"/>')
    parts.append(
        f'<text x="20" y="26" font-family="ui-monospace, \'JetBrains Mono\', Menlo, monospace" '
        f'font-size="12" letter-spacing="1.5" fill="#5c7a95">CONTRIBUTION ACTIVITY</text>'
    )

    for week, dow, level in cells:
        x = LEFT_PAD + week * (CELL + GAP)
        y = TOP_PAD + dow * (CELL + GAP)
        color = LEVEL_COLORS[min(level, 4)]
        delay = (week * 7 + dow) % 30 * 0.05
        parts.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
            f'<animate attributeName="opacity" values="0.55;1;0.55" '
            f'dur="4s" begin="{delay:.2f}s" repeatCount="indefinite"/></rect>'
        )

    legend_y = height - 18
    parts.append(f'<text x="20" y="{legend_y+9}" font-family="ui-monospace, monospace" font-size="10" fill="#3f5468">less</text>')
    for i, color in enumerate(LEVEL_COLORS):
        parts.append(f'<rect x="{52 + i*14}" y="{legend_y}" width="10" height="10" rx="2" fill="{color}"/>')
    parts.append(f'<text x="{52 + 5*14 + 6}" y="{legend_y+9}" font-family="ui-monospace, monospace" font-size="10" fill="#3f5468">more</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def main():
    data = load_input()
    days = data.get("days", [])
    cells, weeks = build_grid(days)
    print(render(cells, weeks))


if __name__ == "__main__":
    main()
