#!/usr/bin/env python3
"""
health_check.py — Audit all documentation repos for consistency and quality.

Checks:
  - Stub/empty files (< 15 lines)
  - Missing standard docs (getting-started, features, commands, changelog, official-links)
  - VERSION.md freshness
  - Internal link validation
  - Cross-repo doc count comparison

Usage:
    python scripts/health_check.py                  # check all repos
    python scripts/health_check.py --repo GeminiDocs # single repo
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPOS_FILE = ROOT / "repos.json"

STANDARD_DOCS = [
    "getting-started.md",
    "features.md",
    "commands.md",
    "changelog.md",
    "official-links.md",
]

STUB_MARKERS = ["pending", "todo", "placeholder", "stub", "coming soon", "tbd"]
MIN_LINES = 15


def load_repos() -> dict:
    with open(REPOS_FILE) as f:
        return json.load(f)


def check_repo(repo_name: str) -> dict:
    """Run all health checks on a single repo."""
    repo_dir = ROOT / repo_name
    docs_dir = repo_dir / "docs"
    issues: list[str] = []
    warnings: list[str] = []
    stats: dict = {}

    # Check repo exists
    if not repo_dir.exists():
        return {"issues": [f"❌ Repository directory not found: {repo_dir}"], "warnings": [], "stats": {}}

    # Check docs/ exists
    if not docs_dir.exists():
        return {"issues": [f"❌ No docs/ directory"], "warnings": [], "stats": {}}

    # Get all md files
    md_files = sorted(docs_dir.glob("*.md"))
    stats["doc_count"] = len(md_files)
    stats["total_lines"] = 0

    # Check for standard docs
    existing = {f.name for f in md_files}
    for std in STANDARD_DOCS:
        if std not in existing:
            warnings.append(f"⚠️ Missing standard doc: docs/{std}")

    # Check each file
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            content = md_file.read_text(encoding="utf-8", errors="replace")

        lines = content.strip().split("\n")
        line_count = len(lines)
        stats["total_lines"] += line_count

        # Stub detection
        if line_count < MIN_LINES:
            issues.append(f"🔴 Stub file: docs/{md_file.name} ({line_count} lines)")

        # Marker detection
        content_lower = content.lower()
        for marker in STUB_MARKERS:
            if marker in content_lower:
                warnings.append(f"⚠️ Placeholder marker '{marker}' in docs/{md_file.name}")
                break

        # Internal link validation
        links = re.findall(r'\[.*?\]\(\./([^)]+)\)', content)
        for link in links:
            link_path = link.split("#")[0]  # strip anchors
            if not (docs_dir / link_path).exists():
                issues.append(f"🔴 Broken link: docs/{md_file.name} → ./{link_path}")

    # Check VERSION.md
    version_file = repo_dir / "VERSION.md"
    if version_file.exists():
        version_content = version_file.read_text(encoding="utf-8")
        if "pending" in version_content.lower() or "unknown" in version_content.lower():
            warnings.append("⚠️ VERSION.md has unresolved fields")
    else:
        issues.append("🔴 Missing VERSION.md")

    # Check JULES.md
    jules_file = repo_dir / "JULES.md"
    if not jules_file.exists():
        warnings.append("⚠️ Missing JULES.md")

    return {"issues": issues, "warnings": warnings, "stats": stats}


def main() -> None:
    ap = argparse.ArgumentParser(description="Health check all doc repos.")
    ap.add_argument("--repo", type=str, help="Check a single repo.")
    ap.add_argument("--json", action="store_true", help="Output as JSON.")
    args = ap.parse_args()

    repos = load_repos()
    targets = {args.repo: repos[args.repo]} if args.repo else repos

    all_results = {}
    total_issues = 0
    total_warnings = 0

    for repo_name in targets:
        result = check_repo(repo_name)
        all_results[repo_name] = result
        total_issues += len(result["issues"])
        total_warnings += len(result["warnings"])

    if args.json:
        print(json.dumps(all_results, indent=2))
        return

    # Pretty print
    print(f"\n{'='*60}")
    print(f"  📋 Documentation Health Report")
    print(f"{'='*60}\n")

    for repo_name, result in all_results.items():
        stats = result["stats"]
        status = "✅" if not result["issues"] else "❌"
        print(f"{status} {repo_name}")
        if stats:
            print(f"   📄 {stats.get('doc_count', 0)} docs, {stats.get('total_lines', 0)} total lines")

        for issue in result["issues"]:
            print(f"   {issue}")
        for warning in result["warnings"]:
            print(f"   {warning}")
        print()

    # Summary
    print(f"{'='*60}")
    print(f"  Summary: {total_issues} issue(s), {total_warnings} warning(s)")

    # Cross-repo comparison
    counts = {name: r["stats"].get("doc_count", 0) for name, r in all_results.items()}
    if counts:
        max_count = max(counts.values())
        min_count = min(counts.values())
        if max_count - min_count > 3:
            print(f"  ⚠️ Doc count imbalance: {dict(counts)}")

    print(f"{'='*60}")
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
