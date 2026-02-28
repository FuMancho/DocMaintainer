---
name: cross-repo-audit
description: Cross-repo documentation consistency and quality audit
---

# Cross-Repo Audit Skill

Validates documentation consistency across all repositories defined in `repos.json`.

## When to Use

- After adding a new documentation file to any repo
- Before triggering Jules weekly updates
- When onboarding a new repo into the system

## Procedure

### 1. Run Health Check

```bash
python scripts/health_check.py
```

This checks all repos for:
- **Stub files** (< 15 lines)
- **Missing standard docs** (getting-started, features, commands, changelog, official-links)
- **Broken internal links**
- **VERSION.md freshness**
- **Cross-repo doc count balance**

### 2. Check Structure Consistency

All doc repos should have this standard structure:
```
<RepoName>/
├── JULES.md              # Auto-generated from template
├── VERSION.md            # Version tracking
├── docs/
│   ├── getting-started.md
│   ├── features.md
│   ├── commands.md
│   ├── changelog.md
│   ├── official-links.md
│   ├── advanced-settings.md
│   ├── experimental-settings.md
│   └── best-practices.md   # Optional
├── scraped_docs/          # Raw crawl output
└── README.md
```

### 3. Check JULES.md Currency

```bash
python scripts/generate_jules.py --dry-run
```

Compare output against current JULES.md files. If they differ, regenerate:

```bash
python scripts/generate_jules.py
```

### 4. Validate Cross-Repo Links

Ensure `docs/official-links.md` in each repo only references verified domains from `repos.json`.

### 5. Report Findings

For each issue found, either:
- Fix immediately (stubs, broken links)
- Log for next Jules session (content updates needed)
- Update `repos.json` if repo config has changed
