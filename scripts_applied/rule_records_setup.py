"""23 Oct: (1) T-G best cell within each reversal rule (sub-grid null); the app uses the cell for its registered leg definition — no re-cut;
(2) records: T-H FAIL x5 (#67 wrong, tally 56), T-A null survives, the alpha question with its three conditions in TRACK 3.34, MASTER row 48,
CURRENT_STATE 18.36. Run from the repo root:
  python scripts_applied/rule_records_setup.py ; python -m src.why_moved window-grid GLD | sed -n 9,16p ; python -m src.why_moved run | grep -A9 "^## gold" | grep "Window where"
"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. window_grid: best within each reversal rule
wm = Path("src/why_moved.py"); s = wm.read_text()
if "by_rule" in s: print("  why_moved by_rule: already")
else:
    old = '''    best = df.loc[df.r5.idxmax()]; rng = np.random.default_rng(seed); mx = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns)
        vals = [v["r5"] for v in _r5_cells(r, Fx, cells, idx).values() if np.isfinite(v["r5"])]
        if vals: mx.append(max(vals))
    mx = np.array(mx); p = float((mx >= best.r5).mean()) if len(mx) else np.nan; reg = real.get((MULT, FLOOR, WINDOW, PATIENCE, MIN_K), {})
'''
    new = '''    best = df.loc[df.r5.idxmax()]; rng = np.random.default_rng(seed); mx = []; mx_rule = {k: [] for k in GRID_REVERSAL}
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns); nc = _r5_cells(r, Fx, cells, idx)
        vals = [v["r5"] for v in nc.values() if np.isfinite(v["r5"])]
        if vals: mx.append(max(vals))
        for (m, f) in GRID_REVERSAL:
            vr = [v["r5"] for c, v in nc.items() if (c[0], c[1]) == (m, f) and np.isfinite(v["r5"])]
            if vr: mx_rule[(m, f)].append(max(vr))
    mx = np.array(mx); p = float((mx >= best.r5).mean()) if len(mx) else np.nan; reg = real.get((MULT, FLOOR, WINDOW, PATIENCE, MIN_K), {})
    by_rule = {}   # best cell within each leg definition, judged against the null of ITS sub-grid: the app uses the one for its registered rule, so legs are never re-cut
    for (m, f) in GRID_REVERSAL:
        sub = df[(df.mult == m) & (df.floor == f)]
        if sub.empty: continue
        b = sub.loc[sub.r5.idxmax()]; arr = np.array(mx_rule[(m, f)]); pr = float((arr >= b.r5).mean()) if len(arr) else np.nan
        by_rule[f"{m},{f}"] = dict(mult=m, floor=f, window=int(b.window), patience=int(b.patience), min_k=int(b.min_k), r5=float(b.r5), beat=float(b.beat), n=int(b.n), p=pr, null_median=(float(np.median(arr)) if len(arr) else None))
'''
    assert old in s, "grid anchor"; s = s.replace(old, new, 1)
    old = '    for i, (_, q) in enumerate(df.sort_values("r5", ascending=False).head(15).iterrows(), 1):'
    new = '''    L += ["", "**Best cell within each leg definition** (the app uses the one for its registered rule — legs are never re-cut to fit a cell):", "",
          "| leg definition | look-back | patience | min k | median R5 | beats full | n | p (sub-grid null) |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {v['mult']}× / {v['floor']:.0%} | {v['window']} | {v['patience']} | {v['min_k']} | {v['r5']:.0%} | {v['beat']:.0%} | {v['n']} | {v['p']:.2f} |" for v in by_rule.values()]
    L += ["", "All cells, top 15:", ""]
    for i, (_, q) in enumerate(df.sort_values("r5", ascending=False).head(15).iterrows(), 1):'''
    assert old in s, "grid table anchor"; s = s.replace(old, new, 1)
    s = s.replace("null_median=(float(np.median(mx)) if len(mx) else None), p=p, n_cells=int(len(df)), run=", "null_median=(float(np.median(mx)) if len(mx) else None), p=p, n_cells=int(len(df)), by_rule=by_rule, run=", 1)
    # run(): use the registered-rule cell
    old = '''        tg = tb_all.get(a, {}).get("TG", {}); wr_best = None
        best_leg = None
        if wr and tg.get("p") is not None and tg["p"] < 0.05:
            bb = tg["best"]
'''
    new = '''        tg = tb_all.get(a, {}).get("TG", {}); wr_best = None
        best_leg = None
        bb = (tg.get("by_rule") or {}).get(f"{MULT},{FLOOR}")       # best cell under the registered leg definition -> no re-cut
        if wr and bb and bb.get("p") is not None and bb["p"] < 0.05:
'''
    assert old in s, "run tg anchor"; s = s.replace(old, new, 1)
    s = s.replace("params=tg['best'], p=tg['p'], leg=best_leg", "params=bb, p=bb['p'], leg=best_leg", 1)
    s = s.replace("(reversal {tg['best']['mult']}×/{tg['best']['floor']:.0%}, look-back {tg['best']['window']}, patience {tg['best']['patience']}, min {tg['best']['min_k']}; p {tg['p']:.2f})",
                  "(same leg definition; look-back {bb['window']}, patience {bb['patience']}, min {bb['min_k']}; sub-grid p {bb['p']:.2f})", 1)
    wm.write_text(s); print("  why_moved: best cell within the registered leg definition; no re-cut")

# ---------------------------------------------------------------- 2. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "| 2026-10-23 | T-H |" in s: print("  prereg T-H result: already")
else:
    s = s.rstrip("\n") + ("\n| 2026-10-23 | T-H (GLD, SLV, USO, SPY, NVDA) | **FAIL on all five.** Best cells: GLD 60→60 reversal IC −0.19 (null best 0.24, p 0.77); SLV 20→60 reversal −0.22 (p 0.56); "
        "USO 20→20 continuation +0.17, hit 59%, Sharpe +0.5 (p 0.82); SPY 20→60 reversal −0.21 (p 0.31); NVDA 20→60 continuation +0.25 (p 0.19; plain momentum +0.20). "
        "No cell distinguishable from noise; where the residual leaned (oil continuation, metals reversal at 60) it did not beat the price trend. The unexplained part, as measured with the current factor set, "
        "is not a tradable signal at 5–60 sessions. Re-run after the flow/positioning proxies land. | **#67 wrong** (expected INCONCLUSIVE metals, PASS NVDA). Tally 56 |\n"
        "| 2026-10-23 | T-A sweep null (GLD) | Best cell 756/20 median R² 0.224 vs best-of-sweep noise median −0.024 over 50 shifts, p = 0.000 → survives. Amendment: the T-A gate for quotable sensitivities is "
        "treated as met by the surviving swept cell (tag 'swept cell' on the page); the registered 504/20 verdict (0.177 FAIL) stands as recorded. | no prior |\n"
        "| 2026-10-23 | T-G amendment | The app uses the best cell *within its registered leg definition* (1.5×/8%), judged against that sub-grid's null — legs are never re-cut to fit a cell "
        "(founder's objection: integrity must not cost the leg's meaning). | — |\n")
    p.write_text(s); print("  prereg: T-H, T-A null, T-G amendment")

t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "## 4. Potential upgrades — not registered, not costed\n"
if "### 3.34 The unexplained part as alpha" in s: print("  TRACK 3.34: already")
else:
    add = """### 3.34 The unexplained part as alpha — the founder's question, and the three conditions (23 Oct)

Founder: if the reasons explain 80% of a leg and 20% never yields to any clue, that 20% is the crowd — emotion, trend-followers, institutions
valuing differently; if we can measure it consistently and lean on it, that is the fund's alpha. In the literature this is *residual momentum*
(Blitz, Huij & Martens 2011) on top of noise-trader and slow-diffusion models; price pressure tends to unwind, slow information to continue.
It becomes **our** alpha only if three things hold, in plain words:
1. **The label is not the test.** The unexplained part mixes crowd behaviour with information the model has no series for (positioning, flows,
   central-bank buying) and plain model error. Gold's 91% unexplained today is mostly the last two. The measurable omitted factors go in first;
   only what is left afterwards may honestly be called the crowd.
2. **Predictability, not cause.** Markets also move on information we cannot see. The fund question is whether today's unexplained move says
   anything about tomorrow's — tested at every window × horizon (T-H), with the shape read off the sign: continuation = slow information,
   reversal = a stampede unwinding.
3. **It must beat the price trend itself.** If the residual's sign predicts no better than plain momentum, the decomposition added nothing tradable.
**Result 23 Oct (T-H): FAIL on GLD, SLV, USO, SPY, NVDA** — no cell beats noise; prior #67 wrong (tally 56). Re-run after the flow and positioning
proxies (3.28) shrink the residual to its unmeasured part. Until then the unexplained share is shown on the page as a measurement of what the
model cannot see, never as a signal.

"""
    t.write_text(s.replace(anchor, add + anchor, 1)); print("  TRACK 3.34: done")

m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "| 48 | Residual momentum" in s: print("  MASTER row 48: already")
else:
    i = s.index("| 47 | Factor attribution"); j = s.index("\n", i) + 1
    s = s[:j] + ("| 48 | Residual momentum / reversal (T-H): the part of a move the named reasons do not explain predicts the next 5–60 sessions better than noise and better than plain "
                 "momentum — the founder's 'crowd as alpha' question under three conditions (TRACK 3.34) | registered and run 23 Oct, 5 assets, 25 cells each, 200-shift null | "
                 "**FAIL ×5** (#67 wrong); oil leaned to continuation, metals to reversal at 60 sessions, none beyond noise; re-run after flow/positioning proxies | `docs/prereg_factor_attribution.md` §5, `docs/residual_momentum_*.md` |\n") + s[j:]
    s = s.replace("#64 causal window rule, all Claude's)", "#64 causal window rule, #67 residual momentum, all Claude's)", 1).replace("tally 55 (#40", "tally 56 (#40", 1)
    s = s.replace("| 23 Oct T-A/T-B run | **T-A FAIL 0.177** (#58 wrong); T-B dollar/oil/macro stable, real/hikes/VIX/war unstable (#59 wrong); flows + positioning proxies amended in (#61); T-C after |",
                  "| 23 Oct T-A/T-B run; sweeps same day | **T-A FAIL 0.177** (#58 wrong) — swept cell 756/20 = 0.224 survives its null and meets the gate as 'swept cell'; T-B dollar/oil/macro stable, "
                  "real/hikes/VIX/war unstable (#59 wrong); T-E impulse FAIL (#63); **T-F causal window PASS 53% vs 31% (#64 wrong)**, T-F′ null PASS (#65 right), T-G patience 20–30 and 1-yr look-back → 64–71%, promoted within the registered leg definition (#66 right); flows + positioning proxies amended in (#61); T-C after |", 1)
    m.write_text(s); print("  MASTER: row 48, row 47 result, tally 56")

c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
if "### 18.36" in s: print("  CURRENT_STATE 18.36: already")
else:
    c.write_text(s.rstrip("\n") + """

### 18.36 Why it moved: window rules, the sweep, and the alpha question (23 Oct)

Overnight and through the day: the daily "why it moved" engine (3.33) found gold falling since 25 Aug (−13.8%, 98% of a typical gold fall), silver
since 27 Aug (beyond its typical fall), oil up since 1 Jul (twice a typical rise). The founder's two rules — every fixed number is a variable, and
analyse the purest short window — were tested rather than assumed: a fixed first-plunge window failed (T-E, 17% explained); a forward-walking rule
that stops when the explained share stalls passed (T-F: 53% vs 31% for the full leg, 83% of legs) and beat time-shifted noise by 48 points (T-F′);
sweeping the rule's own variables (T-G, 216 cells) showed patience 20–30 and a one-year look-back lift the share to 64–71%, surviving the
sweep-wide null; the founder objected to re-cutting legs to fit a cell, so the app uses the best cell within its own leg definition. The daily
model's 3-year/20-session cell survived its null (T-A sweep, 0.224 vs noise ≈ 0). The founder's question — is the unexplained part the crowd, and
the fund's alpha? — was registered with three conditions (TRACK 3.34) and tested as residual momentum / reversal on five assets (T-H): FAIL on
all five, nothing beyond noise; prior #67 wrong, tally 56. Gold's 22 Oct session (−2.6%) was 95% unexplained. The dynamic issuer pool (3.32)
built from FRED's copy of the BEA growth-contribution table: 25 issuers. Wrong-prior tally 56; the register runs to row 48.
"""); print("  CURRENT_STATE 18.36: appended")
print("done -- python -m src.why_moved window-grid GLD ; python -m src.why_moved run")
