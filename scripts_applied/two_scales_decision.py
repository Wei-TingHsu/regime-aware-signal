"""23 Oct evening — founder's decision: two scales. Coarse = zigzag (context, misses nothing at its scale); current leg = the founder's two-step rule
(leg_rule.json, role 'current'); the third (fine) scale withdrawn as redundant. run() and the page restructured; records (#74 wrong, tally 61).
Run from the repo root:  python scripts_applied/two_scales_decision.py ; python -m src.why_moved run | grep -A3 "^## gold" | sed -n 3,4p | cut -c1-420 ; python -m src.context show GLD | sed -n 3,3p | cut -c1-600"""
from pathlib import Path
import sys, json
from datetime import datetime

PROC = Path("processed")
# ---- 1. files: role on the leg rule; third scale withdrawn (kept as a candidate record)
lr = PROC / "leg_rule.json"
if lr.exists():
    j = json.loads(lr.read_text()); j["role"] = "current"; j["decision"] = "founder, 23 Oct: two scales — zigzag for context, this rule for the current leg"; lr.write_text(json.dumps(j, indent=1)); print("  leg_rule.json: role = current")
fr = PROC / "fine_rule.json"
if fr.exists():
    j = json.loads(fr.read_text()); j["withdrawn"] = datetime.now().strftime("%Y-%m-%d %H:%M"); j["reason"] = "founder chose two scales; a third (fine) scale is redundant — the impulse covers the short end"
    fr.replace(PROC / "fine_rule_candidate.json"); (PROC / "fine_rule_candidate.json").write_text(json.dumps(j, indent=1)); print("  fine_rule.json -> fine_rule_candidate.json (record only)")

# ---- 2. why_moved: run() on two scales; T-J records a candidate, never a live file
wm = Path("src/why_moved.py"); s = wm.read_text()
if "two scales (founder, 23 Oct)" in s: print("  why_moved two scales: already")
else:
    old = s[s.index("        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r, a); idx = r.index"):s.index("        s0_pos, kind = tps[-1]; s0, s1 = idx[s0_pos], idx[-1]; direction = 1 if kind == \"trough\" else -1")]
    new = '''        F = factors(r.index); idx = r.index
        # two scales (founder, 23 Oct): coarse = the zigzag (context; it misses nothing at its scale); current leg = the promoted rule (explains most)
        tps_c, trend_c, ext_c, px, thr = turning_points(r); big = None
        if not tps_c: continue
        rule_label = "a reversal needs a counter-move of 1.5 × the asset's own monthly volatility, floor 8% (zigzag rule)"; tps, trend, ext = tps_c, trend_c, ext_c
        if LEG_RULE.exists():
            lj = json.loads(LEG_RULE.read_text()); tps_m, trend_m, ext_m, _ = run_rule(r, lj, a)
            if tps_m:
                c_pos, c_kind = tps_c[-1]
                big = dict(start=idx[c_pos].strftime("%Y-%m-%d"), direction=(1 if c_kind == "trough" else -1), move=float(np.log(px[-1] / px[c_pos])), sessions=int(len(idx) - 1 - c_pos), scale="quarter scale, zigzag")
                tps, trend, ext = tps_m, trend_m, ext_m
                how = (f"{lj['n']} open-to-close days against the trend" if lj.get("daysign") == "oc" else f"{lj['n']} sessions off the extreme")
                rule_label = (f"the founder's rule — a turn is confirmed when the price has given back {lj['f']:.0%} of the leg's own move (floor {lj['c']}× monthly volatility, never more than the zigzag's threshold) "
                              f"and {how}{'; extremes from the high and low of the day' if lj.get('hl') else ''} (current-leg scale, promoted {lj.get('promoted', '')})")
        tps_hist = tps
'''
    s = s.replace(old, new, 1)
    # the T-J fine promotion writes a candidate record, not a live rule
    s = s.replace('        (PROC / "fine_rule.json").write_text(json.dumps(dict(rule="retrace", hl=bool(mm.group(1))', '        (PROC / "fine_rule_candidate.json").write_text(json.dumps(dict(rule="retrace", hl=bool(mm.group(1))', 1)
    s = s.replace('(f"**T-J fine scale: PASS — {fine_best.rule}** (0 missed, lag {fine_best.lag:.0f} sessions, {fine_best.legs} legs, explained {fine_best.r5:.0%}); promoted as the fine scale inside the zigzag\'s legs."',
                  '(f"**T-J fine scale: PASS — {fine_best.rule}** (0 missed, lag {fine_best.lag:.0f} sessions, {fine_best.legs} legs, explained {fine_best.r5:.0%}); recorded as a candidate — the founder chose two scales, a third is not shown."', 1)
    # page line: name the scale of the typical size
    s = s.replace('''              (f"- Typical {'rise' if direction > 0 else 'fall'} of this kind for {NAME.get(a, a)}: {pc(direction * tgt['med_size'])} from the start (middle half of past episodes {pc(direction * tgt['q25'])} to {pc(direction * tgt['q75'])}), "''',
                  '''              (f"- Typical {'rise' if direction > 0 else 'fall'} at this scale for {NAME.get(a, a)}: {pc(direction * tgt['med_size'])} from the start (middle half of past legs {pc(direction * tgt['q25'])} to {pc(direction * tgt['q75'])}), "''', 1)
    s = s.replace('''              + (f" Big picture (leg definition): {'up' if big['direction'] > 0 else 'down'} since {big['start']} ({big['sessions']} sessions, {pc(big['move'])})." if big else ""),''',
                  '''              + (f" Big picture ({big['scale']}): {'up' if big['direction'] > 0 else 'down'} since {big['start']} ({big['sessions']} sessions, {pc(big['move'])})." if big else ""),''', 1)
    wm.write_text(s); print("  why_moved: two scales in run(); T-J records candidates only; scale named on the typical-size line")

# ---- 3. context: say which scale the typical refers to
c = Path("src/context.py"); s = c.read_text()
if "at this scale" in s: print("  context: already")
else:
    s = s.replace('    if bp: S.append(f"Big picture, by the coarser rule: {\'rising\' if bp[\'direction\'] > 0 else \'falling\'} since {bp[\'start\']} ({bp[\'sessions\']} sessions, {_pct(bp[\'move\'])}) {tag(\'measured\')}.")',
                  '    if bp: S.append(f"Big picture ({bp.get(\'scale\', \'coarser rule\')}): {\'rising\' if bp[\'direction\'] > 0 else \'falling\'} since {bp[\'start\']} ({bp[\'sessions\']} sessions, {_pct(bp[\'move\'])}) {tag(\'measured\')}. The current leg below is cut at a finer scale, so \'typical\' there means typical for legs of that scale.")', 1)
    s = s.replace('            S.append(f"Past {kind} of this kind ran a median {_pct(sgn * tg[\'med_size\'])} from their start over {tg[\'med_length\']:.0f} sessions (n {tg[\'n\']}); this one is at "',
                  '            S.append(f"Past {kind} at this scale ran a median {_pct(sgn * tg[\'med_size\'])} from their start over {tg[\'med_length\']:.0f} sessions (n {tg[\'n\']}); this one is at "', 1)
    s = s.replace('            S.append(f"Past {kind} of this kind ran a median {_pct(sgn * tg[\'med_size\'])} (n {tg[\'n\']}); this one is already larger than {tg.get(\'pct_rank\', 0):.0%} of them — the base rate gives no further level {tag(\'measured\')}.")',
                  '            S.append(f"Past {kind} at this scale ran a median {_pct(sgn * tg[\'med_size\'])} (n {tg[\'n\']}); this one is already larger than {tg.get(\'pct_rank\', 0):.0%} of them — at this scale the base rate gives no further level {tag(\'measured\')}.")', 1)
    c.write_text(s); print("  context: scale named")

# ---- 4. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "two scales (founder's decision" in s: print("  prereg: already")
else:
    s = s.replace("| date | change | reason |\n|---|---|---|\n", "| date | change | reason |\n|---|---|---|\n| 2026-10-23 (evening) | **Two scales (founder's decision).** Coarse = the zigzag, kept as context (under the move-date fidelity measure it misses nothing at its scale). "
        "Current leg = the founder's two-step rule (retrace-hl-oc f = 38%, N = 3, c = 0.5): 114 legs, median 25 sessions, explained 79% (zigzag 68%), 1 missed of 114, lag 11, 79% vs 11% on shifted factors. "
        "The third (fine) scale is withdrawn as redundant — the impulse covers the short end; T-J records candidates only. Standing re-evaluation: a grid rule replaces the current-leg rule if it explains more with ≤ 1 missed and lag ≤ 12. "
        "The page names the scale wherever it says 'typical'. | Under the corrected fidelity the zigzag has 0 missed, so the two-step no longer meets the outright criterion (≤ 0 missed) while remaining the best explainer by 11 points; a quarter-scale leg and a five-week leg give opposite readings of 'typical' for the same fall. **#74 wrong** (zigzag ~3 missed predicted; 0 measured; outright promotion did not hold). Tally 61. |\n", 1)
    p.write_text(s); print("  prereg: two-scales amendment")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 61" in s: print("  MASTER: already")
else:
    s = s.replace("#72 cap effect, all Claude's)", "#72 cap effect, #74 corrected-fidelity counts, all Claude's)", 1).replace("tally 60 (#40", "tally 61 (#40", 1)
    s = s.replace("null and promotion as the leg definition pending the corrected fidelity measure (#72 wrong, #73 right, #74 open) |",
                  "null PASS (79% vs 11%); under the move-date fidelity the zigzag misses 0 and the two-step 1, so no outright replacement — **founder's decision: two scales**, zigzag for context, the two-step for the current leg; third scale withdrawn (#72, #74 wrong; #73 right) |", 1)
    s = s.replace("against the zigzag's 68% on 54, 2 missed vs 3, lag 11; 79% real vs 11% on noise → promoted as the leg definition. Five open-to-close days in a row freezes",
                  "against the zigzag's 68% on 54; 79% real vs 11% on noise; under the corrected fidelity it misses 1 and the zigzag 0, so the founder chose two scales — the zigzag for context, his rule for the current leg. Five open-to-close days in a row freezes", 1)
    m.write_text(s); print("  MASTER: row 50 final, Block 5 findings, tally 61")
cs = Path("docs/CURRENT_STATE_2026-08-23.md"); s = cs.read_text()
if "### 18.38" in s: print("  CURRENT_STATE 18.38: already")
else:
    cs.write_text(s.rstrip("\n") + """

### 18.38 Two scales — the founder's decision (23 Oct, evening)

With fidelity measured at the move's own date the zigzag misses nothing at its scale and the founder's two-step rule misses one counter-move in 114
legs while explaining 79% of them against the zigzag's 68%. Neither replaces the other; the founder chose two scales: the zigzag on top as the
quarter-scale context, his rule underneath as the current leg where "why it moved" is computed. The third scale that T-J had promoted is withdrawn
as redundant. The page names the scale wherever it says "typical", because a 14% gold fall is 78% of a typical quarter-scale fall and 193% of a
typical five-week leg at the same time. PROJECT_MASTER §2.1 holds the day's ideas as a story in eight blocks. Tally 61; register row 50.
"""); print("  CURRENT_STATE 18.38: appended")
print("done -- python -m src.why_moved run")
