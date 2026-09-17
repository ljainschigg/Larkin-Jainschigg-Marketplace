# /// script
# dependencies = ["httpx"]
# ///
"""
Google Drive accessor for Contour CSV exports.

Handles OAuth2 token management (lazy refresh) and exposes:
  list_contour_files()  -> list of {id, name, modified} dicts, newest first
  fetch_file(file_id)   -> file content as str
  fetch_contour(date)   -> content of ContourCSVReport file for date (YYYY-MM-DD),
                           or most recent if date is None
"""

import time
import urllib.parse

import httpx

import creds

TOKEN_URL = "https://oauth2.googleapis.com/token"
FILES_URL = "https://www.googleapis.com/drive/v3/files"
DOWNLOAD_URL = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
FILE_PREFIX = "ContourCSVReport"   # legacy export name (fallback)
CONTOUR_FOLDER = "CONTOUR"          # folder the Contour app now exports into
SERVICE = "gdrive"


def refresh() -> dict:
    client_id, client_secret = creds.get_client(SERVICE)
    tokens = creds.load_tokens(SERVICE)
    r = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": tokens["refresh_token"],
        },
    )
    if not r.is_success:
        raise RuntimeError(f"GDrive token refresh failed {r.status_code}: {r.text}")
    result = r.json()
    tokens = {
        "access_token": result["access_token"],
        "refresh_token": tokens["refresh_token"],  # Google doesn't rotate refresh tokens
        "expires_at": time.time() + result.get("expires_in", 3600),
    }
    creds.save_tokens(SERVICE, tokens)
    return tokens


def _access_token() -> str:
    tokens = creds.load_tokens(SERVICE)
    if not tokens or time.time() > tokens.get("expires_at", 0) - 300:
        tokens = refresh()
    return tokens["access_token"]


def list_contour_files() -> list[dict]:
    """Return Contour glucose CSV exports, newest first.

    Prefers CSVs in the CONTOUR folder (current app behaviour); falls back to
    the legacy `ContourCSVReport*` name search anywhere on the Drive.
    """
    files = []
    try:
        files = [
            f for f in list_folder(CONTOUR_FOLDER)
            if f.get("mimeType") != FOLDER_MIME and f["name"].lower().endswith(".csv")
        ]
    except Exception:
        files = []

    if not files:
        files = search(f"name contains '{_q(FILE_PREFIX)}' and trashed=false")

    files.sort(key=lambda f: f.get("modifiedTime", ""), reverse=True)
    return files


def fetch_file(file_id: str) -> str:
    """Download a Drive file by ID and return its content as a string."""
    token = _access_token()
    r = httpx.get(
        DOWNLOAD_URL.format(file_id=file_id),
        headers={"Authorization": f"Bearer {token}"},
        follow_redirects=True,
    )
    r.raise_for_status()
    return r.text


def fetch_contour(date: str | None = None) -> tuple[str, str]:
    """
    Find and download the Contour export for a given date (YYYY-MM-DD),
    or the most recent file if date is None.

    Returns (filename, content).
    Raises FileNotFoundError if no matching file exists.
    """
    files = list_contour_files()
    if not files:
        raise FileNotFoundError(
            "No Contour glucose exports found on Google Drive "
            f"(looked in the '{CONTOUR_FOLDER}' folder and for '{FILE_PREFIX}*')"
        )

    target = files[0]  # newest export

    if date is not None:
        # Match either the legacy slug (YYYY_MM_DD) or the current export
        # filename slug (M_D_YYYY), which reflects the export date.
        y, m, d = date.split("-")
        slugs = {date.replace("-", "_"), f"{int(m)}_{int(d)}_{y}"}
        matches = [f for f in files if any(s in f["name"] for s in slugs)]
        if matches:
            target = matches[0]
        else:
            print(f"No export filename matched {date}; using newest ({target['name']}).")

    content = fetch_file(target["id"])
    return target["name"], content


# ---------------------------------------------------------------------------
# Generic Drive accessors (personal account; drive.readonly scope).
# Use these for any file/folder — the Contour helpers above are thin wrappers
# around the same primitives. Exposed as MCP tools in mcp_server.py and via
# the CLI at the bottom of this file.
# ---------------------------------------------------------------------------

FOLDER_MIME = "application/vnd.google-apps.folder"

# Google-native docs can't be downloaded raw; they must be exported.
_EXPORT_AS = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}

_DEFAULT_FIELDS = "files(id,name,mimeType,modifiedTime,size,parents)"


def _q(value: str) -> str:
    """Escape a value for use inside a Drive query string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def search(query: str, order_by: str = "modifiedTime desc",
           page_size: int = 100, fields: str = _DEFAULT_FIELDS) -> list[dict]:
    """Run a raw Drive v3 query and return matching file/folder metadata."""
    token = _access_token()
    r = httpx.get(
        FILES_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "orderBy": order_by,
                "fields": f"nextPageToken,{fields}", "pageSize": page_size},
    )
    r.raise_for_status()
    return r.json().get("files", [])


def find(name: str, *, exact: bool = False, folders_only: bool = False) -> list[dict]:
    """Find files or folders by name (substring match by default)."""
    op = "=" if exact else "contains"
    query = f"name {op} '{_q(name)}' and trashed=false"
    if folders_only:
        query += f" and mimeType = '{FOLDER_MIME}'"
    return search(query)


def resolve_folder_id(folder: str) -> str:
    """Accept a folder name or ID; return its ID. Raises if a name is ambiguous."""
    matches = find(folder, exact=True, folders_only=True)
    if not matches:
        return folder  # assume it's already an ID
    if len(matches) > 1:
        listing = [f"{m['name']} ({m['id']})" for m in matches]
        raise ValueError(f"Multiple folders named '{folder}': {listing}. Pass an ID instead.")
    return matches[0]["id"]


def list_folder(folder: str, page_size: int = 200) -> list[dict]:
    """List the contents of a folder given its name or ID."""
    folder_id = resolve_folder_id(folder)
    return search(f"'{_q(folder_id)}' in parents and trashed=false",
                  order_by="folder,name", page_size=page_size)


def get_metadata(file_id: str) -> dict:
    """Return metadata for a single file or folder by ID."""
    token = _access_token()
    r = httpx.get(
        f"{FILES_URL}/{file_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"fields": "id,name,mimeType,size,modifiedTime,parents"},
    )
    r.raise_for_status()
    return r.json()


def read_file_by_id(file_id: str, mime_type: str | None = None) -> str:
    """Read a file's content as text. Google-native docs are exported (Docs→text, Sheets→CSV)."""
    if mime_type is None:
        mime_type = get_metadata(file_id).get("mimeType", "")
    headers = {"Authorization": f"Bearer {_access_token()}"}
    if mime_type in _EXPORT_AS:
        r = httpx.get(f"{FILES_URL}/{file_id}/export", headers=headers,
                      params={"mimeType": _EXPORT_AS[mime_type]}, follow_redirects=True)
    else:
        r = httpx.get(DOWNLOAD_URL.format(file_id=file_id), headers=headers,
                      follow_redirects=True)
    r.raise_for_status()
    return r.text


def read(ref: str) -> str:
    """Read a file by ID, or by unique name if the ref isn't a valid ID."""
    try:
        meta = get_metadata(ref)
        return read_file_by_id(meta["id"], meta.get("mimeType"))
    except httpx.HTTPStatusError:
        pass
    matches = [m for m in find(ref, exact=True) if m["mimeType"] != FOLDER_MIME]
    if not matches:
        raise FileNotFoundError(f"No file found named '{ref}'")
    if len(matches) > 1:
        raise ValueError(f"Multiple files named '{ref}'; pass an ID: "
                         f"{[(m['name'], m['id']) for m in matches]}")
    return read_file_by_id(matches[0]["id"], matches[0].get("mimeType"))


def _print_files(files: list[dict]):
    if not files:
        print("(no matches)")
        return
    for f in files:
        kind = "dir " if f.get("mimeType") == FOLDER_MIME else "file"
        print(f"  [{kind}] {f['name']}\t{f['id']}\t{f.get('mimeType', '')}\t{f.get('size', '')}")


def _cli():
    import argparse
    p = argparse.ArgumentParser(description="Personal Google Drive accessor (drive.readonly)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="run a raw Drive v3 query")
    sp.add_argument("query")

    fp = sub.add_parser("find", help="find files/folders by name")
    fp.add_argument("name")
    fp.add_argument("--folders", action="store_true", help="folders only")
    fp.add_argument("--exact", action="store_true", help="exact name match")

    lp = sub.add_parser("ls", help="list a folder's contents by name or ID")
    lp.add_argument("folder")

    rp = sub.add_parser("read", help="print a file's content by ID or unique name")
    rp.add_argument("ref")

    args = p.parse_args()
    if args.cmd == "search":
        _print_files(search(args.query))
    elif args.cmd == "find":
        _print_files(find(args.name, exact=args.exact, folders_only=args.folders))
    elif args.cmd == "ls":
        _print_files(list_folder(args.folder))
    elif args.cmd == "read":
        print(read(args.ref))


if __name__ == "__main__":
    _cli()
