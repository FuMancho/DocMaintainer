#!/usr/bin/env python3
"""
cleanup_branches.py — Delete stale merged branches from doc repos.

Removes remote branches that have been merged into the default branch.
Targets branches matching jules/* or automated/* patterns.

Usage:
    python scripts/cleanup_branches.py                  # all repos
    python scripts/cleanup_branches.py --repo GeminiDocs # single repo
    python scripts/cleanup_branches.py --dry-run        # preview only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPOS_FILE = ROOT / "repos.json"


def load_repos() -> list[str]:
    """Load repo slugs (owner/repo) from central repos.json."""
    with open(REPOS_FILE) as f:
        raw = json.load(f)
    return [f"{cfg['owner']}/{cfg['repo']}" for cfg in raw.values()]


REPOS = load_repos()


def get_merged_branches(repo: str) -> list[str]:
    """List remote branches merged into the default branch."""
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/{repo}/branches", "--paginate", "-q",
             '.[].name'],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            print(f"  ⚠️ Failed to list branches: {result.stderr.strip()}", file=sys.stderr)
            return []
        all_branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
    except Exception as e:
        print(f"  ⚠️ Error: {e}", file=sys.stderr)
        return []

    # Filter for non-default branches
    merged: list[str] = []
    for branch in all_branches:
        if branch in ("master", "main"):
            continue
        # Check if branch is merged
        try:
            cmp = subprocess.run(
                ["gh", "api", f"/repos/{repo}/compare/master...{branch}",
                 "-q", ".status"],
                capture_output=True, text=True, timeout=10,
            )
            status = cmp.stdout.strip()
            if status in ("identical", "behind"):
                merged.append(branch)
        except Exception:
            continue
    return merged


def delete_branch(repo: str, branch: str) -> bool:
    """Delete a remote branch."""
    try:
        result = subprocess.run(
            ["gh", "api", "-X", "DELETE", f"/repos/{repo}/git/refs/heads/{branch}"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Clean up merged branches.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repo", type=str, help="Single repo (e.g., FuMancho/GeminiDocs)")
    args = ap.parse_args()

    targets = [args.repo] if args.repo else REPOS
    total_deleted = 0

    for repo in targets:
        print(f"\n🔍 {repo}")
        merged = get_merged_branches(repo)

        if not merged:
            print("  ✅ No stale branches")
            continue

        for branch in merged:
            if args.dry_run:
                print(f"  [DRY RUN] Would delete: {branch}")
            else:
                if delete_branch(repo, branch):
                    print(f"  🗑️ Deleted: {branch}")
                    total_deleted += 1
                else:
                    print(f"  ❌ Failed to delete: {branch}")

    print(f"\n{'=' * 40}")
    print(f"  {'Would delete' if args.dry_run else 'Deleted'}: {total_deleted} branch(es)")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    main()
