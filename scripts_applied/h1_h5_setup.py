"""19 Oct: H1 (Fed days, split by 2-yr move), H3 (dollar ±3%/5s), H4 (2-yr ±25 bp/5s), H5 (regime label changes) in src/history_tables.py;
results wired into src/context.py. Run from the repo root:
  python h1_h5_setup.py ; python -m src.history_tables selftest ; python -m src.history_tables all"""
from pathlib import Path
import sys

h = Path("src/history_tables.py"); s = h.read_text()
if "def h1(" in s: print("  history_tables H1-H5: already")
else:
    block = r'''
# ---------------------------------------------------------------- H1, H3, H4, H5
def _macro():
    """Price panel + the two macro legs as changes: 2-yr yield in bp per session, dollar as log return per session."""
    rets, dgs2, dxy = load()
    dgs2 = pd.Series(dgs2).reindex(rets.index).ffill(); dxy = pd.Series(dxy).reindex(rets.index).ffill()
    dxy_r = np.log(dxy).diff() if dxy.dropna().median() > 5 else dxy          # level -> return; already a return otherwise
    dgs2_bp = dgs2.diff() * 100 if dgs2.dropna().median() < 20 else dgs2.diff()  # % level -> bp
    return rets, dgs2_bp, dxy_r


def _cross(x5: pd.Series, thr: float, up=True) -> list:
    """Positions where the 5-session sum first crosses +thr (up) or -thr (down); GAP collapse (prereg §1)."""
    v = x5.to_numpy(); pos, last = [], -10 ** 9
    for i in range(len(v)):
        if np.isfinite(v[i]) and ((v[i] >= thr) if up else (v[i] <= -thr)) and i - last >= GAP:
            pos.append(i); last = i
    return pos


def split_test(rows: pd.DataFrame, seed=0) -> dict:
    """H1: the two halves of a split (column 'grp' in {1,-1}); gap in 20-session sign share >= GAP_PTS, each half n >= MIN_N, label-permutation p < ALPHA."""
    g1, g2 = rows[rows.grp > 0], rows[rows.grp < 0]
    if len(g1) < MIN_N or len(g2) < MIN_N: return {"verdict": "INCONCLUSIVE", "n_up": len(g1), "n_dn": len(g2), "reason": f"a half has n < {MIN_N}"}
    s1, s2 = float((g1.f20 > 0).mean()), float((g2.f20 > 0).mean()); gap = s1 - s2
    rng = np.random.default_rng(seed); sign = (rows.f20 > 0).to_numpy(); grp = rows.grp.to_numpy(); null = np.empty(N_NULL)
    for k in range(N_NULL):
        pg = rng.permutation(grp); null[k] = sign[pg > 0].mean() - sign[pg < 0].mean()
    p = float((np.abs(null) >= abs(gap)).mean())
    return {"verdict": "PASS" if (abs(gap) >= GAP_PTS and p < ALPHA) else "FAIL", "n_up": len(g1), "n_dn": len(g2), "up_sign": s1, "dn_sign": s2,
            "up_f20": float(g1.f20.median()), "dn_f20": float(g2.f20.median()), "up_f60": float(g1.f60.median()), "dn_f60": float(g2.f60.median()), "gap": gap, "p": p}


def run_table(tid: str, title: str, rets: pd.DataFrame, pos: list, grp: dict | None = None, note: str = "") -> dict:
    """Shared runner: paths for every market, summary, the uniform test (or the split test when grp maps pos -> ±1). Writes md + json."""
    run = datetime.now().strftime("%Y-%m-%d %H:%M"); pc = lambda x: f"{np.expm1(x):+.1%}"
    res = {"id": tid, "title": title, "run": run, "n_events": len(pos), "dates": [rets.index[p].strftime("%Y-%m-%d") for p in pos], "markets": {}}
    L = [f"# {tid} — {title}", "", f"*{run}. {len(pos)} events after the 20-session collapse, sample {rets.index[0].date()} → {rets.index[-1].date()}. "
         f"Simple % medians; 'positive at 20' is the share of events with a higher price a month later, 'base' the market's ordinary share. "
         f"Test: prereg_history_tables §1 (gap ≥ 15 pts, n ≥ 30, random-date null p < 0.05). {note}*", "",
         "| market | n | 5 s | 20 s | 60 s | worst (session) | best (session) | positive at 20 | base | gap | p | verdict |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; rows = []
        for p in pos:
            d = paths(r, p)
            if d: d["pos"] = p; d["grp"] = (grp or {}).get(p, 0); rows.append(d)
        rows = pd.DataFrame(rows); sm = summarise(rows)
        if sm["n"] == 0: res["markets"][a] = {"summary": sm}; L.append(f"| {a} | 0 | — | — | — | — | — | — | — | — | — | no data |"); continue
        te = cond_test(rows, r); m = {"summary": sm, "test": te}
        if grp is not None: m["split"] = split_test(rows)
        res["markets"][a] = m
        L.append(f"| {a} | {sm['n']} | {pc(sm['f5'])} | {pc(sm['f20'])} | {pc(sm['f60'])} | {pc(sm['worst'])} ({sm['worst_t']:.0f}) | {pc(sm['best'])} ({sm['best_t']:.0f}) | "
                 f"{sm['sign20']:.0%} | {te.get('base', float('nan')):.0%} | {te.get('gap', float('nan')):+.0%} | {te.get('p', float('nan')):.3f} | {te['verdict']} |")
    if grp is not None:
        L += ["", "Split (H1): 2-yr yield up on the day vs down. Medians at 20 / 60 sessions, share positive at 20, gap between halves, label-permutation p.", "",
              "| market | n up / dn | up 20 s | dn 20 s | up 60 s | dn 60 s | positive up / dn | gap | p | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
        for a, m in res["markets"].items():
            sp = m.get("split")
            if not sp: continue
            if sp["verdict"] == "INCONCLUSIVE": L.append(f"| {a} | {sp['n_up']} / {sp['n_dn']} | — | — | — | — | — | — | — | INCONCLUSIVE ({sp['reason']}) |"); continue
            L.append(f"| {a} | {sp['n_up']} / {sp['n_dn']} | {pc(sp['up_f20'])} | {pc(sp['dn_f20'])} | {pc(sp['up_f60'])} | {pc(sp['dn_f60'])} | {sp['up_sign']:.0%} / {sp['dn_sign']:.0%} | "
                     f"{sp['gap']:+.0%} | {sp['p']:.3f} | {sp['verdict']} |")
    allj = json.loads(OUT.read_text()) if OUT.exists() else {}; allj[tid] = res; OUT.write_text(json.dumps(allj, indent=1))
    (DOCS / f"history_{tid}.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> docs/history_{tid}.md\n")
    return res


def h1():
    rets, dgs2_bp, _ = _macro()
    dates = pd.to_datetime(pd.read_csv(PROC / "fomc_decisions.csv")["date"]); idx = rets.index
    pos = []
    for d in dates:
        p = idx.searchsorted(d)
        if p < len(idx) and abs((idx[p] - d).days) <= 1: pos.append(p)
    pos = sorted(set(pos)); grp = {p: (1 if dgs2_bp.iloc[p] > 0 else -1 if dgs2_bp.iloc[p] < 0 else 0) for p in pos}
    return run_table("H1", "Fed decision days (statement days), split by the 2-yr yield's move that day", rets, pos, grp=grp,
                     note="Decision dates from processed/fomc_decisions.csv (2011 on). No GAP collapse applied: meetings are ≥ 6 weeks apart.")


def h3():
    rets, _, dxy_r = _macro(); x5 = dxy_r.rolling(5).sum(); thr = np.log(1.03)
    up = run_table("H3up", "Dollar jumps: DXY ≥ +3% within five sessions", rets, _cross(x5, thr, True))
    dn = run_table("H3dn", "Dollar drops: DXY ≤ −3% within five sessions", rets, _cross(x5, thr, False))
    return up, dn


def h4():
    rets, dgs2_bp, _ = _macro(); x5 = dgs2_bp.rolling(5).sum()
    up = run_table("H4up", "Rate shocks: 2-yr yield +25 bp or more within five sessions", rets, _cross(x5, 25.0, True))
    dn = run_table("H4dn", "Rate shocks: 2-yr yield −25 bp or more within five sessions", rets, _cross(x5, 25.0, False))
    return up, dn


def h5():
    rets = _macro()[0]; lab = regime_labels(rets.index); v = lab.to_numpy()
    pos, last = [], -10 ** 9
    for i in range(1, len(v)):
        if v[i] != v[i - 1] and v[i] >= 0 and v[i - 1] >= 0 and i - last >= GAP: pos.append(i); last = i
    return run_table("H5", "Regime label changes: first session of a new label", rets, pos, note="Changes into or out of the unlabelled stretch (−1) are not events.")


def run_all():
    h1(); h3(); h4(); h5()
    J = json.loads(OUT.read_text()); print("=== verdicts (20-session sign share vs base rate; H1 = split) ===")
    for tid in ("H1", "H3up", "H3dn", "H4up", "H4dn", "H5"):
        T = J.get(tid, {}); vs = {a: (m.get("split", m.get("test", {})).get("verdict", "—")) for a, m in T.get("markets", {}).items()}
        print(f"  {tid:5} n={T.get('n_events', 0):3}  " + "  ".join(f"{a} {v}" for a, v in vs.items()))

'''
    s = s.replace("\n# ---------------------------------------------------------------- selftest\n", block + "\n# ---------------------------------------------------------------- selftest\n", 1)
    s = s.replace('    {"selftest": selftest, "h0": h0}[cmd]()', '    {"selftest": selftest, "h0": h0, "h1": h1, "h3": h3, "h4": h4, "h5": h5, "all": run_all}[cmd]()', 1)
    s = s.replace('  python -m src.history_tables h0          # today\'s-regime return table (measured only, no test)',
                  '  python -m src.history_tables h0          # today\'s-regime return table (measured only, no test)\n  python -m src.history_tables all         # H1, H3, H4, H5 with the uniform test', 1)
    h.write_text(s); print("  history_tables H1-H5: added")

# ---- context.py wiring
c = Path("src/context.py"); s = c.read_text()
if "HIST_LEADS" in s: print("  context H-tables: already")
else:
    # cached ticker history so several tables don't refetch
    old = '''    try:
        import yfinance as yf
        d = yf.Ticker(tk).history(period="max", interval="1d", auto_adjust=False)
        if d.empty: return None
        px = d["Close"]; px.index = pd.to_datetime(px.index).tz_localize(None); r = np.log(px).diff().dropna()
    except Exception:
        return None
    rows = []'''
    new = '''    r = _hist(tk)
    if r is None: return None
    rows = []'''
    if old not in s: sys.exit("  context ticker_paths anchor not found")
    s = s.replace(old, new, 1)
    helper = '''
from functools import lru_cache


@lru_cache(maxsize=32)
def _hist(tk):
    """Daily log returns of a searched ticker from Yahoo, fetched once per process."""
    try:
        import yfinance as yf
        d = yf.Ticker(tk).history(period="max", interval="1d", auto_adjust=False)
        if d.empty: return None
        px = d["Close"]; px.index = pd.to_datetime(px.index).tz_localize(None); return np.log(px).diff().dropna()
    except Exception:
        return None


HIST_LEADS = [("H1", "On Fed decision days"), ("H3up", "After dollar jumps (≥ 3% in five sessions)"), ("H3dn", "After dollar drops (≥ 3% in five sessions)"),
              ("H4up", "After two-year-yield jumps (≥ 25 bp in five sessions)"), ("H4dn", "After two-year-yield drops (≥ 25 bp in five sessions)"),
              ("H5", "After the model's condition label changes")]


def history_sentences(asset, name, ticker=None):
    """One measured sentence per H-table (+ its test verdict) for a model asset; for a searched ticker, its own paths against the saved event dates."""
    HT = _j(PROC / "history_tables.json") or {}; out = []
    for tid, lead in HIST_LEADS:
        T = HT.get(tid)
        if not T or not T.get("dates"): continue
        yr = T["dates"][0][:4]
        if asset in MODEL:
            m = T.get("markets", {}).get(asset)
            if not m or m["summary"].get("n", 0) < 10: continue
            sm, te = m["summary"], m.get("test", {})
            txt = (f"{lead} — {T['n_events']} since {yr} — {name}'s typical path was {_pct(sm['f20'])} after a month and {_pct(sm['f60'])} after a quarter, "
                   f"with a typical worst dip of {_pct(sm['worst'])} (n {sm['n']}) {tag('measured')}.")
            v = te.get("verdict")
            if v in ("PASS", "FAIL"):
                txt += (f" Whether that month differs from {name}'s ordinary month (higher a month later {te['sign20']:.0%} of the time vs {te['base']:.0%} normally): "
                        f"{v} {tag('tested: ' + v)}.")
            elif v == "INCONCLUSIVE":
                txt += f" Too few cases to test (n {te.get('n')}, the rule needs 30) {tag('tested: INCONCLUSIVE')}."
            sp = m.get("split")
            if sp and sp.get("verdict") in ("PASS", "FAIL"):
                txt += (f" Split by whether the two-year yield rose or fell that day: {_pct(sp['up_f20'])} vs {_pct(sp['dn_f20'])} after a month, "
                        f"{sp['verdict']} {tag('tested: ' + sp['verdict'])}.")
            out.append(txt)
        elif ticker and tid in ("H3up", "H4up", "H5"):
            tp = ticker_paths(ticker, T["dates"])
            if tp is None or len(tp) < 10: continue
            out.append(f"{lead} — {len(tp)} in {ticker}'s own history — its typical path was {_pct(tp.f20.median())} after a month and {_pct(tp.f60.median())} "
                       f"after a quarter, typical worst dip {_pct(tp.worst.median())} {tag('measured')}; computed now from its prices, not tested.")
    return out

'''
    s = s.replace("\n# ---------------------------------------------------------------- the block\n", helper + "\n# ---------------------------------------------------------------- the block\n", 1)
    old = "    rf = referee(asset if asset in MODEL else None)\n"
    if old not in s: sys.exit("  context referee anchor not found")
    s = s.replace(old, "    s2 += history_sentences(asset, name, ticker=ticker)\n" + old, 1)
    s = s.replace('What history says after oil shocks, and the engine\'s record', 'What history says after shocks and events, and the engine\'s record', 1)
    c.write_text(s); print("  context H-tables: wired")
print("done -- python -m src.history_tables selftest ; python -m src.history_tables all")
