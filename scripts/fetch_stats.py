#!/usr/bin/env python3
"""
fetch_stats.py

Pulls public profile + repo data from the GitHub REST API (works
unauthenticated at a low rate limit; in Actions it uses the built-in
GITHUB_TOKEN via the Authorization env var for a much higher limit —
that token is provided automatically by GitHub Actions and never
committed to the repo).

Outputs a single JSON object used by render_stats_svg.py,
render_languages_svg.py and render_trophies_svg.py.

Usage:
    python scripts/fetch_stats.py Dev-Harshupadhyay > data/stats.json
"""
import json
import os
import sys
import urllib.request

API = "https://api.github.com"


def gh_get(path, token=None):
    req = urllib.request.Request(f"{API}{path}", headers={"User-Agent": "harsh-profile-bot"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "Dev-Harshupadhyay"
    token = os.environ.get("GITHUB_TOKEN")

    try:
        user = gh_get(f"/users/{username}", token)
        repos = gh_get(f"/users/{username}/repos?per_page=100&type=owner", token)
    except Exception as exc:
        print(json.dumps({"username": username, "error": str(exc)}))
        return

    total_stars = sum(r.get("stargazers_count", 0) for r in repos if isinstance(r, dict))
    languages = {}
    for r in repos:
        if not isinstance(r, dict):
            continue
        lang = r.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    result = {
        "username": username,
        "public_repos": user.get("public_repos", len(repos)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "stars": total_stars,
        "languages": languages,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
