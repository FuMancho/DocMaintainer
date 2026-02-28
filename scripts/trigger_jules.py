#!/usr/bin/env python3
"""
trigger_jules.py — Create Jules sessions for all documentation repos.

Uses the Jules REST API (v1alpha) to kick off documentation update tasks.
Requires the JULES_API_KEY environment variable to be set.

Usage:
    python scripts/trigger_jules.py                 # all repos
    python scripts/trigger_jules.py --repo GeminiDocs  # single repo
    python scripts/trigger_jules.py --dry-run       # preview without sending
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://jules.googleapis.com/v1alpha"

# Repo configurations: owner/repo -> source name + prompt
REPOS = {
    "ClaudeCodeDocs": {
        "owner": "FuMancho",
        "repo": "ClaudeCodeDocs",
        "branch": "master",
        "title": "Weekly documentation update — ClaudeCodeDocs",
        "prompt": (
            "Follow the instructions in JULES.md to update this documentation repo. "
            "Run the crawler, compare scraped content against docs/, update any changed "
            "files, validate links using the link audit report, and commit with the "
            "standard message format: 'docs: weekly documentation update [automated]'."
        ),
    },
    "GeminiDocs": {
        "owner": "FuMancho",
        "repo": "GeminiDocs",
        "branch": "master",
        "title": "Weekly documentation update — GeminiDocs",
        "prompt": (
            "Follow the instructions in JULES.md to update this documentation repo. "
            "Run the crawler, compare scraped content against docs/, update any changed "
            "files, validate links using the link audit report, and commit with the "
            "standard message format: 'docs: weekly documentation update [automated]'."
        ),
    },
    "CodexDocs": {
        "owner": "FuMancho",
        "repo": "CodexDocs",
        "branch": "master",
        "title": "Weekly documentation update — CodexDocs",
        "prompt": (
            "Follow the instructions in JULES.md to update this documentation repo. "
            "Run the crawler, compare scraped content against docs/, update any changed "
            "files, validate links using the link audit report, and commit with the "
            "standard message format: 'docs: weekly documentation update [automated]'."
        ),
    },
    "AntigravityDocs": {
        "owner": "FuMancho",
        "repo": "AntigravityDocs",
        "branch": "master",
        "title": "Weekly documentation update — AntigravityDocs",
        "prompt": (
            "Follow the instructions in JULES.md to update this documentation repo. "
            "Run the crawler, compare scraped content against docs/, update any changed "
            "files, validate links using the link audit report, and commit with the "
            "standard message format: 'docs: weekly documentation update [automated]'."
        ),
    },
}


def jules_request(
    path: str,
    api_key: str,
    method: str = "GET",
    body: dict | None = None,
) -> dict:
    """Make a request to the Jules REST API."""
    url = f"{API_BASE}{path}"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  ERROR: HTTP {e.code} — {error_body}", file=sys.stderr)
        raise


def list_sources(api_key: str) -> list[dict]:
    """List all connected sources (repos)."""
    sources = []
    page_token = None
    while True:
        path = "/sources"
        if page_token:
            path += f"?pageToken={page_token}"
        result = jules_request(path, api_key)
        sources.extend(result.get("sources", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return sources


def create_session(
    api_key: str,
    source_name: str,
    branch: str,
    title: str,
    prompt: str,
) -> dict:
    """Create a new Jules session (task)."""
    body = {
        "prompt": prompt,
        "sourceContext": {
            "source": source_name,
            "githubRepoContext": {
                "startingBranch": branch,
            },
        },
        "automationMode": "AUTO_CREATE_PR",
        "title": title,
    }
    return jules_request("/sessions", api_key, method="POST", body=body)


def main():
    ap = argparse.ArgumentParser(
        description="Trigger Jules documentation update sessions.",
    )
    ap.add_argument(
        "--repo",
        type=str,
        default=None,
        choices=list(REPOS.keys()),
        help="Trigger a single repo instead of all.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be sent without making API calls.",
    )
    ap.add_argument(
        "--list-sources",
        action="store_true",
        help="List connected sources and exit.",
    )
    args = ap.parse_args()

    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("ERROR: JULES_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key from: https://jules.google.com/settings#api", file=sys.stderr)
        sys.exit(1)

    # List sources mode
    if args.list_sources:
        print("Connected sources:")
        for src in list_sources(api_key):
            print(f"  {src['name']}  ({src.get('id', '?')})")
        return

    # Determine which repos to trigger
    targets = {args.repo: REPOS[args.repo]} if args.repo else REPOS

    # Resolve source names
    if not args.dry_run:
        print("Fetching connected sources...")
        sources = list_sources(api_key)
        source_map = {}
        for src in sources:
            gh = src.get("githubRepo", {})
            key = f"{gh.get('owner', '')}/{gh.get('repo', '')}"
            source_map[key] = src["name"]
        print(f"  Found {len(sources)} source(s)\n")

    # Create sessions
    results = []
    for repo_name, config in targets.items():
        full_name = f"{config['owner']}/{config['repo']}"
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Creating session for {full_name}...")

        if args.dry_run:
            print(f"  Source: sources/github/{full_name}")
            print(f"  Branch: {config['branch']}")
            print(f"  Title:  {config['title']}")
            print(f"  Prompt: {config['prompt'][:80]}...")
            print()
            continue

        source_name = source_map.get(full_name)
        if not source_name:
            print(f"  SKIP: {full_name} not found in connected sources.", file=sys.stderr)
            print(f"  Install the Jules GitHub App on this repo first.", file=sys.stderr)
            print()
            continue

        try:
            result = create_session(
                api_key,
                source_name,
                config["branch"],
                config["title"],
                config["prompt"],
            )
            session_id = result.get("id", "?")
            print(f"  ✅ Session created: {session_id}")
            results.append({"repo": repo_name, "session_id": session_id, "status": "ok"})
        except Exception as e:
            print(f"  ❌ Failed: {e}", file=sys.stderr)
            results.append({"repo": repo_name, "error": str(e), "status": "error"})
        print()

    # Summary
    if not args.dry_run:
        ok = sum(1 for r in results if r["status"] == "ok")
        err = sum(1 for r in results if r["status"] == "error")
        print(f"Done: {ok} created, {err} failed")
        if err:
            sys.exit(1)


if __name__ == "__main__":
    main()
