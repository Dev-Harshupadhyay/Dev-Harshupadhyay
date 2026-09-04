#!/usr/bin/env python3
"""
Fetches the public contribution calendar for GITHUB_USER.

Two sources, tried in order:

1. github-contributions-api.jogruber.de — a public mirror of the
   contribution graph. No token, no auth, stable JSON. This is the
   primary source because GitHub's own /contributions fragment is now
   rendered client-side and scraping it silently yields zero cells,
   which is what made the old daily workflow fail.
2. Scraping https://github.com/users/<user>/contributions as a
   fallback, in case the mirror is unreachable.

No GraphQL API and no personal access token is required either way.

Writes data/contributions.json with the raw daily counts plus a few
derived stats (current streak, longest streak, best day, monthly totals)
that render_heatmap_svg.py and make_info_card.py can use.
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

GITHUB_USER = os.environ.get("GITHUB_PROFILE_USER", "Dev-Harshupadhyay")
API = "https://github-contributions-api.jogruber.de/v4/{user}?y={year}"


def level_for(count, max_count):
    if not count:
        return 0
    if max_count <= 0:
        return 1
    r = count / max_count
    if r <= 0.25:
        return 1
    if r <= 0.5:
        return 2
    if r <= 0.75:
        return 3
    return 4


def fetch_from_api(year):
    """Returns a list of {date, level, count} or [] if unavailable."""
    resp = requests.get(
        API.format(user=GITHUB_USER, year=year),
        headers={"User-Agent": "profile-readme-bot"},
        timeout=25,
    )
    resp.raise_for_status()
    payload = resp.json()
    raw = payload.get("contributions") or []
    days = [
        {"date": d["date"], "count": int(d.get("count") or 0)}
        for d in raw
        if d.get("date")
    ]
    if not days:
        return []
    peak = max(d["count"] for d in days)
    for d in days:
        d["level"] = level_for(d["count"], peak)
    return days


def fetch_from_html():
    """Legacy scrape of the contributions fragment. Often returns []."""
    url = f"https://github.com/users/{GITHUB_USER}/contributions"
    resp = requests.get(url, headers={"User-Agent": "profile-readme-bot"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")
    for cell in cells:
        d = cell.get("data-date")
        if d is None:
            continue
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
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


def fetch_days():
    year = datetime.now(timezone.utc).year
    try:
        days = fetch_from_api(year)
        if days:
            print(f"source: contributions API ({len(days)} days, {year})")
            return days
        print("warning: API returned no days", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 - fall through to the scrape
        print(f"warning: API failed ({exc}), trying HTML scrape", file=sys.stderr)

    try:
        days = fetch_from_html()
        if days:
            print(f"source: HTML scrape ({len(days)} days)")
            return days
    except Exception as exc:  # noqa: BLE001
        print(f"warning: HTML scrape failed ({exc})", file=sys.stderr)
    return []


def derive_stats(days):
    days_sorted = sorted(days, key=lambda x: x["date"])
    counts = [d["count"] or 0 for d in days_sorted]

    longest = current = running = 0
    for c in counts:
        if c > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = trailing run of days ending at the last entry
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
        "active_days": sum(1 for c in counts if c > 0),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main():
    days = fetch_days()
    if not days:
        print(f"warning: no contribution data for {GITHUB_USER}", file=sys.stderr)
    stats = derive_stats(days) if days else {}
    out = {"user": GITHUB_USER, "days": days, "stats": stats}

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(
        f"wrote data/contributions.json ({len(days)} days, "
        f"total={stats.get('total_last_year', 0)})"
    )


if __name__ == "__main__":
    main()
