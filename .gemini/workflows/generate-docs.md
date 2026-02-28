---
description: Generate documentation for a feature in any repo (Claude, Gemini, Codex, or Antigravity)
---

This workflow generates documentation for a specific feature, command, or capability in any of the four documentation repos.

1. **Target Selection:**
   - Identify the target repo: ClaudeCodeDocs, GeminiDocs, CodexDocs, or AntigravityDocs.
   - Identify the target doc file (new or existing) in `docs/`.

2. **Information Gathering:**
   - Review official documentation links from the repo's `docs/official-links.md`.
   - Crawl the relevant official page using `read_url_content` or `scripts/crawler.py`.
   - If applicable, run the tool's CLI commands to observe actual behavior.

3. **Drafting:**
   - Generate a Markdown document following `.gemini/rules.md`.
   - Ensure the document includes:
     - A clear `#` title.
     - Summary of what the feature does.
     - Prerequisites and installation steps (if applicable).
     - Usage examples with properly formatted code blocks.
     - Common issues or troubleshooting tips.
     - "See Also" section with cross-links to related docs.

4. **Review & Refinement:**
   - Validate formatting against rules.md.
   - Verify all links resolve correctly.
   - Propose the draft to the user via `notify_user` with the file path.

5. **Finalization:**
   - Incorporate user feedback.
   - Update `docs/changelog.md` if the feature is new.
   - Commit with `docs: add <feature> documentation`.
