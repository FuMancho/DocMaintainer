# Agent Config Audit Report — FuMancho

*Generated: 2026-02-28 22:25*

## Summary

| Repo | Language | Jules | Claude | Gemini | Codex | Score |
|---|---|---|---|---|---|---|
| **Guardian** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **NewBinaBot** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **Test** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **la_castagne** | — | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **DevWorkflowKit** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **redm-ai-director** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **BinaTrader** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |
| **binance-connector-python** | Python | ❌ | ❌ | ❌ | ❌ | ⚪⚪⚪⚪ |

## Detailed Recommendations

### 🔧 Guardian (6 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/Guardian
```

### 🔧 NewBinaBot (6 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/NewBinaBot
```

### 🔧 Test (6 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/Test
```

### 🔧 la_castagne (5 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/la_castagne
```

### 🔧 DevWorkflowKit (6 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/DevWorkflowKit
```

### 🔧 redm-ai-director (6 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/redm-ai-director
```

### 🔧 BinaTrader (6 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.
- **Private repo:** Agent configs are especially valuable here — they provide context that can't be inferred from public docs.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/BinaTrader
```

### 🔧 binance-connector-python (5 recommendations)

- **Add Jules support** — Drop in `AGENTS.md` + `JULES.md` to enable autonomous coding sessions. Jules can handle bug fixes, refactoring, and dependency updates end-to-end without supervision.
- **Add Claude Code config** — Create `CLAUDE.md` for persistent project context across interactive coding sessions. Add `.claude/settings.json` for permission controls.
- **Add Gemini CLI rules** — Create `.gemini/rules.md` with project standards and `.gemini/workflows/` for reusable task automation.
- **Add Codex CLI support** — Create `CODEX.md` for headless autonomous coding with OpenAI models.
- **Python-specific:** AGENTS.md should include `pytest` commands, type checking with `mypy` or `pyright`, and `ruff`/`flake8` linting.

**Quick fix:**
```bash
python scripts/generate_boilerplates.py --github FuMancho/binance-connector-python
```

## Ecosystem Feature Reference

### Jules

- Autonomous PRs — describe a task, get a PR back
- Swarm mode — parallel agents for large refactors
- Critic Agent — adversarial self-review before committing
- AGENTS.md — machine-readable constraints and guardrails
- CI/CD integration via Jules Invoke GitHub Action

### Claude Code

- Interactive coding sessions with full repo context
- Tool execution (shell, file editing, browser)
- CLAUDE.md — persistent project memory across sessions
- Custom permissions via .claude/settings.json
- Headless mode for CI automation

### Gemini CLI

- Interactive sessions with Gemini models
- Custom rules.md for project-specific guidance
- Reusable workflows for common tasks
- Multi-modal support (images, code, docs)
- Google ecosystem integration (Drive, Docs, Sheets)

### Codex CLI

- Headless autonomous coding from terminal
- Structured output for CI integration
- Full sandbox execution with network access
- Multi-model support (o3-mini, o4-mini)
- CODEX.md for project-specific instructions
