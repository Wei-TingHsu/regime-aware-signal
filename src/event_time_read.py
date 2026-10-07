"""
T14 phase B -- read the FOMC statement when it is published, not after the close.

Registered: docs/prereg_event_time.md section 4 (display rule) and TRACK section 3.11 phase B.

On a scheduled FOMC day the launcher starts this before 2:00 pm ET. It:
  1. waits until 13:59 ET, then polls the Fed's statement URL every 10 s until the page exists
     (fetch_fomc_statements writes data_provenance/docs/fomc_statement/YYYYMMDD.txt);
  2. reads it with the SAME reader, prompt version and cache as the nightly job
     (python -m src.doc_read --source fomc_statement --since <today>), so the evening run finds
     the read already done and the daily report is unchanged in method;
  3. writes outputs/event_time/YYYYMMDD.json ONCE: read time, what the statement says per axis,
     stance, specificity, novelty, confidence -- and appends one row to
     processed/event_time_ledger.csv;
  4. 20 minutes later records the market's 1:55 -> 2:15 ET reaction from Yahoo 1-minute bars
     (delayed ~15 min) into outputs/event_time/YYYYMMDD_reaction.json, once.

Nothing here touches outputs/reports/, models.yaml, or the forward ledger. The app's
"Rest of session" line shows the read as soon as the file exists.

Usage
  python -m src.event_time_read                      # live: used by event_run.sh on FOMC days
  python -m src.event_time_read --dry-run --date 2026-09-16   # exercise every step on a past statement
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ET = ZoneInfo("America/New_York")
DOCS = Path("data_provenance/docs/fomc_statement")
READS = Path("data_provenance/doc_reads")
OUT = Path("outputs/event_time")
LEDGER = Path("processed/event_time_ledger.csv")
DECISIONS = Path("processed/fomc_decisions.csv")
AXES = ["equity", "duration", "gold", "dollar", "oil"]
SHOWN = {"^GSPC": "S&P 500", "^TNX": "10-year yield", "GC=F": "gold", "DX-Y.NYB": "DXY", "CL=F": "WTI", "ZQ=F": "fed funds future"}


def log(msg):
    print(f"[{datetime.now(ET):%H:%M:%S ET}] {msg}", flush=True)


def is_fomc_day(d) -> bool:
    if not DECISIONS.exists():
        return False
    days = set(pd.to_datetime(pd.read_csv(DECISIONS).iloc[:, 0], errors="coerce").dt.date.dropna())
    return d in days


def wait_until(hh: int, mm: int):
    target = datetime.now(ET).replace(hour=hh, minute=mm, second=0, microsecond=0)
    while datetime.now(ET) < target:
        time.sleep(min(30, max(1, (target - datetime.now(ET)).total_seconds())))


def fetch_statement(day: str, poll_seconds=10, give_up_minutes=25) -> Path | None:
    f = DOCS / f"{day.replace('-', '')}.txt"
    if f.exists():
        log(f"statement already on disk: {f.name}"); return f
    deadline = time.time() + give_up_minutes * 60
    while time.time() < deadline:
        subprocess.run([sys.executable, "-m", "src.fetch_fomc_statements", "--dates", day], capture_output=True)
        if f.exists():
            log(f"statement fetched: {f.name} ({len(f.read_text().split())} words)"); return f
        time.sleep(poll_seconds)
    log("gave up: statement not published within the window"); return None


def read_statement(day: str) -> dict | None:
    pat = str(READS / f"fomc_statement__{day.replace('-', '')}__*.json")
    if not glob.glob(pat):
        r = subprocess.run([sys.executable, "-m", "src.doc_read", "--source", "fomc_statement",
                            "--since", day.replace("-", ""), "--out", "processed/read_statement.csv"],
                           capture_output=True, text=True)
        tail = (r.stdout or "")[-400:]
        log("reader: " + (tail.strip().splitlines()[-1] if tail.strip() else f"exit {r.returncode}"))
    files = glob.glob(pat)
    if not files:
        log("no read produced -- check the key, the balance and logs"); return None
    return json.loads(Path(sorted(files)[-1]).read_text())


def write_event(day: str, read: dict, dry: bool) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{day.replace('-', '')}.json"
    if f.exists():
        log(f"event file exists, not rewritten: {f.name}"); return f
    ex = read.get("extra") or {}
    stance = ex.get("stance", read.get("stance"))
    direction = {a: (read.get("direction") or {}).get(a) for a in AXES}
    rec = dict(date=day, read_at_et=datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), dry_run=dry,
               prompt_version=read.get("prompt_version"), model=read.get("model"), stance=stance,
               direction=direction, magnitude=read.get("magnitude"), specificity=read.get("specificity"),
               novelty=read.get("novelty"), confidence=read.get("confidence"),
               evidence=(read.get("evidence") or [])[:3])
    f.write_text(json.dumps(rec, indent=2))
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="") as h:
        w = csv.writer(h)
        if new:
            w.writerow(["date", "read_at_et", "dry_run", "stance", *[f"dir_{a}" for a in AXES], "magnitude", "specificity", "novelty", "confidence"])
        w.writerow([day, rec["read_at_et"], dry, stance, *[direction[a] for a in AXES], rec["magnitude"], rec["specificity"], rec["novelty"], rec["confidence"]])
    log(f"event file written: {f.name}; stance {stance}; direction {direction}")
    return f


def record_reaction(day: str, dry: bool):
    f = OUT / f"{day.replace('-', '')}_reaction.json"
    if f.exists():
        log("reaction file exists, not rewritten"); return
    import yfinance as yf
    out = {}
    for tk, name in SHOWN.items():
        try:
            if dry:
                d = yf.Ticker(tk).history(start=day, end=(pd.Timestamp(day) + pd.Timedelta(days=1)).strftime("%Y-%m-%d"), interval="1d", auto_adjust=False)
                if d.empty: continue
                out[name] = dict(ticker=tk, window="open->close (dry run: 1-minute history not available)", start=float(d["Open"].iloc[0]), end=float(d["Close"].iloc[0]))
            else:
                d = yf.Ticker(tk).history(period="1d", interval="1m", auto_adjust=False)
                if d.empty: continue
                idx = d.index.tz_convert(ET)
                a = d[(idx.hour == 13) & (idx.minute >= 55)]["Close"]; b = d[(idx.hour == 14) & (idx.minute >= 10) & (idx.minute <= 15)]["Close"]
                if len(a) and len(b):
                    out[name] = dict(ticker=tk, window="13:55 -> 14:15 ET", start=float(a.iloc[0]), end=float(b.iloc[-1]))
        except Exception as e:
            out[name] = dict(ticker=tk, error=f"{type(e).__name__}: {e}")
    for v in out.values():
        if "start" in v and "end" in v:
            v["change"] = (v["end"] - v["start"]) if v["ticker"] == "^TNX" else (v["end"] / v["start"] - 1)
    f.write_text(json.dumps(dict(date=day, recorded_at_et=datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), dry_run=dry, reaction=out), indent=2))
    log("reaction written: " + ", ".join(f"{k} {v.get('change', float('nan')):+.4f}" for k, v in out.items() if "change" in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--date")
    ap.add_argument("--no-wait", action="store_true", help="live mode without waiting for 13:59 ET (testing)")
    a = ap.parse_args()
    day = a.date or datetime.now(ET).strftime("%Y-%m-%d")
    if not a.dry_run and not is_fomc_day(pd.Timestamp(day).date()):
        log(f"{day} is not in {DECISIONS}; nothing to do"); return
    if not a.dry_run and not a.no_wait:
        log("waiting for 13:59 ET"); wait_until(13, 59)
    f = fetch_statement(day)
    if f is None:
        return
    read = read_statement(day)
    if read is None:
        return
    write_event(day, read, a.dry_run)
    if not a.dry_run and not a.no_wait:
        log("waiting 20 minutes for the delayed 1-minute bars"); time.sleep(20 * 60)
    record_reaction(day, a.dry_run)
    log("done")


if __name__ == "__main__":
    main()
