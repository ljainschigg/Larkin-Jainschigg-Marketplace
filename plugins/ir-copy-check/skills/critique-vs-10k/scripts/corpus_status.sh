#!/usr/bin/env bash
# corpus_status.sh — is this corpus still fit to cite?
#
# A reference corpus derived from a Form 10-K is a snapshot of one fiscal year,
# and it goes stale silently: the figures stay confidently quotable long after
# they stop being current. That is this plugin's worst failure mode.
#
# So a corpus carries a hard drop-dead date. Past it, the skills refuse to
# produce a critique unless the user explicitly and knowingly overrides.
#
# These dates are NOT baked into the plugin — they belong to the user's corpus.
# Set them in a small config file the corpus carries:
#
#     ./resources/corpus-meta.conf
#
# with lines (shell-sourced, so KEY=VALUE, no spaces around =):
#
#     FISCAL_YEAR_END=YYYY-MM-DD    # the fiscal year the corpus covers
#     DROP_DEAD=YYYY-MM-DD          # last date the corpus may be cited as current
#     SNAPSHOT_NOTE="one-line reminder to carry into every critique"   # optional
#
# Pick DROP_DEAD deliberately: the earliest date by which a material later filing
# (the next 10-Q or 10-K) or a stated corporate milestone supersedes the corpus.
#
# Usage:
#   corpus_status.sh [YYYY-MM-DD]     # date arg is for testing; defaults to today
#
# Exit: 0 corpus current or freshness unknown · 1 corpus EXPIRED · 2 usage error

set -euo pipefail

CONF="./resources/corpus-meta.conf"

TODAY="${1:-$(date +%F)}"
if ! printf '%s' "$TODAY" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  echo "usage: $(basename "$0") [YYYY-MM-DD]" >&2
  exit 2
fi

FISCAL_YEAR_END=""
DROP_DEAD=""
SNAPSHOT_NOTE=""
if [[ -f "$CONF" ]]; then
  # shellcheck disable=SC1090
  source "$CONF"
fi

# ── Freshness guard not configured ─────────────────────────────────────────────
if [[ -z "${DROP_DEAD}" ]]; then
  cat <<EOF
STATUS: UNKNOWN

No freshness guard is configured for this corpus. Create ${CONF} and set:

  FISCAL_YEAR_END=YYYY-MM-DD
  DROP_DEAD=YYYY-MM-DD
  SNAPSHOT_NOTE="what a reader must remember about this snapshot"   # optional

Without a drop-dead date this plugin cannot warn you when the corpus has gone
stale — and a superseded figure cited as current, with a citation attached, is
worse than no answer. Set the dates before relying on any critique for
publication clearance.
EOF
  exit 0
fi

# ISO-8601 dates compare correctly as strings.
if [[ "$TODAY" > "$DROP_DEAD" ]]; then
  cat <<EOF
STATUS: EXPIRED

This corpus covers the fiscal year ended ${FISCAL_YEAR_END:-<unset>} and passed
its drop-dead date of ${DROP_DEAD}. Today is ${TODAY}.

Do not produce a critique from it. Its figures are superseded, and citing a
superseded figure as current is worse than declining to answer — the output
looks authoritative precisely because everything in it carries a citation.

By now, later filings (the next 10-Q or a full 10-K) have almost certainly
superseded these figures, and any corporate milestone the corpus treated as
forward-looking may have come due.

TO FIX: download the most recent 10-K from the issuer's investor relations page
or SEC EDGAR into ./resources/, re-run the extractor, and revise
./resources/0*.md against it. Each file carries its period, so what needs
changing is visible. Update DROP_DEAD and FISCAL_YEAR_END in ${CONF}.

TO OVERRIDE: only for a deliberate historical check of what was true in the
covered fiscal year. Every finding must then be stamped as based on an expired
corpus, and the output must not be used to clear content for publication.
EOF
  exit 1
fi

# Portable day-count: GNU date and BSD/macOS date take different flags.
days_left=""
if d1=$(date -d "$DROP_DEAD" +%s 2>/dev/null) && d2=$(date -d "$TODAY" +%s 2>/dev/null); then
  days_left=$(( (d1 - d2) / 86400 ))
elif d1=$(date -j -f %Y-%m-%d "$DROP_DEAD" +%s 2>/dev/null) && d2=$(date -j -f %Y-%m-%d "$TODAY" +%s 2>/dev/null); then
  days_left=$(( (d1 - d2) / 86400 ))
fi

echo "STATUS: CURRENT"
echo
echo "Corpus covers the fiscal year ended ${FISCAL_YEAR_END:-<unset>}. Today is ${TODAY}."
if [[ -n "$days_left" ]]; then
  echo "Drop-dead date ${DROP_DEAD} — ${days_left} day(s) remaining."
else
  echo "Drop-dead date ${DROP_DEAD}."
fi
if [[ -n "${SNAPSHOT_NOTE}" ]]; then
  echo
  echo "Reminder for every critique: ${SNAPSHOT_NOTE}"
fi
exit 0
