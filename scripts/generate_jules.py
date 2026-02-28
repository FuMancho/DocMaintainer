#!/usr/bin/env python3
"""
generate_jules.py — Generate JULES.md files from the central repos.json config.

Reads repos.json + templates/JULES.md.j2 and produces a JULES.md for each repo.

Usage:
    python scripts/generate_jules.py                # generate all
    python scripts/generate_jules.py --repo GeminiDocs  # single repo
    python scripts/generate_jules.py --dry-run      # preview only
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPOS_FILE = ROOT / "repos.json"
TEMPLATE_FILE = ROOT / "templates" / "JULES.md.j2"


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
    import re

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


def generate_jules_md(repo_name: str, config: dict, dry_run: bool = False) -> str:
    """Generate a JULES.md for a single repo."""
    template_text = TEMPLATE_FILE.read_text(encoding="utf-8")

    variables = {
        "repo_name": repo_name,
        "tool_name": config["tool_name"],
        "tool_package": config.get("tool_package", ""),
        "start_url": config["start_url"],
        "base_path": config["base_path"],
        "official_domains": config["official_domains"],
        "github_example": config.get("github_example", ""),
        "extra_keep_domains": config.get("extra_keep_domains", []),
    }

    rendered = render_template(template_text, variables)

    output_path = ROOT / repo_name / "JULES.md"

    if dry_run:
        print(f"\n{'='*60}")
        print(f"[DRY RUN] Would write: {output_path}")
        print(f"{'='*60}")
        print(rendered[:500] + "..." if len(rendered) > 500 else rendered)
    else:
        output_path.write_text(rendered, encoding="utf-8")
        print(f"✅ Generated: {output_path}")

    return rendered


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate JULES.md files from repos.json.")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    ap.add_argument("--repo", type=str, help="Generate for a single repo.")
    args = ap.parse_args()

    repos = load_repos()
    targets = {args.repo: repos[args.repo]} if args.repo else repos

    for repo_name, config in targets.items():
        generate_jules_md(repo_name, config, dry_run=args.dry_run)

    print(f"\n{'='*40}")
    print(f"Generated {len(targets)} JULES.md file(s) from repos.json")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
