#!/bin/zsh
# =============================================================================
# overnight.sh -- the credit-spending jobs, run once while the Mac is held awake:
#
#     caffeinate -is ./overnight.sh
#
# Order (28 Oct 2026): (1) T-K3 chair style -- selftest, cost, rubric read, acceptance check, test, record
#                      (2) the Federal Register backlog -- coverage before, route, measured cost against CAP_USD,
#                          run_corpus.sh (lock + abort on the first credit/auth error), read CSVs, gate, backfill under
#                          the new hash, coverage after, the section-8 comparison against the baseline, record.
# Registrations: docs/prereg_liquidity_and_chair.md (T-K3, 28 Oct amendment), docs/prereg_political_backfill.md.
# Knobs:  CAP_USD=40  STYLE=1  POLITICAL=1   (STYLE=0 / POLITICAL=0 skip a part)
# Nothing here touches models.yaml, the forward ledgers, outputs/reports/ or the nightly job.
# =============================================================================
set -u
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; . ./.env; set +a; fi
source .venv/bin/activate
mkdir -p logs
LOG="logs/overnight_$(date +%Y%m%d_%H%M).log"
exec > >(tee -a "$LOG") 2>&1
CAP_USD="${CAP_USD:-40}"; STYLE="${STYLE:-1}"; POLITICAL="${POLITICAL:-1}"
BASELINE="processed/report_backfill_48a6c4e879a1_n2617_h2.csv"
echo "overnight start $(date '+%F %T %Z'); cap US\$$CAP_USD; STYLE=$STYLE POLITICAL=$POLITICAL; log $LOG"

# ---- guards ---------------------------------------------------------------------------------------------------------------
HH=$(date +%H)
if [ "$HH" -ge 14 ] && [ "$HH" -lt 18 ]; then echo "refusing to start between 14:00 and 18:00 SGT: the nightly job runs at 15:00"; exit 1; fi
python - <<'PY' || exit 1
# refuse to start in the 2 pm ET FOMC window (01:30-03:00 SGT) on a decision day: the live statement read must not queue behind a corpus read
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("Asia/Singapore")); ny = datetime.now(ZoneInfo("America/New_York")).date()
days = set(pd.to_datetime(pd.read_csv("processed/fomc_decisions.csv").iloc[:, 0], errors="coerce").dt.date.dropna())
if ny in days and (now.hour, now.minute) >= (1, 30) and now.hour < 3:
    raise SystemExit(f"refusing to start: FOMC day in New York ({ny}) and it is {now:%H:%M} SGT -- the 2 pm reader owns this window")
print(f"guard: NY date {ny}, FOMC day: {ny in days}; SGT {now:%H:%M} -- ok")
PY
if [ -d .corpus_read.lock ]; then echo "corpus read lock is held (.corpus_read.lock) -- another reader is running or died holding it; see run_corpus.sh"; exit 1; fi
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then echo "ANTHROPIC_API_KEY is not set in .env"; exit 1; fi

# ---- 1. T-K3 chair style ---------------------------------------------------------------------------------------------------
if [ "$STYLE" = "1" ]; then
  echo "=== 1. T-K3 chair style ==="
  python -m src.chair_style selftest || { echo "selftest FAIL -- the rubric read is NOT run"; STYLE=0; }
fi
if [ "$STYLE" = "1" ]; then
  python -m src.chair_style cost
  if python -m src.chair_style read; then
    python -m src.chair_style acceptance || echo "  acceptance check failed to run"
    python -m src.chair_style test       || echo "  test failed to run"
    python -m src.chair_style record     || echo "  record failed"
  else
    echo "T-K3 read stopped on a fatal error (credit or key). Nothing else is attempted tonight: the same balance feeds the political read."
    exit 1
  fi
fi

# ---- 2. the Federal Register backlog ---------------------------------------------------------------------------------------
if [ "$POLITICAL" = "1" ]; then
  echo "=== 2. political backlog ==="
  python -m src.source_compare coverage --tag before || echo "  coverage (before) failed -- C1 will be reported without a 'before'"
  if ! python -m src.political_route --cap "$CAP_USD" --apply; then
    echo "routing stopped (measured cost above CAP_USD=$CAP_USD, or an error) -- nothing read. Raise CAP_USD deliberately and relaunch."; exit 1
  fi
  python measure_unread.py || true
  if ./run_corpus.sh; then
    python rebuild_csv.py --all
    python -m src.gate_check || echo "  GATE FAIL or error -> C2 not met: the new documents are reported separately, never pooled (prereg section 3)"
    python -m src.report_backfill || echo "  backfill failed"
    python -m src.source_compare coverage --tag after || true
    NEW=$(ls -t processed/report_backfill_*.csv | head -1)
    if [ "$NEW" = "$BASELINE" ] || [ -z "$NEW" ]; then
      echo "  no new backfill CSV found -- comparison not run"
    else
      python -m src.source_compare compare --baseline "$BASELINE" --new "$NEW" --record || echo "  comparison failed"
    fi
    python -m src.corpus_status || true
  else
    echo "corpus read did not complete -- gate, backfill and comparison NOT run: a half-read corpus is not a baseline. Relaunch once the cause is fixed; cached reads are never re-billed."
  fi
fi
echo "overnight done $(date '+%F %T %Z') -- log $LOG"
