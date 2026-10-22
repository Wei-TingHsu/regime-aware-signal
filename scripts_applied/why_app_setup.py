"""23 Oct: fixes (causal rule on short episodes; Wikipedia UA), T-F' shifted-factor null for the causal rule, R5-window reasons stored,
records (T-F PASS, #64 wrong, tally 55; T-F' prior #65), and the "Why it moved" paragraph in the app's Context block.
Run from the repo root:  python scripts_applied/why_app_setup.py ; python -m src.why_moved run | grep -A8 "^## gold" ; python -m src.why_moved window-null GLD | sed -n 1,8p ;
                         python -m src.issuer_pool build 2>&1 | tail -14 ; python -m src.context show GLD | sed -n 3,4p"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. why_moved fixes + R5 reasons + T-F'
wm = Path("src/why_moved.py"); s = wm.read_text()
if "def window_null(" in s: print("  why_moved: already")
else:
    old = "    best, kb, since = -np.inf, MIN_K, 0\n    for k in range(MIN_K, n + 1):"
    new = "    if n < MIN_K:\n        out[\"R5_causal\"] = (n, float(sc[n - 1])); return out\n    best, kb, since = -np.inf, MIN_K, 0\n    for k in range(MIN_K, n + 1):"
    assert old in s, "R5 anchor"; s = s.replace(old, new, 1)
    old = "        tf = tb_all.get(a, {}).get(\"TF\", {})\n"
    new = ("        tf = tb_all.get(a, {}).get(\"TF\", {})\n"
           "        r5_attr = attribute(r, F, s0, cv[\"dates\"][wr[\"R5_causal\"][0] - 1]) if wr else None\n")
    assert old in s, "tf anchor"; s = s.replace(old, new, 1)
    old = "                              window_test=tf)"
    new = "                              window_test=tf, r5_rows=(r5_attr[\"rows\"][:4] if r5_attr else None), r5_unexplained=(r5_attr[\"unexplained_share\"] if r5_attr else None))"
    assert old in s, "window_test anchor"; s = s.replace(old, new, 1)
    block = '''

def window_null(asset, n_shift: int = 20, seed: int = 0):
    """T-F' (prereg §4): the causal rule picks the best of several windows, so it scores something on noise. Re-run R5 on every past episode with
    the factor series shifted in time (no real relation to the returns), n_shift times. PASS if the real median R5 share exceeds the median of the
    shifted medians by >= 10 points and the 95th percentile of them."""
    r = returns(asset).dropna(); F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index
    eps = [(a, b, 1 if ka == "trough" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP and a >= WINDOW + 10]
    def r5_median(Fx):
        vals = []
        for a, b, d in eps:
            cv = attr_curve(r, Fx, idx[a], max_k=min(b - a, MAX_K))
            if cv is None: continue
            i0, i1, _ = impulse_window(r, idx[a], d, float(thr[a])); wr = window_rules(cv, min(b - a, MAX_K), max(len(r.loc[i0:i1]) - 1, 1))
            if wr and np.isfinite(wr["R5_causal"][1]): vals.append(wr["R5_causal"][1])
        return float(np.median(vals)) if vals else np.nan, len(vals)
    real, n = r5_median(F); rng = np.random.default_rng(seed); nulls = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns); nulls.append(r5_median(Fx)[0])
    nulls = np.array([v for v in nulls if np.isfinite(v)]); med0, p95 = float(np.median(nulls)), float(np.quantile(nulls, .95))
    verdict = "PASS" if (real - med0 >= 0.10 and real > p95) else "FAIL"
    L = [f"# T-F' causal-rule null — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Real median R5 explained share {real:.0%} over {n} episodes; with time-shifted factors ({len(nulls)} shifts): "
         f"median {med0:.0%}, 95th percentile {p95:.0%}. PASS if real ≥ null median + 10 pts and > 95th pct.*", "", f"**{verdict}** — the rule's score on noise is {med0:.0%}; the real series adds {real - med0:+.0%} points."]
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TFnull"] = dict(real=real, null_median=med0, null_p95=p95, n_shift=int(len(nulls)), verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"window_null_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")

'''
    s = s.replace("\n\ndef selftest():", block + "\n\ndef selftest():", 1)
    s = s.replace('    elif cmd == "window-test": window_test(sys.argv[2])', '    elif cmd == "window-test": window_test(sys.argv[2])\n    elif cmd == "window-null": window_null(sys.argv[2])', 1)
    wm.write_text(s); print("  why_moved: short-episode fix, R5 reasons stored, T-F' window-null")

# ---------------------------------------------------------------- 2. issuer_pool Wikipedia UA
ip = Path("src/issuer_pool.py"); s = ip.read_text()
if "wiki_html" in s: print("  issuer_pool wiki: already")
else:
    old = '    t = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]'
    new = ('    wiki_html = urllib.request.urlopen(urllib.request.Request("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers={"User-Agent": "Mozilla/5.0 regime-aware-signal research"}), timeout=60).read().decode("utf-8", "ignore")\n'
           '    import io; t = pd.read_html(io.StringIO(wiki_html))[0]')
    assert old in s, "wiki anchor"; ip.write_text(s.replace(old, new, 1)); print("  issuer_pool: Wikipedia with a browser header")

# ---------------------------------------------------------------- 3. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "| 2026-10-23 | T-F (GLD) |" in s: print("  prereg T-F record: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **T-F′ (registered 23 Oct after T-F passed, before running):** the causal rule's median share on episodes with time-shifted factor series
  (20 shifts) — PASS if the real share beats the null median by ≥ 10 points and its 95th percentile. **Prior #65:** PASS.
- Nightly: `src/why_moved.py`; app:""", 1)
    s = s.rstrip("\n") + "\n| 2026-10-23 | T-F (GLD) | Causal stop beats the full-leg window in **83%** of 24 episodes → **PASS**; median explained share 53% at a median 7 sessions vs 31% over the full leg (102 sessions); fixed impulse 17%; after-the-fact ceiling 71% at 11 sessions. `docs/window_test_GLD.md` | **#64 wrong** (expected FAIL). Tally 55 |\n"
    p.write_text(s); print("  prereg: T-F result, T-F' registered")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 55" in s: print("  MASTER tally: already")
else:
    s = s.replace("#63 impulse window, all Claude's)", "#63 impulse window, #64 causal window rule, all Claude's)", 1).replace("tally 54 (#40", "tally 55 (#40", 1); m.write_text(s); print("  MASTER: tally 55")
t = Path("docs/TRACK.md"); s = t.read_text()
old = "`src/why_moved.py`, prereg_factor_attribution §4; hooked in daily_run.\n"
if "T-F PASS" in s: print("  TRACK 3.33: already")
elif old in s: t.write_text(s.replace(old, old + "**23 Oct results:** T-A sweep favours 20-session blocks (0.22 at a 3-year window; null pending); T-E fixed-impulse FAIL (#63); "
                               "**T-F causal window rule PASS** — 53% explained at ~7 sessions vs 31% full leg, 83% of episodes (#64 wrong, tally 55); T-F′ shifted-factor null registered (#65). "
                               "App paragraph \"Why it moved\" wired into the Context block the same night.\n", 1)); print("  TRACK 3.33: results noted")
else: print("  TRACK 3.33 anchor not found -- add by hand")

# ---------------------------------------------------------------- 4. app paragraph
c = Path("src/context.py"); s = c.read_text()
if "def why_moved_sentences" in s: print("  context why-moved: already")
else:
    helper = '''
def why_moved_sentences(asset, name, ticker=None):
    """The founder's daily picture (TRACK 3.33): the current leg, how far along a typical leg it is, the rule-found window and its reasons,
    yesterday's reasons, and the pill as today's wind. Reads processed/why_moved.json (nightly)."""
    W = _j(PROC / "why_moved.json"); key = asset if asset in MODEL else ticker
    A = ((W or {}).get("assets") or {}).get(key)
    if not A: return None
    ep, tg, wd, ls, tf = A["episode"], A.get("target"), A.get("windows") or {}, A.get("last_session") or {}, A.get("window_test") or {}
    up = ep["direction"] > 0; S = []
    S.append(f"{name} has been <b>{'rising' if up else 'falling'} since {ep['start']}</b> — {ep['sessions']} sessions, {_pct(ep['move'])} so far, furthest point "
             f"{_pct(ep['extreme_so_far']['move'])} on {ep['extreme_so_far']['date']}; a move of {ep['threshold_now']:.1%} against the trend would end this leg "
             f"(the reversal rule: 1.5 × the asset's own monthly volatility, floor 8%) {tag('measured')}.")
    if tg:
        kind = "rises" if up else "falls"; sgn = 1 if up else -1
        if tg.get("share_of_typical") is not None and tg["share_of_typical"] < 1:
            S.append(f"Past {kind} of this kind ran a median {_pct(sgn * tg['med_size'])} from their start over {tg['med_length']:.0f} sessions (n {tg['n']}); this one is at "
                     f"{tg['share_of_typical']:.0%} of that, so the typical level is <b>{_pct(tg['target_from_now'])} from here</b> (middle half of past legs: {_pct(tg['band_from_now'][0])} to "
                     f"{_pct(tg['band_from_now'][1])}) {tag('measured')} — a base rate of past legs, not a forecast; the reason-conditioned version {tag('registered, not run')}.")
        else:
            S.append(f"Past {kind} of this kind ran a median {_pct(sgn * tg['med_size'])} (n {tg['n']}); this one is already larger than {tg.get('pct_rank', 0):.0%} of them — the base rate gives no further level {tag('measured')}.")
    r5 = wd.get("R5_causal"); rows = A.get("r5_rows") or []
    if r5 and r5.get("explained") is not None:
        top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in rows[:3]) or "—"
        v = tf.get("verdict", "not run"); extra = f" (this rule beat the full-leg window in {tf['share']:.0%} of past legs)" if tf.get("share") is not None else ""
        S.append(f"<b>Why it moved.</b> Over the window where the named reasons explain most on a forward-walking rule — the first {r5['sessions']} sessions to {r5['end']}, "
                 f"{_pct(r5['move'])} — they account for <b>{r5['explained']:.0%}</b> of the move: {top}; the rest is unexplained by rates, the dollar, oil, volatility, geopolitical risk, "
                 f"liquidity or the macro state {tag('tested: ' + v)}{extra}. Each reason's share is its sensitivity (from the two years before the leg) × how far that series moved.")
    la = ls.get("attribution")
    if la:
        top = ", ".join(f"{d['label']} {d['contrib']:+.2%}" for d in la["rows"][:3])
        S.append(f"Last session {ls['date']}: {_pct(ls['ret'])} — {top}; unexplained {la['resid']:+.2%} {tag('measured')}.")
    S.append("Today's wind is the engine's two-session call — the pill above — scored separately on the track record at the top of the page.")
    return " ".join(S)

'''
    s = s.replace("\n# ---------------------------------------------------------------- the block\n", helper + "\n# ---------------------------------------------------------------- the block\n", 1)
    old = "    # 1b. today's condition (H0)\n"
    new = "    # 1a. why it moved (TRACK 3.33)\n    wm = why_moved_sentences(asset, name, ticker=ticker)\n    if wm: P.append((\"Why it moved, and where this leg stands\", wm))\n\n    # 1b. today's condition (H0)\n"
    assert old in s, "context anchor"; s = s.replace(old, new, 1)
    c.write_text(s); print("  context: 'Why it moved' paragraph")
print("done")
