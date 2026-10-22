"""
Input latency audit (TRACK 3.27). At run time: for every series the engine reads, the last session it holds vs the last completed
NYSE session, in sessions; plus the timestamp of Yahoo's live quote for the display instruments. Appends to processed/latency_log.csv,
writes docs/latency_audit.md. Criterion (prereg in TRACK 3.27): a series that is >= 2 sessions behind on >= 20% of runs over 20 runs is
flagged STALE; every live rule that reads it must state the lag on the app, and the backfill alignment for that series is re-checked.

  python -m src.latency_audit
"""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PROC, DOCS = Path("processed"), Path("docs")
LOG = PROC / "latency_log.csv"
FILES = {"asset_returns.parquet": ["SPY", "TLT", "GLD", "UUP", "USO"], "wti_cont.parquet": ["WTI_SPOT", "WTI_FUT", "USO"]}
RAW = {"raw/yfinance": ["SPY", "TLT", "GLD", "UUP", "USO", "CL=F"], "raw/fred": None}   # the caches the nightly --force refresh writes; no forward-fill here
LIVE = ["SPY", "GLD", "USO", "TLT", "UUP", "^TNX", "DX-Y.NYB", "CL=F", "SI=F"]


def last_completed():
    try:
        from src.market_calendar import last_completed_session
        return pd.Timestamp(last_completed_session()).normalize()
    except Exception:
        return (pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(hours=21)).normalize()


def sessions_between(a: pd.Timestamp, b: pd.Timestamp) -> int:
    """NYSE sessions strictly after a up to b (business days; holidays count as a day of lag, stated)."""
    if pd.isna(a) or a >= b: return 0
    return len(pd.bdate_range(a, b)) - 1


def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M"); lc = last_completed(); rows = []
    for f, cols in FILES.items():
        p = PROC / f
        if not p.exists(): rows.append(dict(run=now, file=f, series="(missing)", last="", lag=np.nan)); continue
        df = pd.read_parquet(p); df.index = pd.to_datetime(df.index)
        for c in (cols or list(df.columns)):
            if c not in df.columns: continue
            ld = df[c].last_valid_index()
            rows.append(dict(run=now, file=f, series=c, last=("" if ld is None else ld.strftime("%Y-%m-%d")), lag=(np.nan if ld is None else sessions_between(ld, lc))))
    for d, keys in RAW.items():
        dp = Path(d)
        if not dp.exists(): rows.append(dict(run=now, file=d, series="(missing)", last="", lag=np.nan)); continue
        for fp in sorted(dp.glob("*.parquet")):
            k = fp.stem
            if keys and k not in keys: continue
            try:
                df = pd.read_parquet(fp); df.index = pd.to_datetime(df.index); ld = df.dropna(how="all").index.max()
                rows.append(dict(run=now, file=d, series=k, last=ld.strftime("%Y-%m-%d"), lag=sessions_between(ld.normalize(), lc)))
            except Exception as e:
                rows.append(dict(run=now, file=d, series=k, last=f"error {type(e).__name__}", lag=np.nan))
    try:
        import yfinance as yf
        for t in LIVE:
            try:
                h = yf.Ticker(t).history(period="5d", interval="1d")
                ld = pd.to_datetime(h.index[-1]).tz_localize(None).normalize() if len(h) else None
                rows.append(dict(run=now, file="yahoo-live", series=t, last=("" if ld is None else ld.strftime("%Y-%m-%d")), lag=(np.nan if ld is None else sessions_between(ld, lc))))
            except Exception as e:
                rows.append(dict(run=now, file="yahoo-live", series=t, last=f"error {type(e).__name__}", lag=np.nan))
    except ImportError:
        pass
    new = pd.DataFrame(rows)
    old = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(columns=new.columns)
    allr = pd.concat([old, new], ignore_index=True); allr.to_csv(LOG, index=False)
    # summary over the last 20 runs
    runs = sorted(allr.run.unique())[-20:]; rec = allr[allr.run.isin(runs)]
    L = [f"# Input latency audit", "", f"*{now}. Last completed NYSE session: {lc.date()}. Lag = sessions the series is behind it at run time. "
         f"Flag rule (TRACK 3.27): ≥ 2 sessions behind on ≥ 20% of the last 20 runs → STALE. Runs on record: {len(runs)}.*", "",
         "| file | series | last date this run | lag now | runs seen | share ≥ 2 behind | flag |", "|---|---|---|---|---|---|---|"]
    for (f, s_), g in rec.groupby(["file", "series"], sort=False):
        cur = g.iloc[-1]; share = float((g.lag >= 2).mean()) if g.lag.notna().any() else np.nan
        flag = "STALE" if (len(g) >= 5 and share >= 0.2) else ("watch" if (isinstance(cur.lag, float) and cur.lag >= 2) else "")
        L.append(f"| {f} | {s_} | {cur['last']} | {'' if pd.isna(cur.lag) else int(cur.lag)} | {len(g)} | {'' if pd.isna(share) else f'{share:.0%}'} | {flag} |")
    L += ["", "Reading: raw/fred and raw/yfinance are what the nightly --force refresh actually received (no forward-fill). A lag of 1 on FRED series is their publication schedule, declared where it matters (the oil leg's "
          "provisional flag). A lag of 1 on the price panel at the nightly run time means the download missed the latest close — the fault seen on "
          "16 and 21 Oct 2026. Backtests are unaffected by latency only where the backfill used the same as-of alignment; that is checked per flagged series."]
    (DOCS / "latency_audit.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> docs/latency_audit.md, {LOG}")


if __name__ == "__main__":
    run()
