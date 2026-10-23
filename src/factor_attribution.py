"""
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
ORDER_DEFAULT = ["war", "hikes", "real", "dollar", "oil", "vix", "btc", "macro1", "macro2"]
LABEL = {"war": "geopolitical risk (GPR index)", "hikes": "rate-hike speculation (2-yr yield minus fed funds)", "real": "real 10-yr yield",
         "dollar": "US dollar (broad index)", "oil": "oil (WTI spot)", "vix": "equity volatility (VIX)", "macro1": "macro state, PCA line 1",
         "macro2": "macro state, PCA line 2", "btc": "speculative liquidity (Bitcoin)"}


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
    bp = PROC / "btc_daily.parquet"
    if not bp.exists():
        try:
            import yfinance as yf
            b = yf.Ticker("BTC-USD").history(period="max", interval="1d")["Close"]; b.index = pd.to_datetime(b.index).tz_localize(None).normalize(); b.to_frame("BTC").to_parquet(bp)
        except Exception as e: print(f"  BTC fetch failed: {type(e).__name__}: {str(e)[:80]}")
    if bp.exists():
        b = pd.read_parquet(bp)["BTC"]; b.index = pd.to_datetime(b.index); F["btc"] = np.log(b.reindex(idx).ffill()).diff()
    pc = PROC / "macro_pca_scores.parquet"
    if pc.exists():
        s = pd.read_parquet(pc); s.index = pd.to_datetime(s.index); s = s.select_dtypes("number").reindex(idx).ffill()
        if s.shape[1] >= 1: F["macro1"] = s.iloc[:, 0].diff()
        if s.shape[1] >= 2: F["macro2"] = s.iloc[:, 1].diff()
    return F


EXTRA = {"SLV": "SLV", "SILVER": "SI=F", "GOLD": "GC=F", "COPPER": "HG=F", "BRENT": "BZ=F"}


def returns(asset: str) -> pd.Series:
    """Daily log returns: the panel's assets, or an extra instrument (silver etc.) fetched once from Yahoo into processed/extra_returns.parquet."""
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if asset in r.columns: return r[asset]
    cache = PROC / "extra_returns.parquet"; ex = pd.read_parquet(cache) if cache.exists() else pd.DataFrame()
    if cache.exists(): ex.index = pd.to_datetime(ex.index)
    if asset not in ex.columns or (len(ex) and (r.index[-1] - ex[asset].dropna().index[-1]).days > 3):
        import yfinance as yf
        h = yf.Ticker(EXTRA.get(asset, asset)).history(period="max", interval="1d", auto_adjust=True)["Close"]
        h.index = pd.to_datetime(h.index).tz_localize(None).normalize(); lr = np.log(h).diff().rename(asset)
        ex = ex.drop(columns=[asset], errors="ignore").join(lr, how="outer") if len(ex) else lr.to_frame(); ex.to_parquet(cache)
    return ex[asset].reindex(r.index)


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
    s1 = pd.Timestamp(end)
    if str(start) == "peak":                      # the episode's own peak: highest cumulative level in the 300 sessions before the end
        cum = r.loc[:s1].cumsum().iloc[-300:]; s0 = cum.idxmax(); start = s0.strftime("%Y-%m-%d"); print(f"  peak found: {start}")
    else: s0 = pd.Timestamp(start)
    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename("r")).dropna()
    ep = F.loc[s0:s1][avail].join(r.rename("r")).dropna()
    if len(win) < 250 or len(ep) < 5: sys.exit(f"  not enough data: window {len(win)}, episode {len(ep)}")
    actual = float(ep.r.sum()); P0 = float(price_start); L = []
    L += [f"# Factor attribution — {asset}, {s0.date()} → {s1.date()}", "",
          f"*{datetime.now():%Y-%m-%d %H:%M}. Actual move {np.expm1(actual):+.1%} ({P0:,.0f} → {P0 * np.exp(actual):,.0f} at the quoted start price); {len(ep)} sessions. "
          f"Sensitivities from the {len(win)} sessions before the episode (walk-forward). Dollars = start price × each factor's share of the log move. "
          f"Two orderings + the joint fit; the spread between them is the attribution's uncertainty. prereg_factor_attribution §1.*", ""]
    if missing: L.append(f"Proxies unavailable on disk: {', '.join(missing)}.\n")
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


BLOCKS_GRID = (1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60)
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
    J.setdefault("tests", {}).setdefault(asset, {}).update(rec); (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))   # merge: T-E/T-F/T-G records survive
    out = DOCS / "factor_attribution_tests.md"; prev = out.read_text() if out.exists() else ""
    out.write_text((prev.rstrip("\n") + "\n\n" if prev else "") + "\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")


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
    t = sub.add_parser("tests"); t.add_argument("asset"); t.add_argument("--sweep", action="store_true"); t.add_argument("--null", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "selftest": selftest()
    elif a.cmd == "fetch-gpr": fetch_gpr()
    elif a.cmd == "episode": episode(a.asset, a.start, a.end, a.price_start, a.prime, a.second)
    else: tests(a.asset, sweep=a.sweep, n_null=a.null)
