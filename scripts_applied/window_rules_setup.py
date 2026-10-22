"""23 Oct: (1) explained-share curve per episode; window rules R1 full / R2 impulse / R3 half / R4 ceiling (after the fact) / R5 causal stop;
T-F registered + runnable; run() shows ceiling and causal windows; (2) issuer pool reads BEA contributions from FRED (no BEA key);
(3) records: T-A sweep, T-E FAIL (#63 wrong, tally 54), T-F prior #64.
Run from the repo root:  python scripts_applied/window_rules_setup.py ; python -m src.why_moved window-test GLD | sed -n 1,12p ; python -m src.why_moved run | grep -A6 "^## gold" ; python -m src.issuer_pool build 2>&1 | tail -14"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. why_moved: curve + rules + T-F
wm = Path("src/why_moved.py"); s = wm.read_text()
if "def attr_curve(" in s: print("  why_moved window rules: already")
else:
    block = '''

# ---------------------------------------------------------------- explained-share curve and window rules (founder, 23 Oct)
PATIENCE, MIN_K, MAX_K = 5, 5, 120


def attr_curve(r: pd.Series, F: pd.DataFrame, s0, max_k: int = MAX_K):
    """For windows of 1..max_k sessions after the turning point s0: cumulative move, the reasons' explained part (pre-episode sensitivities,
    drift excluded), residual, and the explained share 1 - |resid|/|move| (NaN while the move is under 1%)."""
    avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename("r")).dropna(); ep = F.loc[s0:][avail].join(r.rename("r")).dropna().iloc[1:max_k + 1]
    if len(win) < 250 or len(ep) < 3: return None
    b = joint_fit(win.r.to_numpy(), win[avail].to_numpy())
    cF = ep[avail].cumsum().to_numpy(); cr = ep.r.cumsum().to_numpy(); explained = cF @ b; resid = cr - explained
    score = 1 - np.abs(resid) / np.maximum(np.abs(cr), 1e-9); score[np.abs(cr) < 0.01] = np.nan
    return dict(k=np.arange(1, len(ep) + 1), move=cr, explained=explained, score=score, dates=ep.index)


def window_rules(curve, L: int, k_imp: int):
    """Scores under each rule for an episode of L sessions. R4 is chosen after the fact (a ceiling); R5 walks forward and stops when the
    score has not improved for PATIENCE sessions (causal, usable live)."""
    sc = curve["score"][:L]; n = len(sc)
    if n == 0: return None
    out = {"R1_full": (n, float(sc[n - 1])), "R2_impulse": (min(k_imp, n), float(sc[min(k_imp, n) - 1]) if k_imp >= 1 else np.nan), "R3_half": (max(n // 2, 1), float(sc[max(n // 2, 1) - 1]))}
    fin = np.where(np.isfinite(sc))[0]
    out["R4_ceiling"] = (int(fin[np.nanargmax(sc[fin])]) + 1, float(np.nanmax(sc[fin]))) if len(fin) else (n, np.nan)
    best, kb, since = -np.inf, MIN_K, 0
    for k in range(MIN_K, n + 1):
        v = sc[k - 1]
        if np.isfinite(v) and v > best: best, kb, since = v, k, 0
        else: since += 1
        if since >= PATIENCE: break
    out["R5_causal"] = (kb, float(best) if np.isfinite(best) else np.nan)
    return out


def window_test(asset):
    """T-F (prereg_factor_attribution §4): does the causal window rule (R5) explain more than the full episode (R1) on past episodes?
    PASS if R5 > R1 in >= 60% of episodes (n >= 15). R4 is reported as the after-the-fact ceiling, never as a result."""
    r = returns(asset).dropna(); F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index; rows = []
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        if b - a < MIN_EP or a < WINDOW + 10: continue
        direction = 1 if ka == "trough" else -1; s0 = idx[a]; L = b - a
        cv = attr_curve(r, F, s0, max_k=min(L, MAX_K))
        if cv is None: continue
        i0, i1, _ = impulse_window(r, s0, direction, float(thr[a])); k_imp = len(r.loc[i0:i1]) - 1
        wr = window_rules(cv, min(L, MAX_K), k_imp)
        if wr is None: continue
        rows.append(dict(start=s0.strftime("%Y-%m-%d"), L=int(L), **{f"{k}_k": v[0] for k, v in wr.items()}, **{f"{k}_s": v[1] for k, v in wr.items()}))
    df = pd.DataFrame(rows); n = len(df)
    share = float((df.R5_causal_s > df.R1_full_s).mean()) if n else np.nan
    verdict = "INCONCLUSIVE" if n < 15 else ("PASS" if share >= 0.6 else "FAIL")
    med = {k: float(df[f"{k}_s"].median()) for k in ("R1_full", "R2_impulse", "R3_half", "R4_ceiling", "R5_causal")} if n else {}
    L_ = [f"# T-F window rules — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {n} past episodes. Explained share = 1 − |residual| / |move|, reasons only (drift excluded), "
          f"pre-episode sensitivities. R4 is chosen after seeing every window — an in-sample ceiling, shown so the gap to the usable rules is visible.*", "",
          (f"**R5 (causal stop) beats R1 (full episode) in {share:.0%} of episodes → {verdict}**" if n >= 15 else f"**{verdict}** (n {n} < 15)"), "",
          "| rule | median explained share | median window (sessions) |", "|---|---|---|"]
    for k, lab in (("R1_full", "R1 full episode"), ("R2_impulse", "R2 impulse (quarter-threshold)"), ("R3_half", "R3 first half"), ("R5_causal", "R5 causal stop (patience 5)"), ("R4_ceiling", "R4 ceiling — after the fact, not a result")):
        if n: L_.append(f"| {lab} | {med[k]:.0%} | {df[f'{k}_k'].median():.0f} |")
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TF"] = dict(n=n, share=share, verdict=verdict, medians=med, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    out = DOCS / f"window_test_{asset}.md"; out.write_text("\\n".join(L_) + "\\n"); print("\\n".join(L_)); print(f"-> {out}")

'''
    s = s.replace("\n\ndef run():", block + "\n\ndef run():", 1)
    # run(): windows for the current episode
    old = "        TB = tb_all.get(a, {}).get(\"TB\", {})\n"
    new = '''        TB = tb_all.get(a, {}).get("TB", {})
        cv = attr_curve(r, F, s0, max_k=MAX_K); Lnow = len(idx) - 1 - s0_pos
        wr = window_rules(cv, min(Lnow, MAX_K), max(len(r.loc[i0:i1]) - 1, 1)) if cv is not None else None
        tf = tb_all.get(a, {}).get("TF", {})
'''
    assert old in s, "run TB anchor"; s = s.replace(old, new, 1)
    old = "                              stable_factors=[f for f, v in TB.items() if v.get(\"stable\")], n_past_episodes=len(eps))"
    new = '''                              stable_factors=[f for f, v in TB.items() if v.get("stable")], n_past_episodes=len(eps),
                              windows=({k: dict(sessions=int(v[0]), explained=(None if not np.isfinite(v[1]) else float(v[1])), move=float(cv["move"][v[0] - 1]), end=cv["dates"][v[0] - 1].strftime("%Y-%m-%d")) for k, v in wr.items()} if wr else None),
                              window_test=tf)'''
    assert old in s, "run json anchor"; s = s.replace(old, new, 1)
    old = '''        if ep_attr:
            top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in ep_attr["rows"][:4])'''
    new = '''        if wr:
            r4, r5 = wr["R4_ceiling"], wr["R5_causal"]; vtf = tf.get("verdict", "not run")
            L.append(f"- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first {r4[0]} sessions to {cv['dates'][r4[0] - 1].date()}, "
                     f"{pc(float(cv['move'][r4[0] - 1]))}, explained {r4[1]:.0%}. Causal rule (stop after {PATIENCE} sessions without improvement): first {r5[0]} sessions, "
                     f"{pc(float(cv['move'][r5[0] - 1]))}, explained {r5[1] if np.isfinite(r5[1]) else float('nan'):.0%} — T-F {vtf}.")
        if ep_attr:
            top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in ep_attr["rows"][:4])'''
    assert old in s, "run wording anchor"; s = s.replace(old, new, 1)
    s = s.replace('    impulse_test(sys.argv[2]) if cmd == "impulse-test" else {"selftest": selftest, "run": run}[cmd]()',
                  '    if cmd == "impulse-test": impulse_test(sys.argv[2])\n    elif cmd == "window-test": window_test(sys.argv[2])\n    else: {"selftest": selftest, "run": run}[cmd]()', 1)
    wm.write_text(s); print("  why_moved: curve, window rules, T-F, run() lines")

# ---------------------------------------------------------------- 2. issuer pool via FRED
ip = Path("src/issuer_pool.py"); s = ip.read_text()
if "FRED_IDS" in s: print("  issuer_pool FRED: already")
else:
    s = s.replace("def bea_contributions(year: int) -> tuple[str, pd.DataFrame]:", '''FRED_IDS = {4: "DDURRY2Q224SBEA", 5: "DNDGRY2Q224SBEA", 6: "DSERRY2Q224SBEA", 10: "A009RY2Q224SBEA", 11: "Y033RY2Q224SBEA", 12: "Y001RY2Q224SBEA",
            13: "A011RY2Q224SBEA", 14: "A014RY2Q224SBEA", 16: "A020RY2Q224SBEA", 24: "A824RY2Q224SBEA", 25: "A825RY2Q224SBEA", 26: "A829RY2Q224SBEA"}


def fred_contributions() -> tuple[str, pd.DataFrame]:
    """NIPA 1.1.2 contributions to percent change in real GDP, from FRED (same BEA numbers; FRED key already on file)."""
    from fredapi import Fred
    key = os.environ.get("FRED_API_KEY") or _env("FRED_API_KEY")
    if not key: raise RuntimeError("FRED_API_KEY missing")
    fred = Fred(api_key=key); rows = []; missing = []
    for ln, sid in FRED_IDS.items():
        try:
            ser = fred.get_series(sid).dropna(); rows.append(dict(LineNumber=ln, LineDescription=LINE_MAP[ln][0], TimePeriod=f"{ser.index[-1].year}Q{(ser.index[-1].month - 1) // 3 + 1}", DataValue=float(ser.iloc[-1])))
        except Exception as e:
            missing.append(f"{sid} ({type(e).__name__})")
    if not rows: raise RuntimeError("FRED returned nothing: " + "; ".join(missing))
    if missing: print(f"  FRED series not found: {', '.join(missing)}")
    df = pd.DataFrame(rows); q = df.TimePeriod.mode().iloc[0]
    return q, df[df.TimePeriod == q].set_index("LineNumber")


def bea_contributions(year: int) -> tuple[str, pd.DataFrame]:''', 1)
    old = "    try:\n        q, d = bea_contributions(year)\n    except Exception as e:\n        print(f\"  BEA {year}: {e}\")\n        q, d = bea_contributions(year - 1); print(f\"  using {q}\")\n"
    new = "    try:\n        q, d = fred_contributions(); print(f\"  contributions from FRED, latest quarter {q}\")\n    except Exception as e:\n        print(f\"  FRED route failed: {e}; trying BEA\")\n        q, d = bea_contributions(year)\n"
    assert old in s, "issuer_pool build anchor"; s = s.replace(old, new, 1)
    ip.write_text(s); print("  issuer_pool: FRED route first")

# ---------------------------------------------------------------- 3. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "| 2026-10-23 | T-E |" in s: print("  prereg records: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **Window rules (founder, 23 Oct: "adjust the time frame so the explained share is as high as possible while the trend holds"):** per episode the
  explained-share curve over every window length; R1 full, R2 impulse, R3 first half, R5 causal stop (patience 5 sessions, usable live), and
  R4 the after-the-fact ceiling, shown but never quoted. **T-F:** R5 beats R1 in ≥ 60% of past episodes (n ≥ 15) → PASS. **Prior #64:** FAIL
  (R5 ≈ R1 within noise; the ceiling's gap over them is the overfitting margin).
- Nightly: `src/why_moved.py`; app:""", 1)
    s = s.rstrip("\n") + """
| 2026-10-23 | T-A sweep (GLD) | 30 cells: blocks 2–3 negative, 5 ≈ 0.05, 15–20 ≈ 0.18, best 756/20 = 0.224 (above the bar; best-of-sweep null pending, background run). Explanatory power rises with block length — day-to-day noise swamps short windows. | sweep, no prior |
| 2026-10-23 | T-E (GLD) | Impulse better explained than the full leg in **46%** of 24 episodes → **FAIL**; median unexplained impulse 81% vs full 63%; current impulse 25 Aug → 1 Sep, 5 sessions, −7.3%, 94% unexplained. | **#63 wrong** (expected PASS for GLD). Tally 54 |
"""
    p.write_text(s); print("  prereg: window rules, T-F, T-A sweep + T-E results")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 54" in s: print("  MASTER tally: already")
else:
    s = s.replace("#58–#59 factor attribution R² and sign stability, all Claude's)", "#58–#59 factor attribution R² and sign stability, #63 impulse window, all Claude's)", 1).replace("tally 53 (#40", "tally 54 (#40", 1)
    m.write_text(s); print("  MASTER: tally 54")
print("done -- python -m src.why_moved window-test GLD ; python -m src.why_moved run")
