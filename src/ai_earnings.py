"""ai_earnings.py -- the AI-chain earnings test, stage A: the results releases of the founder's company list, with the minute each reached the SEC.
(Design: TRACK 3.59. Stage B -- the scores, the registration and the tests on the Nasdaq-100 future and on the stocks -- follows once this is on disk.)

  export SEC_CONTACT=you@example.com           # the SEC asks automated readers to identify themselves
  python -m src.ai_earnings filings            # every 8-K with Item 2.02 (results of operations) from June 2010 for the US filers on the list: the filing's
                                               #   acceptance time (to the second) and the text of the attached release -> data_provenance/ai_earnings/
                                               #   foreign filers (6-K: TSM, and SK Hynix if listed) are counted here and handled in stage B
  python -m src.ai_earnings times              # when in the day the releases arrive, per company -> docs/ai_earnings_times.md
Nothing here calls the LLM. Company list (founder, 12 Nov 2026): AMD NVDA MU INTC AVGO SNDK SKHY ORCL TSM CRWD GOOG META AMZN MSFT.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

LIST = ["AMD", "NVDA", "MU", "INTC", "AVGO", "SNDK", "SKHY", "ORCL", "TSM", "CRWD", "GOOG", "META", "AMZN", "MSFT"]
ALIAS = {"GOOG": ["GOOG", "GOOGL"], "META": ["META", "FB"]}
ROOT = Path("data_provenance/ai_earnings"); TXT = ROOT / "docs"; PROC, DOCS = Path("processed"), Path("docs"); START = "2010-06-01"


def _sec():
    import src.fetch_sources as FS
    return FS


def _all_filings(FS, cik: str) -> pd.DataFrame:
    sub = json.loads(FS.get(FS.SUBS.format(cik=cik))); blocks = [sub.get("filings", {}).get("recent", {})]
    for f in sub.get("filings", {}).get("files", []):
        try: blocks.append(json.loads(FS.get("https://data.sec.gov/submissions/" + f["name"]))); time.sleep(0.12)
        except Exception as e: print(f"      older page {f.get('name')}: {type(e).__name__}")
    rows = []
    for b in blocks:
        n = len(b.get("form", []))
        for i in range(n): rows.append(dict(form=b["form"][i], filing_date=b["filingDate"][i], accepted_raw=b.get("acceptanceDateTime", [""] * n)[i], accession=b["accessionNumber"][i], primary=b.get("primaryDocument", [""] * n)[i], items=b.get("items", [""] * n)[i]))
    return pd.DataFrame(rows), sub.get("name", "")


def cmd_filings(limit: int | None):
    import os
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set. In the terminal: export SEC_CONTACT=your@address  (the SEC refuses automated readers that do not identify themselves)")
    FS = _sec(); TXT.mkdir(parents=True, exist_ok=True); args = SimpleNamespace(sleep=0.12, verbose_exhibits=False)
    cmap = json.loads(FS.get(FS.TICKERS)); lookup = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}; meta = []; old = PROC / "ai_earnings_filings.csv"
    have = pd.read_csv(old, dtype=str) if old.exists() else pd.DataFrame(columns=["accession"])
    for t in LIST:
        tick = next((a for a in ALIAS.get(t, [t]) if a in lookup), None)
        if tick is None: print(f"  {t}: not in the SEC's ticker file -- skipped (no US filings found under {ALIAS.get(t, [t])})"); continue
        cik = lookup[tick]
        try: F, name = _all_filings(FS, cik)
        except Exception as e: print(f"  {t}: submissions FAILED: {e}"); continue
        F = F[F["filing_date"] >= START]; k8 = F[(F.form.str.upper() == "8-K") & F["items"].fillna("").str.contains("2.02", regex=False)]; k6 = F[F.form.str.upper() == "6-K"]
        if len(k8) == 0: print(f"  {t:5} {name[:34]:34} CIK {cik}: no 8-K Item 2.02 since {START}; {len(k6)} 6-K filings (a foreign filer -- stage B)"); meta += [dict(ticker=t, form="6-K", items="", filing_date=r.filing_date, accepted_raw=r.accepted_raw, accession=r.accession, primary=r.primary, words=0, file="") for r in k6.itertuples()]; continue
        todo = k8 if limit is None else k8.head(limit); n_new = n_skip = 0
        for r in todo.itertuples():
            accn = r.accession.replace("-", ""); f = TXT / f"{t}_{accn}.txt"
            if not f.exists() and r.accession not in set(have["accession"]):
                try: body, names = FS.fetch_exhibits(cik, accn, r.primary, args, ticker=t)
                except Exception: body, names = "", []
                if not body or not FS.has_figures(body): n_skip += 1; meta.append(dict(ticker=t, form="8-K", items=r.items, filing_date=r.filing_date, accepted_raw=r.accepted_raw, accession=r.accession, primary=r.primary, words=0, file="")); continue
                f.write_text(f"[{t} 8-K items: {r.items}] [exhibits: {', '.join(names)}]\n\n{body}"); n_new += 1; time.sleep(0.12)
            words = len(f.read_text().split()) if f.exists() else 0
            meta.append(dict(ticker=t, form="8-K", items=r.items, filing_date=r.filing_date, accepted_raw=r.accepted_raw, accession=r.accession, primary=r.primary, words=words, file=str(f) if f.exists() else ""))
        print(f"  {t:5} {name[:34]:34} CIK {cik}: {len(k8)} results filings since {START}; {n_new} release texts fetched now, {n_skip} without a readable release")
    M = pd.DataFrame(meta)
    if M.empty: print("nothing found"); return
    # acceptance time: the SEC's JSON stamps look like 2024-05-22T16:21:06.000Z. Decide from the data whether that is New York clock time or UTC: results
    # releases cluster just after the 16:00 close, so the most common hour is 16 if it is New York time and 20 or 21 if it is UTC.
    ts = pd.to_datetime(M["accepted_raw"].str.replace("Z", "", regex=False), errors="coerce"); us = M["form"] == "8-K"; hrs = ts[us].dt.hour.value_counts()
    is_utc = int(hrs.get(20, 0) + hrs.get(21, 0)) > int(hrs.get(16, 0)); mode = "UTC" if is_utc else "New York clock time"
    M["accepted_ny"] = (ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None) if is_utc else ts)
    print(f"acceptance stamps read as {mode} (hour counts among results filings: 16h {int(hrs.get(16, 0))}, 20h {int(hrs.get(20, 0))}, 21h {int(hrs.get(21, 0))})")
    M = M.drop_duplicates("accession").sort_values(["ticker", "accepted_ny"]); M.to_csv(old, index=False); ok = M[(M.form == "8-K") & (M.words > 0)]
    print(f"-> processed/ai_earnings_filings.csv: {len(M)} filings; {len(ok)} results releases with text ({ok['ticker'].nunique()} companies, {ok['accepted_ny'].min():%Y-%m-%d} -> {ok['accepted_ny'].max():%Y-%m-%d}); texts under {TXT}")


def cmd_times():
    M = pd.read_csv(PROC / "ai_earnings_filings.csv", parse_dates=["accepted_ny"]); E = M[(M.form == "8-K") & (M.words > 0)].copy(); m = E["accepted_ny"].dt.hour * 60 + E["accepted_ny"].dt.minute
    E["when"] = pd.cut(m, [-1, 569, 959, 1019, 1199, 1440], labels=["before the open (to 09:30)", "during the session", "16:00-16:59", "17:00-19:59", "20:00 or later"])
    tab = E.pivot_table(index="ticker", columns="when", values="accession", aggfunc="count", fill_value=0, observed=False); tab["total"] = tab.sum(axis=1); tab["first"] = E.groupby("ticker")["accepted_ny"].min().dt.date; tab["median clock time"] = E.groupby("ticker")["accepted_ny"].apply(lambda s: f"{int((s.dt.hour * 60 + s.dt.minute).median()) // 60:02d}:{int((s.dt.hour * 60 + s.dt.minute).median()) % 60:02d}")
    print(tab.to_string()); six = M[M.form == "6-K"].groupby("ticker").size()
    if len(six): print("foreign filers (6-K, not yet fetched): " + ", ".join(f"{k} {v}" for k, v in six.items()))
    L = ["# AI-chain results releases — when they reach the SEC (New York time)", "", f"{len(E)} results filings (8-K Item 2.02) with a readable release, {E['ticker'].nunique()} companies, {E['accepted_ny'].min():%Y-%m-%d} → {E['accepted_ny'].max():%Y-%m-%d}. The time is the SEC's acceptance stamp; the same release can reach the news wires a few minutes earlier.", "", "| company | " + " | ".join(str(c) for c in tab.columns) + " |", "|---|" + "---|" * len(tab.columns)]
    for t, r in tab.iterrows(): L.append(f"| {t} | " + " | ".join(str(v) for v in r) + " |")
    if len(six): L += ["", "Foreign filers, 6-K (stage B): " + ", ".join(f"{k} {v}" for k, v in six.items()) + "."]
    (DOCS / "ai_earnings_times.md").write_text("\n".join(L) + "\n"); print("-> docs/ai_earnings_times.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["filings", "times"]); ap.add_argument("--limit", type=int, help="filings: only the most recent N per company (a quick trial)"); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    {"filings": lambda: cmd_filings(a.limit), "times": cmd_times}[a.cmd]()
