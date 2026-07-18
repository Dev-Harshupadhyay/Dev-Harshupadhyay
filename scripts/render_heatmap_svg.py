#!/usr/bin/env python3
"""
Renders data/contributions.json as the classic 53-week x 7-day calendar
of rounded boxes, using a GitHub-ish green ramp. Boxes reveal once in a
diagonal, line-after-line slide-down (CSS keyframes, play-once, no loop),
plus a Less->More legend and a stats footer.

If data/contributions.json doesn't exist yet (i.e. the daily workflow
hasn't run once), a small "waiting for first sync" placeholder grid is
written instead so the README never shows a broken image.
"""
import json
import os
from datetime import date, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BOX = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"


def level_from_count(count, max_count):
    if not count:
        return 0
    if max_count <= 0:
        return 1
    ratio = count / max_count
    if ratio > 0.85:
        return 5
    if ratio > 0.6:
        return 4
    if ratio > 0.35:
        return 3
    if ratio > 0.1:
        return 2
    return 1


def load_weeks():
    path = "data/contributions.json"
    if not os.path.exists(path):
        return None, None

    with open(path) as f:
        payload = json.load(f)

    days = payload.get("days", [])
    if not days:
        return None, payload.get("stats", {})

    counts = {d["date"]: (d["count"] or 0) for d in days}
    max_count = max(counts.values(), default=0)

    end = date.today()
    start = end - timedelta(days=7 * 53 - 1)
    # align start to a Sunday so columns are clean weeks
    start -= timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    cur = start
    while cur <= end:
        week = []
        for _ in range(7):
            key = cur.isoformat()
            c = counts.get(key, 0)
            week.append((cur, c, level_from_count(c, max_count)))
            cur += timedelta(days=1)
        weeks.append(week)

    return weeks, payload.get("stats", {})


def placeholder_weeks():
    """A gentle empty grid shown until the first Action run populates real data."""
    end = date.today()
    weeks = []
    cur = end - timedelta(days=7 * 53 - 1)
    cur -= timedelta(days=(cur.weekday() + 1) % 7)
    while cur <= end:
        week = [(cur + timedelta(days=i), 0, 0) for i in range(7)]
        weeks.append(week)
        cur += timedelta(days=7)
    return weeks


def make_svg():
    weeks, stats = load_weeks()
    is_placeholder = weeks is None
    if is_placeholder:
        weeks = placeholder_weeks()

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (BOX + GAP) + 20
    height = TOP_PAD + 7 * (BOX + GAP) + 60

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="11">'
    )
    parts.append("<style>")
    parts.append(
        "@keyframes dropIn {"
        "0%{opacity:0; transform:translate(-6px,-6px);}"
        "100%{opacity:1; transform:translate(0,0);}"
        "}"
    )
    parts.append("</style>")
    parts.append('<rect width="100%" height="100%" fill="transparent"/>')

    for wi, week in enumerate(weeks):
        for di, (d, count, level) in enumerate(week):
            x = LEFT_PAD + wi * (BOX + GAP)
            y = TOP_PAD + di * (BOX + GAP)
            color = PALETTE[level]
            delay = 0.012 * (wi + di)
            title = f"{d.isoformat()}: {count} contribution{'s' if count != 1 else ''}"
            parts.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" ry="2" '
                f'fill="{color}" style="opacity:0; animation:dropIn 0.4s ease-out forwards; '
                f'animation-delay:{delay:.3f}s"><title>{title}</title></rect>'
            )

    # legend
    legend_y = height - 34
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y + 9}" fill="#8b949e">Less</text>')
    lx = LEFT_PAD + 38
    for lvl, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
        lx += BOX + GAP
    parts.append(f'<text x="{lx + 4}" y="{legend_y + 9}" fill="#8b949e">More</text>')

    # stats footer
    footer_y = height - 12
    if is_placeholder:
        footer = "waiting for first sync — runs daily via GitHub Actions"
    else:
        total = stats.get("total_last_year", 0)
        streak = stats.get("current_streak", 0)
        footer = f"{total} contributions in the last year · current streak {streak} days"
    parts.append(f'<text x="{LEFT_PAD}" y="{footer_y}" fill="#58a6ff">{footer}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open("contrib-heatmap.svg", "w") as f:
        f.write(svg)
    print("wrote contrib-heatmap.svg" + (" (placeholder)" if not os.path.exists("data/contributions.json") else ""))
  
