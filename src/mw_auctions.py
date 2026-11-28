"""mw_auctions.py -- test MW-1 for the first kind of market-wide headline: Treasury auction results (TRACK 3.125, 3.143).

On 25 Nov 2026 the one timed official event near the turn was a Treasury auction result. Auctions have a past with a clock time, so this kind can be tested now
instead of waiting for the live collection: after an auction of Treasury notes or bonds closes, do the four futures (S&P 500, Nasdaq-100, gold, 10-year note)
move MORE in the next 5, 15, 30 and 60 minutes than at the same clock minutes of the 20 sessions before?

    export DATABENTO_API_KEY=...            # typed by the founder in the terminal; never written to a file
    python -m src.mw_auctions plan          # the Databento quote for the futures history and what is on disk; nothing downloaded
    python -m src.mw_auctions fetch --max-usd 15   # 1-minute prices of the four futures, month by month, May 2018 to now; safe to stop and run again
    python -m src.mw_auctions auctions      # the Treasury's own list of past auctions (free)
    python -m src.mw_auctions run           # the test (free)

Futures prices go to data_provenance/intraday/fut/ (ignored by git: licensed data). The auction list is the US Treasury's (public) -> data_provenance/market_wire/auctions.csv.
"""
from __future__ import annotations
import argparse, json, time, warnings
from pathlib import Path
import numpy as np, pandas as pd

NY = "America/New_York"; FUT = Path("data_provenance/intraday/fut"); MW = Path("data_provenance/market_wire"); DOCS = Path("docs"); DS = "GLBX.MDP3"; START = "2018-05-01"
ROOTS = {"S&P 500 futures": "ES", "Nasdaq-100 futures": "NQ", "gold futures": "GC", "10-year Treasury note futures": "ZN"}; HS = [5, 15, 30, 60]; BEFORE = 20; M0, M1 = 8 * 60, 16 * 60 + 30      # minutes of the day kept: 08:00 to 16:30 New York


def _months(end):
    return [(f"{p.start_time:%Y-%m-%d}", f"{min(p.end_time + pd.Timedelta(days=1), end):%Y-%m-%d}", f"{p}") for p in pd.period_range(START, end, freq="M") if p.start_time < end]


def _range_end(c):
    r = c.metadata.get_dataset_range(dataset=DS); e = pd.Timestamp(str(r.get("end", r.get("end_date", "")))); return (e.tz_convert("UTC") if e.tzinfo else e.tz_localize("UTC")).tz_localize(None).normalize()


def cmd_plan():
    from src.intraday_fetch import _client
    c = _client(); end = _range_end(c); jobs = [(root, a, b, m) for root in ROOTS.values() for a, b, m in _months(end)]; todo = [j for j in jobs if not (FUT / j[0] / f"{j[3]}.parquet").exists()]; total = 0.0
    for root in ROOTS.values():
        tj = [j for j in todo if j[0] == root]
        if not tj: continue
        try: total += float(c.metadata.get_cost(dataset=DS, symbols=[f"{root}.v.0"], stype_in="continuous", schema="ohlcv-1m", start=min(j[1] for j in tj), end=max(j[2] for j in tj)))
        except Exception as ex: print(f"  {root}: no quote ({type(ex).__name__}: {str(ex)[:80]})")
    print(f"{DS}, 1-minute bars of the most-traded contract of ES, NQ, GC, ZN, {START} to {end:%Y-%m-%d}: {len(jobs)} month-files, {len(jobs) - len(todo)} on disk, {len(todo)} to download.")
    print(f"QUOTED PRICE FOR EVERYTHING STILL MISSING: about US${total:.2f}. Nothing was downloaded.")


def cmd_fetch(max_usd):
    from src.intraday_fetch import _client
    c = _client(); end = _range_end(c); jobs = [(root, a, b, m) for root in ROOTS.values() for a, b, m in _months(end)]; last = f"{pd.Period(end, freq='M')}"
    todo = [j for j in jobs if not (FUT / j[0] / f"{j[3]}.parquet").exists() or j[3] == last]; spent = 0.0; n = 0; rows = 0; bad = []; t0 = time.time()      # the newest month is always asked again (it grows)
    print(f"{len(todo)} month-files to download (of {len(jobs)}); limit US${max_usd:.2f}. Safe to stop with Ctrl+C and run again.")
    for k, (root, a, b, m) in enumerate(todo):
        kw = dict(dataset=DS, symbols=[f"{root}.v.0"], stype_in="continuous", schema="ohlcv-1m", start=a, end=b); ok = False; why = ""
        for attempt in range(4):
            try:
                usd = float(c.metadata.get_cost(**kw))
                if spent + usd > max_usd: print(f"  the limit of US${max_usd:.2f} is reached after {n} files (about US${spent:.2f}). Run again with a higher --max-usd to continue."); print(f"DONE (stopped at the limit): {n} files, {rows:,} bars, about US${spent:.2f}."); return
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore"); df = c.timeseries.get_range(**kw).to_df()
                (FUT / root).mkdir(parents=True, exist_ok=True); tmp = FUT / root / f"{m}.tmp"; df[["close"]].to_parquet(tmp); tmp.replace(FUT / root / f"{m}.parquet"); spent += usd; n += 1; rows += len(df); ok = True; break
            except KeyboardInterrupt: raise
            except Exception as ex: why = f"{type(ex).__name__}: {str(ex)[:90]}"; time.sleep(15 * (attempt + 1))
        if not ok:
            bad.append(f"{root} {m}"); print(f"  {root} {m}: failed 4 times ({why}); the next run tries it again")
            if len(bad) >= 6 and n == 0: print("  stopped: 6 failures and nothing downloaded -- the key or the connection."); break
        if n in (3, 12) or (ok and n and n % 50 == 0): per = (time.time() - t0) / max(k + 1, 1); print(f"  {n} files, {rows:,} bars, about US${spent:.2f} so far; measured {per:.0f} seconds a file -> about {(len(todo) - k - 1) * per / 60:.0f} minutes left")
    print(f"DONE: {n} files downloaded now, {rows:,} bars, about US${spent:.2f} charged, {(time.time() - t0) / 60:.0f} minutes; failed: {', '.join(bad) or 'none'}. -> {FUT} (ignored folder; not uploaded)")


def _pick(d, *names):
    low = {k.lower().replace("_", ""): k for k in d}
    for n in names:
        for k, orig in low.items():
            if n in k: return d.get(orig)
    return None


def cmd_auctions():
    """the Treasury's list of past auctions of notes and bonds: date, term, closing time, high yield, bid-to-cover. Three public addresses are tried; the longest history is used."""
    from src import news_listener as N
    today = pd.Timestamp.now().strftime("%Y-%m-%d"); rows = []; used = ""
    tries = [("TreasuryDirect search", [f"https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type={t}&startDate={START}&endDate={today}&dateFieldName=auctionDate" for t in ("Note", "Bond")]),
             ("TreasuryDirect auctioned", [f"https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type={t}&days=3300" for t in ("Note", "Bond")]),
             ("Fiscal Data, in pages", "PAGED")]
    FD = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?format=json&sort=-{f}&filter={f}:gte:" + START + "{extra}&page%5Bsize%5D=200&page%5Bnumber%5D={n}"
    def paged():      # 28 Nov 2026: one answer of 10,000 auctions was cut off at the reader's limit of 4 MB (the fault of 27 Nov); now 200 auctions a page, with a pause between pages
        last = None
        for f, extra in (("auction_date", ",security_type:in:(Note,Bond)"), ("auction_date", ""), ("record_date", ",security_type:in:(Note,Bond)"), ("record_date", "")):
            got = []
            try:
                for n in range(1, 120):
                    J = json.loads(N.fetch(FD.format(f=f, extra=extra, n=n), timeout=90)); d = J.get("data", [])
                    got += d
                    if n == 1: print(f"    Fiscal Data, dated by '{f}'{' (notes and bonds only)' if extra else ' (every kind)'}: page 1 has {len(d)} records; pages in all: {(J.get('meta') or {}).get('total-pages', '?')}; fields: {', '.join(list(d[0])[:8]) + ' ...' if d else 'none'}")
                    if len(d) < 200: break
                    time.sleep(0.4)
                if got: return got
            except Exception as ex: last = ex; print(f"    Fiscal Data, dated by '{f}'{' (notes and bonds only)' if extra else ''}: no ({type(ex).__name__}: {str(ex)[:60]})")
        if last: raise last
        return []
    for name, urls in tries:
        got = []
        try:
            if urls == "PAGED": got = paged()
            else:
                for u in urls:
                    J = json.loads(N.fetch(u, timeout=90)); got += J.get("data", []) if isinstance(J, dict) else J
        except Exception as ex: print(f"  {name}: no ({type(ex).__name__}: {str(ex)[:70]})"); continue
        out = []
        for a in got:
            typ = str(_pick(a, "securitytype") or ""); d = pd.to_datetime(str(a.get("auction_date") or a.get("auctionDate") or _pick(a, "auctiondate") or a.get("record_date") or "")[:10], errors="coerce"); y = a.get("high_yield") or a.get("highYield") or _pick(a, "highyield"); btc = _pick(a, "bidtocover"); ct = str(_pick(a, "closingtimecomp") or "")
            if pd.isna(d) or typ not in ("Note", "Bond") or y in (None, "", "null") or d < pd.Timestamp(START): continue
            tt = pd.to_datetime(ct, errors="coerce"); hm = (tt.hour, tt.minute) if pd.notna(tt) and tt.hour >= 8 else (13, 0)
            out.append(dict(day=d, type=typ, term=str(_pick(a, "securityterm") or ""), close_h=hm[0], close_m=hm[1], closing_time_given=bool(pd.notna(tt) and tt.hour >= 8), high_yield=pd.to_numeric(y, errors="coerce"), bid_to_cover=pd.to_numeric(btc, errors="coerce"), cusip=str(_pick(a, "cusip") or "")))
        print(f"  {name}: {len(got)} records, {len(out)} auctions of notes and bonds since {START}")
        if len(out) > len(rows): rows, used = out, name      # the address with the longest history is used
    if len(rows) < 100: print("=> no address gave a usable auction history (under 100 auctions). Tell Claude what the lines above say."); return
    A = pd.DataFrame(rows).drop_duplicates(["day", "cusip"]).sort_values("day"); MW.mkdir(parents=True, exist_ok=True); A.to_csv(MW / "auctions.csv", index=False)
    print(f"{len(A)} auctions of notes and bonds, {A.day.min():%Y-%m-%d} to {A.day.max():%Y-%m-%d} (source: {used}); closing time given for {int(A.closing_time_given.sum())}, otherwise 13:00 assumed; by closing time: " + ", ".join(f"{h:02d}:{m:02d} x{n}" for (h, m), n in A.groupby(["close_h", "close_m"]).size().items()) + f" -> {MW / 'auctions.csv'}")


def _grid(root):
    """price at each minute 08:00-16:30 New York of each day; a missing minute takes the last price, at most 5 minutes old. -> (days, array)"""
    fr = [pd.read_parquet(f) for f in sorted((FUT / root).glob("*.parquet"))]
    if not fr: return None, None
    s = pd.concat(fr).close; s = s[~s.index.duplicated(keep="last")]; ix = pd.to_datetime(s.index, utc=True).tz_convert(NY); m = ix.hour * 60 + ix.minute; ok = (m >= M0) & (m < M1); d = pd.DatetimeIndex(ix[ok].date); days = pd.DatetimeIndex(sorted(set(d)))
    G = np.full((len(days), M1 - M0), np.nan); G[days.get_indexer(d), m[ok] - M0] = s.to_numpy(float)[ok]; G = pd.DataFrame(G).T.ffill(limit=5).T.to_numpy(); full = np.isfinite(G).sum(axis=1) >= 300; return days[full], G[full]


def cmd_run(ndraw=20000):
    if not (MW / "auctions.csv").exists(): print("run `python -m src.mw_auctions auctions` first"); return
    A = pd.read_csv(MW / "auctions.csv", parse_dates=["day"]); A["m"] = A.close_h * 60 + A.close_m - M0; ev = A.drop_duplicates(["day", "m"]).copy(); rng = np.random.default_rng(20261127); rows = []; note = []
    clock = set(zip(ev.day, ev.m)); f2 = lambda x: "n/a" if x != x else f"{x * 1e4:.1f}"
    for name, root in ROOTS.items():
        days, G = _grid(root)
        if days is None: note.append(f"{name}: no prices on disk"); continue
        pos = {d: i for i, d in enumerate(days)}
        for H in HS:
            e_abs = []; o_abs = []; ranks = []
            for d, m in zip(ev.day, ev.m):
                i = pos.get(d)
                if i is None or m < 0 or m + H >= G.shape[1]: continue
                r = G[i, m + H] / G[i, m] - 1
                if not np.isfinite(r): continue
                prev = [j for j in range(i - 1, -1, -1) if (days[j], m) not in clock][:BEFORE]      # the 20 sessions before that had no auction closing at this minute
                pr = np.array([G[j, m + H] / G[j, m] - 1 for j in prev]); pr = pr[np.isfinite(pr)]
                if len(pr) < 15: continue
                e_abs.append(abs(r)); o_abs.append(np.abs(pr).mean()); ranks.append((np.sum(np.abs(pr) < abs(r)) + 0.5 * np.sum(np.abs(pr) == abs(r))) / len(pr))
            n = len(ranks)
            if n < 30: rows.append(dict(market=name, H=H, n=n, event=np.nan, ordinary=np.nan, times=np.nan, rank=np.nan, chance=np.nan, verdict="too few")); continue
            mr = float(np.mean(ranks)); sim = rng.integers(0, BEFORE + 1, size=(ndraw, n)).mean(axis=1) / BEFORE; p = float((np.sum(sim >= mr) + 1) / (ndraw + 1))
            rows.append(dict(market=name, H=H, n=n, event=float(np.mean(e_abs)), ordinary=float(np.mean(o_abs)), times=float(np.mean(e_abs) / np.mean(o_abs)), rank=mr, chance=p, verdict=""))
    if not rows: print("no futures prices on disk: run `python -m src.mw_auctions fetch` first"); return
    R = pd.DataFrame(rows); live = R[R.verdict != "too few"]; bar = 0.05 / max(len(live), 1); R.loc[R.verdict == "", "verdict"] = np.where(R.loc[R.verdict == "", "chance"] < bar, "PASSES", "no")
    L = ["# Test MW-1, first kind: Treasury auction results", "", f"Registered in TRACK 3.125 and 3.143 before running. {len(ev)} auction closings of Treasury notes and bonds since {START} (the US Treasury's own list). "
         f"For each: the size of the move (up or down) of each future over the H minutes from the auction's closing minute, against the size of its move over the same clock minutes on the {BEFORE} sessions before that had no auction closing then. "
         "'Times' = the average size after an auction divided by the average ordinary size. 'Place' = where the auction day stands among those sessions on average (0.5 = like any other day, 1 = always the largest). "
         f"'Chance' = how often {ndraw:,} draws of ordinary days give a place at least as high. **PASSES** = chance under {bar:.4f} (0.05 / {len(live)} tests).", "",
         "| future | minutes after the close of the auction | auctions | average move after an auction, basis points | on ordinary days at that minute | times | place | chance | verdict |", "|---|---|---|---|---|---|---|---|---|"]
    print(f"{len(ev)} auction closings since {START}; a test passes under {bar:.4f}")
    print("  times the ordinary move (after an auction / ordinary, basis points) | place | chance | verdict | minutes | future")
    for r in R.itertuples():
        L.append(f"| {r.market} | {r.H} | {r.n} | {f2(r.event)} | {f2(r.ordinary)} | {'n/a' if r.times != r.times else f'{r.times:.2f}'} | {'n/a' if r.rank != r.rank else f'{r.rank:.3f}'} | {'n/a' if r.chance != r.chance else f'{r.chance:.4f}'} | {'**PASSES**' if r.verdict == 'PASSES' else r.verdict} |")
        print(f"    {'n/a' if r.times != r.times else f'{r.times:.2f}'}x ({f2(r.event)} / {f2(r.ordinary)}) | {'n/a' if r.rank != r.rank else f'{r.rank:.3f}'} | {'n/a' if r.chance != r.chance else f'{r.chance:.4f}'} | {r.verdict} | {r.H} | {r.market}")
    L += ["", "What a pass means and does not mean: an auction result moves that market more than an ordinary minute does -- it says the kind of headline matters, not which way the market goes. Direction needs the result compared with what the market expected (the yield traded just before the auction), which is not in this list.",
          "Sources: US Treasury (auction list, public); Databento GLBX.MDP3 1-minute futures prices (licensed, not uploaded)."] + ([""] + note if note else [])
    DOCS.mkdir(exist_ok=True); (DOCS / "mw_auctions.md").write_text("\n".join(L) + "\n"); print(f"=> {int((R.verdict == 'PASSES').sum())} of {len(live)} tests pass. -> docs/mw_auctions.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "fetch", "auctions", "run"]); ap.add_argument("--max-usd", type=float, default=15.0); a = ap.parse_args()
    {"plan": cmd_plan, "fetch": lambda: cmd_fetch(a.max_usd), "auctions": cmd_auctions, "run": cmd_run}[a.cmd]()
