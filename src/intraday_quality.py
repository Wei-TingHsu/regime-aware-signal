"""intraday_quality.py -- how good is the 1-minute data, measured the way a machine-learning project checks data before using it.
Nothing is changed in the raw files: the check writes a table of flags (one row per instrument per day) that the tests then use to keep or drop a day.

  python -m src.intraday_quality condition      # asks Databento which days IT marks as degraded (free; needs DATABENTO_API_KEY) -> processed/databento_condition.csv
  python -m src.intraday_quality audit          # the checks below, per instrument per day -> processed/intraday_quality.parquet, docs/intraday_quality.md
The checks (standard data-treatment list):
  1 completeness   bars present vs the 390 minutes of the US session (09:30-16:00 New York), and in the two release windows the tests use:
                   08:25-08:40 (data releases) and 13:55-14:30 (Fed statements); days with no bars at all
  2 gaps           the longest run of missing minutes inside the US session
  3 validity       high >= open/close >= low, prices > 0, duplicated or out-of-order timestamps
  4 outliers       one-minute moves above 1%; 'spikes' (a jump that is taken back in the next minute -- the mark of a bad print); contract-roll days
  5 consistency    the day's close-to-close move from the 1-minute data against an independent source (the project's daily ETF returns)
  6 vendor flag    Databento's own 'degraded' days: how different are they on checks 1-2, and how many fall on days the tests need
Treatment rules written into the flags (thresholds printed; nothing is filled in or smoothed):
  usable_session = at least 90% of the 390 session minutes and no gap over 5 minutes;  usable_0830 = at least 12 of 15 minutes;  usable_1400 = at least 28 of 35 minutes.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("data_provenance/intraday"); PROC, DOCS = Path("processed"), Path("docs")
SYMS = ["NQ", "ES", "GC", "GCv", "ZN", "ZNv"]; PROXY = {"ES": "SPY", "NQ": "SOXX", "GC": "GLD", "GCv": "GLD", "ZN": "TLT", "ZNv": "TLT"}      # GCv = gold, most-traded contract (see intraday_fetch gold)
SESSION_MIN, W0830, W1400 = 390, 15, 35


def load(sym: str, year: int) -> pd.DataFrame | None:
    p = ROOT / sym / f"{year}.parquet"
    if not p.exists(): return None
    d = pd.read_parquet(p)
    if "ts_event" in d.columns: d = d.set_index("ts_event")
    d.index = pd.to_datetime(d.index, utc=True); d = d[["open", "high", "low", "close", "volume"] + [c for c in ("instrument_id",) if c in d.columns]]
    d["ny"] = d.index.tz_convert("America/New_York"); return d


def cmd_condition():
    if not os.environ.get("DATABENTO_API_KEY"): raise SystemExit("DATABENTO_API_KEY is not set")
    import databento as db
    c = db.Historical(os.environ["DATABENTO_API_KEY"]); r = c.metadata.get_dataset_range(dataset="GLBX.MDP3"); s = str(r.get("start", r.get("start_date", "")))[:10]; e = str(r.get("end", r.get("end_date", "")))[:10]
    rows = c.metadata.get_dataset_condition(dataset="GLBX.MDP3", start_date=s, end_date=e); df = pd.DataFrame(rows); df.to_csv(PROC / "databento_condition.csv", index=False)
    print(df["condition"].value_counts().to_string()); print(f"-> processed/databento_condition.csv ({len(df)} days {s} -> {e})")


def _day_rows(sym: str, d: pd.DataFrame) -> list[dict]:
    out = []; mins = d["ny"].dt.hour * 60 + d["ny"].dt.minute; date = d["ny"].dt.date; ts = d.index.asi8
    lr = np.log(d["close"].to_numpy(float)); ret = np.diff(lr, prepend=np.nan); same = np.ones(len(d), bool)
    if "instrument_id" in d.columns: iid = d["instrument_id"].to_numpy(); same = np.concatenate([[False], iid[1:] == iid[:-1]])
    dt_min = np.diff(ts, prepend=ts[0]) / 60e9; ret = np.where(same & (dt_min <= 1.01), ret, np.nan)          # a one-minute move needs two adjacent minutes of the same contract
    nxt = np.concatenate([ret[1:], [np.nan]]); spike = (np.abs(ret) > 0.003) & (np.sign(nxt) == -np.sign(ret)) & (np.abs(nxt) > 0.8 * np.abs(ret))
    bad = ((d["high"] < d[["open", "close"]].max(axis=1)) | (d["low"] > d[["open", "close"]].min(axis=1)) | (d[["open", "high", "low", "close"]] <= 0).any(axis=1)).to_numpy()
    dup = np.concatenate([[False], ts[1:] <= ts[:-1]]); roll = np.concatenate([[False], ~same[1:]]) if "instrument_id" in d.columns else np.zeros(len(d), bool)
    f = pd.DataFrame(dict(date=date.to_numpy(), mins=mins.to_numpy(), ret=ret, spike=spike, bad=bad, dup=dup, roll=roll, close=d["close"].to_numpy(float)))
    for day, g in f.groupby("date", sort=True):
        m = g["mins"].to_numpy(); s_ = (m >= 570) & (m < 960); ms = np.sort(m[s_])
        gap = int(max(np.diff(np.concatenate([[569], ms, [960]])).max() - 1, 0)) if len(ms) else SESSION_MIN
        cl = g.loc[m < 960, "close"]; out.append(dict(symbol=sym, date=pd.Timestamp(day), n_bars=len(g), n_session=int(s_.sum()), n_0830=int(((m >= 505) & (m < 520)).sum()), n_1400=int(((m >= 835) & (m < 870)).sum()),
            max_gap_session=gap, bad_ohlc=int(g["bad"].sum()), duplicates=int(g["dup"].sum()), moves_over_1pct=int((g["ret"].abs() > 0.01).sum()), spikes=int(g["spike"].sum()), roll_day=bool(g["roll"].any()),
            max_abs_ret=float(np.nanmax(np.abs(g["ret"].to_numpy()))) if np.isfinite(g["ret"]).any() else np.nan, close_16=float(cl.iloc[-1]) if len(cl) else np.nan))
    return out


def cmd_audit():
    rows = []
    for sym in SYMS:
        years = sorted(int(p.stem) for p in (ROOT / sym).glob("*.parquet") if p.stem.isdigit()) if (ROOT / sym).exists() else []
        if not years: print(f"{sym}: no yearly files under {ROOT / sym}"); continue
        for y in years:
            d = load(sym, y)
            if d is not None and len(d): rows += _day_rows(sym, d)
        print(f"  {sym}: {len(years)} yearly files read")
    Q = pd.DataFrame(rows)
    if Q.empty: print("nothing to audit"); return
    Q = Q[Q["date"].dt.dayofweek < 5].copy()
    Q["usable_session"] = (Q.n_session >= 0.9 * SESSION_MIN) & (Q.max_gap_session <= 5); Q["usable_0830"] = Q.n_0830 >= 12; Q["usable_1400"] = Q.n_1400 >= 28
    cond = None; cp = PROC / "databento_condition.csv"
    if cp.exists():
        c = pd.read_csv(cp); c["date"] = pd.to_datetime(c["date"]); cond = c.set_index("date")["condition"]; Q["vendor"] = Q["date"].map(cond).fillna("unknown")
    else: Q["vendor"] = "not fetched"
    try:
        from src.intraday_fetch import needed_days
        need = set(pd.Timestamp(x) for x in needed_days() if pd.Timestamp(x) >= pd.Timestamp("2010-06-07"))
    except Exception: need = set()
    Q["needed"] = Q["date"].isin(need)
    ref = set(Q[(Q.symbol == "ES") & (Q.n_session >= 300)]["date"]) if (Q.symbol == "ES").any() else set(Q["date"])     # trading days = days ES traded a full session
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    L = ["# Intraday data quality — CME futures, 1-minute bars (Databento GLBX.MDP3)", "", "One row per instrument per weekday. 'Trading days' = days the S&P future traded a full session. Nothing in the raw files is altered; the flags in `processed/intraday_quality.parquet` decide which days a test may use.",
         "Rules: usable session = ≥ 90% of the 390 session minutes present and no gap over 5 minutes; usable 08:30 window = ≥ 12 of 15 minutes; usable 14:00 window = ≥ 28 of 35 minutes.", "",
         "| instrument | trading days | days missing entirely | median session minutes (of 390) | usable session | usable 08:30 | usable 14:00 | invalid bars | duplicate times | moves > 1% | spikes | daily move vs ETF: correlation / days differing > 0.5% |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    print(f"\n{'instr':5} {'days':>5} {'missing':>7} {'med min':>7} {'session ok':>10} {'08:30 ok':>8} {'14:00 ok':>8} {'invalid':>7} {'dups':>5} {'>1%':>4} {'spikes':>6}  daily vs ETF")
    for sym in [s for s in SYMS if (Q.symbol == s).any()]:
        g = Q[(Q.symbol == sym) & Q["date"].isin(ref)]; miss = len(ref - set(g["date"])); cons = "n/a"
        if PROXY[sym] in r.columns:
            fut = np.log(g.set_index("date")["close_16"]).diff(); fut[g.set_index("date")["roll_day"]] = np.nan; x = pd.concat([fut.rename("f"), r[PROXY[sym]].rename("e")], axis=1, sort=True).dropna()
            if len(x) > 100: cons = f"{x.f.corr(x.e):+.2f} with {PROXY[sym]} / {(np.abs(x.f - x.e) > 0.005).mean():.0%}"
        L.append(f"| {sym} | {len(g):,} | {miss} | {g.n_session.median():.0f} | {g.usable_session.mean():.1%} | {g.usable_0830.mean():.1%} | {g.usable_1400.mean():.1%} | {int(g.bad_ohlc.sum())} | {int(g.duplicates.sum())} | {int(g.moves_over_1pct.sum())} | {int(g.spikes.sum())} | {cons} |")
        print(f"{sym:5} {len(g):>5,} {miss:>7} {g.n_session.median():>7.0f} {g.usable_session.mean():>10.1%} {g.usable_0830.mean():>8.1%} {g.usable_1400.mean():>8.1%} {int(g.bad_ohlc.sum()):>7} {int(g.duplicates.sum()):>5} {int(g.moves_over_1pct.sum()):>4} {int(g.spikes.sum()):>6}  {cons}")
    L += ["", "## By year — share of trading days with a usable session", "", "| year | " + " | ".join(s for s in SYMS if (Q.symbol == s).any()) + " |", "|---|" + "---|" * int(sum((Q.symbol == s).any() for s in SYMS))]
    Qr = Q[Q["date"].isin(ref)]
    for y, gy in Qr.groupby(Qr["date"].dt.year): L.append(f"| {y} | " + " | ".join(f"{gy[gy.symbol == s].usable_session.mean():.0%} (median {gy[gy.symbol == s].n_session.median():.0f} min)" for s in SYMS if (Q.symbol == s).any()) + " |")
    if cond is not None:
        L += ["", "## Databento's own 'degraded' days", ""]; print("\nDatabento's degraded days vs the rest:")
        for sym in [s for s in SYMS if (Q.symbol == s).any()]:
            g = Qr[Qr.symbol == sym]; dg, okd = g[g.vendor == "degraded"], g[g.vendor == "available"]
            if len(dg): txt = f"{sym}: {len(dg)} degraded trading days — usable session {dg.usable_session.mean():.0%} (other days {okd.usable_session.mean():.0%}); median session minutes {dg.n_session.median():.0f} vs {okd.n_session.median():.0f}; of the days the tests need, {int((dg.needed).sum())} are degraded and {int((dg.needed & ~dg.usable_session).sum())} of those fail the session rule"
            else: txt = f"{sym}: no degraded trading days in the files"
            L.append("- " + txt); print("  " + txt)
        dd = sorted(set(Qr[(Qr.vendor == "degraded") & Qr.needed]["date"].dt.date)); L += ["", f"Degraded days that the tests need ({len(dd)}): " + ", ".join(str(x) for x in dd[:60]) + (" …" if len(dd) > 60 else "")]
    if need:
        L += ["", "## The days the tests need (Fed statement days, document days, event days; from June 2010)", "", "| instrument | needed days with data | usable session | usable 08:30 | usable 14:00 |", "|---|---|---|---|---|"]; print("\nthe days the tests need:")
        for sym in [s for s in SYMS if (Q.symbol == s).any()]:
            g = Q[(Q.symbol == sym) & Q.needed]; L.append(f"| {sym} | {len(g)} of {len(need)} | {g.usable_session.mean():.1%} | {g.usable_0830.mean():.1%} | {g.usable_1400.mean():.1%} |"); print(f"  {sym}: {len(g)} of {len(need)} with data; usable session {g.usable_session.mean():.1%}, 08:30 {g.usable_0830.mean():.1%}, 14:00 {g.usable_1400.mean():.1%}")
    worst = Q[Q.spikes > 0].sort_values("spikes", ascending=False).head(10); L += ["", "## Days with the most spikes (a jump taken back within a minute)", "", "| instrument | date | spikes | largest one-minute move |", "|---|---|---|---|"] + [f"| {w.symbol} | {w.date.date()} | {w.spikes} | {w.max_abs_ret:.2%} |" for w in worst.itertuples()]
    Q.to_parquet(PROC / "intraday_quality.parquet"); (DOCS / "intraday_quality.md").write_text("\n".join(L) + "\n"); print("\n-> processed/intraday_quality.parquet, docs/intraday_quality.md")


def cmd_missing():
    """Founder, 11 Nov: 'if the 0.2% that fails is the critical data because it is extreme, how do we avoid losing it?' This measures whether the days that
    fail the rules are the EXTREME days, and why each one fails, so that nothing is dropped silently.
    For the instruments the tests use (NQ, ES, GCv, ZNv): every needed day that fails the session rule, with a cause -- 'market-wide' (every instrument is
    short that day: an early close before a holiday, or a trading halt -- both are real market states, not bad data), 'vendor' (Databento marks the day
    degraded), or 'this instrument only'. Then: are failing days bigger-move days than passing days?"""
    Q = pd.read_parquet(PROC / "intraday_quality.parquet"); use = [s_ for s_ in ("NQ", "ES", "GCv", "ZNv") if (Q.symbol == s_).any()]; Q = Q[Q.symbol.isin(use)]
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index); spy = r["SPY"].abs() if "SPY" in r.columns else None
    wide = Q.pivot_table(index="date", columns="symbol", values="n_session"); all_short = (wide < 0.9 * SESSION_MIN).sum(axis=1) >= max(len(use) - 1, 1)
    L = ["# Intraday data — are the days that fail the quality rules the extreme days?", "", "Instruments the tests use: " + ", ".join(use) + ". 'Needed' = Fed statement days, official-document days and ≥ 4% event days from June 2010.", ""]; rows = []
    for sym in use:
        g = Q[(Q.symbol == sym)].set_index("date"); g["abs_spy"] = spy.reindex(g.index) if spy is not None else np.nan; g["market_wide"] = all_short.reindex(g.index).fillna(False)
        g["cause"] = np.where(g.usable_session, "", np.where(g.market_wide, "market-wide (early close or halt)", np.where(g.vendor == "degraded", "vendor: degraded day", "this instrument only")))
        f, ok = g[~g.usable_session], g[g.usable_session]; fn = f[f.needed]
        thr = g["abs_spy"].quantile(0.95); big = g[g["abs_spy"] >= thr]
        txt = (f"{sym}: {len(f)} of {len(g)} weekdays fail the session rule ({len(f) / len(g):.1%}); causes: " + ", ".join(f"{k} {v}" for k, v in f["cause"].value_counts().items()) +
               f". Median S&P move on failing days {f['abs_spy'].median():.2%} vs {ok['abs_spy'].median():.2%} on passing days. Of the {len(big)} largest-move days (top 5% by S&P move), {int((~big.usable_session).sum())} fail ({(~big.usable_session).mean():.1%}). Needed days failing: {len(fn)}.")
        print(txt); L.append("- " + txt)
        for d, w in fn.iterrows(): rows.append(dict(instrument=sym, date=d.date(), session_minutes=int(w.n_session), longest_gap=int(w.max_gap_session), usable_0830=bool(w.usable_0830), usable_1400=bool(w.usable_1400), vendor=w.vendor, cause=w.cause, spy_move=w.abs_spy))
    T = pd.DataFrame(rows)
    if len(T):
        T = T.sort_values(["date", "instrument"]); print("\nneeded days that fail the session rule:"); print(T.to_string(index=False, formatters=dict(spy_move=lambda v: f"{v:.2%}" if v == v else "n/a")))
        L += ["", "## Needed days that fail the session rule", "", "| instrument | date | session minutes (of 390) | longest gap | 08:30 window ok | 14:00 window ok | vendor flag | cause | S&P move that day |", "|---|---|---|---|---|---|---|---|---|"]
        for w in T.itertuples(): L.append(f"| {w.instrument} | {w.date} | {w.session_minutes} | {w.longest_gap} | {w.usable_0830} | {w.usable_1400} | {w.vendor} | {w.cause} | {w.spy_move:.2%} |" if w.spy_move == w.spy_move else f"| {w.instrument} | {w.date} | {w.session_minutes} | {w.longest_gap} | {w.usable_0830} | {w.usable_1400} | {w.vendor} | {w.cause} | n/a |")
        T.to_csv(PROC / "intraday_failing_needed_days.csv", index=False)
    (DOCS / "intraday_quality_missing.md").write_text("\n".join(L) + "\n"); print("-> docs/intraday_quality_missing.md, processed/intraday_failing_needed_days.csv")


FINAL = {"NQ": ("NQ", "NQ_alt"), "ES": ("ES", "ES_alt"), "GC": ("GCv", "GC_alt"), "ZN": ("ZNv", "ZN_alt")}


def cmd_final():
    """The table the tests use. Per instrument and day: the main file, or the patch file (the neighbouring contract) when that one has more session minutes.
    One contract per day -- two contracts are never spliced inside a day. Rules, revised 11 Nov after the missing-day check: a session is usable when at
    least 90% of its 390 minutes are present; a gap alone no longer fails a day, because the gaps found on the needed days are exchange trading halts
    (9, 12, 16, 18 March 2020), which are real market states. The two release windows keep their own rules."""
    Q = pd.read_parquet(PROC / "intraday_quality.parquet"); rows = []
    for sym, (main, alt) in FINAL.items():
        g = Q[Q.symbol == main].copy(); g["source"] = "main"; ap = ROOT / alt / "all.parquet"
        if ap.exists():
            d = pd.read_parquet(ap)
            if "ts_event" in d.columns: d = d.set_index("ts_event")
            d.index = pd.to_datetime(d.index, utc=True); d = d[["open", "high", "low", "close", "volume"] + [c for c in ("instrument_id",) if c in d.columns]]; d["ny"] = d.index.tz_convert("America/New_York")
            A = pd.DataFrame(_day_rows(alt, d)).set_index("date"); g = g.set_index("date"); better = A.index[A.index.isin(g.index)]; better = [x for x in better if A.loc[x, "n_session"] > g.loc[x, "n_session"]]
            new_days = [x for x in A.index if x not in g.index and x.dayofweek < 5]
            for col in ("n_bars", "n_session", "n_0830", "n_1400", "max_gap_session", "bad_ohlc", "duplicates", "moves_over_1pct", "spikes", "max_abs_ret", "close_16"): g.loc[better, col] = A.loc[better, col]
            g.loc[better, "source"] = "patch"; g = g.reset_index()
            if new_days:
                extra = A.loc[new_days].reset_index(); extra["source"] = "patch"; extra["vendor"] = "unknown"; extra["needed"] = False; g = pd.concat([g, extra], ignore_index=True)
            print(f"  {sym}: {len(better)} days taken from the patch file, {len(new_days)} days added")
        else: print(f"  {sym}: no patch file ({ap}) -- main file only")
        g["symbol"] = sym; rows.append(g)
    F = pd.concat(rows, ignore_index=True); F["usable_session"] = F.n_session >= 0.9 * SESSION_MIN; F["usable_0830"] = F.n_0830 >= 12; F["usable_1400"] = F.n_1400 >= 28
    try:
        from src.intraday_fetch import needed_days
        need = set(pd.Timestamp(x) for x in needed_days() if pd.Timestamp(x) >= pd.Timestamp("2010-06-07")); F["needed"] = F["date"].isin(need)
    except Exception: pass
    F.to_parquet(PROC / "intraday_quality_final.parquet"); ref = set(F[F.n_session >= 300]["date"])      # a trading day = a day on which ANY of the four traded a full session (an expiry day empties one instrument, not the market)
    L = ["# Intraday data — the final table the tests use", "", "Main file or patch file per day (never both inside a day). Usable session = at least 90% of the 390 session minutes; trading halts are kept. 'Needed' = Fed statement days, document days and event days from June 2010.", "",
         "| instrument | trading days | usable session | on needed days: usable session | usable 08:30 window | usable 14:00 window | days from the patch file |", "|---|---|---|---|---|---|---|"]
    print(f"\n{'instr':5} {'days':>5} {'session ok':>10} | needed: {'session':>7} {'08:30':>6} {'14:00':>6} | patched")
    for sym in FINAL:
        g = F[(F.symbol == sym) & F["date"].isin(ref)]; n = g[g.needed]
        L.append(f"| {sym} | {len(g):,} | {g.usable_session.mean():.2%} | {n.usable_session.mean():.2%} ({int((~n.usable_session).sum())} fail of {len(n)}) | {n.usable_0830.mean():.2%} | {n.usable_1400.mean():.2%} | {int((g.source == 'patch').sum())} |")
        print(f"{sym:5} {len(g):>5,} {g.usable_session.mean():>10.2%} |         {n.usable_session.mean():>7.2%} {n.usable_0830.mean():>6.2%} {n.usable_1400.mean():>6.2%} | {int((g.source == 'patch').sum())}")
    bad = F[F.needed & F["date"].isin(ref) & ~(F.usable_session & F.usable_1400 & F.usable_0830)].sort_values(["date", "symbol"])
    L += ["", f"## Needed days still short on the session or a release window ({len(bad)} instrument-days)", "", "| instrument | date | session minutes | 08:30 window minutes (of 15) | 14:00 window minutes (of 35) | longest gap | source | vendor flag |", "|---|---|---|---|---|---|---|---|"]
    for w in bad.itertuples(): L.append(f"| {w.symbol} | {w.date.date()} | {int(w.n_session)} | {int(w.n_0830)} | {int(w.n_1400)} | {int(w.max_gap_session)} | {w.source} | {w.vendor} |")
    if len(bad): print("\nneeded days still short on the session or a release window:"); print(bad[["symbol", "date", "n_session", "n_0830", "n_1400", "max_gap_session", "source", "vendor"]].to_string(index=False))
    (DOCS / "intraday_quality_final.md").write_text("\n".join(L) + "\n"); print("\n-> processed/intraday_quality_final.parquet, docs/intraday_quality_final.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["condition", "audit", "missing", "final"]); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    {"condition": cmd_condition, "audit": cmd_audit, "missing": cmd_missing, "final": cmd_final}[a.cmd]()
