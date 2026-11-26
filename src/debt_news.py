"""debt_news.py -- test DN-1 (TRACK 3.137): when a large AI spender raises new debt, what do its own share and the semiconductor shares do?

The founder's question behind the CDS (26 Nov 2026): traders change the CDS price because of news -- which news? The CDS itself did not lead chip shares (CDS-1 to CDS-4).
This goes to the news directly: a company's new debt shows in the SEC's files the day it is sold -- a prospectus supplement or pricing sheet (forms 424B2, 424B3, 424B5, FWP)
or an 8-K with item 2.03 ('creation of a direct financial obligation': a loan, a credit line, notes). Free, public, with the minute of filing.

    python -m src.debt_news fetch      # free; the SEC's filing lists of 17 companies (SEC_CONTACT must be set) -> data_provenance/debt_news/filings.csv
    python -m src.debt_news run        # the test; needs the daily check's prices (data_provenance/selloff_live/prices) and SOXX (data_provenance/leading)

A DEAL = a company's first debt filing after 7 days without one. Its day 0 = the day of that filing (for an 8-K filed after 16:00 New York: the next session).
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("data_provenance/debt_news"); DOCS = Path("docs"); PXD = Path("data_provenance/selloff_live/prices"); LEAD = Path("data_provenance/leading")
FIVE = ["ORCL", "META", "GOOG", "AMZN", "MSFT"]; OTHERS = ["CRWV", "NVDA", "AVGO", "AMD", "INTC", "MU", "IBM", "CSCO", "AAPL", "DELL", "QCOM", "TXN"]
DEBT_FORMS = {"424B2", "424B3", "424B5", "FWP"}; GAP_DAYS = 7; MIN_EVENTS = 8; MINSHIFT = 20
WINDOWS = {"day 0 (the day of the filing)": "r0", "the session after": "r1", "the 5 sessions after": "r5"}; PERIODS = {"2018 to now": "2018-01-01", "2025 to now (the AI build-out)": "2025-01-01"}


def cmd_fetch():
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set. In the terminal: export SEC_CONTACT=your@address")
    import src.ai_earnings as A
    FS = A._sec(); cmap = json.loads(FS.get(FS.TICKERS)); look = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}; rows = []; bad = []
    for t in FIVE + OTHERS:
        tick = next((a for a in A.ALIAS.get(t, [t]) if a in look), None)
        if tick is None: bad.append(t); continue
        try: F, _ = A._all_filings(FS, look[tick])
        except Exception as ex: bad.append(f"{t} ({type(ex).__name__})"); continue
        F = F.assign(ticker=t); F["accepted_ny"] = A._ny(F["accepted_raw"]); rows.append(F[["ticker", "form", "items", "accepted_ny", "accession"]]); time.sleep(0.15)
    M = pd.concat(rows, ignore_index=True).dropna(subset=["accepted_ny"]); M = M[M.accepted_ny >= "2017-06-01"]; M["debt"] = M.form.str.upper().isin(DEBT_FORMS) | (M.form.str.upper().isin(["8-K", "8-K/A"]) & M["items"].astype(str).str.contains("2.03", regex=False))
    ROOT.mkdir(parents=True, exist_ok=True); M[M.debt].drop(columns="debt").sort_values(["ticker", "accepted_ny"]).to_csv(ROOT / "filings.csv", index=False)
    print(f"{int(M.debt.sum())} debt filings of {M[M.debt].ticker.nunique()} companies since mid-2017 (of {len(M):,} filings read); no list for: {bad or 'none'}. Free. -> {ROOT / 'filings.csv'}")
    print("  by company: " + ", ".join(f"{t} {n}" for t, n in M[M.debt].ticker.value_counts().items()))


def deals() -> pd.DataFrame:
    F = pd.read_csv(ROOT / "filings.csv", parse_dates=["accepted_ny"]).sort_values(["ticker", "accepted_ny"]); out = []
    for t, g in F.groupby("ticker"):
        last = None; cur = None
        for r in g.itertuples():
            if last is None or (r.accepted_ny - last).days >= GAP_DAYS: cur = dict(ticker=t, first=r.accepted_ny, forms=[r.form], n=1, is8k=str(r.form).upper().startswith("8-K")); out.append(cur)
            else: cur["forms"].append(r.form); cur["n"] += 1
            last = r.accepted_ny
    D = pd.DataFrame(out); D["forms"] = D.forms.apply(lambda x: ", ".join(sorted(set(x)))); return D


def _close(sym):
    for f in (PXD / f"{sym}.parquet", LEAD / f"y_{sym}.parquet"):
        if f.exists():
            d = pd.read_parquet(f); s = d["close"] if "close" in d.columns else d.iloc[:, 0]; s.index = pd.DatetimeIndex(s.index).tz_localize(None) if getattr(s.index, "tz", None) is not None else pd.DatetimeIndex(s.index); return s.dropna()
    return None


def _rets(s, cal):
    s = s.reindex(cal); return dict(r0=(s / s.shift(1) - 1).to_numpy(), r1=(s.shift(-1) / s - 1).to_numpy(), r5=(s.shift(-5) / s - 1).to_numpy())


def cmd_run():
    if not (ROOT / "filings.csv").exists(): print("run `python -m src.debt_news fetch` first"); return
    soxx = _close("SOXX")
    if soxx is None: print("no SOXX prices: run `python -m src.leading fetch` first"); return
    D = deals(); cal = soxx.index[soxx.index >= "2018-01-01"]; pos = {d: i for i, d in enumerate(cal)}; RS = _rets(soxx, cal); RO = {}; miss = []
    for t in FIVE:
        s = _close(t)
        if s is None: miss.append(t)
        else: RO[t] = _rets(s, cal)
    if miss: print(f"  no share prices for {miss}: run the daily check first (python -m src.selloff_live daily)")
    def day0(r):      # the session of the filing; an 8-K filed after the close counts for the next session; a filing on a closed day counts for the next session
        d = r["first"].normalize(); late = r["is8k"] and (r["first"].hour >= 16); i = int(np.searchsorted(cal.values, np.datetime64(d), side="left")); i = i + 1 if (late and i < len(cal) and cal[i] == d) else i
        return cal[i] if i < len(cal) else pd.NaT
    D["day0"] = D.apply(day0, axis=1); D = D.dropna(subset=["day0"]); E = D[D.ticker.isin(RO)]
    flags = {t: np.zeros(len(cal), bool) for t in RO}
    for r in E.itertuples(): flags[r.ticker][pos[r.day0]] = True
    groups = {"the five AI spenders (Oracle, Meta, Alphabet, Amazon, Microsoft)": [t for t in FIVE if t in RO], "Oracle alone": [t for t in ["ORCL"] if t in RO]}
    def z_of(tickers, w, target, lo, shift=0):
        if target == "own":
            a, b = [], []
            for t in tickers:
                e = np.roll(flags[t][lo:], shift) if shift else flags[t][lo:]; r = RO[t][w][lo:]; ok = np.isfinite(r); a.append(r[e & ok]); b.append(r[~e & ok])
            a = np.concatenate(a); b = np.concatenate(b)
        else:
            e = np.zeros(len(cal) - lo, bool)
            for t in tickers: e |= flags[t][lo:]
            e = np.roll(e, shift) if shift else e; r = RS[w][lo:]; ok = np.isfinite(r); a = r[e & ok]; b = r[~e & ok]
        if len(a) < MIN_EVENTS or len(b) < 100: return np.nan, len(a), np.nan
        return (a.mean() - b.mean()) / (np.concatenate([a, b]).std() / np.sqrt(len(a))), len(a), a.mean() - b.mean()
    cells = {}
    for pname, start in PERIODS.items():
        lo = int(np.searchsorted(cal.values, np.datetime64(start)))
        for gname, tk in groups.items():
            for target, tlabel in (("own", "its own share"), ("soxx", "the semiconductor fund (SOXX)")):
                for wlabel, w in WINDOWS.items():
                    z, n, diff = z_of(tk, w, target, lo); cells[(pname, gname, tlabel, wlabel)] = dict(z=z, n=n, diff=diff, lo=lo, tk=tk, w=w, target=target)
    live = {k: v for k, v in cells.items() if v["z"] == v["z"]}; exceed = {k: 0 for k in live}; done = {k: 0 for k in live}; best_obs = max((abs(v["z"]) for v in live.values()), default=np.nan); beat = 0; total = 0
    nmin = min((len(cal) - v["lo"] for v in live.values()), default=0)
    for sh in range(MINSHIFT, max(MINSHIFT, nmin - MINSHIFT)):
        m = 0.0
        for k, v in live.items():
            z, _, _ = z_of(v["tk"], v["w"], v["target"], v["lo"], sh)
            if z == z: done[k] += 1; exceed[k] += abs(z) >= abs(v["z"]); m = max(m, abs(z))
        total += 1; beat += m >= best_obs
    whole = (beat + 1) / (total + 1) if total else np.nan; verdict = "MORE THAN LUCK" if whole == whole and whole < 0.05 else "NOT more than luck"
    rows = [dict(period=k[0], who=k[1], share=k[2], window=k[3], deals=v["n"], diff_pct=v["diff"] * 100 if v["diff"] == v["diff"] else np.nan, chance=(exceed[k] + 1) / (done[k] + 1) if k in live and done[k] else np.nan) for k, v in cells.items()]
    T = pd.DataFrame(rows); J = T[T.chance.notna()].sort_values("chance"); top = J.iloc[0] if len(J) else None; f2 = lambda x: "n/a" if x != x else f"{x:+.2f}"
    counts = D.groupby("ticker").size(); recent = D[D.day0 >= "2025-01-01"].groupby("ticker").size()
    L = ["# Test DN-1: when a large AI spender raises new debt, what do its own share and the semiconductor shares do?", "", f"Registered in TRACK 3.137 before running. Debt filings from the SEC's lists (forms 424B2, 424B3, 424B5, FWP; 8-K item 2.03). A deal = a company's first debt filing after {GAP_DAYS} days without one. "
         f"Deals since 2018: " + ", ".join(f"{t} {int(counts.get(t, 0))} ({int(recent.get(t, 0))} since 2025)" for t in FIVE) + ". 'Difference' = the share's average move in the window after a deal minus its average move on all other days. "
         "One verdict for the whole grid: is the strongest cell matched by the strongest cell of the copies (deal days slid along the calendar) in fewer than 5% of them? Each cell's own chance is a description. Under 8 deals: too few.", "",
         f"**Verdict for the whole grid: {verdict}** -- the strongest cell is matched or beaten in {whole:.0%} of {total} copies (limit 5%). Cells under 0.05 on their own: {int((J.chance < 0.05).sum())} of {len(J)}; by luck alone about {len(J) * 0.05:.0f}.", "",
         "| period | whose deals | share watched | window | deals | difference, % | chance of this cell |", "|---|---|---|---|---|---|---|"]
    for r in T.itertuples(): L.append(f"| {r.period} | {r.who} | {r.share} | {r.window} | {r.deals} | {f2(r.diff_pct)} | {'too few' if r.chance != r.chance else f'{r.chance:.4f}'} |")
    L += ["", "## Every deal of the five since 2025", "", "| day 0 | company | filings | own share: day 0 / the session after / 5 sessions after | SOXX: day 0 / after / 5 after |", "|---|---|---|---|---|"]
    pc = lambda x: "n/a" if x != x else f"{x * 100:+.1f}%"; case = []
    for r in E[E.day0 >= "2025-01-01"].sort_values("day0").itertuples():
        i = pos[r.day0]; a = " / ".join(pc(RO[r.ticker][w][i]) for w in ("r0", "r1", "r5")); b = " / ".join(pc(RS[w][i]) for w in ("r0", "r1", "r5")); case.append(f"{r.day0:%Y-%m-%d} | {r.ticker} | {r.forms} ({r.n}) | {a} | {b}"); L.append("| " + case[-1] + " |")
    oth = D[D.ticker.isin(OTHERS)]
    L += ["", "## Other companies (counted, not tested)", "", ", ".join(f"{t} {int((oth.ticker == t).sum())} deals ({int(((oth.ticker == t) & (oth.day0 >= '2025-01-01')).sum())} since 2025)" for t in OTHERS),
          "", "What this cannot say: a bond sale is usually known to the market in the morning and filed with the SEC in the afternoon or evening, so day 0 is measured as a whole day, not from the filing minute; a filing says debt was raised, not how much or at what price (that needs the document read); deals of different size count the same.",
          "Source: SEC EDGAR submissions (public domain)."]
    DOCS.mkdir(exist_ok=True); (DOCS / "debt_news.md").write_text("\n".join(L) + "\n"); T.to_csv(DOCS / "debt_news.csv", index=False)
    print("deals since 2018 (since 2025): " + ", ".join(f"{t} {int(counts.get(t, 0))} ({int(recent.get(t, 0))})" for t in FIVE))
    print(f"VERDICT FOR THE WHOLE GRID: {verdict} -- the strongest cell is matched or beaten in {whole:.0%} of {total} copies (limit 5%). Cells under 0.05 on their own: {int((J.chance < 0.05).sum())} of {len(J)}; by luck alone about {len(J) * 0.05:.0f}.")
    if top is not None: print(f"  strongest cell: {top.who}, {top.share}, {top.window}, {top.period}: {f2(top.diff_pct)}% on {top.deals} deals (its own chance {top.chance:.4f})")
    print("  difference % (chance) | deals | period | whose deals | share watched | window")
    for r in T.sort_values("chance").itertuples(): print(f"    {f2(r.diff_pct)} ({'too few' if r.chance != r.chance else f'{r.chance:.4f}'}) | {r.deals} | {r.period[:12]} | {r.who[:22]} | {r.share[:22]} | {r.window}")
    print("  every deal of the five since 2025: day 0 | company | filings | own share day 0 / after / 5 after | SOXX day 0 / after / 5 after")
    for c in case: print("    " + c)
    print("-> docs/debt_news.md, docs/debt_news.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fetch", "run"]); a = ap.parse_args(); cmd_fetch() if a.cmd == "fetch" else cmd_run()
