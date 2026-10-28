#!/bin/zsh
# =============================================================================
# overnight.sh v2 -- the credit-spending jobs, run once while the Mac is held awake:
#
#     caffeinate -is ./overnight.sh
#
# v2 (28 Oct, after the first run read 165 declined 6-Ks for ~US$71): the cost guard now covers the WHOLE unread set as
# measure_unread.py counts it, any unread earnings_8k stops the run unless READ_8K=1, and the political sources are read
# directly (own lock) instead of through run_corpus.sh, which reads every source.
#
# Order: (1) T-K3 chair style -- selftest, cost, rubric read, acceptance, test, record
#        (2) the political sources -- coverage before, route, measured cost against CAP_USD, read political_order and
#            political_other only, read CSVs, gate (--allow-partial: the 47 retired-profile reads are a recorded shortfall),
#            backfill under the new hash, coverage after, the section-8 comparison with the gate's verdict passed in.
# Knobs:  CAP_USD=40  STYLE=1  POLITICAL=1  READ_8K=0  GATE_ITERS=10000
# Nothing here touches models.yaml, the forward ledgers, outputs/reports/ or the nightly job.
# =============================================================================
set -u
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; . ./.env; set +a; fi
source .venv/bin/activate
mkdir -p logs
LOG="logs/overnight_$(date +%Y%m%d_%H%M).log"
exec > >(tee -a "$LOG") 2>&1
CAP_USD="${CAP_USD:-40}"; STYLE="${STYLE:-1}"; POLITICAL="${POLITICAL:-1}"; READ_8K="${READ_8K:-0}"; GATE_ITERS="${GATE_ITERS:-10000}"
BASELINE="processed/report_backfill_48a6c4e879a1_n2617_h2.csv"
echo "overnight v2 start $(date '+%F %T %Z'); cap US\$$CAP_USD over the whole unread set; STYLE=$STYLE POLITICAL=$POLITICAL READ_8K=$READ_8K; log $LOG"

# ---- guards ---------------------------------------------------------------------------------------------------------------
HH=$(date +%H)
if [ "$HH" -ge 14 ] && [ "$HH" -lt 18 ]; then echo "refusing to start between 14:00 and 18:00 SGT: the nightly job runs at 15:00"; exit 1; fi
python - <<'PY' || exit 1
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("Asia/Singapore")); ny = datetime.now(ZoneInfo("America/New_York")).date()
days = set(pd.to_datetime(pd.read_csv("processed/fomc_decisions.csv").iloc[:, 0], errors="coerce").dt.date.dropna())
if ny in days and (now.hour, now.minute) >= (1, 30) and now.hour < 3:
    raise SystemExit(f"refusing to start: FOMC day in New York ({ny}) and it is {now:%H:%M} SGT -- the 2 pm reader owns this window")
print(f"guard: NY date {ny}, FOMC day: {ny in days}; SGT {now:%H:%M} -- ok")
PY
LOCK="$PWD/.corpus_read.lock"
if [ -d "$LOCK" ]; then echo "corpus read lock is held ($LOCK) -- another reader is running or died holding it; see run_corpus.sh"; exit 1; fi
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then echo "ANTHROPIC_API_KEY is not set in .env"; exit 1; fi

# ---- 1. T-K3 chair style ---------------------------------------------------------------------------------------------------
if [ "$STYLE" = "1" ]; then
  echo "=== 1. T-K3 chair style ==="
  python -m src.chair_style selftest || { echo "selftest FAIL -- the rubric read is NOT run"; STYLE=0; }
fi
if [ "$STYLE" = "1" ]; then
  python -m src.chair_style cost
  if python -m src.chair_style read; then
    python -m src.chair_style acceptance || echo "  acceptance check did not run (a registered set has an unread member?)"
    python -m src.chair_style test       || echo "  test did not run"
    python -m src.chair_style record     || echo "  record did not run"
  else
    echo "T-K3 read stopped on a fatal error (credit or key). Nothing else is attempted tonight."; exit 1
  fi
fi

# ---- 2. the political sources ---------------------------------------------------------------------------------------------
if [ "$POLITICAL" = "1" ]; then
  echo "=== 2. political sources ==="
  python -m src.source_compare coverage --tag before || echo "  coverage (before) failed -- C1 will be reported without a 'before'"
  if ! python -m src.political_route --cap "$CAP_USD" --apply; then
    echo "routing stopped (measured cost above CAP_USD=$CAP_USD, or an error) -- nothing read."; exit 1
  fi
  # the guard that was missing on 28 Oct: price EVERYTHING unread, refuse unread 8-Ks, cap the total
  python measure_unread.py | tee /tmp/measure_unread.$$ || true
  UNREAD_8K=$(awk '/^  earnings_8k/ {print $2}' /tmp/measure_unread.$$ | head -1); UNREAD_8K="${UNREAD_8K:-0}"
  TOTAL_USD=$(awk '/TOTAL  \$/ {print $3}' /tmp/measure_unread.$$ | head -1); TOTAL_USD="${TOTAL_USD:-0}"
  rm -f /tmp/measure_unread.$$
  echo "measured: unread earnings_8k $UNREAD_8K; whole unread set US\$$TOTAL_USD; cap US\$$CAP_USD"
  if [ "$UNREAD_8K" != "0" ] && [ "$READ_8K" != "1" ]; then
    echo "  $UNREAD_8K unread earnings_8k document(s) on disk. This runner reads political sources only; 8-Ks need READ_8K=1 and a registration."
  fi
  python - "$TOTAL_USD" "$CAP_USD" <<'PY' || exit 1
import sys
tot, cap = float(sys.argv[1]), float(sys.argv[2])
if tot > cap: raise SystemExit(f"measured cost of the whole unread set US${tot:.2f} is above the cap US${cap:.0f} -- nothing read. Read a subset, or raise CAP_USD deliberately.")
print(f"guard: US${tot:.2f} <= US${cap:.0f} -- ok")
PY
  if ! mkdir "$LOCK" 2>/dev/null; then echo "could not take the corpus lock"; exit 1; fi
  echo $$ > "$LOCK/pid"; trap 'rm -rf "$LOCK"' EXIT INT TERM
  OK=1
  python -m src.doc_read --repair-cache || true
  python -m src.doc_read --source political_order --unread-only --out processed/read_political_order_new.csv || OK=0
  python -m src.doc_read --source political_other --unread-only --out processed/read_political_other_new.csv || OK=0
  if [ "$READ_8K" = "1" ]; then python -m src.doc_read --source earnings_8k --unread-only --out processed/read_8k_new.csv || OK=0; fi
  rm -rf "$LOCK"; trap - EXIT INT TERM
  if [ "$OK" = "1" ]; then
    python rebuild_csv.py --all
    GATE=FAIL
    if python -m src.gate_check --iters "$GATE_ITERS" --allow-partial; then GATE=PASS; fi
    echo "gate (C2): $GATE"
    python -m src.report_backfill || echo "  backfill failed"
    python -m src.source_compare coverage --tag after || true
    NEW=$(ls -t processed/report_backfill_*.csv | head -1)
    if [ "$NEW" = "$BASELINE" ] || [ -z "$NEW" ]; then
      echo "  no new backfill CSV found -- comparison not run"
    else
      EXCL=""
      python -m src.source_compare newdocs --source earnings_8k --on "$(date +%F)" && EXCL="processed/newdoc_dates_earnings_8k_$(date +%F).txt"
      if [ -n "$EXCL" ] && [ -s "$EXCL" ]; then
        python -m src.source_compare compare --baseline "$BASELINE" --new "$NEW" --exclude-dates "$EXCL" --gate "$GATE" --record || echo "  comparison failed"
      else
        python -m src.source_compare compare --baseline "$BASELINE" --new "$NEW" --gate "$GATE" --record || echo "  comparison failed"
      fi
    fi
    python -m src.corpus_status || true
  else
    echo "a read did not complete -- gate, backfill and comparison NOT run: a half-read corpus is not a baseline. Cached reads are never re-billed."
  fi
fi
echo "overnight done $(date '+%F %T %Z') -- log $LOG"
