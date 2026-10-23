"""23 Oct evening: withdraw the consecutive-closes promotion (it missed gold's August peak); add the fidelity criterion (no leg may hide a counter-move
larger than the zigzag threshold) and the time-since-extreme persistence rule; re-run T-I with both. Run from the repo root:
  python scripts_applied/leg_fidelity_setup.py ; python -m src.why_moved segmenter-test GLD | sed -n 1,34p ; python -m src.why_moved run | grep -A2 "^## gold" | tail -1 | cut -c1-200"""
from pathlib import Path
import sys, json
from datetime import datetime

# ---- 1. withdraw the promotion (rename, nothing deleted)
lr = Path("processed/leg_rule.json")
if lr.exists():
    j = json.loads(lr.read_text()); j["withdrawn"] = datetime.now().strftime("%Y-%m-%d %H:%M"); j["reason"] = "missed gold's 25 Aug 2026 peak: the fall had no five consecutive down closes; fidelity criterion added"
    lr.replace(Path("processed/leg_rule_withdrawn_20261023.json")); Path("processed/leg_rule_withdrawn_20261023.json").write_text(json.dumps(j, indent=1)); print("  promotion withdrawn (file renamed, reason recorded)")
else: print("  no promotion file present")

# ---- 2. why_moved: time-mode persistence, fidelity, criteria
wm = Path("src/why_moved.py"); s = wm.read_text()
if "def missed_reversals(" in s: print("  why_moved fidelity: already")
else:
    old = s[s.index("def turning_points_persist(r: pd.Series, n_days: int = 3, x: float = 0.02):"):s.index("def turning_points_swing(")]
    new = '''def turning_points_persist(r: pd.Series, n_days: int = 3, x: float = 0.02, mode: str = "time"):
    """Founder's rule: a reversal is a trend, not one bounce. mode='time' (the meant reading): the price has stayed off its extreme for n_days sessions
    AND is at least x against it. mode='closes' (the first, literal reading, withdrawn 23 Oct): n_days CONSECUTIVE closes against the trend and x —
    it never confirmed gold's Aug 2026 peak because the fall had no five-day losing streak."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); d = np.sign(rr.to_numpy())
    hi = lo = 0; trend = 0; tps = []; run_ = 0
    for i in range(1, len(px)):
        if trend >= 0 and px[i] > px[hi]: hi = i
        if trend <= 0 and px[i] < px[lo]: lo = i
        if mode == "closes":
            against = (d[i] < 0) if trend >= 0 else (d[i] > 0); run_ = run_ + 1 if against else 0
            ok_up, ok_dn = run_ >= n_days, run_ >= n_days
        else:
            ok_up, ok_dn = (i - hi) >= n_days, (i - lo) >= n_days          # sessions since the extreme, up days inside allowed
        if trend >= 0 and ok_up and px[i] <= px[hi] * np.exp(-x):
            tps.append((hi, "peak")); trend = -1; lo = i; run_ = 0
        elif trend <= 0 and ok_dn and px[i] >= px[lo] * np.exp(x):
            tps.append((lo, "trough")); trend = 1; hi = i; run_ = 0
    return tps, trend, (hi if trend > 0 else lo), px


def missed_reversals(tps, px, r: pd.Series):
    """Fidelity: inside each leg, the largest counter-move against the leg's direction; a counter-move above the zigzag threshold (max(FLOOR, MULT x monthly vol))
    is a turning point the rule failed to see. Returns the count and the worst one."""
    rr = r.fillna(0.0); thr = np.maximum(FLOOR, MULT * rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20))
    missed, worst = 0, 0.0
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        seg = px[a:b + 1]
        if ka == "trough":   # up leg: largest drawdown inside
            dd = (seg / np.maximum.accumulate(seg) - 1).min()
        else:                # down leg: largest rally inside
            dd = -(seg / np.minimum.accumulate(seg) - 1).max()
        if -dd >= thr[b]: missed += 1
        worst = min(worst, dd)
    return missed, float(-worst)


'''
    s = s.replace(old, new, 1)
    old = s[s.index("SEGMENTERS = [("):s.index("def segmenter_test(")]
    new = '''SEGMENTERS = [("zigzag 1.5× / 8% (registered)", lambda r: turning_points(r)[:4])] + \\
             [(f"persist-time N={n}, X={x:.0%}", (lambda n, x: (lambda r: turning_points_persist(r, n, x, "time")))(n, x)) for n in (2, 3, 5, 10) for x in (0.02, 0.04, 0.08)] + \\
             [(f"persist-closes N={n}, X={x:.0%}", (lambda n, x: (lambda r: turning_points_persist(r, n, x, "closes")))(n, x)) for n in (2, 3, 5) for x in (0.0, 0.02, 0.04, 0.08)] + \\
             [(f"swing k={k}", (lambda k: (lambda r: turning_points_swing(r, k)))(k)) for k in (5, 10, 20)]


'''
    s = s.replace(old, new, 1)
    # segmenter_test: fidelity column + criterion
    s = s.replace("        lengths = np.array([b - a for a, b, _ in legs]); sizes = np.array([abs(np.log(px[b] / px[a])) for a, b, _ in legs]); shares = []",
                  "        lengths = np.array([b - a for a, b, _ in legs]); sizes = np.array([abs(np.log(px[b] / px[a])) for a, b, _ in legs]); shares = []\n        missed, worst = missed_reversals(tps, px, r)", 1)
    s = s.replace("        rows.append(dict(rule=name, legs=len(legs), med_len=float(np.median(lengths)), short=float((lengths < 5).mean()), med_size=float(np.median(sizes)),\n                         scored=len(shares), r5=float(np.median(shares)) if shares else np.nan))",
                  "        rows.append(dict(rule=name, legs=len(legs), med_len=float(np.median(lengths)), short=float((lengths < 5).mean()), med_size=float(np.median(sizes)),\n                         scored=len(shares), r5=float(np.median(shares)) if shares else np.nan, missed=int(missed), worst_missed=float(worst)))", 1)
    s = s.replace("    better = df[(df.r5 >= reg.r5 + 0.05) & (df.scored >= reg.scored)] if np.isfinite(reg.r5) else df.iloc[0:0]",
                  "    better = df[(df.r5 >= reg.r5 + 0.05) & (df.scored >= reg.scored) & (df.missed <= reg.missed)] if np.isfinite(reg.r5) else df.iloc[0:0]   # fidelity: may not hide more reversals than the zigzag", 1)
    s = s.replace('f"(the promoted cell). \'short\' = share of legs under 5 sessions (noise legs). Verdict rule: another segmentation replaces the zigzag only if its median explained share is "\n         f"≥ 5 points higher with at least as many scored legs.*"',
                  'f"(the promoted cell). \'short\' = share of legs under 5 sessions (noise legs); \'missed\' = legs hiding a counter-move above the zigzag threshold (a reversal the rule did not see — fidelity, added 23 Oct after the "\n         f"consecutive-closes rule missed gold\'s August peak). Verdict rule: another segmentation replaces the zigzag only if its median explained share is ≥ 5 points higher, with at least as many scored legs, and no more missed reversals.*"', 1)
    s = s.replace('"| rule | legs since 2006 | median length (sessions) | share < 5 sessions | median size | legs scored | median explained share |", "|---|---|---|---|---|---|---|"]',
                  '"| rule | legs since 2006 | median length | share < 5 sessions | median size | legs scored | median explained share | missed reversals (worst) |", "|---|---|---|---|---|---|---|---|"]', 1)
    s = s.replace('''        L.append(f"| {q.rule} | {q.legs} | {q.get('med_len', float('nan')):.0f} | {q.get('short', float('nan')):.0%} | {np.expm1(q.get('med_size', 0)):.1%} | {q.get('scored', 0)} | {q.r5 if 'r5' in q and np.isfinite(q.r5) else float('nan'):.0%} |")''',
                  '''        L.append(f"| {q.rule} | {q.legs} | {q.get('med_len', float('nan')):.0f} | {q.get('short', float('nan')):.0%} | {np.expm1(q.get('med_size', 0)):.1%} | {q.get('scored', 0)} | {q.r5 if 'r5' in q and np.isfinite(q.r5) else float('nan'):.0%} | {int(q.get('missed', 0)) if 'missed' in q and pd.notna(q.get('missed')) else '—'} ({q.get('worst_missed', 0) if pd.notna(q.get('worst_missed', 0)) else 0:.0%}) |")''', 1)
    # segmenter_null + segment: support persist-time names / mode
    s = s.replace('    mm = re.match(r"persist N=(\\d+), X=(\\d+)%", rule_name)\n    if not mm: print(f"  only persistence rules are promotable here ({rule_name})"); return\n    n_, x_ = int(mm.group(1)), int(mm.group(2)) / 100; P = TI["params"]',
                  '    mm = re.match(r"persist-(time|closes) N=(\\d+), X=(\\d+)%", rule_name)\n    if not mm: print(f"  only persistence rules are promotable here ({rule_name})"); return\n    mode_, n_, x_ = mm.group(1), int(mm.group(2)), int(mm.group(3)) / 100; P = TI["params"]', 1)
    s = s.replace("    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; tps, trend, ext, px = turning_points_persist(r, n_, x_)",
                  "    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; tps, trend, ext, px = turning_points_persist(r, n_, x_, mode_)", 1)
    s = s.replace('        LEG_RULE.write_text(json.dumps(dict(rule="persist", n=n_, x=x_, promoted=',
                  '        LEG_RULE.write_text(json.dumps(dict(rule="persist", mode=mode_, n=n_, x=x_, promoted=', 1)
    s = s.replace('            n, x = int(j["n"]), float(j["x"]); tps, trend, ext, px = turning_points_persist(r, n, x)\n            thr = np.full(len(r), x if x > 0 else FLOOR)\n            return tps, trend, ext, px, thr, f"a reversal needs {n} consecutive sessions against the trend and a counter-move of at least {x:.0%} (persistence rule, promoted {j.get(\'promoted\', \'\')})"',
                  '            n, x, mode = int(j["n"]), float(j["x"]), j.get("mode", "time"); tps, trend, ext, px = turning_points_persist(r, n, x, mode)\n            thr = np.full(len(r), x if x > 0 else FLOOR)\n            how = (f"{n} consecutive sessions against the trend" if mode == "closes" else f"the price staying off its extreme for {n} sessions")\n            return tps, trend, ext, px, thr, f"a reversal needs {how} and a counter-move of at least {x:.0%} (persistence rule, promoted {j.get(\'promoted\', \'\')})"', 1)
    wm.write_text(s); print("  why_moved: time-mode persistence, fidelity column and criterion, promotion supports mode")

# ---- 3. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "fidelity" in s: print("  prereg fidelity: already")
else:
    s = s.replace("| date | change | reason |\n|---|---|---|\n", "| date | change | reason |\n|---|---|---|\n| 2026-10-23 (evening) | **T-I criterion amended: fidelity.** A segmentation may not hide a counter-move larger than the zigzag threshold inside a leg (a missed reversal); promotion needs share ≥ +5 pts, as many legs, and no more missed reversals than the zigzag. "
        "**Persistence rule re-specified** as 'sessions since the extreme ≥ N and counter-move ≥ X' (the founder's meaning: a trend that fails to resume), beside the literal 'N consecutive closes' version. | The consecutive-closes rule passed T-I (74%) and T-I′ (vs 11% noise) and was promoted — then failed by eye: it never confirmed gold's 25 Aug 2026 peak (the 14% fall had no five-day losing streak) and showed gold 'up since July'. "
        "The explained-share criterion rewarded a rule that keeps only clean, streaky legs. Promotion withdrawn the same evening (`processed/leg_rule_withdrawn_20261023.json`); the zigzag reinstated. **Prior #70:** persist-time N = 5, X = 4% passes fidelity, finds the August peak, and lands within ±5 points of the zigzag — no promotion. |\n", 1)
    s = s.rstrip("\n") + "\n| 2026-10-23 | T-I′ (GLD, consecutive-closes N=5/4%) | 74% vs 11% on shifted factors → PASS and promoted — **withdrawn two hours later**: the rule missed gold's August peak (no five-day losing streak in a 14% fall). A criterion that scores only explanation can be passed by a rule that declines to see messy legs. Fidelity added; see amendment. | **#69 right** on the null; the criterion was wrong, not the prior |\n"
    p.write_text(s); print("  prereg: fidelity amendment, T-I' record")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "withdrawn the same evening" in s: print("  MASTER row 49: already")
else:
    s = s.replace("| **PASS: N = 5, X = 4% → 74% vs 68%** (#68 wrong); pure gradient rules (X = 0) cut gold into hundreds of noise legs; T-I′ shifted-factor null decides promotion |",
                  "| **PASS: N = 5, X = 4% → 74% vs 68%** (#68 wrong), T-I′ null PASS, promoted — **withdrawn the same evening**: the consecutive-closes form never confirmed gold's 25 Aug peak (no five-day losing streak inside a 14% fall); fidelity criterion added (no leg may hide a counter-move above the zigzag threshold); persistence re-specified as sessions-since-extreme; re-run pending (#70) |", 1)
    m.write_text(s); print("  MASTER row 49: withdrawal recorded")
c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
if "withdrawn two hours later" in s: print("  CURRENT_STATE: already")
else:
    c.write_text(s.rstrip("\n") + """

**Addendum, 23 Oct evening — withdrawn two hours later.** The promoted rule (five consecutive closes against the trend, 4% counter-move) passed both
registered tests and then failed by eye: it showed gold "up since 16 July" with an "extreme of +17% on 25 Aug", because the 14% fall since August
never contained five straight down closes. A segmentation scored only on explained share can win by refusing to see messy legs. The promotion was
withdrawn (file kept with the reason), the zigzag reinstated, a fidelity criterion added — no leg may hide a counter-move larger than the zigzag's
threshold — and the founder's rule re-specified as he meant it: a trend that has failed to resume for N sessions, up days inside allowed. Prior #70:
that form finds the August peak and lands within five points of the zigzag; no promotion. The lesson goes in the standing rules: a test criterion must
include what a human would check first.
"""); print("  CURRENT_STATE: addendum")
print("done -- python -m src.why_moved segmenter-test GLD")
