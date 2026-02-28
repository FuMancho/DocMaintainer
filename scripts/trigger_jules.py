#!/usr/bin/env python3
"""
trigger_jules.py — Create Jules sessions for all documentation repos.

Uses the Jules REST API (v1alpha) to kick off documentation update tasks.
Requires the JULES_API_KEY environment variable to be set.

Usage:
    python scripts/trigger_jules.py                    # all repos
    python scripts/trigger_jules.py --repo GeminiDocs  # single repo
    python scripts/trigger_jules.py --auto-merge       # create + poll + merge
    python scripts/trigger_jules.py --dry-run          # preview without sending
"""

import argparse
import json
import os
import subprocess
import sys
import time
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
            "files, validate links using the link audit report, update docs/changelog.md "
            "with any new release notes found, and commit with the standard message format: "
            "'docs: weekly documentation update [automated]'."
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
            "files, validate links using the link audit report, update docs/changelog.md "
            "with any new release notes found, and commit with the standard message format: "
            "'docs: weekly documentation update [automated]'."
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
            "files, validate links using the link audit report, update docs/changelog.md "
            "with any new release notes found, and commit with the standard message format: "
            "'docs: weekly documentation update [automated]'."
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

# Session states that mean "still working"
ACTIVE_STATES = {"STATE_UNSPECIFIED", "ACTIVE", "WAITING_FOR_USER"}
# Session states that mean "done"
TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


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
    sources: list[dict] = []
    page_token: str | None = None
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


def get_session(api_key: str, session_id: str) -> dict:
    """Get the current state of a Jules session."""
    return jules_request(f"/sessions/{session_id}", api_key)


def poll_sessions(
    api_key: str,
    session_ids: dict[str, str],
    poll_interval: int = 60,
    timeout: int = 3600,
) -> dict[str, dict]:
    """
    Poll multiple sessions until they all reach a terminal state.

    Args:
        api_key: Jules API key
        session_ids: {repo_name: session_id}
        poll_interval: seconds between polls
        timeout: max seconds to wait

    Returns:
        {repo_name: session_data}
    """
    start = time.time()
    completed: dict[str, dict] = {}
    pending = dict(session_ids)

    print(f"\n⏳ Polling {len(pending)} session(s) (interval={poll_interval}s, timeout={timeout}s)...")

    while pending and (time.time() - start) < timeout:
        for repo_name, sid in list(pending.items()):
            try:
                session = get_session(api_key, sid)
                state = session.get("state", "UNKNOWN")

                if state in TERMINAL_STATES:
                    completed[repo_name] = session
                    del pending[repo_name]
                    pr_url = extract_pr_url(session)
                    status = "✅" if state == "COMPLETED" else "❌"
                    print(f"  {status} {repo_name}: {state}" +
                          (f" → {pr_url}" if pr_url else ""))
                else:
                    elapsed = int(time.time() - start)
                    print(f"  ⏳ {repo_name}: {state} ({elapsed}s elapsed)")
            except Exception as e:
                print(f"  ⚠️ {repo_name}: poll error — {e}", file=sys.stderr)

        if pending:
            time.sleep(poll_interval)

    # Timed-out sessions
    for repo_name in pending:
        print(f"  ⏰ {repo_name}: TIMED OUT after {timeout}s", file=sys.stderr)
        completed[repo_name] = {"state": "TIMED_OUT", "id": pending[repo_name]}

    return completed


def extract_pr_url(session: dict) -> str | None:
    """Extract the PR URL from a completed session."""
    for output in session.get("outputs", []):
        pr = output.get("pullRequest", {})
        url = pr.get("url")
        if url:
            return url
    return None


def merge_pr(pr_url: str, gh_token: str | None = None) -> bool:
    """Merge a GitHub PR using the gh CLI."""
    env = os.environ.copy()
    if gh_token:
        env["GH_TOKEN"] = gh_token

    try:
        result = subprocess.run(
            ["gh", "pr", "merge", pr_url, "--merge", "--delete-branch"],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"  🔀 Merged: {pr_url}")
            return True
        else:
            print(f"  ❌ Merge failed: {result.stderr.strip()}", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("  ❌ 'gh' CLI not found. Install: https://cli.github.com", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ Merge timed out for {pr_url}", file=sys.stderr)
        return False


def main() -> None:
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
    ap.add_argument(
        "--auto-merge",
        action="store_true",
        help="After creating sessions, poll until complete and auto-merge PRs.",
    )
    ap.add_argument(
        "--poll-interval",
        type=int,
        default=60,
        help="Seconds between status polls when using --auto-merge (default: 60).",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Max seconds to wait for sessions when using --auto-merge (default: 3600).",
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
    source_map: dict[str, str] = {}
    if not args.dry_run:
        print("Fetching connected sources...")
        sources = list_sources(api_key)
        for src in sources:
            gh = src.get("githubRepo", {})
            key = f"{gh.get('owner', '')}/{gh.get('repo', '')}"
            source_map[key] = src["name"]
        print(f"  Found {len(sources)} source(s)\n")

    # Create sessions
    results: list[dict] = []
    session_ids: dict[str, str] = {}
    err = 0
    for repo_name, config in targets.items():
        full_name = f"{config['owner']}/{config['repo']}"
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Creating session for {full_name}...")

        if args.dry_run:
            print(f"  Source: sources/github/{full_name}")
            print(f"  Branch: {config['branch']}")
            print(f"  Title:  {config['title']}")
            print(f"  Prompt: {config['prompt'][:80]}...")
            print(f"  Auto-merge: {args.auto_merge}")
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
            session_ids[repo_name] = session_id
        except Exception as e:
            print(f"  ❌ Failed: {e}", file=sys.stderr)
            results.append({"repo": repo_name, "error": str(e), "status": "error"})
            err += 1
        print()

    # Summary
    if not args.dry_run:
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"Sessions: {ok} created, {err} failed")

    # Auto-merge: poll and merge
    if args.auto_merge and session_ids:
        completed = poll_sessions(
            api_key, session_ids, args.poll_interval, args.timeout,
        )

        gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        merged = 0
        for repo_name, session in completed.items():
            state = session.get("state", "UNKNOWN")
            if state != "COMPLETED":
                print(f"  ⏭️ {repo_name}: skipping merge (state={state})")
                continue

            pr_url = extract_pr_url(session)
            if not pr_url:
                print(f"  ⏭️ {repo_name}: no PR found in session output")
                continue

            if merge_pr(pr_url, gh_token):
                merged += 1

        print(f"\n{'=' * 40}")
        print(f"  Final: {merged} PR(s) merged")
        print(f"{'=' * 40}")

        if merged < len(session_ids):
            sys.exit(1)
    elif not args.dry_run and err > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
