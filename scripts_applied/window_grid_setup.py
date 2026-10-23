"""23 Oct: (1) tests() merges instead of overwriting an asset's record; (2) window-rule variables parametrised and swept (T-G: patience x
min window x look-back x reversal rule), best cell vs best-of-sweep null on shifted factors; (3) the after-the-fact ceiling on the current
leg gets a noise calibration; (4) records. Run from the repo root:
  python scripts_applied/window_grid_setup.py ; python -m src.why_moved window-test GLD | sed -n 5,5p ; python -m src.why_moved impulse-test GLD | sed -n 5,5p ;
  python -m src.why_moved window-grid GLD | tail -14 ; python -m src.why_moved run | grep -A9 "^## gold" ; tail -3 logs/ta_null_GLD.log"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. merge
fa = Path("src/factor_attribution.py"); s = fa.read_text()
old = '    J.setdefault("tests", {})[asset] = rec; (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))'
if old in s: fa.write_text(s.replace(old, '    J.setdefault("tests", {}).setdefault(asset, {}).update(rec); (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))   # merge: T-E/T-F/T-G records survive', 1)); print("  tests(): merges")
else: print("  tests() merge: already/absent")

# ---------------------------------------------------------------- 2. why_moved: parametrise + grid + ceiling null
wm = Path("src/why_moved.py"); s = wm.read_text()
if "def window_grid(" in s: print("  window grid: already")
else:
    # turning_points with explicit rule
    s = s.replace("def turning_points(r: pd.Series):", "def turning_points(r: pd.Series, mult: float = MULT, floor: float = FLOOR):", 1)
    s = s.replace("    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20); thr = np.maximum(FLOOR, MULT * sig)",
                  "    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20); thr = np.maximum(floor, mult * sig)", 1)
    # attr_curve with look-back
    s = s.replace("def attr_curve(r: pd.Series, F: pd.DataFrame, s0, max_k: int = MAX_K):", "def attr_curve(r: pd.Series, F: pd.DataFrame, s0, max_k: int = MAX_K, window: int = WINDOW):", 1)
    s = s.replace("    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename(\"r\")).dropna(); ep = F.loc[s0:][avail].join(r.rename(\"r\")).dropna().iloc[1:max_k + 1]",
                  "    win = F.loc[:s0].iloc[-window - 1:-1][avail].join(r.rename(\"r\")).dropna(); ep = F.loc[s0:][avail].join(r.rename(\"r\")).dropna().iloc[1:max_k + 1]", 1)
    # window_rules with patience / min_k
    s = s.replace("def window_rules(curve, L: int, k_imp: int):", "def window_rules(curve, L: int, k_imp: int, patience: int = PATIENCE, min_k: int = MIN_K):", 1)
    s = s.replace("    if n < MIN_K:\n        out[\"R5_causal\"] = (n, float(sc[n - 1])); return out\n    best, kb, since = -np.inf, MIN_K, 0\n    for k in range(MIN_K, n + 1):",
                  "    if n < min_k:\n        out[\"R5_causal\"] = (n, float(sc[n - 1])); return out\n    best, kb, since = -np.inf, min_k, 0\n    for k in range(min_k, n + 1):", 1)
    s = s.replace("        if since >= PATIENCE: break", "        if since >= patience: break", 1)
    block = '''

# ---------------------------------------------------------------- T-G: the window rule's own variables, swept (founder's rule, 23 Oct)
GRID_PATIENCE = (2, 3, 5, 7, 10, 15, 20, 30)
GRID_MINK = (3, 5, 10)
GRID_WINDOW = (252, 504, 756)
GRID_REVERSAL = ((1.0, 0.05), (1.5, 0.08), (2.0, 0.12))


def _r5_cells(r, F, cells, idx):
    """Median R5 share and share-beating-R1 for every cell; episodes depend on the reversal rule, curves on the look-back; rules are cheap on top."""
    out = {}; cache = {}
    for (mult, floor, window, patience, min_k) in cells:
        key = (mult, floor)
        if key not in cache:
            tps, _, _, px, thr = turning_points(r, mult, floor)
            cache[key] = [(a, b, 1 if ka == "trough" else -1, float(thr[a])) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP]
        eps = cache[key]; ckey = (mult, floor, window)
        if ckey not in cache:
            cache[ckey] = [(attr_curve(r, F, idx[a], max_k=min(b - a, MAX_K), window=window), a, b, d, t) for a, b, d, t in eps if a >= window + 10]
        v5, v1 = [], []
        for cv, a, b, d, t in cache[ckey]:
            if cv is None: continue
            i0, i1, _ = impulse_window(r, idx[a], d, t); wr = window_rules(cv, min(b - a, MAX_K), max(len(r.loc[i0:i1]) - 1, 1), patience, min_k)
            if wr and np.isfinite(wr["R5_causal"][1]): v5.append(wr["R5_causal"][1]); v1.append(wr["R1_full"][1])
        v5, v1 = np.array(v5), np.array(v1)
        out[(mult, floor, window, patience, min_k)] = dict(n=int(len(v5)), r5=float(np.median(v5)) if len(v5) else np.nan, beat=float((v5 > v1).mean()) if len(v5) else np.nan)
    return out


def window_grid(asset, n_shift: int = 10, seed: int = 0):
    """Every cell of the window rule's variables; the best cell judged against the best cell of the same sweep on time-shifted factors."""
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index
    cells = [(m, f, w, p, k) for (m, f) in GRID_REVERSAL for w in GRID_WINDOW for p in GRID_PATIENCE for k in GRID_MINK]
    real = _r5_cells(r, F, cells, idx); df = pd.DataFrame([dict(mult=c[0], floor=c[1], window=c[2], patience=c[3], min_k=c[4], **v) for c, v in real.items()]).dropna(subset=["r5"])
    best = df.loc[df.r5.idxmax()]; rng = np.random.default_rng(seed); mx = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns)
        vals = [v["r5"] for v in _r5_cells(r, Fx, cells, idx).values() if np.isfinite(v["r5"])]
        if vals: mx.append(max(vals))
    mx = np.array(mx); p = float((mx >= best.r5).mean()) if len(mx) else np.nan; reg = real.get((MULT, FLOOR, WINDOW, PATIENCE, MIN_K), {})
    L = [f"# T-G window-rule grid — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {len(df)} cells: reversal rule (mult, floor) × look-back × patience × min window. "
         f"Statistic: median R5 explained share over past episodes. Best cell judged against the best cell of the same sweep on {len(mx)} time-shifted factor series (SPEC_GRID rule 2).*", "",
         f"**Registered cell** (1.5, 8%, 504, patience 5, min 5): median {reg.get('r5', float('nan')):.0%}, beats full leg in {reg.get('beat', float('nan')):.0%} (n {reg.get('n', 0)}).", "",
         f"**Best cell:** mult {best.mult}, floor {best.floor:.0%}, look-back {int(best.window)}, patience {int(best.patience)}, min window {int(best.min_k)} → median **{best.r5:.0%}**, beats full leg in {best.beat:.0%} (n {int(best.n)}); "
         f"best-of-sweep null median {np.median(mx) if len(mx) else float('nan'):.0%}, **p = {p:.2f}** → " + ("survives the sweep" if p < 0.05 else "does not beat the best noise cell"), "",
         "| rank | mult | floor | look-back | patience | min k | median R5 | beats full | n |", "|---|---|---|---|---|---|---|---|---|"]
    for i, (_, q) in enumerate(df.sort_values("r5", ascending=False).head(15).iterrows(), 1):
        L.append(f"| {i} | {q.mult} | {q.floor:.0%} | {int(q.window)} | {int(q.patience)} | {int(q.min_k)} | {q.r5:.0%} | {q.beat:.0%} | {int(q.n)} |")
    L += ["", "By patience (median over the other variables): " + ", ".join(f"{int(pp)}: {df[df.patience == pp].r5.median():.0%}" for pp in GRID_PATIENCE),
          "By look-back: " + ", ".join(f"{int(w)}: {df[df.window == w].r5.median():.0%}" for w in GRID_WINDOW),
          "By reversal rule: " + ", ".join(f"({m}, {f:.0%}): {df[(df.mult == m) & (df.floor == f)].r5.median():.0%}" for m, f in GRID_REVERSAL),
          "", "Reading: the registered 5/5 cell stays the recorded verdict; a surviving best cell is promoted (dated amendment) as the rule the app uses, with its p shown."]
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TG"] = dict(best=dict(mult=float(best.mult), floor=float(best.floor), window=int(best.window), patience=int(best.patience), min_k=int(best.min_k), r5=float(best.r5), beat=float(best.beat), n=int(best.n)),
                                                               null_median=(float(np.median(mx)) if len(mx) else None), p=p, n_cells=int(len(df)), run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"window_grid_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")


def ceiling_null(r, F, s0, L, n_shift: int = 20, seed: int = 0):
    """What the after-the-fact best window (R4) scores on time-shifted factors for the same leg — the noise part of a chosen-after-the-fact share."""
    rng = np.random.default_rng(seed); vals = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns)
        cv = attr_curve(r, Fx, s0, max_k=min(L, MAX_K))
        if cv is None: continue
        sc = cv["score"][:L]; fin = sc[np.isfinite(sc)]
        if len(fin): vals.append(float(np.nanmax(fin)))
    return float(np.median(vals)) if vals else np.nan

'''
    s = s.replace("\n\ndef window_test(asset):", block + "\n\ndef window_test(asset):", 1)
    # run(): use best grid cell if it survived; ceiling null line
    old = "        cv = attr_curve(r, F, s0, max_k=MAX_K); Lnow = len(idx) - 1 - s0_pos\n        wr = window_rules(cv, min(Lnow, MAX_K), max(len(r.loc[i0:i1]) - 1, 1)) if cv is not None else None\n"
    new = '''        cv = attr_curve(r, F, s0, max_k=MAX_K); Lnow = len(idx) - 1 - s0_pos
        wr = window_rules(cv, min(Lnow, MAX_K), max(len(r.loc[i0:i1]) - 1, 1)) if cv is not None else None
        tg = tb_all.get(a, {}).get("TG", {}); wr_best = None
        if wr and tg.get("p") is not None and tg["p"] < 0.05:
            bb = tg["best"]; cvb = attr_curve(r, F, s0, max_k=MAX_K, window=bb["window"])
            wr_best = window_rules(cvb, min(Lnow, MAX_K), max(len(r.loc[i0:i1]) - 1, 1), bb["patience"], bb["min_k"]) if cvb is not None else None
        c_null = ceiling_null(r, F, s0, min(Lnow, MAX_K)) if cv is not None else np.nan
'''
    assert old in s, "run cv anchor"; s = s.replace(old, new, 1)
    old = "                              window_test=tf, r5_rows="
    new = "                              window_test=tf, ceiling_null=(None if not np.isfinite(c_null) else float(c_null)), best_rule=(dict(sessions=int(wr_best['R5_causal'][0]), explained=float(wr_best['R5_causal'][1]), params=tg['best'], p=tg['p']) if wr_best and np.isfinite(wr_best['R5_causal'][1]) else None), r5_rows="
    assert old in s, "run json anchor"; s = s.replace(old, new, 1)
    old = '''                     f"{pc(float(cv['move'][r5[0] - 1]))}, explained {r5[1] if np.isfinite(r5[1]) else float('nan'):.0%} — T-F {vtf}.")'''
    new = '''                     f"{pc(float(cv['move'][r5[0] - 1]))}, explained {r5[1] if np.isfinite(r5[1]) else float('nan'):.0%} — T-F {vtf}. "
                     f"Noise calibration of the ceiling: a time-shifted series reaches {c_null:.0%} by the same after-the-fact choice, so the ceiling's excess over noise is {r4[1] - c_null:+.0%} points."
                     + (f" Best swept rule (patience {tg['best']['patience']}, min {tg['best']['min_k']}, look-back {tg['best']['window']}; p {tg['p']:.2f}): first {wr_best['R5_causal'][0]} sessions, explained {wr_best['R5_causal'][1]:.0%}." if wr_best else ""))'''
    assert old in s, "run wording anchor"; s = s.replace(old, new, 1)
    s = s.replace('    elif cmd == "window-null": window_null(sys.argv[2])', '    elif cmd == "window-null": window_null(sys.argv[2])\n    elif cmd == "window-grid": window_grid(sys.argv[2])', 1)
    wm.write_text(s); print("  why_moved: variables parametrised, T-G grid, ceiling null, best-rule line")

# ---------------------------------------------------------------- 3. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "T-G" in s: print("  prereg T-G: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **T-G (registered 23 Oct, founder's rule — "why are we satisfied with 53%; sweep the variables"):** the window rule's own variables swept —
  patience {2,3,5,7,10,15,20,30} × min window {3,5,10} × look-back {252,504,756} × reversal rule {(1.0, 5%), (1.5, 8%), (2.0, 12%)} = 216 cells;
  statistic = median R5 share over past episodes; the best cell vs the best cell of the same sweep on 10 time-shifted factor series (p < 0.05
  survives) → promoted as the app's rule by dated amendment, the registered 5/5 cell staying the recorded verdict. The after-the-fact ceiling on
  the current leg is reported with its own noise calibration (median R4 on 20 shifted series). **Prior #66:** patience 10–20 wins, median
  share 58–65%, survives the null; the ceiling's excess over noise on gold's current leg ≈ 30 points.
- Nightly: `src/why_moved.py`; app:""", 1)
    s = s.rstrip("\n") + "\n| 2026-10-23 | T-F′ (GLD) | Real median R5 share 53% vs 5% on time-shifted factors (20 shifts; 95th pct 9%) → **PASS**. Gold's current leg: ceiling 61% at 22 sessions, the 5/5 rule stopped at 5 sessions (12%) — patience too short, swept under T-G. | **#65 right** |\n"
    p.write_text(s); print("  prereg: T-G registered, T-F' result")
print("done -- python -m src.why_moved window-test GLD ; python -m src.why_moved impulse-test GLD ; python -m src.why_moved window-grid GLD ; python -m src.why_moved run")
