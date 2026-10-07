#!/bin/zsh
# T14 phase B launcher. launchd starts this at 01:45 Singapore time every weekday; the Python
# script exits at once unless today (New York date) is in processed/fomc_decisions.csv, and
# otherwise waits until 13:59 ET before polling the Fed. Logs to logs/event_<date>.log.
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; . ./.env; set +a; fi
source .venv/bin/activate
mkdir -p logs
python -m src.event_time_read >> "logs/event_$(TZ=America/New_York date +%Y%m%d).log" 2>&1
