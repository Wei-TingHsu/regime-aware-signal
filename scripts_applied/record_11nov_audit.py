"""record_11nov_audit.py -- horizon audit on record: results table in docs/prereg_horizon_audit.md, priors #132-#135 judged from the JSON files,
a results section appended to docs/TEST_BOOK.md, TRACK 3.52. Idempotent.    python scripts_applied/record_11nov_audit.py"""
import json
from pathlib import Path

J = {}
for f in sorted(Path("docs").glob("horizon_audit_*.json")):
    j = json.loads(f.read_text())
    if j: J[j["name"]] = j
def P(n, g):
    v = J.get(n, {}).get("family", {}).get(g, {}).get("p"); return v if (v is not None and v == v) else None
def cell(n, g):
    fm = J[n]["family"][g]; b = fm.get("best")
    return "not measured" if b is None else f"{b['variant']}, {b['span']}: {b['mean_bp']:+.0f} bp, t {b['t']:+.1f}, n {b['n']}, hit {b['hit']:.0%}; family p {fm['p']:.3f}"
lt = lambda v: v is not None and v < 0.05
p132 = not any(lt(P(n, "after")) for n in J)
p133 = lt(P("calls", "day0")) and lt(P("fomc", "day0")) and not lt(P("liquidity", "day0"))
p134 = sum(lt(P(n, "day0")) for n in ("selloff", "sudden", "oil", "htables")) >= 4
p135 = sum(lt(P(n, "before")) for n in ("sudden", "fomc", "calls", "liquidity")) <= 1
verd = {132: p132, 133: p133, 134: p134, 135: p135}; print({k: ("right" if v else "WRONG") for k, v in verd.items()})
NOTE = {
 "calls": "Label by the registered rule. Read with care: the calls are mostly 'up' calls on assets that drift up; the shift null keeps that drift and the result clears it narrowly (p 0.034, best of 3 span cells × variants). The same calls at 2 sessions did not beat drift in the scoreboard (p 0.40) and earned a Sharpe of 0.07 after costs. Day 0 itself shows nothing (p 0.245): the documents' direction does NOT go with the same-day move. The day −1 check fails for tier 2 (−25 bp, p 0.007): those calls point against the previous day's move, so part of what the call 'predicts' may be a bounce from the day before. Next: a registered, costed rule at 1 / 2 / 3 sessions with the previous day's move controlled.",
 "states": "Label by the registered rule. Read with care: the state covers about half of all days (n 2,411) and the S&P's ordinary five-session gain is roughly +20 bp; the excess is about +10 bp per five sessions before costs. The state flips almost daily (median run 1 session), so trading it means paying costs constantly; the costed version of this test at five sessions (F1, net Sharpe) found no survivor at three states (p 0.36). What the audit adds: calm-type days are followed by slightly better S&P returns than other days, in every era — a sizing tilt at most. Next: a registered, costed rule at 1 / 2 / 3 sessions.",
 "fomc": "Confirms T9b on the audit's own measure: on statement days gold moves 76 bp in the direction the rate surprise predicts, 80% of the time, in every era; nothing reliable is left on the days after (large surprises: +38 bp on day +1, p 0.40). SUBJECTIVE grade B; not QUANT.",
 "oil": "Gold rises about 31 bp on the day an oil shock completes — two prices moving together (stronger before 2015); nothing after. CONTEXT.",
 "htables": "The day-0 passes are market mechanics (on Fed decision days the dollar moves with the 2-year yield, −42 bp on the signed measure, t −8.7). Nothing reliable after (best: oil −141 bp the day after a 2-year yield drop, n 30, family p 0.12). CONTEXT.",
 "selloff": "Gold shows no reliable move on the day a drawdown completes or after. The S&P itself gains 128 bp over the five sessions after a −4% ten-session fall (t 3.1) but that does not clear the family null (p 0.16) and reverses sign in 2022–26.",
 "sudden": "On days the S&P falls ≥ 4% gold is up 51 bp on average but not reliably (t 1.2): gold is not a dependable same-day hedge on crash days. Nothing after.",
 "liquidity": "Nothing on the day, before or after.",
 "resid": "After a large unexplained 20-session move the S&P gives back about 55 bp over the next five sessions, with the same sign in every era (t −4.4), but the family null is not cleared (p 0.106). Closest miss of the audit; NEITHER as registered."}
order = [n for n in ("fomc", "calls", "liquidity", "selloff", "sudden", "oil", "htables", "states", "resid") if n in J]
ROWS = "".join(f"| 2026-11-11 | `{n}` — {J[n]['kind']} | {cell(n, 'day0')} | {cell(n, 'after')} | {cell(n, 'before')} | **{J[n]['label']}**. {NOTE.get(n, '')} | |\n" for n in order)
ROWS += f"| 2026-11-11 | priors | | | | | **#132 {'right' if p132 else 'wrong (counted)'}** (two audits clear p_after < 0.05); **#133 {'right' if p133 else 'wrong (counted)'}** (the calls show no day-0 link); **#134 {'right' if p134 else 'wrong (counted)'}** (gold does not co-move on S&P sell-off days; only oil and the history tables pass); **#135 {'right' if p135 else 'wrong (counted)'}** |\n"
BOOK = "\n### B7. Horizon audit results (11 Nov 2026) — these replace the 'day 0 checked? no' entries above\n\nMethod and label rule: `docs/prereg_horizon_audit.md`; code `src/horizon_audit.py`; command `python -m src.horizon_audit all`; per-audit tables `docs/horizon_audit_<name>.md`.\n\n| audit (index rows it updates) | day 0 | days +1 … +5 | category after the audit |\n|---|---|---|---|\n" + "".join(
    f"| `{n}` ({ {'fomc': 'row 14, T9b', 'calls': 'rows 24/27/33, A, D7', 'liquidity': 'D2c', 'selloff': 'D1, T-L5b', 'sudden': 'D1b', 'oil': 'A3a, D5', 'htables': 'H0–H7', 'states': 'F1, Y3', 'resid': 'T-H'}[n] }) | {cell(n, 'day0')} | {cell(n, 'after')} | **{J[n]['label']}** — {NOTE.get(n, '')} |\n" for n in order)
BOOK += "\nAfter the audit the lists read — **QUANT:** gold–equity correlation persistence (confirmed, a risk forecast); candidates: calm days rarer before regime changes; S&P the session after a ≥ 4% rise; the report's calls over the next 1–3 sessions (narrow, drift-sensitive); calm-type fast state → S&P next sessions (small, cost-sensitive). **SUBJECTIVE grade B:** gold on Fed statement days by the rate surprise (re-confirmed: 76 bp, 80% of days); Fed documents after ≥ 4% semiconductor falls. **Dropped from SUBJECTIVE:** gold on the day an S&P drawdown completes (no day-0 move found). **CONTEXT added:** gold rises with oil on oil-shock days; the dollar moves with the 2-year yield on Fed days. Everything else audited: NEITHER.\n"
TRACK = f"""
### 3.52 Horizon audit result (11 Nov 17:10)
Nine audits, each on day −1, day 0, +1, +1…+2, +1…+3, +1…+5. Labels by the registered rule: `calls` QUANT candidate (pooled, +16 bp over days +1…+3, family p 0.034; day 0 nothing; day −1 check fails for tier 2), `states` QUANT candidate (calm-type state → S&P +31 bp over five sessions, p 0.002, about +10 bp over the ordinary gain, flips daily), `fomc` SUBJECTIVE grade B (gold 76 bp with the surprise on the day, 80% hit, nothing after), `oil` and `htables` CONTEXT (same-day co-movement), `selloff`, `sudden`, `liquidity`, `resid` NEITHER (resid closest: S&P gives back 55 bp after a large unexplained 20-session move, p 0.106). Priors: #132 {'right' if p132 else 'wrong'}, #133 {'right' if p133 else 'wrong'}, #134 {'right' if p134 else 'wrong'}, #135 {'right' if p135 else 'wrong'}. Both QUANT-candidate labels are narrow or cost-sensitive and each needs its own registered, costed rule (QC-1 calls at 1/2/3 sessions with the previous day's move controlled; QC-2 calm-state tilt at 1/2/3 sessions) before it is called a signal. Intraday route started: `src/intraday_fetch.py` (Databento; cost asked before any download).
"""
p = Path("docs/prereg_horizon_audit.md"); s = p.read_text()
if "| 2026-11-11 | priors |" in s: print("  prereg_horizon_audit: already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("  prereg_horizon_audit: results and prior verdicts recorded")
b = Path("docs/TEST_BOOK.md"); s = b.read_text()
if "### B7. Horizon audit results" in s: print("  TEST_BOOK: B7 already present -- skipped")
else:
    anchor = "\n---\n\n## Part C — rebuild cards"
    b.write_text(s.replace(anchor, BOOK + anchor, 1) if anchor in s else s.rstrip("\n") + "\n" + BOOK); print("  TEST_BOOK: B7 audit results added to Part B")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.52 Horizon audit result" in s: print("  TRACK: 3.52 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.52 appended")
