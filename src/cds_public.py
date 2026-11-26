"""cds_public.py -- can single-company CDS trades be followed automatically and free? A PROBE only (TRACK 3.126).

Since 2022 a US rule (the SEC's Regulation SBSR) makes swap data repositories publish every single-company CDS trade soon after it happens: the company it is written on,
the price as a spread in basis points, the time, the size (capped). The largest repository is DTCC's (DDR). If its daily public files can be downloaded, an Oracle CDS
series -- and one for every large technology company -- can be built from real trades, free.

    python -m src.cds_public probe        # free; tries to download ONE day's public file of credit swaps, and reports what is in it. Keeps no data; writes docs/cds_public_probe.md.

NOT yet done, on purpose: no daily collection. The file addresses below are from Claude's memory (unverified), and DTCC's terms for this public data have not been read yet.
"""
from __future__ import annotations
import argparse, io, time, urllib.request, zipfile
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np, pandas as pd

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PATTERNS = ["https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDITS_{y}_{m}_{d}.zip",
            "https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDIT_{y}_{m}_{d}.zip",
            "https://kgc0418-tdw-data-0.s3.amazonaws.com/sec/eod/SEC_CUMULATIVE_CREDITS_{y}_{m}_{d}.zip"]
NAMES = {"Oracle": ["ORACLE"], "Meta": ["META PLATFORMS", "FACEBOOK"], "Alphabet": ["ALPHABET", "GOOGLE"], "Microsoft": ["MICROSOFT"], "Amazon": ["AMAZON"], "Apple": ["APPLE INC"], "Nvidia": ["NVIDIA"], "Broadcom": ["BROADCOM"],
         "Intel": ["INTEL CORP"], "AMD": ["ADVANCED MICRO"], "Micron": ["MICRON"], "IBM": ["INTERNATIONAL BUSINESS MACHINES", "IBM CORP"], "Cisco": ["CISCO"], "Dell": ["DELL"], "CoreWeave": ["COREWEAVE"], "Tesla": ["TESLA"], "Qualcomm": ["QUALCOMM"]}


RAW = Path("data_provenance/cds_public/raw")      # every folder named raw/ is ignored by git: the files are not uploaded (DTCC's terms for re-publishing are not yet read)
URL = PATTERNS[0]; START = "2022-02-14"      # the first address answered in the probe of 26 Nov 2026; public reporting under the SEC's rule began in February 2022
NAMES.update({"Hewlett Packard Enterprise": ["HEWLETT PACKARD ENTERPRISE"], "Super Micro": ["SUPER MICRO"], "Salesforce": ["SALESFORCE"], "Texas Instruments": ["TEXAS INSTRUMENTS"], "Applied Materials": ["APPLIED MATERIALS"], "Netflix": ["NETFLIX"], "TSMC": ["TAIWAN SEMICONDUCTOR"]})


def cmd_fetch(since: str):
    """downloads the daily public file of single-company credit swaps for every weekday from `since`; one small file a day; safe to stop (Ctrl+C) and run again"""
    RAW.mkdir(parents=True, exist_ok=True); today = datetime.utcnow().date(); days = [d.date() for d in pd.bdate_range(since, today - timedelta(days=1))]
    todo = [d for d in days if not (RAW / f"{d}.parquet").exists() and not (RAW / f"{d}.none").exists()]; n = 0; none = 0; bad = []; t0 = time.time(); rows = 0
    print(f"{len(days)} weekdays from {since}; {len(days) - len(todo)} already on disk; {len(todo)} to ask for. Free. One request every half second. Safe to stop with Ctrl+C and run again.")
    for k, d in enumerate(todo):
        url = URL.format(y=d.year, m=f"{d.month:02d}", d=f"{d.day:02d}"); ok = False; why = ""
        for attempt in range(3):
            try:
                raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"}), timeout=90).read(); z = zipfile.ZipFile(io.BytesIO(raw)); df = pd.read_csv(z.open(z.namelist()[0]), dtype=str, low_memory=False)
                tmp = RAW / f"{d}.tmp"; df.to_parquet(tmp); tmp.replace(RAW / f"{d}.parquet"); n += 1; rows += len(df); ok = True; break
            except urllib.error.HTTPError as ex:
                why = f"HTTP {ex.code}"
                if ex.code == 404:
                    if (today - d).days > 5: (RAW / f"{d}.none").write_text("no file\n")      # a holiday, or DTCC no longer keeps that day
                    none += 1; ok = True; break
                time.sleep(5 * (attempt + 1))
            except KeyboardInterrupt: raise
            except Exception as ex: why = f"{type(ex).__name__}: {str(ex)[:60]}"; time.sleep(5 * (attempt + 1))
        if not ok:
            bad.append(str(d))
            if len(bad) <= 5: print(f"  {d}: failed 3 times ({why}); the next run tries it again")
            if len(bad) >= 15 and n == 0: print("  stopped: 15 failures and nothing downloaded -- the connection or the address. Tell Claude what the lines above say."); break
        done = k + 1
        if done in (20, 100) or done % 250 == 0: per = (time.time() - t0) / done; print(f"  {done} days asked: {n} files, {none} days without a file, {rows:,} rows; measured {per:.1f} seconds a day -> about {(len(todo) - done) * per / 60:.0f} minutes left")
        time.sleep(0.5)
    have = sorted(RAW.glob("*.parquet")); print(f"DONE: {n} files downloaded now ({rows:,} rows), {none} days without a file, {len(bad)} failed, {(time.time() - t0) / 60:.0f} minutes. On disk: {len(have)} days" + (f", {have[0].stem} to {have[-1].stem}" if have else "") + f". -> {RAW} (ignored folder; not uploaded)")


def _load(only_named=True) -> pd.DataFrame:
    fr = []
    for f in sorted(RAW.glob("*.parquet")):
        d = pd.read_parquet(f); d["file_day"] = f.stem
        if only_named:
            cols = [c for c in d.columns if any(w in c.lower() for w in ("underl", "asset name", "product name"))]; blob = d[cols].fillna("").astype(str).agg(" | ".join, axis=1).str.upper(); d["company"] = ""
            for comp, keys in NAMES.items(): d.loc[blob.apply(lambda s, keys=keys: any(k in s for k in keys)) & (d.company == ""), "company"] = comp
            d = d[d.company != ""]
        fr.append(d)
    return pd.concat(fr, ignore_index=True) if fr else pd.DataFrame()


def cmd_describe():
    """what is in the files for the large technology companies: how many trades, on how many days, and WHICH PRICE INFORMATION each trade carries. Free, no download."""
    D = _load()
    if not len(D): print("no files on disk: run fetch first"); return
    act = next((c for c in D.columns if c.lower().startswith("action type")), None); new = D[D[act].isin(["NEWT"])] if act else D; allfiles = len(list(RAW.glob("*.parquet")))
    L = ["# Public single-company CDS trades of large technology companies: what the files hold", "", f"{allfiles} daily files, {D.file_day.min()} to {D.file_day.max()}. Rows that name one of {len(NAMES)} companies: {len(D):,}; of them new trades (action NEWT): {len(new):,}.", "",
         "| company | rows | new trades | days with a new trade | first day | new trades in the last 60 files |", "|---|---|---|---|---|---|"]
    last60 = set(sorted(D.file_day.unique())[-60:]); print(f"{allfiles} daily files, {D.file_day.min()} to {D.file_day.max()}; rows naming a listed company {len(D):,}; new trades {len(new):,}")
    print("  company | rows | new trades | days with a new trade (of all days) | first day | new trades in the last 60 files")
    for comp in sorted(NAMES, key=lambda c: -int((new.company == c).sum())):
        g = D[D.company == comp]; gn = new[new.company == comp]
        if not len(g): continue
        row = f"{comp} | {len(g):,} | {len(gn):,} | {gn.file_day.nunique()} of {allfiles} | {g.file_day.min()} | {int(gn.file_day.isin(last60).sum())}"; print("  " + row); L.append("| " + row + " |")
    key = [c for c in D.columns if any(w in c.lower() for w in ("price", "spread", "fixed rate", "other payment", "notation", "notional amount-leg 1", "upfront", "coupon"))]
    L += ["", "## Which price information the new trades carry (share of new trades with the column filled)", "", "| column | all listed companies | Oracle | most frequent values (Oracle) |", "|---|---|---|---|"]; o = new[new.company == "Oracle"]
    print("  price information on new trades -- column: share filled, all listed companies / Oracle; most frequent Oracle values")
    for c in key:
        fa = float((new[c].fillna("") != "").mean()) if len(new) else 0.0; fo = float((o[c].fillna("") != "").mean()) if len(o) else 0.0
        if fa < 0.005 and fo < 0.005: continue
        top = "; ".join(f"{v} ({n})" for v, n in o[c][o[c].fillna("") != ""].value_counts().head(4).items()); print(f"    {c}: {fa:.0%} / {fo:.0%}; {top[:140]}"); L.append(f"| {c} | {fa:.0%} | {fo:.0%} | {top[:140]} |")
    nc = next((c for c in D.columns if c.lower().startswith("notional amount-leg 1")), None)
    if nc and len(new): cap = float(new[nc].fillna("").str.contains(r"\+").mean()); print(f"  size hidden behind the cap ('5,000,000+'): {cap:.0%} of new trades"); L += ["", f"Size hidden behind the cap ('+'): {cap:.0%} of the new trades."]
    Path("docs").mkdir(exist_ok=True); Path("docs/cds_public_describe.md").write_text("\n".join(L) + "\n"); print("-> docs/cds_public_describe.md. Paste all of this to Claude.")


# ---------------------------------------------------------------- test CDS-1 (TRACK 3.128): from trades to a daily spread, then the LI-1 method
SER = RAW / "series"; AI_DEBT = ["Oracle", "CoreWeave", "Meta", "Alphabet", "Microsoft", "Amazon"]; RATE, RECOVERY, MIN_DAYS = 0.04, 0.40, 250
JUNK = {"NT", "SR NT", "NO NAME OBTAINABLE", "", "NA", "N/A", "SR"}


def _col(D, start):
    return next((c for c in D.columns if c.lower().startswith(start.lower())), None)


def _num(x):
    return pd.to_numeric(x.astype(str).str.replace(",", "", regex=False).str.replace("+", "", regex=False), errors="coerce")


def _upfront_to_spread(c, u, T, sign):
    """a trade priced as a fixed yearly rate c plus a one-off payment u (share of the size): the spread that is worth the same. spread = c + sign * u / A, where A is the value of
    paying 1 a year for T years while the company has not defaulted: A = (1 - exp(-(r + h) T)) / (r + h), h = spread / (1 - recovery). Solved by repeating the step."""
    sp = np.full(len(c), np.nan); s0 = np.maximum(c + sign * u / np.maximum(T, 0.5), 1e-5)
    for _ in range(25):
        h = s0 / (1 - RECOVERY); A = (1 - np.exp(-(RATE + h) * T)) / (RATE + h); s0 = np.maximum(c + sign * u / A, 1e-6)
    sp[:] = s0; return sp


def trades() -> pd.DataFrame:
    """every usable NEW trade of a 5-year single-company CDS in US dollars, with a spread in basis points and how it was obtained"""
    fr = []
    for f in sorted(RAW.glob("*.parquet")):
        d = pd.read_parquet(f)
        act = _col(d, "Action type"); ex = _col(d, "Execution Timestamp"); exp = _col(d, "Expiration Date"); nt = _col(d, "Notional amount-Leg 1"); cur = _col(d, "Notional currency-Leg 1"); fx = _col(d, "Fixed rate-Leg 1"); sp = _col(d, "Spread-Leg 1"); spn = _col(d, "Spread notation-Leg 1")
        op = _col(d, "Other payment amount"); opt = _col(d, "Other payment type"); pk = _col(d, "Package transaction spread"); pkp = _col(d, "Package transaction price"); did = _col(d, "Dissemination Identifier"); oid = _col(d, "Original Dissemination Identifier"); un = _col(d, "Underlying Asset Name"); upi = _col(d, "UPI Underlier Name"); fisn = _col(d, "UPI FISN")
        if not all([act, ex, exp, nt, un or upi]): continue
        gone = set(d.loc[d[act].isin(["EROR", "TERM"]), oid].dropna()) if oid else set(); n = d[d[act] == "NEWT"].copy()
        if did: n = n[~n[did].isin(gone)]
        if fisn: n = n[n[fisn].fillna("").str.contains("CDS") & n[fisn].fillna("").str.contains("SN")]      # single-company CDS only
        if cur: n = n[n[cur].fillna("USD").str.startswith("USD")]
        if pk: n = n[n[pk].fillna("") == ""]
        if pkp: n = n[n[pkp].fillna("") == ""]
        if not len(n): continue
        a = n[upi].fillna("").str.upper().str.strip() if upi else pd.Series("", index=n.index); b = n[un].fillna("").str.upper().str.strip() if un else pd.Series("", index=n.index); name = a.where(~a.isin(JUNK), b); name = name.where(~name.isin(JUNK), "")
        t = pd.to_datetime(n[ex], utc=True, errors="coerce"); T = (pd.to_datetime(n[exp], utc=True, errors="coerce") - t).dt.days / 365.25
        out = pd.DataFrame(dict(nm=name.str.replace(r"[^A-Z0-9 ]+", " ", regex=True).str.replace(r"\b(INC|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|PLC|THE|HOLDINGS|GROUP|LLC|LP|SA|AG|NV)\b", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip(), raw_name=name, t=t, tenor=T,
                                capped=n[nt].fillna("").str.contains(r"\+", regex=True), sz=_num(n[nt]), fixed=_num(n[fx]) if fx else np.nan, direct=_num(n[sp]) if sp else np.nan, notation=n[spn].fillna("") if spn else "", upfront=_num(n[op]) if op else np.nan, uptype=n[opt].fillna("") if opt else ""))
        fr.append(out)
    X = pd.concat(fr, ignore_index=True); X = X[X.t.notna() & (X.nm != "") & X.tenor.between(4.25, 5.75)].copy()
    X["company"] = ""
    for comp, keys in NAMES.items(): X.loc[X.raw_name.apply(lambda s, keys=keys: any(k in s for k in keys)) & (X.company == ""), "company"] = comp
    X["key"] = X.company.where(X.company != "", X.nm); ny = X.t.dt.tz_convert("America/New_York"); X["day"] = pd.to_datetime(ny.dt.date); X = X[(ny.dt.hour < 16) & (ny.dt.dayofweek < 5)]      # only trades done before the share market closes
    # (a) the spread is given directly; notation 3 = a decimal (0.0164 = 164 basis points), notation 4 = basis points
    X["bp"] = np.where(X.notation.astype(str) == "4", X.direct, X.direct * 1e4); X["how"] = np.where(X.bp.notna(), "given", ""); X.loc[~X.bp.between(3, 5000), ["bp", "how"]] = [np.nan, ""]
    # (b) a fixed rate plus a one-off payment, and the size is NOT hidden: two possible spreads (the payment may go either way); the one nearer to the company's given spreads of the days around is kept
    fixed = X.fixed.where(X.fixed < 0.2, X.fixed / 100); m = X.bp.isna() & fixed.between(0.001, 0.1) & (X.upfront > 0) & ~X.capped & (X.sz > 0) & X.uptype.astype(str).str.startswith("UFRO") & ~X.uptype.astype(str).str.contains(";")
    u = (X.upfront / X.sz).where(m); ok = m & u.between(1e-5, 0.5); c = fixed[ok].to_numpy(float); uu = u[ok].to_numpy(float); TT = X.tenor[ok].to_numpy(float)
    up = _upfront_to_spread(c, uu, TT, +1) * 1e4; dn = _upfront_to_spread(c, uu, TT, -1) * 1e4; dn = np.where(c - uu / np.maximum(TT, 0.5) > 0, dn, np.nan)
    G = X[X.how == "given"].groupby(["key", "day"]).bp.median(); anchors = {k: g.droplevel(0).sort_index() for k, g in G.groupby(level=0)}; idx = X.index[ok]; chosen = np.full(len(idx), np.nan)
    for i, (k, dday) in enumerate(zip(X.key[ok], X.day[ok])):
        g = anchors.get(k)
        if g is None: continue
        near = g[(g.index >= dday - pd.Timedelta(days=10)) & (g.index <= dday + pd.Timedelta(days=10))]
        if not len(near): continue
        anc = float(near.iloc[(np.abs((near.index - dday).days)).argmin()]); cand = [x for x in (up[i], dn[i]) if x == x]; best = min(cand, key=lambda x: abs(np.log(x / anc))) if cand else np.nan
        if best == best and 0.5 <= best / anc <= 2.0: chosen[i] = best
    X.loc[idx, "bp"] = chosen; X.loc[idx[np.isfinite(chosen)], "how"] = "from the one-off payment"
    return X[X.bp.notna()].copy()


def cmd_series():
    X = trades(); SER.mkdir(parents=True, exist_ok=True); days = pd.DatetimeIndex(sorted(pd.to_datetime([f.stem for f in RAW.glob("*.parquet")]))); bd = pd.bdate_range(days.min(), days.max())
    D = X.groupby(["key", "day"]).bp.median().unstack(0).reindex(bd); L = np.log(D); cnt = D.notna().sum(); tech = [c for c in D.columns if c in NAMES]; others = [c for c in D.columns if c not in NAMES and cnt[c] >= 60]
    dl = L.ffill(limit=5).diff().where(L.notna())      # the change since the last day with a trade, at most 5 sessions back
    market = dl[others].median(axis=1).where(dl[others].notna().sum(axis=1) >= 8); M = market.fillna(0).cumsum()      # the move of all OTHER single-company CDS that day
    rows = []; made = []
    for c in sorted(tech, key=lambda c: -cnt[c]):
        g = X[X.key == c]; first = D[c].dropna(); row = dict(company=c, days=int(cnt[c]), trades=len(g), given=int((g.how == "given").sum()), converted=int((g.how != "given").sum()), first=f"{first.index[0]:%Y-%m-%d}" if len(first) else "", start_bp=float(first.iloc[:20].median()) if len(first) else np.nan, end_bp=float(first.iloc[-20:].median()) if len(first) else np.nan, used=bool(cnt[c] >= MIN_DAYS)); rows.append(row)
        if row["used"]: (L[c] - M).dropna().to_frame("value").to_parquet(SER / f"CDS_{c}.parquet"); made.append(c)
    ai = dl[[c for c in AI_DEBT if c in dl.columns]]; aim = (ai.mean(axis=1) - market).where(ai.notna().sum(axis=1) >= 1); (aim.fillna(0).cumsum().where(aim.notna()).dropna()).to_frame("value").to_parquet(SER / "CDS_AI_DEBT.parquet")
    pd.DataFrame(rows).to_csv(SER / "summary.csv", index=False)
    print(f"{len(X):,} usable trades of 5-year single-company CDS ({int((X.how == 'given').sum()):,} with the spread given, {int((X.how != 'given').sum()):,} worked out from the one-off payment); {X.key.nunique():,} companies; {len(others)} other companies form the market-wide move ({int(market.notna().sum())} days with one).")
    print("  company | days with a spread (of %d) | trades: spread given + worked out | first day | spread, first 20 days -> last 20 days (basis points) | in the test" % len(bd))
    for r in rows: print(f"  {r['company']} | {r['days']} | {r['given']} + {r['converted']} | {r['first']} | {r['start_bp']:.0f} -> {r['end_bp']:.0f} | {'YES' if r['used'] else 'no: under ' + str(MIN_DAYS) + ' days'}")
    T2 = X[X.key.isin(tech)]; g = T2[T2.how == "given"].groupby(["key", "day"]).bp.median(); w = T2[T2.how != "given"].groupby(["key", "day"]).bp.median(); J = pd.concat([g, w], axis=1, keys=["g", "w"]).dropna(); gap = (J.w / J.g - 1).abs()
    print(f"  check of the working-out: on {len(J)} company-days with both kinds of trade, the worked-out spread differs from the given one by {gap.median():.1%} in the middle, {gap.quantile(0.9):.1%} at the 9-in-10 mark" if len(J) else "  check of the working-out: no company-day has both kinds of trade")
    print(f"  the combined 'AI debt' series ({', '.join(AI_DEBT)}): {int(aim.notna().sum())} days")
    return rows, made, int(aim.notna().sum()), len(bd)


def cmd_test(shifts: int):
    rows, made, ai_days, nbd = cmd_series()
    from src import leading as LD
    old = LD._series
    def series(k):
        if isinstance(k, str) and k.startswith("CDS_"):
            f = SER / f"{k}.parquet"; return pd.read_parquet(f)["value"] if f.exists() else None
        return old(k)
    LD._series = series; LD.START = f"{min(pd.to_datetime([f.stem for f in RAW.glob('*.parquet')])):%Y-%m-%d}"
    C = {f"{c} CDS spread against all other companies' CDS": dict(kind="level", a=f"CDS_{c}", lag=0, rise="its credit worse") for c in made}
    if ai_days >= MIN_DAYS: C["AI debt: CDS of " + ", ".join(AI_DEBT) + " against all other companies' CDS"] = dict(kind="level", a="CDS_AI_DEBT", lag=0, rise="AI borrowers' credit worse")
    if not C: print("no company has enough days with a spread: the test cannot be run"); return
    ex = ["## How the daily spreads were built", "", f"New trades of 5-year single-company CDS in US dollars, done before 16:00 New York time. A trade's spread is taken as given where the file gives it; where the trade is priced as a fixed yearly rate plus a one-off payment and its size is not hidden, the spread worth the same is worked out (interest {RATE:.0%}, recovery {RECOVERY:.0%}; of the two possible answers the one nearer to the company's given spreads within 10 days is kept). Trades whose size is hidden behind the cap and that give no spread are not usable. "
          "The day's spread = the middle one of its trades. Each series is measured against the same day's move of all other single-company CDS, so that a move of the whole credit market is taken out.", "",
          "| company | days with a spread | trades: spread given + worked out | first day | spread, first 20 days -> last 20 days (basis points) | in the test |", "|---|---|---|---|---|---|"] + [f"| {r['company']} | {r['days']} of {nbd} | {r['given']} + {r['converted']} | {r['first']} | {r['start_bp']:.0f} -> {r['end_bp']:.0f} | {'yes' if r['used'] else 'no (under ' + str(MIN_DAYS) + ' days)'} |" for r in rows]
    ex += ["", "The data: public trade reports under the SEC's Regulation SBSR, from DTCC's repository, 2 Sep 2024 onward (earlier days are no longer offered). Kept for our own testing in an ignored folder; not uploaded; not on the page (terms of re-use not settled, TRACK 3.127)."]
    LD.cmd_run(shifts, C, "leading_cds", "CDS-1", "3.128", ex)
    f = Path("docs/leading_cds.md"); f.write_text(f.read_text().replace(" Single AI borrowers' credit default swap spreads are sold data and are not here.", " The candidates here ARE the credit default swap spreads of single companies, built from public trade reports."))


def cmd_recent(n_days: int):
    """the last days, read directly: each company's spread of the day (the middle one of its trades) and Oracle's trades one by one with their New York time. A look, not a test."""
    X = trades(); X["ny"] = X.t.dt.tz_convert("America/New_York"); X["d"] = pd.to_datetime(X.ny.dt.date); days = sorted(X.d.unique())[-n_days:]; comps = ["Oracle", "Amazon", "Meta", "Alphabet", "Microsoft", "Nvidia", "AMD", "CoreWeave"]
    print(f"Spread of the day in basis points (number of usable trades), trades done before 16:00 New York. The last {len(days)} days with files.")
    print("  day | " + " | ".join(comps))
    for d in days:
        g = X[X.d == d]; print(f"  {pd.Timestamp(d):%a %d %b} | " + " | ".join((f"{g[g.key == c].bp.median():.0f} ({int((g.key == c).sum())})" if (g.key == c).any() else "-") for c in comps))
    o = X[(X.key == "Oracle") & X.d.isin(days[-4:])].sort_values("t"); print("\nOracle's usable trades of the last 4 of those days, one by one (New York time; 'given' = the file gives the spread, otherwise worked out from the one-off payment):")
    for r in o.itertuples(): print(f"  {r.ny:%a %d %b %H:%M:%S} | {r.bp:.0f} bp | {r.how}")
    if not len(o): print("  none")
    print("Paste all of this to Claude.")


def _days(n=6):
    d = datetime.utcnow().date() - timedelta(days=1); out = []
    while len(out) < n:
        if d.weekday() < 5: out.append(d)
        d -= timedelta(days=1)
    return out


def cmd_probe():
    L = ["# Public single-company CDS trades (SEC rule, DTCC repository): the probe", ""]; got = None
    print("Trying to download ONE day's public file of credit swaps from DTCC's repository. Free. No data is kept.")
    for day in _days():
        for pat in PATTERNS:
            url = pat.format(y=day.year, m=f"{day.month:02d}", d=f"{day.day:02d}")
            try:
                raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"}), timeout=60).read()
                z = zipfile.ZipFile(io.BytesIO(raw)); name = z.namelist()[0]; df = pd.read_csv(z.open(name), dtype=str, low_memory=False); got = (day, url, df); print(f"  ANSWERS: {url}  ({len(raw) / 1e6:.1f} MB, file {name}, {len(df):,} rows, {len(df.columns)} columns)"); break
            except Exception as ex: print(f"  no: {url.split('/')[-1]} via {url.split('/')[2]} -- {type(ex).__name__}: {str(ex)[:60]}")
        if got: break
    if not got:
        L += ["None of the remembered addresses answered. The public page to look at by hand: the DTCC 'Public Price Dissemination' dashboard, SEC section (pddata.dtcc.com). Tell Claude what the download link of a 'cumulative' credit file looks like."]
        Path("docs").mkdir(exist_ok=True); Path("docs/cds_public_probe.md").write_text("\n".join(L) + "\n"); print("=> nothing answered. Open pddata.dtcc.com in a browser, go to the SEC section, and tell Claude what the link of a 'Cumulative' credit report looks like. -> docs/cds_public_probe.md"); return
    day, url, df = got; text = df.fillna("").astype(str); blob = text.apply(lambda r: " | ".join(r.values).upper(), axis=1)
    print(f"  columns: {', '.join(df.columns)[:900]}")
    L += [f"Day {day}, address `{url}`: {len(df):,} rows, {len(df.columns)} columns.", "", "Columns: " + ", ".join(f"`{c}`" for c in df.columns), "", "| company | trades that day that name it |", "|---|---|"]
    print("  trades that name a large technology company:")
    for comp, keys in NAMES.items():
        m = blob.apply(lambda s: any(k in s for k in keys)); n = int(m.sum()); L.append(f"| {comp} | {n} |"); print(f"    {comp}: {n}")
        if n and comp in ("Oracle", "Meta", "Alphabet", "Microsoft"):
            for _, r in df[m].head(3).iterrows(): print("       " + " ; ".join(f"{c}={str(v)[:40]}" for c, v in r.items() if isinstance(v, str) and v and any(w in c.lower() for w in ("time", "underl", "price", "spread", "notional", "action", "upi", "product", "expir", "currency")))[:520])
    L += ["", "Nothing was kept on disk. Before any daily collection: read DTCC's terms for this public data, and check the columns that hold the company, the spread and the time."]
    Path("docs").mkdir(exist_ok=True); Path("docs/cds_public_probe.md").write_text("\n".join(L) + "\n"); print("=> the public file exists and can be read. -> docs/cds_public_probe.md. Paste all of this to Claude.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["probe", "fetch", "describe", "series", "test", "recent"]); ap.add_argument("--days", type=int, default=10); ap.add_argument("--since", default=START); ap.add_argument("--shifts", type=int, default=5000); a = ap.parse_args()
    {"probe": cmd_probe, "fetch": lambda: cmd_fetch(a.since), "describe": cmd_describe, "series": cmd_series, "test": lambda: cmd_test(a.shifts), "recent": lambda: cmd_recent(a.days)}[a.cmd]()
