import base64
import time

import httpx

import creds

TOKEN_URL = "https://api.fitbit.com/oauth2/token"
API_BASE = "https://api.fitbit.com"
SERVICE = "fitbit"


def refresh() -> dict:
    client_id, client_secret = creds.get_client(SERVICE)
    refresh_token = creds.load_tokens(SERVICE)["refresh_token"]
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    r = httpx.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )
    if not r.is_success:
        raise RuntimeError(f"FitBit token refresh failed {r.status_code}: {r.text}")
    result = r.json()
    tokens = {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "expires_at": time.time() + result.get("expires_in", 28800),
    }
    creds.save_tokens(SERVICE, tokens)
    print("  [fitbit] tokens refreshed")
    return tokens


def _access_token() -> str:
    tokens = creds.load_tokens(SERVICE)
    if not tokens or time.time() > tokens.get("expires_at", 0) - 300:
        tokens = refresh()
    return tokens["access_token"]


def fetch(date: str) -> dict:
    """Return FitBit daily metrics for date (YYYY-MM-DD)."""
    token = _access_token()
    headers = {"Authorization": f"Bearer {token}"}

    def get(url):
        r = httpx.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    activity = get(f"{API_BASE}/1/user/-/activities/date/{date}.json")["summary"]
    sleep_raw = get(f"{API_BASE}/1.2/user/-/sleep/date/{date}.json")["summary"]
    weight_raw = get(f"{API_BASE}/1/user/-/body/log/weight/date/{date}.json")
    weight_entry = (weight_raw.get("weight") or [None])[0]

    return {
        "date": date,
        "steps": activity.get("steps"),
        "calories_out": activity.get("caloriesOut"),
        "sedentary_minutes": activity.get("sedentaryMinutes"),
        "lightly_active_minutes": activity.get("lightlyActiveMinutes"),
        "fairly_active_minutes": activity.get("fairlyActiveMinutes"),
        "very_active_minutes": activity.get("veryActiveMinutes"),
        "sleep_minutes": sleep_raw.get("totalMinutesAsleep"),
        "time_in_bed": sleep_raw.get("totalTimeInBed"),
        "weight_lbs": weight_entry.get("weight") if weight_entry else None,
        "body_fat_pct": weight_entry.get("fat") if weight_entry else None,
    }
