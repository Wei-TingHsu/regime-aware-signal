#!/bin/zsh
# =============================================================================
# run_corpus.sh -- finish the corpus read in ONE launch.
#
# WHY THE LOCK EXISTS (added 2026-08-25)
#     The atomic os.replace() in doc_read.py means a second concurrent launch
#     can no longer CORRUPT a cache entry. It can still BILL every unread
#     document twice: both processes check the same empty cache slot before
#     either writes it, both miss, both call the API. On the ~932 documents
#     outstanding that is roughly $16 of double billing.
#
#     "Launch it once" as a human instruction has already failed once on this
#     project -- that is what corrupted the cache on 2026-08-25. A guard that
#     the machine enforces is worth more than an instruction that the operator
#     remembers.
#
#     mkdir is atomic on POSIX: exactly one of two racing processes creates the
#     directory, the other gets EEXIST. A stale lock is REPORTED, never
#     auto-removed -- auto-removal reopens the race it was added to close.
# =============================================================================
set -e          # STOP on the first non-zero exit. doc_read exits 1 on a fatal
                # error; without this the script just tries the next source and
                # burns more calls against the same exhausted balance.
set -u

cd ~/Projects/regime-aware-signal

LOCK="$PWD/.corpus_read.lock"

if ! mkdir "$LOCK" 2>/dev/null; then
  echo "" >&2
  echo "!!!!!! ANOTHER CORPUS READ IS ALREADY RUNNING (or died holding the lock)" >&2
  if [[ -f "$LOCK/pid" ]]; then
    OTHER=$(cat "$LOCK/pid")
    if kill -0 "$OTHER" 2>/dev/null; then
      echo "  PID $OTHER is alive. Do NOT start a second reader: it would bill" >&2
      echo "  every unread document a second time. Wait for it, or kill it." >&2
    else
      echo "  PID $OTHER is NOT running -- this is a STALE lock from a run that" >&2
      echo "  was killed. Inspect, then remove it BY HAND:" >&2
      echo "" >&2
      echo "      rm -rf '$LOCK'" >&2
      echo "" >&2
      echo "  It is not removed automatically: doing so would reintroduce the" >&2
      echo "  double-launch race the lock exists to prevent." >&2
    fi
  fi
  exit 1
fi
echo $$ > "$LOCK/pid"
cleanup() { rm -rf "$LOCK"; }
trap cleanup EXIT INT TERM

echo "corpus read starting, PID $$, lock held at $LOCK"

source .venv/bin/activate

# Clear any unparseable cache entry and any stray .tmp left by an interrupted
# atomic write, BEFORE the read. Costs nothing; a corrupt entry found here is
# one API call, a corrupt entry found mid-run is a diagnostic detour.
python -m src.doc_read --repair-cache

# State before. Recorded so the log carries the starting counts and the run can
# be audited against them afterwards without trusting the log's own totals.
python -m src.corpus_status

python -m src.doc_read --source fomc_statement               --out processed/read_statement.csv
python -m src.doc_read --source fomc_minutes    --with-prev  --out processed/read_minutes.csv
python -m src.doc_read --source earnings_8k                  --out processed/read_8k.csv
python -m src.doc_read --source political_order              --out processed/read_political_order.csv
python -m src.doc_read --source political_other              --out processed/read_political_other.csv

# State after, from disk. If this still shows unread documents the run did not
# finish, whatever the line below says.
python -m src.corpus_status

echo "CORPUS READ COMPLETE"
