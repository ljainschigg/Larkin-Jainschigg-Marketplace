# /// script
# dependencies = ["httpx"]
# ///
"""Interactive FitBit OAuth setup — reads client creds from and writes tokens to
the secret-resolver (keys personal/fitbit/*). Store the client first:
    secret-resolver set personal/fitbit/client_id      (from dev.fitbit.com)
    secret-resolver set personal/fitbit/client_secret
"""
import base64
import sys
import time
import urllib.parse
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import creds  # noqa: E402

REDIRECT_URI = "http://localhost"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"

CLIENT_ID, CLIENT_SECRET = creds.get_client("fitbit")
if not CLIENT_ID or not CLIENT_SECRET:
    print("FitBit client credentials not found in secret-resolver. Store them first:")
    print("  secret-resolver set personal/fitbit/client_id      (from dev.fitbit.com)")
    print("  secret-resolver set personal/fitbit/client_secret")
    raise SystemExit(1)

auth_url = (
    "https://www.fitbit.com/oauth2/authorize"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    f"&scope=activity%20heartrate%20nutrition%20profile%20settings%20sleep%20weight"
    f"&state=diet_setup"
)

print("\n1. Open this URL in your browser:\n")
print(f"   {auth_url}\n")
print("2. Log in and approve access.")
print("3. You'll be redirected to http://localhost — the page won't load, that's fine.")
print("4. Copy the full URL from the browser address bar and paste it here.\n")

redirect = input("Paste the redirect URL (or just the code): ").strip()

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

auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
r = httpx.post(
    TOKEN_URL,
    headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    },
)

if not r.is_success:
    print(f"\nERROR {r.status_code}: {r.text}")
    raise SystemExit(1)

result = r.json()
creds.save_tokens("fitbit", {
    "access_token": result["access_token"],
    "refresh_token": result["refresh_token"],
    "expires_at": time.time() + result.get("expires_in", 28800),
})

print("\nFitBit tokens saved to secret-resolver. Run fetch.py to test.")
