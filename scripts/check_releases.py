#!/usr/bin/env python3
"""
check_releases.py — Monitor upstream GitHub repos for new releases.

Checks Atom feeds for new tags/releases and triggers Jules sessions
for affected documentation repos.

Usage:
    python scripts/check_releases.py                  # check all feeds
    python scripts/check_releases.py --dry-run        # preview only
    python scripts/check_releases.py --repo GeminiDocs # check single repo
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "last_releases.json"
REPOS_FILE = ROOT / "repos.json"


def load_feeds() -> dict:
    """Load feed configs from central repos.json."""
    with open(REPOS_FILE) as f:
        raw = json.load(f)
    feeds = {}
    for name, cfg in raw.items():
        feeds[name] = {
            "name": cfg.get("tool_name", name),
            "feed_url": cfg.get("feed_url", ""),
            "disabled": cfg.get("feed_disabled", False) or not cfg.get("feed_url"),
        }
    return feeds


FEEDS = load_feeds()

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch_latest_release(feed_url: str) -> dict | None:
    """Fetch the latest entry from a GitHub Atom feed."""
    try:
        req = urllib.request.Request(
            feed_url,
            headers={"User-Agent": "DocMaintainer-ReleaseWatcher/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read().decode()
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  ⚠️ Feed fetch failed: {e}", file=sys.stderr)
        return None

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"  ⚠️ XML parse error: {e}", file=sys.stderr)
        return None

    entry = root.find(f"{ATOM_NS}entry")
    if entry is None:
        return None

    title_el = entry.find(f"{ATOM_NS}title")
    link_el = entry.find(f"{ATOM_NS}link")
    updated_el = entry.find(f"{ATOM_NS}updated")
    tag_id_el = entry.find(f"{ATOM_NS}id")

    return {
        "title": title_el.text if title_el is not None else "unknown",
        "url": link_el.get("href", "") if link_el is not None else "",
        "updated": updated_el.text if updated_el is not None else "",
        "tag_id": tag_id_el.text if tag_id_el is not None else "",
    }


def load_state() -> dict:
    """Load the last-known release state from disk."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    """Save the release state to disk."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main() -> None:
    ap = argparse.ArgumentParser(description="Check for new upstream releases.")
    ap.add_argument("--dry-run", action="store_true", help="Preview without updating state.")
    ap.add_argument("--repo", choices=list(FEEDS.keys()), help="Check a single repo.")
    ap.add_argument("--output-json", action="store_true", help="Output changed repos as JSON.")
    args = ap.parse_args()

    targets = {args.repo: FEEDS[args.repo]} if args.repo else FEEDS
    state = load_state()
    changed: list[str] = []
    now = datetime.now(timezone.utc).isoformat()

    for repo_name, feed_info in targets.items():
        print(f"Checking {feed_info['name']} ({repo_name})...")

        if feed_info.get("disabled"):
            print(f"  ⏭️ Skipped (no public release feed)\n")
            continue

        latest = fetch_latest_release(feed_info["feed_url"])

        if latest is None:
            print(f"  ⚠️ No release data found\n")
            continue

        prev = state.get(repo_name, {})
        prev_tag = prev.get("tag_id", "")

        if latest["tag_id"] != prev_tag:
            print(f"  🆕 New release: {latest['title']}")
            print(f"     Previous: {prev.get('title', 'none')}")
            print(f"     URL: {latest['url']}")
            changed.append(repo_name)

            if not args.dry_run:
                state[repo_name] = {
                    "tag_id": latest["tag_id"],
                    "title": latest["title"],
                    "url": latest["url"],
                    "updated": latest["updated"],
                    "last_checked": now,
                    "last_triggered": now,
                }
        else:
            print(f"  ✅ No change (latest: {latest['title']})")
            if not args.dry_run:
                state.setdefault(repo_name, {})["last_checked"] = now
        print()

    if not args.dry_run:
        save_state(state)
        print(f"State saved to {DATA_FILE}")

    if args.output_json:
        print(json.dumps({"changed": changed}))
    else:
        if changed:
            print(f"\n📦 Repos with new releases: {', '.join(changed)}")
        else:
            print("\n✅ All repos up to date — no new releases detected.")

    # Exit code: 0 = changes found, 1 = no changes (for CI logic)
    sys.exit(0 if changed else 1)


if __name__ == "__main__":
    main()
