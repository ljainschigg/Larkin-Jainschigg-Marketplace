# /// script
# dependencies = ["httpx"]
# ///
"""Interactive Google Drive OAuth setup — reads client creds from and writes tokens
to the secret-resolver (keys personal/gdrive/*). Store the client first (from the
OAuth client JSON you download in Google Cloud Console → Credentials → Desktop app):
    secret-resolver set personal/gdrive/client_id
    secret-resolver set personal/gdrive/client_secret
"""
import sys
import time
import urllib.parse
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import creds  # noqa: E402

TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost"
SCOPE = "https://www.googleapis.com/auth/drive.readonly"

CLIENT_ID, CLIENT_SECRET = creds.get_client("gdrive")
if not CLIENT_ID or not CLIENT_SECRET:
    print("Google client credentials not found in secret-resolver. Store them first")
    print("(from Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client")
    print(" ID → Desktop app → Download JSON, then copy client_id/client_secret):")
    print("  secret-resolver set personal/gdrive/client_id")
    print("  secret-resolver set personal/gdrive/client_secret")
    raise SystemExit(1)

auth_url = (
    "https://accounts.google.com/o/oauth2/v2/auth"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    f"&scope={urllib.parse.quote(SCOPE, safe='')}"
    f"&access_type=offline"
    f"&prompt=consent"
)

if len(sys.argv) > 1:
    redirect = sys.argv[1].strip()
else:
    print("\n1. Open this URL in your browser:\n")
    print(f"   {auth_url}\n")
    print("2. Log in and approve access.")
    print("3. You'll be redirected to http://localhost — the page won't load, that's fine.")
    print("4. Copy the full URL from the browser address bar, then re-run this script")
    print("   with it in quotes as an argument, e.g.:")
    print('     uv run server/setup_gdrive_auth.py "http://localhost/?code=...&scope=..."\n')
    try:
        redirect = input("...or paste the redirect URL (or just the code) here: ").strip()
    except EOFError:
        print("\nNo input available. Re-run with the redirect URL as an argument (see above).")
        raise SystemExit(1)

if redirect.startswith("http"):
    parsed = urllib.parse.urlparse(redirect)
    params = urllib.parse.parse_qs(parsed.query)
    if "code" not in params:
        print(f"\nERROR: no 'code' found in URL. Got params: {params}")
        raise SystemExit(1)
    code = params["code"][0]
else:
    code = redirect

print(f"\nGot code: {code[:12]}...")

r = httpx.post(
    TOKEN_URL,
    data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    },
)

if not r.is_success:
    print(f"\nERROR {r.status_code}: {r.text}")
    raise SystemExit(1)

result = r.json()
if "access_token" not in result:
    print(f"\nERROR: unexpected response: {result}")
    raise SystemExit(1)

creds.save_tokens("gdrive", {
    "access_token": result["access_token"],
    "refresh_token": result["refresh_token"],
    "expires_at": time.time() + result.get("expires_in", 3600),
})

print("\nGDrive tokens saved to secret-resolver. Run contour_gdrive.py to test.")
