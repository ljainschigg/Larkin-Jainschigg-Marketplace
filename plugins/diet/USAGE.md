# /diet — daily quick reference

*The engine is person-neutral; the specifics below (targets, foods, standing habits) come from **your** instance config — `targets.json` and `food-reference.md`.*

## Daily workflow

| When | Command | What to say |
|---|---|---|
| Any meal/snack | `/diet log` | whatever you ate |
| Anytime | `/diet summary` | check where you stand without logging |
| Device sync | `/diet fetch` | pull yesterday's device data |
| Full sync | `/diet pull` | all enabled devices for today |

Any standing daily habits you've listed in `food-reference.md` are auto-logged on your first call of the day — you never need to mention them.

---

## Operations

### `/diet log`
Describe what you ate. Grams are best but entirely optional — vague amounts are resolved automatically:

| You say | Logged as |
|---|---|
| "a handful" (nuts) | 30g |
| "a small handful" (berries, edamame) | 40g |
| "a few bites" (protein) | 45g |
| "a slice" (rugbrød, dense bread) | 30g |
| "a scoop" (whey protein powder) | 30g |
| "a tablespoon" (oil, condiment) | 14g |
| "a cup" (liquid) | 240ml |

Anything outside the table gets a best-guess estimate noted in the log. Correct anything that looks off.

Anything outside the table gets a best-guess estimate noted in the log — correct anything that looks off, and the portion vocabulary self-corrects over time.

> *"a big salad with some salmon and a handful of nuts"*
> *"half a burrito, a soy egg, did the supplements"*

The engine reads today's existing rows, skips duplicates, updates the running `daily_total`, and prints a gap analysis against `targets.json`.

### `/diet biometrics`
Report weight, BP, glucose, or lipids.
> *"weight 194 lbs"* → logs weight (+ BMI if a height is set)
> *"BP 118/74"* → logs systolic + diastolic
> *"fasted glucose 91"*

### `/diet summary`
Today's full gap analysis from existing rows. No new logging.

### `/diet fetch [YYYY-MM-DD]` · `/diet pull [YYYY-MM-DD]`
Pull enabled device data into `biometrics.csv` (fetch defaults to yesterday; pull to today). Requires connectors configured via `secret-resolver`.

---

## Targets

Your targets live in `targets.json` and drive every gap analysis — one line per metric, graded by direction (`min` → `≥`, `under` → `<`). Edit that file to change what you steer by.

---

## Watch-outs

**Loose amounts self-correct** — don't fuss over grams. If a term is ambiguous (e.g. "2x psyllium"), pin its meaning in `portion-vocabulary.csv` once and it resolves consistently thereafter.

**HIGH UNCERTAINTY sodium** — cured/pickled fish, deli meats, and restaurant/prepared dishes vary a lot; the engine flags them and warns when a capped metric (e.g. sodium) is already near its target.

**Devices measure; you don't** — weight, steps, BP arrive from the scale/tracker via `fetch`/`pull`; never type a number a device can supply (see `approach.md`).
