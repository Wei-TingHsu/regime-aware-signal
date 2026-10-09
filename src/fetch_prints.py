"""
T16 Part A -- fetch scheduled data-print releases into data_provenance/docs/data_print/<YYYYMMDD>_<name>.txt
and their first-print numbers into processed/prints.csv. Registered: docs/prereg_prints_and_attribution.md A1-A2.

Layer 1 (numbers, $0, no LLM): ALFRED vintages via fredapi -> processed/prints.csv with columns
  date, name, series, actual_first_print, prior_first_print, revision_of_prior, expectation_source, expected, surprise
  expectation_source is 'naive_prior' for the backfill (registered A2 item 3); 'market_5min' is filled forward by S5 later.

Layer 3 (text, read by the LLM later): the release text from the agency archive. URL patterns are NOT assumed:
  --inspect <name> prints the archive index page's links so the pattern is confirmed on the first run, then
  --fetch <name> writes files. A release whose text cannot be found still gets its Layer-1 row.

  python -m src.fetch_prints --numbers                 # Layer 1 for all series, 2006 -> today
  python -m src.fetch_prints --inspect empsit          # show archive links (BLS Employment Situation)
  python -m src.fetch_prints --fetch empsit --since 2006-01-01
"""
from __future__ import annotations
import argparse, html, os, re, sys, time, urllib.request
from pathlib import Path
import pandas as pd

DOCS = Path("data_provenance/docs/data_print"); CSV = Path("processed/prints.csv")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 regime-aware-signal-research"
SERIES = {  # name -> (ALFRED series, agency, archive index page)
    "empsit": ("PAYEMS", "BLS", "https://www.bls.gov/bls/news-release/empsit.htm"),
    "unrate": ("UNRATE", "BLS", None),
    "cpi":    ("CPIAUCSL", "BLS", "https://www.bls.gov/bls/news-release/cpi.htm"),
    "cpi_core": ("CPILFESL", "BLS", None),
    "ppi":    ("PPIFIS", "BLS", "https://www.bls.gov/bls/news-release/ppi.htm"),
    "claims": ("ICSA", "DOL", "https://www.dol.gov/newsroom/economicdata"),
    "gdp":    ("GDP", "BEA", "https://apps.bea.gov/histdata/"),
    "pce":    ("PCEPI", "BEA", None),
    "retail": ("RSAFS", "Census", "https://www.census.gov/retail/marts/historic_releases.html"),
}


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def numbers(since="2006-01-01"):
    from dotenv import load_dotenv; load_dotenv()
    from fredapi import Fred
    fred = Fred(api_key=os.environ["FRED_API_KEY"]); rows = []
    for name, (sid, agency, _) in SERIES.items():
        for attempt in range(4):
            try:
                ar = fred.get_series_all_releases(sid); break
            except Exception as e:
                err = e; time.sleep(3 * (attempt + 1)); ar = None
        if ar is None:
            print(f"  {name}: FRED unavailable ({type(err).__name__}); skipped"); continue
        ar = ar.dropna(subset=["value"]).copy()                      # 9 Oct: ALFRED carries withheld observations as None
        ar["realtime_start"] = pd.to_datetime(ar["realtime_start"]); ar["date"] = pd.to_datetime(ar["date"])
        # first print of each observation = the row with the earliest realtime_start for that observation date
        first = ar.sort_values("realtime_start").groupby("date").first().reset_index()
        first = first[first.realtime_start >= pd.Timestamp(since)].sort_values("date")
        # weekly claims are levels; monthly series: use the first-print CHANGE vs the prior month's first print for payrolls, level for rates/indices
        for i in range(1, len(first)):
            cur, prev = first.iloc[i], first.iloc[i - 1]
            actual = float(cur["value"]); prior = float(prev["value"])
            # revision of prior: prior observation's value as published in the current release vintage
            rev_rows = ar[(ar["date"] == prev["date"]) & (ar["realtime_start"] <= cur["realtime_start"])].sort_values("realtime_start")
            revised_prior = float(rev_rows.iloc[-1]["value"]) if len(rev_rows) else prior
            if sid in ("PAYEMS",):
                actual_stat, expected = actual - revised_prior, prior - float(ar[(ar["date"] == first.iloc[i - 2]["date"]) & (ar["realtime_start"] <= prev["realtime_start"])].sort_values("realtime_start").iloc[-1]["value"]) if i >= 2 else float("nan")
                unit = "change"
            else:
                actual_stat, expected, unit = actual, prior, "level"
            rows.append(dict(date=cur["realtime_start"].strftime("%Y-%m-%d"), name=name, series=sid, agency=agency, obs=cur["date"].strftime("%Y-%m-%d"),
                             unit=unit, actual_first_print=actual_stat, prior_first_print=prior, revision_of_prior=revised_prior - prior,
                             expectation_source="naive_prior", expected=expected, surprise=(actual_stat - expected) if pd.notna(expected) else float("nan")))
        print(f"  {name:9} {len([r for r in rows if r['name'] == name])} releases")
    df = pd.DataFrame(rows).sort_values(["date", "name"]); CSV.parent.mkdir(exist_ok=True); df.to_csv(CSV, index=False)
    print(f"  -> {CSV} ({len(df)} rows; expectation = naive prior, as registered for the backfill)")


def inspect(name: str):
    sid, agency, index_url = SERIES[name]
    if not index_url:
        print(f"{name}: numbers-only series (no separate release text); nothing to inspect"); return
    page = _get(index_url)
    links = sorted(set(re.findall(r'href="([^"]+)"', page)))
    cand = [l for l in links if re.search(r"(archives?|histdata|releases?|\.pdf|\.htm)", l, re.I)]
    print(f"{name} ({agency}) index {index_url}: {len(links)} links, {len(cand)} candidate release links. First 25:")
    for l in cand[:25]: print("  ", l)
    print("Confirm the per-release URL pattern from these, then set it in PATTERNS below and run --fetch.")


PATTERNS = {   # filled in after --inspect confirms them; a missing pattern makes --fetch refuse
    # "empsit": "https://www.bls.gov/news.release/archives/empsit_{mmddyyyy}.htm",
    # "cpi":    "https://www.bls.gov/news.release/archives/cpi_{mmddyyyy}.htm",
}


def _text(page: str) -> str:
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    body = re.sub(r"</(p|div|li|h[1-6]|br|tr)>", "\n", body, flags=re.I); body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body); body = re.sub(r"[ \t]+", " ", body); return re.sub(r"\n\s*\n+", "\n\n", body).strip()


def fetch(name: str, since: str, sleep=0.5):
    if name not in PATTERNS:
        raise SystemExit(f"{name}: no confirmed URL pattern -- run --inspect {name} first and set PATTERNS[{name!r}]")
    if not CSV.exists():
        raise SystemExit("run --numbers first; release dates come from processed/prints.csv")
    df = pd.read_csv(CSV); df = df[(df.name == name) & (df.date >= since)]
    DOCS.mkdir(parents=True, exist_ok=True); written = exists = failed = 0
    for d in df.date:
        f = DOCS / f"{d.replace('-', '')}_{name}.txt"
        if f.exists(): exists += 1; continue
        dt = pd.Timestamp(d); url = PATTERNS[name].format(mmddyyyy=dt.strftime("%m%d%Y"), yyyymmdd=dt.strftime("%Y%m%d"), yyyy=dt.year)
        try:
            txt = _text(_get(url))
            if len(txt.split()) < 150: failed += 1; print(f"  {d}: too short, not written ({url})"); continue
            f.write_text(txt); written += 1; time.sleep(sleep)
        except Exception as e:
            failed += 1; print(f"  {d}: {type(e).__name__} ({url})")
    print(f"{name}: written {written}, existed {exists}, failed {failed} -> {DOCS}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--numbers", action="store_true"); ap.add_argument("--inspect"); ap.add_argument("--fetch")
    ap.add_argument("--since", default="2006-01-01"); a = ap.parse_args()
    if a.numbers: numbers(a.since)
    if a.inspect: inspect(a.inspect)
    if a.fetch: fetch(a.fetch, a.since)


if __name__ == "__main__":
    main()
