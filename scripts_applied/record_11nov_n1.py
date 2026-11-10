"""record_11nov_n1.py -- N1 second pass on record: v2 cause read (#123), the finance-section instrument finding, the release-composition split (#119),
the 5 Nov / 6 Nov pair (#121), the learner (#120), #118, the one PASS cell as a forward-log candidate. Prints the split first. Idempotent.
    python scripts_applied/record_11nov_n1.py"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

c = pd.read_csv("processed/news_causes_v2.csv", dtype={"date": str}); n = len(c); vc = c["cause"].value_counts()
share = (c["cause"] == "no_identifiable_news_positioning").mean(); yr = pd.to_datetime(c["date"], format="%Y%m%d").dt.year
pre, post = [(c.loc[m, "cause"] == "no_identifiable_news_positioning").mean() for m in (yr < 2017, yr >= 2017)]
counts = ", ".join(f"{k} {v}" for k, v in vc.items())
rel = pd.read_csv("processed/news_release_reads.csv"); rel["contradiction"] = pd.to_numeric(rel["contradiction"], errors="coerce")
tab = pd.DataFrame(json.loads(Path("docs/news_events_tables_v2.json").read_text()))
split = tab[tab.cause.isin(["with contradicting release", "without"])].sort_values(["index", "direction", "h", "cause"])
print("Release-composition split (v2 tables):"); print(split[["index", "direction", "h", "cause", "n", "reversal", "base", "gap", "p", "verdict"]].to_string(index=False))
passes = tab[tab.verdict == "PASS"]; print("\nPASS cells:"); print(passes[["index", "direction", "h", "cause", "n", "reversal", "base", "gap", "p"]].to_string(index=False))
with_pass = bool((split.verdict == "PASS").any() and (split[split.verdict == "PASS"].cause == "with contradicting release").any())
nov5 = json.loads(Path("data_provenance/news_reads/20261105__n1-cause-v2-2026-11-07.json").read_text())
r6 = rel[(rel.event_date == "2026-11-05") & (rel.kind == "empsit")]
r6s = (f"6 Nov payrolls read: surprise {int(r6.iloc[0].headline_surprise_sign):+d}, breadth {float(r6.iloc[0].breadth):.2f}, contradiction {float(r6.iloc[0].contradiction):+.2f}; drivers {r6.iloc[0].drivers}" if len(r6) else "6 Nov payrolls not in the release set")
learn = json.loads(Path("docs/news_events_learn_v2.json").read_text()); l1 = learn[0]
split_md = "<br>".join(f"{r_['index']} {r_['direction']} h{r_['h']} {r_['cause']}: n {r_['n']}, reversal {r_['reversal']:.0%} vs base {r_['base']:.0%}, gap {r_['gap']:+.0f}, p {r_['p']:.3f} → {r_['verdict']}" for _, r_ in split.iterrows() if r_["n"] >= 30) or "no split cell reaches n ≥ 30"
print(f"\n5 Nov read: cause {nov5['cause']} (secondary {nov5.get('secondary')}), confidence {nov5['confidence']}; story: {nov5.get('story')}"); print(r6s)

ROWS = f"""| 2026-11-11 | S1 cause read, **v2** digest (finance section), prompt n1-cause-v2 | {n} event days. Classes: {counts}. Share "no identifiable news — positioning" **{share:.0%}** (before 2017 {pre:.0%} n {int((yr < 2017).sum())}, from 2017 {post:.0%} n {int((yr >= 2017).sum())}; the pre-2013 archives carry no source URL so those days have no finance section — the before/after split is confounded by the instrument, not evidence). Mean confidence {c['confidence'].astype(float).mean():.2f}. One read failed (2022-10-07, `.failed.txt`). | **#123 right** (35–50%). **Instrument finding, recorded:** the finance section is a substring match on URL slugs ("stock" catches Stockton; 4,680 matches on 5 Nov 2026, ranked by mentions, mostly politics); on 5 Nov it surfaced the Democrats-AI-giants story and the oil slump but not Qualcomm. GDELT is a weak same-day source for market causes even filtered; the {share:.0%} is an upper bound on "positioning". A v3, if run, reads the day's own corpus (8-Ks, FOMC, Federal Register) instead of GDELT. |
| 2026-11-11 | S2b release composition | {len(rel)} release reads (empsit {int((rel.kind == 'empsit').sum())}, cpi {int((rel.kind == 'cpi').sum())}, fomc {int((rel.kind == 'fomc').sum())}); contradiction score mean {rel.contradiction.mean():+.2f}, share > +0.3: {(rel.contradiction > 0.3).mean():.0%}, share < −0.3: {(rel.contradiction < -0.3).mean():.0%}. {r6s}. | **#121** {'right' if (nov5['cause'] in ('no_identifiable_news_positioning', 'election_regulation') and float(nov5['confidence']) < 0.7 and len(r6) and abs(float(r6.iloc[0].contradiction)) <= 0.3) else 'wrong (counted)'}: 5 Nov read as {nov5['cause']} / {nov5.get('secondary')} at confidence {nov5['confidence']}. |
| 2026-11-11 | S3 tables, v1 and v2 (identical ALL rows; the cause classes change only the sub-rows) | 12 index × direction × horizon cells, H-table standard. **One PASS:** S&P the session after a ≥ 4% *rise* — reversal {float(passes.iloc[0].reversal):.0%} vs base {float(passes.iloc[0].base):.0%}, n {int(passes.iloc[0].n)}, p {float(passes.iloc[0].p):.3f}. SOX after a fall: 60% vs 53% at one session (p 0.029) but gap 7 < 10 → FAIL. All 3- and 5-session cells FAIL. Release split: {split_md}. | **#118** half: after falls both indices reverse > 50% at five sessions (SOX 57%, SPX 60%) as predicted, but after rises SPX is 55%, not below 50% — **counted wrong**. **#119** {'wrong (counted)' if with_pass else 'right'}: a contradicting release in the window {'does' if with_pass else 'does not'} lift the reversal rate past the standard. The PASS cell is one of twelve: **forward-log candidate N1-a** — "short SPY at the close of a session that rose ≥ 4%, one session" — logged, not promoted. |
| 2026-11-11 | S4 learner, v2 features | h = 1: best {l1['best']} Sharpe {l1['best_stat']:+.2f} vs null q95 {l1['q95']:+.2f}, p_family {l1['p_family']:.3f}; plain "buy the session after a ≥ 4% fall" +1.87 (n 278, from the run log). h = 3 and 5: null. v1 features did better at h = 1 (+2.12, p 0.005) and still lost to the plain rule — more cause detail added noise. | **#120 right.** Compendium tag: **neither** quant nor discretionary. |
| 2026-11-11 | Cost | ≈ US$10.3 of the US$25 cap (cause reads 0.31 + 1.58 + 2.73; release reads 5.72). | — |
"""
TRACK = f"""
### 3.45 N1 second pass (11 Nov 00:51)
v2 cause read: "no identifiable news" {share:.0%} (#123 right), but the finance section is a noisy slug-keyword match and GDELT missed the day's earnings story on 5 Nov 2026 — recorded as an instrument limit; a v3 would read the project's own corpus. 192 release-composition reads; #119 {'wrong' if with_pass else 'right'}; #121 see table; #118 counted wrong (S&P does not reverse below 50% after rises at five sessions); #120 right (learner loses to the plain post-fall rule). One PASS cell — S&P falls the session after a ≥ 4% rise, n 42 — becomes forward-log candidate N1-a, not a product rule. Total N1 spend ≈ US$10.3. Open: QQQ absent from the panel; 2001–2012 archives not fetched; v3 corpus-based cause read not registered.
"""
COMP = f"""
### N1 — news-attributed ≥ 4% days (SOXX, SPY; 2009 → 2026; recorded 2026-11-11)
- **Cause of a ≥ 4% day, read from GDELT:** about half of event days show no identifiable same-day news in GDELT even with a finance filter; earnings, central bank, macro and election/regulation classes share the rest. Instrument-limited (GDELT misses company news); not a tradeable fact. — *neither*
- **Reversal after a ≥ 4% day:** after falls, the next five sessions are up 57–60% of the time, which is only 2–4 points above how often any five sessions are up — no signal. After a ≥ 4% *rise* the S&P falls the next session 67% vs 45% base (n 42, p 0.006) — one cell of twelve, on the forward log as candidate N1-a. — *discretionary at most, after the forward test*
- **A contradicting bureau release in the next five sessions:** {'lifts' if with_pass else 'does not lift'} the reversal rate past the standard. — *{'quant candidate' if with_pass else 'neither'}*
- **Learner on cause class, move size, trend, VIX, release scores:** does not beat "buy the session after a ≥ 4% fall". — *neither*
"""
p = Path("docs/prereg_news_events.md"); s = p.read_text()
if "S1 cause read, **v2** digest" in s: print("\n  prereg_news_events: already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("\n  prereg_news_events: v2 / S2b / S3 / S4 / cost rows appended")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.45 N1 second pass" in s: print("  TRACK: 3.45 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.45 appended")
cp = Path("docs/RESULTS_COMPENDIUM.md")
if cp.exists():
    s = cp.read_text()
    if "### N1 — news-attributed" in s: print("  compendium: N1 already present -- skipped")
    else: cp.write_text(s.rstrip("\n") + "\n" + COMP); print("  compendium: N1 section appended")
