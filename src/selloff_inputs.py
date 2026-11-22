"""selloff_inputs.py -- sell-off study, stage D, step 1: the INPUT TABLES for the machine pattern search (TRACK 3.97). No outcome is computed here.

Founder (21 Nov 2026): the type and amount of data given to the machine matters; too many kinds in one table is noise, so several tables of
different length are built and the search runs inside each table and across pairs of tables. Free sources only.

    python -m src.selloff_inputs fetch      # new free data: more market series (Yahoo), stress series (FRED), each company's industry code and
                                            #   reported financials (SEC). Long (the SEC's financial files are large); it can be run again.
    python -m src.selloff_inputs fetch_insiders   # the SEC's quarterly insider-transaction data sets (large files)
    python -m src.selloff_inputs fetch_short      # FINRA's daily short-sale volume files (thousands of small files; an hour or more)
    python -m src.selloff_inputs tables     # builds the tables -> data_provenance/selloff/tables/, docs/selloff_tables.md

Tables (one row per sell-off of data_provenance/selloff/events.csv; a row is missing from a table when its inputs do not exist yet at that date):
  T1 the fall and the market   -- the 12 conditions of stage B                                              (stocks 2005+, funds 1999+)
  T2 who fell and who set it off -- sector, AI chain, own filing, peers, the sector's biggest faller        (stocks)
  T3 the company's condition   -- profitable, growth, debt, cash (as last REPORTED before the day), size, momentum, sensitivity to the market (stocks, about 2010+)
  T4 stress and other markets  -- credit spread, yield curve, financial conditions, VIX curve, rates, dollar, oil, gold, copper, banks, emerging markets, bitcoin
  T5 calendar                  -- weekday, month, month-end, quarter-end, option expiry, Fed meetings (2011+), results season
  T6 Claude's reading          -- for the scored AI-chain companies: the score of the latest results and of an event in the window (2018+, if the score files are on disk)
  T7 short selling             -- the share of the day's reported volume that was short sales, against its own 20-day average (FINRA's daily files, from 2009 where they exist)
  T8 insiders' trades          -- officers' and directors' open-market purchases and sales filed in the 90 days before (the SEC's data sets, from 2006)
"""
from __future__ import annotations
import argparse, io, json, os, time, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
from src.selloff_study import ROOT, DOCS, CHAIN, FEATS, CAUSE, _px, _stocks

EX = ROOT / "extra"; SEC = ROOT / "sec"; TB = ROOT / "tables"
YAHOO = {"^VIX3M": "three-month VIX", "^VIX9D": "nine-day VIX", "^VVIX": "volatility of the VIX", "^SKEW": "SKEW index", "^TNX": "10-year yield", "^IRX": "3-month yield", "DX-Y.NYB": "dollar index", "CL=F": "oil", "GC=F": "gold", "HG=F": "copper",
         "HYG": "high-yield bond fund", "LQD": "investment-grade bond fund", "TLT": "long Treasury fund", "EEM": "emerging-market shares", "KRE": "regional banks", "BTC-USD": "bitcoin", "IWM": "small companies", "IVE": "value shares", "IVW": "growth shares", "RSP": "the equal-weight S&P 500"}
FRED = {"BAMLH0A0HYM2": ("high-yield credit spread", 1), "T10Y2Y": ("10-year minus 2-year yield", 1), "NFCI": ("Chicago Fed financial conditions index", 6), "DGS2": ("2-year yield", 1), "T10YIE": ("10-year expected inflation", 1), "USEPUINDXD": ("news-based policy uncertainty index", 1), "STLFSI4": ("St. Louis Fed financial stress index", 6), "ICSA": ("new jobless claims", 6), "DFF": ("Fed funds rate", 1)}      # (name, sessions of delay before it is public)
CONCEPTS = {"rev": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"], "ni": ["NetIncomeLoss"], "assets": ["Assets"], "liab": ["Liabilities"], "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]}
SECTOR_FUND = {"semiconductors": "XLK", "software and internet": "XLK", "computers and equipment": "XLK", "banks and finance": "XLF", "payments and business services": "XLF", "insurance and health insurers": "XLF", "real estate": "XLRE", "drugs and biotech": "XLV", "medical devices and services": "XLV",
               "energy": "XLE", "utilities": "XLU", "telecom and media": "XLC", "consumer staples": "XLP", "retail and consumer": "XLY", "cars, aircraft and industry": "XLI", "materials": "XLB", "other": "SPY"}


def sector_of(sic) -> str:
    """Claude's grouping of the SEC's industry code (SIC) into sectors -- printed in docs/selloff_tables.md so that mistakes can be seen"""
    try: c = int(sic)
    except Exception: return "other"
    R = [((3674, 3674), "semiconductors"), ((7370, 7379), "software and internet"), ((3570, 3579), "computers and equipment"), ((3660, 3669), "computers and equipment"), ((3600, 3699), "computers and equipment"), ((7389, 7389), "payments and business services"), ((6099, 6099), "payments and business services"),
         ((6300, 6411), "insurance and health insurers"), ((6500, 6599), "real estate"), ((6798, 6798), "real estate"), ((6000, 6299), "banks and finance"), ((6700, 6799), "banks and finance"), ((2830, 2836), "drugs and biotech"), ((8731, 8731), "drugs and biotech"), ((3840, 3851), "medical devices and services"), ((8000, 8099), "medical devices and services"), ((5912, 5912), "medical devices and services"),
         ((1300, 1389), "energy"), ((2900, 2999), "energy"), ((4900, 4999), "utilities"), ((4800, 4899), "telecom and media"), ((7810, 7841), "telecom and media"), ((2700, 2799), "telecom and media"), ((2000, 2199), "consumer staples"), ((2840, 2844), "consumer staples"), ((5331, 5331), "consumer staples"), ((5399, 5411), "consumer staples"),
         ((5000, 5999), "retail and consumer"), ((3021, 3021), "retail and consumer"), ((7000, 7099), "retail and consumer"), ((2800, 2829), "materials"), ((1000, 1099), "materials"), ((3500, 3569), "cars, aircraft and industry"), ((3700, 3799), "cars, aircraft and industry"), ((3800, 3829), "cars, aircraft and industry"), ((3400, 3499), "cars, aircraft and industry"), ((4000, 4799), "cars, aircraft and industry")]
    for (a, b), name in R:
        if a <= c <= b: return name
    return "other"


def cmd_fetch():
    import yfinance as yf
    EX.mkdir(parents=True, exist_ok=True); SEC.mkdir(parents=True, exist_ok=True); bad = []; n = 0
    for t in YAHOO:
        f = EX / f"y_{t.replace('^', '_').replace('=', '_')}.parquet"
        if f.exists(): continue
        try:
            d = yf.download(t, start="1998-01-01", interval="1d", progress=False, auto_adjust=True)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            c = d["Close"].dropna(); c.index = pd.DatetimeIndex(c.index).tz_localize(None)
            if len(c) < 200: bad.append(t); continue
            c.to_frame("close").to_parquet(f); n += 1
        except Exception: bad.append(t)
    print(f"  Yahoo: {n} series downloaded now; without data: {bad or 'none'}"); bad = []; n = 0
    for k in FRED:
        f = EX / f"fred_{k}.parquet"
        if f.exists(): continue
        err = None
        for attempt in range(4):      # 22 Nov: every series failed once with a dropped connection; try again, slowly, with a plain browser-like request
            try:
                raw = urllib.request.urlopen(urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={k}", headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15", "Accept": "text/csv,*/*"}), timeout=90).read().decode(); d = pd.read_csv(io.StringIO(raw)); d.columns = ["date", "value"]
                d["value"] = pd.to_numeric(d["value"], errors="coerce"); d = d.dropna(); d.index = pd.to_datetime(d.pop("date")); d.to_parquet(f); n += 1; err = None; break
            except Exception as e: err = type(e).__name__; time.sleep(8 + 8 * attempt)
        if err: bad.append(f"{k} ({err})")
        time.sleep(2)
    print(f"  FRED: {n} series downloaded now; failed: {bad or 'none'}")
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set (needed for the SEC part; the Yahoo and FRED parts are done)")
    import src.ai_earnings as A
    FS = A._sec(); cmap = json.loads(FS.get(FS.TICKERS)); look = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}; rows = []; bad = []; n = 0; meta = SEC / "companies.csv"
    old = pd.read_csv(meta, dtype=str) if meta.exists() else pd.DataFrame(columns=["ticker", "cik", "sic", "sic_description", "name"]); have = set(old.ticker)
    for t in _stocks():
        f = SEC / f"{t}_facts.csv"
        if t in have and f.exists(): continue
        tick = next((a for a in A.ALIAS.get(t, [t]) if a in look), None)
        if tick is None: bad.append(t); continue
        try:
            sub = json.loads(FS.get(FS.SUBS.format(cik=look[tick]))); time.sleep(0.15); cf = json.loads(FS.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{look[tick]}.json")); time.sleep(0.15); out = []
            for key, names in CONCEPTS.items():
                for nm in names:
                    for unit, facts in ((cf.get("facts", {}).get("us-gaap", {}).get(nm, {}) or {}).get("units", {}) or {}).items():
                        if unit != "USD": continue
                        out += [dict(key=key, concept=nm, start=x.get("start", ""), end=x.get("end", ""), val=x.get("val"), filed=x.get("filed", ""), form=x.get("form", "")) for x in facts]
            pd.DataFrame(out, columns=["key", "concept", "start", "end", "val", "filed", "form"]).to_csv(f, index=False); rows.append(dict(ticker=t, cik=look[tick], sic=str(sub.get("sic", "")), sic_description=sub.get("sicDescription", ""), name=sub.get("name", ""))); n += 1
        except Exception as e: bad.append(f"{t} ({type(e).__name__})")
        if n and n % 20 == 0: print(f"    SEC: {n} companies done")
    pd.concat([old, pd.DataFrame(rows)]).drop_duplicates("ticker", keep="last").to_csv(meta, index=False)
    print(f"  SEC: industry code and reported financials for {n} companies downloaded now; failed or not found: {bad or 'none'} (run again to retry). No cost. -> {SEC}")


def _get_bytes(url, sec=False, timeout=60):
    h = {"User-Agent": f"regime-aware-signal academic research ({os.environ.get('SEC_CONTACT', 'set SEC_CONTACT')})"} if sec else {"User-Agent": "Mozilla/5.0"}
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout).read()


def cmd_fetch_short():
    """FINRA's public daily short-sale volume files (free). One file per day for the whole market; only the securities of this study are kept."""
    out = EX / "short"; out.mkdir(parents=True, exist_ok=True); keep = set(_stocks()); days = pd.bdate_range("2009-08-03", pd.Timestamp.now().normalize() - pd.Timedelta(days=1)); months = sorted({(d.year, d.month) for d in days}, reverse=True); tried = ok = 0; t0 = time.time(); empty = 0; first = True
    for y, m in months:      # newest month first: the recent files certainly exist if the address is right; going back, three empty months in a row mean the history has ended
        f = out / f"{y}-{m:02d}.csv"
        if f.exists(): first = False; continue
        rows = []; ok0 = ok
        for d in [x for x in days if x.year == y and x.month == m]:
            got = None
            for names in (["CNMS"], ["FNSQ", "FNYX"]):
                parts = []
                for nm in names:
                    try: parts.append(_get_bytes(f"https://cdn.finra.org/equity/regsho/daily/{nm}shvol{d:%Y%m%d}.txt", timeout=30).decode("utf-8", "ignore"))
                    except Exception: pass
                    time.sleep(0.05)
                if parts: got = parts; break
            tried += 1
            if not got: continue
            ok += 1
            for txt in got:
                for line in txt.splitlines()[1:]:
                    q = line.split("|")
                    if len(q) >= 5 and q[1] in keep:
                        try: rows.append((d.strftime("%Y-%m-%d"), q[1], float(q[2]), float(q[4])))
                        except Exception: pass
        if ok == ok0:
            if first: print("  FINRA short-sale files: the most recent month could not be read -- this source is skipped (its address may have changed)"); return
            empty += 1
            if empty >= 3: print(f"  FINRA short-sale files: nothing before {y}-{m:02d} plus three months -- the history ends there"); break
            continue
        first = False; empty = 0; pd.DataFrame(rows, columns=["date", "ticker", "short", "total"]).groupby(["date", "ticker"], as_index=False).sum().to_csv(f, index=False)
        if (m == 1): print(f"    FINRA short-sale volume: {y} done ({ok} of {tried} days read so far, {(time.time() - t0) / 60:.0f} min)")
    print(f"  FINRA short-sale volume: {ok} of {tried} days read now. -> {out}")


def cmd_fetch_insiders():
    """the SEC's quarterly data sets of insiders' transactions (Forms 3, 4, 5), free, from 2006: open-market purchases (code P) and sales (code S) by officers and directors"""
    if not os.environ.get("SEC_CONTACT"): print("  insiders: SEC_CONTACT is not set -- skipped"); return
    import zipfile, warnings
    warnings.simplefilter("ignore"); comp = pd.read_csv(SEC / "companies.csv", dtype=str) if (SEC / "companies.csv").exists() else None
    if comp is None: print("  insiders: run the main fetch first (the companies' SEC numbers are needed) -- skipped"); return
    cik = {str(int(c)): t for t, c in zip(comp.ticker, comp.cik)}; out = EX / "insiders"; out.mkdir(parents=True, exist_ok=True); now = pd.Timestamp.now(); n = bad = 0
    for y in range(2006, now.year + 1):
        for q in range(1, 5):
            if pd.Timestamp(year=y, month=3 * q, day=1) + pd.offsets.QuarterEnd(0) >= now: continue
            f = out / f"{y}q{q}.csv"
            if f.exists(): continue
            try:
                z = zipfile.ZipFile(io.BytesIO(_get_bytes(f"https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{y}q{q}_form345.zip", sec=True, timeout=180))); names = {x.upper().split("/")[-1]: x for x in z.namelist()}
                S_ = pd.read_csv(z.open(names["SUBMISSION.TSV"]), sep="\t", dtype=str, low_memory=False); T_ = pd.read_csv(z.open(names["NONDERIV_TRANS.TSV"]), sep="\t", dtype=str, low_memory=False); S_.columns = [c.upper() for c in S_.columns]; T_.columns = [c.upper() for c in T_.columns]
                S_["k"] = S_["ISSUERCIK"].str.lstrip("0"); S_ = S_[S_.k.isin(cik)]; T_ = T_[T_["ACCESSION_NUMBER"].isin(S_["ACCESSION_NUMBER"]) & T_["TRANS_CODE"].isin(["P", "S"])]; T_["v"] = pd.to_numeric(T_["TRANS_SHARES"], errors="coerce") * pd.to_numeric(T_["TRANS_PRICEPERSHARE"], errors="coerce")
                g = T_.groupby(["ACCESSION_NUMBER", "TRANS_CODE"]).v.sum().unstack(fill_value=0.0).reindex(columns=["P", "S"], fill_value=0.0); M = S_[["ACCESSION_NUMBER", "FILING_DATE", "k"]].merge(g, left_on="ACCESSION_NUMBER", right_index=True); M["ticker"] = M.k.map(cik)
                M["filed"] = pd.to_datetime(M["FILING_DATE"], errors="coerce"); M[["ticker", "filed", "P", "S"]].dropna(subset=["filed"]).to_csv(f, index=False); n += 1
            except Exception as e: bad += 1; print(f"    insiders {y}q{q}: {type(e).__name__}: {str(e)[:70]}") if bad <= 5 else None
            time.sleep(0.3)
            if bad == 6 and n == 0: print("  insiders: the first six quarters could not be read -- this source is skipped (its address or layout may have changed)"); return
    print(f"  SEC insiders' transactions: {n} quarters downloaded now, {bad} failed. -> {out}")


def _ser(f, col):
    d = pd.read_parquet(f); return d[col].astype(float).sort_index()


def _facts(t):
    """reported annual revenue and profit, and the latest balance-sheet figures, each with the date it became public"""
    f = SEC / f"{t}_facts.csv"
    if not f.exists(): return None
    d = pd.read_csv(f)
    if d.empty: return None
    d["end"] = pd.to_datetime(d["end"], errors="coerce"); d["start"] = pd.to_datetime(d["start"], errors="coerce"); d["filed"] = pd.to_datetime(d["filed"], errors="coerce"); d = d.dropna(subset=["end", "filed", "val"]); out = {}
    for key in CONCEPTS:
        g = d[d.key == key]
        if key in ("rev", "ni"): g = g[((g.end - g.start).dt.days >= 350) & ((g.end - g.start).dt.days <= 380)]
        if g.empty: out[key] = None; continue
        g = g.sort_values("filed").groupby("end", as_index=False).first().sort_values("end"); out[key] = g[["end", "val", "filed"]]      # the FIRST time each figure was filed
    return out


def _known(g, day, back=0):
    """the latest figure (by period end) that had been filed by `day`; back=1 gives the period about a year before it"""
    if g is None: return np.nan, None
    k = g[g.filed <= day]
    if k.empty: return np.nan, None
    last = k.iloc[-1]
    if back == 0: return float(last.val), last.end
    p = k[(k.end >= last.end - pd.Timedelta(days=380)) & (k.end <= last.end - pd.Timedelta(days=350))]
    return (float(p.iloc[-1].val), p.iloc[-1].end) if len(p) else (np.nan, None)


def cmd_tables():
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); TB.mkdir(parents=True, exist_ok=True); spy = P["SPY"].close; S = E[E.unit == "stocks"]; days = pd.DatetimeIndex(sorted(E.day.unique())); notes = []
    comp = pd.read_csv(SEC / "companies.csv", dtype=str) if (SEC / "companies.csv").exists() else pd.DataFrame(columns=["ticker", "sic", "sic_description", "name"]); comp["sector"] = comp.sic.map(sector_of); sec = dict(zip(comp.ticker, comp.sector))
    # ---- T1
    T1 = E[["event_id", "unit", "definition", "ticker", "day"] + FEATS].copy()
    # ---- T2 who fell and who set it off (stocks)
    stocks = [t for t in _stocks() if t in P]; R1 = pd.DataFrame({t: P[t].close.pct_change() for t in stocks}); F8 = pd.read_csv(ROOT / "filings8k.csv", parse_dates=["accepted_ny"]) if (ROOT / "filings8k.csv").exists() else pd.DataFrame(columns=["ticker", "accepted_ny", "results"])
    F8["d"] = (F8.accepted_ny + pd.Timedelta(hours=8)).dt.normalize()      # a filing after 16:00 belongs to the next day
    anyf = set(zip(F8.ticker, F8.d)) if len(F8) else set(); resf = set(zip(F8[F8.results].ticker, F8[F8.results].d)) if len(F8) else set(); lastres = {t: np.sort(g.d.unique()) for t, g in F8[F8.results].groupby("ticker")} if len(F8) else {}
    allf = {t: np.sort(g.d.to_numpy()) for t, g in F8.groupby("ticker")} if len(F8) else {}
    groups = {}; [groups.setdefault(sec.get(t, "other"), []).append(t) for t in stocks]; rows = []
    for r in S.itertuples():
        g = sec.get(r.ticker, "other"); peers = [p for p in groups.get(g, []) if p != r.ticker]; d = r.day; row = dict(event_id=r.event_id, sector=g, in_ai_chain=float(r.ticker in CHAIN), own_results_filing=float(E.at[r.event_id, CAUSE[0]]), own_other_filing=float(E.at[r.event_id, CAUSE[1]]))
        af = allf.get(r.ticker); row["own_filings_in_the_last_30_days"] = float(((af <= np.datetime64(d)) & (af > np.datetime64(d - pd.Timedelta(days=30)))).sum()) if af is not None else np.nan
        lr = lastres.get(r.ticker); row["days_since_own_results"] = float((d - pd.Timestamp(lr[lr <= np.datetime64(d)][-1])).days) if lr is not None and (lr <= np.datetime64(d)).any() else np.nan
        if len(peers) >= 3 and d in R1.index:
            pr = R1.loc[d, peers].dropna(); own = R1.at[d, r.ticker] if r.ticker in R1.columns else np.nan
            if len(pr) >= 3:
                worst = pr.idxmin(); prev = R1.index[R1.index.get_loc(d) - 1]; row.update(share_of_peers_down_3pct=float((pr <= -0.03).mean()), peers_average_move_pct=float(pr.mean() * 100), fell_more_than_every_peer=float(own < pr.min()), worst_peer_move_pct=float(pr.min() * 100),
                    worst_peer_had_results=float((worst, d) in resf or (worst, prev) in resf), worst_peer_had_any_filing=float((worst, d) in anyf or (worst, prev) in anyf), a_peer_reported_results_and_fell_3pct=float(any(((p, d) in resf or (p, prev) in resf) and pr.get(p, 0) <= -0.03 for p in pr.index)),
                    no_own_filing_but_a_peer_filed_and_fell=float(not ((r.ticker, d) in anyf or (r.ticker, prev) in anyf) and any(((p, d) in anyf or (p, prev) in anyf) and pr.get(p, 0) <= -0.03 for p in pr.index)))
        fund = SECTOR_FUND.get(g, "SPY"); fc = P.get(fund, P["SPY"]).close
        if d in fc.index and fc.index.get_loc(d) > 0: j = fc.index.get_loc(d); fm = float(fc.iloc[j] / fc.iloc[j - 1] - 1) * 100; row.update(sector_fund_move_pct=fm, move_against_sector_fund_pct=float(E.at[r.event_id, FEATS[1]]) - fm)
        rows.append(row)
    T2 = pd.DataFrame(rows)
    # ---- T3 the company's condition
    rows = []; DV = pd.DataFrame({t: (P[t].close * P[t].volume).rolling(60).mean() for t in stocks}); rank = DV.rank(axis=1, pct=True); FC = {t: _facts(t) for t in stocks}; sr = spy.pct_change()
    for r in S.itertuples():
        d = r.day; c = P[r.ticker].close; i = int(r.i); n = int(r.n); row = dict(event_id=r.event_id); fx = FC.get(r.ticker)
        if fx:
            rev0, e0 = _known(fx["rev"], d); rev1, _ = _known(fx["rev"], d, 1); ni0, _ = _known(fx["ni"], d); a0, _ = _known(fx["assets"], d); l0, _ = _known(fx["liab"], d); q0, _ = _known(fx["equity"], d); c0, _ = _known(fx["cash"], d)
            if not np.isfinite(l0) and np.isfinite(a0) and np.isfinite(q0): l0 = a0 - q0
            row.update(profitable_last_year=float(ni0 > 0) if np.isfinite(ni0) else np.nan, revenue_growth_last_year_pct=(rev0 / rev1 - 1) * 100 if np.isfinite(rev0) and np.isfinite(rev1) and rev1 > 0 else np.nan, profit_margin_pct=ni0 / rev0 * 100 if np.isfinite(ni0) and np.isfinite(rev0) and rev0 > 0 else np.nan,
                       liabilities_to_assets_pct=l0 / a0 * 100 if np.isfinite(l0) and np.isfinite(a0) and a0 > 0 else np.nan, cash_to_assets_pct=c0 / a0 * 100 if np.isfinite(c0) and np.isfinite(a0) and a0 > 0 else np.nan)
        row["size_rank_in_the_list"] = float(rank.at[d, r.ticker]) if d in rank.index and r.ticker in rank.columns else np.nan
        if i - n - 252 >= 0: row["move_over_the_year_before_pct"] = float(c.iloc[i - n] / c.iloc[i - n - 252] - 1) * 100
        if i - n - 250 >= 1:
            a = c.pct_change().iloc[i - n - 250:i - n]; b = sr.reindex(a.index); ok = a.notna() & b.notna()
            if ok.sum() > 120 and b[ok].var() > 0: row["sensitivity_to_the_market"] = float(np.cov(a[ok], b[ok])[0, 1] / b[ok].var()); row["usual_daily_move_pct"] = float(a[ok].std() * 100)
        rows.append(row)
    T3 = pd.DataFrame(rows)
    # ---- T4 stress and other markets (everything as it stood at the close of the event day; FRED series with their publication delay)
    T4 = pd.DataFrame({"event_id": E.event_id}); dser = E.day
    def at(s, lag=0): s = s.shift(lag) if lag else s; return s.reindex(s.index.union(days)).ffill().reindex(dser).to_numpy()
    for k, (name, lag) in FRED.items():
        f = EX / f"fred_{k}.parquet"
        if not f.exists(): notes.append(f"{name}: not downloaded"); continue
        s = _ser(f, "value"); T4[name] = at(s, lag); T4[f"{name}, change over 5 observations"] = at(s.diff(5), lag)
    vix = P["^VIX"].close
    for t, name in YAHOO.items():
        f = EX / f"y_{t.replace('^', '_').replace('=', '_')}.parquet"
        if not f.exists(): notes.append(f"{name}: not downloaded"); continue
        s = _ser(f, "close")
        if t in ("^VIX3M", "^VIX9D"): T4[f"VIX against the {name}"] = at((vix / s.reindex(vix.index)).dropna())
        elif t in ("^VVIX", "^SKEW"): T4[name] = at(s)
        elif t in ("^TNX", "^IRX"): T4[f"{name}, change over 5 sessions"] = at(s.diff(5))
        elif t in ("IWM", "IVE", "RSP"):
            other = spy if t != "IVE" else (_ser(EX / "y_IVW.parquet", "close") if (EX / "y_IVW.parquet").exists() else None)
            if other is not None: T4[{"IWM": "small against large companies", "IVE": "value against growth shares", "RSP": "the average share against the S&P 500"}[t] + ", 5 sessions %"] = at((s.pct_change(5) - other.reindex(s.index).pct_change(5)) * 100)
        elif t == "IVW": pass
        else: T4[f"{name}, move over 5 sessions %"] = at(s.pct_change(5) * 100)
    # ---- T5 calendar
    T5 = pd.DataFrame({"event_id": E.event_id, "weekday": E.day.dt.day_name(), "month": E.day.dt.month_name()}); sess = spy.index; pos = pd.Series(np.arange(len(sess)), index=sess); me = pd.Series(sess, index=sess).groupby([sess.year, sess.month]).transform("max"); qe = pd.Series(sess, index=sess).groupby([sess.year, sess.quarter]).transform("max")
    T5["sessions_to_month_end"] = (pos.reindex(me.reindex(E.day).to_numpy()).to_numpy() - pos.reindex(E.day).to_numpy()); T5["sessions_to_quarter_end"] = (pos.reindex(qe.reindex(E.day).to_numpy()).to_numpy() - pos.reindex(E.day).to_numpy())
    third = E.day.apply(lambda d: [x for x in pd.date_range(d.replace(day=1), periods=31) if x.month == d.month and x.weekday() == 4][2]); T5["option_expiry_week"] = ((third - E.day).dt.days.between(0, 4)).astype(float).to_numpy()
    fed = sorted({pd.Timestamp(p.name.split("__")[1][:8]) for p in Path("data_provenance/doc_reads").glob("fomc_statement__*") if p.name.split("__")[1][:8].isdigit()}) if Path("data_provenance/doc_reads").exists() else []
    if fed:
        fa = np.array(fed, dtype="datetime64[ns]"); dv = E.day.to_numpy(); nx = np.searchsorted(fa, dv, side="left"); T5["days_to_next_fed_statement"] = np.where((nx < len(fa)) & (dv >= fa[0]), (fa[np.clip(nx, 0, len(fa) - 1)] - dv).astype("timedelta64[D]").astype(float), np.nan); T5["days_since_last_fed_statement"] = np.where(nx > 0, (dv - fa[np.clip(nx - 1, 0, len(fa) - 1)]).astype("timedelta64[D]").astype(float), np.nan)
    else: notes.append("Fed statement dates: data_provenance/doc_reads not found")
    if len(F8): rs = F8[F8.results].groupby("d").size().reindex(pd.date_range(F8.d.min(), F8.d.max()), fill_value=0).rolling(10).sum(); T5["results_filings_in_the_list_last_10_days"] = rs.reindex(E.day).to_numpy()
    # ---- T6 Claude's reading (AI-chain companies; only if the score files are on this disk)
    T6 = pd.DataFrame(columns=["event_id"]); pe, pv = Path("processed/ai_earnings_scores.csv"), Path("processed/ai_events_scores.csv")
    if pe.exists() and pv.exists():
        A1 = pd.read_csv(pe, parse_dates=["accepted_ny"]).sort_values("accepted_ny"); A2 = pd.read_csv(pv, parse_dates=["accepted_ny"]).sort_values("accepted_ny"); rows = []
        for r in S[S.ticker.isin(A1.ticker.unique())].itertuples():
            end = r.day + pd.Timedelta(hours=16); a = A1[(A1.ticker == r.ticker) & (A1.accepted_ny <= end)]; b = A2[(A2.ticker == r.ticker) & (A2.accepted_ny <= end) & (A2.accepted_ny > end - pd.Timedelta(days=int(r.n) + 1))]
            if len(a) == 0: continue
            row = dict(event_id=r.event_id, latest_results_score=float(a.iloc[-1].own_stock), days_since_those_results=float((r.day - a.iloc[-1].accepted_ny.normalize()).days), results_in_the_window=float((end - a.iloc[-1].accepted_ny).days <= int(r.n)))
            if len(b): row.update(event_in_the_window_score=float(b.iloc[-1].own_stock), event_in_the_window_material=float(b.iloc[-1].material), event_in_the_window_type=str(b.iloc[-1].event_type))
            rows.append(row)
        T6 = pd.DataFrame(rows)
    else: notes.append("T6: Claude's score files (processed/ai_earnings_scores.csv, ai_events_scores.csv) not found on this disk -- table empty")
    # ---- T7 short selling (FINRA) and T8 insiders (SEC) -- second-wave inputs (founder, 21 Nov: include every free one in the same run)
    T7 = pd.DataFrame(columns=["event_id"]); fs = sorted((EX / "short").glob("*.csv")) if (EX / "short").exists() else []
    if fs:
        Sh = pd.concat([pd.read_csv(f, parse_dates=["date"]) for f in fs]); Sh = Sh[Sh.total > 0]; Sh["share"] = Sh.short / Sh.total; rows = []; by = {t: g.set_index("date").share.sort_index() for t, g in Sh.groupby("ticker")}
        for r in S.itertuples():
            g = by.get(r.ticker)
            if g is None or r.day not in g.index: continue
            j = g.index.get_loc(r.day)
            if j < 20: continue
            avg = float(g.iloc[j - 20:j].mean()); rows.append(dict(event_id=r.event_id, short_sales_share_of_volume_that_day=float(g.iloc[j]), short_sales_share_average_of_20_days_before=avg, short_sales_share_that_day_against_its_average=float(g.iloc[j] / avg) if avg > 0 else np.nan))
        T7 = pd.DataFrame(rows)
    else: notes.append("T7: FINRA short-sale files not downloaded -- table empty")
    T8 = pd.DataFrame(columns=["event_id"]); fi = sorted((EX / "insiders").glob("*.csv")) if (EX / "insiders").exists() else []
    if fi:
        In = pd.concat([pd.read_csv(f, parse_dates=["filed"]) for f in fi]); first = In.filed.min(); rows = []; by = {t: g.sort_values("filed") for t, g in In.groupby("ticker")}
        for r in S.itertuples():
            if r.day < first + pd.Timedelta(days=90): continue
            g = by.get(r.ticker); w = g[(g.filed <= r.day) & (g.filed > r.day - pd.Timedelta(days=90))] if g is not None else None; nb = int((w.P > 0).sum()) if w is not None else 0; ns = int((w.S > 0).sum()) if w is not None else 0
            rows.append(dict(event_id=r.event_id, insider_purchase_filings_in_90_days=float(nb), insider_sale_filings_in_90_days=float(ns), any_insider_purchase_in_90_days=float(nb > 0), insider_purchases_minus_sales_in_90_days=float(nb - ns)))
        T8 = pd.DataFrame(rows)
    else: notes.append("T8: the SEC's insider data sets not downloaded -- table empty")
    L = ["# Sell-off study, stage D: the input tables (no outcome computed)", "", f"{len(E)} sell-offs ({len(S)} of stocks, {len(E) - len(S)} of index and sector funds). A column is empty for a sell-off when its input did not exist yet at that date. 'Rows with every column' is what a search inside that table alone can use.", "",
         "| table | what it holds | rows | columns | rows with every column | first year with every column |", "|---|---|---|---|---|---|"]
    for name, what, T in (("T1", "the fall and the market", T1), ("T2", "who fell and who set it off", T2), ("T3", "the company's condition", T3), ("T4", "stress and other markets", T4), ("T5", "calendar", T5), ("T6", "Claude's reading (AI chain)", T6), ("T7", "short selling", T7), ("T8", "insiders' trades", T8)):
        T.to_csv(TB / f"{name}.csv", index=False); cols = [c for c in T.columns if c not in ("event_id", "unit", "definition", "ticker", "day")]; full = T[cols].notna().all(axis=1) if len(T) and cols else pd.Series(dtype=bool); yr = E.day.dt.year.reindex(T.event_id[full.to_numpy()].to_numpy()) if len(T) and full.any() else pd.Series(dtype=float)
        L.append(f"| {name} | {what} | {len(T)} | {len(cols)} | {int(full.sum()) if len(full) else 0} | {int(yr.min()) if len(yr) else ''} |"); print(f"  {name} ({what}): {len(T)} rows, {len(cols)} columns; rows with every column {int(full.sum()) if len(full) else 0}" + (f", from {int(yr.min())}" if len(yr) else ""))
        if len(T) and cols: L_cols = "; ".join(f"{c} ({T[c].notna().mean():.0%})" for c in cols); notes.append(f"{name} columns (share of rows filled): {L_cols}")
    cnt = S.assign(sector=S.ticker.map(lambda t: sec.get(t, "other"))).groupby("sector").agg(companies=("ticker", "nunique"), sell_offs=("ticker", "size")).sort_values("sell_offs", ascending=False)
    L += ["", "## Sectors (Claude's grouping of the SEC's industry codes)", "", "| sector | fund used for 'against its sector' | companies | sell-offs (all definitions) |", "|---|---|---|---|"] + [f"| {k} | {SECTOR_FUND.get(k, 'SPY')} | {int(v.companies)} | {int(v.sell_offs)} |" for k, v in cnt.iterrows()]
    L += ["", "| company | SEC industry code | SEC's description | sector given |", "|---|---|---|---|"] + [f"| {r.ticker} | {r.sic} | {r.sic_description} | {r.sector} |" for r in comp.sort_values(["sector", "ticker"]).itertuples()] + ["", "## Notes", ""] + [f"- {x}" for x in notes]
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_tables.md").write_text("\n".join(L) + "\n"); print("  sectors: " + ", ".join(f"{k} {int(v.companies)} companies / {int(v.sell_offs)} sell-offs" for k, v in cnt.iterrows()))
    for x in notes:
        if "not " in x: print(f"  note: {x}")
    print(f"No outcome was computed. -> {TB}, docs/selloff_tables.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fetch", "fetch_insiders", "fetch_short", "tables"]); a = ap.parse_args(); {"fetch": cmd_fetch, "fetch_insiders": cmd_fetch_insiders, "fetch_short": cmd_fetch_short, "tables": cmd_tables}[a.cmd]()
