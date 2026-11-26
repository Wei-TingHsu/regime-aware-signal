"""reversal_check.py -- a look at ONE day: what did the engine record around a market turn, and at which minute did each market turn? A description, not a test.

Founder, 26 Nov 2026: after the hawkish PCE release of 25 Nov, stocks, gold and bonds all bounced back at about 11:00 New York time. Did the engine see news that supports it?

    python -m src.reversal_check engine --day 2026-11-25                 # free, reads only what the engine already wrote on this laptop
    python -m src.reversal_check prices --day 2026-11-25 --max-usd 1     # Databento (key needed): 1-minute futures prices 08:00-13:00 New York for the S&P 500, Nasdaq-100, gold and the 10-year Treasury note

Nothing is changed by `engine`. `prices` writes one file into data_provenance/intraday/ (ignored by git; licensed data is not uploaded).
"""
from __future__ import annotations
import argparse, json, warnings
from pathlib import Path
import pandas as pd

NY = "America/New_York"; LIVE = Path("data_provenance/live/events.jsonl")
FOLDERS = [("release reads (PCE, GDP, jobs ...)", Path("data_provenance/doc_reads_prints")), ("official documents (White House, Fed, Treasury ...)", Path("data_provenance/doc_reads")), ("company documents read live", Path("data_provenance/ai_earnings/reads"))]
# 26 Nov 2026: the MOST-TRADED contract of each (x.v.0), not the nearest-expiry one (x.c.0) -- the first version asked for the nearest gold contract, which hardly trades, and got no prices.
# The same lesson was already written in src/intraday_fetch.py (cmd_volume); Claude did not apply it here.
SYMS = {"S&P 500 futures": "ES.v.0", "Nasdaq-100 futures": "NQ.v.0", "gold futures": "GC.v.0", "10-year Treasury note futures (price up = yield down)": "ZN.v.0"}


def _short(v, n=260):
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v; s = " ".join(s.split()); return s if len(s) <= n else s[:n] + " ..."


def cmd_engine(day: str, t0: str, t1: str):
    d = pd.Timestamp(day); a = pd.Timestamp(f"{day} {t0}", tz=NY); b = pd.Timestamp(f"{day} {t1}", tz=NY); tag = d.strftime("%Y%m%d")
    print(f"WHAT THE ENGINE RECORDED on {day}, {t0} to {t1} New York time. Nothing is changed by this command.\n")
    # 1. the live listener
    rows = []
    if LIVE.exists():
        for line in LIVE.read_text().splitlines():
            try: e = json.loads(line)
            except Exception: continue
            pub = pd.to_datetime(e.get("published"), utc=True, errors="coerce"); seen = pd.to_datetime(e.get("seen"), utc=True, errors="coerce"); when = pub if pd.notna(pub) else seen
            if pd.isna(when) or not (a <= when.tz_convert(NY) <= b): continue
            rows.append((when.tz_convert(NY), seen.tz_convert(NY) if pd.notna(seen) else None, e))
    rows.sort(key=lambda r: r[0]); print(f"1. The live listener (company news and filings): {len(rows)} items published in the window" + ("" if LIVE.exists() else " -- the file data_provenance/live/events.jsonl is missing"))
    for when, seen, e in rows:
        rd = e.get("read") or {}; near = " <-- within 30 minutes of 11:00" if abs((when - pd.Timestamp(f"{day} 11:00", tz=NY)).total_seconds()) <= 1800 else ""
        print(f"   {when:%H:%M} published" + (f", seen {seen:%H:%M}" if seen is not None else "") + f" | {e.get('ticker', '')} | {e.get('source', '')} | {_short(e.get('title', ''), 110)}{near}")
        if rd: print(f"        the engine's reading: type '{rd.get('event_type', '')}', material {rd.get('material', '')}, own stock {rd.get('own_stock', '')}, market {rd.get('market', '')} | {_short(rd.get('evidence', ''), 170)}")
    # 1b. market-wide headlines (collected since 26 Nov 2026)
    mw = Path("data_provenance/live/market_wire.jsonl"); M = []
    if mw.exists():
        for line in mw.read_text().splitlines():
            try: e = json.loads(line)
            except Exception: continue
            when = pd.to_datetime(e.get("published"), utc=True, errors="coerce")
            if pd.notna(when) and a <= when.tz_convert(NY) <= b: M.append((when.tz_convert(NY), e))
    M.sort(key=lambda r: r[0]); print(f"\n1b. Market-wide headlines (Fed, Treasury auctions, White House, Federal Register ...): {len(M)} items in the window" + ("" if mw.exists() else " -- not collected yet"))
    for when, e in M: print(f"   {when:%H:%M} | {e.get('source', '')} | {_short(e.get('title', ''), 150)}" + (" <-- within 30 minutes of 11:00" if abs((when - pd.Timestamp(f"{day} 11:00", tz=NY)).total_seconds()) <= 1800 else ""))
    # 2. the stored reads of that day
    for name, folder in FOLDERS:
        fs = sorted(f for f in folder.glob("*.json") if tag in f.name) if folder.exists() else []
        print(f"\n2. {name}: {len(fs)} files of {day}" + ("" if folder.exists() else f" -- folder {folder} not found"))
        for f in fs:
            try: J = json.loads(f.read_text())
            except Exception as ex: print(f"   {f.name}: cannot be read ({type(ex).__name__})"); continue
            print(f"   {f.name}")
            items = J.items() if isinstance(J, dict) else enumerate(J if isinstance(J, list) else [J])
            for k, v in items:
                if str(k).startswith("_") or v in (None, "", [], {}): continue
                print(f"        {k}: {_short(v)}")
    # 3. the ledgers
    for f in [Path("processed/event_time_ledger.csv"), Path("processed/report_ledger.csv"), Path("processed/forward_ledger.csv")]:
        if not f.exists(): continue
        try: T = pd.read_csv(f, dtype=str)
        except Exception: continue
        M = T[T.apply(lambda r: any(day in str(x) for x in r), axis=1)]
        print(f"\n3. {f}: {len(M)} rows that mention {day}")
        for _, r in M.head(12).iterrows(): print("   " + _short({k: v for k, v in r.items() if isinstance(v, str) and v}, 420))
    f = Path("processed/why_moved.json")
    if f.exists():
        try: print(f"\n4. processed/why_moved.json (what the page says moved the markets): {_short(json.loads(f.read_text()), 1500)}")
        except Exception: pass
    print("\nPaste all of this to Claude.")


def cmd_prices(day: str, max_usd: float):
    from src.intraday_fetch import _client
    out = Path("data_provenance/intraday") / f"reversal_{day}_v.parquet"; a = pd.Timestamp(f"{day} 08:00", tz=NY); b = pd.Timestamp(f"{day} 13:00", tz=NY)
    if out.exists(): df = pd.read_parquet(out); print(f"prices already on disk ({out}); nothing downloaded, nothing charged")
    else:
        c = _client(); r = c.metadata.get_dataset_range(dataset="GLBX.MDP3"); end = pd.Timestamp(str(r.get("end", r.get("end_date", "")))).tz_convert("UTC") if pd.Timestamp(str(r.get("end", r.get("end_date", "")))).tzinfo else pd.Timestamp(str(r.get("end", r.get("end_date", ""))), tz="UTC")
        if end < b.tz_convert("UTC"): raise SystemExit(f"Databento does not have this day yet: its futures data ends {end.tz_convert(NY):%Y-%m-%d %H:%M} New York. Nothing downloaded. Try again later today.")
        kw = dict(dataset="GLBX.MDP3", symbols=list(SYMS.values()), stype_in="continuous", schema="ohlcv-1m", start=a.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M"), end=b.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M"))
        usd = float(c.metadata.get_cost(**kw)); print(f"Databento quotes US${usd:.2f} for 5 hours of 1-minute prices of 4 futures; limit US${max_usd:.2f}")
        if usd > max_usd: raise SystemExit("quoted price above the limit -- nothing downloaded")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore"); df = c.timeseries.get_range(**kw).to_df()
        out.parent.mkdir(parents=True, exist_ok=True); df.to_parquet(out)
    ix = pd.to_datetime(df.index, utc=True).tz_convert(NY); df = df.assign(t=ix); rel = pd.Timestamp(f"{day} 08:30", tz=NY); marks = ["09:30", "09:45", "10:00", "10:30", "10:45", "11:00", "11:10", "11:20", "11:30", "12:00", "12:59"]
    print(f"\nAT WHICH MINUTE DID EACH MARKET TURN on {day}? Moves are measured from the price at 08:29, one minute before the PCE and GDP release (New York time).")
    print("  market | lowest price 08:30-12:59: minute, move from 08:29 | highest price 08:30-12:59: minute, move | inside 10:30-12:00 only: minute of the low, minute of the high | " + " | ".join(marks))
    lows = {}; turns = {}
    for name, sym in SYMS.items():
        g = df[df["symbol"] == sym] if "symbol" in df.columns else df; g = g.set_index("t").sort_index()
        if not len(g): print(f"  {name}: no prices"); continue
        base = float(g.close[g.index < rel].iloc[-1]) if (g.index < rel).any() else float(g.close.iloc[0]); post = g[g.index >= rel]; lo_t = post.low.idxmin(); lo = float(post.low.min()); lows[name] = lo_t
        at = lambda hm: (float(g.close[g.index <= pd.Timestamp(f"{day} {hm}", tz=NY)].iloc[-1]) / base - 1) * 100
        mid = post[(post.index >= pd.Timestamp(f"{day} 10:30", tz=NY)) & (post.index <= pd.Timestamp(f"{day} 12:00", tz=NY))]; hi_all = post.high.idxmax(); turns[name] = (mid.low.idxmin(), mid.high.idxmax()) if len(mid) else (None, None)
        print(f"  {name} | {lo_t:%H:%M}, {(lo / base - 1) * 100:+.2f}% | {hi_all:%H:%M}, {(float(post.high.max()) / base - 1) * 100:+.2f}% | " + (f"low {turns[name][0]:%H:%M}, high {turns[name][1]:%H:%M}" if len(mid) else "no prices") + " | " + " | ".join(f"{at(m):+.2f}%" for m in marks))
    if len(lows) > 1:
        ts = sorted(lows.values()); print(f"\nThe lows of the whole morning fall between {ts[0]:%H:%M} and {ts[-1]:%H:%M}: " + ("within 15 minutes of each other." if (ts[-1] - ts[0]).total_seconds() <= 900 else "more than 15 minutes apart -- the markets did NOT make their low at the same minute."))
        print("Read the 10:30-12:00 column for the turn seen at about 11:00: a market that turned UP there has its low near 11:00; one that turned DOWN there has its high near 11:00.")
    print("Paste all of this to Claude.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["engine", "prices"]); ap.add_argument("--day", required=True); ap.add_argument("--from", dest="t0", default="07:00"); ap.add_argument("--to", dest="t1", default="13:00"); ap.add_argument("--max-usd", type=float, default=1.0); a = ap.parse_args()
    cmd_engine(a.day, a.t0, a.t1) if a.cmd == "engine" else cmd_prices(a.day, a.max_usd)
