---
description: Generate optimized agent config boilerplates for a repo
---

# Generate Boilerplates Workflow

Auto-detect tech stack and generate agent config files for any repo.

## Steps

1. To generate boilerplates for a local repo:

```bash
python scripts/generate_boilerplates.py --repo-path /path/to/repo --dry-run
```

2. If the dry-run looks good, generate the files:

```bash
python scripts/generate_boilerplates.py --repo-path /path/to/repo
```

3. To generate for a GitHub repo (auto-clones):

```bash
python scripts/generate_boilerplates.py --github FuMancho/Guardian --dry-run
```

4. To just detect the tech stack without generating:

```bash
python scripts/generate_boilerplates.py --repo-path /path/to/repo --detect-only
```

5. To audit all repos and see what's missing:

```bash
python scripts/audit_repos.py --skip-docs
```

6. Save the audit report:

```bash
python scripts/audit_repos.py --skip-docs --output data/audit_report.md
```

## Generated Files

| File | Ecosystem | Purpose |
|---|---|---|
| `AGENTS.md` | Jules | Machine-readable project context |
| `JULES.md` | Jules | Autonomous task instructions |
| `CLAUDE.md` | Claude Code | Project context and standards |
| `.claude/settings.json` | Claude Code | Permissions and tool config |
| `CODEX.md` | Codex CLI | Project context for Codex |
| `.gemini/rules.md` | Gemini CLI | Project rules and standards |

## Notes

- Detection is based on file analysis (requirements.txt, package.json, etc.)
- Generated files are starting points — customize after generation
- Use `--dry-run` to preview before writing
