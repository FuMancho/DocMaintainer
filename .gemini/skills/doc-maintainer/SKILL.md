---
name: doc-maintainer
description: Automated documentation maintenance pipeline for GitHub repositories
---

# Doc Maintainer Skill

Automate the process of keeping documentation repositories up-to-date by crawling official sources, comparing against existing docs, and generating pull requests with changes.

## Prerequisites

- Python 3.10+
- `gh` CLI authenticated (`gh auth login`)
- Jules API key (set as `JULES_API_KEY` environment variable)
- Target repository on GitHub with `JULES.md` instructions

## Quick Start

To onboard a new documentation repository:

1. **Create the repo structure:**
   ```
   <RepoName>/
   ├── README.md
   ├── JULES.md          ← Copy from templates/JULES.md.template
   ├── VERSION.md         ← Copy from templates/VERSION.md.template
   ├── .gitignore         ← Must include scraped_docs/
   └── docs/
       ├── getting-started.md
       ├── features.md
       ├── commands.md
       ├── best-practices.md
       ├── troubleshooting.md
       ├── changelog.md
       └── official-links.md  ← List all crawl sources here
   ```

2. **Configure JULES.md** with the specific crawl URLs and update instructions for the new repo.

3. **Add the repo to `scripts/trigger_jules.py`** in the `REPOS` dictionary:
   ```python
   "NewRepoDocs": {
       "github": "YourOrg/NewRepoDocs",
       "prompt": "Follow the instructions in JULES.md to update...",
   },
   ```

4. **Add a release feed** (if available) to `scripts/check_releases.py`:
   ```python
   "NewRepoDocs": {
       "name": "New Repo",
       "feed_url": "https://github.com/org/repo/releases.atom",
   },
   ```

5. **Enable auto-delete branches** on the new repo:
   ```bash
   gh api -X PATCH /repos/YourOrg/NewRepoDocs \
     -f delete_branch_on_merge=true
   ```

6. **Add the repo to `scripts/cleanup_branches.py`** in the `REPOS` list.

## Pipeline Architecture

```
Release Watcher (6h)  ──┐
                        ├──▶ trigger_jules.py --auto-merge
Weekly Cron (Mon)  ─────┘         │
                                  ▼
                           Jules API Session
                                  │
                                  ▼
                           PR Created → Auto-Merged
                                  │
                                  ▼
                           Branch Deleted
```

## Scripts Reference

| Script | Purpose | Key Flags |
|---|---|---|
| `trigger_jules.py` | Create Jules sessions for doc updates | `--auto-merge`, `--repos`, `--timeout` |
| `check_releases.py` | Monitor GitHub Atom feeds for new releases | `--dry-run` |
| `cleanup_branches.py` | Delete stale merged branches | `--dry-run` |
| `crawler.py` | Crawl documentation websites | `--url`, `--output` |

## File Templates

### JULES.md Template
See `templates/JULES.md.template` for the standard JULES.md structure including:
- Crawl instructions
- File structure expectations
- Link handling policy
- Files to ignore

### VERSION.md Template
See `templates/VERSION.md.template` for version tracking format.

## Verification

After onboarding a new repo, verify by running:

```bash
# Test release checking
python scripts/check_releases.py --dry-run

# Test branch cleanup
python scripts/cleanup_branches.py --dry-run

# Trigger a manual Jules session
python scripts/trigger_jules.py --repos NewRepoDocs
```

## Maintenance

- **PAT expiration**: The `GH_PAT` secret expires periodically — renew it
- **Feed URL changes**: Upstream repos may change their GitHub org — update feed URLs
- **New doc sources**: Add new official links to `docs/official-links.md` as discovered
