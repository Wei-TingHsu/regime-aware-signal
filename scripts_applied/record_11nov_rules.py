"""record_11nov_rules.py -- records: v3d at spans 1-3 (the short-window rule applied), the founder's TWO-CATEGORY rule (quant vs subjective/intraday)
as a standing rule, the founder's expectations proposal (price just before a scheduled release = the market's agreed value) as the v3e design note,
and the agenda. Points RESULTS_COMPENDIUM at docs/TEST_BOOK.md. Idempotent.    python scripts_applied/record_11nov_rules.py"""
import json
from pathlib import Path

def f(v, fmt="+.3f"):
    return "n/a" if v is None or v != v else format(v, fmt)

prim = [("all", "SOX", "fall"), ("fed", "SOX", "fall"), ("all", "SOX", "rise"), ("fed", "SOX", "rise")]; parts = []
for k in (1, 2, 3):
    p = Path(f"docs/news_events_v3_decay_k{k}.json")
    if not p.exists(): parts.append(f"span +1…+{k}: file missing"); continue
    T = {(r["family"], r["index"], r["direction"]): r for r in json.loads(p.read_text())["tests"]}
    parts.append(f"**span +1…+{k}:** " + "; ".join(f"{a} documents, SOX {d}: day 0 minus later {f(T[(a, i, d)]['decay'])} (p {f(T[(a, i, d)]['p_decay'], '.3f')}), later days {f(T[(a, i, d)]['drift_1to5'])} (p {f(T[(a, i, d)]['p_drift'], '.3f')})" for a, i, d in prim if (a, i, d) in T))
RULE2 = """**Two-category rule (founder, 11 Nov 2026; standing).** A finding can be used in two ways and every test is labelled for both. **QUANT** = usable by a rule-based strategy that holds from one session to several weeks: the effect must still be there after the information is known at a daily close. **SUBJECTIVE (intraday)** = usable by the founder's own judgement inside the day: the effect is on the same day as the information and nothing is left afterwards. "Nothing is left after day 0" ends a finding as QUANT but not as SUBJECTIVE. Grade B = seen at daily closes only (a same-day association; capture after the release not yet tested); grade A = confirmed with intraday prices from the release time to the close. Findings that are neither a direction nor null are **CONTEXT** (how to size, hedge or explain); the rest are **NEITHER**. Every past test is re-labelled this way in `docs/TEST_BOOK.md` Part B, which also marks the tests where day 0 was never measured separately (the horizon audit list)."""
ROWS = f"""| 2026-11-11 | v3d at spans 1, 2, 3 (short-window rule applied; day-0 numbers unchanged: all documents +0.169 p 0.004, Fed documents +0.382 p 0.001 after SOX falls) | {' '.join(parts)} | The conclusion does not depend on the span: the link is on the release day and nothing is distinguishable afterwards at 1, 2, 3 or 5 sessions. Category under the two-category rule: **SUBJECTIVE grade B; not QUANT.** |
| 2026-11-11 | **Two-category rule recorded** | {RULE2} | — |
| 2026-11-11 | **v3e design note (not yet registered) — the founder's answer to "the reader cannot see what traders expected"** | Founder: for heavily traded instruments assume the price just before a scheduled release is the value investors agreed on; the move right after the release then measures the surprise. His two limits, recorded: (1) outside regular hours trading is thin, so the price is a poor measure of agreement; (2) it works only for releases whose time is known in advance — for news that appears without warning one can only look back from the minute it is detected. Claude's additions: for the 08:30 ET data releases, index futures trade actively at that hour and can stand in for the cash market (limit 1); for unscheduled news, the first minute of abnormal price and volume can date the news (limit 2). Proposed test: surprise = the move in the first minutes after the release; then, does the document's composition score tell whether the rest of the day CONTINUES or REVERSES that first move (a strong headline with a weak composition fading, for example). This is the intraday test that would turn the SUBJECTIVE grade B findings into grade A or close them. Needs: the release time of each document and intraday prices (the project's own 1-minute collector since Oct 2026; hourly bars for about two years from free sources; longer history only from a paid source). | founder to choose the data route before registration |
"""
TRACK = f"""
### 3.50 Two-category rule; test book; v3e design; agenda (11 Nov 16:10)
{RULE2}

`docs/TEST_BOOK.md` created: Part A rules and shared method, Part B every test labelled QUANT / SUBJECTIVE / CONTEXT / NEITHER with "day 0 checked?", Part C rebuild cards (N1 complete; five more parts pending). Labels as of today — QUANT: gold–equity correlation persistence (risk forecast), calm-day warning before regime changes (candidate), S&P the session after a ≥ 4% rise (candidate, forward log). SUBJECTIVE grade B: gold on Fed statement days by rate surprise (stronger when yields are volatile and in regimes 1 and 3), Fed documents after ≥ 4% semiconductor falls, gold on the day a 6% S&P drawdown completes (weak). No grade A yet.

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | **Horizon audit** — every index row marked "day 0 checked? no" rerun at day 0, +1, +1…+2, +1…+3 (calls, history tables, oil shocks, sell-offs, residual momentum, day-types, fast states, daily liquidity) | applies the short-window and two-category rules to the past tests; may move nulls into SUBJECTIVE | nothing — Claude builds the runner |
| 2 | **v3e intraday** — first-minutes surprise, then continuation or reversal by composition score | the only route to SUBJECTIVE grade A and to a useful release-time line on the app | the intraday data route |
| 3 | Test book parts 2–6 (rebuild cards for the other families) | lets a quant specialist rebuild every test alone | order of parts, if any preference |
| 4 | Reader consistency (30 documents read twice) | how reliable the composition score is | yes / no (≈ US$0.50) |
| 5 | §3.46 items 3–9 (N1-a forward log, QQQ, S1, S2, S3, carried regime items, buyer conversation), then the main track | — | — |
"""
p = Path("docs/prereg_news_events.md"); s = p.read_text()
if "**Two-category rule recorded**" in s: print("  prereg_news_events: already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("  prereg_news_events: spans 1-3, two-category rule, v3e design note recorded")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.50 Two-category rule" in s: print("  TRACK: 3.50 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.50 appended")
for name in ("docs/SPEC_GRID.md", "docs/PROJECT_MASTER.md", "docs/RESULTS_COMPENDIUM.md"):
    q = Path(name)
    if not q.exists(): print(f"  {name}: not found -- skipped"); continue
    s = q.read_text()
    if "Two-category rule (founder, 11 Nov 2026" in s: print(f"  {name}: rule already present -- skipped")
    else: q.write_text(s.rstrip("\n") + "\n\n### Standing rule — two ways to use a finding\n\n" + RULE2 + ("\n\nThe long form of every test — method, data, pass rule, result, use — is `docs/TEST_BOOK.md`.\n" if "COMPENDIUM" in name else "\n")); print(f"  {name}: two-category rule appended")
print("  docs/TEST_BOOK.md " + ("present" if Path("docs/TEST_BOOK.md").exists() else "MISSING -- unzip again"))
