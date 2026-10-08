"""
S5 -- collect 1-minute bars every night, forward only. (TRACK §3.9 S5, feeds T14 phase D and T2)

Yahoo serves 1-minute bars for the last 7 calendar days and nothing older, so the only free
intraday history is the one we save ourselves, starting now. Every run writes one parquet per
ticker per session under data_provenance/intraday/<ticker>/<YYYYMMDD>.parquet and never
rewrites an existing day. Roughly 0.5 MB a day for all tickers; untracked; in the backup list.

Tickers: the five display instruments, the five model ETFs, and the front-month fed funds
future (the live surprise proxy for phase B).

Usage
  python -m src.collect_intraday            # save any missing sessions from the last 7 days
  python -m src.collect_intraday --status   # what is on disk
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path("data_provenance/intraday")
TICKERS = ["^GSPC", "^TNX", "GC=F", "DX-Y.NYB", "CL=F",          # shown
           "SPY", "TLT", "GLD", "UUP", "USO",                     # modelled
           "ZQ=F",                                                # fed funds front month (phase B surprise)
           "SR3=F"]                                               # 3-month SOFR front quarterly -- the contract the Fed's surprise series uses since 2023


def fetch_1m(tk: str) -> pd.DataFrame:
    import yfinance as yf
    d = yf.Ticker(tk).history(period="7d", interval="1m", auto_adjust=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    keep = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in d.columns]
    d = d[keep].dropna(subset=["Close"])
    if d.empty:
        return d
    idx = pd.DatetimeIndex(d.index)
    d.index = idx.tz_convert("America/New_York") if idx.tz is not None else idx.tz_localize("UTC").tz_convert("America/New_York")
    return d


def save_missing(tk: str) -> tuple[int, int]:
    out = ROOT / tk.replace("^", "").replace("=", "_").replace(".", "_")
    out.mkdir(parents=True, exist_ok=True)
    try:
        d = fetch_1m(tk)
    except Exception as e:
        print(f"  {tk:9} fetch failed: {type(e).__name__}: {e}"); return 0, 0
    if d.empty:
        return 0, 0
    written = skipped = 0
    today = datetime.now().astimezone().date()
    for day, g in d.groupby(d.index.date):
        if day >= today:                      # a session still in progress is never written
            continue
        f = out / f"{day:%Y%m%d}.parquet"
        if f.exists():
            skipped += 1; continue
        g.to_parquet(f); written += 1
    return written, skipped


def status():
    if not ROOT.exists():
        print("nothing collected yet"); return
    for p in sorted(ROOT.iterdir()):
        days = sorted(x.stem for x in p.glob("*.parquet"))
        if days:
            print(f"  {p.name:10} {len(days):4d} sessions  {days[0]} -> {days[-1]}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--status", action="store_true"); a = ap.parse_args()
    if a.status:
        status(); return
    tw = ts = 0
    for tk in TICKERS:
        w, s = save_missing(tk); tw += w; ts += s
        if w:
            print(f"  {tk:9} +{w} session(s)")
    print(f"intraday collector: {tw} new session file(s) written, {ts} already on disk")


if __name__ == "__main__":
    main()
