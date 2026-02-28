#!/usr/bin/env python3
"""
generate_jules.py — Generate JULES.md and AGENTS.md from central repos.json config.

Reads repos.json + templates/*.j2 and produces files for each repo.

Usage:
    python scripts/generate_jules.py                   # generate all
    python scripts/generate_jules.py --repo GeminiDocs  # single repo
    python scripts/generate_jules.py --dry-run          # preview only
    python scripts/generate_jules.py --jules-only       # JULES.md only
    python scripts/generate_jules.py --agents-only      # AGENTS.md only
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPOS_FILE = ROOT / "repos.json"
TEMPLATE_FILE = ROOT / "templates" / "JULES.md.j2"
AGENTS_TEMPLATE_FILE = ROOT / "templates" / "AGENTS.md.j2"


def load_repos() -> dict:
    with open(REPOS_FILE) as f:
        return json.load(f)


def render_template(template_text: str, variables: dict) -> str:
    """Simple Jinja2-like rendering without requiring the jinja2 package.

    Supports:
    - {{ var }}
    - {{ var | join(', ') }}
    - {% for item in list %}...{% endfor %}
    """
    result = template_text

    # Handle {% for item in list %}...{% endfor %} blocks
    for_pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
    def replace_for(match):
        item_name = match.group(1)
        list_name = match.group(2)
        body = match.group(3)
        items = variables.get(list_name, [])
        output = []
        for item in items:
            line = body.replace("{{ " + item_name + " }}", str(item))
            output.append(line)
        return "".join(output)

    result = re.sub(for_pattern, replace_for, result, flags=re.DOTALL)

    # Handle {{ var | join('sep') }}
    join_pattern = r'\{\{\s*(\w+)\s*\|\s*join\([\'"]([^\'"]*)[\'\"]\)\s*\}\}'
    def replace_join(match):
        var_name = match.group(1)
        separator = match.group(2)
        val = variables.get(var_name, [])
        if isinstance(val, list):
            return separator.join(str(v) for v in val)
        return str(val)

    result = re.sub(join_pattern, replace_join, result)

    # Handle simple {{ var }}
    simple_pattern = r'\{\{\s*(\w+)\s*\}\}'
    def replace_simple(match):
        var_name = match.group(1)
        val = variables.get(var_name, "")
        return str(val)

    result = re.sub(simple_pattern, replace_simple, result)

    return result


def get_template_vars(repo_name: str, config: dict) -> dict:
    """Build the template variables dict for a repo."""
    return {
        "repo_name": repo_name,
        "tool_name": config["tool_name"],
        "tool_package": config.get("tool_package", ""),
        "start_url": config["start_url"],
        "base_path": config["base_path"],
        "official_domains": config["official_domains"],
        "github_example": config.get("github_example", ""),
        "extra_keep_domains": config.get("extra_keep_domains", []),
    }


def generate_file(template_path: Path, output_path: Path, variables: dict, dry_run: bool = False) -> str:
    """Render a template and write to output path."""
    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_template(template_text, variables)

    if dry_run:
        print(f"  [DRY RUN] Would write: {output_path}")
    else:
        output_path.write_text(rendered, encoding="utf-8")
        print(f"  ✅ {output_path.name}")

    return rendered


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate JULES.md and AGENTS.md from repos.json.")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    ap.add_argument("--repo", type=str, help="Generate for a single repo.")
    ap.add_argument("--jules-only", action="store_true", help="Only generate JULES.md.")
    ap.add_argument("--agents-only", action="store_true", help="Only generate AGENTS.md.")
    args = ap.parse_args()

    repos = load_repos()
    targets = {args.repo: repos[args.repo]} if args.repo else repos

    count = 0
    for repo_name, config in targets.items():
        variables = get_template_vars(repo_name, config)
        repo_dir = ROOT / repo_name
        if not repo_dir.exists():
            print(f"⚠️ Skipping {repo_name} — directory not found")
            continue

        print(f"📦 {repo_name}")

        if not args.agents_only:
            generate_file(TEMPLATE_FILE, repo_dir / "JULES.md", variables, args.dry_run)
            count += 1

        if not args.jules_only and AGENTS_TEMPLATE_FILE.exists():
            generate_file(AGENTS_TEMPLATE_FILE, repo_dir / "AGENTS.md", variables, args.dry_run)
            count += 1

    print(f"\n{'='*40}")
    print(f"Generated {count} file(s) from repos.json")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
