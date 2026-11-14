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
    if "kind" in have.columns:          # keep what an earlier `filings6k` run established for the foreign filers
        km = have.drop_duplicates("accession").set_index("accession"); six = (M["form"] == "6-K").to_numpy(); M["kind"] = M["accession"].map(km["kind"]).fillna("")
        w = pd.to_numeric(M["accession"].map(km["words"]), errors="coerce").fillna(0).to_numpy(); fl = M["accession"].map(km["file"]).fillna("").astype(str).to_numpy()
        M["words"] = [w[k] if six[k] else M["words"].iloc[k] for k in range(len(M))]; M["file"] = [fl[k] if six[k] else M["file"].iloc[k] for k in range(len(M))]
    else: M["kind"] = ""
    M = M.drop_duplicates("accession").sort_values(["ticker", "accepted_ny"]); M.to_csv(old, index=False); M["words"] = pd.to_numeric(M["words"], errors="coerce").fillna(0); ok = M[(M.form == "8-K") & (M.words > 0)]
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


# ------------------------------------------------------------------------------------------------ foreign filers (6-K): TSMC, SK Hynix
RX_RESULTS = r"(reports?|announces?)\s+[^.]{0,60}(quarter|quarterly|q[1-4])[^.]{0,60}(eps|results|earnings|profit)|(first|second|third|fourth)\s+quarter\s+(20\d\d\s+)?(eps|results|earnings)|earnings\s+release|business\s+results"
RX_MONTHLY = r"(monthly|net)\s+revenue\s+report|revenue\s+report\s+for\s+[a-z]+|reports?\s+[a-z]+\s+20\d\d\s+(net\s+)?revenue|[a-z]+\s+20\d\d\s+revenue\s+report"


def cmd_filings6k(limit: int | None):
    """6-K filings of the foreign filers: fetch each filing's main document, keep those that carry figures, and sort them by what the opening text says:
    'results' (a quarterly results release), 'monthly' (a monthly revenue report), 'other'. Prints the counts and a few opening lines of each kind so the
    sorting can be checked by eye before anything is scored. The SEC stamp of a 6-K can be HOURS after the release in Asia -- recorded as a limit."""
    import os, re
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set")
    FS = _sec(); TXT.mkdir(parents=True, exist_ok=True); M = pd.read_csv(PROC / "ai_earnings_filings.csv", dtype=str); six = M[M.form == "6-K"]; cmap = json.loads(FS.get(FS.TICKERS)); lookup = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}; args = SimpleNamespace(sleep=0.12, verbose_exhibits=False)
    M["kind"] = M.get("kind", pd.Series("", index=M.index)).fillna(""); M.loc[M.form == "8-K", "kind"] = "results"
    for t, g in six.groupby("ticker"):
        cik = lookup.get(t); g = g.sort_values("filing_date", ascending=False); g = g if limit is None else g.head(limit); n = {"results": 0, "monthly": 0, "other": 0, "no text": 0}; shown = {"results": 0, "monthly": 0}
        for r in g.itertuples():
            accn = r.accession.replace("-", ""); f = TXT / f"{t}_{accn}.txt"
            if f.exists(): body = f.read_text()
            else:
                try: body = FS.clean(FS.get(FS.ARCH.format(cik=str(int(cik)), acc=accn, doc=r.primary))) if r.primary else ""
                except Exception: body = ""
                time.sleep(0.12)
                if len(body.split()) < 120 or not FS.has_figures(body):
                    try: ex, names = FS.fetch_exhibits(cik, accn, r.primary, args, ticker=t)
                    except Exception: ex = ""
                    body = ex or body
            head = " ".join(body.split()[:400]).lower()
            kind = "no text" if (len(body.split()) < 120 or not FS.has_figures(body)) else ("monthly" if re.search(RX_MONTHLY, head) else ("results" if re.search(RX_RESULTS, head) else "other"))
            n[kind] += 1; M.loc[M.accession == r.accession, "kind"] = kind
            if kind in ("results", "monthly"):
                if not f.exists(): f.write_text(f"[{t} 6-K {kind}]\n\n{body}")
                M.loc[M.accession == r.accession, ["words", "file"]] = [str(len(body.split())), str(f)]
                if shown[kind] < 3: shown[kind] += 1; print(f"      {t} {r.filing_date} [{kind}]: {' '.join(body.split()[:28])[:170]}")
        print(f"  {t}: {len(g)} 6-K filings -> results {n['results']}, monthly revenue {n['monthly']}, other {n['other']}, no readable figures {n['no text']}")
    M.to_csv(PROC / "ai_earnings_filings.csv", index=False); print("-> processed/ai_earnings_filings.csv (column `kind`). Check the sample lines above: do the [results] lines look like quarterly results and the [monthly] lines like monthly revenue?")


def cmd_peek(ticker: str):
    """Shows what is inside a company's most recent filings (file names and sizes), to see why a release could not be read."""
    import os
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set")
    FS = _sec(); M = pd.read_csv(PROC / "ai_earnings_filings.csv", dtype=str); g = M[M.ticker == ticker.upper()].sort_values("filing_date", ascending=False).head(6); cmap = json.loads(FS.get(FS.TICKERS)); cik = next(str(v["cik_str"]) for v in cmap.values() if v["ticker"].upper() == ticker.upper())
    for r in g.itertuples():
        accn = r.accession.replace("-", "")
        try: items = json.loads(FS.get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn}/index.json"))["directory"]["item"]
        except Exception as e: print(f"  {r.filing_date} {r.accession}: index failed ({type(e).__name__})"); continue
        print(f"  {r.filing_date} {r.form} accepted {r.accepted_raw} primary={r.primary}: " + "; ".join(f"{i.get('name')} ({i.get('size', '?')})" for i in items)); time.sleep(0.15)


# ------------------------------------------------------------------------------------------------ the reader
PV = "ai-earn-v1-2026-11-15"; READS = ROOT / "reads"; CHARS = 15000; IN_RATE, OUT_RATE = 2.0, 10.0
SYS = """You are given the text of a company's results release (quarterly results, or a monthly revenue report), as filed. Judge it on its own text only:
compare what it reports with what the text itself says was guided or expected, and with the trend it describes. Do not use anything you know about how
markets reacted to it. Return STRICT JSON, no preamble:
{"own_stock": -1..+1 (what the release means for the company's own share price over the next few sessions; +1 clearly good, -1 clearly bad, 0 neutral or mixed),
 "market": -1..+1 (what it means for large US technology shares as a group -- does it change the picture for the wider chain of AI-related companies, or is it only about this company; 0 if it says little beyond the company),
 "ai_demand": -1..+1 (what it says about demand for AI computing: chips, data centres, cloud capacity, AI software; 0 if not addressed),
 "results_vs_guidance": -1, 0 or +1 (reported results against the company's own prior guidance or stated expectation; 0 if the text gives no basis),
 "guidance_change": -1..+1 (the outlook given for the coming period against the current level; 0 if no outlook is given),
 "drivers": [up to five, each {"item": name, "direction": "+" | "-", "size": "large" | "moderate" | "small"}],
 "evidence": one quoted clause that best supports own_stock}"""


def _events() -> pd.DataFrame:
    M = pd.read_csv(PROC / "ai_earnings_filings.csv", parse_dates=["accepted_ny"]); M["kind"] = M["kind"].fillna("") if "kind" in M.columns else ""
    M.loc[(M.form == "8-K") & (M["kind"] == ""), "kind"] = "results"; M["words"] = pd.to_numeric(M["words"], errors="coerce").fillna(0)
    return M[(M.words > 0) & M["kind"].isin(["results", "monthly"]) & M["file"].notna()].reset_index(drop=True)


def cmd_cost():
    E = _events(); todo = [r for r in E.itertuples() if not (READS / f"{Path(r.file).stem}__{PV}.json").exists()]
    tok = sum(min(len(Path(r.file).read_text()), CHARS) / 4 + 450 for r in todo); usd = tok / 1e6 * IN_RATE + len(todo) * 350 / 1e6 * OUT_RATE
    print(f"{len(E)} releases with text ({E.groupby('kind').size().to_dict()}); {len(todo)} not yet scored under {PV}; about US${usd:.2f}. Counted on disk.")


def cmd_score(limit: int | None, max_usd: float):
    from src.news_events2 import _client, _ask
    E = _events(); todo = [r for r in E.itertuples() if not (READS / f"{Path(r.file).stem}__{PV}.json").exists()]
    if limit: step = max(1, len(todo) // limit); todo = todo[::step][:limit]              # a sample spread over companies and years
    print(f"scoring {len(todo)} release(s) under {PV}; cap US${max_usd:.2f}"); client = _client(); tin = tout = 0
    for k, r in enumerate(todo):
        body = Path(r.file).read_text(); body = body.split("\n\n", 1)[1] if body.startswith("[") and "\n\n" in body else body       # the bracketed header is ours, not the company's
        import re as _re
        m_ = _re.search(RX_RESULTS + "|" + RX_MONTHLY, body, _re.I)
        if m_ and m_.start() > 1500: body = body[max(0, m_.start() - 300):]          # a foreign filing can open with pages of SEC submission header; start at the release itself
        d, a, b = _ask(client, SYS, f"RELEASE:\n{body[:CHARS]}", Path(r.file).stem, READS, PV); tin += a; tout += b; usd = tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
        if limit and d: print(f"  {r.ticker:5} {str(r.accepted_ny)[:16]}  own {d.get('own_stock')!s:>5}  market {d.get('market')!s:>5}  AI demand {d.get('ai_demand')!s:>5}  vs guidance {d.get('results_vs_guidance')!s:>3}  outlook {d.get('guidance_change')!s:>5}  | {str(d.get('evidence'))[:110]}")
        elif (k + 1) % 50 == 0: print(f"  {k + 1}/{len(todo)}  ~US${usd:.2f}")
        if usd >= max_usd: print(f"  cap reached after {k + 1} reads (~US${usd:.2f})"); break
    print(f"done: ~US${tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE:.2f}"); rows = []
    for r in E.itertuples():
        f = READS / f"{Path(r.file).stem}__{PV}.json"
        if f.exists():
            d = json.loads(f.read_text()); rows.append(dict(ticker=r.ticker, kind=r.kind, accepted_ny=r.accepted_ny, accession=r.accession, **{k_: d.get(k_) for k_ in ("own_stock", "market", "ai_demand", "results_vs_guidance", "guidance_change")}))
    pd.DataFrame(rows).to_csv(PROC / "ai_earnings_scores.csv", index=False); print(f"-> processed/ai_earnings_scores.csv ({len(rows)} scored)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["filings", "filings6k", "times", "cost", "score", "peek"]); ap.add_argument("--limit", type=int, help="only N items (a quick trial / a sample)"); ap.add_argument("--max-usd", type=float, default=15.0); ap.add_argument("--ticker", default="SKHY"); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    {"filings": lambda: cmd_filings(a.limit), "filings6k": lambda: cmd_filings6k(a.limit), "times": cmd_times, "cost": cmd_cost, "score": lambda: cmd_score(a.limit, a.max_usd), "peek": lambda: cmd_peek(a.ticker)}[a.cmd]()
