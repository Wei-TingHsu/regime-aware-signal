"""
fomc_corpus.py -- download the FOMC statement TEXT for every decision date.

PROBLEM 3, FIRST PIECE. Every event test in this project so far treated an event
as a TIMESTAMP: "do returns move after date T". None of them read what the Fed
actually SAID. This script builds the corpus that makes content-based reading
possible.

    fetch_fomc_dates.py  ->  WHEN the Fed decided
    fomc_corpus.py       ->  WHAT the Fed said          <-- this file
    fomc_llm_read.py     ->  what it MEANS, per asset

The statement URL is deterministic from the decision date, which is why the date
fetcher parsed dates out of those same URLs:

    /newsevents/pressreleases/monetary{YYYYMMDD}a.htm

Text is stored one file per decision under data_provenance/fomc/ so the corpus is
versioned, auditable, and re-readable without re-fetching. A future LLM read is
then reproducible against a fixed text, not against whatever the site serves that
day.

WHAT THIS DOES NOT DO
    No interpretation. No scoring. Fetch and store only. Interpretation is a
    separate step BY DESIGN: if fetching and reading are entangled, you can never
    re-read the same text with a different prompt and compare.

Run:
    python -m src.fomc_corpus --dates processed/fomc_decisions.csv
    python -m src.fomc_corpus --dates processed/fomc_decisions.csv --refetch
"""
import argparse
import html
import re
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://www.federalreserve.gov/newsevents/pressreleases/monetary{d}a.htm"
UA = {"User-Agent": "Mozilla/5.0 (academic research; regime-aware-signal)"}
OUT = Path("data_provenance/fomc")


def clean(raw):
    """HTML -> plain text. Deliberately simple: no parser dependency, and the
    Fed's press releases are clean single-column documents."""
    s = re.sub(r"(?is)<(script|style|head).*?</\1>", " ", raw)
    s = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</h\d>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def body(text):
    """Trim site chrome to the statement itself.

    Two failure modes were observed on the real corpus and both are handled:
      * statements whose opener matched but whose VOTING ROSTER marker did not,
        so the text ran on into the page footer (~1000 words instead of ~675);
      * 2019-2020 pages with a different layout whose opener never matched at
        all, leaving 'Skip to main content / An official website of the United
        States Government' at the head (~1900 words).

    The reliable anchor is the Fed's own release line -- 'For release at 2:00
    p.m.' -- which immediately precedes every statement. Openers are the
    fallback. Multiple end markers are tried, so a missing voting roster no
    longer means 'keep everything'.
    """
    rel = list(re.finditer(r"(?i)For (?:release|immediate release)[^\n]{0,80}", text))
    s = None
    if rel:
        s = rel[-1].end()
    else:
        m = re.search(r"(?im)^\s*(Recent indicators|Information received|"
                      r"The Committee decided|The Federal Open Market Committee|"
                      r"Consistent with its statutory mandate|"
                      r"The Federal Reserve is prepared|The coronavirus|"
                      r"Although .{0,40}indicators)", text)
        s = m.start() if m else None
    if s is None:
        return text, False

    ENDS = (r"Voting for the monetary policy action",
            r"Voting against (?:the|this) action",
            r"Implementation Note issued",
            r"For media inquiries",
            r"Last Update:",
            r"Board of Governors of the Federal Reserve System\s*$")
    e = len(text)
    for pat in ENDS:
        m = re.search(pat, text[s:], flags=re.I)
        if m:
            e = min(e, s + m.start())
    return text[s:e].strip(), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", default="processed/fomc_decisions.csv")
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.5)
    args = ap.parse_args()

    d = pd.read_csv(args.dates)
    col = next(c for c in d.columns if "date" in c.lower())
    dates = pd.DatetimeIndex(pd.to_datetime(d[col])).sort_values()
    OUT.mkdir(parents=True, exist_ok=True)

    print(f"corpus target: {len(dates)} statements -> {OUT}/")
    got = skipped = failed = untrimmed = 0
    lens = []
    for dt in dates:
        stamp = dt.strftime("%Y%m%d")
        f = OUT / f"{stamp}.txt"
        if f.exists() and not args.refetch:
            skipped += 1
            lens.append(len(f.read_text().split()))
            continue
        url = BASE.format(d=stamp)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"  {stamp}  FAILED: {e}")
            failed += 1
            continue
        txt, trimmed = body(clean(raw))
        if not trimmed:
            untrimmed += 1
        f.write_text(txt)
        lens.append(len(txt.split()))
        got += 1
        time.sleep(args.sleep)

    print(f"\nfetched {got}, already present {skipped}, failed {failed}")
    if untrimmed:
        print(f"  {untrimmed} statement(s) kept UNTRIMMED -- the opening marker "
              f"was not found. Layout may have changed; inspect those files.")
    if lens:
        s = pd.Series(lens)
        print(f"word count: median {s.median():.0f}, min {s.min()}, max {s.max()}")
        print("  A 2011-2026 FOMC statement runs roughly 300-800 words.")
        odd = s[(s < 150) | (s > 2000)]
        if len(odd):
            print(f"  {len(odd)} file(s) outside that range -- CHECK THEM before "
                  f"any interpretation step reads the corpus.")
    print(f"\ncorpus at {OUT}/ -- commit it so every later read is reproducible "
          f"against fixed text.")


if __name__ == "__main__":
    main()
