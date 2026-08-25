#!/usr/bin/env python3
"""
fetch_contributions.py

Scrapes the public, unauthenticated contribution calendar page that GitHub
serves at https://github.com/users/<username>/contributions and writes the
daily contribution counts out as JSON.

No personal access token is required because this page is public HTML,
not the GraphQL API. This keeps the workflow secret-free.

Usage:
    python scripts/fetch_contributions.py Dev-Harshupadhyay > data/contributions.json
"""
import json
import re
import sys
import urllib.request

USERNAME_DEFAULT = "Dev-Harshupadhyay"


def fetch_contribution_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "harsh-profile-bot"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_contributions(html: str):
    """
    Each day cell on that page is rendered as a <td> with a data-date
    attribute and either a data-level attribute (0-4) or an inline
    fill color we can map to a level. We only depend on data-date and
    data-level, both of which are stable, documented rendering hooks
    GitHub itself uses for this page.
    """
    cell_pattern = re.compile(
        r'data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*data-level="(?P<level>\d)"'
    )
    days = []
    for match in cell_pattern.finditer(html):
        days.append({"date": match.group("date"), "level": int(match.group("level"))})

    if not days:
        # Fallback older markup: data-count instead of data-level
        alt_pattern = re.compile(
            r'data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*data-count="(?P<count>\d+)"'
        )
        for match in alt_pattern.finditer(html):
            count = int(match.group("count"))
            level = 0 if count == 0 else 1 if count < 3 else 2 if count < 6 else 3 if count < 10 else 4
            days.append({"date": match.group("date"), "level": level})

    return days


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME_DEFAULT
    try:
        html = fetch_contribution_html(username)
        days = parse_contributions(html)
    except Exception as exc:  # network unavailable, GitHub markup changed, etc.
        print(json.dumps({"username": username, "days": [], "error": str(exc)}), file=sys.stdout)
        sys.exit(0)

    print(json.dumps({"username": username, "days": days}))


if __name__ == "__main__":
    main()
