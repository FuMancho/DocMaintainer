#!/usr/bin/env python3
"""
generate_boilerplates.py — Generate optimized agent config files for any repo.

Detects the tech stack (language, framework, tests, CI) and produces
ready-to-use config files for Jules, Claude Code, Gemini CLI, Codex CLI.

Usage:
    python scripts/generate_boilerplates.py --repo-path /path/to/repo
    python scripts/generate_boilerplates.py --github FuMancho/Guardian
    python scripts/generate_boilerplates.py --repo-path ./Guardian --dry-run
    python scripts/generate_boilerplates.py --repo-path ./Guardian --output ./Guardian
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


# ================= TECH STACK DETECTION =================

def detect_tech_stack(repo_path: Path) -> dict:
    """Analyze a repo directory and detect its tech stack."""
    stack = {
        "name": repo_path.name,
        "languages": [],
        "frameworks": [],
        "test_tools": [],
        "build_tools": [],
        "install_cmd": "",
        "build_cmd": "",
        "test_cmd": "",
        "lint_cmd": "",
        "has_ci": False,
        "ci_files": [],
        "has_docker": False,
        "has_readme": False,
        "existing_agent_files": [],
        "key_dirs": [],
        "entry_points": [],
        "description": "",
    }

    # Check for existing agent config files
    agent_files = {
        "AGENTS.md": "Jules",
        "JULES.md": "Jules",
        "CLAUDE.md": "Claude Code",
        ".claude/settings.json": "Claude Code",
        ".codex/config.json": "Codex CLI",
        "codex.md": "Codex CLI",
        "CODEX.md": "Codex CLI",
        ".gemini/rules.md": "Gemini CLI",
        ".gemini/settings.json": "Gemini CLI",
    }
    for f, ecosystem in agent_files.items():
        if (repo_path / f).exists():
            stack["existing_agent_files"].append({"file": f, "ecosystem": ecosystem})

    # Python detection
    if (repo_path / "requirements.txt").exists():
        stack["languages"].append("Python")
        stack["install_cmd"] = "pip install -r requirements.txt"
        reqs = (repo_path / "requirements.txt").read_text(encoding="utf-8", errors="ignore").lower()
        _detect_python_frameworks(reqs, stack)

    if (repo_path / "pyproject.toml").exists():
        if "Python" not in stack["languages"]:
            stack["languages"].append("Python")
        toml = (repo_path / "pyproject.toml").read_text(encoding="utf-8", errors="ignore").lower()
        if "poetry" in toml:
            stack["install_cmd"] = "poetry install"
            stack["build_tools"].append("poetry")
        elif "setuptools" in toml or "hatchling" in toml:
            stack["install_cmd"] = "pip install -e ."
        _detect_python_frameworks(toml, stack)

    if (repo_path / "setup.py").exists():
        if "Python" not in stack["languages"]:
            stack["languages"].append("Python")
        if not stack["install_cmd"]:
            stack["install_cmd"] = "pip install -e ."

    if (repo_path / "Pipfile").exists():
        stack["install_cmd"] = "pipenv install"
        stack["build_tools"].append("pipenv")

    # JavaScript / TypeScript
    if (repo_path / "package.json").exists():
        try:
            pkg = json.loads((repo_path / "package.json").read_text(encoding="utf-8"))
            stack["install_cmd"] = "npm install"
            scripts = pkg.get("scripts", {})
            deps_all = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            if "typescript" in deps_all or (repo_path / "tsconfig.json").exists():
                stack["languages"].append("TypeScript")
            else:
                stack["languages"].append("JavaScript")

            if "build" in scripts:
                stack["build_cmd"] = "npm run build"
            if "test" in scripts:
                stack["test_cmd"] = "npm test"
            if "lint" in scripts:
                stack["lint_cmd"] = "npm run lint"

            # Detect frameworks
            for fw, name in [
                ("react", "React"), ("next", "Next.js"), ("vue", "Vue"),
                ("express", "Express"), ("fastify", "Fastify"), ("nest", "NestJS"),
                ("svelte", "Svelte"), ("angular", "Angular"),
            ]:
                if any(fw in d.lower() for d in deps_all):
                    stack["frameworks"].append(name)

            # Test tools
            for tool, name in [
                ("jest", "jest"), ("vitest", "vitest"), ("mocha", "mocha"),
                ("cypress", "cypress"), ("playwright", "playwright"),
            ]:
                if tool in deps_all:
                    stack["test_tools"].append(name)

            stack["description"] = pkg.get("description", "")
        except (json.JSONDecodeError, IOError):
            stack["languages"].append("JavaScript")

    # Go
    if (repo_path / "go.mod").exists():
        stack["languages"].append("Go")
        stack["install_cmd"] = "go mod download"
        stack["build_cmd"] = "go build ./..."
        stack["test_cmd"] = "go test ./..."
        stack["lint_cmd"] = "golangci-lint run"
        stack["test_tools"].append("go test")

    # Rust
    if (repo_path / "Cargo.toml").exists():
        stack["languages"].append("Rust")
        stack["install_cmd"] = "cargo build"
        stack["test_cmd"] = "cargo test"
        stack["lint_cmd"] = "cargo clippy"

    # Python test detection
    if "Python" in stack["languages"]:
        if (repo_path / "pytest.ini").exists() or (repo_path / "conftest.py").exists():
            stack["test_tools"].append("pytest")
            stack["test_cmd"] = "pytest"
        elif any(repo_path.glob("**/test_*.py")) or any(repo_path.glob("**/tests/")):
            stack["test_tools"].append("pytest")
            stack["test_cmd"] = "pytest"
        if not stack["test_cmd"]:
            stack["test_cmd"] = "python -m pytest"

        # Lint
        if (repo_path / ".flake8").exists() or (repo_path / "setup.cfg").exists():
            stack["lint_cmd"] = "flake8"
        elif (repo_path / "ruff.toml").exists() or (repo_path / ".ruff.toml").exists():
            stack["lint_cmd"] = "ruff check ."
        elif (repo_path / "pyproject.toml").exists():
            toml = (repo_path / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
            if "ruff" in toml:
                stack["lint_cmd"] = "ruff check ."
            elif "flake8" in toml:
                stack["lint_cmd"] = "flake8"

    # CI detection
    gh_workflows = repo_path / ".github" / "workflows"
    if gh_workflows.exists():
        stack["has_ci"] = True
        stack["ci_files"] = [f.name for f in gh_workflows.glob("*.yml")]

    # Docker
    stack["has_docker"] = (repo_path / "Dockerfile").exists() or (repo_path / "docker-compose.yml").exists()

    # README
    stack["has_readme"] = (repo_path / "README.md").exists()

    # Key directories
    for d in ["src", "lib", "app", "api", "tests", "test", "scripts", "docs", "config"]:
        if (repo_path / d).is_dir():
            stack["key_dirs"].append(d)

    # Entry points
    for ep in ["main.py", "app.py", "server.py", "index.js", "index.ts", "main.go", "main.rs"]:
        if (repo_path / ep).exists():
            stack["entry_points"].append(ep)
        for d in ["src", "app"]:
            if (repo_path / d / ep).exists():
                stack["entry_points"].append(f"{d}/{ep}")

    return stack


def _detect_python_frameworks(text: str, stack: dict):
    """Detect Python frameworks from requirements/pyproject text."""
    frameworks = [
        ("django", "Django"), ("flask", "Flask"), ("fastapi", "FastAPI"),
        ("starlette", "Starlette"), ("tornado", "Tornado"), ("celery", "Celery"),
        ("sqlalchemy", "SQLAlchemy"), ("pydantic", "Pydantic"),
        ("streamlit", "Streamlit"), ("gradio", "Gradio"),
        ("ccxt", "CCXT"), ("binance", "Binance API"),
        ("discord", "Discord.py"), ("telegram", "Telegram Bot"),
    ]
    for key, name in frameworks:
        if key in text and name not in stack["frameworks"]:
            stack["frameworks"].append(name)


# ================= BOILERPLATE GENERATORS =================

def generate_agents_md(stack: dict) -> str:
    """Generate AGENTS.md (Jules context file)."""
    name = stack["name"]
    langs = ", ".join(stack["languages"]) or "Unknown"
    frameworks = ", ".join(stack["frameworks"]) or "None"

    setup_cmds = []
    if stack["install_cmd"]:
        setup_cmds.append(stack["install_cmd"])
    if stack["build_cmd"]:
        setup_cmds.append(stack["build_cmd"])
    setup_block = "\n".join(setup_cmds) if setup_cmds else "# No automated setup detected"

    test_block = stack["test_cmd"] or "# No test command detected"
    lint_block = stack["lint_cmd"] or "# No lint command detected"

    dirs = "\n".join(f"├── {d}/" for d in stack["key_dirs"])
    entries = "\n".join(f"├── {e}" for e in stack["entry_points"])

    return f"""# AGENTS.md — {name}

## Project Context

**Language:** {langs}
**Frameworks:** {frameworks}

## Setup

```bash
{setup_block}
```

## Testing

```bash
{test_block}
```

## Linting

```bash
{lint_block}
```

## Architecture

```
{name}/
{dirs}
{entries}
├── README.md
└── AGENTS.md
```

## Constraints

- Maintain existing code style and patterns
- Do not modify CI/CD configuration without explicit approval
- All new code must have corresponding tests
- Do not add new dependencies without justification
- Keep backward compatibility unless explicitly instructed otherwise

## Security

- Never commit secrets, API keys, or credentials
- Validate all external inputs
- Use parameterized queries for database access
- Follow the principle of least privilege

## Validation

The agent must confirm:
1. All existing tests pass after changes
2. No new lint warnings introduced
3. Changes are backward compatible
4. New code has test coverage
"""


def generate_claude_md(stack: dict) -> str:
    """Generate CLAUDE.md (Claude Code project context)."""
    name = stack["name"]
    langs = ", ".join(stack["languages"]) or "Unknown"
    frameworks = ", ".join(stack["frameworks"]) or "None"

    install = stack["install_cmd"] or "# see project docs"
    test = stack["test_cmd"] or "# see project docs"
    lint = stack["lint_cmd"] or "# no lint configured"

    return f"""# {name}

## Project Overview

{stack['description'] or f'{name} is a {langs} project.'}

**Stack:** {langs}
**Frameworks:** {frameworks}

## Development Commands

```bash
# Install
{install}

# Test
{test}

# Lint
{lint}
```

## Code Style

- Follow existing patterns in the codebase
- Use type hints (Python) / TypeScript strict mode (JS/TS)
- Keep functions focused and under 50 lines
- Write descriptive variable names
- Add docstrings to public functions and classes

## Architecture Guidelines

- Maintain separation of concerns
- Business logic should not depend on framework-specific code
- Use dependency injection where appropriate
- Keep configuration in environment variables or config files

## Testing

- Write tests for all new functionality
- Maintain existing test coverage
- Use descriptive test names that explain the scenario
- Mock external services in unit tests
"""


def generate_gemini_rules(stack: dict) -> str:
    """Generate .gemini/rules.md (Gemini CLI project rules)."""
    name = stack["name"]
    langs = ", ".join(stack["languages"]) or "Unknown"

    install = stack["install_cmd"] or "# see project docs"
    test = stack["test_cmd"] or "# see project docs"

    return f"""# {name} — Project Rules

## Quick Reference

- **Language:** {langs}
- **Install:** `{install}`
- **Test:** `{test}`
{f'- **Lint:** `{stack["lint_cmd"]}`' if stack["lint_cmd"] else ''}

## Coding Standards

- Follow existing code patterns and conventions
- All new code must include tests
- Use clear, descriptive names for variables and functions
- Keep functions small and focused
- Add comments for non-obvious logic

## File Organization

- Keep related code together
- Use consistent naming conventions
- Separate concerns: data, logic, presentation

## Before Committing

1. Run tests: `{test}`
{f'2. Run lint: `{stack["lint_cmd"]}`' if stack["lint_cmd"] else ''}
3. Review the diff for accidental changes
4. Write a clear commit message
"""


def generate_codex_md(stack: dict) -> str:
    """Generate CODEX.md (Codex CLI project context)."""
    name = stack["name"]
    langs = ", ".join(stack["languages"]) or "Unknown"

    install = stack["install_cmd"] or "# see project docs"
    test = stack["test_cmd"] or "# see project docs"

    return f"""# {name}

{stack['description'] or f'{name} is a {langs} project.'}

## Setup

```bash
{install}
```

## Test

```bash
{test}
```

{f'## Lint' + chr(10) + chr(10) + '```bash' + chr(10) + stack["lint_cmd"] + chr(10) + '```' if stack["lint_cmd"] else ''}

## Guidelines

- Maintain backward compatibility
- Write tests for new functionality
- Follow existing code style
- Keep changes minimal and focused
"""


def generate_jules_md_for_project(stack: dict) -> str:
    """Generate JULES.md for a non-docs project (autonomous task instructions)."""
    name = stack["name"]
    langs = ", ".join(stack["languages"]) or "Unknown"

    test = stack["test_cmd"] or "# see project docs"
    lint = stack["lint_cmd"] or ""

    validation = f"""```bash
# Run tests
{test}
"""
    if lint:
        validation += f"""
# Run lint
{lint}
"""
    validation += "```"

    return f"""# Jules Task Instructions — {name}

## Purpose

This repository is a {langs} project. Jules is responsible for executing
coding tasks autonomously: implementing features, fixing bugs, and
maintaining code quality.

## Before Making Changes

1. Read `AGENTS.md` for project constraints and architecture
2. Understand the existing code structure
3. Check existing tests for patterns to follow

## Validation

Before committing, verify all checks pass:

{validation}

## Quality Gates

```
[ ] All existing tests pass
[ ] New code has test coverage
[ ] No new lint warnings
[ ] Changes match the requested task scope
[ ] No unintended side effects
```

## Commit Format

Use conventional commits:

```
feat: add new feature description
fix: resolve issue with component
refactor: improve code structure
test: add tests for module
docs: update documentation
```

## Files to Ignore

Do not modify:
- `JULES.md` (this file)
- `AGENTS.md` (project context)
- `.github/workflows/` (CI configuration)
- `.gitignore`
"""


def generate_claude_settings(stack: dict) -> str:
    """Generate .claude/settings.json."""
    settings = {
        "permissions": {
            "allow": [
                "Read files",
                "Edit files",
                "Run shell commands",
            ],
            "deny": [
                "Access network",
                "Modify CI/CD config",
                "Delete production files",
            ],
        },
        "context": {
            "include": ["CLAUDE.md", "AGENTS.md"],
            "exclude": [
                "node_modules/**",
                ".git/**",
                "__pycache__/**",
                "*.pyc",
                ".env",
                "*.log",
            ],
        },
    }
    return json.dumps(settings, indent=2)


# ================= ORCHESTRATION =================

def generate_all(stack: dict, output_dir: Path, dry_run: bool = False) -> list[str]:
    """Generate all boilerplate files for a repo."""
    files_generated = []

    generators = [
        ("AGENTS.md", generate_agents_md),
        ("JULES.md", generate_jules_md_for_project),
        ("CLAUDE.md", generate_claude_md),
        (".claude/settings.json", lambda s: generate_claude_settings(s)),
        ("CODEX.md", generate_codex_md),
        (".gemini/rules.md", generate_gemini_rules),
    ]

    for filename, generator in generators:
        file_path = output_dir / filename
        content = generator(stack)

        # Check if file already exists
        exists = file_path.exists()
        action = "OVERWRITE" if exists else "CREATE"

        if dry_run:
            print(f"  [{action}] {filename} ({len(content)} chars)")
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            print(f"  ✅ {filename}")

        files_generated.append(filename)

    return files_generated


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate agent config boilerplates for a repo.")
    ap.add_argument("--repo-path", type=str, help="Path to local repo directory.")
    ap.add_argument("--github", type=str, help="GitHub repo (owner/name) to clone and analyze.")
    ap.add_argument("--output", type=str, help="Output directory (default: repo directory).")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    ap.add_argument("--detect-only", action="store_true", help="Only print detected tech stack.")
    args = ap.parse_args()

    if not args.repo_path and not args.github:
        print("ERROR: Specify --repo-path or --github", file=sys.stderr)
        sys.exit(1)

    # Resolve repo path
    if args.github:
        tmpdir = tempfile.mkdtemp(prefix="boilerplate_")
        repo_url = f"https://github.com/{args.github}.git"
        print(f"📥 Cloning {args.github}...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmpdir],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print(f"ERROR: Clone failed — {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        repo_path = Path(tmpdir)
        print(f"  Cloned to {tmpdir}\n")
    else:
        repo_path = Path(args.repo_path).resolve()
        if not repo_path.is_dir():
            print(f"ERROR: {repo_path} is not a directory", file=sys.stderr)
            sys.exit(1)

    # Detect tech stack
    print(f"🔍 Analyzing {repo_path.name}...")
    stack = detect_tech_stack(repo_path)

    # Print detection results
    print(f"\n📦 {stack['name']}")
    print(f"   Languages:  {', '.join(stack['languages']) or 'Unknown'}")
    print(f"   Frameworks: {', '.join(stack['frameworks']) or 'None detected'}")
    print(f"   Tests:      {', '.join(stack['test_tools']) or 'None detected'}")
    print(f"   CI/CD:      {'Yes (' + ', '.join(stack['ci_files']) + ')' if stack['has_ci'] else 'None'}")
    print(f"   Docker:     {'Yes' if stack['has_docker'] else 'No'}")
    print(f"   Key dirs:   {', '.join(stack['key_dirs']) or 'None'}")

    if stack["existing_agent_files"]:
        print(f"   Existing:   {', '.join(f['file'] + ' (' + f['ecosystem'] + ')' for f in stack['existing_agent_files'])}")
    else:
        print(f"   Existing:   No agent config files found")

    if args.detect_only:
        print(f"\n{json.dumps(stack, indent=2)}")
        return

    # Generate boilerplates
    output_dir = Path(args.output).resolve() if args.output else repo_path
    print(f"\n{'📝 Would generate:' if args.dry_run else '📝 Generating boilerplates:'}")

    files = generate_all(stack, output_dir, dry_run=args.dry_run)

    print(f"\n{'=' * 40}")
    print(f"  {'[DRY RUN] ' if args.dry_run else ''}Generated {len(files)} config file(s)")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    main()
