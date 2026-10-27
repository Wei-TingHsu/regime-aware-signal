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
# 22 Oct (TRACK 3.27): the refresh moved here from inside forward_log, followed by the Stooq fallback for the session Yahoo has not
# served yet at this hour, so the forward row's signal bar is the actual last close. forward_log then runs --no-refresh.
python -m src.download_data --force || echo "  download failed -- cached history kept"
python -m src.build_panel || echo "  build_panel failed"
python -m src.price_fallback || echo "  price fallback failed -- continuing"
python -m src.pca_macro || echo "  pca_macro failed"

step "2/7  forward-test row  [THE REGISTERED EXPERIMENT]"
# The one step whose absence cannot be repaired later. It is deliberately NOT
# guarded by || true: if the forward log cannot be written, the run must fail
# loudly so the gap is noticed the same day rather than at submission.
python -m src.forward_log --no-refresh

step "3/7  new policy documents (free)"
# FOMC statements were never auto-fetched before 2026-09-24 (no writer existed);
# --days 60 keeps the nightly call cheap. Minutes stay a manual fetch until
# cmd_minutes is confirmed to tolerate an unpublished date.
# S5: save 1-minute bars for the last 7 days; Yahoo keeps nothing older, so this is the only free intraday history
python -m src.collect_intraday || echo "  intraday collector failed -- continuing"
python -m src.fetch_fomc_statements --days 60 || echo "  FOMC statement fetch failed -- continuing, the corpus is additive"
python -m src.fetch_sources political --start "$(date -v-14d +%Y-%m-%d 2>/dev/null || date -d '14 days ago' +%Y-%m-%d)" \
  --limit 100000 --max-pages 3 \
  --types "executive order,proclamation,notice,memorandum,determination,presidential order" \
  || echo "  fetch failed -- continuing, the corpus is additive"
# 19 Oct (TRACK 3.26): the live feed had two routing faults -- no nightly 8-K fetch since the backfill (last earnings document 14 Aug),
# and presidential documents landing in political/ which step 6 never reads. Earnings: SEC submissions feed, free, skips files on disk.
# Executive orders -> political_order/, proclamations/memoranda/determinations -> political_other/ (the two folders step 6 reads).
SINCE14="$(date -v-14d +%Y-%m-%d 2>/dev/null || date -d '14 days ago' +%Y-%m-%d)"
POOL="$(cat processed/issuer_pool_tickers.txt 2>/dev/null || echo NVDA,TSM,ASML,MU,INTC,MSFT,ORCL,TSLA,LMT)"
python -m src.fetch_sources edgar --tickers "$POOL" --limit 4 --sleep 0.5 || echo "  8-K fetch failed -- continuing, the corpus is additive"
python -m src.fetch_sources political --start "$SINCE14" --limit 100000 --max-pages 3 --types "executive order" --out political_order \
  || echo "  executive-order fetch failed -- continuing"
python -m src.fetch_sources political --start "$SINCE14" --limit 100000 --max-pages 3 --types "proclamation,memorandum,determination,presidential order" --out political_other \
  || echo "  proclamation fetch failed -- continuing"

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
# T13 case A: per-market coverage state and the oil-shock chain alert for the last completed session
python -m src.blindspot --today || echo "  blindspot failed -- continuing"
# 22 Oct (TRACK 3.27 audit): the oil columns were built once on 12 Oct and read stale ever since; rebuild nightly before the oil forward row
python -m src.wti_cont build || echo "  wti_cont rebuild failed -- continuing"
python -m src.oil_shock forward || echo "  oil forward failed -- continuing"
python -m src.latency_audit || echo "  latency audit failed -- continuing"
# TRACK 3.33: turning points, episode and last-session attribution, base-rate target, every asset incl. silver
python -m src.flows update || echo "  flows update failed -- continuing"
python -m src.why_moved run > /dev/null || echo "  why_moved failed -- continuing"
