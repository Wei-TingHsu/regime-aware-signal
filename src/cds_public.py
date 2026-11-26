"""cds_public.py -- can single-company CDS trades be followed automatically and free? A PROBE only (TRACK 3.126).

Since 2022 a US rule (the SEC's Regulation SBSR) makes swap data repositories publish every single-company CDS trade soon after it happens: the company it is written on,
the price as a spread in basis points, the time, the size (capped). The largest repository is DTCC's (DDR). If its daily public files can be downloaded, an Oracle CDS
series -- and one for every large technology company -- can be built from real trades, free.

    python -m src.cds_public probe        # free; tries to download ONE day's public file of credit swaps, and reports what is in it. Keeps no data; writes docs/cds_public_probe.md.

NOT yet done, on purpose: no daily collection. The file addresses below are from Claude's memory (unverified), and DTCC's terms for this public data have not been read yet.
"""
from __future__ import annotations
import argparse, io, urllib.request, zipfile
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PATTERNS = ["https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDITS_{y}_{m}_{d}.zip",
            "https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDIT_{y}_{m}_{d}.zip",
            "https://kgc0418-tdw-data-0.s3.amazonaws.com/sec/eod/SEC_CUMULATIVE_CREDITS_{y}_{m}_{d}.zip"]
NAMES = {"Oracle": ["ORACLE"], "Meta": ["META PLATFORMS", "FACEBOOK"], "Alphabet": ["ALPHABET", "GOOGLE"], "Microsoft": ["MICROSOFT"], "Amazon": ["AMAZON"], "Apple": ["APPLE INC"], "Nvidia": ["NVIDIA"], "Broadcom": ["BROADCOM"],
         "Intel": ["INTEL CORP"], "AMD": ["ADVANCED MICRO"], "Micron": ["MICRON"], "IBM": ["INTERNATIONAL BUSINESS MACHINES", "IBM CORP"], "Cisco": ["CISCO"], "Dell": ["DELL"], "CoreWeave": ["COREWEAVE"], "Tesla": ["TESLA"], "Qualcomm": ["QUALCOMM"]}


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
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["probe"]); ap.parse_args(); cmd_probe()
