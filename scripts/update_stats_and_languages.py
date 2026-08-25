#!/usr/bin/env python3
"""
update_stats_and_languages.py
-------------------------------
Regenerates harsh-stats.svg and harsh-languages.svg from live public
GitHub data, keeping the same dark/blue visual identity as the rest of
the profile.

Auth: uses the GITHUB_TOKEN that GitHub Actions injects automatically
for every workflow run (read-only, scoped to the workflow). No personal
access token needs to be created or stored. When run locally without a
token, the script falls back to the GitHub REST API's low-rate
unauthenticated access, which is enough for one manual run.

Never expose or print the token value.
"""

import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

USERNAME = "Dev-Harshupadhyay"
ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"


def api_get(path):
    req = urllib.request.Request(f"{API}{path}", headers=_headers())
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-art-bot",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_profile():
    return api_get(f"/users/{USERNAME}")


def fetch_repos():
    repos, page = [], 1
    while True:
        batch = api_get(f"/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def fetch_language_breakdown(repos):
    totals = Counter()
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            langs = api_get(f"/repos/{USERNAME}/{repo['name']}/languages")
        except Exception:
            continue
        for lang, bytes_ in langs.items():
            totals[lang] += bytes_
    return totals


def render_stats_svg(profile, repos):
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    values = [
        (str(profile.get("public_repos", len(repos))), "PUBLIC REPOS"),
        (str(profile.get("followers", 0)), "FOLLOWERS"),
        (str(profile.get("following", 0)), "FOLLOWING"),
        (str(stars), "STARS EARNED"),
    ]
    cols = "".join(
        f"""
    <g transform="translate({26 + i*120},86)">
      <text x="0" y="0" font-size="30" font-weight="700" fill="{'#5b8def' if label=='STARS EARNED' else '#eef2f7'}">{val}</text>
      <text x="0" y="20" font-size="11" letter-spacing="1.5" fill="#7c8aa0">{label}</text>
    </g>"""
        for i, (val, label) in enumerate(values)
    )

    svg = f"""<svg width="480" height="220" viewBox="0 0 480 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Harsh Upadhyay GitHub statistics">
  <defs>
    <linearGradient id="statsbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1119"/>
      <stop offset="100%" stop-color="#080a0f"/>
    </linearGradient>
    <radialGradient id="statsglow" cx="90%" cy="0%" r="80%">
      <stop offset="0%" stop-color="#4f8fe8" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#4f8fe8" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="2" y="2" width="476" height="216" rx="14" fill="url(#statsbg)" stroke="#1c2431" stroke-width="1.5"/>
  <rect x="2" y="2" width="476" height="216" rx="14" fill="url(#statsglow)"/>
  <text x="26" y="38" font-family="'Cascadia Code','Fira Code',Consolas,monospace" font-size="12" letter-spacing="3" fill="#5b8def">GITHUB STATISTICS</text>
  <text x="26" y="54" font-family="'Cascadia Code','Fira Code',Consolas,monospace" font-size="9.5" fill="#4a5568">github.com/{USERNAME}</text>
  <line x1="26" y1="66" x2="454" y2="66" stroke="#1c2431" stroke-width="1"/>
  <g font-family="'Segoe UI', Helvetica, Arial, sans-serif">{cols}
  </g>
  <line x1="26" y1="140" x2="454" y2="140" stroke="#1c2431" stroke-width="1"/>
  <g transform="translate(26,150)" font-family="'Cascadia Code','Fira Code',Consolas,monospace">
    <text x="0" y="12" font-size="10.5" fill="#4a5568">LAST SYNCED</text>
    <text x="0" y="30" font-size="12.5" fill="#a9b4c6">auto-updated by GitHub Actions</text>
    <g transform="translate(0,44)">
      <circle cx="4" cy="0" r="4" fill="#4f8fe8"/>
      <text x="14" y="4" font-size="11.5" fill="#8fc2ff">live values refreshed daily</text>
    </g>
  </g>
  <text x="454" y="204" text-anchor="end" font-family="'Cascadia Code','Fira Code',Consolas,monospace" font-size="9" fill="#3a4452">source: GitHub REST API</text>
</svg>"""
    (ROOT / "harsh-stats.svg").write_text(svg)


def render_languages_svg(totals):
    if not totals:
        return
    top = totals.most_common(4)
    total_bytes = sum(v for _, v in top) or 1

    rows = ""
    for i, (lang, byte_count) in enumerate(top):
        pct = round(100 * byte_count / total_bytes)
        y = 61 + i * 30
        w = round(308 * byte_count / max(v for _, v in top))
        rows += f"""
    <text x="26" y="{y+11}">{lang}</text>
    <rect x="120" y="{y}" width="308" height="12" rx="6" fill="#161c27"/>
    <rect x="120" y="{y}" width="{w}" height="12" rx="6" fill="url(#barfill)"/>
    <text x="440" y="{y+11}" text-anchor="end" fill="#7c8aa0" font-size="11">~{pct}%</text>"""

    svg = f"""<svg width="480" height="220" viewBox="0 0 480 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Harsh Upadhyay most used languages">
  <defs>
    <linearGradient id="langbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1119"/>
      <stop offset="100%" stop-color="#080a0f"/>
    </linearGradient>
    <linearGradient id="barfill" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2f5fb0"/>
      <stop offset="100%" stop-color="#5b9dff"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="476" height="216" rx="14" fill="url(#langbg)" stroke="#1c2431" stroke-width="1.5"/>
  <text x="26" y="36" font-family="'Cascadia Code','Fira Code',Consolas,monospace" font-size="12" letter-spacing="3" fill="#5b8def">MOST USED LANGUAGES</text>
  <line x1="26" y1="48" x2="454" y2="48" stroke="#1c2431" stroke-width="1"/>
  <g font-family="'Segoe UI', Helvetica, Arial, sans-serif" font-size="12.5" fill="#c7d1e0">{rows}
  </g>
  <line x1="26" y1="180" x2="454" y2="180" stroke="#1c2431" stroke-width="1"/>
  <text x="26" y="200" font-family="'Cascadia Code','Fira Code',Consolas,monospace" font-size="9.5" fill="#3a4452">auto-updated from public repository language data</text>
</svg>"""
    (ROOT / "harsh-languages.svg").write_text(svg)


def main():
    try:
        profile = fetch_profile()
        repos = fetch_repos()
    except Exception as exc:
        print(f"[update_stats_and_languages] skipped, API unreachable: {exc}")
        return

    render_stats_svg(profile, repos)

    try:
        totals = fetch_language_breakdown(repos)
        render_languages_svg(totals)
    except Exception as exc:
        print(f"[update_stats_and_languages] language breakdown skipped: {exc}")

    print("[update_stats_and_languages] done")


if __name__ == "__main__":
    main()
