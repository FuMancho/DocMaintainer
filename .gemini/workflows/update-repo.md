---
description: Trigger a Jules update session for a single repo or all repos
---

# Update Repo Workflow

Quick-trigger a Jules documentation update session.

## Steps

1. Identify the target repo (user will specify, or use all if not specified)

2. Dry-run to preview what would be sent:

```bash
python scripts/trigger_jules.py --repo <RepoName> --dry-run
```

3. If the dry-run looks good, trigger the actual session:

```bash
python scripts/trigger_jules.py --repo <RepoName>
```

4. For a research-enriched update (uses latest deep research findings):

```bash
python scripts/trigger_jules.py --repo <RepoName> --use-research
```

5. To auto-merge the resulting PR when Jules completes:

```bash
python scripts/trigger_jules.py --repo <RepoName> --auto-merge
```

## Available Repos

- ClaudeCodeDocs
- GeminiDocs
- CodexDocs
- AntigravityDocs
- JulesDocs

## Notes

- Requires `JULES_API_KEY` environment variable
- Use `--list-sources` to verify which repos are connected to Jules
- The `--smart` flag skips repos with no upstream changes
