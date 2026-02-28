#!/usr/bin/env python3
"""
audit_repos.py — Scan GitHub repos and produce agent config recommendations.

Checks all repos in a GitHub account for existing agent config files
and recommends what could be added to leverage AI coding ecosystems.

Usage:
    python scripts/audit_repos.py                     # audit all repos
    python scripts/audit_repos.py --owner FuMancho    # specific owner
    python scripts/audit_repos.py --output report.md  # save report
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

AGENT_FILES = [
    ("AGENTS.md", "Jules", "Machine-readable project context for autonomous agents"),
    ("JULES.md", "Jules", "Task instructions for Jules coding sessions"),
    ("CLAUDE.md", "Claude Code", "Project context for Claude Code CLI"),
    (".claude/settings.json", "Claude Code", "Permissions and tool config for Claude Code"),
    ("CODEX.md", "Codex CLI", "Project context for OpenAI Codex CLI"),
    (".codex/config.json", "Codex CLI", "Configuration for Codex CLI"),
    (".gemini/rules.md", "Gemini CLI", "Project rules for Gemini CLI sessions"),
    (".gemini/settings.json", "Gemini CLI", "Settings for Gemini CLI"),
    (".gemini/workflows/", "Gemini CLI", "Custom workflows for Gemini"),
]

ECOSYSTEM_FEATURES = {
    "Jules": [
        "Autonomous PRs — describe a task, get a PR back",
        "Swarm mode — parallel agents for large refactors",
        "Critic Agent — adversarial self-review before committing",
        "AGENTS.md — machine-readable constraints and guardrails",
        "CI/CD integration via Jules Invoke GitHub Action",
    ],
    "Claude Code": [
        "Interactive coding sessions with full repo context",
        "Tool execution (shell, file editing, browser)",
        "CLAUDE.md — persistent project memory across sessions",
        "Custom permissions via .claude/settings.json",
        "Headless mode for CI automation",
    ],
    "Gemini CLI": [
        "Interactive sessions with Gemini models",
        "Custom rules.md for project-specific guidance",
        "Reusable workflows for common tasks",
        "Multi-modal support (images, code, docs)",
        "Google ecosystem integration (Drive, Docs, Sheets)",
    ],
    "Codex CLI": [
        "Headless autonomous coding from terminal",
        "Structured output for CI integration",
        "Full sandbox execution with network access",
        "Multi-model support (o3-mini, o4-mini)",
        "CODEX.md for project-specific instructions",
    ],
}


def list_repos(owner: str) -> list[dict]:
    """List all repos for a GitHub owner."""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", owner, "--limit", "100",
             "--json", "name,description,primaryLanguage,isPrivate,updatedAt,isFork"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def check_repo_files(owner: str, repo: str) -> dict[str, bool]:
    """Check which agent config files exist in a repo."""
    found = {}
    for filepath, ecosystem, desc in AGENT_FILES:
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{owner}/{repo}/contents/{filepath}"],
                capture_output=True, text=True, timeout=10,
            )
            found[filepath] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            found[filepath] = False
    return found


def generate_recommendations(repo: dict, files: dict[str, bool]) -> list[str]:
    """Generate recommendations for a repo based on missing files."""
    recs = []
    lang = repo.get("primaryLanguage", {})
    lang_name = lang.get("name", "Unknown") if lang else "Unknown"

    # Group by ecosystem
    ecosystems_present = set()
    ecosystems_missing = set()
    for filepath, ecosystem, desc in AGENT_FILES:
        if files.get(filepath, False):
            ecosystems_present.add(ecosystem)
        else:
            ecosystems_missing.add(ecosystem)

    # Recommendations per missing ecosystem
    if "Jules" not in ecosystems_present:
        recs.append(
            f"**Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous "
            f"coding sessions. Jules can handle bug fixes, refactoring, and dependency updates "
            f"end-to-end without supervision."
        )

    if "Claude Code" not in ecosystems_present:
        recs.append(
            f"**Add Claude Code config** — Create `CLAUDE.md` for persistent project context "
            f"across interactive coding sessions. Add `.claude/settings.json` for permission "
            f"controls."
        )

    if "Gemini CLI" not in ecosystems_present:
        recs.append(
            f"**Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards "
            f"and `.gemini/workflows/` for reusable task automation."
        )

    if "Codex CLI" not in ecosystems_present:
        recs.append(
            f"**Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding "
            f"with OpenAI models."
        )

    # Special recommendations based on project type
    if lang_name == "Python":
        if not files.get("AGENTS.md", False):
            recs.append(
                "**Python-specific:** AGENTS.md should include `pytest` commands, "
                "type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting."
            )

    if repo.get("isPrivate", False):
        recs.append(
            "**Private repo:** Agent configs are especially valuable here — they provide "
            "context that can't be inferred from public docs."
        )

    return recs


def generate_report(owner: str, repos: list[dict], all_files: dict[str, dict], output_path: str | None = None) -> str:
    """Generate the full audit report."""
    lines = []
    lines.append(f"# Agent Config Audit Report — {owner}\n")
    lines.append(f"*Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Repo | Language | Jules | Claude | Gemini | Codex | Score |")
    lines.append("|---|---|---|---|---|---|---|")

    for repo in repos:
        name = repo["name"]
        lang = (repo.get("primaryLanguage") or {}).get("name", "—")
        files = all_files.get(name, {})

        jules = "✅" if files.get("AGENTS.md") or files.get("JULES.md") else "❌"
        claude = "✅" if files.get("CLAUDE.md") or files.get(".claude/settings.json") else "❌"
        gemini = "✅" if files.get(".gemini/rules.md") or files.get(".gemini/settings.json") else "❌"
        codex = "✅" if files.get("CODEX.md") or files.get(".codex/config.json") else "❌"

        score = sum(1 for v in [jules, claude, gemini, codex] if v == "✅")
        score_bar = "🟢" * score + "⚪" * (4 - score)

        lines.append(f"| **{name}** | {lang} | {jules} | {claude} | {gemini} | {codex} | {score_bar} |")

    # Per-repo detailed recommendations
    lines.append("\n## Detailed Recommendations\n")

    for repo in repos:
        name = repo["name"]
        files = all_files.get(name, {})
        recs = generate_recommendations(repo, files)

        if not recs:
            lines.append(f"### ✅ {name}\n")
            lines.append("All ecosystems configured. No action needed.\n")
        else:
            missing_count = len(recs)
            lines.append(f"### 🔧 {name} ({missing_count} recommendation{'s' if missing_count != 1 else ''})\n")
            for rec in recs:
                lines.append(f"- {rec}")
            lines.append("")

            # Quick-fix command
            lines.append(f"**Quick fix:**")
            lines.append(f"```bash")
            lines.append(f"python scripts/generate_boilerplates.py --github {owner}/{name}")
            lines.append(f"```\n")

    # Ecosystem feature reference
    lines.append("## Ecosystem Feature Reference\n")
    for ecosystem, features in ECOSYSTEM_FEATURES.items():
        lines.append(f"### {ecosystem}\n")
        for feat in features:
            lines.append(f"- {feat}")
        lines.append("")

    report = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"\n📄 Report saved to {output_path}")

    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit GitHub repos for agent config files.")
    ap.add_argument("--owner", type=str, default="FuMancho", help="GitHub owner (default: FuMancho).")
    ap.add_argument("--output", type=str, help="Save report to file.")
    ap.add_argument("--skip-docs", action="store_true", help="Skip *Docs repos and DocMaintainer.")
    ap.add_argument("--quick", action="store_true", help="Skip API file checks, just list repos.")
    args = ap.parse_args()

    print(f"🔍 Auditing repos for {args.owner}...\n")

    repos = list_repos(args.owner)
    if not repos:
        print("ERROR: No repos found or gh CLI not authenticated.", file=sys.stderr)
        sys.exit(1)

    # Filter out docs repos if requested
    if args.skip_docs:
        docs_names = {"DocMaintainer", "ClaudeCodeDocs", "GeminiDocs", "CodexDocs", "AntigravityDocs", "JulesDocs"}
        repos = [r for r in repos if r["name"] not in docs_names]

    # Sort by update time (most recent first)
    repos.sort(key=lambda r: r.get("updatedAt", ""), reverse=True)

    print(f"Found {len(repos)} repo(s)\n")

    # Check each repo for agent files
    all_files: dict[str, dict] = {}
    for i, repo in enumerate(repos):
        name = repo["name"]
        lang = (repo.get("primaryLanguage") or {}).get("name", "—")
        private = "🔒" if repo.get("isPrivate") else "🌐"
        print(f"  [{i+1}/{len(repos)}] {private} {name} ({lang})")

        if args.quick:
            all_files[name] = {}
        else:
            files = check_repo_files(args.owner, name)
            all_files[name] = files
            found = [f for f, v in files.items() if v]
            if found:
                print(f"         Found: {', '.join(found)}")
            else:
                print(f"         No agent config files")

    # Generate report
    report = generate_report(args.owner, repos, all_files, args.output)

    if not args.output:
        print(f"\n{report}")

    # Summary stats
    total = len(repos)
    configured = sum(1 for name in all_files if any(all_files[name].values()))
    print(f"\n{'=' * 40}")
    print(f"  {configured}/{total} repos have agent configs")
    print(f"  {total - configured} repos need attention")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    main()
