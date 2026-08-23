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
import urllib.error
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
    """Fetch, and on an HTTP error RAISE WITH THE SERVER'S OWN MESSAGE.

    A bare "HTTP Error 400: Bad Request" says nothing about which parameter was
    wrong. APIs almost always explain themselves in the response body; throwing
    that away turns a five-second fix into guesswork."""
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "ignore")[:400]
            except Exception:
                pass
            last = RuntimeError(f"HTTP {e.code} for {url}\n    server said: {body}")
            if e.code < 500:
                raise last                      # client error: retrying will not help
        except Exception as e:
            last = e
        if i < retries - 1:
            time.sleep(1.5 * (i + 1))
    raise last


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
FR_DOCS = ("https://www.federalregister.gov/api/v1/documents.json"
           "?conditions[type][]=PRESDOCU"
           "&conditions[publication_date][gte]={start}"
           "&per_page=1000&page={page}&order=oldest"
           "&fields[]=document_number&fields[]=title"
           "&fields[]=publication_date&fields[]=signing_date"
           "&fields[]=raw_text_url&fields[]=body_html_url"
           "&fields[]=type&fields[]=subtype")


def cmd_political(args):
    """Presidential documents from the Federal Register.

    WHY THIS AND NOT GDELT OR X
      doc_read needs TEXT. GDELT returns article COUNTS -- it can tell you a
      topic spiked but not what was said, so it is a trigger, not a document.
      The X API is ~$200/mo and its HISTORICAL archive is the costly tier; a
      source with no history can never enter step 3, which conditions on
      macro-similar precedent. Truth Social has no public API at all.

      Federal Register: free, no key, full plain text, back to 1994. Executive
      orders and proclamations are DECIDED policy -- the high-`specificity` end
      the reader uses to separate an actual measure from a threat to act.

    QUERY DESIGN, after a 400 on the first attempt
      The first version filtered server-side on
      conditions[presidential_document_type][] with guessed enum values and was
      rejected. Rather than guess again, this queries ONLY on
      conditions[type][]=PRESDOCU -- the one parameter that is certain -- and
      filters by document type CLIENT-SIDE on whatever the API actually
      returns. Slower, but it cannot be broken by an enum name being wrong, and
      the observed type values are printed so the filter can be tightened later
      from evidence instead of assumption.

    COVERAGE GAP, stated because it biases every result
      This is decided policy only. Statements, posts and rhetoric -- the
      low-specificity end, which is exactly where a market-moving threat lives
      -- are NOT here. Their absence is a gap, not evidence.
    """
    out = DOCS / "political"; out.mkdir(parents=True, exist_ok=True)
    want = {t.strip().lower() for t in args.types.split(",") if t.strip()}

    docs, page = [], 1
    while page <= args.max_pages:
        try:
            js = json.loads(get(FR_DOCS.format(start=args.start, page=page)))
        except Exception as e:
            print(f"  page {page} FAILED: {e}")
            break
        got = js.get("results", [])
        if not got:
            break
        docs += got
        total = js.get("count")
        print(f"  page {page}: {len(got)} docs (API reports {total} total)")
        if len(docs) >= (total or 0) or len(got) < 1000:
            break
        page += 1
        time.sleep(args.sleep)

    if not docs:
        print("  no documents returned -- inspect the error above before retrying")
        return

    seen = {}
    for d in docs:
        t = (d.get("presidential_document_type") or d.get("subtype")
             or d.get("type") or "unknown")
        seen[str(t).lower()] = seen.get(str(t).lower(), 0) + 1
    print("\n  document types actually returned by the API:")
    for k, v in sorted(seen.items(), key=lambda x: -x[1]):
        mark = "  <- kept" if (not want or k in want) else ""
        print(f"    {k:32} {v:5d}{mark}")

    got_n = skipped = 0
    for d in docs:
        t = str(d.get("presidential_document_type") or d.get("subtype")
                or d.get("type") or "unknown").lower()
        if want and t not in want:
            continue
        pub = d.get("publication_date") or d.get("signing_date")
        if not pub:
            continue
        stamp = pd.to_datetime(pub).strftime("%Y%m%d")
        num = str(d.get("document_number") or "").replace("-", "")
        f = out / f"{stamp}_{t[:4]}{num}.txt"
        if f.exists() and not args.refetch:
            continue
        url = d.get("raw_text_url") or d.get("body_html_url")
        if not url:
            skipped += 1
            continue
        try:
            txt = get(url)
        except Exception:
            skipped += 1
            continue
        if "<" in txt[:200]:
            txt = clean(txt)
        txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
        if len(txt.split()) < 80:
            continue
        f.write_text(f"[{t}] {d.get('title','')}\n\n{txt}")
        got_n += 1
        if got_n >= args.limit:
            break
        time.sleep(args.sleep)

    print(f"\npolitical: {got_n} documents -> {out}/  ({skipped} unfetchable)")
    print("  Dated by PUBLICATION date -- when it entered the public record.")
    print("  COVERAGE GAP: decided policy only. Statements, posts and rhetoric")
    print("  are not here; their absence is a gap, not evidence.")


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
    p.add_argument("--max-pages", type=int, default=6)
    p.add_argument("--refetch", action="store_true")
    p.add_argument("--sleep", type=float, default=0.2)
    p.set_defaults(fn=cmd_political)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
