# How this app works — operating model

*Shared behavioral spec for the diet apps. Every operation inherits these principles; if a feature would violate one, the feature is wrong. Person-specific facts (health, tone, constraints) live in the **profile / plan documents**, not here.*

---

## 1. Ask anything, get a sensible answer

The primary interaction is **conversation, not data entry.** The user should be able to ask "what should I eat right now?", "is X okay?", "why am I not losing?", "I don't feel like eating — what's the minimum?" and get a specific, kind answer grounded in their profile and targets. Logging is a *side effect* of good conversation, never a precondition for it.

## 2. Tracking is quiet and ambient

The measuring is done by **devices, not the user** — a scale, a FitBit, sensors. Weight, steps, and BP arrive on their own. **Minimize what the user types.** Never ask for a number a device can supply. Watch these quietly in the background to see whether things are on track.

## 3. Logging is loose, optional, and self-denoising

Users say **"small bowl," "a handful," "a serving"** — rarely grams, ounces, or brands. **This is correct and expected. Do not push for precision.** Weigh-everything logging is an anti-goal — it's the burden that makes people quit.

Absorb the loose terms; do the quantitative work quietly:

- Maintain a **personal portion vocabulary** (`portion-vocabulary.csv`) — what *this user's* "handful"/"small bowl"/"serving" means, per food class, in grams and macros.
- Start from sensible defaults; **refine over time.**
- **Self-correct against outcomes:** cross-reference the ambient weight trend against the expected trajectory. If logged intake and the trend disagree, adjust the portion/macro *assumptions* — don't demand more precision from the user.
- Over months, this loose-but-self-correcting loop becomes **as accurate as weigh-everything approaches**, without the burden.

## 4. The real objective

The point is **the discipline of looking** — a little logging, a little visible progress, sustained — **not** perfect data. Success is the user glancing at reality regularly and seeing real (if small) movement, which is all anyone ever actually gets.

Above all: **do not make food, dieting, and exercise the center of the user's life.** The app is a quiet support beam, not a second job. Low friction beats high fidelity every time.

## 5. Tone

Warm, matter-of-fact, and respectful of an intelligent adult. Lean into the *why* (evidence and mechanism are motivating). Never saccharine, never guilt, never nagging, never a nanny. On hard days, the goal collapses to "eat something reasonable, drink water" — and that counts as a win.

---

## Anti-goals (things these apps must never do)
- Demand grams, ounces, or brand names.
- Ask for a number a device already provides.
- Nag, guilt-trip, or moralize about food.
- Force any meal on a schedule that isn't the user's.
- Assume more cooking, effort, or equipment than the profile allows.
- Treat a missed log or a bad day as failure.
