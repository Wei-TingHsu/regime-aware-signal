"""news_events.py -- N1 stage 1 (docs/prereg_news_events.md): the event days, their GDELT daily records, the digests and the measured cost.
Stage 2 (the LLM cause read, the release composition read, the tables and the learner) follows once the cost is on record.

  python -m src.news_events events                  # every session with |close-to-close| >= 4% in SOX (^SOX), QQQ or S&P 500 (SPY / ^GSPC); counts by index,
                                                    #   sign, year; -> processed/news_events.csv
  python -m src.news_events fetch [--limit N]       # GDELT 1.0 daily events file for each event day (data.gdeltproject.org, 1979 ->) and, from 2015-02-19, the
                                                    #   day's GKG files; write-once under data_provenance/gdelt_days/; prints bytes fetched
  python -m src.news_events digest                  # per event day: a compact text digest (top-50 events by mentions with actors, CAMEO code, tone, source slug;
                                                    #   theme counts where the GKG exists) -> data_provenance/gdelt_days/digest/YYYYMMDD.txt
  python -m src.news_events cost                    # tokens and US$ of reading every digest, counted on disk
Primary sources only (standing rule, 6 Nov): GDELT raw files, the project's own corpus, agency releases. Nothing here calls the LLM.
"""
from __future__ import annotations

import argparse
import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
GD = Path("data_provenance/gdelt_days"); RAW, DIG = GD / "raw", GD / "digest"
THRESH = 0.04
INDEX_CANDIDATES = {"SOX": ["^SOX", "SOX", "SOXX"], "QQQ": ["QQQ", "^NDX"], "SPX": ["^GSPC", "SPY", "SPX"]}
EVENTS_URL = "http://data.gdeltproject.org/events/{d}.export.CSV.zip"               # GDELT 1.0 daily, 2013-04-01 -> ; earlier years are monthly/yearly files
EVENTS_URL_OLD = "http://data.gdeltproject.org/events/{ym}.zip"                     # 2006-2013-03: one file per month (YYYYMM); before 2006 one per year (YYYY)
GKG_INDEX = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
UA = {"User-Agent": "regime-aware-signal research (news-attributed large moves, prereg_news_events.md)"}
IN_RATE, OUT_RATE, OUT_TOK, SYSTEM_TOK = 2.0, 10.0, 350, 600
CAMEO_TOP = {"01": "public statement", "02": "appeal", "03": "intent to cooperate", "04": "consult", "05": "diplomatic cooperation", "06": "material cooperation", "07": "aid", "08": "yield",
             "09": "investigate", "10": "demand", "11": "disapprove", "12": "reject", "13": "threaten", "14": "protest", "15": "force posture", "16": "reduce relations", "17": "coerce", "18": "assault", "19": "fight", "20": "mass violence"}


def _returns() -> pd.DataFrame:
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if getattr(r.index, "tz", None) is not None: r.index = r.index.tz_localize(None)
    return r.sort_index()


def cmd_events():
    r = _returns(); rows = []; used = {}
    for name, cands in INDEX_CANDIDATES.items():
        col = next((c for c in cands if c in r.columns), None)
        if col is None: print(f"  {name}: none of {cands} in asset_returns -- skipped (add ^SOX to the panel for the semiconductor index)"); continue
        used[name] = col; s = r[col].dropna(); simple = np.expm1(s)
        big = simple[simple.abs() >= THRESH]
        for d, v in big.items(): rows.append(dict(date=d.date(), index=name, column=col, move=float(v), sign=int(np.sign(v)), year=d.year))
    ev = pd.DataFrame(rows).sort_values(["date", "index"]); ev.to_csv(PROC / "news_events.csv", index=False)
    days = ev["date"].nunique(); print(f"columns used: {used}"); print(f"{len(ev)} index-events on {days} distinct sessions (|move| >= {THRESH:.0%})")
    print(ev.groupby(["index", "sign"]).size().unstack(fill_value=0).to_string()); print(ev.groupby("year").date.nunique().to_string())
    L = ["# N1 — event days (|close-to-close| ≥ 4%)", "", f"Columns used: {used}. {len(ev)} index-events on {days} sessions.", "", "| year | sessions | SOX | QQQ | SPX |", "|---|---|---|---|---|"]
    for y, g in ev.groupby("year"): L.append(f"| {y} | {g.date.nunique()} | {(g['index'] == 'SOX').sum()} | {(g['index'] == 'QQQ').sum()} | {(g['index'] == 'SPX').sum()} |")
    (DOCS / "news_events_days.md").write_text("\n".join(L) + "\n"); print("-> processed/news_events.csv, docs/news_events_days.md")


def _get(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as resp: return resp.read()
    except Exception as e:
        print(f"    {url.rsplit('/', 1)[-1]}: {type(e).__name__}: {str(e)[:80]}"); return None


def cmd_fetch(limit: int | None):
    ev = pd.read_csv(PROC / "news_events.csv", parse_dates=["date"]); days = sorted(ev["date"].dt.date.unique()); RAW.mkdir(parents=True, exist_ok=True)
    if limit: days = days[-limit:]
    total = 0; n_new = 0
    for d in days:
        ds = pd.Timestamp(d); tag = ds.strftime("%Y%m%d")
        if ds >= pd.Timestamp("2013-04-01"):
            target = RAW / f"{tag}.export.CSV.zip"
            if target.exists(): continue
            b = _get(EVENTS_URL.format(d=tag))
        elif ds >= pd.Timestamp("2006-01-01"):
            target = RAW / f"{ds.strftime('%Y%m')}.zip"
            if target.exists(): continue
            b = _get(EVENTS_URL_OLD.format(ym=ds.strftime("%Y%m")))
        else:
            target = RAW / f"{ds.year}.zip"
            if target.exists(): continue
            b = _get(EVENTS_URL_OLD.format(ym=str(ds.year)))
        if b:
            target.write_bytes(b); total += len(b); n_new += 1
    print(f"fetched {n_new} file(s), {total / 1e6:.1f} MB; GDELT 1.0 events files are the daily (2013-04 ->), monthly (2006-13) and yearly (<2006) archives. "
          f"The pre-2013 archives are large (yearly files run to hundreds of MB) -- fetch them deliberately with --limit widened once the daily set is in.")


def _events_for_day(ds: pd.Timestamp) -> pd.DataFrame | None:
    tag = ds.strftime("%Y%m%d")
    p = RAW / f"{tag}.export.CSV.zip" if ds >= pd.Timestamp("2013-04-01") else RAW / (f"{ds.strftime('%Y%m')}.zip" if ds >= pd.Timestamp("2006-01-01") else f"{ds.year}.zip")
    if not p.exists(): return None
    with zipfile.ZipFile(p) as z:
        name = z.namelist()[0]
        df = pd.read_csv(io.BytesIO(z.read(name)), sep="\t", header=None, low_memory=False, dtype=str)
    # GDELT 1.0 export columns: 0 GLOBALEVENTID, 1 SQLDATE, 5 Actor1Code, 6 Actor1Name, 15 Actor2Name, 26 EventCode, 28 EventRootCode, 30 GoldsteinScale, 31 NumMentions, 34 AvgTone, 57 SOURCEURL (58 cols) -- 1.0 files before 2013 have 57 columns without SOURCEURL
    df = df[df[1] == tag] if len(df.columns) >= 58 else df[df[1] == tag]
    cols = {6: "a1", 15: "a2", 26: "code", 28: "root", 30: "gold", 31: "mentions", 34: "tone"}
    if len(df.columns) >= 58: cols[57] = "url"
    out = df[list(cols)].rename(columns=cols)
    for c in ("gold", "mentions", "tone"): out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def cmd_digest():
    ev = pd.read_csv(PROC / "news_events.csv", parse_dates=["date"]); DIG.mkdir(parents=True, exist_ok=True); n_ok = 0
    for d, g in ev.groupby(ev["date"].dt.date):
        ds = pd.Timestamp(d); out = DIG / f"{ds:%Y%m%d}.txt"
        if out.exists(): n_ok += 1; continue
        df = _events_for_day(ds)
        if df is None or df.empty: continue
        moves = "; ".join(f"{r_['index']} {r_['move']:+.1%}" for _, r_ in g.iterrows())
        top = df.sort_values("mentions", ascending=False).head(50)
        roots = df.groupby("root")["mentions"].sum().sort_values(ascending=False).head(8)
        L = [f"DATE {ds:%Y-%m-%d}. MARKET MOVES THAT SESSION: {moves}.", f"GDELT 1.0 events that day: {len(df):,} records; mean tone {df['tone'].mean():+.2f}; mean Goldstein {df['gold'].mean():+.2f}.",
             "Event root codes by mentions: " + ", ".join(f"{CAMEO_TOP.get(str(k).zfill(2), k)} {int(v):,}" for k, v in roots.items()), "", "TOP 50 EVENTS BY MENTIONS (actor1 | actor2 | type | tone | source):"]
        for _, r_ in top.iterrows():
            slug = str(r_.get("url", "") or "").rsplit("/", 1)[-1][:90].replace("-", " ")
            L.append(f"- {r_['a1'] or '?'} | {r_['a2'] or '?'} | {CAMEO_TOP.get(str(r_['root']).zfill(2), r_['root'])} ({r_['code']}) | tone {r_['tone']:+.1f} | {slug}")
        out.write_text("\n".join(L) + "\n"); n_ok += 1
    print(f"digests on disk: {n_ok} of {ev['date'].nunique()} event days -> {DIG}")


def cmd_cost():
    files = sorted(DIG.glob("*.txt")); words = sum(len(p.read_text().split()) for p in files); tok = words * 1.6 + SYSTEM_TOK * len(files)
    usd = tok / 1e6 * IN_RATE + len(files) * OUT_TOK / 1e6 * OUT_RATE
    print(f"{len(files)} digests, {words:,} words -> ~{tok:,.0f} input tokens; about US${usd:.2f} for the cause read at {IN_RATE}/{OUT_RATE} $/M. Counted on disk. "
          f"Release reads (S2) are priced separately once the release texts are fetched.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["events", "fetch", "digest", "cost"]); ap.add_argument("--limit", type=int); a = ap.parse_args()
    DOCS.mkdir(exist_ok=True)
    {"events": cmd_events, "fetch": lambda: cmd_fetch(a.limit), "digest": cmd_digest, "cost": cmd_cost}[a.cmd]()
