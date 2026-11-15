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


# ------------------------------------------------------------------------------------------------ type 2: other company events
# Founder, 15 Nov: besides results releases, score the OTHER news about each company. Primary source with an exact time: the company's own 8-K filings
# under the items below (a US company must file one within four business days of a material event), and the foreign filers' 6-Ks that are not results.
KEEP_ITEMS = {"1.01": "material agreement", "1.02": "agreement terminated", "1.03": "bankruptcy", "1.05": "cybersecurity incident", "2.01": "acquisition or disposal completed", "2.03": "new debt or obligation",
              "2.04": "obligation accelerated", "2.05": "restructuring / exit costs", "2.06": "impairment", "3.01": "listing notice", "4.01": "auditor change", "4.02": "earlier statements not reliable",
              "5.01": "change of control", "5.02": "director or officer leaves / is appointed", "7.01": "disclosure to all investors", "8.01": "other event"}
EVT = ROOT / "events"


def _ny(raw: pd.Series) -> pd.Series:      # the SEC's stamps are UTC (established on the results filings: they cluster at 20h and 21h, i.e. 16:00 New York)
    return pd.to_datetime(raw.astype(str).str.replace("Z", "", regex=False), errors="coerce").dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)


def cmd_events8k(limit: int | None, since: str):
    import os, re
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set")
    FS = _sec(); EVT.mkdir(parents=True, exist_ok=True); cmap = json.loads(FS.get(FS.TICKERS)); lookup = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}; rows = []
    known = pd.read_csv(PROC / "ai_earnings_filings.csv", dtype=str) if (PROC / "ai_earnings_filings.csv").exists() else pd.DataFrame(columns=["accession", "kind"]); is_res = set(known[known.get("kind", "").isin(["results", "monthly"])]["accession"]) if len(known) else set()
    for t in LIST:
        tick = next((a for a in ALIAS.get(t, [t]) if a in lookup), None)
        if tick is None: print(f"  {t}: not in the SEC's ticker file -- skipped"); continue
        cik = lookup[tick]
        try: F, name = _all_filings(FS, cik)
        except Exception as e: print(f"  {t}: submissions FAILED: {e}"); continue
        F = F[F["filing_date"] >= since]; form = F.form.str.upper(); items = F["items"].fillna("")
        k8 = F[(form == "8-K") & ~items.str.contains("2.02", regex=False) & items.apply(lambda x: any(i.strip() in KEEP_ITEMS for i in x.split(",")))]; k6 = F[(form == "6-K") & ~F["accession"].isin(is_res)]
        todo = pd.concat([k8, k6]).sort_values("filing_date", ascending=False); todo = todo if limit is None else todo.head(limit); n_new = n_short = 0
        for r in todo.itertuples():
            accn = r.accession.replace("-", ""); f = EVT / f"{t}_{accn}.txt"
            if not f.exists():
                try: body = FS.clean(FS.get(FS.ARCH.format(cik=str(int(cik)), acc=accn, doc=r.primary))) if r.primary else ""
                except Exception: body = ""
                time.sleep(0.12)
                try:
                    names = [i.get("name", "") for i in json.loads(FS.get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn}/index.json"))["directory"]["item"]]
                    for nme in [x for x in names if x != r.primary and x.lower().endswith((".htm", ".html", ".txt")) and re.search(r"ex-?_?99|press|release|exhibit99|ex99", x.lower())][:2]:
                        try: body += "\n\n[EXHIBIT]\n" + FS.clean(FS.get(FS.ARCH.format(cik=str(int(cik)), acc=accn, doc=nme)))
                        except Exception: pass
                        time.sleep(0.12)
                except Exception: pass
                time.sleep(0.12)
                if len(body.split()) < 80: n_short += 1; continue
                f.write_text(f"[{t} {r.form} items: {r.items or 'n/a'}]\n\n{body}"); n_new += 1
            rows.append(dict(ticker=t, form=r.form, items=r.items, filing_date=r.filing_date, accepted_raw=r.accepted_raw, accession=r.accession, words=len(f.read_text().split()), file=str(f)))
        print(f"  {t:5} {name[:30]:30}: {len(k8)} event filings (8-K) + {len(k6)} other 6-K since {since}; {n_new} texts fetched now, {n_short} too short to read")
    M = pd.DataFrame(rows)
    if M.empty: print("nothing found"); return
    old = PROC / "ai_events_filings.csv"
    if old.exists(): M = pd.concat([pd.read_csv(old, dtype=str), M.astype(str)]).drop_duplicates("accession", keep="last")
    M["accepted_ny"] = _ny(M["accepted_raw"]); M = M.sort_values(["ticker", "accepted_ny"]); M.to_csv(old, index=False)
    it = pd.Series([i.strip() for x in M["items"].fillna("").astype(str) for i in x.split(",") if i.strip() in KEEP_ITEMS]).value_counts()
    print(f"-> processed/ai_events_filings.csv: {len(M)} event filings with text, {M['ticker'].nunique()} companies. By item: " + "; ".join(f"{KEEP_ITEMS[k]} {v}" for k, v in it.items()))


# ------------------------------------------------------------------------------------------------ the reader (two prompts)
PV1, PV2 = "ai-earn-v3-2026-11-15", "ai-event-v2-2026-11-15"; READS = ROOT / "reads"; CHARS1, CHARS2, TABLES = 12000, 8000, 9000;      # v3 / v2 after the 15 Nov trial: the cash-flow tables sat beyond the text sent, and one answer was cut short
_TOK = 3.2; OUT1, OUT2 = 1200, 650      # characters per token and answer lengths, set from the trial's bill
IN_RATE, OUT_RATE = 2.0, 10.0
_NAMES = "AMD, NVDA, MU, INTC, AVGO, SNDK, SKHY, ORCL, TSM, CRWD, GOOG, META, AMZN, MSFT"
SYS1 = f"""You are given a company's results release as filed, and (when available) the guidance the same company gave in its PREVIOUS release.
Score the release by comparing what is reported with that prior guidance and with what the text itself says was expected, and by the guidance it gives for
the coming period. Judge from these texts only; do not use anything you know about how markets reacted. Return STRICT JSON, no preamble:
{{"facts": {{"period": the fiscal period reported, "revenue": as stated with units, "operating_income": ..., "net_income": ..., "eps": ..., "operating_cash_flow": ...,
   "capex": ..., "free_cash_flow": as stated or operating cash flow minus capex if both are given, "cash_and_investments": ..., "total_debt": ...,
   "guidance_next": the guidance given for the next period, in the release's own words and numbers}}   (use null for anything the text does not give),
 "results_vs_prior_guidance": -1..+1 (reported results against the prior guidance or stated expectation; 0 if there is no basis),
 "guidance_change": -1..+1 (the new guidance against the current level and against what the prior guidance implied; 0 if none is given),
 "fcf_trend": -1..+1 (direction of free cash flow and of the balance sheet's strength in this release),
 "own_stock": -1..+1 (what the release means for the company's own share price over the next few sessions),
 "market": -1..+1 (what it means for large US technology shares as a group; 0 if it says little beyond this company),
 "ai_demand": -1..+1 (what it says about demand for AI computing: chips, memory, data centres, cloud capacity, AI software; 0 if not addressed),
 "affected": [up to five OTHER companies this release bears on -- competitors, suppliers, customers; use these tickers where they apply: {_NAMES}; each
   {{"company": ticker or name, "relation": "competitor" | "supplier" | "customer" | "peer", "direction": -1..+1, "reason": a few words}}],
 "evidence": one quoted clause that best supports own_stock}}"""
SYS2 = f"""You are given (1) a BASELINE: the company's most recent reported financials and guidance before this event, and (2) the text of an EVENT the
company filed (not a results release): for example a change of chief executive, an acquisition, a large contract, a financing, a restructuring, a legal or
regulatory matter, a monthly revenue figure. Score what the event changes relative to the baseline: its effect on future free cash flow, on the guidance,
and on how UNCERTAIN those are -- investors dislike uncertainty, so an event that makes future cash flows or governance less predictable is negative for
the share even when its direct cost is small. Then consider who else is affected: a problem at one company can be an opening for its competitors, and
reaches its suppliers and customers. Judge from the two texts only; do not use anything you know about how markets reacted. Return STRICT JSON, no preamble:
{{"event_type": one of "leadership change", "acquisition or disposal", "contract or partnership", "financing or capital return", "restructuring", "legal or regulatory",
   "product or technology", "guidance update", "monthly revenue", "cyber incident", "accounting", "routine or administrative", "other",
 "material": 0..1 (how much this matters against the size of the baseline; routine filings near 0),
 "fcf_outlook": -1..+1 (change in expected future free cash flow against the baseline),
 "uncertainty": -1..+1 (+1 = makes future cash flows, guidance or governance clearly LESS predictable; -1 = removes an uncertainty),
 "own_stock": -1..+1 (what the event means for the company's own share price over the next few sessions),
 "market": -1..+1 (for large US technology shares as a group; 0 if it concerns only this company),
 "affected": [up to six OTHER companies -- use these tickers where they apply: {_NAMES}; each {{"company": ticker or name, "relation": "competitor" | "supplier" | "customer" | "peer",
   "direction": -1..+1, "reason": a few words}}],
 "evidence": one quoted clause that best supports own_stock}}"""


def _ask2(client, system: str, body: str, stem: str, pv: str):
    from src.news_events2 import MODEL, _parse, is_fatal
    READS.mkdir(parents=True, exist_ok=True); out = READS / f"{stem}__{pv}.json"
    if out.exists(): return json.loads(out.read_text()), 0, 0
    try:
        r = client.messages.create(model=MODEL, max_tokens=2500, system=system, messages=[{"role": "user", "content": body}]); t = "".join(b.text for b in r.content if b.type == "text"); tin, tout = r.usage.input_tokens, r.usage.output_tokens
        try: d = _parse(t)
        except json.JSONDecodeError:
            r2 = client.messages.create(model=MODEL, max_tokens=2500, system=system, messages=[{"role": "user", "content": body}, {"role": "assistant", "content": t or "(empty)"}, {"role": "user", "content": "That was not valid JSON. Reply with the JSON object only."}])
            t2 = "".join(b.text for b in r2.content if b.type == "text"); tin += r2.usage.input_tokens; tout += r2.usage.output_tokens
            try: d = _parse(t2)
            except json.JSONDecodeError: (READS / f"{stem}__{pv}.failed.txt").write_text(t + "\n----\n" + t2); return None, tin, tout
        d["_model"] = MODEL; d["_prompt_version"] = pv; tmp = out.with_suffix(".tmp"); tmp.write_text(json.dumps(d, indent=1)); tmp.replace(out); return d, tin, tout
    except Exception as e:
        if is_fatal(e): print("!" * 60 + f"\nFATAL -- {type(e).__name__}: {e}\nnothing retried; finished reads kept\n" + "!" * 60); raise SystemExit(1)
        print(f"    {stem}: {type(e).__name__}: {str(e)[:100]}"); return None, 0, 0


def _release_body(path: str, cap: int, tables: int = 0) -> str:
    import re
    body = Path(path).read_text(); body = body.split("\n\n", 1)[1] if body.startswith("[") and "\n\n" in body else body       # the bracketed header is ours
    m = re.search(RX_RESULTS + "|" + RX_MONTHLY, body, re.I)
    if m and m.start() > 1500: body = body[max(0, m.start() - 300):]          # some filings open with pages of cover text or submission header; start at the release
    head = body[:cap]
    if tables and len(body) > cap:      # the balance sheet and the cash-flow statement usually sit AFTER the first pages: send that part too
        hits = [m.start() for m in re.finditer(r"total\s+(current\s+)?assets|operating\s+activities|free\s+cash\s+flow", body[cap:], re.I)]
        if hits: a = cap + max(0, hits[0] - 1500); head += "\n\n[LATER IN THE SAME RELEASE: FINANCIAL STATEMENTS]\n" + body[a:a + tables]
    return head


def _results() -> pd.DataFrame:
    M = pd.read_csv(PROC / "ai_earnings_filings.csv", parse_dates=["accepted_ny"]); M["kind"] = M["kind"].fillna("") if "kind" in M.columns else ""
    M.loc[(M.form == "8-K") & (M["kind"] == ""), "kind"] = "results"; M["words"] = pd.to_numeric(M["words"], errors="coerce").fillna(0)
    return M[(M.words > 0) & M["kind"].isin(["results", "monthly"]) & M["file"].notna()].sort_values(["ticker", "accepted_ny"]).reset_index(drop=True)


def _event_rows() -> pd.DataFrame:
    R = _results(); mon = R[R.kind == "monthly"][["ticker", "form", "accepted_ny", "accession", "file"]].assign(items="monthly revenue"); p = PROC / "ai_events_filings.csv"
    E = pd.read_csv(p, parse_dates=["accepted_ny"])[["ticker", "form", "accepted_ny", "accession", "file", "items"]] if p.exists() else pd.DataFrame(columns=mon.columns)
    return pd.concat([E, mon], ignore_index=True).sort_values(["ticker", "accepted_ny"]).reset_index(drop=True)


def _read1(file: str):
    f = READS / f"{Path(file).stem}__{PV1}.json"; return json.loads(f.read_text()) if f.exists() else None


def _baseline(R: pd.DataFrame, ticker: str, when) -> str:
    g = R[(R.ticker == ticker) & (R.kind == "results") & (R.accepted_ny < when)]
    for r in g.iloc[::-1].itertuples():
        d = _read1(r.file)
        if d:
            fx = d.get("facts") or {}; return (f"Most recent results before this event (filed {str(r.accepted_ny)[:10]}), period {fx.get('period')}: revenue {fx.get('revenue')}; operating income {fx.get('operating_income')}; net income {fx.get('net_income')}; "
                f"operating cash flow {fx.get('operating_cash_flow')}; capital spending {fx.get('capex')}; free cash flow {fx.get('free_cash_flow')}; cash and investments {fx.get('cash_and_investments')}; debt {fx.get('total_debt')}. "
                f"Guidance then given: {fx.get('guidance_next')}. That release against its prior guidance: {d.get('results_vs_prior_guidance')}; outlook change: {d.get('guidance_change')}; free-cash-flow trend: {d.get('fcf_trend')}.")
    return "No scored results release is on file before this event."


def cmd_cost():
    R = _results(); res = R[R.kind == "results"]; E = _event_rows(); t1 = [r for r in res.itertuples() if _read1(r.file) is None]; t2 = [r for r in E.itertuples() if not (READS / f"{Path(r.file).stem}__{PV2}.json").exists()]
    u1 = sum(len(_release_body(r.file, CHARS1, TABLES)) / _TOK + 900 for r in t1) / 1e6 * IN_RATE + len(t1) * OUT1 / 1e6 * OUT_RATE; u2 = sum(len(_release_body(r.file, CHARS2)) / _TOK + 1100 for r in t2) / 1e6 * IN_RATE + len(t2) * OUT2 / 1e6 * OUT_RATE
    yr = pd.to_datetime(E["accepted_ny"]).dt.year; print(f"results releases: {len(res)} ({len(t1)} to score, about US${u1:.2f}).  other events incl. monthly revenue: {len(E)} ({len(t2)} to score, about US${u2:.2f}; from 2018 only: {int((yr >= 2018).sum())} events).  Total about US${u1 + u2:.2f}. Counted on disk.")


def cmd_score(limit: int | None, max_usd: float, only: str, since: str):
    from src.news_events2 import _client
    R = _results(); res = R[R.kind == "results"]; client = _client(); tin = tout = 0; usd = 0.0; cost = lambda: tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
    if only in ("all", "results"):
        todo = [r for r in res.itertuples() if _read1(r.file) is None]
        if limit: todo = [r for t_ in dict.fromkeys(x.ticker for x in todo) for r in [x for x in todo if x.ticker == t_][-2:]][:limit]      # a trial: the last two releases of each company, so the second one sees the first one's guidance
        print(f"results releases: scoring {len(todo)} under {PV1} (in date order within each company, so each sees the guidance of the one before); cap US${max_usd:.2f}")
        for k, r in enumerate(todo):
            prev = res[(res.ticker == r.ticker) & (res.accepted_ny < r.accepted_ny)]; pg = None
            for q in prev.iloc[::-1].itertuples():
                d0 = _read1(q.file)
                if d0: pg = (d0.get("facts") or {}).get("guidance_next"); break
            body = f"PRIOR GUIDANCE (from the company's previous release): {pg or 'none available'}\n\nRELEASE:\n{_release_body(r.file, CHARS1, TABLES)}"; d, a, b = _ask2(client, SYS1, body, Path(r.file).stem, PV1); tin += a; tout += b; usd = cost()
            if limit and d: fx = d.get("facts") or {}; print(f"  {r.ticker:5} {str(r.accepted_ny)[:10]} vs prior guidance {d.get('results_vs_prior_guidance')!s:>5} outlook {d.get('guidance_change')!s:>5} FCF {d.get('fcf_trend')!s:>5} own {d.get('own_stock')!s:>5} market {d.get('market')!s:>5} AI {d.get('ai_demand')!s:>5} | revenue {str(fx.get('revenue'))[:22]}; FCF {str(fx.get('free_cash_flow'))[:22]}; affects {[(x.get('company'), x.get('direction')) for x in (d.get('affected') or [])][:4]}")
            elif (k + 1) % 50 == 0: print(f"  {k + 1}/{len(todo)}  ~US${usd:.2f}")
            if usd >= max_usd: print(f"  cap reached after {k + 1} reads (~US${usd:.2f}); rerun to continue"); break
    if only in ("all", "events") and usd < max_usd:
        E = _event_rows(); E = E[pd.to_datetime(E["accepted_ny"]) >= since]; todo = [r for r in E.itertuples() if not (READS / f"{Path(r.file).stem}__{PV2}.json").exists()]
        if limit: todo = todo[:: max(1, len(todo) // limit)][:limit]
        print(f"other events: scoring {len(todo)} under {PV2}, each against the company's latest results before it; cap US${max_usd:.2f}")
        for k, r in enumerate(todo):
            body = f"BASELINE: {_baseline(R, r.ticker, r.accepted_ny)}\n\nEVENT ({r.ticker}, filing items: {r.items}):\n{_release_body(r.file, CHARS2)}"; d, a, b = _ask2(client, SYS2, body, Path(r.file).stem, PV2); tin += a; tout += b; usd = cost()
            if limit and d: print(f"  {r.ticker:5} {str(r.accepted_ny)[:10]} [{str(d.get('event_type'))[:24]:24}] material {d.get('material')!s:>4} FCF {d.get('fcf_outlook')!s:>5} uncertainty {d.get('uncertainty')!s:>5} own {d.get('own_stock')!s:>5} | affects {[(x.get('company'), x.get('direction')) for x in (d.get('affected') or [])][:4]} | {str(d.get('evidence'))[:90]}")
            elif (k + 1) % 100 == 0: print(f"  {k + 1}/{len(todo)}  ~US${usd:.2f}")
            if usd >= max_usd: print(f"  cap reached after {k + 1} reads (~US${usd:.2f}); rerun to continue"); break
    print(f"done: ~US${cost():.2f}"); rows = []
    for r in res.itertuples():
        d = _read1(r.file)
        if d: rows.append(dict(ticker=r.ticker, accepted_ny=r.accepted_ny, accession=r.accession, **{k_: d.get(k_) for k_ in ("results_vs_prior_guidance", "guidance_change", "fcf_trend", "own_stock", "market", "ai_demand")}, affected=json.dumps(d.get("affected")), facts=json.dumps(d.get("facts"))))
    pd.DataFrame(rows).to_csv(PROC / "ai_earnings_scores.csv", index=False); rows2 = []
    for r in _event_rows().itertuples():
        f = READS / f"{Path(r.file).stem}__{PV2}.json"
        if f.exists(): d = json.loads(f.read_text()); rows2.append(dict(ticker=r.ticker, accepted_ny=r.accepted_ny, accession=r.accession, items=r.items, **{k_: d.get(k_) for k_ in ("event_type", "material", "fcf_outlook", "uncertainty", "own_stock", "market")}, affected=json.dumps(d.get("affected"))))
    pd.DataFrame(rows2).to_csv(PROC / "ai_events_scores.csv", index=False); print(f"-> processed/ai_earnings_scores.csv ({len(rows)} results scored), processed/ai_events_scores.csv ({len(rows2)} events scored)")


def cmd_summary():
    """What the two sets of scores look like, before any price is touched: how many, how they spread, when in the day they arrive. Printed and written to docs/."""
    out = []; P = lambda x="": (print(x), out.append(x))
    R = _results(); res = R[R.kind == "results"]; S = pd.read_csv(PROC / "ai_earnings_scores.csv", parse_dates=["accepted_ny"]); E = pd.read_csv(PROC / "ai_events_scores.csv", parse_dates=["accepted_ny"])
    def bucket(t): m = t.hour * 60 + t.minute; return "weekend" if t.dayofweek >= 5 else ("before 09:30" if m < 570 else ("09:30-15:59" if m < 960 else ("16:00-16:59" if m < 1020 else "17:00 or later")))
    P("# AI-chain scores: summary (no prices used)"); P(); P(f"## Type 1: results releases, reader {PV1}"); P(f"- scored {len(S)} of {len(res)}; not scored: {sorted(set(res.accession) - set(S.accession))}")
    P("- per company: " + ", ".join(f"{k} {v}" for k, v in S.ticker.value_counts().sort_index().items())); P("- time of day (New York): " + ", ".join(f"{k} {v}" for k, v in S.accepted_ny.apply(bucket).value_counts().items()))
    fx = S["facts"].apply(lambda x: json.loads(x) if isinstance(x, str) else {}).apply(lambda d: d or {}); has = lambda k: fx.apply(lambda d: d.get(k) not in (None, "", "null")).mean()
    P(f"- facts found: revenue {has('revenue'):.0%}, operating cash flow {has('operating_cash_flow'):.0%}, capital spending {has('capex'):.0%}, free cash flow {has('free_cash_flow'):.0%}, cash {has('cash_and_investments'):.0%}, debt {has('total_debt'):.0%}, next guidance {has('guidance_next'):.0%}")
    P(); P("| score | mean | above 0 | exactly 0 | below 0 | at +/-0.9 or beyond |"); P("|---|---|---|---|---|---|")
    for c in ("results_vs_prior_guidance", "guidance_change", "fcf_trend", "own_stock", "market", "ai_demand"):
        x = pd.to_numeric(S[c], errors="coerce").dropna(); P(f"| {c} | {x.mean():+.2f} | {(x > 0).mean():.0%} | {(x == 0).mean():.0%} | {(x < 0).mean():.0%} | {(x.abs() >= 0.9).mean():.0%} |")
    P(); P("own_stock by company (mean; share below 0): " + ", ".join(f"{t} {pd.to_numeric(g.own_stock, errors='coerce').mean():+.2f}; {(pd.to_numeric(g.own_stock, errors='coerce') < 0).mean():.0%}" for t, g in S.groupby("ticker")))
    P(); P(f"## Type 2: other events, reader {PV2}"); P(f"- scored {len(E)}; from 2018: {(E.accepted_ny >= '2018-01-01').sum()}"); E["material"] = pd.to_numeric(E["material"], errors="coerce"); E["own_stock"] = pd.to_numeric(E["own_stock"], errors="coerce"); E["uncertainty"] = pd.to_numeric(E["uncertainty"], errors="coerce")
    P(f"- how material: below 0.2: {(E.material < 0.2).sum()}; 0.2 to 0.49: {((E.material >= 0.2) & (E.material < 0.5)).sum()}; 0.5 or more: {(E.material >= 0.5).sum()}")
    P(); P("| event type | all | material 0.3+ | of these: own stock above 0 | below 0 | mean uncertainty |"); P("|---|---|---|---|---|---|")
    for k, g in sorted(E.groupby("event_type"), key=lambda kv: -len(kv[1])):
        m = g[g.material >= 0.3]; P(f"| {k} | {len(g)} | {len(m)} | {(m.own_stock > 0).sum()} | {(m.own_stock < 0).sum()} | {m.uncertainty.mean():+.2f} |" if len(m) else f"| {k} | {len(g)} | 0 | - | - | - |")
    M = E[E.material >= 0.3]; P(); P(f"material 0.3+ ({len(M)} events): per company: " + ", ".join(f"{k} {v}" for k, v in M.ticker.value_counts().sort_index().items()))
    P("- time of day (New York): " + ", ".join(f"{k} {v}" for k, v in M.accepted_ny.apply(bucket).value_counts().items())); P(f"- from 2018: {(M.accepted_ny >= '2018-01-01').sum()}; own stock above 0: {(M.own_stock > 0).sum()}, exactly 0: {(M.own_stock == 0).sum()}, below 0: {(M.own_stock < 0).sum()}; uncertainty 0.3+: {(M.uncertainty >= 0.3).sum()}")
    P(); P("## Other companies named as affected (direction not 0)")
    for name, D in (("results", S), ("material events", M)):
        rows = [(str(a.get("company")).upper()[:12], float(a.get("direction") or 0), a.get("relation")) for x in D["affected"].dropna() for a in (json.loads(x) or []) if isinstance(a, dict)]; A = pd.DataFrame(rows, columns=["company", "direction", "relation"]); A = A[A.direction != 0]
        if len(A): top = A.groupby("company").direction.agg(["size", "mean"]).sort_values("size", ascending=False).head(16); P(f"- from {name}: {len(A)} mentions; by relation: { {k: int(v) for k, v in A.relation.value_counts().items()} }; most named (count; mean direction): " + ", ".join(f"{k} {int(v['size'])}; {v['mean']:+.2f}" for k, v in top.iterrows()))
    DOCS.mkdir(exist_ok=True); (DOCS / "ai_chain_scores_summary.md").write_text("\n".join(out) + "\n"); print("\n-> docs/ai_chain_scores_summary.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["filings", "filings6k", "events8k", "times", "cost", "score", "summary", "peek"]); ap.add_argument("--limit", type=int, help="only N items (a quick trial / a sample)"); ap.add_argument("--max-usd", type=float, default=15.0); ap.add_argument("--ticker", default="SKHY"); ap.add_argument("--only", choices=["all", "results", "events"], default="all"); ap.add_argument("--since", default=START, help="events8k / score: only events from this date"); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    {"filings": lambda: cmd_filings(a.limit), "filings6k": lambda: cmd_filings6k(a.limit), "times": cmd_times, "cost": cmd_cost, "events8k": lambda: cmd_events8k(a.limit, a.since), "score": lambda: cmd_score(a.limit, a.max_usd, a.only, a.since), "summary": cmd_summary, "peek": lambda: cmd_peek(a.ticker)}[a.cmd]()
