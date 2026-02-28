---
description: Run health check and dispatch Jules to fix any issues found
---

# Fix Health Workflow

Automatically detect and fix documentation health issues via Jules.

## Steps

1. Run the health check to see current status:

```bash
python scripts/health_check.py
```

2. If issues are found, preview what Jules fix tasks would look like:

```bash
python scripts/trigger_jules.py --from-health-check --dry-run
```

3. Dispatch Jules to fix the issues:

```bash
python scripts/trigger_jules.py --from-health-check
```

4. To also auto-merge the resulting PRs:

```bash
python scripts/trigger_jules.py --from-health-check --auto-merge
```

## What Gets Fixed

Jules will receive targeted prompts to address specific issues:
- **Stub files** (< 15 lines) → expanded with official documentation
- **Broken links** → replaced with verified URLs from official-links.md
- **Missing files** → created following existing doc structure
- **Placeholder markers** → replaced with real content

## Notes

- Requires `JULES_API_KEY` environment variable
- Only dispatches sessions for repos with actual issues
- If no issues found, no tasks are created
