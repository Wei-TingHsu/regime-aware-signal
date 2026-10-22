"""
History tables H0–H7 (prereg_history_tables.md, TRACK 3.25). Shared engine: event dates -> forward paths per market -> medians, IQR, n;
one uniform conditional test (20-session sign share vs the market's base rate, >= 15 pts, n >= 30, random-date null p < 0.05).
Outputs: docs/history_<id>.md (table) and processed/history_tables.json (what the app reads). Values stored as log returns; the app shows simple %.

  python -m src.history_tables selftest
  python -m src.history_tables h0          # today's-regime return table (measured only, no test)
  python -m src.history_tables all         # H1, H3, H4, H5 with the uniform test
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.oil_shock import load, regime_labels, ASSETS  # same price panel, same labels as A3

PROC, DOCS = Path("processed"), Path("docs")
H = (5, 10, 20, 40, 60)
GAP, HOLD = 20, 60
GAP_PTS, MIN_N, N_NULL, ALPHA = 0.10, 30, 10000, 0.05   # amended 19 Oct: floor 15 -> 10 pts (prereg §4)
ALPHA_CELL = ALPHA / 6                                  # per-table Bonferroni across the six markets (prereg §4)
TEST_H = (5, 20)
OUT = PROC / "history_tables.json"


# ---------------------------------------------------------------- engine
def paths(r: pd.Series, pos: int) -> dict:
    """Forward log returns of one market after index position pos (NaN-aware; needs HOLD sessions)."""
    seg = r.iloc[pos + 1:pos + HOLD + 1]
    if len(seg) < HOLD or seg.isna().any(): return {}
    cum = seg.cumsum().to_numpy()
    d = {f"f{h}": float(cum[h - 1]) for h in H}
    d["worst"], d["worst_t"] = float(min(cum.min(), 0)), int(cum.argmin()) + 1
    d["best"], d["best_t"] = float(max(cum.max(), 0)), int(cum.argmax()) + 1
    return d


def collapse(idx: pd.DatetimeIndex, events: list) -> list:
    """Events within GAP sessions of the previous kept event are dropped (prereg §1)."""
    pos, keep, last = [], [], -10 ** 9
    for d in sorted(events):
        p = idx.searchsorted(pd.Timestamp(d))
        if p >= len(idx) or p - last < GAP: continue
        keep.append(idx[p]); last = p
    return keep


def summarise(rows: pd.DataFrame) -> dict:
    if rows.empty: return {"n": 0}
    out = {"n": int(len(rows))}
    for c in [f"f{h}" for h in H] + ["worst", "best"]:
        out[c] = float(rows[c].median()); out[c + "_q25"], out[c + "_q75"] = float(rows[c].quantile(.25)), float(rows[c].quantile(.75))
    out["worst_t"], out["best_t"] = float(rows.worst_t.median()), float(rows.best_t.median())
    out["sign20"] = float((rows.f20 > 0).mean())
    return out


def base_rate(r: pd.Series, h: int = 20) -> tuple[float, np.ndarray]:
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


# ---------------------------------------------------------------- H0
def h0() -> dict:
    """Each market's 20/60-session forward return inside each regime label vs all history. Measured only (prereg: no test)."""
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo
    lab = regime_labels(rets.index)
    res = {"id": "H0", "run": datetime.now().strftime("%Y-%m-%d %H:%M"), "markets": {}}
    L = ["# H0 — what each market did inside each regime (measured, no test)", "",
         f"*{res['run']}. Forward 20- and 60-session returns, simple %, median [IQR], sessions counted. The regime label is the engine's own input; "
         "prereg_history_tables §2: measured only, no claim. Label 'all' is the unconditional row for comparison.*", ""]
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; f20, f60 = r.rolling(20).sum().shift(-20), r.rolling(60).sum().shift(-60)
        d = pd.DataFrame({"f20": f20, "f60": f60, "lab": lab}).dropna()
        tab = {}
        for k, g in [("all", d)] + [(str(int(k)), g) for k, g in d.groupby("lab")]:
            tab[k] = {"n": int(len(g)), "f20": float(g.f20.median()), "f20_q25": float(g.f20.quantile(.25)), "f20_q75": float(g.f20.quantile(.75)),
                      "f60": float(g.f60.median()), "sign20": float((g.f20 > 0).mean())}
        res["markets"][a] = tab
        L += [f"## {a}", "", "| regime | sessions | 20-session median [IQR] | share positive at 20 | 60-session median |", "|---|---|---|---|---|"]
        for k, v in tab.items():
            pc = lambda x: f"{np.expm1(x):+.1%}"
            L.append(f"| {k} | {v['n']:,} | {pc(v['f20'])} [{pc(v['f20_q25'])}, {pc(v['f20_q75'])}] | {v['sign20']:.0%} | {pc(v['f60'])} |")
        L.append("")
    allj = json.loads(OUT.read_text()) if OUT.exists() else {}
    allj["H0"] = res; OUT.write_text(json.dumps(allj, indent=1))
    (DOCS / "history_H0.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {DOCS/'history_H0.md'}, {OUT}")
    return res


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


def split_test(rows: pd.DataFrame, h: int = 20, seed=0) -> dict:
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
    rets, _, dxy_r = _macro(); x5 = dxy_r.rolling(5).sum(); thr = np.log(1.02)  # amended 19 Oct from 3%: 6/3 events; prereg §4
    up = run_table("H3up", "Dollar jumps: DXY ≥ +2% within five sessions (amended from 3%, prereg §4)", rets, _cross(x5, thr, True))
    dn = run_table("H3dn", "Dollar drops: DXY ≤ −2% within five sessions (amended from 3%, prereg §4)", rets, _cross(x5, thr, False))
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


# ---------------------------------------------------------------- selftest
def selftest():
    idx = pd.bdate_range("2000-01-03", periods=400); r = pd.Series(0.0, index=idx); r.iloc[101:121] = 0.01
    p = paths(r, 100); assert abs(p["f20"] - 0.20) < 1e-9 and p["best_t"] >= 20; print("  T1 paths: PASS")
    ev = collapse(idx, [idx[10], idx[15], idx[40]]); assert len(ev) == 2; print("  T2 collapse GAP: PASS")
    rng = np.random.default_rng(1); rr = pd.Series(rng.normal(0, 0.01, 3000), index=pd.bdate_range("1995-01-02", periods=3000))
    rows = pd.DataFrame([paths(rr, p) for p in range(100, 2900, 60)]); t = cond_test(rows, rr); assert t["verdict"] == "FAIL", t; print("  T3 null data -> FAIL: PASS")
    rr2 = rr.copy(); pos = list(range(100, 2900, 60))
    for p in pos: rr2.iloc[p + 1:p + 21] += 0.004
    rows = pd.DataFrame([paths(rr2, p) for p in pos]); t = cond_test(rows, rr2); assert t["verdict"] == "PASS", t; print("  T4 planted effect -> PASS: PASS")
    print("selftest: 4/4")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    {"selftest": selftest, "h0": h0, "h1": h1, "h3": h3, "h4": h4, "h5": h5, "all": run_all}[cmd]()
