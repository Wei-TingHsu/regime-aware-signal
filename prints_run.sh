#!/bin/zsh
# 08:30 event-time launcher (TRACK 3.19). launchd starts this at 20:20 and 21:20 Singapore time every weekday; the
# Python script exits at once unless today (New York date) is in processed/release_calendar.csv AND the clock is
# 08:10-08:28 ET (so only one of the two slots does anything, summer or winter). Logs to logs/prints_<date>.log.
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; . ./.env; set +a; fi
source .venv/bin/activate
mkdir -p logs
python -m src.event_time_prints live >> "logs/prints_$(TZ=America/New_York date +%Y%m%d).log" 2>&1
