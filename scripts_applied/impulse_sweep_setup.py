"""23 Oct: (1) T-A as a sweep over block length x window with a max-statistic null; (2) impulse windows + T-E; (3) why_moved: impulse first,
over-extended wording, tests for every asset, tech names; (4) selftest expectation fixed; (5) .env tolerant parse.
Run from the repo root:  python scripts_applied/impulse_sweep_setup.py ; python -m src.why_moved selftest ; python -m src.factor_attribution tests GLD --sweep ;
                         python -m src.why_moved impulse-test GLD ; python -m src.why_moved run | sed -n 1,30p"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. T-A sweep
fa = Path("src/factor_attribution.py"); s = fa.read_text()
if "def _ta(" in s: print("  T-A sweep: already")
else:
    old = s[s.index("def tests(asset):"):s.index("def selftest():")]
    new = '''BLOCKS_GRID = (1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60)
WINDOWS_GRID = (252, 504, 756)


def _ta(X, y, window, block):
    """Median out-of-sample R² of the joint fit: betas from the prior `window` sessions, scored on each next `block` sessions."""
    r2s = []; i = window
    while i + block <= len(y):
        Xw, yw = X[i - window:i], y[i - window:i]; bj = joint_fit(yw, Xw)
        Xb, yb = X[i:i + block], y[i:i + block]; pred = (Xb - Xw.mean(0)) @ bj + yw.mean()
        ss = ((yb - yb.mean()) ** 2).sum() if block > 1 else np.nan
        r2s.append(1 - ((yb - pred) ** 2).sum() / ss if (block > 1 and ss > 0) else np.nan); i += block
    r2s = np.array(r2s); return float(np.nanmedian(r2s)) if np.isfinite(r2s).any() else np.nan, int(np.isfinite(r2s).sum())


def tests(asset, sweep=False, n_null=0, seed=0):
    """T-A (registered cell: window 504, block 20) and T-B. With --sweep: every (window, block) cell of the grid, the curve, and the best cell
    judged against the best cell of the same sweep on shifted returns (max-statistic null) when n_null > 0. SPEC_GRID rule 2."""
    r = returns(asset); F = factors(r.index); avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    D = F[avail].join(r.rename("r")).dropna(); D = D[D.index >= "2006-01-01"]; X, y = D[avail].to_numpy(), D.r.to_numpy()
    med, nb = _ta(X, y, WINDOW, BLOCK); bar = 0.20 if asset == "GLD" else 0.10
    TA = dict(median_r2=med, blocks=nb, verdict="PASS" if med >= bar else "FAIL", window=WINDOW, block=BLOCK)
    signs = {c: [] for c in avail}; i = WINDOW
    while i + BLOCK <= len(D):
        bj = joint_fit(y[i - WINDOW:i], X[i - WINDOW:i])
        for c, b in zip(avail, bj): signs[c].append(np.sign(b))
        i += STEP
    TB = {}
    for c in avail:
        sg = np.array(signs[c]); sg = sg[sg != 0]; share = float(max((sg > 0).mean(), (sg < 0).mean())) if len(sg) else np.nan
        TB[c] = dict(share=share, stable=bool(share >= 0.7), windows=int(len(sg)))
    rec = {"TA": TA, "TB": TB, "run": datetime.now().strftime("%Y-%m-%d %H:%M")}
    L = [f"# Factor attribution — tests for {asset}", "", f"*{rec['run']}. T-A registered cell: window {WINDOW}, block {BLOCK}, bar {bar:.2f}. T-B: sign of each beta across rolling windows (step {STEP}); stable if ≥ 70%.*", "",
         f"**T-A (registered cell):** median out-of-sample R² **{med:.3f}** over {nb} blocks → **{TA['verdict']}**", "", "| factor | windows | share with the majority sign | T-B |", "|---|---|---|---|"]
    for c, v in TB.items(): L.append(f"| {LABEL[c]} | {v['windows']} | {v['share']:.0%} | {'stable' if v['stable'] else 'UNSTABLE — not quotable'} |")
    if sweep:
        cells = []
        for w in WINDOWS_GRID:
            for b in BLOCKS_GRID:
                m_, n_ = _ta(X, y, w, b); cells.append(dict(window=w, block=b, median_r2=m_, blocks=n_))
        cdf = pd.DataFrame(cells).dropna(subset=["median_r2"]); best = cdf.loc[cdf.median_r2.idxmax()]
        L += ["", f"## T-A sweep — {len(cdf)} cells (window × block), SPEC_GRID family 2.10", "", "| window | " + " | ".join(f"b{b}" for b in BLOCKS_GRID) + " |", "|---|" + "---|" * len(BLOCKS_GRID)]
        for w in WINDOWS_GRID:
            row = cdf[cdf.window == w].set_index("block").median_r2
            L.append(f"| {w} | " + " | ".join(f"{row.get(b, float('nan')):.3f}" for b in BLOCKS_GRID) + " |")
        line = f"Best cell: window {int(best.window)}, block {int(best.block)}, median R² {best.median_r2:.3f}"
        if n_null > 0:
            rng = np.random.default_rng(seed); mx = []
            for _ in range(n_null):
                ys = np.roll(y, int(rng.integers(120, len(y) - 120)))
                vals = [v for v in (_ta(X, ys, w, b)[0] for w in WINDOWS_GRID for b in BLOCKS_GRID) if np.isfinite(v)]
                if vals: mx.append(max(vals))
            mx = np.array(mx); p = float((mx >= best.median_r2).mean()) if len(mx) else np.nan
            line += f"; best-of-sweep null ({len(mx)} shifted draws): median best {np.median(mx):.3f}, p = {p:.3f} → " + ("survives the sweep" if p < 0.05 else "does not beat the best noise cell")
            rec["TA_sweep_null"] = dict(n=int(len(mx)), null_best_median=float(np.median(mx)), p=p)
        rec["TA_sweep"] = dict(best=dict(window=int(best.window), block=int(best.block), median_r2=float(best.median_r2)), cells=cells)
        L += ["", line, "", "Reading: a block of 1 has no R² (one point); short blocks are noisier per block but closer to the founder's 'purest window' idea. "
              "The registered verdict is the 504/20 cell; the sweep is the alternatives track and a survivor is promoted to its own forward test, never adopted in place."]
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {})[asset] = rec; (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    out = DOCS / "factor_attribution_tests.md"; prev = out.read_text() if out.exists() else ""
    out.write_text((prev.rstrip("\\n") + "\\n\\n" if prev else "") + "\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")


def impulse_window(r: pd.Series, s0, direction: int, thr: float, max_len: int = 40):
    """The purest stretch of an episode: from the turning point s0 while the pullback from the running extreme (in the episode's direction)
    stays under thr/4; ends at that extreme. Dynamic by construction (founder, 23 Oct)."""
    seg = r.loc[s0:].iloc[1:max_len + 1]
    if seg.empty: return s0, s0, 0.0
    c = seg.cumsum().to_numpy(); ext = 0
    for i in range(len(c)):
        if direction * c[i] >= direction * c[ext]: ext = i
        elif direction * (c[ext] - c[i]) >= thr / 4: break
    return s0, seg.index[ext], float(c[ext])


'''
    s = s.replace(old, new, 1)
    s = s.replace('    t = sub.add_parser("tests"); t.add_argument("asset")', '    t = sub.add_parser("tests"); t.add_argument("asset"); t.add_argument("--sweep", action="store_true"); t.add_argument("--null", type=int, default=0)', 1)
    s = s.replace("    else: tests(a.asset)", "    else: tests(a.asset, sweep=a.sweep, n_null=a.null)", 1)
    fa.write_text(s); print("  T-A sweep + impulse_window: added")

# ---------------------------------------------------------------- 2. why_moved
wm = Path("src/why_moved.py"); s = wm.read_text()
if "impulse_window" in s: print("  why_moved impulse: already")
else:
    s = s.replace("from src.factor_attribution import factors, returns, joint_fit, ORDER_DEFAULT, LABEL, WINDOW",
                  "from src.factor_attribution import factors, returns, joint_fit, ORDER_DEFAULT, LABEL, WINDOW, impulse_window, tests as fa_tests", 1)
    s = s.replace('ASSETS = ["SPY", "TLT", "GLD", "SLV", "UUP", "USO"]', 'ASSETS = ["SPY", "TLT", "GLD", "SLV", "UUP", "USO", "NVDA", "META"]   # the five markets, silver, two tech names as the founder asked', 1)
    s = s.replace('NAME = {"SPY": "US equities", "TLT": "long Treasuries", "GLD": "gold", "SLV": "silver", "UUP": "the dollar", "USO": "oil"}',
                  'NAME = {"SPY": "US equities", "TLT": "long Treasuries", "GLD": "gold", "SLV": "silver", "UUP": "the dollar", "USO": "oil", "NVDA": "Nvidia", "META": "Meta"}', 1)
    # episode attribution excludes the turning-point session itself
    s = s.replace("    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename(\"r\")).dropna(); ep = F.loc[s0:s1][avail].join(r.rename(\"r\")).dropna()",
                  "    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename(\"r\")).dropna(); ep = F.loc[s0:s1][avail].join(r.rename(\"r\")).dropna()\n    if s1 != s0: ep = ep.iloc[1:]   # the move starts after the turning point", 1)
    # tests for assets without a record; impulse attribution; wording
    old = "        ep_attr = attribute(r, F, s0, s1); day_attr = attribute(r, F, s1, s1)\n        TB = tb_all.get(a, {}).get(\"TB\", {})\n"
    new = '''        if a not in tb_all:
            try: fa_tests(a); tb_all = json.loads((PROC / "factor_attribution.json").read_text()).get("tests", {})
            except Exception as e: print(f"  {a}: tests failed ({type(e).__name__})")
        ep_attr = attribute(r, F, s0, s1); day_attr = attribute(r, F, s1, s1)
        i0, i1, imp_move = impulse_window(r, s0, direction, float(thr[s0_pos])); imp_attr = attribute(r, F, i0, i1) if i1 != i0 else None
        TB = tb_all.get(a, {}).get("TB", {})
'''
    assert old in s, "why_moved attr anchor"; s = s.replace(old, new, 1)
    s = s.replace("                              target=tgt, attribution=ep_attr, last_session=",
                  "                              target=tgt, attribution=ep_attr, impulse=dict(end=i1.strftime(\"%Y-%m-%d\"), sessions=int(len(r.loc[i0:i1]) - 1), move=imp_move, attribution=imp_attr), last_session=", 1)
    old = '''              (f"- Typical {'rise' if direction > 0 else 'fall'} of this kind for {NAME.get(a, a)}: {pc(direction * tgt['med_size'])} from the start [{pc(direction * tgt['q25'])}, {pc(direction * tgt['q75'])}], "
               f"median {tgt['med_length']:.0f} sessions, n {tgt['n']} — this one is at {tgt['share_of_typical']:.0%} of the typical size; from here that is {pc(tgt['target_from_now'])} "
               f"(band {pc(tgt['band_from_now'][0])} to {pc(tgt['band_from_now'][1])}). Base rate, UNTESTED as a conditional target." if tgt else "- Fewer than 5 past episodes of this kind: no target."),
              ]'''
    new = '''              (f"- Typical {'rise' if direction > 0 else 'fall'} of this kind for {NAME.get(a, a)}: {pc(direction * tgt['med_size'])} from the start (middle half of past episodes {pc(direction * tgt['q25'])} to {pc(direction * tgt['q75'])}), "
               f"median {tgt['med_length']:.0f} sessions, n {tgt['n']} — this one is at {tgt['share_of_typical']:.0%} of the typical size; "
               + (f"the typical level is {pc(tgt['target_from_now'])} from here (band {pc(tgt['band_from_now'][0])} to {pc(tgt['band_from_now'][1])})." if tgt['share_of_typical'] < 1
                  else f"it is already beyond the typical size — larger than {tgt['pct_rank']:.0%} of past episodes of this kind; the base rate gives no further level.")
               + " Base rate, UNTESTED as a conditional target." if tgt else "- Fewer than 5 past episodes of this kind: no target."),
              ]
        if imp_attr:
            top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in imp_attr["rows"][:3])
            L.append(f"- **The impulse** (purest stretch, {s0.date()} → {i1.date()}, {len(r.loc[i0:i1]) - 1} sessions, {pc(imp_move)}): {top}; unexplained {imp_attr['unexplained_share']:+.0%}.")'''
    assert old in s, "why_moved wording anchor"; s = s.replace(old, new, 1)
    s = s.replace("                       share_of_typical=float(abs(move) / q50) if q50 > 0 else None, status=",
                  "                       share_of_typical=float(abs(move) / q50) if q50 > 0 else None, pct_rank=float((sizes <= abs(move)).mean()), status=", 1)
    # T-E impulse test
    old = "def selftest():"
    new = '''def impulse_test(asset):
    """T-E (prereg_factor_attribution §4): is the impulse window better explained than the whole episode? Past episodes with >= 5 sessions;
    unexplained share |resid/actual| at the impulse vs the full episode, same sensitivities. PASS if the impulse is lower in >= 60% of episodes (n >= 15)."""
    r = returns(asset).dropna(); F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index; rows = []
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        if b - a < MIN_EP or a < WINDOW + 10: continue
        direction = 1 if ka == "trough" else -1; s0, s1 = idx[a], idx[b]
        i0, i1, imp_move = impulse_window(r, s0, direction, float(thr[a])); full = attribute(r, F, s0, s1); imp = attribute(r, F, i0, i1) if i1 != i0 else None
        if not full or not imp: continue
        rows.append(dict(start=s0.strftime("%Y-%m-%d"), end=s1.strftime("%Y-%m-%d"), direction=direction, full_move=full["actual"], imp_sessions=int(len(r.loc[i0:i1]) - 1), imp_move=imp["actual"],
                         full_unexpl=abs(full["unexplained_share"]), imp_unexpl=abs(imp["unexplained_share"])))
    df = pd.DataFrame(rows); n = len(df)
    if n < 15: verdict, share = "INCONCLUSIVE", float("nan")
    else: share = float((df.imp_unexpl < df.full_unexpl).mean()); verdict = "PASS" if share >= 0.6 else "FAIL"
    L = [f"# T-E impulse vs full episode — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {n} past episodes. Unexplained share = |residual / actual| with the same pre-episode sensitivities. "
         f"PASS if the impulse's share is lower in ≥ 60% of episodes.*", "", f"**Impulse better in {share:.0%} of episodes → {verdict}**" if n >= 15 else f"**{verdict}** (n {n} < 15)", "",
         f"Median unexplained share: impulse {df.imp_unexpl.median():.0%} vs full {df.full_unexpl.median():.0%}; median impulse length {df.imp_sessions.median():.0f} sessions, median impulse move {np.expm1(df.imp_move.abs().median()):.1%} of a full move {np.expm1(df.full_move.abs().median()):.1%}." if n else "",
         "", "| start | end | dir | full move | impulse sessions | impulse move | unexplained full | unexplained impulse |", "|---|---|---|---|---|---|---|---|"]
    for _, q in df.tail(25).iterrows():
        L.append(f"| {q.start} | {q.end} | {'up' if q.direction > 0 else 'down'} | {np.expm1(q.full_move):+.1%} | {q.imp_sessions} | {np.expm1(q.imp_move):+.1%} | {q.full_unexpl:.0%} | {q.imp_unexpl:.0%} |")
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TE"] = dict(n=n, share=share, verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M")); (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    out = DOCS / f"impulse_test_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")


def selftest():'''
    s = s.replace(old, new, 1)
    s = s.replace('    kinds = [k for _, k in tps]; assert kinds[:3] == ["peak", "trough", "peak"], kinds; print("  T1 peak/trough sequence: PASS")',
                  '    kinds = [k for _, k in tps]; assert kinds[:4] == ["trough", "peak", "trough", "peak"], kinds; print("  T1 trough-at-start, peak, trough, peak: PASS")', 1)
    s = s.replace("    assert tps[0][0] == 100 and tps[1][0] == 200, tps[:2]; print(\"  T2 turning points at the true extremes: PASS\")",
                  "    assert [p for p, _ in tps[:4]] == [0, 100, 200, 300], tps[:4]; print(\"  T2 turning points at the true extremes: PASS\")", 1)
    s = s.replace("    eps = past_episodes(tps, px); assert eps[0][\"direction\"] == -1 and abs(eps[0][\"size\"] + 0.30) < 1e-9; print(\"  T4 episode sizes: PASS\")",
                  "    eps = past_episodes(tps, px); assert eps[1][\"direction\"] == -1 and abs(eps[1][\"size\"] + 0.30) < 1e-9; print(\"  T4 episode sizes: PASS\")\n"
                  "    i0, i1, mv = impulse_window(r, idx[100], -1, 0.08); assert abs(mv + 0.12) < 1e-9 and i1 == idx[140], (i1, mv); print(\"  T5 impulse window runs to the extreme within max_len (40 sessions x -0.3%): PASS\")", 1)
    s = s.replace('    {"selftest": selftest, "run": run}[sys.argv[1] if len(sys.argv) > 1 else "run"]()',
                  '    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"\n    impulse_test(sys.argv[2]) if cmd == "impulse-test" else {"selftest": selftest, "run": run}[cmd]()', 1)
    wm.write_text(s); print("  why_moved: impulse first, T-E, wording, tests for all assets, NVDA/META")

# ---------------------------------------------------------------- 3. .env tolerant
ip = Path("src/issuer_pool.py"); s = ip.read_text()
if "export " in s and "names present" in s: print("  issuer_pool .env: already")
else:
    old = s[s.index("def _env(name):"):s.index("def universe()")]
    new = '''def _env(name):
    try:
        for ln in Path(".env").read_text().splitlines():
            ln = ln.strip().removeprefix("export ").strip()
            if "=" in ln and ln.split("=", 1)[0].strip() == name: return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""


def _env_names():
    try: return sorted({ln.strip().removeprefix("export ").split("=", 1)[0].strip() for ln in Path(".env").read_text().splitlines() if "=" in ln and not ln.strip().startswith("#")})
    except Exception: return []


'''
    s = s.replace(old, new, 1)
    s = s.replace('raise RuntimeError("no BEA key found in .env (tried BEA_API_KEY, BEA_KEY, BEA_USERID, BEA_USER_ID, BEAKEY)")',
                  'raise RuntimeError(f"no BEA key under BEA_API_KEY/BEA_KEY/BEA_USERID/BEA_USER_ID/BEAKEY; names present in .env: {_env_names()}")', 1)
    ip.write_text(s); print("  issuer_pool .env: tolerant parse, names listed")

# ---------------------------------------------------------------- 4. prereg T-E + sweep note
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "T-E" in s: print("  prereg T-E: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **Impulse window (founder, 23 Oct):** the purest stretch of an episode — from the turning point while the pullback from the running extreme
  stays under a quarter of the reversal threshold; attributed first, the full episode second. **T-E:** the impulse's unexplained share is lower
  than the full episode's in ≥ 60% of past episodes (n ≥ 15) → PASS. **Prior #63:** PASS for GLD, SLV, USO; FAIL for SPY, TLT, UUP.
- **Sweep rule (founder, 23 Oct):** every fixed number in a test is a variable; when the registered cell fails, the sweep runs (T-A: block
  1–60 × window 252/504/756), the curve is published, and the best cell is judged against the best cell of the same sweep on shifted returns.
  A survivor is promoted to a forward test; the registered verdict stands.
- Assets: the five markets, silver, and single names (NVDA, META first) through the same machinery; the unexplained share says how much a
  macro model can carry for a stock.
- Nightly: `src/why_moved.py`; app:""", 1)
    p.write_text(s); print("  prereg: impulse, T-E, sweep rule, assets")
print("done -- python -m src.why_moved selftest ; python -m src.factor_attribution tests GLD --sweep ; python -m src.why_moved impulse-test GLD")
