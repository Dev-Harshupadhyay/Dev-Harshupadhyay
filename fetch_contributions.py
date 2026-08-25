#!/usr/bin/env python3
"""
fetch_contributions.py
-----------------------
Fetches Harsh Upadhyay's public GitHub contribution calendar and saves it
as JSON so render_heatmap_svg.py can turn it into harsh-heatmap.svg.

Two strategies are used, in order:

1. GitHub's public contribution SVG at
   https://github.com/users/<username>/contributions
   This endpoint is public, requires no authentication, and no token.

2. If that request fails for any reason (rate limiting, network issues,
   markup changes), the script falls back to whatever contributions.json
   already exists in the repo, so the workflow never breaks the profile.

Output: contributions.json
  {
    "username": "Dev-Harshupadhyay",
    "generated_at": "...",
    "days": [{"date": "2026-08-24", "count": 3, "level": 2}, ...]
  }

No secrets or personal access tokens are required or read by this script.
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USERNAME = "Dev-Harshupadhyay"
OUT_PATH = Path(__file__).resolve().parent.parent / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"

# GitHub renders each day as a <td>/<rect> with a data-level (0-4) and
# data-date attribute in its public contribution graph markup.
CELL_RE = re.compile(
    r'data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*'
    r'(?:data-level="(?P<level>\d+)")?',
    re.MULTILINE,
)
COUNT_RE = re.compile(
    r'(?P<count>\d+|No) contributions? on (?P<date>[A-Za-z]+ \d{1,2}, \d{4})'
)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "profile-art-bot"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_contributions(html: str):
    days = {}

    # Preferred: tooltip text "<N> contributions on <Month D, YYYY>"
    for m in COUNT_RE.finditer(html):
        raw_count, raw_date = m.group("count"), m.group("date")
        count = 0 if raw_count == "No" else int(raw_count)
        date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
        days[date] = count

    if not days:
        return None

    # Normalize into level buckets (0-4) similar to GitHub's own scale.
    max_count = max(days.values()) or 1
    result = []
    for date in sorted(days):
        count = days[date]
        if count == 0:
            level = 0
        else:
            ratio = count / max_count
            level = min(4, max(1, round(ratio * 4)))
        result.append({"date": date, "count": count, "level": level})
    return result


def main():
    try:
        html = fetch_html(URL)
        days = parse_contributions(html)
        if not days:
            raise ValueError("no contribution cells found in response")
    except Exception as exc:  # noqa: BLE001 - fall back cleanly, never crash CI
        print(f"[fetch_contributions] live fetch failed: {exc}", file=sys.stderr)
        if OUT_PATH.exists():
            print("[fetch_contributions] keeping existing contributions.json", file=sys.stderr)
            return 0
        print("[fetch_contributions] no existing data to fall back on", file=sys.stderr)
        return 1

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"[fetch_contributions] wrote {len(days)} days to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
