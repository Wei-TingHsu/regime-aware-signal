"""
fetch_sources.py -- pull every source that HAS a free structured feed into the
doc_read drop folder.

    python -m src.fetch_sources minutes
    python -m src.fetch_sources edgar --tickers NVDA,MSFT,TSM --limit 40

WHAT IS AND IS NOT FETCHABLE
    fetchable here      FOMC minutes        federalreserve.gov
                        SEC 8-K filings     data.sec.gov (free, no key)
    fetchable elsewhere political / Iran    GDELT via BigQuery -- you already
                                            have the infrastructure and 944
                                            days of history. Prefer it to the X
                                            API, which costs ~$200/mo and whose
                                            HISTORICAL archive is the expensive
                                            part; without history a source can
                                            never enter step 3.
    manual only         transcripts         no free structured source. Save as
                        bank_research       data_provenance/docs/<type>/
                                            YYYYMMDD_<id>.txt and doc_read picks
                                            them up unchanged.

DATING RULE: THE FILE DATE IS WHEN THE DOCUMENT BECAME PUBLIC
    Not when the meeting happened, not when the quarter ended. FOMC minutes are
    released ~3 weeks AFTER the decision they describe; filing them under the
    meeting date would place the event three weeks before anyone could read it,
    which is look-ahead built into the filename. Release dates are parsed from
    the Fed's own calendar, and the +21-day fallback is reported when used.

SEC ETIQUETTE
    data.sec.gov requires a descriptive User-Agent with contact details and asks
    for <=10 requests/second. Both are honoured. Set SEC_CONTACT to your email.
"""
import argparse
import html
import json
import re
import time
import urllib.request
from pathlib import Path

import pandas as pd

DOCS = Path("data_provenance/docs")
UA = {"User-Agent": "regime-aware-signal academic research "
                    f"({__import__('os').environ.get('SEC_CONTACT', 'set SEC_CONTACT')})"}
FED_CAL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
FED_HIST = "https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm"
MIN_URL = "https://www.federalreserve.gov/monetarypolicy/fomcminutes{d}.htm"
TICKERS = "https://www.sec.gov/files/company_tickers.json"
SUBS = "https://data.sec.gov/submissions/CIK{cik}.json"
ARCH = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}"


def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def clean(raw):
    s = re.sub(r"(?is)<(script|style|head).*?</\1>", " ", raw)
    s = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</h\d>|</tr>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def trim(text, starts, ends):
    m = None
    for p in starts:
        m = re.search(p, text, flags=re.I)
        if m:
            break
    s = m.start() if m else 0
    e = len(text)
    for p in ends:
        m2 = re.search(p, text[s:], flags=re.I)
        if m2:
            e = min(e, s + m2.start())
    return text[s:e].strip(), bool(m)


# --------------------------------------------------------------------------- #
def cmd_minutes(args):
    """Minutes URL keys on the MEETING date; the file is dated on RELEASE."""
    out = DOCS / "fomc_minutes"; out.mkdir(parents=True, exist_ok=True)
    dec = pd.read_csv(args.dates)
    col = next(c for c in dec.columns if "date" in c.lower())
    meetings = pd.DatetimeIndex(pd.to_datetime(dec[col])).sort_values()

    # release dates: the Fed prints "(Released January 3, 2024)" beside each
    # minutes link. Parse them; fall back to +21 days and say so.
    pages = [get(FED_CAL)]
    for y in range(meetings.min().year, meetings.max().year + 1):
        try:
            pages.append(get(FED_HIST.format(y=y)))
        except Exception:
            pass
    blob = " ".join(pages)
    rel = {}
    for m in re.finditer(r"fomcminutes(\d{8})\.htm.{0,400}?Released\s+"
                         r"([A-Z][a-z]+ \d{1,2},\s*\d{4})", blob, flags=re.S):
        try:
            rel[m.group(1)] = pd.to_datetime(m.group(2))
        except Exception:
            pass
    print(f"parsed {len(rel)} explicit release dates from the Fed calendar")

    got = miss = fb = 0
    for d in meetings:
        stamp = d.strftime("%Y%m%d")
        rd = rel.get(stamp)
        if rd is None:
            rd = d + pd.Timedelta(days=21)
            fb += 1
        f = out / f"{rd.strftime('%Y%m%d')}_meeting{stamp}.txt"
        if f.exists() and not args.refetch:
            continue
        try:
            raw = get(MIN_URL.format(d=stamp))
        except Exception:
            miss += 1
            continue
        txt, ok = trim(clean(raw),
                       [r"A meeting of the Federal Open Market Committee",
                        r"Developments in Financial Markets",
                        r"The Manager(?: of the System Open Market Account)? "
                        r"(?:turned first |)"],
                       [r"Notation Vote", r"Last Update:",
                        r"Board of Governors of the Federal Reserve System\s*$"])
        f.write_text(txt)
        got += 1
        time.sleep(args.sleep)
    print(f"minutes: fetched {got}, unavailable {miss}, "
          f"release date INFERRED (+21d) for {fb}")
    if fb:
        print("  inferred dates are approximate -- the Fed shifts releases around "
              "holidays. Spot-check a few before they feed a dated test.")
    print(f"-> {out}/   (files dated by RELEASE, meeting date kept in the id)")


# --------------------------------------------------------------------------- #
def cmd_edgar(args):
    """8-K filings. Item 2.02 IS the earnings release, so this covers both
    earnings line-items and other material corporate events."""
    out = DOCS / "earnings_8k"; out.mkdir(parents=True, exist_ok=True)
    tick = [t.strip().upper() for t in args.tickers.split(",")]
    print("resolving tickers -> CIK ...")
    cmap = json.loads(get(TICKERS))
    lookup = {v["ticker"].upper(): str(v["cik_str"]).zfill(10)
              for v in cmap.values()}
    missing = [t for t in tick if t not in lookup]
    if missing:
        print(f"  not found in the SEC ticker file: {', '.join(missing)}")
    tick = [t for t in tick if t in lookup]

    total = 0
    for t in tick:
        cik = lookup[t]
        try:
            sub = json.loads(get(SUBS.format(cik=cik)))
        except Exception as e:
            print(f"  {t}: submissions FAILED: {e}")
            continue
        r = sub.get("filings", {}).get("recent", {})
        rows = list(zip(r.get("form", []), r.get("filingDate", []),
                        r.get("accessionNumber", []),
                        r.get("primaryDocument", []), r.get("items", [])))
        forms = {f.strip().upper() for f in args.forms.split(",")}
        eights = [x for x in rows if x[0].upper() in forms]
        # 6-K has no item codes, so the item filter must not silently drop it
        if args.items:
            want = set(args.items.split(","))
            eights = [x for x in eights
                      if x[0].upper() != "8-K"
                      or any(i.strip() in want
                             for i in (x[4] or "").split(","))]
        eights = eights[:args.limit]
        n = 0
        for form, fdate, acc, doc, items in eights:
            if not doc:
                continue
            stamp = pd.to_datetime(fdate).strftime("%Y%m%d")
            f = out / f"{stamp}_{t}.txt"
            if f.exists() and not args.refetch:
                continue
            url = ARCH.format(cik=str(int(cik)), acc=acc.replace("-", ""), doc=doc)
            try:
                txt = clean(get(url))
            except Exception:
                continue
            if len(txt.split()) < 60:
                continue                      # cover page only, no substance
            f.write_text(f"[{form} items: {items or 'n/a'}]\n\n{txt}")
            n += 1
            time.sleep(max(args.sleep, 0.11))   # SEC asks <=10 req/sec
        kinds = sorted({x[0] for x in eights})
        print(f"  {t:6} CIK {cik}  {len(eights):3d} matching "
              f"{'/'.join(kinds) or 'none'}  -> {n} saved")
        total += n
    print(f"\n8-K: {total} documents -> {out}/")
    print("  Item 2.02 = results of operations (the earnings release itself).")
    print("  Filed date is the PUBLIC date, which is the correct event date.")


# --------------------------------------------------------------------------- #
FR_API = ("https://www.federalregister.gov/api/v1/documents.json"
          "?conditions[type][]=PRESDOCU"
          "&conditions[publication_date][gte]={start}"
          "&conditions[presidential_document_type][]={ptype}"
          "&per_page=1000&order=oldest"
          "&fields[]=document_number&fields[]=title"
          "&fields[]=publication_date&fields[]=signing_date"
          "&fields[]=raw_text_url&fields[]=presidential_document_type")


def cmd_political(args):
    """Presidential documents from the Federal Register.

    WHY THIS AND NOT GDELT OR X
      doc_read needs TEXT. GDELT returns article COUNTS, so it can tell you a
      topic spiked but not what was said -- useful as a trigger, useless as a
      document. The X API is ~$200/mo and its historical archive is the costly
      part; a source with no history can never enter step 3.

      The Federal Register API is free, needs no key, returns full plain text,
      and reaches back to 1994. Executive orders and proclamations are DECIDED
      policy, which is the high-`specificity` end of the scale the reader uses
      to separate an actual measure from a threat to act. Tariff and Iran
      sanctions actions land here as executive orders.

    WHAT IT DOES NOT COVER
      Statements, posts and rhetoric -- the low-specificity end. Those are the
      X/Truth Social problem and remain uncovered. So this source is biased
      toward the decided end by construction, and that must be stated when
      results are read: an absence of low-specificity political events here is
      a coverage gap, not evidence they do not matter.
    """
    out = DOCS / "political"; out.mkdir(parents=True, exist_ok=True)
    got = 0
    for ptype in [p.strip() for p in args.types.split(",")]:
        url = FR_API.format(start=args.start, ptype=ptype)
        try:
            js = json.loads(get(url))
        except Exception as e:
            print(f"  {ptype}: API FAILED: {e}")
            continue
        docs = js.get("results", [])
        print(f"  {ptype:22} {len(docs):4d} documents since {args.start}")
        for d in docs[:args.limit]:
            # publication_date is when it entered the public record
            pub = d.get("publication_date") or d.get("signing_date")
            if not pub:
                continue
            stamp = pd.to_datetime(pub).strftime("%Y%m%d")
            num = (d.get("document_number") or "").replace("-", "")
            f = out / f"{stamp}_{ptype[:4]}{num}.txt"
            if f.exists() and not args.refetch:
                continue
            ru = d.get("raw_text_url")
            if not ru:
                continue
            try:
                txt = get(ru)
            except Exception:
                continue
            txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
            if len(txt.split()) < 80:
                continue
            f.write_text(f"[{ptype}] {d.get('title','')}\n\n{txt}")
            got += 1
            time.sleep(args.sleep)
    print(f"\npolitical: {got} documents -> {out}/")
    print("  Dated by PUBLICATION date (when it entered the public record).")
    print("  COVERAGE GAP recorded: decided policy only. Statements, posts and")
    print("  rhetoric are not here -- absence of them is a gap, not evidence.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("minutes")
    m.add_argument("--dates", default="processed/fomc_decisions.csv")
    m.add_argument("--refetch", action="store_true")
    m.add_argument("--sleep", type=float, default=0.4)
    m.set_defaults(fn=cmd_minutes)

    e = sub.add_parser("edgar")
    e.add_argument("--tickers",
                   default="NVDA,TSM,ASML,MU,INTC,MSFT,ORCL,TSLA,LMT")
    e.add_argument("--items", default="2.02",
                   help="comma-separated 8-K item codes; empty for all. "
                        "Ignored for 6-K, which carries no item codes.")
    e.add_argument("--forms", default="8-K,6-K",
                   help="8-K is the DOMESTIC material-event form. Foreign "
                        "private issuers (TSM Taiwan, ASML Netherlands) file "
                        "6-K instead and will return zero 8-Ks forever.")
    e.add_argument("--limit", type=int, default=40)
    e.add_argument("--refetch", action="store_true")
    e.add_argument("--sleep", type=float, default=0.15)
    e.set_defaults(fn=cmd_edgar)

    p = sub.add_parser("political")
    p.add_argument("--types",
                   default="executive_order,proclamation,presidential_memorandum")
    p.add_argument("--start", default="2011-01-01")
    p.add_argument("--limit", type=int, default=400)
    p.add_argument("--refetch", action="store_true")
    p.add_argument("--sleep", type=float, default=0.2)
    p.set_defaults(fn=cmd_political)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
