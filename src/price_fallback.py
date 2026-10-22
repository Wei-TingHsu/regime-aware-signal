"""
Latest-session price fallback (TRACK 3.27 finding, 22 Oct): Yahoo's daily history lags one session at the nightly hour (03:00 ET).
If processed/asset_returns.parquet lacks the last completed session for the five model assets, pull Stooq's daily CSV (free, no key) and fill
that session's log return from Stooq's own two closes. Marked provisional in processed/price_provisional.csv; the next Yahoo rebuild overwrites it.
Known difference: Stooq closes are unadjusted, so on an ex-dividend day the provisional return omits the dividend (fixed next day by Yahoo).

  python -m src.price_fallback
"""
from __future__ import annotations
import io, sys, urllib.request
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PROC = Path("processed"); PANEL = PROC / "asset_returns.parquet"; LOG = PROC / "price_provisional.csv"
STOOQ = {"SPY": "spy.us", "TLT": "tlt.us", "GLD": "gld.us", "UUP": "uup.us", "USO": "uso.us"}


UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) regime-aware-signal academic research"}


def _yahoo(a):
    """Yahoo's short-window request (period=10d): the audit showed it current when the long-history request lags a session. Adjusted closes."""
    import yfinance as yf
    h = yf.Ticker(a).history(period="10d", interval="1d", auto_adjust=True)
    if h.empty: return None, None
    c = h["Close"]; c.index = pd.to_datetime(c.index).tz_localize(None).normalize(); return c.dropna(), "yahoo-10d"


def _stooq(a):
    """Stooq daily CSV (unadjusted closes); needs a browser-style header."""
    req = urllib.request.Request(f"https://stooq.com/q/d/l/?s={STOOQ[a]}&i=d", headers=UA)
    csv = urllib.request.urlopen(req, timeout=30).read().decode()
    d = pd.read_csv(io.StringIO(csv), parse_dates=["Date"]).set_index("Date")["Close"].dropna(); return d, "stooq"


def run():
    from src.market_calendar import last_completed_session
    lc = pd.Timestamp(last_completed_session()).normalize(); now = datetime.now().strftime("%Y-%m-%d %H:%M")
    r = pd.read_parquet(PANEL); name = r.index.name or "date"; r.index = pd.to_datetime(r.index)
    if lc not in r.index:
        r.loc[lc] = np.nan; r = r.sort_index()
    need = [a for a in STOOQ if a in r.columns and pd.isna(r.loc[lc, a])]
    if not need: print(f"  panel has {lc.date()} for all model assets -- nothing to fill"); return
    filled = []
    for a in need:
        d, src = None, None
        for fn in (_yahoo, _stooq):
            try:
                d, src = fn(a)
                if d is not None and lc in d.index: break
            except Exception as e:
                print(f"  {a}: {fn.__name__[1:]} failed ({type(e).__name__})"); d = None
        if d is None or lc not in d.index: print(f"  {a}: no source has {lc.date()} yet -- left NaN"); continue
        i = d.index.get_loc(lc); prev = d.index[i - 1]; ret = float(np.log(d.iloc[i] / d.iloc[i - 1]))
        r.loc[lc, a] = ret; filled.append(dict(date=lc.strftime("%Y-%m-%d"), asset=a, ret=ret, prev=prev.strftime("%Y-%m-%d"), source=src, filled_at=now))
    if filled:
        r.index.name = name; r.to_parquet(PANEL)
        f = pd.DataFrame(filled); f.to_csv(LOG, mode="a", header=not LOG.exists(), index=False)
        print(f"  filled {lc.date()} from Stooq for {', '.join(x['asset'] for x in filled)} (provisional; {LOG})")
    else:
        print("  nothing filled")


if __name__ == "__main__":
    run()
