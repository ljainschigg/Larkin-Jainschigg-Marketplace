import json
import time
import datetime
from pathlib import Path

import httpx

import creds

TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"
API_BASE = "https://wbsapi.withings.net"
SERVICE = "withings"

MEASURE_TYPES = {
    1: "weight_kg",
    4: "bmi",
    6: "fat_ratio_pct",
    8: "fat_mass_kg",
    11: "heart_rate",
    12: "temperature",
    76: "muscle_mass_kg",
    77: "water_mass_kg",
    88: "bone_mass_kg",
}


def refresh() -> dict:
    client_id, client_secret = creds.get_client(SERVICE)
    refresh_token = creds.load_tokens(SERVICE)["refresh_token"]
    r = httpx.post(
        TOKEN_URL,
        data={
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
    )
    r.raise_for_status()
    result = r.json()
    if result.get("status") != 0:
        raise RuntimeError(f"Withings token refresh failed: {result}")
    body = result["body"]
    tokens = {
        "access_token": body["access_token"],
        "refresh_token": body["refresh_token"],
        "expires_at": time.time() + body.get("expires_in", 10800),
    }
    creds.save_tokens(SERVICE, tokens)
    print("  [withings] tokens refreshed")
    return tokens


def _access_token() -> str:
    tokens = creds.load_tokens(SERVICE)
    if not tokens or time.time() > tokens.get("expires_at", 0) - 300:
        tokens = refresh()
    return tokens["access_token"]


def _post(endpoint: str, params: dict) -> dict:
    token = _access_token()
    r = httpx.post(f"{API_BASE}/{endpoint}", data={**params, "access_token": token})
    r.raise_for_status()
    result = r.json()
    if result.get("status") != 0:
        raise RuntimeError(f"Withings API error on {endpoint}: {result}")
    return result["body"]


def fetch(date: str) -> dict:
    """Return Withings daily metrics for date (YYYY-MM-DD)."""
    d = datetime.date.fromisoformat(date)
    start = int(datetime.datetime.combine(d, datetime.time.min).timestamp())
    end = start + 86400

    measures_body = _post(
        "measure",
        {
            "action": "getmeas",
            "meastypes": ",".join(str(k) for k in MEASURE_TYPES),
            "category": "1",
            "startdate": start,
            "enddate": end,
        },
    )
    latest = {}
    for grp in measures_body.get("measuregrps", []):
        for m in grp.get("measures", []):
            if m["type"] in MEASURE_TYPES:
                latest[MEASURE_TYPES[m["type"]]] = m["value"] * (10 ** m["unit"])

    sleep_body = _post(
        "v2/sleep",
        {"action": "getsummary", "startdateymd": date, "enddateymd": date},
    )
    sleep = (
        (sleep_body.get("series") or [{}])[0].get("data", {})
    )

    activity_body = _post(
        "v2/measure",
        {"action": "getactivity", "startdateymd": date, "enddateymd": date},
    )
    activity = (activity_body.get("activities") or [{}])[0]

    config_path = Path.home() / ".local" / "share" / "diet" / "config.json"
    try:
        height_m = json.loads(config_path.read_text()).get("height_m")
    except (FileNotFoundError, json.JSONDecodeError):
        height_m = None

    weight_kg = latest.get("weight_kg")
    bmi_raw = latest.get("bmi") or (weight_kg / (height_m ** 2) if weight_kg and height_m else None)
    sleep_total = (
        (sleep.get("remsleepduration") or 0)
        + (sleep.get("deepsleepduration") or 0)
        + (sleep.get("lightsleepduration") or 0)
    ) or None

    return {
        "date": date,
        "weight_kg": round(weight_kg, 2) if weight_kg else None,
        "weight_lbs": round(weight_kg * 2.20462, 1) if weight_kg else None,
        "bmi": round(bmi_raw, 1) if bmi_raw else None,
        "fat_ratio_pct": latest.get("fat_ratio_pct"),
        "fat_mass_kg": latest.get("fat_mass_kg"),
        "muscle_mass_kg": latest.get("muscle_mass_kg"),
        "water_mass_kg": latest.get("water_mass_kg"),
        "bone_mass_kg": latest.get("bone_mass_kg"),
        "heart_rate": latest.get("heart_rate"),
        "temperature": latest.get("temperature"),
        "sleep_minutes": sleep_total,
        "rem_sleep_minutes": sleep.get("remsleepduration"),
        "deep_sleep_minutes": sleep.get("deepsleepduration"),
        "light_sleep_minutes": sleep.get("lightsleepduration"),
        "wake_minutes": sleep.get("wakeupduration"),
        "steps": activity.get("steps"),
        "calories_active": activity.get("calories"),
        "distance_km": activity.get("distance"),
    }
