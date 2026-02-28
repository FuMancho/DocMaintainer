#!/usr/bin/env python3
"""Google Drive API helper for DocMaintainer.

Usage:
    python drive_api.py auth        # First-time OAuth authentication
    python drive_api.py list        # List files in My Drive
    python drive_api.py search <q>  # Search for files
    python drive_api.py read <id>   # Read a document as text
    python drive_api.py move <id> <folder_id>  # Move file to folder
    python drive_api.py create-doc <folder_id> <title> <content_file>  # Create doc
"""

import json
import os
import sys
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]
SCRIPT_DIR = Path(__file__).parent
CREDS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"


def get_service(api="drive", version="v3"):
    """Build and return an authenticated Google API service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=8090)
        TOKEN_FILE.write_text(creds.to_json())
    return build(api, version, credentials=creds)


def cmd_auth():
    """Run OAuth flow and save token."""
    svc = get_service()
    about = svc.about().get(fields="user").execute()
    print(f"Authenticated as: {about['user']['displayName']} ({about['user']['emailAddress']})")
    print(f"Token saved to: {TOKEN_FILE}")


def cmd_list():
    """List files in My Drive root."""
    svc = get_service()
    results = svc.files().list(
        q="'root' in parents and trashed=false",
        pageSize=50,
        fields="files(id, name, mimeType, modifiedTime)",
        orderBy="modifiedTime desc",
    ).execute()
    files = results.get("files", [])
    for f in files:
        mime_short = f["mimeType"].split(".")[-1] if "." in f["mimeType"] else f["mimeType"]
        print(f"  {f['id'][:12]}...  {mime_short:<15}  {f.get('modifiedTime','')[:10]}  {f['name']}")
    print(f"\nTotal: {len(files)} items")


def cmd_search(query):
    """Search for files by name."""
    svc = get_service()
    results = svc.files().list(
        q=f"name contains '{query}' and trashed=false",
        pageSize=30,
        fields="files(id, name, mimeType, modifiedTime, parents)",
        orderBy="modifiedTime desc",
    ).execute()
    files = results.get("files", [])
    for f in files:
        parents = ",".join(f.get("parents", []))
        print(f"  {f['id']}  {f['name']}  [{parents}]")
    print(f"\nFound: {len(files)} results")


def cmd_read(file_id):
    """Export a Google Doc as plain text."""
    svc = get_service()
    content = svc.files().export(fileId=file_id, mimeType="text/plain").execute()
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    print(content)


def cmd_move(file_id, folder_id):
    """Move a file to a folder."""
    svc = get_service()
    file_meta = svc.files().get(fileId=file_id, fields="parents").execute()
    prev_parents = ",".join(file_meta.get("parents", []))
    svc.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=prev_parents,
        fields="id, parents",
    ).execute()
    print(f"Moved {file_id} to folder {folder_id}")


def cmd_create_doc(folder_id, title, content_file=None):
    """Create a Google Doc in a folder."""
    svc = get_service()
    doc_svc = get_service("docs", "v1")

    # Create empty doc
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    created = svc.files().create(body=file_metadata, fields="id").execute()
    doc_id = created["id"]
    print(f"Created doc: {doc_id} — {title}")

    # Insert content if file provided
    if content_file and os.path.exists(content_file):
        with open(content_file, "r", encoding="utf-8") as f:
            text = f.read()
        requests = [{"insertText": {"location": {"index": 1}, "text": text}}]
        doc_svc.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
        print(f"Inserted {len(text)} chars from {content_file}")

    return doc_id


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd == "auth":
        cmd_auth()
    elif cmd == "list":
        cmd_list()
    elif cmd == "search" and len(sys.argv) >= 3:
        cmd_search(sys.argv[2])
    elif cmd == "read" and len(sys.argv) >= 3:
        cmd_read(sys.argv[2])
    elif cmd == "move" and len(sys.argv) >= 4:
        cmd_move(sys.argv[2], sys.argv[3])
    elif cmd == "create-doc" and len(sys.argv) >= 4:
        content_file = sys.argv[4] if len(sys.argv) >= 5 else None
        cmd_create_doc(sys.argv[2], sys.argv[3], content_file)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
