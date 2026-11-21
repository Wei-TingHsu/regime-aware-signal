"""events100.py -- ET-2: the announcement test widened from 12 companies to about 100 large US companies (founder, 21 Nov: 'widen, yes').

Why: ET-1 (docs/ai_event_types.md) had too few events per type -- 'guidance update' had 16. The same reader on the 8-K event filings of the S&P 100
companies gives several times more. What can and cannot be tested: minute prices for these companies are NOT on disk and paid data is banned, so the
price side is free DAILY open and close prices. The SEC's acceptance stamp is a real clock time, so a filing can be placed before the open, during the
session or after the close, and the pieces a user could trade at the open or the close can be separated from what was gone already. The first minutes
after a filing (where ET-1's near miss sat) cannot be tested this way.

    python -m src.events100 universe     # the company list -> processed/universe100.csv (the index fund's own holdings file; a fixed list if that is refused)
    python -m src.events100 filings      # each company's 8-K event filings since May 2018, with the SEC's time. Counts only. Free.
    python -m src.events100 texts        # download the text of each filing (and its press release). Free; long; can be stopped and run again.
    python -m src.events100 cost         # what the reading would cost, counted on the texts. Nothing is read.
    python -m src.events100 score --max-usd 20 [--press-only]     # Claude reads (reader ai-event-v2, the same prompt as ET-1, without a results baseline)
The price test is registered in TRACK before it is added. The twelve US companies of the founder's list are left out here: they are ET-1."""
from __future__ import annotations
import argparse, csv, io, json, os, re, time, urllib.request
from pathlib import Path
import pandas as pd
import src.ai_earnings as A

PROC = Path("processed"); ROOT = Path("data_provenance/events100"); TXT = ROOT / "docs"; READS = ROOT / "reads"; SINCE = "2018-05-01"
OEF = "https://www.ishares.com/us/products/239723/ishares-sp-100-etf/1467271812596.ajax?fileType=csv&fileName=OEF_holdings&dataType=fund"
FIXED = ("AAPL ABBV ABT ACN ADBE AIG AMD AMGN AMT AMZN AVGO AXP BA BAC BK BKNG BLK BMY BRK-B C CAT CHTR CL CMCSA COF COP COST CRM CSCO CVS CVX DE DHR DIS DUK EMR FDX GD GE GILD GM GOOG GS HD HON IBM INTC INTU ISRG JNJ JPM KO LIN LLY LMT "
         "LOW MA MCD MDLZ MDT MET META MMM MO MRK MS MSFT NEE NFLX NKE NOW NVDA ORCL PEP PFE PG PLTR PM PYPL QCOM RTX SBUX SCHW SO SPG T TGT TMO TMUS TSLA TXN UBER UNH UNP UPS USB V VZ WFC WMT XOM").split()
ET1 = set(A.LIST) | {"GOOGL", "FB"}      # already tested in ET-1 with a results baseline


def cmd_universe():
    src = "fixed list written by Claude from the S&P 100's membership as it knew it in mid-2026 (the index fund's holdings file could not be read)"; ticks = list(FIXED)
    try:
        raw = urllib.request.urlopen(urllib.request.Request(OEF, headers={"User-Agent": "Mozilla/5.0"}), timeout=25).read().decode("utf-8-sig", "ignore"); i = raw.find("Ticker,")
        rows = list(csv.DictReader(io.StringIO(raw[i:]))) if i != -1 else []; got = [r["Ticker"].strip().upper().replace(".", "-").replace("BRKB", "BRK-B") for r in rows if r.get("Asset Class", "").strip() == "Equity" and re.fullmatch(r"[A-Za-z.\-]{1,6}", r.get("Ticker", "").strip() or "")]
        if len(got) >= 90: ticks = sorted(set(got)); src = f"iShares S&P 100 ETF holdings file, read {pd.Timestamp.now():%Y-%m-%d}"; extra = sorted(set(ticks) - set(FIXED)); gone = sorted(set(FIXED) - set(ticks)); print(f"  holdings file read: {len(ticks)} equities. Not on Claude's fixed list: {extra or 'none'}. On the fixed list but not in the file: {gone or 'none'}.")
        else: print(f"  the holdings file answered but gave {len(got)} equities -- the fixed list is used")
    except Exception as e: print(f"  the holdings file could not be read ({type(e).__name__}) -- the fixed list is used")
    FS = A._sec(); cmap = json.loads(FS.get(FS.TICKERS)); look = {v["ticker"].upper(): (str(v["cik_str"]).zfill(10), v.get("title", "")) for v in cmap.values()}; rows = []; miss = []
    for t in ticks:
        if t in ("GOOGL",): continue
        if t in look: rows.append(dict(ticker=t, cik=look[t][0], name=look[t][1], in_et1=t in ET1))
        else: miss.append(t)
    U = pd.DataFrame(rows); PROC.mkdir(exist_ok=True); U.to_csv(PROC / "universe100.csv", index=False); ROOT.mkdir(parents=True, exist_ok=True); U.to_csv(ROOT / "universe100.csv", index=False)
    print(f"{len(U)} companies ({int((~U.in_et1).sum())} new, {int(U.in_et1.sum())} already in ET-1). Source: {src}. Not found in the SEC's ticker file: {miss or 'none'}. NOTE: this is TODAY's list applied to past years -- companies that shrank or disappeared since 2018 are missing. -> processed/universe100.csv")
    (PROC / "universe100_source.txt").write_text(src + "\n")


def cmd_filings(since: str):
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set")
    FS = A._sec(); U = pd.read_csv(PROC / "universe100.csv", dtype=str); U = U[U.in_et1 != "True"]; rows = []; bad = []
    for r in U.itertuples():
        try: F, _ = A._all_filings(FS, r.cik)
        except Exception as e: bad.append(r.ticker); print(f"  {r.ticker}: filing list FAILED ({type(e).__name__})"); continue
        F = F[F["filing_date"] >= since]; items = F["items"].fillna(""); k = F[(F.form.str.upper() == "8-K") & ~items.str.contains("2.02", regex=False) & items.apply(lambda x: any(i.strip() in A.KEEP_ITEMS for i in x.split(",")))]
        rows += [dict(ticker=r.ticker, cik=r.cik, form=x.form, items=x.items, filing_date=x.filing_date, accepted_raw=x.accepted_raw, accession=x.accession, primary=x.primary) for x in k.itertuples()]; time.sleep(0.15)
    M = pd.DataFrame(rows); M["accepted_ny"] = A._ny(M["accepted_raw"]); M = M.sort_values(["ticker", "accepted_ny"]); M.to_csv(PROC / "events100_filings.csv", index=False); ROOT.mkdir(parents=True, exist_ok=True); M.to_csv(ROOT / "filings.csv", index=False)      # the second copy is the one that is pushed (processed/ is not)
    it = pd.Series([i.strip() for x in M["items"].astype(str) for i in x.split(",") if i.strip() in A.KEEP_ITEMS]).value_counts(); hm = M.accepted_ny.dt.hour * 60 + M.accepted_ny.dt.minute; wk = M.accepted_ny.dt.dayofweek >= 5
    print(f"{len(M)} event filings (8-K without results) of {M.ticker.nunique()} companies since {since}" + (f"; failed: {bad}" if bad else "") + ". Per year: " + ", ".join(f"{y} {n}" for y, n in M.groupby(M.accepted_ny.dt.year).size().items()))
    print("By item: " + "; ".join(f"{A.KEEP_ITEMS[k_]} {v}" for k_, v in it.items()))
    print(f"When the SEC accepted them (New York): before the open {int((~wk & (hm < 570)).sum())}, during the session {int((~wk & (hm >= 570) & (hm < 960)).sum())}, after the close {int((~wk & (hm >= 960)).sum())}, weekend {int(wk.sum())}. No text was downloaded and no price was used. -> processed/events100_filings.csv")


def cmd_texts(limit: int | None):
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set")
    FS = A._sec(); TXT.mkdir(parents=True, exist_ok=True); M = pd.read_csv(PROC / "events100_filings.csv", dtype=str); n_new = n_short = n_fail = 0; t0 = time.time(); meta = ROOT / "texts.csv"
    done = {r["accession"]: r for r in csv.DictReader(meta.open())} if meta.exists() else {}; todo = [r for r in M.itertuples() if r.accession not in done]; todo = todo if limit is None else todo[:limit]
    print(f"{len(M)} filings; {len(done)} texts already on disk; {len(todo)} to download now (about {len(todo) * 0.6 / 60:.0f} minutes). It can be stopped with Ctrl-C and run again: it continues where it stopped.")
    with meta.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["accession", "ticker", "words", "press", "file"])
        if not done: w.writeheader()
        for k, r in enumerate(todo, 1):
            accn = r.accession.replace("-", ""); f = TXT / f"{r.ticker}_{accn}.txt"; press = 0; body = ""
            try:
                body = FS.clean(FS.get(FS.ARCH.format(cik=str(int(r.cik)), acc=accn, doc=r.primary))) if isinstance(r.primary, str) and r.primary else ""; time.sleep(0.12)
                names = [i.get("name", "") for i in json.loads(FS.get(f"https://www.sec.gov/Archives/edgar/data/{int(r.cik)}/{accn}/index.json"))["directory"]["item"]]; time.sleep(0.12)
                for nme in [x for x in names if x != r.primary and x.lower().endswith((".htm", ".html", ".txt")) and re.search(r"ex-?_?99|press|release|exhibit99|ex99", x.lower())][:2]:
                    try: body += "\n\n[EXHIBIT]\n" + FS.clean(FS.get(FS.ARCH.format(cik=str(int(r.cik)), acc=accn, doc=nme))); press = 1
                    except Exception: pass
                    time.sleep(0.12)
            except KeyboardInterrupt: raise
            except Exception: n_fail += 1; continue
            words = len(body.split())
            if words < 80: n_short += 1; w.writerow(dict(accession=r.accession, ticker=r.ticker, words=words, press=press, file="")); continue
            f.write_text(f"[{r.ticker} {r.form} items: {r.items or 'n/a'}]\n\n{body}"); w.writerow(dict(accession=r.accession, ticker=r.ticker, words=words, press=press, file=str(f))); n_new += 1
            if k % 250 == 0: fh.flush(); print(f"  {k} of {len(todo)} ({(time.time() - t0) / 60:.0f} min)")
    print(f"done: {n_new} texts downloaded now, {n_short} too short to read, {n_fail} failed (run again to retry). No cost. -> {TXT}")


def _rows(press_only=False):
    M = pd.read_csv(PROC / "events100_filings.csv", parse_dates=["accepted_ny"], dtype={"accession": str}); X = pd.read_csv(ROOT / "texts.csv", dtype={"accession": str}); X = X[X.file.notna() & (X.file != "")]
    D = M.merge(X[["accession", "words", "press", "file"]], on="accession"); return D[D.press.astype(int) == 1] if press_only else D


def cmd_cost():
    for lab, po in (("ALL event filings with a text", False), ("only those that carry a press release", True)):
        D = _rows(po); todo = [r for r in D.itertuples() if not (READS / f"{Path(r.file).stem}__{A.PV2}.json").exists()]
        tin = sum(len(A._release_body(r.file, A.CHARS2)) / A._TOK + 1100 for r in todo); lo = tin / 1e6 * A.IN_RATE + len(todo) * A.OUT2 / 1e6 * A.OUT_RATE; hi = tin / 1e6 * A.IN_RATE + len(todo) * 2 * A.OUT2 / 1e6 * A.OUT_RATE
        print(f"  {lab}: {len(D)} filings, {len(todo)} still to read: between about US${lo:.2f} and US${hi:.2f} (the lower figure uses the answer length measured on ET-1's events; the upper doubles it).")
    print("Nothing was read.")


def cmd_score(max_usd: float, press_only: bool):
    from src.news_events2 import _client
    client = _client(); A.READS = READS; READS.mkdir(parents=True, exist_ok=True); D = _rows(press_only).sort_values("accepted_ny", ascending=False); tin = tout = n = bad = 0; cost = lambda: tin / 1e6 * A.IN_RATE + tout / 1e6 * A.OUT_RATE
    for r in D.itertuples():
        stem = Path(r.file).stem
        if (READS / f"{stem}__{A.PV2}.json").exists(): continue
        d, a, b = A._ask2(client, A.SYS2, f"BASELINE: No scored results release is on file before this event.\n\nEVENT ({r.ticker}, filed {str(r.accepted_ny)[:16]} New York; 8-K items {r.items}):\n{A._release_body(r.file, A.CHARS2)}", stem, A.PV2); tin += a; tout += b
        if d is None: bad += 1
        else: n += 1
        if n and n % 100 == 0: print(f"  {n} read, about US${cost():.2f}")
        if cost() >= max_usd: print(f"  cap US${max_usd:.2f} reached after {n} filings; run again to continue"); break
    left = sum(1 for r in D.itertuples() if not (READS / f"{Path(r.file).stem}__{A.PV2}.json").exists()); rows = []
    for r in _rows(False).itertuples():
        f = READS / f"{Path(r.file).stem}__{A.PV2}.json"
        if f.exists(): d = json.loads(f.read_text()); rows.append(dict(ticker=r.ticker, accepted_ny=r.accepted_ny, accession=r.accession, items=r.items, press=r.press, **{k: d.get(k) for k in ("event_type", "material", "fcf_outlook", "uncertainty", "own_stock", "market")}))
    if rows: S = pd.DataFrame(rows); S.to_csv(PROC / "events100_scores.csv", index=False); S.to_csv(ROOT / "scores.csv", index=False); m = pd.to_numeric(S.material, errors="coerce"); print(f"scores on file: {len(S)}; material 0.2 or more: {int((m >= 0.2).sum())}; by type (material 0.2+): " + ", ".join(f"{k} {v}" for k, v in S[m >= 0.2].event_type.value_counts().items()))
    print(f"done: {n} read now, {bad} failed now, {left} still unread, about US${cost():.2f} -> processed/events100_scores.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["universe", "filings", "texts", "cost", "score"]); ap.add_argument("--since", default=SINCE); ap.add_argument("--limit", type=int); ap.add_argument("--max-usd", type=float, default=20.0); ap.add_argument("--press-only", action="store_true"); a = ap.parse_args()
    {"universe": cmd_universe, "filings": lambda: cmd_filings(a.since), "texts": lambda: cmd_texts(a.limit), "cost": cmd_cost, "score": lambda: cmd_score(a.max_usd, a.press_only)}[a.cmd]()
