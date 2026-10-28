"""fetch_comex_stocks.py -- CME's daily COMEX depository report for silver (and gold), kept raw and parsed.

docs/prereg_silver_stocks.md section 2. The URL and the sheet layout are UNVERIFIED from the sandbox the module was written in
(the CME host is not on its allow-list), so the module is defensive: --probe reports what the server answers before anything is
saved; the daily run keeps the raw file write-once by date and only then tries to parse it; when the layout is not what it
expects it prints the sheet and keeps the raw file, so nothing is lost and the parser can be fixed against a real file.

  python -m src.fetch_comex_stocks --probe          # HTTP status, content type, size for each URL; nothing written
  python -m src.fetch_comex_stocks                  # today's files -> data_provenance/comex_stocks/raw/, rows -> processed/comex_<metal>_stocks.csv
  python -m src.fetch_comex_stocks --parse-only     # re-parse every raw file on disk into the CSVs (no network)

Needs: pandas and an .xls reader (`pip install xlrd`); .xlsx needs openpyxl. The report is published once per business day and
describes the previous session's positions; the row date is the DOWNLOAD date -- the report's own 'as of' date is parsed into
`report_date` when the sheet carries one.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

URLS = {"silver": "https://www.cmegroup.com/delivery_reports/Silver_stocks.xls",
        "gold": "https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls"}
RAW = Path("data_provenance/comex_stocks/raw")
OUT = Path("processed")
UA = {"User-Agent": "Mozilla/5.0 (regime-aware-signal research; depository report collector)"}
COLS = ["registered", "eligible", "total", "received", "withdrawn", "adjustment"]


def fetch(url: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "") if e.headers else "", b""


def probe():
    for metal, url in URLS.items():
        code, ctype, body = fetch(url)
        kind = "xls (BIFF)" if body[:4] == b"\xd0\xcf\x11\xe0" else "xlsx (zip)" if body[:2] == b"PK" else "html/text" if body[:1] in (b"<", b"\n", b" ") else "unknown"
        print(f"{metal:6s} HTTP {code}  {len(body):>9,} bytes  type {ctype or '?'}  looks like {kind}  <- {url}")
    print("A 200 with an xls/xlsx body means the URL is right; a 403/404 or html means the address or the host's rules differ -- fix URLS before scheduling.")


def _num(x):
    try:
        return float(str(x).replace(",", "").replace("(", "-").replace(")", "").strip())
    except Exception:
        return None


def parse(raw: Path, metal: str, day: str) -> pd.DataFrame | None:
    """Find the sheet/row block that carries Registered and Eligible per depository. Layout-agnostic: scans every sheet for a header
    row containing both words, then reads rows until a blank first cell or a 'Total' row."""
    try:
        sheets = pd.read_excel(raw, sheet_name=None, header=None)
    except Exception as e:
        print(f"  {raw.name}: cannot open ({type(e).__name__}: {e}); raw file kept. `pip install xlrd` for .xls, openpyxl for .xlsx."); return None
    rows, report_date = [], None
    for name, df in sheets.items():
        txt = df.fillna("").astype(str)
        for i in range(len(txt)):
            line = " ".join(str(x) for x in txt.iloc[i].tolist()).lower()
            m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", line)
            if m and report_date is None and ("report" in line or "as of" in line or "date" in line):
                report_date = m.group(1)
            if "registered" in line and "eligible" in line:
                hdr = [str(c).lower() for c in txt.iloc[i].tolist()]
                col = {}
                for k in COLS:
                    for j, c in enumerate(hdr):
                        if k[:6] in c and j not in col.values():
                            col[k] = j; break
                for r in range(i + 1, len(df)):
                    first = str(df.iloc[r, 0]).strip()
                    if first in ("", "nan"):
                        if rows and rows[-1].get("sheet") == name:
                            break
                        continue
                    vals = {k: _num(df.iloc[r, j]) for k, j in col.items()}
                    if all(v is None for v in vals.values()):
                        continue
                    rows.append(dict(date=day, metal=metal, sheet=name, depository=first, **vals))
                    if first.lower().startswith("total"):
                        break
                break
    if not rows:
        print(f"  {raw.name}: no header row with 'Registered' and 'Eligible' found -- raw kept; first rows of each sheet:")
        for name, df in sheets.items():
            print(f"   [{name}]"); print(df.head(12).to_string(max_cols=10, max_colwidth=22))
        return None
    out = pd.DataFrame(rows); out["report_date"] = report_date
    return out


def append(df: pd.DataFrame, metal: str):
    p = OUT / f"comex_{metal}_stocks.csv"
    if p.exists():
        old = pd.read_csv(p)
        if (old["date"] == df["date"].iloc[0]).any():
            print(f"  {p.name}: {df['date'].iloc[0]} already present -- not appended (write-once)"); return
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(p, index=False); print(f"  -> {p} ({len(df)} rows)")


def run(parse_only: bool):
    RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(exist_ok=True)
    day = datetime.now().strftime("%Y%m%d")
    if parse_only:
        files = sorted(RAW.glob("*_*.xls*"))
        for f in files:
            d, metal = f.stem.split("_", 1)
            df = parse(f, metal, d)
            if df is not None:
                append(df, metal)
        return
    for metal, url in URLS.items():
        code, ctype, body = fetch(url)
        if code != 200 or len(body) < 1000 or body[:1] == b"<":
            print(f"{metal}: HTTP {code}, {len(body)} bytes, type {ctype} -- nothing saved (run --probe)"); continue
        ext = ".xlsx" if body[:2] == b"PK" else ".xls"
        raw = RAW / f"{day}_{metal}{ext}"
        if raw.exists():
            print(f"{metal}: {raw.name} already on disk -- write-once, not replaced")
        else:
            raw.write_bytes(body); print(f"{metal}: saved {raw} ({len(body):,} bytes)")
        df = parse(raw, metal, day)
        if df is not None:
            tot = df[df["depository"].str.lower().str.startswith("total")]
            if len(tot):
                t = tot.iloc[-1]; print(f"  {metal} total: registered {t.get('registered')}, eligible {t.get('eligible')} (report date {df['report_date'].iloc[0]})")
            append(df, metal)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--parse-only", action="store_true")
    a = ap.parse_args()
    if a.probe:
        probe()
    else:
        run(a.parse_only)
