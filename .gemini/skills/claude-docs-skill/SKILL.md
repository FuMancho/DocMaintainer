---
description: Specialized skill for maintaining the ClaudeCodeDocs repository.
---

# Claude Code Documentation Skill

This skill inherits all rules from the `base-docs-maintainer` skill and specializes in the context of the **Anthropic Claude Code CLI**.

## 1. Context and Scope
*   **Workspace:** This skill ONLY applies when operating within the `ClaudeCodeDocs/` directory.
*   **Subject Matter:** The Anthropic Claude Code CLI (`@anthropic-ai/claude-code`).

## 2. Specialized Knowledge
When generating or reviewing documentation in `ClaudeCodeDocs/`:
*   **Authentication:** Always remind users that Claude Pro or Claude Max is required.
*   **Features:** Emphasize its agentic capabilities—it doesn't just suggest code, it *executes* tools, reads files, and can spawn sub-agents.
*   **Integration:** Be familiar with `CLAUDE.md`, Model Context Protocol (MCP), and custom slash commands (Skills).
*   **Links:** Whenever linking to an official source, ensure it points to `docs.anthropic.com` or `platform.claude.com`. Refer to `docs/official-links.md` (if available in the repo) for verified URLs.

## 3. Execution Directives
*   **Before Generation:** If asked to document a Claude command, attempt to run `claude -h` or `claude <command> -h` (if safely available) to understand the exact CLI flags before writing.
