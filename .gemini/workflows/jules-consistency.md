---
description: Use Jules to enforce consistency across all managed repos
---

# Jules Cross-Repo Consistency Check

Use Jules to audit and fix inconsistencies across all 5 docs repos.

## What Gets Checked

- All repos have the same standard files (README.md, VERSION.md, JULES.md, AGENTS.md)
- Formatting is consistent (heading styles, code block languages, table formats)
- All repos have a populated changelog
- Official-links.md is comprehensive and accurate
- No broken cross-references between docs

## Steps

1. Run the health check to identify issues:

```bash
python scripts/health_check.py
```

2. If issues found, dispatch Jules to fix each repo:

```bash
python scripts/trigger_jules.py --from-health-check --dry-run
```

3. Review the dry run output, then dispatch:

```bash
python scripts/trigger_jules.py --from-health-check --auto-merge
```

## Manual Cross-Repo Consistency Tasks

For deeper consistency work, dispatch Jules with a specific prompt:

```bash
# Example: ensure all repos have consistent heading styles
python scripts/trigger_jules.py --repo ClaudeCodeDocs
```

With a custom prompt in the JULES.md or via the web UI:

> "Audit all docs/*.md files for formatting consistency: ensure all use ## for sections,
> ### for subsections, all code blocks have language tags, all tables have header separators,
> and all lists use - (not *). Fix any inconsistencies."

## Automation

This runs automatically via the Wednesday health check workflow.
If issues are found, they're reported as GitHub issues.
