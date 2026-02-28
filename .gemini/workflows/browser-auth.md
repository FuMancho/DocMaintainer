---
description: How to use Chrome as the authenticated user for browser-based tasks
---

# Browser Authentication Workflow

## Chrome Profile

The browser uses a **persistent Chrome profile** stored at:

```
C:\Users\Stoufims\.gemini\antigravity-browser-profile
```

This profile retains all cookies, sessions, and login state between conversations.

## Authenticated Services

The following services are logged in within this profile:

| Service | Account | Verified |
|---------|---------|----------|
| GitHub | FuMancho | 2026-02-28 |
| Jules (jules.google.com) | Google account | 2026-02-28 |
| Google (general) | Stoufims | 2026-02-28 |

## Using Browser in Future Sessions

// turbo-all

1. To verify browser access, open any authenticated page:
   ```
   Use the browser_subagent tool to navigate to https://github.com/settings/profile
   ```

2. The session should already be authenticated — no login needed.

3. If a session has expired (e.g., GitHub 2FA timeout), the user can sign in manually and the session will persist for future use.

## Important Notes

- **Do NOT clear this profile directory** — it contains all login sessions.
- The GitHub fine-grained PAT `DocMaintainer-AutoMerge` expires **May 29, 2026** and will need renewal.
- The Jules API key is stored as a GitHub secret `JULES_API_KEY` in `FuMancho/DocMaintainer`.
- The GitHub PAT is stored as `GH_PAT` in `FuMancho/DocMaintainer`.
