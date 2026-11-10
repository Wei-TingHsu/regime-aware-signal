"""record_7nov_n1.py -- N1 stage-2 first pass on record: the v1 cause read (prior #117 wrong, counted), the BLS fetch failure, the missing GDELT day,
and the dated amendment registering the v2 digest + prompt version. Idempotent.    python scripts_applied/record_7nov_n1.py"""
from pathlib import Path
import pandas as pd
c = pd.read_csv("processed/news_causes.csv", dtype={"date": str}); n = len(c); vc = c["cause"].value_counts()
share = (c["cause"] == "no_identifiable_news_positioning").mean(); yr = pd.to_datetime(c["date"], format="%Y%m%d").dt.year
pre, post = [(c.loc[m, "cause"] == "no_identifiable_news_positioning").mean() for m in (yr < 2017, yr >= 2017)]
counts = ", ".join(f"{k} {v}" for k, v in vc.items())
ROWS = f"""| 2026-11-07 | S1 cause read, **v1** digest (top-50 by mentions), prompt n1-cause-v1 | {n} event days read (2009 → 2026; 181 GDELT files, 3.2 GB; 2022-11-10 missing from GDELT, 404). Classes: {counts}. Mean confidence {c['confidence'].astype(float).mean():.2f}. Share "no identifiable news — positioning" **{share:.0%}** (before 2017 {pre:.0%}, from 2017 {post:.0%}). | **#117 wrong (counted)** — predicted 20–35%. Caveat recorded with it: the v1 digest ranks GDELT records by mentions, which on any day is wars, elections and diplomacy; market, earnings and Fed records barely surface, so part of the {share:.0%} is the instrument not seeing finance rather than the market moving on nothing. The v2 digest below tests how much. |
| 2026-11-07 | S2a release fetch | 0 BLS releases fetched — every archive request failed silently (v1 fetcher swallowed the error; BLS refuses scripted clients without a contact address in the User-Agent). 38 FOMC-statement pairs found in the +1…+5 window from the corpus. S2b/S3 contradiction split not yet run. | — |
| 2026-11-07 | **Amendment — v2 digest and prompt version registered before running** | `news_events digest --v2` adds to each day a FINANCE / MACRO / EARNINGS section: the GDELT records whose source slug carries a market, Fed, yield, earnings, chip, bank, tariff, oil or pandemic term (fixed keyword list in `src/news_events.py`), ranked by mentions, up to 40. Same classification prompt under version **n1-cause-v2-2026-11-07**, own cache; v1 reads stay on disk and in this table. Prior **#123:** the v2 share of "no identifiable news" falls to 35–50% — still above #117's band — with the gain going mostly to earnings/guidance and central-bank; the before/after-2017 ordering is unchanged. S3 tables and S4 learner run on v2; v1 tables kept for comparison. | — |
"""
TRACK = f"""
### 3.44 N1 first pass (7 Nov 00:25)
v1 cause read on {n} event days: "no identifiable news — positioning" {share:.0%} → prior #117 (20–35%) wrong, counted; caveat that the mention-ranked GDELT digest under-represents finance, so a v2 digest with a finance section is registered (prompt n1-cause-v2, prior #123, own cache). BLS release fetch returned nothing (no contact address in the User-Agent — fixed, `BLS_CONTACT`); 38 FOMC pairs in window. GDELT 2022-11-10 absent (404). `news_events2` v2: `reads/` folder bug and empty-CSV crash in tables/learn fixed.
"""
p = Path("docs/prereg_news_events.md"); s = p.read_text()
if "S1 cause read, **v1** digest" in s: print("  prereg_news_events: already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("  prereg_news_events: S1 v1 result, S2a failure, v2 amendment appended")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.44 N1 first pass" in s: print("  TRACK: 3.44 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.44 appended")
