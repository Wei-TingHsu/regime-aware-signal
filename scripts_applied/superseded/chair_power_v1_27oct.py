"""T-K0/T-K1/T-K2: the few-shot chair problem. Statement-day reaction of GLD (and TLT) to the 2-yr-yield surprise, by chair; power of a per-chair
coefficient; chair x surprise interaction with a permutation null; empirical-Bayes posterior for the current chair.
docs/prereg_liquidity_and_chair.md section 3.   python -m src.chair_power run"""
from __future__ import annotations
import json, sys
from datetime import datetime
from math import comb
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
CHAIRS = [("Bernanke", "2006-02-01", "2014-01-31"), ("Yellen", "2014-02-03", "2018-02-03"), ("Powell", "2018-02-05", "2026-05-15"), ("Warsh", "2026-05-22", "2099-12-31")]
MIN_N, NPERM, SEED, Z = 20, 2000, 0, 1.96 + 0.84   # alpha 5% two-sided, power 80%


def chair_of(d: pd.Timestamp) -> str:
    for name, a, b in CHAIRS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def table() -> pd.DataFrame:
    dates = pd.to_datetime(pd.read_csv(PROC / "fomc_decisions.csv")["date"]); dates = dates[dates <= pd.Timestamp.today().normalize()]
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); s = (m["DGS2"].diff() * 100).reindex(r.index)
    rows = [dict(date=d, chair=chair_of(d), s=s.get(d, np.nan), gld=r["GLD"].get(d, np.nan), tlt=(r["TLT"].get(d, np.nan) if "TLT" in r.columns else np.nan)) for d in dates]
    df = pd.DataFrame(rows).dropna(subset=["s", "gld"]); return df


def ols(x, y):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx if sxx > 0 else np.nan; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); return float(a), float(b), float(np.sqrt(s2 / sxx)) if sxx > 0 else np.nan, e


def interaction_F(df: pd.DataFrame, col: str, labels: np.ndarray) -> float:
    """F for chair x surprise slopes (full: own intercept and slope per chair) against a common slope with own intercepts."""
    y = df[col].to_numpy(); s = df["s"].to_numpy(); groups = sorted(set(labels)); n = len(y)
    D = np.column_stack([(labels == g).astype(float) for g in groups]); Xr = np.column_stack([D, s]); Xf = np.column_stack([D, D * s[:, None]])
    def rss(X): c, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ c; return float(e @ e)
    rf, rr = rss(Xf), rss(Xr); kf, kr = Xf.shape[1], Xr.shape[1]; return ((rr - rf) / (kf - kr)) / (rf / max(n - kf, 1))


def run():
    df = table(); n = len(df); a, b, se, e = ols(df.s.to_numpy(), df.gld.to_numpy()); sigma = float(e.std(ddof=2)); var_s = float(df.s.var())
    per = []
    for name, _, _ in CHAIRS:
        g = df[df.chair == name]
        if len(g) >= 3: _, bc, sec, _ = ols(g.s.to_numpy(), g.gld.to_numpy()); per.append(dict(chair=name, n=int(len(g)), beta=bc, se=sec, mean_s=float(g.s.mean()), sd_s=float(g.s.std()), mean_gld=float(g.gld.mean())))
        else: per.append(dict(chair=name, n=int(len(g)), beta=np.nan, se=np.nan, mean_s=float(g.s.mean()) if len(g) else np.nan, sd_s=np.nan, mean_gld=float(g.gld.mean()) if len(g) else np.nan))
    P = pd.DataFrame(per); big = P[P.n >= MIN_N]
    tau2 = float(max(0.0, big.beta.var(ddof=1) - (big.se ** 2).mean())) if len(big) >= 2 else 0.0
    # T-K0 power: meetings needed to detect delta
    need = {f"delta = beta/{k}": (Z ** 2) * sigma ** 2 / ((abs(b) / k) ** 2 * var_s) if b != 0 else np.nan for k in (2, 1)}
    # T-K1 interaction among the chairs with n >= MIN_N
    sub = df[df.chair.isin(big.chair)].reset_index(drop=True); lab = sub.chair.to_numpy(); rng = np.random.default_rng(SEED)
    F_obs = interaction_F(sub, "gld", lab); null = np.array([interaction_F(sub, "gld", rng.permutation(lab)) for _ in range(NPERM)]); p_gld = float((null >= F_obs).mean())
    p_tlt = np.nan; F_tlt = np.nan
    if sub.tlt.notna().sum() == len(sub):
        F_tlt = interaction_F(sub, "tlt", lab); null_t = np.array([interaction_F(sub, "tlt", rng.permutation(lab)) for _ in range(NPERM)]); p_tlt = float((null_t >= F_tlt).mean())
    # T-K2 posterior for the current chair
    cur = P.iloc[-1]; post = None
    if np.isfinite(cur.se):
        w = tau2 / (tau2 + cur.se ** 2) if tau2 > 0 else 0.0; mean = b + w * (cur.beta - b); sd = (1 / tau2 + 1 / cur.se ** 2) ** -0.5 if tau2 > 0 else 0.0
        post = dict(chair=cur.chair, n=int(cur.n), beta_hat=float(cur.beta), se=float(cur.se), weight_on_own=float(w), posterior_mean=float(mean), posterior_sd=float(sd))
    min_p = {k: 1 / comb(k + 8, k) for k in (3, 4, 5, 6, 8)}
    v1 = "PASS — chairs differ" if p_gld < 0.05 else "FAIL — no detectable chair difference"
    L = [f"# T-K — the few-shot chair problem (GLD on the 2-yr surprise, statement days)", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} statement days {df.date.min().date()} → {df.date.max().date()}; s = ΔDGS2 bp on the day, y = GLD log return on the day (%). prereg_liquidity_and_chair §3.*", "",
         f"**Pooled:** β = {b * 100:+.4f}% per bp (se {se * 100:.4f}), residual σ = {sigma * 100:.2f}% a day, sd of the surprise {np.sqrt(var_s):.1f} bp.", "",
         "| chair | statements | mean surprise (bp) | sd (bp) | mean GLD day (%) | β (% per bp) | se |", "|---|---|---|---|---|---|---|"]
    for q in P.itertuples(): L.append(f"| {q.chair} | {q.n} | {q.mean_s:+.1f} | {q.sd_s:.1f} | {q.mean_gld * 100:+.2f} | {q.beta * 100:+.4f} | {q.se * 100:.4f} |" if np.isfinite(q.beta) else f"| {q.chair} | {q.n} | {q.mean_s:+.1f} | — | {q.mean_gld * 100:+.2f} | — | — |")
    L += ["", f"**T-K0 power:** meetings needed to detect a chair-specific difference at α 5%, power 80% — " + "; ".join(f"{k}: **{v:,.0f}**" for k, v in need.items()) + f". A tenure is 8 meetings a year.", "",
          f"**T-K1 chairs differ?** interaction F = {F_obs:.2f} among {', '.join(big.chair)}; permutation p = **{p_gld:.3f}** → **{v1}**; between-chair τ = {np.sqrt(tau2) * 100:.4f}% per bp" + (f"; TLT cross-check F = {F_tlt:.2f}, p = {p_tlt:.3f}" if np.isfinite(p_tlt) else "") + ".", ""]
    if post: L += [f"**T-K2 {post['chair']} so far ({post['n']} statements):** own estimate {post['beta_hat'] * 100:+.4f}% per bp (se {post['se'] * 100:.4f}); weight the data earns against the pooled prior {post['weight_on_own']:.0%}; posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f}. The page quotes the posterior, not the own estimate.", ""]
    L += ["**T-K3 (not run):** smallest attainable exact-permutation p for n statements against the previous chair's last 8 — " + ", ".join(f"n = {k}: {v:.4f}" for k, v in min_p.items()) + "."]
    out = DOCS / "chair_power.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")
    J = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, beta=b, se=se, sigma=sigma, var_s=var_s, chairs=per, tau2=tau2, need=need, TK1=dict(F=F_obs, p=p_gld, F_tlt=F_tlt, p_tlt=p_tlt, verdict=v1), TK2=post, min_p=min_p)
    (PROC / "chair_power.json").write_text(json.dumps(J, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run()
    elif cmd == "table": print(table().tail(12))
