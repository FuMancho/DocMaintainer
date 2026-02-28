#!/usr/bin/env python3
"""
sync_repos.py — Git add/commit/push across all doc repos in one command.

Usage:
    python scripts/sync_repos.py -m "docs: update all repos"          # all repos
    python scripts/sync_repos.py --repo GeminiDocs -m "docs: fix"     # single repo
    python scripts/sync_repos.py --dry-run -m "test message"          # preview only
    python scripts/sync_repos.py --status                             # check git status
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPOS_FILE = ROOT / "repos.json"


def load_repos() -> dict:
    with open(REPOS_FILE) as f:
        return json.load(f)


def run_git(repo_dir: Path, args: list[str], timeout: int = 30) -> tuple[int, str]:
    """Run a git command in a repo directory."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(repo_dir),
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode, result.stdout.strip() + result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "Timed out"
    except Exception as e:
        return -1, str(e)


def git_status(repo_dir: Path) -> str:
    """Get short git status."""
    code, out = run_git(repo_dir, ["status", "--porcelain"])
    return out if out else "(clean)"


def sync_repo(repo_name: str, message: str, dry_run: bool = False) -> bool:
    """Add, commit, and push a single repo."""
    repo_dir = ROOT / repo_name
    if not repo_dir.exists():
        print(f"  ❌ Directory not found: {repo_dir}")
        return False

    # Check if there are changes
    status = git_status(repo_dir)
    if status == "(clean)":
        print(f"  ✅ No changes")
        return True

    if dry_run:
        print(f"  [DRY RUN] Would commit and push:")
        for line in status.split("\n")[:10]:
            print(f"    {line}")
        return True

    # git add -A
    code, out = run_git(repo_dir, ["add", "-A"])
    if code != 0:
        print(f"  ❌ git add failed: {out}")
        return False

    # git commit
    code, out = run_git(repo_dir, ["commit", "-m", message])
    if code != 0:
        print(f"  ❌ git commit failed: {out}")
        return False
    print(f"  📝 Committed: {message}")

    # git push
    code, out = run_git(repo_dir, ["push"], timeout=60)
    if code != 0:
        print(f"  ❌ git push failed: {out}")
        return False
    print(f"  🚀 Pushed to remote")

    return True


def show_status(repos: dict) -> None:
    """Show git status for all repos."""
    print(f"\n{'='*50}")
    print(f"  📋 Git Status Report")
    print(f"{'='*50}\n")

    for repo_name in repos:
        repo_dir = ROOT / repo_name
        if not repo_dir.exists():
            print(f"❌ {repo_name}: directory not found")
            continue
        status = git_status(repo_dir)
        icon = "✅" if status == "(clean)" else "📝"
        print(f"{icon} {repo_name}")
        if status != "(clean)":
            for line in status.split("\n")[:5]:
                print(f"   {line}")
        print()

    # Also check DocMaintainer itself
    status = git_status(ROOT)
    icon = "✅" if status == "(clean)" else "📝"
    print(f"{icon} DocMaintainer (parent)")
    if status != "(clean)":
        for line in status.split("\n")[:5]:
            print(f"   {line}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync all doc repos (add/commit/push).")
    ap.add_argument("-m", "--message", type=str, help="Commit message.")
    ap.add_argument("--repo", type=str, help="Sync a single repo.")
    ap.add_argument("--dry-run", action="store_true", help="Preview without committing.")
    ap.add_argument("--status", action="store_true", help="Show git status only.")
    ap.add_argument("--include-parent", action="store_true", help="Also sync DocMaintainer itself.")
    args = ap.parse_args()

    repos = load_repos()

    if args.status:
        show_status(repos)
        return

    if not args.message:
        print("Error: --message / -m is required for sync.", file=sys.stderr)
        sys.exit(1)

    targets = {args.repo: repos[args.repo]} if args.repo else repos
    results: dict[str, bool] = {}

    print(f"\n{'='*50}")
    print(f"  🔄 Syncing {len(targets)} repo(s)")
    print(f"{'='*50}\n")

    for repo_name in targets:
        print(f"📦 {repo_name}")
        results[repo_name] = sync_repo(repo_name, args.message, dry_run=args.dry_run)
        print()

    # Optionally sync parent
    if args.include_parent:
        print(f"📦 DocMaintainer (parent)")
        results["DocMaintainer"] = sync_repo(".", args.message, dry_run=args.dry_run)
        print()

    # Summary
    ok = sum(1 for v in results.values() if v)
    fail = sum(1 for v in results.values() if not v)
    print(f"{'='*50}")
    print(f"  ✅ {ok} synced, ❌ {fail} failed")
    print(f"{'='*50}")

    sys.exit(1 if fail > 0 else 0)


if __name__ == "__main__":
    main()
