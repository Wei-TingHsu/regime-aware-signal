#!/bin/zsh
# Load secrets for EVERY step (doc_read.py does not call load_dotenv itself).
# .env is git-ignored; .env.example lists the names. TRACK section 7.
if [ -f .env ]; then set -a; . ./.env; set +a; fi
# =============================================================================
# daily_run.sh -- STEP 7. One command, run every trading evening by launchd.
#
# WHY THIS EXISTS
#     The forward test is a PRE-REGISTERED LIVE EXPERIMENT. Its value is that
#     its timestamps make retrospective claim-fitting impossible -- and that
#     value is destroyed by a gap. A log that stops on 19 August is not a
#     stale website; it is an experiment that stopped running, and no amount of
#     back-filling later can repair it, because back-filled rows are exactly
#     what the design excludes.
#
#     So this runs unattended, every weekday, and fails loudly rather than
#     silently skipping.
#
# WHAT IT DOES, IN ORDER
#     1. refresh prices and macro       (free)
#     2. append today's forward-test row (free) -- the registered experiment
#     3. fetch any new policy documents  (free, Federal Register)
#     4. read ONLY the new documents     (costs money; skipped if --no-read)
#     5. rebuild the read CSVs from cache (free)
#     6. regenerate today's decision report (free)
#     7. refresh the report index the app reads (free)
#
#     Step 4 is the only paid step and it is capped: --max-new limits how many
#     documents a single night may read, so an unattended job cannot empty the
#     API balance while nobody is watching. That failure has happened four
#     times on this project already.
#
# WHY IT DOES NOT REFIT ANYTHING
#     The three forward-test models are FROZEN in models.yaml. The regime model
#     is refit on an expanding window inside the pipeline, never here. This
#     script adds observations; it never changes an estimator. A nightly job
#     that quietly re-tuned a model would invalidate every registered result
#     behind it.
#
# Run manually:   ./daily_run.sh
#                 ./daily_run.sh --no-read     # free, no API spend at all
# =============================================================================
set -e
set -u
cd "$(dirname "$0")"

LOCK="$PWD/.daily_run.lock"
LOG="$PWD/logs/daily_$(date +%Y%m%d).log"
mkdir -p logs outputs/reports

if ! mkdir "$LOCK" 2>/dev/null; then
  if [[ -f "$LOCK/pid" ]] && kill -0 "$(cat "$LOCK/pid")" 2>/dev/null; then
    echo "$(date): another daily run is live (PID $(cat "$LOCK/pid")). Exiting." >> "$LOG"
    exit 0
  fi
  echo "$(date): STALE LOCK at $LOCK from a killed run. Not removing it" >> "$LOG"
  echo "  automatically -- that reopens the double-launch race. Remove by hand:" >> "$LOG"
  echo "      rm -rf '$LOCK'" >> "$LOG"
  exit 1
fi
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT INT TERM

NO_READ=0
MAX_NEW=40
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-read) NO_READ=1; shift;;
    --max-new) MAX_NEW="$2"; shift 2;;
    *) shift;;
  esac
done

# When launchd runs this there is no terminal, so everything goes to the log.
# When a human runs it, silence looks like failure -- so tee to both.
if [[ -t 1 ]]; then
  exec > >(tee -a "$LOG") 2>&1
  echo "(also logging to $LOG)"
else
  exec >> "$LOG" 2>&1
fi
echo "==============================================================="
echo "DAILY RUN  $(date '+%Y-%m-%d %H:%M:%S %z')   PID $$"
echo "==============================================================="

source .venv/bin/activate

step () { echo; echo "--- $1 ---"; }

step "1/7  prices and macro"
python -m src.data_io || echo "  (data_io has no CLI entry point; skipped)"

step "2/7  forward-test row  [THE REGISTERED EXPERIMENT]"
# The one step whose absence cannot be repaired later. It is deliberately NOT
# guarded by || true: if the forward log cannot be written, the run must fail
# loudly so the gap is noticed the same day rather than at submission.
python -m src.forward_log

step "3/7  new policy documents (free)"
# FOMC statements were never auto-fetched before 2026-09-24 (no writer existed);
# --days 60 keeps the nightly call cheap. Minutes stay a manual fetch until
# cmd_minutes is confirmed to tolerate an unpublished date.
python -m src.fetch_fomc_statements --days 60 || echo "  FOMC statement fetch failed -- continuing, the corpus is additive"
python -m src.fetch_sources political --start "$(date -v-14d +%Y-%m-%d 2>/dev/null || date -d '14 days ago' +%Y-%m-%d)" \
  --limit 100000 --max-pages 3 \
  --types "executive order,proclamation,notice,memorandum,determination,presidential order" \
  || echo "  fetch failed -- continuing, the corpus is additive"

step "4/7  read new documents"
if [[ "$NO_READ" -eq 1 ]]; then
  echo "  --no-read: skipped. No API spend this run."
else
  echo "  cap: $MAX_NEW new documents, so an unattended job cannot drain the"
  echo "  balance overnight. Four interruptions on this project were caused by"
  echo "  exactly that."
    # Documents dated before READ_SINCE are deferred backfill sets (TRACK 3.1:
  # 4,595 political; 163 over-cap 6-Ks). They are read as dedicated, funded
  # runs -- never by the nightly cap, which would spend it oldest-first.
  READ_SINCE=20260827
  for SRC in fomc_statement fomc_minutes earnings_8k political_order political_other political; do
    python -m src.doc_read --source "$SRC" --unread-only --since "$READ_SINCE" --limit "$MAX_NEW" \
      --out "processed/read_$(echo $SRC | sed 's/fomc_//;s/political_//;s/earnings_//').csv" \
      || { echo "  READ ABORTED on $SRC -- see the line above: a missing ANTHROPIC_API_KEY prints \"set ANTHROPIC_API_KEY\"; an empty balance prints an API error. They are not the same fault."; break; }
  done
fi

step "5/7  rebuild read CSVs from cache (free)"
python rebuild_csv.py --all

step "6/7  decision reports -- every completed session since 11 Sep with no report; deferred while its documents are unread"
for D in $(python step6_report.py --pending | awk '/^PENDING /{print $2}'); do
  python step6_report.py --date "$D"
done

step "6b/7 FOMC->GLD forward ledger (registered 2026-09-08)"
python fomc_gld_forward.py 2>/dev/null | tail -4 || echo "  (no new matured FOMC observation)"

step "6c/7 report-level scoreboard (docs/prereg_report_scoreboard.md) -- scores reports on disk; never writes one"
python -m src.report_scoreboard \
  || echo "  report scoreboard FAILED -- reports and forward ledger untouched; see traceback above; continuing"

step "7/7  refresh the index the app reads"
# index-only: reports on disk are frozen; only the index is rebuilt.
python generate_reports.py --index-only

echo
echo "DONE  $(date '+%H:%M:%S')"
python -m src.corpus_status | tail -14

step "8/7  commit the record and push -- ledgers, scoreboards, write-once reports (TRACK section 7)"
# Only these paths are staged; unrelated working-tree changes are never swept in.
# outputs/ and processed/ are git-ignored, hence -f. .env is never listed here.
git add -f processed/forward_ledger.csv processed/report_ledger.csv \
           processed/asset_returns.parquet processed/macro_pca_scores.parquet processed/pipeline_coverage.json \
           docs/forward_scoreboard.md docs/report_scoreboard.md docs/fomc_gld_forward.md docs/pipeline_coverage.md docs/fomc_minutes_forward.md \
           outputs/reports/*.json outputs/reports/*.md 2>/dev/null
if git diff --cached --quiet; then
  echo "  nothing new to commit"
else
  git commit -qm "nightly record $(date '+%Y-%m-%d'): ledgers, scoreboards, reports" && echo "  committed"
  git push -q 2>&1 | tail -1 || echo "  PUSH FAILED -- commit is local; push by hand"
fi
