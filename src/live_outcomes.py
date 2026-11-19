"""live_outcomes.py -- step 1 of the agenda (17 Nov): the FORWARD record. Joins minute prices to what the live listener saw and scored
(data_provenance/live/events.jsonl) and writes, for each candidate rule, what the trade would have earned. Rules and cells are FIXED here before any
live outcome exists (TRACK 3.64); nothing is searched.

    rule   what                                                                                           where it came from
    FA-1   Fed statement: Nasdaq future in the direction of the score, 1 min after the release, 60 min     v3e E1(c)
    FA-2   Fed day: gold's own move from the release to 15:15 continues to the next day's 09:30            v3e-3 (d), near miss
    FA-3   results: own stock in the direction of the MARKET score, 5 min after, hold 30 min               ai-chain F2 best cell, near miss
    FA-4   results, STEP RULE: own stock in the direction of the own-stock score, only when the score is    sizing test S (TRACK 3.68), registered 18 Nov
           0.7 or more in size; 1 min after, hold 60 min
    QC-3   results stamped 16:00-16:40: Nasdaq future in the direction of 'results against prior           ai-chain F1 best cell, near miss
           guidance', 5 min after, to the next 09:35
    CV-1   customer view (not a registered rule): own stock in the direction of the own-stock score, entered 1 min after the SCORE WAS READY on
           this machine, hold 60 min -- what a user of the product could actually have done

Clocks. Backtests used the release time (Fed) or the SEC stamp (results). Live, "the release" = the time the first source states, or, when it states
none, the time this machine first saw the item. CV-1 always uses the time the score was ready.

    python -m src.live_outcomes plan                 # which days and symbols are needed, and Databento's quoted price. Downloads nothing.
    python -m src.live_outcomes fetch --max-usd 2    # downloads those minute bars (ignored folder; not uploaded)
    python -m src.live_outcomes ledger               # -> docs/live_outcomes.md, data_provenance/live/outcomes.csv
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from src.ai_chain_test import Book, _ny, ret, COST

LIVE = Path("data_provenance/live"); LOG = LIVE / "events.jsonl"; PX = Path("data_provenance/intraday/live"); DOCS = Path("docs")
FUT = {"NQ": "NQ.c.0", "ES": "ES.c.0", "GC": "GC.v.0"}      # the same contracts as the backtest's final data (gold by volume)
RULES = {"FA-1": "Fed statement score -> Nasdaq future, 1 min after the release, hold 60 min", "FA-2": "Fed day: gold's move from the release to 15:15 -> held to the next 09:30",
         "FA-3": "results: market score -> own stock, 5 min after, hold 30 min", "FA-4": "results, step rule: own-stock score of 0.7 or more in size -> own stock, 1 min after, hold 60 min", "QC-3": "results after the close: results against prior guidance -> Nasdaq future, 5 min after, to the next 09:35",
         "CV-1": "customer view: own-stock score -> own stock, 1 min after the score was ready, hold 60 min"}


def events() -> pd.DataFrame:
    if not LOG.exists(): raise SystemExit(f"{LOG} does not exist yet -- the listener has logged nothing")
    rows = [json.loads(x) for x in LOG.read_text().splitlines() if x.strip()]; rows = [r for r in rows if r.get("kind") in ("results", "fed") and not r.get("drill") and isinstance(r.get("read"), dict) and not r.get("empty")]
    rows = [r for r in rows if not (r["kind"] == "results" and (r["read"].get("facts") or {}).get("revenue") in (None, "", "null") and not any(r["read"].get(k) for k in ("own_stock", "market", "results_vs_prior_guidance")))]      # an empty read is not a score
    keep = {}
    for r in rows: keep[(r["ticker"], r["kind"], str(r.get("seen_ny", ""))[:10])] = r      # one row per release: the last valid read (a later 'rescored' row replaces a live one)
    E = pd.DataFrame(list(keep.values()))
    if E.empty: return E
    for c in ("published", "seen"): E[c] = pd.to_datetime(E[c], utc=True, errors="coerce", format="ISO8601").dt.tz_convert("America/New_York").dt.tz_localize(None)
    E["release"] = E["published"].fillna(E["seen"]); E["release"] = E[["release", "seen"]].min(axis=1)      # a source that states a time later than we saw it is not believed over our own clock
    E["scored"] = E["seen"] + pd.to_timedelta(pd.to_numeric(E["score_s"], errors="coerce").fillna(0) if "score_s" in E.columns else 0, unit="s"); E["date"] = E["release"].dt.normalize()
    return E.sort_values("seen").reset_index(drop=True)


def _min(t) -> int: return int(t.hour * 60 + t.minute + (1 if (t.second or t.microsecond) else 0))      # the first whole minute at or after t


def needs(E: pd.DataFrame) -> list:
    """(key, dataset, symbol, stype, first day, last day exclusive): the event day and the next trading day (five calendar days cover a weekend)"""
    out = {}
    for r in E.itertuples():
        a, b = str(r.date.date()), str((r.date + pd.Timedelta(days=5)).date()); syms = ["NQ", "ES"] + (["GC"] if r.kind == "fed" else [r.ticker])
        for s in syms: out[(s, a)] = (f"{s}_{a}", "GLBX.MDP3" if s in FUT else "XNAS.ITCH", FUT.get(s, s), "continuous" if s in FUT else "raw_symbol", a, b)
    return list(out.values())


def _ready(c, todo):
    """keep only the files whose event day AND next trading day the vendor already holds; the request never runs past what is available"""
    ends = {}; out = []
    for key, ds, sym, stype, a, b in todo:
        if ds not in ends:
            try: r = c.metadata.get_dataset_range(dataset=ds); ends[ds] = pd.Timestamp(str(r["end"] if isinstance(r, dict) else r)).tz_convert("UTC") if pd.Timestamp(str(r["end"] if isinstance(r, dict) else r)).tzinfo else pd.Timestamp(str(r["end"] if isinstance(r, dict) else r)).tz_localize("UTC")
            except Exception as e: print(f"  {ds}: could not ask what is available ({type(e).__name__}); trying as is"); ends[ds] = None
        end = ends[ds]; need = (pd.Timestamp(a) + pd.tseries.offsets.BDay(1) + pd.Timedelta(hours=22)).tz_localize("UTC")      # through the next trading day's close and after-hours
        if end is not None and end < need: print(f"  {key}: not ready -- the vendor has {ds} up to {end:%Y-%m-%d %H:%M} UTC; the day after the event is needed. Try again in a day."); continue
        out.append((key, ds, sym, stype, a, b if end is None or pd.Timestamp(b).tz_localize("UTC") <= end else end.strftime("%Y-%m-%dT%H:%M:%S")))
    return out


def cmd_plan():
    from src.intraday_fetch import _client
    E = events()
    if E.empty: print("no scored results release or Fed statement in the live log yet -- nothing to price"); return
    N = needs(E); todo = [n for n in N if not (PX / f"{n[0]}.parquet").exists()]; c = _client(); total = 0.0; todo = _ready(c, todo)
    for key, ds, sym, stype, a, b in todo:
        try: usd = float(c.metadata.get_cost(dataset=ds, symbols=[sym], stype_in=stype, schema="ohlcv-1m", start=a, end=b))
        except Exception as e: print(f"  {key}: quote failed: {type(e).__name__}: {str(e)[:90]}"); continue
        total += usd; print(f"  {key}: {ds} {sym} {a} -> {b}: US${usd:.4f}")
    print(f"{len(E)} live events; {len(N)} price files needed, {len(todo)} ready to download; quoted US${total:.2f}. Nothing was downloaded.")


def cmd_fetch(max_usd: float):
    from src.intraday_fetch import _client
    import warnings
    E = events()
    if E.empty: print("nothing to price yet"); return
    todo = [n for n in needs(E) if not (PX / f"{n[0]}.parquet").exists()]; c = _client(); PX.mkdir(parents=True, exist_ok=True); spent = 0.0; todo = _ready(c, todo)
    for key, ds, sym, stype, a, b in todo:
        try:
            usd = float(c.metadata.get_cost(dataset=ds, symbols=[sym], stype_in=stype, schema="ohlcv-1m", start=a, end=b))
            if spent + usd > max_usd: print(f"  cap US${max_usd:.2f} reached before {key}; rerun with a higher --max-usd"); break
            with warnings.catch_warnings():
                warnings.simplefilter("ignore"); df = c.timeseries.get_range(dataset=ds, symbols=[sym], stype_in=stype, schema="ohlcv-1m", start=a, end=b).to_df()
            if len(df): df.to_parquet(PX / f"{key}.parquet"); spent += usd; print(f"  {key}: {len(df):,} bars (US${usd:.4f})")
            else: print(f"  {key}: no bars returned (the vendor publishes a day's data some hours later -- try again tomorrow)")
        except Exception as e: print(f"  {key}: {type(e).__name__}: {str(e)[:110]}")
    print(f"done; about US${spent:.2f} -> {PX} (ignored folder; not uploaded)")


def book() -> Book:
    B = Book(); parts = {}
    for p in sorted(PX.glob("*.parquet")): parts.setdefault(p.stem.split("_")[0], []).append(_ny(pd.read_parquet(p)))
    for s, L in parts.items(): B.add(s, pd.concat(L, ignore_index=True).sort_values(["date", "minute"]).drop_duplicates(["date", "minute"]))
    return B


def _trade(B, sym, date, m, x, last):
    return ret(B, sym, (date, m), x, last) if date in B.d.get(sym, {}) else np.nan


def cmd_ledger():
    E = events(); B = book(); rows = []
    def add(r, rule, sym, score, m, x, last, note=""):
        s = np.sign(float(score)) if score is not None and pd.notna(pd.to_numeric(score, errors="coerce")) else 0.0
        if s == 0: rows.append(dict(date=str(r.date.date()), who=r.ticker, rule=rule, direction="no position (score 0)", entry="", gross_bp=np.nan, note=note)); return
        g = _trade(B, sym, r.date, m, x, last); rows.append(dict(date=str(r.date.date()), who=r.ticker, rule=rule, direction="buy" if s > 0 else "sell", entry=f"{m // 60:02d}:{m % 60:02d}", gross_bp=round(s * g, 1) if np.isfinite(g) else np.nan, note=(note + ("" if np.isfinite(g) else "; no price yet")).lstrip("; ")))
    for r in (E.itertuples() if len(E) else []):
        d = r.read; rel, sc = _min(r.release), _min(r.scored)
        if r.kind == "fed":
            add(r, "FA-1", "NQ", d.get("implication_equities"), rel + 1, 60, 1019, note=f"score ready {max(0, round((r.scored - r.release).total_seconds()))} s after the release")
            p0, p1 = B.p("GC", r.date, rel + 1), B.p("GC", r.date, 915); mv = np.sign(p1 - p0) if np.isfinite(p0) and np.isfinite(p1) else 0.0
            if rel < 900:      # exit at 09:30 on the next trading day, as registered
                nx = B.day("GC", r.date, strictly_after=True); q0, q1 = B.p("GC", r.date, 915), (B.p("GC", nx, 570, 15) if nx is not None else np.nan); g = np.log(q1 / q0) * 1e4 if np.isfinite(q0) and np.isfinite(q1) and q0 > 0 else np.nan
                rows.append(dict(date=str(r.date.date()), who=r.ticker, rule="FA-2", direction="no position (gold flat)" if mv == 0 else ("buy" if mv > 0 else "sell"), entry="15:15" if mv != 0 else "", gross_bp=round(mv * g, 1) if np.isfinite(g) and mv != 0 else np.nan, note="direction = gold's own move from the release to 15:15" + ("" if np.isfinite(g) or mv == 0 else "; no price yet")))
        else:
            add(r, "FA-3", r.ticker, d.get("market"), rel + 5, 30, 1199)
            own = pd.to_numeric(d.get("own_stock"), errors="coerce"); add(r, "FA-4", r.ticker, own if pd.notna(own) and abs(own) >= 0.7 else 0, rel + 1, 60, 1199, note="" if pd.notna(own) and abs(own) >= 0.7 else f"own-stock score {own} is under 0.7")
            if 960 <= rel <= 1000: add(r, "QC-3", "NQ", d.get("results_vs_prior_guidance"), rel + 5, "open", 1019)
            if getattr(r, "rescored", False) is True: rows.append(dict(date=str(r.date.date()), who=r.ticker, rule="CV-1", direction="not counted", entry="", gross_bp=np.nan, note="the live read failed; the score was made after the fact, so no user could have acted on it")); continue
            add(r, "CV-1", r.ticker, d.get("own_stock"), sc + 1, 60, 1199, note=f"seen {max(0, round((r.seen - r.release).total_seconds()))} s after the source's time; score ready {round((r.scored - r.seen).total_seconds())} s later")
    T = pd.DataFrame(rows); L = ["# Live outcomes: the forward record of the candidate rules", "", "Each row is one live event seen and scored by `src/news_listener.py`, priced afterwards. The rules and their cells were fixed before any row existed (TRACK 3.64). Returns in bp (1 bp = 0.01%) in the direction of the trade, before cost. None of these is yet a confirmed signal.", ""]
    if T.empty: L.append("No scored results release or Fed statement has been logged yet."); print("no live events to score yet")
    else:
        LIVE.mkdir(parents=True, exist_ok=True); T.to_csv(LIVE / "outcomes.csv", index=False); L += ["## Running totals", "", "| rule | what | trades with a price | average, before cost | assumed cost | right on | backtest said |", "|---|---|---|---|---|---|---|"]
        back = {"FA-1": "+30.0 bp, 74% of 101", "FA-2": "+40.3 bp, 67% of 132", "FA-3": "+41.4 bp, 58% of 330", "FA-4": "+141.5 bp per trade on 140 trades, 2020-2026, thresholds fitted on earlier years", "QC-3": "+16.7 bp, 61% of 294", "CV-1": "no backtest at this clock (own-stock score from the SEC stamp + 1 min: +64.9 bp, 58% of 365)"}
        for k, what in RULES.items():
            v = T[(T.rule == k)]["gross_bp"].dropna(); c = COST["future"] if k in ("FA-1", "FA-2", "QC-3") else COST["stock"]
            L.append(f"| {k} | {what} | {len(v)} | {v.mean():+.1f} bp | {c:.0f} bp | {(v > 0).mean():.0%} | {back[k]} |" if len(v) else f"| {k} | {what} | 0 | | {c:.0f} bp | | {back[k]} |"); print(f"  {k}: {len(v)} trades" + (f", average {v.mean():+.1f} bp, right on {(v > 0).mean():.0%}" if len(v) else ""))
        L += ["", "A verdict needs at least 30 trades per rule; before that the totals are only a record.", "", "## Every event", "", "| date (New York) | who | rule | direction | entry | result, before cost | note |", "|---|---|---|---|---|---|---|"]
        L += [f"| {r.date} | {r.who} | {r.rule} | {r.direction} | {r.entry} | {'' if pd.isna(r.gross_bp) else f'{r.gross_bp:+.1f} bp'} | {r.note} |" for r in T.itertuples()]
    DOCS.mkdir(exist_ok=True); (DOCS / "live_outcomes.md").write_text("\n".join(L) + "\n"); print("-> docs/live_outcomes.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "fetch", "ledger"]); ap.add_argument("--max-usd", type=float, default=2.0); a = ap.parse_args()
    {"plan": cmd_plan, "fetch": lambda: cmd_fetch(a.max_usd), "ledger": cmd_ledger}[a.cmd]()
