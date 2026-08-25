#!/usr/bin/env python3
"""
render_languages_svg.py — themed top-languages card from fetch_stats.py's
JSON (stdin), counting repos-per-language (a simple, honest proxy since the
per-byte language breakdown requires one extra API call per repo).

Usage:
    cat data/stats.json | python scripts/render_languages_svg.py > harsh-languages.svg
"""
import json
import sys

WIDTH, HEIGHT = 380, 200
BAR_COLORS = ["#7ec8ff", "#4a90c9", "#3a6fa5", "#2a5580", "#1c3a52"]


def load():
    raw = sys.stdin.read().strip()
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}


def main():
    data = load()
    languages = data.get("languages", {})
    top = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)[:5]
    total = sum(v for _, v in top) or 1

    parts = [
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        'fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Top languages for Harsh Upadhyay">',
        '<defs><linearGradient id="langBg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0a0d13"/><stop offset="1" stop-color="#0d1420"/></linearGradient></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#langBg)"/>',
        '<text x="24" y="32" font-family="ui-monospace, \'JetBrains Mono\', Menlo, monospace" '
        'font-size="13" letter-spacing="1.5" fill="#7ec8ff">TOP LANGUAGES</text>',
        '<line x1="24" y1="44" x2="356" y2="44" stroke="#1c2330" stroke-width="1"/>',
    ]

    if not top:
        parts.append(
            '<text x="24" y="80" font-family="ui-monospace, monospace" font-size="12" '
            'fill="#5c7a95">no public language data yet</text>'
        )
    else:
        y = 70
        for i, (lang, count) in enumerate(top):
            pct = count / total
            bar_w = int(240 * pct)
            color = BAR_COLORS[i % len(BAR_COLORS)]
            parts.append(
                f'<text x="24" y="{y}" font-family="ui-monospace, monospace" font-size="12" fill="#dbe6f0">{lang}</text>'
            )
            parts.append(
                f'<rect x="24" y="{y+8}" width="240" height="8" rx="4" fill="#141c26"/>'
            )
            parts.append(
                f'<rect x="24" y="{y+8}" width="{bar_w}" height="8" rx="4" fill="{color}"/>'
            )
            parts.append(
                f'<text x="272" y="{y}" font-family="ui-monospace, monospace" font-size="11" '
                f'fill="#5c7a95">{round(pct*100)}%</text>'
            )
            y += 30

    parts.append(f'<rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="11" fill="none" stroke="#1c2330" stroke-width="1"/>')
    parts.append('</svg>')
    print("\n".join(parts))


if __name__ == "__main__":
    main()
