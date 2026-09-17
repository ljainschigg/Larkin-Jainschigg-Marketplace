# Food reference — instance config (template)

*Copy this into the instance directory as `food-reference.md` and edit for the person. The engine reads it during `log`/`summary`; nothing here is baked into the engine. It self-corrects alongside `portion-vocabulary.csv`. Delete rows that don't apply and add the person's real foods.*

## Standing daily habits — auto-log if not already present for today

*Foods the person has every day without mentioning them (e.g. milk in coffee). Leave empty if none.*

| food_item | amount_g | meal_context | kcal | protein_g | sat_fat_g | soy_protein_g | omega3_g | soluble_fiber_g | sodium_mg | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | | | | |

## Vague amount defaults (seed — refined per-user in `portion-vocabulary.csv`)

| User says | Log as | Note |
|---|---|---|
| "a handful" (nuts) | 30g | est. |
| "a few bites" (protein) | 45g | est. |
| "a scoop" (protein powder) | 30g | est. |
| "a tablespoon" (oil, condiment) | 14g | est. |
| "a cup" (liquid) | 240ml | est. |
| "a small handful" (berries) | 40g | est. |

## HIGH UNCERTAINTY items

Flag in `notes` with `HIGH UNCERTAINTY sodium ~Xmg`. On days where any HIGH UNCERTAINTY item is present and sodium is already near its target, warn the user explicitly.

| food_item | key uncertainty | typical sodium est./100g |
|---|---|---|
| any restaurant or prepared dish | recipe unknown | flag as HIGH UNCERTAINTY |

## Nutritional reference values (per 100g unless noted)

*Add the person's common foods. Columns match `compliance.csv`. Use general knowledge for anything unlisted.*

| Food | kcal | protein_g | sat_fat_g | soy_protein_g | omega3_g | soluble_fiber_g | sodium_mg |
|---|---|---|---|---|---|---|---|
| _(add foods)_ | | | | | | | |

## Named recipes (log by name; add fruit and other add-ins as separate rows)

| Recipe | Weight | kcal | protein_g | sat_fat_g | soy_protein_g | omega3_g | soluble_fiber_g | sodium_mg | Contents |
|---|---|---|---|---|---|---|---|---|---|
| _(add recipes)_ | | | | | | | | | |
