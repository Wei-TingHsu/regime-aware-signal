"""spread_measure.py -- measure the REAL spread of the stocks and of their single-stock funds at the times the sell-off rules trade, to replace the two
assumed numbers (2 basis points per order for shares, 10 for funds) that the 'cheapest way' comparison of TRACK 3.106 rests on. Registered in TRACK 3.112.

What is measured. For every fund trade of the fund check (docs/selloff_funds_audit.csv: a sell-off day, its stock, its inverse fund) -- the days the
rules would actually trade -- the best bid and best ask on Nasdaq for the STOCK and for the FUND:
    at the entry: 1 and 5 minutes after the open (09:31, 09:35 New York) of the session after the sell-off;
    at the exit:  5 and 1 minutes before the close (15:55, 15:59) two sessions after the sell-off.
The cost of one order = HALF the gap between ask and bid, as a share of the price, in basis points.
Limit to know: this is Nasdaq's own order book. The best price across ALL US exchanges is equal or better, so the measured spread is an upper limit.

    python -m src.spread_measure plan                 # free: asks Databento what the download would cost; downloads nothing
    python -m src.spread_measure fetch --max-usd 5    # downloads the quotes, stops at the limit -> data_provenance/intraday/spreads (not uploaded)
    python -m src.spread_measure report               # no download -> docs/spread_measure.md
Needs DATABENTO_API_KEY set in the window (typed by the founder; never in the chat).
"""
from __future__ import annotations
import argparse, warnings
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path("data_provenance/intraday/spreads"); DOCS = Path("docs"); AUDIT = DOCS / "selloff_funds_audit.csv"; DS = "XNAS.ITCH"
MOMENTS = {"entry, 1 minute after the open": ("in", "09:31"), "entry, 5 minutes after the open": ("in", "09:35"), "exit, 5 minutes before the close": ("out", "15:55"), "exit, 1 minute before the close": ("out", "15:59")}


def _windows() -> list:
    """one 10-minute window per security and session: 09:30-09:40 on the entry day, 15:50-16:00 on the exit day"""
    from src.selloff_study import _px
    A = pd.read_csv(AUDIT, parse_dates=["day"]); idx = _px()["SPY"].index; W = {}
    for r in A.itertuples():
        if r.day not in idx: continue
        i = idx.get_loc(r.day)
        if i + 2 >= len(idx): continue
        for sym, kind in ((r.stock, "stock"), (r.fund, "2x fund" if abs(r.mult) >= 1.5 else "1x fund")):
            for part, d, a, b in (("in", idx[i + 1], "09:30", "09:40"), ("out", idx[i + 2], "15:50", "16:00")):
                k = f"{sym}_{d:%Y%m%d}_{part}"; z = lambda hm: pd.Timestamp(f"{d:%Y-%m-%d} {hm}").tz_localize("America/New_York").tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%S")
                W[k] = dict(key=k, sym=sym, kind=kind, date=d, part=part, start=z(a), end=z(b), event=f"{r.day:%Y-%m-%d}", stock=r.stock)
    return list(W.values())


def _schema(c):
    have = [str(x) for x in c.metadata.list_schemas(dataset=DS)]; return next((x for x in ("bbo-1m", "bbo-1s", "tbbo", "mbp-1") if x in have), None), have


def cmd_plan(sample: int):
    from src.intraday_fetch import _client
    c = _client(); sch, have = _schema(c); print(f"Nasdaq quote data offered: {', '.join(have)}; using: {sch}")
    if sch is None: print("no quote data is offered for this data set -- tell Claude"); return
    W = _windows(); todo = [w for w in W if not (OUT / f"{w['key']}.parquet").exists()]; pick = todo[:: max(1, len(todo) // sample)][:sample]; usd = 0.0; bad = 0
    for w in pick:
        try: usd += float(c.metadata.get_cost(dataset=DS, symbols=[w["sym"]], stype_in="raw_symbol", schema=sch, start=w["start"], end=w["end"]))
        except Exception as e:
            bad += 1
            if bad <= 3: print(f"  {w['key']}: {type(e).__name__}: {str(e)[:90]}")
    ok = len(pick) - bad; est = usd / max(1, ok) * len(todo); kinds = pd.Series([w["kind"] for w in W]).value_counts().to_dict()
    print(f"{len(W)} windows of 10 minutes ({kinds}); {len(todo)} still to download. Asked the price of {ok} of them: US${usd:.4f} -> about US${est:.2f} for all" + (f" ({bad} could not be priced)" if bad else "") + ". Nothing was downloaded, nothing was charged.")


def cmd_fetch(max_usd: float):
    from src.intraday_fetch import _client
    c = _client(); sch, _ = _schema(c); W = _windows(); OUT.mkdir(parents=True, exist_ok=True); spent = 0.0; n = 0; bad = 0; empty = 0
    for w in W:
        f = OUT / f"{w['key']}.parquet"
        if f.exists(): continue
        try:
            usd = float(c.metadata.get_cost(dataset=DS, symbols=[w["sym"]], stype_in="raw_symbol", schema=sch, start=w["start"], end=w["end"]))
            if spent + usd > max_usd: print(f"  limit of US${max_usd:.2f} reached after {n} windows; run again with a higher limit to continue"); break
            with warnings.catch_warnings():
                warnings.simplefilter("ignore"); df = c.timeseries.get_range(dataset=DS, symbols=[w["sym"]], stype_in="raw_symbol", schema=sch, start=w["start"], end=w["end"]).to_df()
            empty += int(len(df) == 0); df.to_parquet(f); spent += usd; n += 1
            if n % 200 == 0: print(f"  {n} windows, about US${spent:.2f}")
        except Exception as e:
            bad += 1
            if bad <= 5: print(f"  {w['key']}: {type(e).__name__}: {str(e)[:90]}")
            if bad >= 25 and n == 0: print("  stopped: 25 failures and nothing downloaded -- the key or the connection; tell Claude what the lines above say"); break
    print(f"{n} windows downloaded now ({empty} of them empty), {bad} failed; about US${spent:.2f} charged -> {OUT} (ignored folder; not uploaded)")


def _half_spread_bp(df, when_utc):
    ix = pd.to_datetime(df.index, utc=True); d = df[(ix <= when_utc) & (df["bid_px_00"] > 0) & (df["ask_px_00"] > df["bid_px_00"])]
    if not len(d) or (when_utc - pd.to_datetime(d.index[-1], utc=True)).total_seconds() > 300: return np.nan      # no valid quote in the 5 minutes before the moment
    b, a = float(d["bid_px_00"].iloc[-1]), float(d["ask_px_00"].iloc[-1]); return (a - b) / 2 / ((a + b) / 2) * 1e4


def cmd_report():
    from src import real_cost as RC
    W = _windows(); rows = []
    for w in W:
        f = OUT / f"{w['key']}.parquet"
        if not f.exists(): continue
        df = pd.read_parquet(f)
        if not len(df) or "bid_px_00" not in df.columns: rows += [dict(kind=w["kind"], sym=w["sym"], moment=m, bp=np.nan, date=w["date"]) for m, (p, _) in MOMENTS.items() if p == w["part"]]; continue
        for m, (p, hm) in MOMENTS.items():
            if p == w["part"]: rows.append(dict(kind=w["kind"], sym=w["sym"], moment=m, bp=_half_spread_bp(df, pd.Timestamp(f"{w['date']:%Y-%m-%d} {hm}").tz_localize("America/New_York").tz_convert("UTC")), date=w["date"]))
    R = pd.DataFrame(rows)
    if not len(R): print("no quotes on disk: run `python -m src.spread_measure fetch --max-usd 5` first"); return
    L = ["# The real spread at the times the sell-off rules trade", "", f"Registered in TRACK 3.112. Nasdaq's best bid and ask (Databento, {DS}) for each stock and its inverse fund on the entry and exit sessions of {R.date.nunique()} sessions since {R.date.min():%b %Y}. "
         "**Cost of one order = half the gap between ask and bid, in basis points of the price.** Nasdaq's own book only: the best price across all exchanges is equal or better, so these numbers are an upper limit. "
         f"The tests so far ASSUMED {RC.SPREAD_BP['stock']:.0f} basis points per order for shares and {RC.SPREAD_BP['etf']:.0f} for funds.", "", "| what is traded | moment | middle value, bp per order | average | 9 in 10 are under | measured | no valid quote |", "|---|---|---|---|---|---|---|"]; S = {}
    for kind in ("stock", "1x fund", "2x fund"):
        for m in MOMENTS:
            x = R[(R.kind == kind) & (R.moment == m)].bp; v = x.dropna()
            if not len(x): continue
            S[(kind, m)] = float(v.median()) if len(v) else np.nan; L.append(f"| {kind} | {m} | {v.median():.1f} | {v.mean():.1f} | {v.quantile(0.9):.1f} | {len(v)} | {int(x.isna().sum())} |" if len(v) else f"| {kind} | {m} | n/a | n/a | n/a | 0 | {int(x.isna().sum())} |")
    # the cheapest way again, with the measured spreads: entry at 09:31, exit at 15:59; fees 1 bp; a short held two sessions about 2.6 bp
    def way(kind, mult): a, b = S.get((kind, "entry, 1 minute after the open"), np.nan), S.get((kind, "exit, 1 minute before the close"), np.nan); return (a + b) / mult
    st = way("stock", 1) + 1.0 + 2.6; f1 = way("1x fund", 1) + 1.5; f2 = way("2x fund", 2) + 1.0
    L += ["", "## The cheapest way for the same exposure, with the measured spreads", "", "Entry one minute after the open, exit one minute before the close two sessions later; middle values. Fees about 1 basis point (1.5 for the cheaper-priced 1x funds); a short sale also carries about 2.6 basis points for two nights (the 4.8% a year stand-in). A 2x fund needs half the money, so its spread counts half.", "",
          "| way | spread, in and out | total cost, bp of the exposure | with the assumed spreads it was |", "|---|---|---|---|", f"| sell the stock short | {way('stock', 1):.1f} | {st:.1f} | 13.1 |", f"| buy the 1x inverse fund | {way('1x fund', 1):.1f} | {f1:.1f} | 28.2 |", f"| buy the 2x inverse fund with half the money | {way('2x fund', 2):.1f} | {f2:.1f} | 18.7 |",
          "", "By fund (middle value at the entry, 1 minute after the open; number measured): " + ", ".join(f"{s} {g.bp.median():.0f} ({g.bp.notna().sum()})" for s, g in R[(R.kind != "stock") & (R.moment == "entry, 1 minute after the open")].groupby("sym")) + "."]
    DOCS.mkdir(exist_ok=True); (DOCS / "spread_measure.md").write_text("\n".join(L) + "\n"); print("\n".join(L[4:])); print("-> docs/spread_measure.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "fetch", "report"]); ap.add_argument("--max-usd", type=float, default=0.0); ap.add_argument("--sample", type=int, default=40); a = ap.parse_args()
    if a.cmd == "plan": cmd_plan(a.sample)
    elif a.cmd == "report": cmd_report()
    elif a.max_usd <= 0: raise SystemExit("this step spends Databento credit: give a limit, for example --max-usd 5")
    else: cmd_fetch(a.max_usd)
