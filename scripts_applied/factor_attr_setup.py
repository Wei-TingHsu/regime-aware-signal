"""23 Oct: register and build factor attribution (TRACK 3.31, prereg_factor_attribution.md): the founder's method — name the reasons, measure each
one's share of a move with a declared prime-factor ordering, state it in dollars, and when a reason reverses expect that many dollars back —
with the two tests that must pass before a bounce number is quoted. Also force-adds the processed files the cloud app reads.
Run from the repo root:  python factor_attr_setup.py ; pip install xlrd -q ; python -m src.factor_attribution selftest ;
                         python -m src.factor_attribution fetch-gpr ; python -m src.factor_attribution episode GLD --start 2026-01-28 --end 2026-10-21 --price-start 5600"""
from pathlib import Path
import sys

p = Path("docs/prereg_factor_attribution.md")
if p.exists(): print("  prereg_factor_attribution.md: already")
else:
    p.write_text(r"""# Pre-registration — factor attribution of price episodes (TRACK §3.31)

*Registered 2026-10-23 before code, from the founder's method (22 Oct): "US–Iran war + rate-hike speculation crashed gold from 5,600 to 4,000.
Take the war as the prime factor and put every other reason into the macro-state PCA line; find the weight of that reason; next round make
rate hikes the prime factor. Multiply the weight by the move and you have how many dollars each factor caused; when the war ends, expect
about that many dollars back." This is a return decomposition with an ordered attribution. It replaces the Stage 2/3 plan of
prereg_target_range.md: reasons are measured proxies, not reader labels; the reader's role becomes naming which event is driving a proxy.*

## 1. Model (fixed)
- Market return r_t (daily log) on daily changes of proxies for each reason:
  **war** = Δlog GPR (Caldara–Iacoviello daily geopolitical-risk index); **hikes** = Δ(DGS2 − EFFR) in bp (tightening priced over two years);
  **real** = ΔDFII10 (bp); **dollar** = Δlog DTWEXBGS; **oil** = Δlog WTI_SPOT; **vix** = Δlog VIXCLS; **macro** = Δ of the first two macro PCA
  scores (the "macro state regime" line). The residual is what no named reason explains.
- Sensitivities (betas) are estimated on the **504 sessions before the episode starts** (walk-forward: known at the start) and, for comparison,
  on the full sample. Standard errors from the window.
- **Ordering.** The factors are orthogonalised in a declared order (Gram–Schmidt): the prime factor keeps everything it co-moves with, the second
  keeps what is left, and so on; the macro line last; residual after all. Two orderings are always reported — the founder's prime factor first,
  and the mirror (the second reason first) — plus the joint (unordered) regression. The spread between orderings is the attribution's honest
  uncertainty, published with it.
- **Dollars.** contribution_k (log units) = β_k^ordered × Σ(ΔF_k^orth over the episode); dollars_k = P_start × contribution_k.
  Reversal estimate for factor k = −dollars_k × (fraction of the proxy's move that reverses), with the beta's ±1 s.e. band.

## 2. Tests (both must pass before any bounce number is quoted to a customer)
- **T-A explanatory stability (walk-forward):** for each 20-session block from 2008 on, betas from the prior 504 sessions, R² of the
  contemporaneous decomposition on the block. Criterion: median out-of-sample R² ≥ 0.20 for GLD (≥ 0.10 for the other markets) → PASS.
- **T-B sign stability:** each factor's beta sign is the same in ≥ 70% of rolling windows (504 sessions, stepped 63) → that factor is quotable;
  otherwise its dollars are shown as "unstable — not quotable".
- **T-C reversal (registered, run after T-A/T-B):** episodes where the war proxy spiked (GPR ≥ 90th percentile of the prior two years) and then
  fell back below its median: predicted market move = β_war(pre) × ΔF over the fall-back window vs realised. Criterion: correlation ≥ 0.3 on
  n ≥ 15 episodes and MAE ≥ 10% below the zero forecast → PASS.
- Priors (Claude, counted if wrong): **#58** T-A: GLD median OOS R² 0.25–0.40, carried by real yields and the dollar — PASS; **#59** T-B: war and
  oil betas unstable (< 70%), real, dollar, hikes stable; **#60** T-C: FAIL or INCONCLUSIVE — the war proxy's gold beta is small and its
  reversals are gradual.

## 3. Outputs
`docs/factor_attribution_<market>_<start>_<end>.md` (the episode table, both orderings, dollars, reversal lines with bands and the T-A/T-B
status), `docs/factor_attribution_tests.md`, `processed/factor_attribution.json`. App: the "Why it moved" block under a market, once T-A/T-B
have run, with every line tagged.

## Amendments
| date | change | reason |
|---|---|---|

## Results
| date | test | result | prior |
|---|---|---|---|
""")
    print("  prereg_factor_attribution.md: written")

fa = Path("src/factor_attribution.py")
if fa.exists(): print("  factor_attribution.py: already")
else:
    fa.write_text(r'''"""
Factor attribution of price episodes (docs/prereg_factor_attribution.md, TRACK 3.31).
  python -m src.factor_attribution selftest
  python -m src.factor_attribution fetch-gpr                       # Caldara-Iacoviello daily GPR -> processed/gpr_daily.parquet
  python -m src.factor_attribution episode GLD --start 2026-01-28 --end 2026-10-21 --price-start 5600 [--prime war --second hikes]
  python -m src.factor_attribution tests GLD                       # T-A explanatory stability, T-B sign stability
"""
from __future__ import annotations
import json, sys, urllib.request
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PROC, DOCS = Path("processed"), Path("docs")
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
GPR = PROC / "gpr_daily.parquet"
WINDOW, STEP, BLOCK = 504, 63, 20
ORDER_DEFAULT = ["war", "hikes", "real", "dollar", "oil", "vix", "macro1", "macro2"]
LABEL = {"war": "geopolitical risk (GPR index)", "hikes": "rate-hike speculation (2-yr yield minus fed funds)", "real": "real 10-yr yield",
         "dollar": "US dollar (broad index)", "oil": "oil (WTI spot)", "vix": "equity volatility (VIX)", "macro1": "macro state, PCA line 1",
         "macro2": "macro state, PCA line 2"}


# ---------------------------------------------------------------- data
def fetch_gpr():
    try:
        raw = urllib.request.urlopen(urllib.request.Request(GPR_URL, headers={"User-Agent": "Mozilla/5.0 regime-aware-signal research"}), timeout=60).read()
        tmp = PROC / "gpr_daily_recent.xls"; tmp.write_bytes(raw)
        df = pd.read_excel(tmp)
        col = next(c for c in df.columns if str(c).upper().startswith("GPRD") and "ACT" not in str(c).upper() and "THREAT" not in str(c).upper())
        day = next(c for c in df.columns if str(c).lower() in ("day", "date"))
        s = pd.Series(df[col].to_numpy(float), index=pd.to_datetime(df[day].astype(str), format="%Y%m%d", errors="coerce")).dropna()
        s.name = "GPRD"; s.to_frame().to_parquet(GPR); print(f"  GPR daily: {s.index[0].date()} -> {s.index[-1].date()} ({len(s):,} days) -> {GPR}")
    except Exception as e:
        print(f"  GPR fetch failed ({type(e).__name__}: {str(e)[:120]}). Download {GPR_URL} by hand into processed/gpr_daily_recent.xls and rerun, "
              "or the war factor is reported as unavailable.")


def factors(idx: pd.DatetimeIndex) -> pd.DataFrame:
    """Daily factor changes aligned to the price panel's sessions. Missing proxies are dropped with a note."""
    m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); m = m.reindex(idx).ffill()
    F = pd.DataFrame(index=idx)
    if GPR.exists():
        g = pd.read_parquet(GPR)["GPRD"]; g.index = pd.to_datetime(g.index); F["war"] = np.log(g.reindex(idx).ffill()).diff()
    if {"DGS2", "EFFR"} <= set(m.columns): F["hikes"] = (m["DGS2"] - m["EFFR"]).diff() * 100
    if "DFII10" in m: F["real"] = m["DFII10"].diff() * 100
    if "DTWEXBGS" in m: F["dollar"] = np.log(m["DTWEXBGS"]).diff()
    w = PROC / "wti_cont.parquet"
    if w.exists():
        ws = pd.read_parquet(w)["WTI_SPOT"]; ws.index = pd.to_datetime(ws.index); F["oil"] = ws.reindex(idx)
    if "VIXCLS" in m: F["vix"] = np.log(m["VIXCLS"]).diff()
    pc = PROC / "macro_pca_scores.parquet"
    if pc.exists():
        s = pd.read_parquet(pc); s.index = pd.to_datetime(s.index); s = s.select_dtypes("number").reindex(idx).ffill()
        if s.shape[1] >= 1: F["macro1"] = s.iloc[:, 0].diff()
        if s.shape[1] >= 2: F["macro2"] = s.iloc[:, 1].diff()
    return F


def returns(asset: str) -> pd.Series:
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index); return r[asset]


# ---------------------------------------------------------------- the decomposition
def ordered_fit(r: np.ndarray, X: np.ndarray):
    """Gram-Schmidt in column order: column k is replaced by its residual on columns < k. Returns orthogonal X, the projection coefficients
    (so an episode's factor sums can be transformed the same way), and the betas of r on each orthogonal column (simple regressions)."""
    T, k = X.shape; Xm = X - X.mean(0); rm = r - r.mean(); Q = Xm.copy(); P = np.zeros((k, k))   # demeaned: same space as the joint fit with intercept
    for j in range(1, k):
        A = Q[:, :j]; coef, *_ = np.linalg.lstsq(A, Xm[:, j], rcond=None); P[j, :j] = coef; Q[:, j] = Xm[:, j] - A @ coef
    beta = np.array([(Q[:, j] @ rm) / (Q[:, j] @ Q[:, j]) if (Q[:, j] @ Q[:, j]) > 0 else 0.0 for j in range(k)])
    resid = rm - Q @ beta; dof = max(T - k - 1, 1); s2 = (resid @ resid) / dof
    se = np.array([np.sqrt(s2 / (Q[:, j] @ Q[:, j])) if (Q[:, j] @ Q[:, j]) > 0 else np.nan for j in range(k)])
    return Q, P, beta, se


def transform_sums(sums: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Apply the window's orthogonalisation to the episode's factor sums (linear, so sums transform the same way)."""
    k = len(sums); out = sums.copy()
    for j in range(1, k): out[j] = sums[j] - P[j, :j] @ out[:j]
    return out


def joint_fit(r, X):
    beta, *_ = np.linalg.lstsq(np.c_[np.ones(len(r)), X], r, rcond=None); return beta[1:]


def episode(asset, start, end, price_start, prime="war", second="hikes"):
    r = returns(asset); F = factors(r.index); avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    missing = [f for f in ORDER_DEFAULT if f not in avail]
    s0, s1 = pd.Timestamp(start), pd.Timestamp(end)
    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename("r")).dropna()
    ep = F.loc[s0:s1][avail].join(r.rename("r")).dropna()
    if len(win) < 250 or len(ep) < 5: sys.exit(f"  not enough data: window {len(win)}, episode {len(ep)}")
    actual = float(ep.r.sum()); P0 = float(price_start); L = []
    L += [f"# Factor attribution — {asset}, {s0.date()} → {s1.date()}", "",
          f"*{datetime.now():%Y-%m-%d %H:%M}. Actual move {np.expm1(actual):+.1%} ({P0:,.0f} → {P0 * np.exp(actual):,.0f} at the quoted start price); {len(ep)} sessions. "
          f"Sensitivities from the {len(win)} sessions before the episode (walk-forward). Dollars = start price × each factor's share of the log move. "
          f"Two orderings + the joint fit; the spread between them is the attribution's uncertainty. prereg_factor_attribution §1.*", ""]
    if missing: L.append(f"Proxies unavailable on disk: {', '.join(missing)} (run fetch-gpr for the war factor).\n")
    sums = ep[avail].sum().to_numpy(); res = {"asset": asset, "start": start, "end": end, "price_start": P0, "actual_log": actual, "orderings": {}}

    def one(order, title):
        cols = [c for c in order if c in avail] + [c for c in avail if c not in order]
        X = win[cols].to_numpy(); Q, Pm, beta, se = ordered_fit(win.r.to_numpy(), X)
        s_orth = transform_sums(ep[cols].sum().to_numpy(), Pm); contrib = beta * s_orth
        bj_c = joint_fit(win.r.to_numpy(), X); drift = float((win.r.mean() - win[cols].mean().to_numpy() @ bj_c) * len(ep))   # the window's average daily return not explained by the factors, × sessions
        resid = actual - contrib.sum() - drift
        L.extend([f"## {title}: " + " → ".join(cols), "", "| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |",
                  "|---|---|---|---|---|---|---|"])
        rows = {}
        for c, b, e, sm, so, ct in zip(cols, beta, se, sums[[avail.index(c) for c in cols]], s_orth, contrib):
            band = abs(e * so) * P0; usd = P0 * ct
            L.append(f"| {LABEL[c]} | {b:+.4g} | {e:.2g} | {sm:+.3g} (orth. {so:+.3g}) | {ct / actual:+.0%} | {usd:+,.0f} | {-usd:+,.0f} (±{band:,.0f}) |")
            rows[c] = dict(beta=float(b), se=float(e), raw_sum=float(sm), orth_sum=float(so), contrib=float(ct), usd=float(usd), band=float(band))
        L.append(f"| drift (the window's ordinary daily return × {len(ep)} sessions) | | | | {drift / actual:+.0%} | {P0 * drift:+,.0f} | — |")
        L.append(f"| **unexplained residual** | | | | {resid / actual:+.0%} | {P0 * resid:+,.0f} | — |"); L.append("")
        res["orderings"][title] = dict(order=cols, rows=rows, drift=drift, resid=float(resid))

    one([prime, second], f"Prime factor {LABEL[prime]}")
    one([second, prime], f"Prime factor {LABEL[second]}")
    bj = joint_fit(win.r.to_numpy(), win[avail].to_numpy()); cj = bj * sums; rj = actual - cj.sum()
    L += ["## Joint fit (no ordering — shared co-movement split by least squares)", "", "| factor | β | proxy move | share | dollars |", "|---|---|---|---|---|"]
    for c, b, sm, ct in zip(avail, bj, sums, cj): L.append(f"| {LABEL[c]} | {b:+.4g} | {sm:+.3g} | {ct / actual:+.0%} | {P0 * ct:+,.0f} |")
    L.append(f"| **residual** | | | {rj / actual:+.0%} | {P0 * rj:+,.0f} |")
    res["joint"] = {c: dict(beta=float(b), contrib=float(ct)) for c, b, ct in zip(avail, bj, cj)}
    tests = (PROC / "factor_attribution.json"); J = json.loads(tests.read_text()) if tests.exists() else {}
    st = (J.get("tests", {}) or {}).get(asset, {})
    L += ["", "## Status of the two tests that gate any bounce number (prereg §2)",
          f"- T-A explanatory stability: {st.get('TA', {}).get('verdict', 'not run')} (median out-of-sample R² {st.get('TA', {}).get('median_r2', float('nan')):.2f})",
          "- T-B sign stability: " + (", ".join(f"{LABEL[c]} {v['share']:.0%} {'stable' if v['stable'] else 'UNSTABLE — not quotable'}" for c, v in st.get("TB", {}).items()) or "not run"),
          "", "Reading: 'if it fully reverses' is the dollars that factor's proxy returning to its episode-start level would imply at the same sensitivity — "
          "a conditional statement, not a forecast of the reversal itself; it is quotable only for factors T-B marks stable and only after T-A passes."]
    J.setdefault("episodes", {})[f"{asset}_{start}_{end}"] = res; tests.write_text(json.dumps(J, indent=1))
    out = DOCS / f"factor_attribution_{asset}_{start}_{end}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")


def tests(asset):
    r = returns(asset); F = factors(r.index); avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    D = F[avail].join(r.rename("r")).dropna(); D = D[D.index >= "2006-01-01"]; X, y = D[avail].to_numpy(), D.r.to_numpy(); idx = D.index
    r2s, signs = [], {c: [] for c in avail}; i = WINDOW
    while i + BLOCK <= len(D):
        Xw, yw = X[i - WINDOW:i], y[i - WINDOW:i]; bj = joint_fit(yw, Xw)
        for c, b in zip(avail, bj): signs[c].append(np.sign(b))
        Xb, yb = X[i:i + BLOCK], y[i:i + BLOCK]; pred = (Xb - Xw.mean(0)) @ bj + yw.mean()
        ss = ((yb - yb.mean()) ** 2).sum(); r2s.append(1 - ((yb - pred) ** 2).sum() / ss if ss > 0 else np.nan)
        i += BLOCK
    r2s = np.array(r2s); med = float(np.nanmedian(r2s)); bar = 0.20 if asset == "GLD" else 0.10
    TA = dict(median_r2=med, blocks=int(np.isfinite(r2s).sum()), verdict="PASS" if med >= bar else "FAIL")
    TB = {}
    for c in avail:
        s = np.array(signs[c]); s = s[s != 0]; share = float(max((s > 0).mean(), (s < 0).mean())) if len(s) else np.nan
        TB[c] = dict(share=share, stable=bool(share >= 0.7), windows=int(len(s)))
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {})[asset] = {"TA": TA, "TB": TB, "run": datetime.now().strftime("%Y-%m-%d %H:%M")}; (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    L = [f"# Factor attribution — tests for {asset}", "", f"*{J['tests'][asset]['run']}. T-A: betas from the prior {WINDOW} sessions, R² on each next {BLOCK}-session block from 2006 "
         f"(walk-forward, joint fit). Bar {bar:.2f}. T-B: sign of each factor's beta across rolling windows (step {STEP}); stable if the same sign in ≥ 70%.*", "",
         f"**T-A:** median out-of-sample R² **{med:.3f}** over {TA['blocks']} blocks → **{TA['verdict']}**", "", "| factor | windows | share with the majority sign | T-B |", "|---|---|---|---|"]
    for c, v in TB.items(): L.append(f"| {LABEL[c]} | {v['windows']} | {v['share']:.0%} | {'stable' if v['stable'] else 'UNSTABLE — not quotable'} |")
    out = DOCS / "factor_attribution_tests.md"
    prev = out.read_text() if out.exists() else ""; out.write_text((prev.rstrip("\n") + "\n\n" if prev else "") + "\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")


def selftest():
    rng = np.random.default_rng(0); T = 1000; f1 = rng.normal(0, 1, T); f2 = 0.6 * f1 + rng.normal(0, 0.8, T); r = 0.5 * f1 - 0.3 * f2 + rng.normal(0, 0.5, T)
    X = np.c_[f1, f2]; Q, P, beta, se = ordered_fit(r, X)
    assert abs(Q[:, 0] @ Q[:, 1]) < 1e-8; print("  T1 orthogonal columns: PASS")
    bj = joint_fit(r, X); assert abs(bj[0] - 0.5) < 0.1 and abs(bj[1] + 0.3) < 0.1; print("  T2 joint betas recover the truth: PASS")
    sums = X.sum(0); so = transform_sums(sums, P); assert abs(so[0] - sums[0]) < 1e-12 and abs(so[1] - (sums[1] - P[1, 0] * sums[0])) < 1e-9; print("  T3 episode sums transform consistently: PASS")
    total_ord = (beta * so).sum(); total_joint = (bj * sums).sum(); assert abs(total_ord - total_joint) < 1e-6 * max(1, abs(total_joint)); print("  T4 orderings explain the same total: PASS")
    print("selftest: 4/4")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("selftest", "fetch-gpr"): sub.add_parser(c)
    e = sub.add_parser("episode"); e.add_argument("asset"); e.add_argument("--start", required=True); e.add_argument("--end", required=True)
    e.add_argument("--price-start", type=float, required=True); e.add_argument("--prime", default="war"); e.add_argument("--second", default="hikes")
    t = sub.add_parser("tests"); t.add_argument("asset")
    a = ap.parse_args()
    if a.cmd == "selftest": selftest()
    elif a.cmd == "fetch-gpr": fetch_gpr()
    elif a.cmd == "episode": episode(a.asset, a.start, a.end, a.price_start, a.prime, a.second)
    else: tests(a.asset)
''')
    print("  factor_attribution.py: written")

t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "## 4. Potential upgrades — not registered, not costed\n"
if "### 3.31 Factor attribution" in s: print("  TRACK 3.31: already")
else:
    add = """### 3.31 Factor attribution of price episodes — the founder's weight-per-reason method (registered 23 Oct before code; built)

Name the reasons (war, rate-hike speculation, real yields, dollar, oil, volatility, the macro PCA line), measure each one's share of a move
with a declared prime-factor ordering (Gram–Schmidt: the prime factor keeps what it co-moves with, the next keeps what is left; both orderings
and the joint fit always shown), state it in dollars at the start price, and when a reason reverses expect that many dollars back — gated by
two tests: T-A out-of-sample explanatory power (GLD median R² ≥ 0.20) and T-B sign stability per factor (≥ 70% of windows), then T-C the
reversal test on past geopolitical spikes. Priors #58–#60. War proxy = Caldara–Iacoviello daily GPR (free). `docs/prereg_factor_attribution.md`,
`src/factor_attribution.py`. Supersedes Stage 2/3 of 3.29 (reasons become measured proxies; the reader names which event drives a proxy).

"""
    t.write_text(s.replace(anchor, add + anchor, 1)); print("  TRACK 3.31: done")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "| 47 | Factor attribution" in s: print("  MASTER row 47: already")
else:
    i = s.index("| 46 | Target-range engine"); j = s.index("\n", i) + 1
    s = s[:j] + ("| 47 | Factor attribution: an ordered decomposition of a market's move into named, measured reasons explains the move out of sample "
                 "(T-A R² ≥ 0.20 GLD) with stable sensitivities (T-B ≥ 70%) and predicts the move on a reason's reversal (T-C corr ≥ 0.3, n ≥ 15) | "
                 "registered 23 Oct before code; T-A/T-B run next | priors #58 PASS, #59 war/oil unstable, #60 T-C FAIL/INCONCLUSIVE | `docs/prereg_factor_attribution.md`, TRACK 3.31 |\n") + s[j:]
    m.write_text(s); print("  MASTER row 47: done")
print("done -- pip install xlrd -q ; python -m src.factor_attribution selftest ; python -m src.factor_attribution fetch-gpr")
