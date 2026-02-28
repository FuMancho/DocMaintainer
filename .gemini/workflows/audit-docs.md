---
description: Audit Existing Documentation for Consistency
---

This workflow is used to review the existing documentation repository for out-of-date information, inconsistencies, or deviations from the defined Style Guide.

1. **Scope Definition:**
   - Determine which files or directories to audit (e.g., all of `docs/` or a specific guide like `getting-started.md`).

2. **Analysis:**
   - Read the target documentation files.
   - Cross-reference the content against the known capabilities of the latest Anthropic Claude Code CLI.
   - Check formatting against `.gemini/rules.md` (e.g., heading structure, Mermaid.js usage, GitHub-style alerts).
   - Identify broken or missing internal links.

3. **Reporting & Proposals:**
   - Create a summary of findings detailing what is accurate, what is outdated, and formatting errors.
   - For simple, unambiguous fixes (like formatting tweaks), automatically prepare the changes.
   - For factual updates, propose the specific content changes to the user.

4. **Execution:**
   - Apply user-approved updates to the `.md` files.
