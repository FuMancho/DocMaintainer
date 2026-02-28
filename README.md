# DocMaintainer

Automated documentation maintenance system for AI coding tool repositories.

## Managed Repositories

| Repository | Tool | Status |
|---|---|---|
| [ClaudeCodeDocs](https://github.com/FuMancho/ClaudeCodeDocs) | Anthropic Claude Code CLI | ✅ Active |
| [GeminiDocs](https://github.com/FuMancho/GeminiDocs) | Google Gemini CLI | ✅ Active |
| [CodexDocs](https://github.com/FuMancho/CodexDocs) | OpenAI Codex CLI | ✅ Active |
| [AntigravityDocs](https://github.com/FuMancho/AntigravityDocs) | Google Antigravity | ✅ Active |
| [JulesDocs](https://github.com/FuMancho/JulesDocs) | Google Jules Agent | ✅ Active |

## Automation Schedule

| Cron | Action | Workflow |
|---|---|---|
| Every 6h | Check upstream releases → trigger Jules | `release-watcher.yml` |
| Friday 14:00 UTC | Deep research via Gemini API | `weekly-research.yml` |
| Monday 06:00 UTC | Smart dispatch → Jules updated repos → cleanup | `weekly-docs-update.yml` |
| Wednesday 12:00 UTC | Health audit → auto-issue if problems | `health-check.yml` |

## Quick Start

```bash
# Health check all repos
python scripts/health_check.py

# Research all repos (requires GEMINI_API_KEY)
python scripts/deep_research.py --local

# Sync all repos (git add + commit + push)
python scripts/sync_repos.py -m "docs: update"

# Regenerate JULES.md + AGENTS.md from templates
python scripts/generate_jules.py

# Audit all repos for agent config coverage
python scripts/audit_repos.py --skip-docs

# Generate agent boilerplates for any repo
python scripts/generate_boilerplates.py --github owner/repo

# Smart Jules dispatch (skip unchanged repos)
python scripts/trigger_jules.py --smart --use-research --dry-run
```

## Scripts

| Script | Purpose |
|---|---|
| `health_check.py` | Audit all repos for stubs, broken links, missing docs |
| `deep_research.py` | Gemini API research with model fallback chain |
| `sync_repos.py` | Multi-repo git operations |
| `generate_jules.py` | Render JULES.md + AGENTS.md from templates + repos.json |
| `trigger_jules.py` | Create Jules sessions (`--smart`, `--use-research`, `--from-health-check`) |
| `check_releases.py` | Monitor upstream release feeds |
| `cleanup_branches.py` | Delete merged branches |
| `crawler.py` | Web scraper for official documentation |
| `generate_boilerplates.py` | Auto-detect tech stack → generate agent configs for all ecosystems |
| `audit_repos.py` | Scan GitHub repos → recommendations report |
| `drive_api.py` | Google Drive integration |
| `apps_script_research.js` | Google Apps Script for autonomous research |

## Gemini Workflows

| Workflow | Purpose |
|---|---|
| `/update-repo` | Trigger a Jules session for a specific repo |
| `/fix-health` | Run health check → dispatch Jules to fix issues |
| `/research-update` | Deep research → Jules with context |
| `/generate-boilerplates` | Auto-generate agent configs for any repo |
| `/health-check` | Run documentation health check |
| `/audit-docs` | Cross-repo documentation audit |
| `/generate-docs` | Generate documentation with crawler |
| `/sync-drive` | Sync reports to Google Drive |
| `/browser-auth` | Authenticate Google APIs via browser |

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
├── repos.json                  # Central config (single source of truth)
├── templates/
│   ├── JULES.md.j2             # Shared JULES.md template (with quality gates)
│   └── AGENTS.md.j2            # Shared AGENTS.md template
├── scripts/                    # 12 automation scripts
├── data/                       # Release state + research reports + audit report
├── .github/workflows/          # 4 GitHub Actions
├── .gemini/
│   ├── skills/                 # 8 skills (per-repo + cross-audit)
│   └── workflows/              # 9 slash-command workflows
├── ClaudeCodeDocs/             # Git subdir
├── GeminiDocs/                 # Git subdir
├── CodexDocs/                  # Git subdir
├── AntigravityDocs/            # Git subdir
└── JulesDocs/                  # Git subdir
```
