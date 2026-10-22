"""22 Oct: (1) latency audit reads the RAW caches (FRED, Yahoo) not the forward-filled panel; nightly wti_cont rebuild; SEC 429 backoff.
(2) Register and build Stage 1 of the target-range engine (docs/prereg_target_range.md, src/target_range.py; TRACK 3.29, MASTER row 46).
Run from the repo root:  python target_range_setup.py ; python -m src.target_range selftest ; python -m src.target_range build ; python -m src.target_range calibrate"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1a. latency audit: raw caches
la = Path("src/latency_audit.py"); s = la.read_text()
if 'raw/fred' in s: print("  latency_audit raw: already")
else:
    old = 'FILES = {"asset_returns.parquet": ["SPY", "TLT", "GLD", "UUP", "USO"], "macro_panel.parquet": None, "wti_cont.parquet": ["WTI_SPOT", "WTI_FUT", "USO"]}'
    new = 'FILES = {"asset_returns.parquet": ["SPY", "TLT", "GLD", "UUP", "USO"], "wti_cont.parquet": ["WTI_SPOT", "WTI_FUT", "USO"]}\nRAW = {"raw/yfinance": ["SPY", "TLT", "GLD", "UUP", "USO", "CL=F"], "raw/fred": None}   # the caches the nightly --force refresh writes; no forward-fill here'
    assert old in s; s = s.replace(old, new, 1)
    old = "    try:\n        import yfinance as yf\n        for t in LIVE:"
    new = '''    for d, keys in RAW.items():
        dp = Path(d)
        if not dp.exists(): rows.append(dict(run=now, file=d, series="(missing)", last="", lag=np.nan)); continue
        for fp in sorted(dp.glob("*.parquet")):
            k = fp.stem
            if keys and k not in keys: continue
            try:
                df = pd.read_parquet(fp); df.index = pd.to_datetime(df.index); ld = df.dropna(how="all").index.max()
                rows.append(dict(run=now, file=d, series=k, last=ld.strftime("%Y-%m-%d"), lag=sessions_between(ld.normalize(), lc)))
            except Exception as e:
                rows.append(dict(run=now, file=d, series=k, last=f"error {type(e).__name__}", lag=np.nan))
    try:
        import yfinance as yf
        for t in LIVE:'''
    assert old in s; s = s.replace(old, new, 1)
    s = s.replace("Reading: a lag of 1 on FRED series (yields, dollar, oil spot) is their publication schedule",
                  "Reading: raw/fred and raw/yfinance are what the nightly --force refresh actually received (no forward-fill). A lag of 1 on FRED series is their publication schedule", 1)
    la.write_text(s); print("  latency_audit raw: fixed")

# ---------------------------------------------------------------- 1b. nightly wti_cont rebuild
d = Path("daily_run.sh"); s = d.read_text()
if "src.wti_cont build" in s: print("  wti_cont nightly: already")
else:
    old = 'python -m src.oil_shock forward || echo "  oil forward failed -- continuing"\n'
    if old not in s: print("  daily_run oil-forward anchor not found -- add by hand before it: python -m src.wti_cont build || echo \"  wti_cont rebuild failed -- continuing\"")
    else: d.write_text(s.replace(old, '# 22 Oct (TRACK 3.27 audit): the oil columns were built once on 12 Oct and read stale ever since; rebuild nightly before the oil forward row\npython -m src.wti_cont build || echo "  wti_cont rebuild failed -- continuing"\n' + old, 1)); print("  wti_cont nightly: added")

# ---------------------------------------------------------------- 1c. SEC 429 backoff
f = Path("src/fetch_sources.py"); s = f.read_text()
if "e.code == 429" in s: print("  SEC backoff: already")
else:
    old = "            if e.code < 500:\n                raise last                      # client error: retrying will not help\n"
    new = ("            if e.code == 429:                   # SEC rate threshold: back off and retry (22 Oct)\n"
           "                time.sleep(12 * (i + 1)); continue\n" + old)
    assert old in s; f.write_text(s.replace(old, new, 1)); print("  SEC backoff: added")

# ---------------------------------------------------------------- 2a. prereg
p = Path("docs/prereg_target_range.md")
if p.exists(): print("  prereg_target_range.md: already")
else:
    p.write_text(r"""# Pre-registration — target-range engine (TRACK §3.29, T2 + T13)

*Registered 2026-10-22 before code, at the founder's direction: attribution, magnitude and a point target are to be designed and tested, not
discussed. What A3b tested and failed was **direction** (sign hit-rate at 20 sessions from three shock-week features, as few as 8 comparable
cases). This engine answers a different question — **how far, how likely** — which depends on volatility and regime, both of which persist.*

## Output (fixed form)
For a market, today's price P, a horizon h and a target T: the median h-session path end (P × e^median), the inter-quartile band, and
**the probability that the price touches T within h sessions** under today's condition, with the independent-case count, against the
unconditional probability. The point target is the median; the probability is the claim. Reasons (Stage 2/3) may shift the probability only
through cells that have passed their own test.

## Stage 1 — statistics (built 22 Oct)
- Markets SPY, TLT, GLD, UUP, USO, WTI_SPOT; horizons 20, 60, 120 sessions; targets ±2.5, 5, 10, 15, 20%.
- For every session i: max and min cumulative log return over sessions i+1 … i+h. Reach-up(X) = share of sessions whose max ≥ log(1+X);
  reach-down likewise. Conditioned on the regime label at i (expanding labels, as the app); "all" row unconditional. Independent cases = n ÷ h.
- **Test (walk-forward calibration):** for each year y = 2012 … last complete year, probabilities are estimated from sessions whose window
  ends before 1 Jan y, applied to non-overlapping starts in y (step h), scored by Brier against the unconditional probabilities estimated the
  same way. Primary cells: h = 60, X = 5% and 10%, up and down, each market. Criterion: Brier skill ≥ 0.05 and positive in ≥ 60% of years →
  PASS; skill ≤ 0 → FAIL; else INCONCLUSIVE. 10% of cells may pass by chance at this count (48 cells); a PASS is reported with that sentence.
- **Prior #55 (Claude):** skill between 0 and 0.03 on most cells — the regime adds little beyond what the unconditional base rate already
  carries; INCONCLUSIVE overall, no market with a majority of PASS cells.

## Stage 2 — reasons (registered, built after Stage 1 is recorded)
- Episodes: peak-to-trough and trough-to-peak swings ≥ 10% per market, 1995 →.
- The reader labels the documents dated inside each episode (FOMC, 8-K, political; prints from 2026) with the reasons present, v1 vocabulary
  open-ended on the first pass over 20 episodes, then **frozen** before the full pass (the prompt-review rule of prereg_prints).
- Measured: each reason's frequency in rises vs falls (lift) with a label-permutation null; nothing enters Stage 3 without lift p < 0.05/k
  for k reasons.
- **Prior #56:** fewer than three reasons clear the bar; the same reasons appear in both rises and falls.

## Stage 3 — weights (registered, built after Stage 2)
- Walk-forward regularised quantile model: inputs = reason indicators that cleared Stage 2 + regime + trailing 60-session volatility;
  output = the 25/50/75 quantiles of the h-session path end and the reach probabilities. Scored on held-out years by pinball loss and Brier
  against Stage 1. Criterion: ≥ 5% improvement on both, in ≥ 60% of years. Weights are published with the cell count that earned them.
- **Prior #57:** volatility carries the improvement; reasons add < 1%; FAIL on the reasons' marginal contribution.

## Amendments
| date | change | reason |
|---|---|---|

## Results
| date | stage | result | prior |
|---|---|---|---|
""")
    print("  prereg_target_range.md: written")

# ---------------------------------------------------------------- 2b. engine stage 1
tr = Path("src/target_range.py")
if tr.exists(): print("  target_range.py: already")
else:
    tr.write_text(r'''"""
Target-range engine, Stage 1 (docs/prereg_target_range.md). How far and how likely, by regime: reach probabilities and path quantiles.
  python -m src.target_range selftest
  python -m src.target_range build                      # processed/target_range.json + docs/target_range.md
  python -m src.target_range calibrate                  # the registered walk-forward test -> docs/target_range_calibration.md
  python -m src.target_range ask GLD --price 4090 --target 4500 --h 60
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.oil_shock import load, regime_labels, ASSETS

PROC, DOCS = Path("processed"), Path("docs")
H = (20, 60, 120); X = (0.025, 0.05, 0.10, 0.15, 0.20)
OUT = PROC / "target_range.json"
SKILL_PASS, YEAR_SHARE, FIRST_YEAR = 0.05, 0.60, 2012


def extremes(r: pd.Series, h: int):
    """Per start session i: max and min cumulative log return over i+1..i+h, and the end value. NaN where the window is incomplete."""
    c = np.nancumsum(r.to_numpy()); n = len(r)      # c[i] = cumulative through session i
    mx = np.full(n, np.nan); mn = np.full(n, np.nan); end = np.full(n, np.nan)
    if n > h:
        w = sliding_window_view(c, h + 1)            # w[i] = c[i..i+h]
        seg = w[:, 1:] - w[:, [0]]                   # = returns of sessions i+1..i+h, cumulative from the close of session i
        k = seg.shape[0]                             # = n - h windows, for starts 0..n-h-1
        mx[:k], mn[:k], end[:k] = seg.max(1), seg.min(1), seg[:, -1]
    bad = r.isna().rolling(h).sum().shift(-h).fillna(1).to_numpy() > 0   # any NaN inside the window -> drop
    mx[bad] = mn[bad] = end[bad] = np.nan
    return mx, mn, end


def _probs(mx, mn, end, mask):
    m = mask & np.isfinite(mx); n = int(m.sum())
    if n == 0: return {"n": 0}
    d = {"n": n, "end_med": float(np.median(end[m])), "end_q25": float(np.quantile(end[m], .25)), "end_q75": float(np.quantile(end[m], .75)),
         "worst_med": float(np.median(mn[m])), "best_med": float(np.median(mx[m]))}
    for x in X:
        d[f"up_{x}"] = float((mx[m] >= np.log1p(x)).mean()); d[f"dn_{x}"] = float((mn[m] <= np.log1p(-x)).mean())
    return d


def build():
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; lab = regime_labels(rets.index).to_numpy()
    res = {"run": datetime.now().strftime("%Y-%m-%d %H:%M"), "horizons": list(H), "targets": list(X), "markets": {}}
    L = [f"# Target range — reach probabilities and path quantiles by regime (Stage 1, measured)", "",
         f"*{res['run']}. For each start session, the max/min cumulative return over the next h sessions. 'up 10%' = share of starts whose "
         "price touched +10% within h; 'end' = median path end [IQR]. Overlapping starts; independent cases ≈ n ÷ h. Measured only until the "
         "calibration test (prereg_target_range §Stage 1) has run.*", ""]
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; res["markets"][a] = {}
        L += [f"## {a}", "", "| h | regime | n (indep.) | end median [IQR] | typical worst | typical best | up 5% | up 10% | up 20% | down 5% | down 10% | down 20% |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for h in H:
            mx, mn, end = extremes(r, h); res["markets"][a][str(h)] = {}
            for k in ["all"] + sorted(set(int(v) for v in lab if v >= 0)):
                mask = np.ones(len(r), bool) if k == "all" else (lab == k)
                d = _probs(mx, mn, end, mask); res["markets"][a][str(h)][str(k)] = d
                if d["n"] == 0: continue
                pc = lambda v: f"{np.expm1(v):+.1%}"
                L.append(f"| {h} | {k} | {d['n']:,} ({d['n'] // h}) | {pc(d['end_med'])} [{pc(d['end_q25'])}, {pc(d['end_q75'])}] | {pc(d['worst_med'])} | {pc(d['best_med'])} | "
                         f"{d['up_0.05']:.0%} | {d['up_0.1']:.0%} | {d['up_0.2']:.0%} | {d['dn_0.05']:.0%} | {d['dn_0.1']:.0%} | {d['dn_0.2']:.0%} |")
        L.append("")
    OUT.write_text(json.dumps(res, indent=1)); (DOCS / "target_range.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40])); print(f"... -> docs/target_range.md, {OUT}")


def calibrate():
    """Walk-forward: probabilities from windows ending before year y, applied to non-overlapping starts in y, Brier vs unconditional."""
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; lab = regime_labels(rets.index).to_numpy(); idx = rets.index
    h = 60; last_year = idx[-1].year - 1; rows = []
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; mx, mn, end = extremes(r, h); yrs = idx.year.to_numpy()
        for x in (0.05, 0.10):
            for side, arr, thr in (("up", mx, np.log1p(x)), ("down", mn, np.log1p(-x))):
                per_year = []
                for y in range(FIRST_YEAR, last_year + 1):
                    train = (yrs < y) & np.isfinite(arr) & (np.arange(len(r)) + h < idx.searchsorted(pd.Timestamp(f"{y}-01-01")))
                    if train.sum() < 500: continue
                    starts = [i for i in range(idx.searchsorted(pd.Timestamp(f"{y}-01-01")), idx.searchsorted(pd.Timestamp(f"{y + 1}-01-01")), h) if np.isfinite(arr[i])]
                    if len(starts) < 2: continue
                    hit_tr = (arr[train] >= thr) if side == "up" else (arr[train] <= thr)
                    p_unc = hit_tr.mean(); lab_tr = lab[train]
                    b_reg = b_unc = 0.0; cnt = 0
                    for i in starts:
                        k = lab[i]; sel = lab_tr == k
                        p_reg = hit_tr[sel].mean() if (k >= 0 and sel.sum() >= 100) else p_unc
                        y_ = float((arr[i] >= thr) if side == "up" else (arr[i] <= thr))
                        b_reg += (p_reg - y_) ** 2; b_unc += (p_unc - y_) ** 2; cnt += 1
                    per_year.append((y, cnt, b_reg / cnt, b_unc / cnt))
                if not per_year: rows.append(dict(market=a, x=x, side=side, verdict="INCONCLUSIVE", years=0)); continue
                py = pd.DataFrame(per_year, columns=["year", "n", "b_reg", "b_unc"])
                skill = 1 - py.b_reg.sum() / py.b_unc.sum() if py.b_unc.sum() > 0 else np.nan
                share = float((py.b_reg < py.b_unc).mean())
                verdict = "PASS" if (skill >= SKILL_PASS and share >= YEAR_SHARE) else ("FAIL" if skill <= 0 else "INCONCLUSIVE")
                rows.append(dict(market=a, x=x, side=side, years=len(py), cases=int(py.n.sum()), skill=skill, years_better=share, verdict=verdict))
    df = pd.DataFrame(rows)
    L = [f"# Target range — Stage 1 calibration (registered test)", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. h = 60; targets ±5%, ±10%; years {FIRST_YEAR}–{last_year}; Brier skill of regime-conditional reach probabilities "
         f"over unconditional ones, walk-forward. PASS: skill ≥ {SKILL_PASS} and better in ≥ {YEAR_SHARE:.0%} of years; FAIL: skill ≤ 0. "
         f"{len(df)} cells — about {int(0.1 * len(df))} could pass by chance.*", "",
         "| market | target | side | years | cases | Brier skill | years better | verdict |", "|---|---|---|---|---|---|---|---|"]
    for _, q in df.iterrows():
        L.append(f"| {q.market} | {q.x:.0%} | {q.side} | {q.years} | {q.get('cases', '')} | {q.skill:+.3f} | {q.years_better:.0%} | {q.verdict} |" if "skill" in q and pd.notna(q.skill)
                 else f"| {q.market} | {q.x:.0%} | {q.side} | {q.years} | | | | {q.verdict} |")
    vc = df.verdict.value_counts().to_dict()
    L += ["", f"Verdict counts: {vc}. Per market, majority PASS: " + ", ".join(f"{m}: {'yes' if (g.verdict == 'PASS').mean() > 0.5 else 'no'}" for m, g in df.groupby('market'))]
    (DOCS / "target_range_calibration.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/target_range_calibration.md")


def ask(asset, price, target, h, regime=None):
    J = json.loads(OUT.read_text()); T = J["markets"][asset][str(h)]
    if regime is None:
        lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; regime = int(regime_labels(rets.index).iloc[-1])
    d, al = T.get(str(regime)) or T["all"], T["all"]; x = target / price - 1; side = "up" if x > 0 else "dn"; ax = abs(x)
    xs = np.array(X); j = int(np.argmin(np.abs(xs - ax))); key = f"{side}_{xs[j]}"
    med_px = price * np.exp(d["end_med"]); lo_px, hi_px = price * np.exp(d["end_q25"]), price * np.exp(d["end_q75"])
    print(f"{asset} at {price:,.0f}, horizon {h} sessions, condition {regime}: median path end {med_px:,.0f} [{lo_px:,.0f}, {hi_px:,.0f}] "
          f"(n {d['n']:,}, ≈{d['n'] // h} independent). Touching {target:,.0f} ({x:+.1%}; nearest registered target ±{xs[j]:.1%}): "
          f"{d[key]:.0%} in this condition vs {al[key]:.0%} over all history. Measured; calibration verdict in docs/target_range_calibration.md.")


def selftest():
    idx = pd.bdate_range("2000-01-03", periods=300); r = pd.Series(0.0, index=idx); r.iloc[11:21] = 0.01; r.iloc[21:31] = -0.03
    mx, mn, end = extremes(r, 20)
    assert abs(mx[10] - 0.10) < 1e-9 and abs(mn[10] - (0.10 - 0.30)) < 1e-9 and abs(end[10] - (-0.20)) < 1e-9, (mx[10], mn[10], end[10]); print("  T1 extremes: PASS")
    assert np.isnan(mx[-1]) and np.isfinite(mx[0]); print("  T2 window bounds: PASS")
    d = _probs(mx, mn, end, np.ones(len(r), bool)); assert 0 <= d["up_0.05"] <= 1 and d["n"] == 280; print("  T3 probabilities: PASS")
    print("selftest: 3/3")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("selftest", "build", "calibrate"): sub.add_parser(c)
    q = sub.add_parser("ask"); q.add_argument("asset"); q.add_argument("--price", type=float, required=True); q.add_argument("--target", type=float, required=True)
    q.add_argument("--h", type=int, default=60); q.add_argument("--regime", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "ask": ask(a.asset, a.price, a.target, a.h, a.regime)
    else: {"selftest": selftest, "build": build, "calibrate": calibrate}[a.cmd]()
''')
    print("  target_range.py: written (Stage 1)")

# ---------------------------------------------------------------- 2c. TRACK + MASTER
t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "## 4. Potential upgrades — not registered, not costed\n"
if "### 3.29 Target-range engine" in s: print("  TRACK 3.29: already")
else:
    add = """### 3.29 Target-range engine — how far, how likely (registered 22 Oct at the founder's direction; Stage 1 built)

Founder: attribution, magnitude and a point target are to be designed and tested, not discussed. A3b failed on *direction*; this engine answers
*how far and how likely*: per market, horizon and regime, the probability of touching ±X% within h sessions and the path-end quantiles, applied to
today's price (median = the point target, the probability = the claim). Stage 1 statistics with a walk-forward Brier calibration test (prior #55);
Stage 2 reader-labelled reasons per episode with a lift test (prior #56); Stage 3 regularised quantile weights (prior #57). `docs/prereg_target_range.md`,
`src/target_range.py`. The §4 design note of 22 Oct is superseded by this registration.

"""
    s = s.replace(anchor, add + anchor, 1)
    s = s.replace("- **Reason-weighted path range (founder, 22 Oct).**", "- **Reason-weighted path range (founder, 22 Oct) — registered as 3.29 the same day.**", 1)
    t.write_text(s); print("  TRACK 3.29: done")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "| 46 | Target-range engine" in s: print("  MASTER row 46: already")
else:
    i = s.index("| 45 | History tables"); j = s.index("\n", i) + 1
    s = s[:j] + ("| 46 | Target-range engine (T2 + T13): regime-conditional reach probabilities and path quantiles beat the unconditional ones out of sample "
                 "(Brier skill ≥ 0.05, ≥ 60% of years); reasons (Stage 2 lift test) and weights (Stage 3 pinball/Brier) each earn their place | registered 22 Oct "
                 "before code; Stage 1 built | priors #55 INCONCLUSIVE, #56 < 3 reasons, #57 reasons add < 1% | `docs/prereg_target_range.md`, TRACK 3.29 |\n") + s[j:]
    m.write_text(s); print("  MASTER row 46: done")
print("done -- python -m src.target_range selftest ; python -m src.target_range build ; python -m src.target_range calibrate")
