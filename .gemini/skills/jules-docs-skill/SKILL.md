---
name: jules-docs-skill
description: Documentation skill for Google Jules autonomous coding agent
---

# Jules Documentation Skill

## Repository

- **Repo:** `FuMancho/JulesDocs`
- **Tool:** Google Jules — autonomous coding agent
- **Official:** [jules.google.com](https://jules.google.com)

## Doc Structure

| File | Content |
|---|---|
| `getting-started.md` | Setup, tiers, first task, key concepts |
| `features.md` | Async execution, swarm mode, critic agent, CLI piping |
| `commands.md` | CLI reference (`jules run`, `fix`, `status`, `cancel`) |
| `agents-md-spec.md` | AGENTS.md specification and best practices |
| `advanced-settings.md` | Model tiers, task/rate limits, VM config |
| `experimental-settings.md` | Critic tuning, Big-O enforcement, swarm strategies |
| `integrations.md` | GitHub Actions, CI/CD, webhooks, IDE integration |
| `changelog.md` | Release history |
| `official-links.md` | Official resources and references |

## Key Topics to Track

1. **Model tier updates** — Gemini model changes, context window sizes
2. **Task limits** — changes to daily/concurrent limits per tier
3. **AGENTS.md specification** — format changes, new directives
4. **CLI flags** — new commands and experimental flags
5. **GitHub Action integration** — `google/jules-invoke` updates
6. **Swarm mode** — new strategies, parallel limits

## Official Sources

- [jules.google.com](https://jules.google.com)
- [Google AI docs](https://ai.google.dev)
- [Google Cloud AI](https://cloud.google.com/ai)

## Formatting Standards

- Use tables for tier comparisons
- Include shell commands in fenced code blocks
- AGENTS.md examples in nested code blocks
- YAML examples for GitHub Action integration
