#!/usr/bin/env python3
"""
render_trophies_svg.py — a small set of self-generated milestone badges
derived only from real numbers in fetch_stats.py's JSON output (stdin).
These are honest thresholds, not GitHub's own trophy service and not
invented achievements.

Usage:
    cat data/stats.json | python scripts/render_trophies_svg.py > harsh-trophies.svg
"""
import json
import sys

WIDTH, HEIGHT = 620, 130


def load():
    raw = sys.stdin.read().strip()
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


def badge(label, value, unlocked):
    color = "#7ec8ff" if unlocked else "#2a3446"
    text_color = "#0a0d13" if unlocked else "#5c7a95"
    return (label, value, color, text_color, unlocked)


def main():
    def as_int(v):
        return v if isinstance(v, int) else 0

    data = load()
    repos = as_int(data.get("public_repos", 0))
    stars = as_int(data.get("stars", 0))
    followers = as_int(data.get("followers", 0))

    badges = [
        badge("FIRST REPO", "1+ repos", repos >= 1),
        badge("BUILDER", "5+ repos", repos >= 5),
        badge("STARRED", "1+ stars", stars >= 1),
        badge("CONNECTED", "1+ followers", followers >= 1),
    ]

    parts = [
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        'fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Milestones for Harsh Upadhyay">',
        '<defs><linearGradient id="trophyBg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0a0d13"/><stop offset="1" stop-color="#0d1420"/></linearGradient></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#trophyBg)"/>',
        '<text x="24" y="28" font-family="ui-monospace, \'JetBrains Mono\', Menlo, monospace" '
        'font-size="13" letter-spacing="1.5" fill="#7ec8ff">MILESTONES</text>',
    ]

    x = 24
    for label, value, color, text_color, unlocked in badges:
        w = 130
        opacity = "1" if unlocked else "0.5"
        parts.append(f'<g transform="translate({x},50)" opacity="{opacity}">')
        parts.append(f'<rect width="{w}" height="60" rx="8" fill="#12161d" stroke="{color}" stroke-width="1.5"/>')
        parts.append(
            f'<text x="10" y="24" font-family="ui-monospace, monospace" font-size="10" '
            f'letter-spacing="1" fill="{color}">{label}</text>'
        )
        parts.append(
            f'<text x="10" y="44" font-family="ui-monospace, monospace" font-size="12" fill="#dbe6f0">{value}</text>'
        )
        parts.append('</g>')
        x += w + 12

    parts.append(f'<rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="11" fill="none" stroke="#1c2330" stroke-width="1"/>')
    parts.append('</svg>')
    print("\n".join(parts))


if __name__ == "__main__":
    main()
