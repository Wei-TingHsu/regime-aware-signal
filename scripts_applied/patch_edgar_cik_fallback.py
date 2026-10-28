"""patch_edgar_cik_fallback.py -- keep the nightly 8-K fetch alive when sec.gov refuses the ticker file.

FOUND 28 Oct 2026 by reading logs/daily_*.log: every nightly run since the feed repair of 19 Oct ends its 8-K step with
    RuntimeError: HTTP 403 for https://www.sec.gov/files/company_tickers.json  ...  Request Rate Threshold Exceeded
    8-K fetch failed -- continuing, the corpus is additive
while the same fetch run by hand (19 Oct 14:06, 22 Oct 22:56 SGT) succeeded and wrote 20261021_TSLA.txt / 20261022_LMT.txt.
So TRACK 3.26's "forward from 20 Oct the feed is live" holds for the manual path only; the automated earnings feed -- the one
source that scored above chance in the backfill -- has delivered nothing by itself for nine nights. Cause not yet known (the
request is the first of the run, so it is not our own rate; the UA is sent; the manual run uses the same code). This patch
does not guess the cause: it caches the ticker->CIK map the first time the file is fetched and falls back to the cache on a
403, and it prints the User-Agent actually sent so the next failure names itself.

Protocol (wrong prior #19): verify the anchor is unique, apply, py_compile, revert on failure.
    python scripts_applied/patch_edgar_cik_fallback.py          # dry run
    python scripts_applied/patch_edgar_cik_fallback.py --write
Then, from an interactive shell, populate the cache once:
    python -m src.fetch_sources edgar --tickers NVDA --limit 1 --sleep 0.5
"""
import py_compile
import shutil
import sys
from pathlib import Path

P = Path("src/fetch_sources.py")
OLD = "    cmap = json.loads(get(TICKERS))\n"
NEW = '''    cache = Path("processed/cik_map.json")
    try:
        cmap = json.loads(get(TICKERS))
        cache.parent.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(cmap))
    except Exception as e:
        # 28 Oct: sec.gov answered 403 "Request Rate Threshold Exceeded" to this FIRST request of every nightly run since
        # 19 Oct while the same call succeeded by hand. Until the cause is found, a cached map keeps the fetch alive.
        first = str(e).splitlines()[0] if str(e) else type(e).__name__
        if not cache.exists():
            print(f"  ticker file unavailable ({first}); no processed/cik_map.json cached yet -- UA sent: {UA['User-Agent']}")
            raise
        print(f"  ticker file unavailable ({first}); using cached processed/cik_map.json -- UA sent: {UA['User-Agent']}")
        cmap = json.loads(cache.read_text())
'''


def main():
    s = P.read_text()
    n = s.count(OLD)
    print(f"anchor occurrences: {n} (need exactly 1)")
    if n != 1:
        sys.exit("anchor not unique or missing -- nothing changed")
    if "--write" not in sys.argv:
        print("dry run: anchor verified; add --write to apply"); return
    bak = P.with_suffix(".py.bak_20261028")
    shutil.copy2(P, bak)
    P.write_text(s.replace(OLD, NEW, 1))
    try:
        py_compile.compile(str(P), doraise=True)
    except Exception as e:
        shutil.copy2(bak, P); sys.exit(f"py_compile FAILED, reverted: {e}")
    print(f"applied; {P} compiles; backup at {bak.name}")


if __name__ == "__main__":
    main()
