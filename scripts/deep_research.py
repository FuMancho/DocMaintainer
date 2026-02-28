#!/usr/bin/env python3
"""
deep_research.py — Automated deep research via Gemini API free tier.

Researches upstream changes for each doc repo and writes reports to Google Drive.
Uses the Gemini API (free tier, no extra cost) and existing drive_api.py for Drive.

Usage:
    python scripts/deep_research.py                  # research all repos
    python scripts/deep_research.py --repo GeminiDocs # single repo
    python scripts/deep_research.py --dry-run        # preview prompts only
    python scripts/deep_research.py --local          # save to local files only

Environment:
    GEMINI_API_KEY — from Google AI Studio (free tier)

Setup:
    1. Go to https://aistudio.google.com/apikey
    2. Create a free API key
    3. Set: export GEMINI_API_KEY=<your-key>
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPOS_FILE = ROOT / "repos.json"
REPORTS_DIR = ROOT / "data" / "research_reports"

# Default model — gemini-2.0-flash-lite has the highest free-tier quota (30 RPM)
# Override with --model or GEMINI_MODEL env var
DEFAULT_MODEL = "gemini-2.0-flash-lite"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
MAX_RETRIES = 3
RETRY_DELAY = 60  # seconds between retries on 429
INTER_REQUEST_DELAY = 10  # seconds between repos to avoid burst rate limits


def load_repos() -> dict:
    with open(REPOS_FILE) as f:
        return json.load(f)


def build_research_prompt(repo_name: str, config: dict) -> str:
    """Build a deep research prompt for a specific repo."""
    domains = ", ".join(config["official_domains"])
    return f"""You are a documentation research assistant. Research the latest updates for 
**{config['tool_name']}** and produce a structured report.

Sources to check:
- Official documentation: {config['start_url']}
- Official domains: {domains}
- GitHub releases: {config.get('feed_url', 'N/A')}

Report structure:
1. **Latest Version** — What is the current release? Any breaking changes?
2. **New Features** — List features added since the last major release, with brief descriptions.
3. **Deprecations & Removals** — Features deprecated or removed.
4. **Configuration Changes** — New settings, flags, environment variables, or config file formats.
5. **Experimental Features** — Anything marked experimental, beta, or preview.
6. **Documentation Gaps** — Official pages that exist but are thin, or topics that lack documentation.

Format the report as clean Markdown. Be specific — include CLI flags, config keys, and code examples where relevant.
Repository: {repo_name}
Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"""


def call_gemini_api(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    """Call the Gemini API free tier with retry logic for rate limits."""
    import time as _time
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 4096,
        }
    }).encode("utf-8")

    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return "Error: No response generated"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            if e.code == 429 and attempt < MAX_RETRIES:
                print(f"  ⏳ Rate limited (429), retrying in {RETRY_DELAY}s... (attempt {attempt}/{MAX_RETRIES})")
                _time.sleep(RETRY_DELAY)
                continue
            return f"Error: API returned {e.code} — {body[:300]}"
        except Exception as e:
            return f"Error: {e}"

    return "Error: Max retries exceeded"


def save_report_local(repo_name: str, report: str) -> Path:
    """Save a report to local data/research_reports/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{repo_name}_{date_str}.md"
    filepath = REPORTS_DIR / filename
    filepath.write_text(report, encoding="utf-8")
    return filepath


def save_report_drive(repo_name: str, report: str) -> str | None:
    """Save a report to Google Drive using drive_api.py."""
    try:
        # Write to a temp file first
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tmp_file = REPORTS_DIR / f"_tmp_{repo_name}.md"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        tmp_file.write_text(report, encoding="utf-8")

        # Use drive_api to create the doc
        sys.path.insert(0, str(ROOT / "scripts"))
        from drive_api import cmd_search, get_service

        # Search for the research folder
        svc = get_service()
        results = svc.files().list(
            q=f"name = 'DocMaintainer Research' and mimeType = 'application/vnd.google-apps.folder' and trashed=false",
            pageSize=1,
            fields="files(id, name)",
        ).execute()
        folders = results.get("files", [])

        if not folders:
            # Create the folder
            folder_meta = {
                "name": "DocMaintainer Research",
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = svc.files().create(body=folder_meta, fields="id").execute()
            folder_id = folder["id"]
            print(f"  📁 Created Drive folder: DocMaintainer Research")
        else:
            folder_id = folders[0]["id"]

        # Create the doc
        from drive_api import cmd_create_doc
        title = f"Research: {repo_name} — {date_str}"
        doc_id = cmd_create_doc(folder_id, title, str(tmp_file))

        # Clean up temp file
        tmp_file.unlink(missing_ok=True)
        return doc_id
    except Exception as e:
        print(f"  ⚠️ Drive upload failed: {e}")
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Run deep research for doc repos via Gemini API.")
    ap.add_argument("--repo", type=str, help="Research a single repo.")
    ap.add_argument("--dry-run", action="store_true", help="Preview prompts only.")
    ap.add_argument("--local", action="store_true", help="Save to local files only (no Drive).")
    ap.add_argument("--no-drive", action="store_true", help="Skip Drive upload.")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        print("Get a free key at: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    repos = load_repos()
    targets = {args.repo: repos[args.repo]} if args.repo else repos

    print(f"\n{'='*60}")
    print(f"  🔬 Deep Research — {len(targets)} repo(s)")
    print(f"{'='*60}\n")

    for repo_name, config in targets.items():
        print(f"📦 {repo_name} ({config['tool_name']})")

        prompt = build_research_prompt(repo_name, config)

        if args.dry_run:
            print(f"  [DRY RUN] Prompt ({len(prompt)} chars):")
            print(f"  {prompt[:200]}...")
            print()
            continue

        # Call Gemini API
        print(f"  🔄 Calling Gemini API...")
        report = call_gemini_api(prompt, api_key)

        if report.startswith("Error:"):
            print(f"  ❌ {report}")
            continue

        print(f"  ✅ Got {len(report)} chars")

        # Add header
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        full_report = (
            f"# Research Report: {config['tool_name']}\n\n"
            f"> Generated: {date_str}\n"
            f"> Source: Gemini API (automated)\n"
            f"> Repository: {repo_name}\n\n"
            f"---\n\n{report}"
        )

        # Save locally
        local_path = save_report_local(repo_name, full_report)
        print(f"  💾 Saved: {local_path}")

        # Upload to Drive
        if not args.local and not args.no_drive:
            doc_id = save_report_drive(repo_name, full_report)
            if doc_id:
                print(f"  📄 Drive doc: {doc_id}")

        print()

    print(f"{'='*60}")
    print(f"  ✅ Research complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
