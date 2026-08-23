"""
fetch_fomc_dates.py -- build the FOMC decision-date CSV from the Fed's own pages.

WHY THIS SCRIPT INSTEAD OF TYPING THE DATES
    Hand-transcribing ~90 meeting dates is a silent-failure vector: one wrong
    date corrupts the test with no error raised, which is the exact class of bug
    this project has spent days catching. The Fed embeds the DECISION DATE in
    every statement URL:

        /newsevents/pressreleases/monetary20190130a.htm
                                          ^^^^^^^^

    So the dates are parsed from the source rather than retyped. Each meeting is
    two days; the statement is released at 14:00 ET on the SECOND day, and that
    URL date IS the decision date. No second-day arithmetic needed.

VERIFY BEFORE USING. The script prints per-year counts. The FOMC holds EIGHT
regularly scheduled meetings a year, so any year showing far from 8 means the
page layout changed or unscheduled meetings are included (2020 had several --
those are real events and are kept, but you should see them).

Run:
    python -m src.fetch_fomc_dates --out processed/fomc_decisions.csv
"""
import argparse
import re
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://www.federalreserve.gov"
RECENT = f"{BASE}/monetarypolicy/fomccalendars.htm"
HIST = f"{BASE}/monetarypolicy/fomchistorical{{year}}.htm"
PAT = re.compile(r"monetary(\d{8})a\.htm")
UA = {"User-Agent": "Mozilla/5.0 (research; contact via repo)"}


def scrape(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"    {url}  FAILED: {e}")
        return set()
    hits = set(PAT.findall(html))
    print(f"    {url.rsplit('/', 1)[-1]:32} {len(hits):3d} statement dates")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="processed/fomc_decisions.csv")
    args = ap.parse_args()

    print("fetching FOMC statement URLs from federalreserve.gov ...")
    found = scrape(RECENT)
    for y in range(args.start, args.end + 1):
        found |= scrape(HIST.format(year=y))

    if not found:
        raise SystemExit("no dates found -- page layout may have changed. "
                         "Inspect the HTML before trusting any fallback.")

    d = pd.DatetimeIndex(sorted(pd.to_datetime(sorted(found), format="%Y%m%d")))
    d = d[(d.year >= args.start) & (d.year <= args.end)]

    print(f"\n{len(d)} decision dates, {d.min().date()} -> {d.max().date()}")
    print("per year (EIGHT scheduled meetings is normal; more = unscheduled):")
    vc = pd.Series(1, index=d).groupby(d.year).sum()
    for y, n in vc.items():
        flag = "   <- CHECK" if n < 6 or n > 10 else ""
        print(f"    {y}: {n}{flag}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"date": d.strftime("%Y-%m-%d")}).to_csv(out, index=False)
    print(f"\nwritten -> {out}")
    print("Spot-check a few against the Fed calendar before running any test.")


if __name__ == "__main__":
    main()
