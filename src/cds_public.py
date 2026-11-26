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
import pandas as pd

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
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["probe", "fetch", "describe"]); ap.add_argument("--since", default=START); a = ap.parse_args()
    {"probe": cmd_probe, "fetch": lambda: cmd_fetch(a.since), "describe": cmd_describe}[a.cmd]()
