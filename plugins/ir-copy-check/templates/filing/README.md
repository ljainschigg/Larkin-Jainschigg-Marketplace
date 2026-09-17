# Filing corpus (templates)

These are **empty scaffolds** for the `/critique-vs-10k` skill. Copy this folder's
files into your working directory's `./resources/` and fill each from a company's
filed Form 10-K. Nothing here is real data.

The corpus is a distilled, citable rendering of one 10-K, organized around the
questions marketing content actually raises. Keep it small enough to load in full
on every critique. Consult the sectioned filing text (`./extract/`, produced by
the extractor) for exact wording the corpus does not cover.

| File | Contents |
|------|----------|
| `00-filing-map.md` | Which filing is authority; fiscal-year convention; body-vs-exhibits; how to cite |
| `01-official-self-description.md` | The company's filed self-description; business structure; named competitors |
| `02-defined-terms.md` | The filed glossary; non-GAAP rules; currency and units |
| `03-citable-metrics.md` | Every citable figure with its period; material contracts; figures the filing does NOT support |
| `04-risk-factor-constraints.md` | Risk-factor headings and the claims they cap |
| `05-disclosure-rules.md` | Safe harbor, Reg FD channels, superseded material, scope boundary |
| `corpus-meta.conf` | Freshness guard (dates); read by `corpus_status.sh` |
| `writing-rules.md` | House tone and formatting (governs rewrites) |

You may add entity-specific files (e.g. one distilling everything the filing says
about a subsidiary or a business line). Keep this material out of git — `/setup`
gitignores `resources/` and `extract/` for you.
