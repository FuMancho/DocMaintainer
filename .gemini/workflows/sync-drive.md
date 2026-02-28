---
description: Sync Google Drive research folders with local repo documentation
---

This workflow syncs the Google Drive research index documents with the current state of the local documentation repos.

1. **Authenticate:**
   // turbo
   - Run `python scripts/drive_api.py auth` to ensure the OAuth token is valid.

2. **Inventory Drive:**
   // turbo
   - List files in each Drive research folder:
     - Claude: `python scripts/drive_api.py search "parents in '1KzPhc8_d_vN9ElYZqMcQgZZvXZzOBe1c'"`
     - Gemini: `python scripts/drive_api.py search "parents in '1LVO7TZBc40bbQLQQE5WryXnaGykbOcfu'"`
     - Codex: `python scripts/drive_api.py search "parents in '1L7mNJbd50RbmIcJ045SMXmYLZNDcq8BW'"`

3. **Compare:**
   - Compare Drive file inventory with local `docs/` content.
   - Identify new research documents that should be indexed.
   - Identify stale Drive docs that no longer match local content.

4. **Update Indexes:**
   - Use `python scripts/drive_api.py create-doc <folder_id> <title> <content_file>` to create/update index docs.
   - Deduplicate using the pattern from `scripts/_dedup_drive.py`.

5. **Report:**
   - Summarize what was synced, added, or flagged.
   - Commit any local changes with `docs: sync Drive research indexes`.
