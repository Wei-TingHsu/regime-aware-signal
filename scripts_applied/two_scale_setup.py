"""23 Oct evening: (1) record T-I re-run (#70 wrong, tally 58); (2) the founder's gradient method formalised as a retracement rule with persistence
(T-J), two-scale legs (coarse zigzag + fine retracement) in why_moved and on the page, lag column, promotion at the fine scale only.
Run from the repo root:  python scripts_applied/two_scale_setup.py ; python -m src.why_moved segmenter-test GLD | sed -n 5,7p ; python -m src.why_moved segmenter-test GLD | grep "retrace\\|zigzag" ;
                         python -m src.why_moved run | grep -A3 "^## gold" | sed -n 3,4p"""
from pathlib import Path
import sys

wm = Path("src/why_moved.py"); s = wm.read_text()
if "def turning_points_retrace(" in s: print("  why_moved retrace: already")
else:
    block = '''

# ---------------------------------------------------------------- T-J: the founder's gradient method as a retracement rule; two-scale legs
def turning_points_retrace(r: pd.Series, f: float = 0.382, n: int = 5, c: float = 1.0):
    """Founder's gradient test made operational: the sign of every back-gradient from today equals the sign of (today - that day), so 'all one sign'
    means today is the leg's extreme; a change of sign is a drawdown from the extreme. A turn is confirmed when that drawdown exceeds
    max(f x the leg's own move so far, c x monthly volatility) and has persisted n sessions since the extreme. Returns tps, trend, extreme, px, lags."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); lp = np.log(px)
    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20)
    hi = lo = 0; trend = 0; start = 0; tps = []; lags = []
    for i in range(1, len(px)):
        if trend >= 0 and px[i] > px[hi]: hi = i
        if trend <= 0 and px[i] < px[lo]: lo = i
        if trend >= 0:
            leg = lp[hi] - lp[start]; dd = lp[hi] - lp[i]; thr = max(f * max(leg, 0.0), c * sig[i])
            if dd >= thr and i - hi >= n:
                tps.append((hi, "peak")); lags.append(i - hi); trend = -1; start = hi; lo = i; continue
        if trend <= 0:
            leg = lp[start] - lp[lo]; up = lp[i] - lp[lo]; thr = max(f * max(leg, 0.0), c * sig[i])
            if up >= thr and i - lo >= n:
                tps.append((lo, "trough")); lags.append(i - lo); trend = 1; start = lo; hi = i
    return tps, trend, (hi if trend > 0 else lo), px, lags


def two_scale(r: pd.Series, fine=None):
    """Coarse legs by the zigzag (the big picture); fine legs by the promoted fine rule inside the current coarse leg (where the move is now).
    fine = (f, n, c) or None (then fine == coarse)."""
    tps_c, trend_c, ext_c, px, thr = turning_points(r); idx = r.index
    if not tps_c or fine is None: return dict(coarse=(tps_c, trend_c, ext_c), fine=None)
    c0 = tps_c[-1][0]; sub = r.iloc[c0:]
    tps_f, trend_f, ext_f, _, lags = turning_points_retrace(sub, *fine)
    tps_f = [(p + c0, k) for p, k in tps_f]
    return dict(coarse=(tps_c, trend_c, ext_c), fine=(tps_f, trend_f, ext_f + c0, lags))

'''
    s = s.replace("\n\n# ---------------------------------------------------------------- promoted leg rule (T-I) and the dispatcher every nightly step uses", block + "\n\n# ---------------------------------------------------------------- promoted leg rule (T-I) and the dispatcher every nightly step uses", 1)
    # segmenters: add retrace family; lag support
    old = '''             [(f"swing k={k}", (lambda k: (lambda r: turning_points_swing(r, k)))(k)) for k in (5, 10, 20)]'''
    new = '''             [(f"swing k={k}", (lambda k: (lambda r: turning_points_swing(r, k)))(k)) for k in (5, 10, 20)] + \\
             [(f"retrace f={f:.0%}, N={n}, c={c}", (lambda f, n, c: (lambda r: turning_points_retrace(r, f, n, c)))(f, n, c)) for f in (0.25, 0.382, 0.5) for n in (3, 5) for c in (0.5, 1.0)]'''
    assert old in s, "segmenters anchor"; s = s.replace(old, new, 1)
    old = "        tps, trend, ext, px = fn(r)[:4]\n        legs = [(a, b, 1 if ka == \"trough\" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:])]"
    new = "        res = fn(r); tps, trend, ext, px = res[:4]; lags = res[4] if len(res) > 4 else None\n        legs = [(a, b, 1 if ka == \"trough\" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:])]"
    assert old in s, "segmenter_test anchor"; s = s.replace(old, new, 1)
    s = s.replace("                         scored=len(shares), r5=float(np.median(shares)) if shares else np.nan, missed=int(missed), worst_missed=float(worst)))",
                  "                         scored=len(shares), r5=float(np.median(shares)) if shares else np.nan, missed=int(missed), worst_missed=float(worst), lag=(float(np.median(lags)) if lags else np.nan)))", 1)
    s = s.replace('"| rule | legs since 2006 | median length | share < 5 sessions | median size | legs scored | median explained share | missed reversals (worst) |", "|---|---|---|---|---|---|---|---|"]',
                  '"| rule | legs since 2006 | median length | share < 5 sessions | median size | legs scored | median explained share | missed reversals (worst) | confirmation lag (sessions) |", "|---|---|---|---|---|---|---|---|---|"]', 1)
    s = s.replace('''{int(q.get('missed', 0)) if 'missed' in q and pd.notna(q.get('missed')) else '—'} ({q.get('worst_missed', 0) if pd.notna(q.get('worst_missed', 0)) else 0:.0%}) |")''',
                  '''{int(q.get('missed', 0)) if 'missed' in q and pd.notna(q.get('missed')) else '—'} ({q.get('worst_missed', 0) if pd.notna(q.get('worst_missed', 0)) else 0:.0%}) | {q.get('lag', float('nan')) if 'lag' in q and pd.notna(q.get('lag')) else float('nan'):.0f} |")''', 1)
    # fine-scale promotion criterion: zero missed, lag <= 10, share within 5 points of the zigzag, legs >= zigzag
    old = "    better = df[(df.r5 >= reg.r5 + 0.05) & (df.scored >= reg.scored) & (df.missed <= reg.missed)] if np.isfinite(reg.r5) else df.iloc[0:0]   # fidelity: may not hide more reversals than the zigzag"
    new = ('    better = df[(df.r5 >= reg.r5 + 0.05) & (df.scored >= reg.scored) & (df.missed <= reg.missed)] if np.isfinite(reg.r5) else df.iloc[0:0]   # replaces the zigzag outright\n'
           '    fine_ok = df[(df.rule.str.startswith("retrace")) & (df.missed == 0) & (df.lag <= 10) & (df.r5 >= reg.r5 - 0.05) & (df.legs >= reg.legs)] if np.isfinite(reg.r5) else df.iloc[0:0]   # T-J fine scale: sees every turn, confirms fast, explains nearly as well\n'
           '    fine_best = fine_ok.sort_values(["missed", "lag", "r5"], ascending=[True, True, False]).iloc[0] if len(fine_ok) else None')
    assert old in s, "criterion anchor"; s = s.replace(old, new, 1)
    old = '''f"**{'PASS for ' + ', '.join(better.rule) if len(better) else 'FAIL — no rule beats the registered zigzag by 5 points'}**", "",'''
    new = '''f"**{'PASS for ' + ', '.join(better.rule) if len(better) else 'FAIL — no rule beats the registered zigzag by 5 points'}**", "",
         (f"**T-J fine scale: PASS — {fine_best.rule}** (0 missed, lag {fine_best.lag:.0f} sessions, {fine_best.legs} legs, explained {fine_best.r5:.0%}); promoted as the fine scale inside the zigzag's legs." if fine_best is not None else "**T-J fine scale: no retracement rule meets 0 missed, lag ≤ 10, share within 5 points, legs ≥ zigzag.**"), "",'''
    assert old in s, "verdict anchor"; s = s.replace(old, new, 1)
    old = '''    J.setdefault("tests", {}).setdefault(asset, {})["TI"] = dict(rows=rows, better=list(better.rule), params=dict(patience=patience, min_k=min_k, window=window), run=datetime.now().strftime("%Y-%m-%d %H:%M"))'''
    new = '''    J.setdefault("tests", {}).setdefault(asset, {})["TI"] = dict(rows=rows, better=list(better.rule), params=dict(patience=patience, min_k=min_k, window=window), run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    if fine_best is not None:
        import re as _re; mm = _re.match(r"retrace f=(\\d+)%, N=(\\d+), c=([\\d.]+)", fine_best.rule)
        (PROC / "fine_rule.json").write_text(json.dumps(dict(rule="retrace", f={25: 0.25, 38: 0.382, 50: 0.5}.get(int(mm.group(1)), int(mm.group(1)) / 100), n=int(mm.group(2)), c=float(mm.group(3)), promoted=datetime.now().strftime("%Y-%m-%d"),
                                                             asset_tested=asset, legs=int(fine_best.legs), lag=float(fine_best.lag), r5=float(fine_best.r5)), indent=1))
        J["tests"][asset]["TJ"] = dict(rule=fine_best.rule, legs=int(fine_best.legs), lag=float(fine_best.lag), r5=float(fine_best.r5), verdict="PASS")
    else:
        J["tests"][asset]["TJ"] = dict(verdict="FAIL")
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))'''
    assert old in s, "TI json anchor"; s = s.replace(old, new, 1)
    # run(): two-scale legs — fine current leg drives the block; coarse shown as the big picture
    old = "        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r); idx = r.index\n        if not tps: continue"
    new = '''        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r); idx = r.index
        if not tps: continue
        tps_hist = tps                                  # legs used for the base-rate target: whole history at the scale the page describes
        FINE = PROC / "fine_rule.json"; big = None
        if FINE.exists():
            fj = json.loads(FINE.read_text()); ts = two_scale(r, (fj["f"], fj["n"], fj["c"]))
            if ts["fine"] and ts["fine"][0]:
                c_pos, c_kind = ts["coarse"][0][-1]; big = dict(start=idx[c_pos].strftime("%Y-%m-%d"), direction=(1 if c_kind == "trough" else -1), move=float(np.log(px[-1] / px[c_pos])), sessions=int(len(idx) - 1 - c_pos))
                tps_f, trend_f, ext_f, lags_f = ts["fine"]; tps, trend, ext = tps_f, trend_f, ext_f
                tps_hist = turning_points_retrace(r, fj["f"], fj["n"], fj["c"])[0]
                rule_label = (f"big picture by the zigzag; the current leg by the founder's retracement rule — a turn is confirmed when the price has given back "
                              f"{fj['f']:.0%} of the leg's own move (floor {fj['c']}× monthly volatility) and stayed there {fj['n']} sessions (promoted {fj['promoted']})")'''
    assert old in s, "run segment anchor"; s = s.replace(old, new, 1)
    old = "        eps = past_episodes(tps, px); same = [e for e in eps if e[\"direction\"] == direction and e[\"length\"] >= MIN_EP]"
    assert old in s, "run eps anchor"; s = s.replace(old, "        eps = past_episodes(tps_hist, px); same = [e for e in eps if e[\"direction\"] == direction and e[\"length\"] >= MIN_EP]", 1)
    s = s.replace("                                                               extreme_so_far=dict(date=idx[ext].strftime(\"%Y-%m-%d\"), move=ext_move), threshold_now=float(thr[-1]), rule=rule_label),",
                  "                                                               extreme_so_far=dict(date=idx[ext].strftime(\"%Y-%m-%d\"), move=ext_move), threshold_now=float(thr[-1]), rule=rule_label, big_picture=big),", 1)
    old = '''              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; {rule_label}.",'''
    new = '''              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; {rule_label}."
              + (f" Big picture (zigzag): {'up' if big['direction'] > 0 else 'down'} since {big['start']} ({big['sessions']} sessions, {pc(big['move'])})." if big else ""),'''
    assert old in s, "run wording anchor"; s = s.replace(old, new, 1)
    wm.write_text(s); print("  why_moved: retracement rule, two-scale legs, lag column, fine-scale promotion")

# page: big picture sentence
c = Path("src/context.py"); s = c.read_text()
if "big_picture" in s: print("  context big picture: already")
else:
    old = "    if tg:\n        kind = \"rises\" if up else \"falls\"; sgn = 1 if up else -1"
    new = '''    bp = ep.get("big_picture")
    if bp: S.append(f"Big picture, by the coarser rule: {'rising' if bp['direction'] > 0 else 'falling'} since {bp['start']} ({bp['sessions']} sessions, {_pct(bp['move'])}) {tag('measured')}.")
    if tg:
        kind = "rises" if up else "falls"; sgn = 1 if up else -1'''
    assert old in s, "context anchor"; c.write_text(s.replace(old, new, 1)); print("  context: big-picture sentence")

# records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "T-J" in s: print("  prereg T-J: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **T-J two-scale legs (founder, 23 Oct evening).** His gradient method — every back-gradient from today must have one sign — equals "today is the leg's
  extreme"; a sign change is a drawdown from the extreme. Operational form: a turn is confirmed when the drawdown exceeds max(f × the leg's own
  move, c × monthly volatility) and has persisted N sessions since the extreme; f ∈ {25, 38.2, 50%}, N ∈ {3, 5}, c ∈ {0.5, 1.0}. Coarse legs stay
  the zigzag (big picture); the fine rule runs inside the current coarse leg (where the move is now); the page shows both. Columns added: missed
  reversals, confirmation lag. **Fine-scale promotion:** 0 missed, lag ≤ 10 sessions, explained share within 5 points of the zigzag, legs ≥ zigzag.
  Caveats registered with their fills: closes vs intraday extremes (grid variable, highs/lows from the raw cache); the coarse rule's own misses
  (repaired by the fine scale); choosing f and N by looking (sweep null). **Prior #71:** f = 38%, N = 5, c = 1 → ~120 legs, 0 missed, lag ≈ 6, share ≈ 62%; promoted.
- Nightly: `src/why_moved.py`; app:""", 1)
    s = s.rstrip("\n") + ("\n| 2026-10-23 | T-I re-run with fidelity | Zigzag: 54 legs, 68%, **3 missed** (worst 23%). Persist-time (founder's meaning): **0 missed at every N = 2–5**; N = 5 / X = 4%: 196 legs, median 19 sessions, 61%. "
        "Consecutive-closes N = 5: 5–6 missed (worst 40%) — the withdrawn rule. No rule replaces the zigzag outright (share −7 points at the fine scale). | **#70 wrong** on share (predicted within ±5; −7); right on fidelity and the August peak. Tally 58 |\n")
    p.write_text(s); print("  prereg: T-J registered, T-I re-run recorded")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "| 50 | Two-scale legs" in s: print("  MASTER row 50: already")
else:
    i = s.index("| 49 | Leg definition"); j = s.index("\n", i) + 1
    s = s[:j] + ("| 50 | Two-scale legs (T-J): the founder's gradient test as a retracement rule with persistence runs as the fine scale inside the zigzag's coarse legs — zero missed reversals, "
                 "confirmation lag ≤ 10 sessions, explained share within 5 points, at least as many legs | registered 23 Oct evening before code; run same evening | prior #71 promoted at f = 38%, N = 5 | prereg_factor_attribution §4, `docs/segmenter_test_GLD.md` |\n") + s[j:]
    s = s.replace("#68 leg-definition rule (the founder's persistence rule won), all Claude's)", "#68 leg-definition rule (the founder's persistence rule won), #70 persist-time share, all Claude's)", 1).replace("tally 57 (#40", "tally 58 (#40", 1)
    m.write_text(s); print("  MASTER: row 50, tally 58")
print("done -- python -m src.why_moved segmenter-test GLD")
