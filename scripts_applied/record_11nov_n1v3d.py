"""record_11nov_n1v3d.py -- puts on record: the v3c joint result (#128), the v3d registration with the order of events stated, the v3d results
(#129-#131), and the founder's SHORT-WINDOW RULE as a standing rule in TRACK / SPEC_GRID / PROJECT_MASTER. Idempotent.
    python scripts_applied/record_11nov_n1v3d.py"""
import json
from pathlib import Path

def f(v, fmt="+.3f"):
    return "n/a" if v is None or v != v else format(v, fmt)

J = {(r["family"], r["index"], r["direction"]): r for r in json.loads(Path("docs/news_events_v3_joint.json").read_text())}
D = {(r["family"], r["index"], r["direction"]): r for r in json.loads(Path("docs/news_events_v3_decay.json").read_text())["tests"]}
def jc(k):
    r = J.get(k); return "not testable" if r is None else f"{f(r['mean_rank_corr'])} (p {f(r['p'], '.4f')}; before 2020 {f(r['before_2020'])}, from 2020 {f(r['from_2020'])})"
def dc(k):
    r = D.get(k); return "not testable" if r is None else (f"day 0 {f(r['day0'])} (p {f(r['p_day0'], '.4f')}); day 0 minus later days {f(r['decay'])} (p {f(r['p_decay'], '.4f')}); "
        f"days +1..+5 {f(r['drift_1to5'])} (p {f(r['p_drift'], '.4f')}); two days before {f(r['placebo'])} (p {f(r['p_placebo'], '.4f')}); "
        f"day-0 return by third of the score {f(r['day0_low'], '+.2%')} / {f(r['day0_mid'], '+.2%')} / {f(r['day0_high'], '+.2%')}; days +1..+5 {f(r['drift_low'], '+.2%')} / {f(r['drift_mid'], '+.2%')} / {f(r['drift_high'], '+.2%')}")
a, b = J[("all", "SOX", "fall")], J[("all", "SOX", "rise")]; p128 = a["p"] < 0.05 and b["p"] < 0.05 and min(a["p"], b["p"]) < 0.0125
prim = [("all", "SOX", "fall"), ("all", "SOX", "rise"), ("fed", "SOX", "fall"), ("fed", "SOX", "rise")]
p129 = D[prim[2]]["p_day0"] < 0.0125 and D[prim[2]]["day0"] > 0 and D[prim[0]]["p_day0"] < 0.05 and D[prim[0]]["day0"] > 0
p130 = D[prim[0]]["decay"] > 0 and D[prim[2]]["decay"] > 0 and all(D[k]["p_drift"] > 0.05 for k in prim)
p131 = all(abs(D[k]["placebo"]) < 0.08 for k in prim)
print(f"#128 {'right' if p128 else 'WRONG'}; #129 {'right' if p129 else 'WRONG'}; #130 {'right' if p130 else 'WRONG'}; #131 {'right' if p131 else 'WRONG'}")
RULE = """**Short-window rule (founder, 11 Nov 2026; standing).** News arrives every day. The longer the span of sessions a test measures, the more unrelated news is mixed into it, which adds noise and can hide or fake an effect. So: (1) every test of a reaction to news is run at several span lengths, the shortest first (the release day itself, then +1, +1…+2, +1…+3, and only then 5, 10, 20); (2) no conclusion — pass or null — is written from one span length alone; (3) where a long span fails, the short spans are run before the idea is called null; (4) this applies back to earlier tests whose verdict rests on a single span of five sessions or more (horizon audit, TRACK §3.49). It sits beside the grid-by-default rule (28 Oct) and the sub-period rule; the search over span lengths is judged against the best the same search finds on shuffled data."""
ROWS = f"""| 2026-11-11 | v3c joint size test (primary: all documents; bar p < 0.0125) | SOX fall {jc(('all', 'SOX', 'fall'))}; SOX rise {jc(('all', 'SOX', 'rise'))}; SPX fall {jc(('all', 'SPX', 'fall'))}; SPX rise not testable. Neither semiconductor group clears 0.0125; both are below 0.05. Measured beside it: Fed documents only — SOX fall {jc(('fed', 'SOX', 'fall'))}, SOX rise {jc(('fed', 'SOX', 'rise'))}; BLS only — SOX fall {jc(('bls', 'SOX', 'fall'))}, SOX rise {jc(('bls', 'SOX', 'rise'))}. | **#128 {'right' if p128 else 'wrong (counted)'}** |
| 2026-11-11 | Caveat on v3a–v3c (Claude) | The return was measured over the sessions after the event day and the documents came out INSIDE those sessions, so the link is mostly same-period, not a forecast. v3d separates the two. | — |
| 2026-11-11 | **v3d registration — release-day decay (founder's hypothesis)** | "The news has its strongest effect the day it is released, then weakens day by day." Re-aligned on the document's release day (day 0). Per index × direction × family: (a) day-0 link, (b) day 0 minus the mean of days +1…+5, (c) link with the cumulative return over days +1…+5 (the part still tradeable after reading the document at the close of day 0), (d) the two days before the document (a document cannot move prices before it exists). 2,000 shuffles of scores across document days. Primary: SOX fall and SOX rise × all documents and Fed documents; bar p < 0.0125. Priors **#129** day 0 positive, p < 0.0125 for Fed documents after SOX falls and p < 0.05 for all documents; **#130** day 0 larger than later days in both SOX-fall cells and nothing distinguishable over days +1…+5 in all four; **#131** the two days before: |mean| < 0.08 in all four. **Order of events, stated:** both recording scripts that carry the v3c and v3d registrations crashed before writing their rows (an import path, then a number-format error on an empty cell — both Claude's errors); each was nevertheless committed with its registration text and priors BEFORE the corresponding result commit (v3c: script at 80c952a, result 70b6e54; v3d: script at bc773b2, result 837b1ef). These rows are written afterwards from the files on disk. | — |
| 2026-11-11 | **v3d results** (score: higher = the document does NOT support the event's direction; returns signed so positive = price moving back) | **SOX fall, all documents:** {dc(prim[0])}. **SOX fall, Fed documents:** {dc(prim[2])}. **SOX rise, all documents:** {dc(prim[1])}. **SOX rise, Fed documents:** {dc(prim[3])}. Not primary: SPX fall, Fed documents: {dc(('fed', 'SPX', 'fall'))}. | **#129 {'right' if p129 else 'wrong (counted)'}; #130 {'right' if p130 else 'wrong (counted)'}; #131 {'right' if p131 else 'wrong (counted)'}.** The founder's hypothesis holds after semiconductor falls: the whole link is on the release day and nothing measurable is left on days +1…+5. In percent, Fed documents after a SOX fall: on the release day the index fell a further 2.93% when the document supported the fall and rose 0.83% when it did not; over the next five sessions the three groups returned about the same (+1.5% / +1.2% / +1.1%). Consequence: at daily closes there is nothing left to trade once the document has been read; the only open question is INSIDE the release day (from the release minute to the close), which daily data cannot see. Caveats: same-day link — the document and the price may both be reacting to the same conditions; hindsight in the reader cannot be excluded; one read per document, no repeat-read consistency check yet. |
| 2026-11-11 | **Short-window rule recorded** | {RULE} Applied here at once: `news_events3 decayk` reruns v3d with the span after day 0 cut to +1, +1…+2, +1…+3. | — |
"""
TRACK = f"""
### 3.49 N1 v3d result; the short-window rule; next steps (11 Nov 15:40)
v3d: after ≥ 4% semiconductor falls the link between official documents and price is on the document's release day (all documents +0.169, p 0.004; Fed documents +0.382, p 0.001) and is gone on days +1…+5 (p 0.59); the two days before the document show nothing. Priors #129–#131 {'all right' if (p129 and p130 and p131) else 'see table'}; #128 {'right' if p128 else 'counted wrong'}. Not a daily-close trading signal: the move is finished by the close of the release day.

{RULE}

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | `decayk` — v3d with spans +1, +1…+2, +1…+3 | the short-window rule applied to the test that prompted it | nothing — run |
| 2 | **v3e intraday** — from the release minute to the close of the same day, for Fed statements and Chair / Vice Chair speeches after ≥ 4% semiconductor moves (needs intraday prices and the release time of each document) | the only place a tradeable signal can still be; also decides whether showing the score on the app at release is useful or only explanatory | whether to register; which intraday data source |
| 3 | Reader consistency — read 30 documents a second time and compare the scores | the score is one model judgement per document; this shows how much it wobbles | yes / no (≈ US$0.50) |
| 4 | **Horizon audit** — list every past test whose verdict rests on one span of five sessions or more; rerun each at 0, 1, 2, 3 | the short-window rule applied backwards | nothing — Claude prepares the list from RESULTS_COMPENDIUM |
| 5 | Then the agenda of §3.46 from item 3 (N1-a forward log, QQQ, S1, S2, S3, carried items, buyer conversation), then back to the main track | — | — |
"""
p = Path("docs/prereg_news_events.md"); s = p.read_text()
if "**v3d results**" in s: print("  prereg_news_events: v3d already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("  prereg_news_events: v3c result, v3d registration + results, short-window rule recorded")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.49 N1 v3d result" in s: print("  TRACK: 3.49 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.49 appended")
for name in ("docs/SPEC_GRID.md", "docs/PROJECT_MASTER.md", "docs/RESULTS_COMPENDIUM.md"):
    q = Path(name)
    if not q.exists(): print(f"  {name}: not found -- skipped"); continue
    s = q.read_text()
    if "Short-window rule (founder, 11 Nov 2026" in s: print(f"  {name}: rule already present -- skipped")
    else: q.write_text(s.rstrip("\n") + "\n\n### Standing rule — short windows first\n\n" + RULE + "\n"); print(f"  {name}: short-window rule appended")
