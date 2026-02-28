---
description: Audit documentation across all repos for consistency and accuracy
---

This workflow audits documentation across ClaudeCodeDocs, GeminiDocs, CodexDocs, and AntigravityDocs.

1. **Scope Definition:**
   - Determine which repos to audit (default: all four). Accept `--repo <name>` to narrow scope.
   - Target directories: `docs/` in each repo.

2. **Content Analysis:**
   - Read all `.md` files in the target `docs/` directory.
   - Cross-reference content against the official documentation links in `docs/official-links.md`.
   - Compare `VERSION.md` to detect if upstream has released since last crawl.
   - Check for stub files (< 15 lines or containing "Pending" placeholders).

3. **Formatting Check:**
   - Validate against `.gemini/rules.md` (heading structure, Mermaid diagrams, GitHub alerts).
   - Verify all code blocks specify a language.
   - Check internal links resolve to existing files.

4. **Cross-Repo Consistency:**
   - Ensure all repos follow the standard `docs/` layout.
   - Verify `VERSION.md` exists and is populated.
   - Confirm `changelog.md` has real content (not a placeholder).

5. **Drive Index Sync:**
   - If repo docs changed, flag that the corresponding Drive research index may need updating.
   - Reference folder IDs: Claude (`1KzPhc8_d_vN9ElYZqMcQgZZvXZzOBe1c`), Gemini (`1LVO7TZBc40bbQLQQE5WryXnaGykbOcfu`), Codex (`1L7mNJbd50RbmIcJ045SMXmYLZNDcq8BW`).

6. **Reporting:**
   - Create a summary: accurate items, outdated items, formatting errors, missing content.
   - For simple fixes (formatting), apply automatically.
   - For factual updates, propose changes to the user.

7. **Execution:**
   - Apply approved updates to `.md` files.
   - Commit with `docs: audit fix — <description>`.
