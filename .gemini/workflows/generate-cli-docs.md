---
description: Generate Documentation for a Claude Code Feature
---

This workflow is used to generate documentation for a specific feature, command, or capability of the Claude Code CLI.

1. **Information Gathering:**
   - Prompt the user or review provided source files (code, commit logs, PR descriptions) to understand the feature.
   - Run relevant `claude` CLI commands (if applicable and safe) to observe actual output and behavior.

2. **Drafting:**
   - Generate a Markdown document following the `Project Rules`.
   - Ensure the document includes:
     - A clear, descriptive `<h1>` title.
     - A summary of what the feature does.
     - Prerequisite steps, if any.
     - Usage examples with appropriate code block formatting.
     - Common issues or troubleshooting tips.

3. **Review & Refinement:**
   - Review the draft against `.gemini/rules.md` to guarantee formatting consistency and tone matching.
   - Propose the draft to the user via the `notify_user` tool with the path to the newly created `.md` file in the `docs/` directory.

4. **Finalization:**
   - Incorporate user feedback.
   - Format any changes securely.
