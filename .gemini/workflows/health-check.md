---
description: Run a documentation health check across all repos
---

# Health Check Workflow

Run `health_check.py` to audit all repos for consistency and quality issues.

// turbo
1. Run the health check script:
```bash
python scripts/health_check.py
```

2. Review the output for any issues (🔴) or warnings (⚠️).

3. For any stub files detected (< 15 lines), populate them with substantive content from official documentation.

4. For any broken internal links, fix the link targets in the affected files.

5. For doc count imbalances, identify which repo is missing docs and create them.

6. If JULES.md files are out of date with `repos.json`, regenerate them:
// turbo
```bash
python scripts/generate_jules.py
```

7. Commit and push all fixes:
// turbo
```bash
python scripts/sync_repos.py -m "docs: fix health check issues" --include-parent
```
