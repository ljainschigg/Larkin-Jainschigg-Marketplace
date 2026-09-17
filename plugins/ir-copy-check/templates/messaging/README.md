# Messaging resources (templates)

These are **empty scaffolds** for the `/critique-messaging` skill. Copy this
folder's files into your working directory's `./resources/` and fill each with
your own material. Nothing here is real data.

The skill maps files to roles by content, so you may rename or merge them — but
keeping these names makes setup's checks straightforward.

| File | Role |
|------|------|
| `ir-guidance.md` | Most authoritative, most recent direct guidance from your IR function. Overrides inferences elsewhere. |
| `investor-narrative.md` | The parent/investor narrative, framework, key metrics, stated constraints. |
| `product-messaging.md` | The brand's product and positioning messaging. |
| `messaging-tensions.md` | Fault lines and absolute no-gos. This and `ir-guidance.md` define the always-active rules the skill enforces. |
| `approved-boilerplate.md` | Approved messaging frameworks — what "good" looks like. |
| `authentic-voice.md` | The brand's desired voice. Ground truth; the skill does NOT critique this. |
| `strategic-context.md` | Optional. Working theories about strategic intent, with confidence levels. |
| `transition-notes.md` | Optional. Open questions and placeholder rules during an org change. |
| `writing-rules.md` | House tone and formatting rules (governs rewrites). |

Keep these files out of git — they are confidential. `/setup` will gitignore `resources/` for you.
