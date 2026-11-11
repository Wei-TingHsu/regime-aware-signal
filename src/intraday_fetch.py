"""intraday_fetch.py -- 1-minute prices from Databento for the intraday test (v3e). Step 1 only: check the key, see what exists, and ask the PRICE
before anything is downloaded. Nothing is downloaded by `check` or `cost`.

  pip install databento                       # once, inside the project's virtual environment
  export DATABENTO_API_KEY=...                # typed in the terminal by the founder; never written to a file or committed
  python -m src.intraday_fetch check          # the key works; which datasets the account can see; the date range of the futures dataset
  python -m src.intraday_fetch cost           # price in US$ of 1-minute bars for the instruments the test needs: whole history, and only the days needed
  python -m src.intraday_fetch fetch --max-usd 20 [--full]     # download (only the needed days by default); refuses if the quoted price is above the cap

Instruments (CME futures, dataset GLBX.MDP3, continuous front contract): NQ (Nasdaq-100; stands in for semiconductors intraday), ES (S&P 500),
GC (gold), ZN (10-year Treasury note). They trade almost round the clock, so the 08:30 ET data releases are covered.
Days needed: every Fed statement day (processed/fomc_decisions.csv), every official-document day inside an N1 event window (data_provenance/releases),
and every N1 event day. Files are written once under data_provenance/intraday/<symbol>/<YYYY-MM-DD>.parquet (or <symbol>/<year>.parquet with --full).
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import pandas as pd

DATASET, SCHEMA = "GLBX.MDP3", "ohlcv-1m"
SYMBOLS = {"NQ": "NQ.c.0", "ES": "ES.c.0", "GC": "GC.c.0", "ZN": "ZN.c.0"}
OUT = Path("data_provenance/intraday"); PROC = Path("processed")


def _client():
    if not os.environ.get("DATABENTO_API_KEY"): raise SystemExit("DATABENTO_API_KEY is not set. In the terminal: export DATABENTO_API_KEY=your-key")
    try: import databento as db
    except ImportError: raise SystemExit("the databento package is not installed: pip install databento")
    return db.Historical(os.environ["DATABENTO_API_KEY"])


def needed_days() -> list:
    days = set()
    f = PROC / "fomc_decisions.csv"
    if f.exists(): days.update(pd.to_datetime(pd.read_csv(f)["date"]).dt.date)
    e = PROC / "news_events.csv"
    if e.exists(): days.update(pd.to_datetime(pd.read_csv(e)["date"]).dt.date)
    for p in Path("data_provenance/releases").glob("*.txt"):
        m = re.match(r"[a-z]+_(\d{2})(\d{2})(\d{4})", p.stem)
        if m: days.add(pd.Timestamp(year=int(m.group(3)), month=int(m.group(1)), day=int(m.group(2))).date())
    fs = Path("data_provenance/docs/fomc_statement")
    if fs.exists(): days.update(pd.to_datetime(p.stem, format="%Y%m%d").date() for p in fs.glob("*.txt") if re.fullmatch(r"\d{8}", p.stem))
    return sorted(days)


def _range(c):
    r = c.metadata.get_dataset_range(dataset=DATASET); start = str(r.get("start", r.get("start_date", "")))[:10]; end = str(r.get("end", r.get("end_date", "")))[:10]; return start, end


def cmd_check():
    c = _client()
    try: ds = c.metadata.list_datasets(); print(f"key accepted. datasets visible: {len(ds)}; {DATASET} {'is' if DATASET in ds else 'is NOT'} among them")
    except Exception as e: print(f"list_datasets failed: {type(e).__name__}: {e}"); return
    try: s, e = _range(c); print(f"{DATASET} covers {s} -> {e}")
    except Exception as e: print(f"get_dataset_range failed: {type(e).__name__}: {e}")
    try: print(f"schemas: {c.metadata.list_schemas(dataset=DATASET)}")
    except Exception as e: print(f"list_schemas failed: {type(e).__name__}: {e}")
    d = needed_days(); print(f"days the test needs: {len(d)} ({d[0]} -> {d[-1]})" if d else "no needed days found on disk")


def _cost(c, start, end):
    return float(c.metadata.get_cost(dataset=DATASET, symbols=list(SYMBOLS.values()), stype_in="continuous", schema=SCHEMA, start=str(start), end=str(end)))


def cmd_cost():
    c = _client(); s, e = _range(c); days = [d for d in needed_days() if str(d) >= s and str(d) < e]
    try: full = _cost(c, s, e); print(f"whole history {s} -> {e}, {len(SYMBOLS)} instruments, 1-minute bars: US${full:.2f}")
    except Exception as ex: print(f"cost request failed: {type(ex).__name__}: {ex}"); return
    sample = days[:: max(1, len(days) // 12)][:12]; per = []
    for d in sample:
        try: per.append(_cost(c, d, pd.Timestamp(d) + pd.Timedelta(days=1)))
        except Exception as ex: print(f"  {d}: {type(ex).__name__}: {str(ex)[:100]}")
    if per:
        est = sum(per) / len(per) * len(days); print(f"only the {len(days)} needed days: about US${est:.2f} (from {len(per)} sample days at US${sum(per) / len(per):.4f} each)")
        print(f"days needed before the dataset starts ({s}): {len([d for d in needed_days() if str(d) < s])} -- those cannot be tested with this source")
    print("Nothing was downloaded. Compare with the free credit shown on the Databento account page, then choose: `fetch` (needed days) or `fetch --full`.")


def cmd_fetch(max_usd: float, full: bool):
    c = _client(); s, e = _range(c)
    if full:
        price = _cost(c, s, e)
        if price > max_usd: raise SystemExit(f"quoted US${price:.2f} is above the cap US${max_usd:.2f} -- nothing downloaded")
        for y in range(int(s[:4]), int(e[:4]) + 1):
            a, b = max(s, f"{y}-01-01"), min(e, f"{y + 1}-01-01")
            if a >= b: continue
            for name, sym in SYMBOLS.items():
                out = OUT / name / f"{y}.parquet"
                if out.exists(): continue
                out.parent.mkdir(parents=True, exist_ok=True); df = c.timeseries.get_range(dataset=DATASET, symbols=[sym], stype_in="continuous", schema=SCHEMA, start=a, end=b).to_df(); df.to_parquet(out); print(f"  {name} {y}: {len(df):,} bars")
        print(f"done; quoted price US${price:.2f}"); return
    days = [d for d in needed_days() if str(d) >= s and str(d) < e]; todo = [d for d in days if not all((OUT / n / f"{d}.parquet").exists() for n in SYMBOLS)]
    sample = todo[:: max(1, len(todo) // 8)][:8]; est = (sum(_cost(c, d, pd.Timestamp(d) + pd.Timedelta(days=1)) for d in sample) / max(len(sample), 1)) * len(todo)
    print(f"{len(todo)} of {len(days)} days to download; estimated US${est:.2f}; cap US${max_usd:.2f}")
    if est > max_usd: raise SystemExit("estimate above the cap -- nothing downloaded")
    for k, d in enumerate(todo):
        df = c.timeseries.get_range(dataset=DATASET, symbols=list(SYMBOLS.values()), stype_in="continuous", schema=SCHEMA, start=str(d), end=str(pd.Timestamp(d) + pd.Timedelta(days=1))).to_df()
        for name, sym in SYMBOLS.items():
            out = OUT / name / f"{d}.parquet"; out.parent.mkdir(parents=True, exist_ok=True); sub = df[df["symbol"] == sym] if "symbol" in df.columns else df
            if not out.exists(): sub.to_parquet(out)
        if (k + 1) % 50 == 0: print(f"  {k + 1}/{len(todo)} days")
    print(f"done -> {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["check", "cost", "fetch"]); ap.add_argument("--max-usd", type=float, default=20.0); ap.add_argument("--full", action="store_true"); a = ap.parse_args()
    {"check": cmd_check, "cost": cmd_cost, "fetch": lambda: cmd_fetch(a.max_usd, a.full)}[a.cmd]()
