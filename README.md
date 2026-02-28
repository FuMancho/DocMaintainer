# DocMaintainer

Automated documentation maintenance system for AI coding tool repositories.

## Managed Repositories

| Repository | Tool | Status |
|---|---|---|
| [ClaudeCodeDocs](https://github.com/FuMancho/ClaudeCodeDocs) | Anthropic Claude Code CLI | ✅ Active |
| [GeminiDocs](https://github.com/FuMancho/GeminiDocs) | Google Gemini CLI | ✅ Active |
| [CodexDocs](https://github.com/FuMancho/CodexDocs) | OpenAI Codex CLI | ✅ Active |
| [AntigravityDocs](https://github.com/FuMancho/AntigravityDocs) | Google Antigravity | ✅ Active |

## Automation Schedule

| Cron | Action | Workflow |
|---|---|---|
| Every 6h | Check upstream releases → trigger Jules | `release-watcher.yml` |
| Friday 14:00 UTC | Deep research via Gemini API | `weekly-research.yml` |
| Monday 06:00 UTC | Pre-flight → Jules all repos → cleanup | `weekly-docs-update.yml` |
| Wednesday 12:00 UTC | Health audit → auto-issue if problems | `health-check.yml` |

## Quick Start

```bash
# Health check all repos
python scripts/health_check.py

# Research all repos (requires GEMINI_API_KEY)
python scripts/deep_research.py --local

# Sync all repos (git add + commit + push)
python scripts/sync_repos.py -m "docs: update"

# Regenerate JULES.md from template
python scripts/generate_jules.py

# Check git status across all repos
python scripts/sync_repos.py --status
```

## Scripts

| Script | Purpose |
|---|---|
| `health_check.py` | Audit all repos for stubs, broken links, missing docs |
| `deep_research.py` | Gemini API research with model fallback chain |
| `sync_repos.py` | Multi-repo git operations |
| `generate_jules.py` | Render JULES.md from template + repos.json |
| `trigger_jules.py` | Create Jules sessions for doc updates |
| `check_releases.py` | Monitor upstream release feeds |
| `cleanup_branches.py` | Delete merged branches |
| `crawler.py` | Web scraper for official documentation |
| `drive_api.py` | Google Drive integration |
| `apps_script_research.js` | Google Apps Script for autonomous research |

## Configuration

All repository metadata is centralized in [`repos.json`](repos.json). Adding a new repo:

1. Add entry to `repos.json`
2. Run `python scripts/generate_jules.py`
3. Run `python scripts/health_check.py` to verify

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | For research | Free from [Google AI Studio](https://aistudio.google.com/apikey) |
| `JULES_API_KEY` | For Jules | From [jules.google.com/settings/api](https://jules.google.com/settings/api) |
| `GH_TOKEN` / `GH_PAT` | For GitHub API | Personal Access Token |

## Architecture

```
DocMaintainer/
├── repos.json              # Central config (single source of truth)
├── templates/JULES.md.j2   # Shared JULES.md template
├── scripts/                # All automation scripts
├── data/                   # Release state + research reports
├── .github/workflows/      # 4 GitHub Actions
├── .gemini/
│   ├── skills/             # 7 skills (per-repo + cross-audit)
│   └── workflows/          # 6 slash-command workflows
├── ClaudeCodeDocs/         # Git submodule
├── GeminiDocs/             # Git submodule
├── CodexDocs/              # Git submodule
└── AntigravityDocs/        # Git submodule
```
