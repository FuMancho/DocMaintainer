---
description: Specialized skill for maintaining the CodexDocs repository.
---

# Codex Documentation Skill

This skill inherits all rules from the `base-docs-maintainer` skill and specializes in the context of the **OpenAI Codex CLI**.

## 1. Context and Scope
*   **Workspace:** This skill ONLY applies when operating within the `CodexDocs/` directory.
*   **Subject Matter:** The OpenAI Codex coding agent (`@openai/codex`) — available as a CLI, desktop app, IDE extension, and cloud platform.

## 2. Specialized Knowledge
When generating or reviewing documentation in `CodexDocs/`:
*   **Terminology:** Use accurate OpenAI Codex terminology (e.g., approval modes, AGENTS.md, config.toml, cloud environments, Codex SDK).
*   **Features:** Differentiate between the App, IDE Extension, CLI, and Cloud interfaces. Emphasize the agentic nature — Codex reads, edits, and runs code autonomously.
*   **Links:** Always verify external links against `developers.openai.com/codex/` official documentation.

## 3. Execution Directives
*   **Focus:** Emphasize practical CLI usage examples, configuration via `config.toml`, and the multi-agent / non-interactive automation workflows.

