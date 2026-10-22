"""19 Oct: (1) prereg_history_tables amendment — 5-session horizon beside 20, gap floor 10 pts, per-table Bonferroni p < 0.05/6, prior #54;
engine + Context block updated; (2) step6_report.py: a session is reportable only when the panel has its prices; (3) TRACK open item: longer dollar series.
Run from the repo root:  python horizon_amend.py ; python -m src.history_tables selftest ; python -m src.history_tables all 2>&1 | tail -9"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1a. prereg
p = Path("docs/prereg_history_tables.md"); s = p.read_text()
if "5-session horizon" in s: print("  prereg amendment: already")
else:
    old = "| date | change | reason |\n|---|---|---|\n"
    s = s.replace(old, old + "| 2026-10-19 | **Second horizon and a lower floor.** Every table is tested at 5 sessions as well as 20; the frequency-gap floor is 10 points "
        "(was 15); with 6 tables × 6 markets × 2 horizons = 72 cells, a PASS now also needs p < 0.05 ÷ 6 = 0.0083 within its table. The 20-session results already "
        "recorded in §5 stand as written under the old rule; all cells are re-evaluated under the new rule and recorded again. | Founder's point: an event's effect "
        "can act over days and be swamped by other news within a month; and 15 points of frequency was stricter than a usable signal needs (60/40 is one). The tighter "
        "p guards against manufacturing passes by adding cells. **Prior #54 (Claude):** at 5 sessions Fed days show the largest gaps, but no cell clears 10 points at "
        "p < 0.0083 — everything FAIL or INCONCLUSIVE. |\n", 1)
    p.write_text(s); print("  prereg amendment: added")

# ---------------------------------------------------------------- 1b. engine
h = Path("src/history_tables.py"); s = h.read_text()
if "ALPHA_CELL" in s: print("  history_tables two-horizon: already")
else:
    s = s.replace("GAP_PTS, MIN_N, N_NULL, ALPHA = 0.15, 30, 10000, 0.05",
                  "GAP_PTS, MIN_N, N_NULL, ALPHA = 0.10, 30, 10000, 0.05   # amended 19 Oct: floor 15 -> 10 pts (prereg §4)\nALPHA_CELL = ALPHA / 6                                  # per-table Bonferroni across the six markets (prereg §4)\nTEST_H = (5, 20)", 1)
    old_base = s[s.index("def base_rate(r: pd.Series)"):s.index("# ---------------------------------------------------------------- H0")]
    new_base = '''def base_rate(r: pd.Series, h: int = 20) -> tuple[float, np.ndarray]:
    """Unconditional h-session sign share and the array of all h-session forward returns (for the null)."""
    fh = r.rolling(h).sum().shift(-h).dropna()
    return float((fh > 0).mean()), fh.to_numpy()


def cond_test(rows: pd.DataFrame, r: pd.Series, h: int = 20, seed=0) -> dict:
    """Prereg §1 + §4: sign share after events vs base rate at horizon h; |gap| >= GAP_PTS, n >= MIN_N, random-date null p < ALPHA_CELL."""
    n = len(rows); col = f"f{h}"
    if n < MIN_N: return {"verdict": "INCONCLUSIVE", "n": n, "h": h, "reason": f"n < {MIN_N}"}
    br, allf = base_rate(r, h); obs = float((rows[col] > 0).mean()); gap = obs - br
    rng = np.random.default_rng(seed)
    null = np.array([(rng.choice(allf, n, replace=False) > 0).mean() - br for _ in range(N_NULL)])
    p = float((np.abs(null) >= abs(gap)).mean())
    out = {"verdict": "PASS" if (abs(gap) >= GAP_PTS and p < ALPHA_CELL) else "FAIL", "n": n, "h": h, "sign": obs, "base": br, "gap": gap, "p": p}
    if h == 20: out["sign20"] = obs
    return out


'''
    s = s.replace(old_base, new_base, 1)
    old_split = s[s.index("def split_test(rows: pd.DataFrame, seed=0)"):s.index("def h1():")]
    new_split = '''def split_test(rows: pd.DataFrame, h: int = 20, seed=0) -> dict:
    """H1: the two halves of a split (column 'grp' in {1,-1}); gap in h-session sign share >= GAP_PTS, each half n >= MIN_N, label-permutation p < ALPHA_CELL."""
    col = f"f{h}"; g1, g2 = rows[rows.grp > 0], rows[rows.grp < 0]
    if len(g1) < MIN_N or len(g2) < MIN_N: return {"verdict": "INCONCLUSIVE", "h": h, "n_up": len(g1), "n_dn": len(g2), "reason": f"a half has n < {MIN_N}"}
    s1, s2 = float((g1[col] > 0).mean()), float((g2[col] > 0).mean()); gap = s1 - s2
    rng = np.random.default_rng(seed); sign = (rows[col] > 0).to_numpy(); grp = rows.grp.to_numpy(); null = np.empty(N_NULL)
    for k in range(N_NULL):
        pg = rng.permutation(grp); null[k] = sign[pg > 0].mean() - sign[pg < 0].mean()
    p = float((np.abs(null) >= abs(gap)).mean())
    return {"verdict": "PASS" if (abs(gap) >= GAP_PTS and p < ALPHA_CELL) else "FAIL", "h": h, "n_up": len(g1), "n_dn": len(g2), "up_sign": s1, "dn_sign": s2,
            "up_f20": float(g1.f20.median()), "dn_f20": float(g2.f20.median()), "up_f5": float(g1.f5.median()), "dn_f5": float(g2.f5.median()),
            "up_f60": float(g1.f60.median()), "dn_f60": float(g2.f60.median()), "gap": gap, "p": p}


def run_table(tid: str, title: str, rets: pd.DataFrame, pos: list, grp: dict | None = None, note: str = "") -> dict:
    """Shared runner: paths for every market, summary, the uniform test at 5 and 20 sessions (split test for H1). Writes md + json."""
    run = datetime.now().strftime("%Y-%m-%d %H:%M"); pc = lambda x: f"{np.expm1(x):+.1%}"
    res = {"id": tid, "title": title, "run": run, "n_events": len(pos), "dates": [rets.index[p].strftime("%Y-%m-%d") for p in pos], "markets": {},
           "rule": {"gap_pts": GAP_PTS, "min_n": MIN_N, "alpha_cell": ALPHA_CELL, "horizons": list(TEST_H)}}
    L = [f"# {tid} — {title}", "", f"*{run}. {len(pos)} events after the 20-session collapse, sample {rets.index[0].date()} → {rets.index[-1].date()}. "
         f"Simple % medians. 'positive' = share of events with a higher price h sessions later; 'base' = the market's ordinary share. "
         f"Test (prereg §1 as amended §4): |gap| ≥ {GAP_PTS:.0%} points, n ≥ {MIN_N}, random-date null p < {ALPHA_CELL:.4f}. {note}*", "",
         "| market | n | 5 s | 20 s | 60 s | worst (session) | best (session) | 5 s: positive / base / gap / p | 5 s verdict | 20 s: positive / base / gap / p | 20 s verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    fmt = lambda te: (f"{te['sign']:.0%} / {te['base']:.0%} / {te['gap']:+.0%} / {te['p']:.3f}" if "gap" in te else f"n {te['n']} < {MIN_N}")
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; rows = []
        for p in pos:
            d = paths(r, p)
            if d: d["pos"] = p; d["grp"] = (grp or {}).get(p, 0); rows.append(d)
        rows = pd.DataFrame(rows); sm = summarise(rows)
        if sm["n"] == 0: res["markets"][a] = {"summary": sm}; L.append(f"| {a} | 0 | — | — | — | — | — | — | no data | — | no data |"); continue
        te5, te20 = cond_test(rows, r, 5), cond_test(rows, r, 20); m = {"summary": sm, "test": te20, "test5": te5}
        if grp is not None: m["split"], m["split5"] = split_test(rows, 20), split_test(rows, 5)
        res["markets"][a] = m
        L.append(f"| {a} | {sm['n']} | {pc(sm['f5'])} | {pc(sm['f20'])} | {pc(sm['f60'])} | {pc(sm['worst'])} ({sm['worst_t']:.0f}) | {pc(sm['best'])} ({sm['best_t']:.0f}) | "
                 f"{fmt(te5)} | {te5['verdict']} | {fmt(te20)} | {te20['verdict']} |")
    if grp is not None:
        L += ["", "Split (H1): 2-yr yield up on the day vs down. Medians for each half; 'positive up / dn' is the share higher h sessions later; label-permutation p.", "",
              "| market | n up / dn | h | up median | dn median | positive up / dn | gap | p | verdict |", "|---|---|---|---|---|---|---|---|---|"]
        for a, m in res["markets"].items():
            for key, hh in (("split5", 5), ("split", 20)):
                sp = m.get(key)
                if not sp: continue
                if sp["verdict"] == "INCONCLUSIVE": L.append(f"| {a} | {sp['n_up']} / {sp['n_dn']} | {hh} | — | — | — | — | — | INCONCLUSIVE ({sp['reason']}) |"); continue
                L.append(f"| {a} | {sp['n_up']} / {sp['n_dn']} | {hh} | {pc(sp[f'up_f{hh}'])} | {pc(sp[f'dn_f{hh}'])} | {sp['up_sign']:.0%} / {sp['dn_sign']:.0%} | {sp['gap']:+.0%} | {sp['p']:.3f} | {sp['verdict']} |")
    allj = json.loads(OUT.read_text()) if OUT.exists() else {}; allj[tid] = res; OUT.write_text(json.dumps(allj, indent=1))
    (DOCS / f"history_{tid}.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> docs/history_{tid}.md\n")
    return res


'''
    s = s.replace(old_split, new_split, 1)
    old_sum = s[s.index("def run_all():"):s.index("# ---------------------------------------------------------------- selftest")]
    new_sum = '''def run_all():
    h1(); h3(); h4(); h5()
    J = json.loads(OUT.read_text()); print(f"=== verdicts: sign share vs base, |gap| >= {GAP_PTS:.0%} pts, n >= {MIN_N}, p < {ALPHA_CELL:.4f}; H1 = split ===")
    for tid in ("H1", "H3up", "H3dn", "H4up", "H4dn", "H5"):
        T = J.get(tid, {})
        for key5, key20, lab in (("split5", "split", "H1") if tid == "H1" else ("test5", "test", tid),):
            v5 = {a: m.get(key5, {}).get("verdict", "—") for a, m in T.get("markets", {}).items()}
            v20 = {a: m.get(key20, {}).get("verdict", "—") for a, m in T.get("markets", {}).items()}
            print(f"  {tid:5} n={T.get('n_events', 0):3}   5 s: " + " ".join(f"{a} {v[:4]}" for a, v in v5.items()))
            print(f"  {'':5}        20 s: " + " ".join(f"{a} {v[:4]}" for a, v in v20.items()))
    passes = [(tid, a, k) for tid, T in J.items() if tid != "H0" for a, m in T.get("markets", {}).items() for k in ("test5", "test", "split5", "split") if m.get(k, {}).get("verdict") == "PASS"]
    print(f"  PASS cells: {passes if passes else 'none'}")


'''
    s = s.replace(old_sum, new_sum, 1)
    # selftest: planted effect must still PASS under the tighter alpha (effect is large), noise still FAIL
    h.write_text(s); print("  history_tables two-horizon: done")

# ---------------------------------------------------------------- 1c. context: one-week sentence
c = Path("src/context.py"); s = c.read_text()
if "test5" in s: print("  context one-week: already")
else:
    old = "            out.append(txt)\n        elif ticker and tid in"
    new = '''            te5 = m.get("test5", {}); sp5 = m.get("split5", {})
            if te5.get("verdict") in ("PASS", "FAIL"):
                txt += (f" At one week (5 sessions): {_pct(sm['f5'])}, higher {te5['sign']:.0%} of the time vs {te5['base']:.0%} normally — "
                        f"{te5['verdict']} {tag('tested: ' + te5['verdict'])}.")
            if sp5.get("verdict") in ("PASS", "FAIL"):
                txt += f" One-week split by the yield's move: {_pct(sp5['up_f5'])} vs {_pct(sp5['dn_f5'])}, {sp5['verdict']} {tag('tested: ' + sp5['verdict'])}."
            out.append(txt)
        elif ticker and tid in'''
    if old not in s: sys.exit("  context anchor not found")
    s = s.replace(old, new, 1)
    s = s.replace("(higher a month later {te['sign20']:.0%} of the time vs {te['base']:.0%} normally)", "(higher a month later {te['sign']:.0%} of the time vs {te['base']:.0%} normally)", 1)
    c.write_text(s); print("  context one-week: added")

# ---------------------------------------------------------------- 2. step6 guard
q = Path("step6_report.py"); s = q.read_text()
if "panel has no prices for this session yet" in s: print("  step6 guard: already")
else:
    old = '''        for d in done:
            stem = d.strftime("%Y%m%d")
            if not (REPORT_DIR / f"{stem}.json").exists():
                print(f"PENDING {stem}")
        return'''
    new = '''        # 19 Oct: a calendar-completed session is reportable only once the panel HAS its prices. On 16 Oct the download lagged a
        # session and a report was written over an all-NaN row; the forward log had already guarded against this, step 6 had not.
        rp = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet")
        for d in done:
            stem = d.strftime("%Y%m%d")
            if (REPORT_DIR / f"{stem}.json").exists():
                continue
            if d not in rp.index or rp.loc[d].notna().mean() < 0.5:
                print(f"DEFERRED {stem}: panel has no prices for this session yet"); continue
            print(f"PENDING {stem}")
        return'''
    if old not in s: sys.exit("  step6 pending anchor not found")
    s = s.replace(old, new, 1)
    old = '''    if not a.date:
        raise SystemExit("give --date YYYYMMDD, --latest or --pending")
'''
    new = old + '''    if not a.force:
        _rp = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet"); _d = pd.Timestamp(a.date)
        if _d not in _rp.index or _rp.loc[_d].notna().mean() < 0.5:
            raise SystemExit(f"  {a.date}: panel has no prices for this session yet -- deferred (--force overrides)")
'''
    if old not in s: sys.exit("  step6 date anchor not found")
    q.write_text(s.replace(old, new, 1)); print("  step6 guard: added (--pending and --date)")

# ---------------------------------------------------------------- 3. TRACK
t = Path("docs/TRACK.md"); s = t.read_text()
if "Horizon amendment 19 Oct" in s: print("  TRACK: already")
else:
    old = "H3 needs a dollar series that starts before the one the engine reads.\n"
    if old not in s: print("  TRACK anchor not found -- add by hand")
    else:
        t.write_text(s.replace(old, old + "**Horizon amendment 19 Oct** (founder): every table also at 5 sessions, gap floor 10 points, PASS needs p < 0.05/6 within its "
                     "table; prior #54. **Data item:** a dollar series from the 1990s (the engine's FRED broad index starts 2006; DXY runs from the 1970s) — needed before "
                     "H3 can reach 30 events. **Pipeline fix:** step 6 now defers a session until the panel has its prices (16 Oct report had been written over an "
                     "all-NaN row).\n", 1)); print("  TRACK: amendment + data item + guard noted")
print("done -- python -m src.history_tables selftest ; python -m src.history_tables all 2>&1 | tail -9")
