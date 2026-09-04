#!/usr/bin/env python3
"""
Fetches the public contribution calendar for GITHUB_USER from
https://github.com/users/<user>/contributions — the same HTML fragment
GitHub's own profile page uses. No GraphQL API, no personal access token.

Writes data/contributions.json with the raw daily counts plus a few
derived stats (current streak, longest streak, best day, monthly totals)
that render_heatmap_svg.py and make_info_card.py can use.
"""
import json
import os
import sys
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

GITHUB_USER = os.environ.get("GITHUB_PROFILE_USER", "Dev-Harshupadhyay")
URL = f"https://github.com/users/{GITHUB_USER}/contributions"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as a <td> with data-date / data-level, or
    # an <li>/<rect> with data-date + tooltip depending on markup version.
    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")
    for cell in cells:
        d = cell.get("data-date")
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
        if d is None:
            continue
        count = None
        if count_attr is not None:
            try:
                count = int(count_attr)
            except ValueError:
                count = None
        days.append(
            {
                "date": d,
                "level": int(level) if level is not None else None,
                "count": count,
            }
        )
    return days


def derive_stats(days):
    days_sorted = sorted(days, key=lambda x: x["date"])
    counts = [d["count"] or 0 for d in days_sorted]

    longest = current = 0
    running = 0
    for c in counts:
        if c > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = trailing run ending today
    for c in reversed(counts):
        if c > 0:
            current += 1
        else:
            break

    best = max(days_sorted, key=lambda x: x["count"] or 0, default=None)
    total = sum(counts)

    monthly = {}
    for d in days_sorted:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + (d["count"] or 0)

    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    days = fetch_days()
    if not days:
        print(f"warning: no contribution cells parsed for {GITHUB_USER}", file=sys.stderr)
    stats = derive_stats(days) if days else {}
    out = {"user": GITHUB_USER, "days": days, "stats": stats}

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote data/contributions.json ({len(days)} days)")


if __name__ == "__main__":
    main()
  
