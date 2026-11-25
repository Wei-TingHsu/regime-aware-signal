"""pool_intraday.py -- 1-minute prices of the 20 pool stocks (docs/POOL_PLAN.md) from Databento, for the work on news and turns at the level of minutes.

Why. A company's filing carries the minute it became public (the SEC's acceptance time). With daily prices one can only ask 'did the trend turn on that DAY';
with 1-minute prices one can ask 'what did the price do in the minutes and hours after the news came out' -- the founder's points on publication time and on
recording news at once. Daily prices cannot answer that. This file only DOWNLOADS; it tests nothing.

    export DATABENTO_API_KEY=...                 # typed by the founder in the terminal; never written to a file
    python -m src.pool_intraday plan             # the price quoted by Databento and what is already on disk; nothing is downloaded
    python -m src.pool_intraday fetch --max-usd 15     # downloads until done or until the limit; safe to stop (Ctrl+C) and run again -- it continues where it stopped

Data: dataset XNAS.ITCH (trades on the Nasdaq exchange, 04:00-20:00 New York, from May 2018), 1-minute bars, prices as traded (not adjusted for splits).
One file per stock per year: data_provenance/intraday/eq/<STOCK>/<year>.parquet -- the same place and layout as src.intraday_fetch equities_fetch, so
anything already downloaded there is not downloaded or paid for again. That folder is ignored by git: licensed data is not uploaded.
"""
from __future__ import annotations
import argparse, time, warnings
from pathlib import Path
import pandas as pd

POOL = ["AAPL", "AMD", "AMZN", "AVGO", "CRWD", "CSCO", "EMR", "GE", "GOOG", "IBM", "INTC", "META", "MSFT", "MU", "NVDA", "ORCL", "QCOM", "SNDK", "TSM", "TXN"]      # docs/POOL_PLAN.md
DS, SCHEMA = "XNAS.ITCH", "ohlcv-1m"; OUT = Path("data_provenance/intraday/eq")
OLD = {"META": [("FB", "2022-06-09")]}      # Meta traded as FB until 8 June 2022


def _jobs(s_: str, e_: str) -> list:
    """one job = one stock, one year (and FB for Meta's years before the change of name)"""
    J = []
    for t in POOL:
        for y in range(int(s_[:4]), int(e_[:4]) + 1):
            a, b = max(s_, f"{y}-01-01"), min(e_, f"{y + 1}-01-01")
            if a < b: J.append(dict(stock=t, sym=t, year=y, start=a, end=b, file=OUT / t / f"{y}.parquet"))
            for old, until in OLD.get(t, []):
                b2 = min(b, until)
                if a < b2: J.append(dict(stock=t, sym=old, year=y, start=a, end=b2, file=OUT / t / f"{y}_{old}.parquet"))
    return J


def _done(j) -> bool: return j["file"].exists() or j["file"].with_suffix(".none").exists()      # .none = asked before, Databento had no bars for it (the stock was not listed that year)


def _range(c):
    r = c.metadata.get_dataset_range(dataset=DS); return str(r.get("start", r.get("start_date", "")))[:10], str(r.get("end", r.get("end_date", "")))[:10]


def cmd_plan():
    from src.intraday_fetch import _client
    c = _client(); s_, e_ = _range(c); J = _jobs(s_, e_); todo = [j for j in J if not _done(j)]; total = 0.0; per = {}
    print(f"{DS}, 1-minute bars, {s_} to {e_}. {len(POOL)} pool stocks -> {len(J)} stock-years; {len(J) - len(todo)} already on disk, {len(todo)} to download.")
    for t in POOL:
        tj = [j for j in todo if j["stock"] == t]; usd = 0.0
        for sym in sorted({j["sym"] for j in tj}):
            sj = [j for j in tj if j["sym"] == sym]
            try: usd += float(c.metadata.get_cost(dataset=DS, symbols=[sym], stype_in="raw_symbol", schema=SCHEMA, start=min(j["start"] for j in sj), end=max(j["end"] for j in sj)))
            except Exception as ex: print(f"  {sym}: no quote ({type(ex).__name__}: {str(ex)[:80]})")
        per[t] = usd; total += usd
    print("  quoted, US$: " + ", ".join(f"{t} {v:.2f}" for t, v in per.items()))
    print(f"QUOTED PRICE FOR EVERYTHING STILL MISSING: about US${total:.2f} (an upper figure: years already on disk inside a stock's range are counted again here, not charged again). Nothing was downloaded.")


def cmd_fetch(max_usd: float):
    from src.intraday_fetch import _client
    c = _client(); s_, e_ = _range(c); J = _jobs(s_, e_); todo = [j for j in J if not _done(j)]; spent = 0.0; n = 0; bars = 0; bad = []; t0 = time.time()
    print(f"{len(todo)} stock-years to download (of {len(J)}); limit US${max_usd:.2f}. Safe to stop with Ctrl+C and run again: finished files are kept and never paid twice.")
    for k, j in enumerate(todo):
        ok = False
        for attempt in range(4):      # Databento sometimes answers 'gateway timeout' (504) or the network drops: wait and ask again
            try:
                usd = float(c.metadata.get_cost(dataset=DS, symbols=[j["sym"]], stype_in="raw_symbol", schema=SCHEMA, start=j["start"], end=j["end"]))
                if spent + usd > max_usd: print(f"  the limit of US${max_usd:.2f} is reached after {n} files (about US${spent:.2f} charged). Run again with a higher --max-usd to continue."); _summary(n, bars, spent, bad, t0); return
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore"); df = c.timeseries.get_range(dataset=DS, symbols=[j["sym"]], stype_in="raw_symbol", schema=SCHEMA, start=j["start"], end=j["end"]).to_df()
                j["file"].parent.mkdir(parents=True, exist_ok=True)
                if len(df): tmp = j["file"].with_suffix(".tmp"); df.to_parquet(tmp); tmp.replace(j["file"]); bars += len(df)
                else: j["file"].with_suffix(".none").write_text("no bars\n")
                spent += usd; n += 1; ok = True; break
            except KeyboardInterrupt: raise
            except Exception as ex:
                why = f"{type(ex).__name__}: {str(ex)[:90]}"
                if attempt < 3: time.sleep(15 * (attempt + 1))
        if not ok:
            bad.append(f"{j['sym']} {j['year']}"); print(f"  {j['sym']} {j['year']}: failed 4 times ({why}) -- skipped; the next run tries it again")
            if len(bad) >= 8 and n == 0: print("  stopped: 8 failures and nothing downloaded -- the key or the connection. Tell Claude what the lines above say."); break
        if n in (3, 10) or (n and n % 25 == 0 and ok):
            per = (time.time() - t0) / max(n, 1); left = len(todo) - k - 1; print(f"  {n} files, {bars:,} bars, about US${spent:.2f} so far; measured {per:.0f} seconds a file -> about {left * per / 60:.0f} minutes left for {left} files")
    _summary(n, bars, spent, bad, t0)


def _summary(n, bars, spent, bad, t0):
    have = sum(1 for t in POOL if (OUT / t).exists() and any((OUT / t).glob("*.parquet")))
    print(f"DONE: {n} files downloaded now, {bars:,} one-minute bars, about US${spent:.2f} charged, {(time.time() - t0) / 60:.0f} minutes; failed: {', '.join(bad) or 'none'}. Stocks with data on disk: {have} of {len(POOL)}. -> {OUT} (ignored folder; not uploaded)")


def cmd_show():
    """what is on disk, per stock (free, no key needed)"""
    for t in POOL:
        fs = sorted((OUT / t).glob("*.parquet")) if (OUT / t).exists() else []
        if not fs: print(f"  {t}: nothing"); continue
        n = sum(len(pd.read_parquet(f, columns=["close"])) for f in fs); print(f"  {t}: {len(fs)} files ({fs[0].stem} to {fs[-1].stem}), {n:,} bars")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "fetch", "show"]); ap.add_argument("--max-usd", type=float, default=15.0); a = ap.parse_args()
    {"plan": cmd_plan, "fetch": lambda: cmd_fetch(a.max_usd), "show": cmd_show}[a.cmd]()
