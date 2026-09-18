---
name: diet
description: Track food intake and biometric readings against the instance's own health targets — invoke with log, biometrics, summary, fetch, or pull
---

Read the first word of the user's message to determine the operation: `log`, `biometrics`, `summary`, `fetch`, or `pull`. Follow the instructions for that operation below.

This is a **person-neutral engine.** All personalization lives in the instance directory (the current working directory), never in this skill:

- **`targets.json`** — the daily targets this person steers by (metric → target, direction, label, unit). Drives every gap analysis and output. The engine never hardcodes target numbers.
- **`food-reference.md`** — this person's nutritional reference values, named recipes, standing daily habits, HIGH UNCERTAINTY list, and vague-amount seed defaults.
- **`portion-vocabulary.csv`** — the living, self-correcting map of this person's loose amounts → grams/macros.

Always read those three files at the start of a `log`/`summary`; treat them as the source of truth over anything in this skill.

If no operation is given or the operation is unrecognised, print:

```
Usage:
  /diet setup       — first-time setup: targets, config files, device credentials
  /diet log         — log food intake and print a gap analysis
  /diet biometrics  — log a biometric reading (weight, BP, glucose, lipids)
  /diet summary     — print today's compliance summary
  /diet fetch       — pull device data for a date and log to biometrics.csv
  /diet pull        — pull all device data for today
```

---

## Operating model

Before acting on any operation, follow `approach.md` — the shared behavioral spec: conversation first ("ask anything, get a sensible answer"), tracking is ambient (devices measure, the user doesn't), logging is loose and self-correcting, and the goal is the discipline of looking, not perfect data. Never demand grams, ounces, or brand names.

---

## Operation: setup

Walk the user through first-time configuration. Work through each step in order, skipping any already complete.

**Step 0 — Runtime prerequisites**

Check that `uv` is available — the MCP server and all device-connector scripts run via `uv run`:

```bash
uv --version
```

If not found, stop and tell the user to install `uv` (https://docs.astral.sh/uv/) before continuing — nothing else in this skill works without it.

This step only confirms `uv` itself. Whether device connectors are configured is optional and covered in Step 4.

**Step 1 — Targets**

Check for `targets.json` in the current directory. If absent, copy the engine template `templates/targets.json` and help the user set their targets (calories, protein, and whatever else matters for their goal). Each entry is `{"target": N, "dir": "min"|"under", "label": "...", "short": "...", "unit": "..."}`. This is what every gap analysis is measured against — there are no hardcoded targets anywhere else.

**Step 2 — Personalization & data files**

Ensure these exist in the current directory; create any that are missing:

```
targets.json             (from templates/targets.json — see Step 1)
food-reference.md        (from templates/food-reference.md — the person's foods, recipes, habits)
compliance.csv           date,meal_context,food_item,amount_g,kcal,protein_g,sat_fat_g,soy_protein_g,omega3_g,soluble_fiber_g,sodium_mg,notes
biometrics.csv           date,time,metric,value,unit,notes
portion-vocabulary.csv   term,food_class,example,grams_est,kcal,protein_g,sat_fat_g,soy_protein_g,omega3_g,soluble_fiber_g,sodium_mg,confidence,last_updated,notes
```

`food-reference.md` is where you record the person's actual foods; `portion-vocabulary.csv` is the living map of their loose amounts, seeded from the defaults in `food-reference.md` and refined over time (see `approach.md`).

**Step 3 — Height (for BMI, optional)**

Check `~/.local/share/diet/config.json` for `height_m`. If absent and the person wants BMI, ask their height in feet/inches, convert to metres (1 inch = 0.0254 m), and write `{"height_m": X.XXX}`.

**Step 4 — Device connectors (optional)**

Device sync is optional; manual logging works with none of it. When enabled, connectors read credentials **server-side** at use time in this order (see the credential contract in `CONVENTIONS.md` §3): the env var `<SERVICE>_<FIELD>` (e.g. `FITBIT_CLIENT_ID`) if set, else the `secret-resolver` store. Secrets never live in this instance, the plugin, or the model's context. The keys diet needs are declared in this plugin's `plugin.json` `requires_credentials`.

Only set this up if the user wants device sync. If they do, negotiate the credential solution:

1. **Detect the preferred store.** Check whether `secret-resolver` is installed and set up as the user's credential store:
   ```bash
   find "$(dirname "$(dirname "${CLAUDE_PLUGIN_ROOT}")")" -path "*/secret-resolver/*/skills/secret-resolver/SKILL.md" | sort -V | tail -1
   ```
   If found, run `secret-resolver status` to report the active backend (keyring / pass / file).

2. **Ask which solution to use** for diet's credentials:
   - **`secret-resolver`** (recommended — provider-agnostic keyring/pass/file), or
   - **their own solution** — any tool that can export the `<SERVICE>_<FIELD>` env vars (e.g. `FITBIT_CLIENT_ID`, `WITHINGS_CLIENT_SECRET`) into the environment diet's server runs in.

   If they want `secret-resolver` but it isn't installed: "Install it (`/plugin install secret-resolver@Larkin-Jainschigg-Marketplace`), run `secret-resolver setup`, then come back." Manual logging keeps working meanwhile.

3. **Get the required credentials into the chosen solution** (the `requires_credentials` keys, per service they want):
   - **secret-resolver:** run `secret-resolver install` once (drops the discovery pointer), then the user stores each OAuth client id/secret **themselves, value via stdin** so it never reaches the model or argv:
     ```bash
     printf '%s' "$CLIENT_ID" | secret-resolver set personal/fitbit/client_id --stdin
     ```
     Then run the connector's OAuth flow: `uv run server/setup_fitbit_auth.py` (likewise `setup_withings_auth.py`, `setup_gdrive_auth.py`) — it exchanges and stores the tokens back into the resolver.
   - **their own solution:** have them export `FITBIT_CLIENT_ID` / `FITBIT_CLIENT_SECRET` (etc.) from their tool, then run the same `setup_*_auth.py` OAuth flow.

4. **Confirm the read path** before relying on sync — e.g. `uv run server/fetch.py <today>` for an enabled connector (or `secret-resolver get personal/fitbit/client_id`). If it can't read the credential, the chosen solution isn't wired correctly — fix before finishing.

Migrating an older instance that kept `server/secrets.json`? Run `uv run server/migrate_secrets_to_resolver.py` once, verify, then delete the old JSON files.

**Step 5 — Summary**

Print what is and isn't configured:

```
Setup status
────────────────────────────
uv runtime:          ✓ / ✗ (required — install from https://docs.astral.sh/uv/)
targets.json:        ✓ / ✗ (created from template)
food-reference.md:   ✓ / ✗ (created from template)
compliance.csv:      ✓ / ✗ (created)
biometrics.csv:      ✓ / ✗ (created)
portion-vocabulary:  ✓ / ✗ (created)
Height (BMI):        ✓ X.XXX m / — not set
Device connectors:   [list connected / — none (optional)]
────────────────────────────
[Next step or "Setup complete — run /diet log to start tracking"]
```

---

## Operation: log

The user logs food incrementally throughout the day. Each invocation adds new items to today's date. Expect 2–5 separate log calls per day.

**Steps:**
1. Get today's date (`date +%F`).
2. Read `targets.json`, `food-reference.md`, and `portion-vocabulary.csv`.
3. Read `compliance.csv`; identify rows already logged for today — do not re-log them.
4. Auto-log any **standing daily habits** from `food-reference.md` not already present for today.
5. Parse each food item and amount. For vague amounts ("a handful", "a small bowl", "a serving"), resolve grams via `portion-vocabulary.csv` first; fall back to the vague-amount seed defaults in `food-reference.md`, then append a new `portion-vocabulary.csv` row (confidence `seed`) so it starts accumulating. Note the estimate in `notes`. **Never demand precise weights.**
6. Look up nutrition from `food-reference.md` (values + named recipes); use general knowledge for unlisted items.
7. Flag HIGH UNCERTAINTY items (per `food-reference.md`) in `notes` as `HIGH UNCERTAINTY sodium ~Xmg`. If any is present and a capped metric (e.g. sodium) is already near its target, warn explicitly.
8. Append one row per new food item.
9. Recompute the day's totals across all non-`daily_total` rows; append or replace the `daily_total` row.
10. Print the gap analysis (format below).

*Mechanical helper: `server/diet.py` (`log`/`close`/`show`/`summary`/`bio`) performs these CSV operations deterministically — it recomputes `daily_total` from `targets.json` and snapshots a `.bak` before each write. Prefer it over hand-editing when available.*

**CSV schema — `compliance.csv`**

Header: `date,meal_context,food_item,amount_g,kcal,protein_g,sat_fat_g,soy_protein_g,omega3_g,soluble_fiber_g,sodium_mg,notes`

- `date` — YYYY-MM-DD
- `meal_context` — see vocabulary below
- `food_item` — snake_case (e.g., `baked_salmon`)
- `amount_g` — grams; for liquids, 1ml water-density ≈ 1g; note volume in `notes`
- nutrient columns — the fixed superset the engine tracks; a metric matters to a given person only if it appears in their `targets.json`. Fill what's known, `0` otherwise.
  - `sat_fat_g` — saturated fat only; `soy_protein_g` — soy-derived protein only (= `protein_g` for tofu/edamame); `omega3_g` — EPA+DHA (marine) or ALA (plant), note source; `soluble_fiber_g` — soluble only; `sodium_mg` — 0 for unsalted
- `notes` — prep, sourcing, caveats; `HIGH UNCERTAINTY sodium ~Xmg` for pickled/cured/restaurant items

**meal_context vocabulary:** `incidental` (coffee/tea, standing habits) · `main` (primary courses) · `finisher` (grain/dessert-style close) · `snack` · `supplement` (capsules, powders, doses) · `daily_total` (one summary row/day; `food_item`=`TOTAL`, blank `amount_g`).

**daily_total row:** `YYYY-MM-DD,daily_total,TOTAL,,<kcal>,<protein_g>,<sat_fat_g>,<soy_protein_g>,<omega3_g>,<soluble_fiber_g>,<sodium_mg>,"<gap summary>"`

Build the gap summary from `targets.json`: for each metric, `"<short> <value>/<target><unit> ✓|✗"` per its `dir` (`min` → met when ≥ target; `under` → met when ≤ target). Mark the day **PARTIAL** if the user hasn't reported all meals/supplements yet; **CLEAN SWEEP** when every target is met; **DAY CLOSED** when finalized. Append a miss count / miss list.

**Gap analysis output** — one line per metric in `targets.json`, in file order:

```
[YYYY-MM-DD] — Day log updated
─────────────────────────────
<Label>:  <value> / <dir-symbol><target> <unit>   [✓ | ✗ short/over X]
... (one per target) ...
─────────────────────────────
[One sentence on the biggest gap or win; note any HIGH UNCERTAINTY items]
```

(`dir-symbol`: `min` → `≥`, `under` → `<`/`~`.)

---

## Operation: biometrics

The user reports one or more biometric readings. Append each as a row to `biometrics.csv`, then confirm.

**CSV schema — `biometrics.csv`:** `date,time,metric,value,unit,notes`
- `date` — YYYY-MM-DD (today unless specified)
- `time` — `morning`|`midday`|`evening`|`fasted`|`postprandial`|HH:MM (default `morning`)
- `metric` — snake_case (see vocabulary); `value` — numeric; `unit` — per vocabulary; `notes` — context

**Metric vocabulary:** `weight` (lbs) · `bmi` (kg/m², auto-computed) · `bp_systolic`/`bp_diastolic` (mmHg) · `heart_rate` (bpm) · `blood_glucose_fasted`/`blood_glucose_postprandial` (mg/dL) · `ldl`/`hdl`/`triglycerides`/`total_cholesterol` (mg/dL). Log only what the person reports.

**BMI auto-compute:** when weight is reported, append a `bmi` row. `bmi = weight_kg / height_m²` (lbs→kg ÷ 2.205), 1 dp. Height from `~/.local/share/diet/config.json` (`height_m`); if unset, ask, convert, save, proceed. Skip if the person hasn't set a height.

**Output:** one line per row appended: `Logged: [metric] [value] [unit] ([date] [time])`

---

## Operation: fetch

Pull device data for a date via connectors and append each canonical metric to `biometrics.csv`. Date given → use it; else yesterday.

**Canonical-source policy:** each metric has exactly ONE trusted source; everything else a device returns is ignored. Each connector declares which metrics it is authoritative for (e.g. weight/body-composition ← Withings; steps ← FitBit). Only log declared-canonical fields.

**Steps:** determine date → ask each enabled connector for its data → keep only its canonical metrics → append one row per non-null value (`time = morning`) → for weight, also compute+append BMI → dedupe on `date`+`metric` → print a summary.

---

## Operation: pull

Pull all device data for today (or a given date) and import into `biometrics.csv`, running each enabled connector in sequence (e.g. Withings+FitBit via `server/fetch.py <date>`; blood pressure via `server/bp_import.py`; glucose via `server/contour_gdrive.py <date>`). Parse connector output, append new canonical metrics (same mapping as `fetch`), dedupe. Print a per-source summary and the total new rows.

---

## Operation: summary

Read `compliance.csv`, filter today (excluding `daily_total`), sum the nutrient columns, and print a gap analysis against `targets.json`. If no rows exist for today, say so and suggest `/diet log`.

**Steps:** get today's date → read `targets.json` and `compliance.csv` → filter today's non-`daily_total` rows → sum each column → compare to targets per `dir` → print.

**Output:**

```
[YYYY-MM-DD] — Diet summary
─────────────────────────────
Foods logged:
  [meal_context]  [food_item] ([amount_g]g) — [kcal] kcal
  ...

Totals vs targets:  (one line per metric in targets.json)
  <Label>:  <value> / <dir-symbol><target> <unit>   [met / short X / over X]
─────────────────────────────
[One sentence on the biggest gap or win today]
```
