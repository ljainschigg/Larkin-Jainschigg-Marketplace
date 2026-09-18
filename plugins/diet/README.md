# diet — health-behavior tracking engine

A person-neutral Claude Code plugin for tracking food intake and biometric readings against **your own** health targets — with loose, low-burden logging, a self-correcting portion vocabulary, and optional device sync. The engine ships no one's numbers or foods; all personalization lives in your instance's config files.

---

## How it's structured

- **The engine** (this plugin) — the operations (`log`, `biometrics`, `summary`, `fetch`, `pull`, `setup`) and the operating model in `approach.md`. Versioned and installed; never holds personal data.
- **Your instance** (your working directory) — your config and data:
  - `targets.json` — the daily targets the engine measures against
  - `food-reference.md` — your foods, recipes, standing habits, and HIGH-UNCERTAINTY list
  - `portion-vocabulary.csv` — the living map of your loose amounts → grams/macros
  - `compliance.csv` / `biometrics.csv` — your logs

Templates for the first three ship in `templates/`; `/diet setup` copies them.

---

## Install

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
/plugin install diet@Larkin-Jainschigg-Marketplace
```

## Use

### Log food intake

```
/diet log
```

Describe what you ate. Gram amounts are precise but not required — vague measures are resolved automatically: "a handful" of nuts → 30g, "a few bites" of protein → 45g, "a slice" of rugbrød → 30g, "a cup" of liquid → 240ml, and so on. Anything outside the standard defaults gets a best-guess estimate noted in the log.

Claude looks up nutritional values, appends rows to `compliance.csv`, and prints a gap analysis against your daily targets (calories, protein, saturated fat, soy protein, soluble fiber, omega-3, sodium).

Examples:
- *"300g roast broccoli, 177g baked salmon, 25g walnuts, 40g rolled oats with 100g kefir"*
- *"a handful of walnuts, a few bites of salmon, slice of rugbrød"*
- *"a bowl of lentil soup, some edamame, did all the supplements"*

---

## Use

| Command | What it does |
|---|---|
| `/diet log` | Describe what you ate; the engine looks up nutrition, appends to `compliance.csv`, and prints a gap analysis against `targets.json`. Vague amounts ("a handful", "a cup") are resolved via your `portion-vocabulary.csv`. |
| `/diet biometrics` | Report weight, BP, glucose, or lipids; appended to `biometrics.csv` (BMI auto-computed if you've set a height). |
| `/diet summary` | Today's gap analysis from existing rows — no new logging. |
| `/diet fetch [date]` | Pull enabled device data for a date (default: yesterday). |
| `/diet pull [date]` | Full device sync for today (or a given date). |

Logging is loose and incremental — call `/diet log` as many times a day as you like; grams and brand names are never required (see `approach.md`).

---

## Device sync (optional)

Manual logging needs no credentials. For device sync, credentials live per-user **outside the plugin** in the `secret-resolver` tool (keys `<domain>/<service>/<field>`) — never in this plugin or your instance. Once:

```bash
secret-resolver install                              # register the resolver
secret-resolver set personal/fitbit/client_id        # store client id/secret (and client_secret)
uv run server/setup_fitbit_auth.py                   # OAuth; tokens land in the resolver
```

Likewise `setup_withings_auth.py` and `setup_gdrive_auth.py` (Google Drive is only needed for BP/glucose import). Migrating an older instance that kept `server/secrets.json`? Run `uv run server/migrate_secrets_to_resolver.py` once, verify, then delete the old JSON.

---

## How it works

Every invocation is self-contained: the engine reads your instance config and produces consistent output regardless of prior conversation. Logging is deliberately loose and **self-correcting** — the portion vocabulary learns what *your* "handful" means over time and reconciles against the ambient weight trend, so precision isn't required (see `approach.md`). The deterministic CSV math (summing a day, grading against targets, recomputing `daily_total`) is handled by `server/diet.py`.

---

## Details

| | |
|---|---|
| **Version** | 2.1.7 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
