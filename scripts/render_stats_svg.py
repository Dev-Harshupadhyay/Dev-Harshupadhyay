#!/usr/bin/env python3
"""
render_stats_svg.py — themed stats card from fetch_stats.py's JSON (stdin).
Falls back to zeroed placeholders (clearly labeled, never invented numbers)
if the API call failed.

Usage:
    cat data/stats.json | python scripts/render_stats_svg.py > harsh-stats.svg
"""
import json
import sys

WIDTH, HEIGHT = 380, 200


def load():
    raw = sys.stdin.read().strip()
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


def row(y, label, value):
    return (
        f'<text x="24" y="{y}" font-family="ui-monospace, \'JetBrains Mono\', Menlo, monospace" '
        f'font-size="13" fill="#5c7a95">{label}</text>'
        f'<text x="260" y="{y}" text-anchor="end" font-family="ui-monospace, \'JetBrains Mono\', Menlo, monospace" '
        f'font-size="13" fill="#eef4fb" font-weight="700">{value}</text>'
    )


def main():
    data = load()
    repos = data.get("public_repos", "—")
    stars = data.get("stars", "—")
    followers = data.get("followers", "—")
    following = data.get("following", "—")

    parts = [
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        'fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats for Harsh Upadhyay">',
        '<defs><linearGradient id="statsBg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0a0d13"/><stop offset="1" stop-color="#0d1420"/></linearGradient></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#statsBg)"/>',
        '<text x="24" y="32" font-family="ui-monospace, \'JetBrains Mono\', Menlo, monospace" '
        'font-size="13" letter-spacing="1.5" fill="#7ec8ff">GITHUB STATS</text>',
        '<line x1="24" y1="44" x2="284" y2="44" stroke="#1c2330" stroke-width="1"/>',
        row(76, "Public Repos", repos),
        row(108, "Total Stars", stars),
        row(140, "Followers", followers),
        row(172, "Following", following),
        f'<rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="11" fill="none" stroke="#1c2330" stroke-width="1"/>',
        '</svg>',
    ]
    print("\n".join(parts))


if __name__ == "__main__":
    main()
