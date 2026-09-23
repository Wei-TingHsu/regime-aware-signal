"""
Fetch FOMC statements into data_provenance/docs/fomc_statement/YYYYMMDD.txt.

Written 2026-09-24. Until this date no script in the repository wrote to
fomc_statement/: the 131 statements on disk were pulled in August by hand or by a
one-off, and the nightly job (Federal Register only) could never see a new one.
The 16 Sep 2026 statement was therefore never fetched, never read, and the
16 Sep report was correctly deferred rather than frozen empty.

Source: https://www.federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm
(the Fed's fixed URL pattern for FOMC statements; public domain).

Rules:
  - a file that exists is never rewritten (--refetch to override)
  - a 404 means "not published yet" (a future date in the CSV), not an error
  - only the article body is kept; navigation and boilerplate are stripped
  - dates come from processed/fomc_decisions.csv, or --dates, or both

Usage:
  python -m src.fetch_fomc_statements                       # every CSV date missing on disk
  python -m src.fetch_fomc_statements --days 60             # only CSV dates within the last 60 days (nightly)
  python -m src.fetch_fomc_statements --dates 2026-09-16
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

OUT = Path("data_provenance/docs/fomc_statement")
CSV = Path("processed/fomc_decisions.csv")
URL = "https://www.federalreserve.gov/newsevents/pressreleases/monetary{ymd}a.htm"
UA = "regime-aware-signal research (contact in .env SEC_CONTACT)"


def _dates_from_csv(path: Path) -> list[date]:
    if not path.exists():
        return []
    df = pd.read_csv(path)
    col = df.columns[0]
    out = []
    for v in df[col].astype(str):
        try:
            out.append(pd.Timestamp(v).date())
        except Exception:
            pass
    return out


def _article_text(page: str) -> str:
    """Statement body only, matching the scope of the 131 August files: from the
    first 'The Committee decided' through the voting paragraph. The article div
    nests other divs, so the region is cut by markers rather than by tag depth."""
    start = page.find('id="article"')
    start = start if start > 0 else 0
    ends = [page.find(m, start) for m in ("Implementation Note", 'id="footer"', "<footer", "Last Update")]
    ends = [e for e in ends if e > start]
    end = min(ends) if ends else len(page)
    body = page[start:end]
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    body = re.sub(r"</(p|div|li|h[1-6]|br)>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n+", "\n\n", body).strip()
    # Start at the preamble, not at "The Committee decided": in the 2026 format the
    # vote count ("approved ... by a 12-0 vote") lives in the preamble and nowhere
    # else when the vote is unanimous. Only site navigation is dropped ahead of it.
    k = -1
    for m in ("The Federal Open Market Committee approved", "For release at", "The Committee decided", "The Committee"):
        k = body.find(m)
        if k >= 0:
            break
    if k > 0:
        body = body[k:]
    for m in ("For media inquiries", "Implementation Note", "Last Update"):   # trailing chrome
        j = body.find(m)
        if j > 0:
            body = body[:j]
    return body.strip()


def fetch_one(d: date, refetch: bool, sleep: float) -> str:
    ymd = d.strftime("%Y%m%d")
    f = OUT / f"{ymd}.txt"
    if f.exists() and not refetch:
        return "exists"
    req = urllib.request.Request(URL.format(ymd=ymd), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            page = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "not published"
        return f"HTTP {e.code}"
    except Exception as e:
        return f"error {type(e).__name__}"
    text = _article_text(page)
    if len(text.split()) < 80:
        return f"too short ({len(text.split())} words) -- page layout may have changed; NOT written"
    OUT.mkdir(parents=True, exist_ok=True)
    f.write_text(text)
    time.sleep(sleep)
    return f"written ({len(text.split())} words)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(CSV))
    ap.add_argument("--dates", help="comma-separated YYYY-MM-DD, added to the CSV dates")
    ap.add_argument("--days", type=int, help="only dates within the last N days (nightly use)")
    ap.add_argument("--refetch", action="store_true",
                    help="rewrite files for the --dates given; never touches CSV dates")
    ap.add_argument("--refetch-all", action="store_true",
                    help="rewrite EVERY file. A corpus change: re-read and re-baseline afterwards "
                         "(CURRENT_STATE 18.8). On 2026-09-24 plain --refetch did this by accident.")
    ap.add_argument("--sleep", type=float, default=0.5)
    a = ap.parse_args()

    explicit = {datetime.strptime(x.strip(), "%Y-%m-%d").date() for x in (a.dates or "").split(",") if x.strip()}
    dates = set(_dates_from_csv(Path(a.csv))) | explicit
    today = date.today()
    dates = sorted(d for d in dates if d <= today)          # never ask the Fed for tomorrow
    if a.days:
        dates = [d for d in dates if (today - d).days <= a.days]
    print(f"FOMC statements: {len(dates)} candidate date(s) -> {OUT}")
    counts = {}
    for d in dates:
        r = fetch_one(d, a.refetch_all or (a.refetch and d in explicit), a.sleep)
        counts[r.split(" ")[0]] = counts.get(r.split(" ")[0], 0) + 1
        if r != "exists":
            print(f"  {d}: {r}")
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
