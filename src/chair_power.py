"""T-K0/T-K1/T-K1'/T-K2: the few-shot chair problem. Statement-day reaction of GLD (and TLT) to the 2-yr-yield surprise by chair; power of a per-chair
coefficient; chair x surprise interaction with a permutation null, in basis points (T-K1) and in units of the yield's own trailing volatility (T-K1');
empirical-Bayes posterior for the current chair, per bp and (v3) in volatility units -- the scale on which chairs are exchangeable.
docs/prereg_liquidity_and_chair.md section 3.    python -m src.chair_power run ; python -m src.chair_power record"""
from __future__ import annotations
import json, re, sys
from datetime import datetime
from math import comb
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
CHAIRS = [("Bernanke", "2006-02-01", "2014-01-31"), ("Yellen", "2014-02-03", "2018-02-03"), ("Powell", "2018-02-05", "2026-05-15"), ("Warsh", "2026-05-22", "2099-12-31")]
MIN_N, NPERM, SEED, Z, VOLWIN = 20, 2000, 0, 1.96 + 0.84, 504


def chair_of(d: pd.Timestamp) -> str:
    for name, a, b in CHAIRS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def table() -> pd.DataFrame:
    dates = pd.to_datetime(pd.read_csv(PROC / "fomc_decisions.csv")["date"]); dates = dates[dates <= pd.Timestamp.today().normalize()]
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); ds = m["DGS2"].dropna().diff() * 100
    vol = ds.rolling(VOLWIN, min_periods=250).std().shift(1); s = ds.reindex(r.index); v = vol.reindex(r.index).ffill()
    rows = [dict(date=d, chair=chair_of(d), s=s.get(d, np.nan), vol=v.get(d, np.nan), gld=r["GLD"].get(d, np.nan), tlt=(r["TLT"].get(d, np.nan) if "TLT" in r.columns else np.nan)) for d in dates]
    df = pd.DataFrame(rows).dropna(subset=["s", "gld"]); df["s_norm"] = df["s"] / df["vol"]; return df


def ols(x, y):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx if sxx > 0 else np.nan; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); return float(a), float(b), float(np.sqrt(s2 / sxx)) if sxx > 0 else np.nan, e, float(sxx)


def interaction_F(df: pd.DataFrame, col: str, labels: np.ndarray, xcol: str = "s") -> float:
    y = df[col].to_numpy(); s = df[xcol].to_numpy(); groups = sorted(set(labels)); n = len(y)
    D = np.column_stack([(labels == g).astype(float) for g in groups]); Xr = np.column_stack([D, s]); Xf = np.column_stack([D, D * s[:, None]])
    def rss(X): c, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ c; return float(e @ e)
    rf, rr = rss(Xf), rss(Xr); kf, kr = Xf.shape[1], Xr.shape[1]; return ((rr - rf) / (kf - kr)) / (rf / max(n - kf, 1))


def perm_p(sub, col, lab, xcol, rng):
    F = interaction_F(sub, col, lab, xcol); null = np.array([interaction_F(sub, col, rng.permutation(lab), xcol) for _ in range(NPERM)]); return F, float((null >= F).mean())


def posterior(b_pool: float, b_own: float, se_pooled: float, tau2: float) -> tuple[float, float, float]:
    w = tau2 / (tau2 + se_pooled ** 2) if tau2 > 0 else 0.0; mean = b_pool + w * (b_own - b_pool); sd = (1 / tau2 + 1 / se_pooled ** 2) ** -0.5 if tau2 > 0 else 0.0; return float(w), float(mean), float(sd)


def run():
    df = table(); n = len(df); a, b, se, e, _ = ols(df.s.to_numpy(), df.gld.to_numpy()); sigma = float(e.std(ddof=2)); var_s = float(df.s.var())
    dn = df.dropna(subset=["s_norm"]); _, bn, sen, en, _ = ols(dn.s_norm.to_numpy(), dn.gld.to_numpy()); sigma_n = float(en.std(ddof=2))
    per = []
    for name, _, _ in CHAIRS:
        g = df[df.chair == name]; gn = g.dropna(subset=["s_norm"])
        row = dict(chair=name, n=int(len(g)), mean_s=float(g.s.mean()) if len(g) else np.nan, sd_s=float(g.s.std()) if len(g) > 1 else np.nan, mean_gld=float(g.gld.mean()) if len(g) else np.nan,
                   beta=np.nan, se=np.nan, sxx=np.nan, se_pooled=np.nan, beta_norm=np.nan, se_norm=np.nan, sxx_norm=np.nan, se_norm_pooled=np.nan, mean_vol=float(g.vol.mean()) if len(g) else np.nan)
        if len(g) >= 3:
            _, bc, sec, _, sxx = ols(g.s.to_numpy(), g.gld.to_numpy()); row.update(beta=bc, se=sec, sxx=sxx, se_pooled=float(sigma / np.sqrt(sxx)) if sxx > 0 else np.nan)
        if len(gn) >= 3:
            _, bcn, secn, _, sxxn = ols(gn.s_norm.to_numpy(), gn.gld.to_numpy()); row.update(beta_norm=bcn, se_norm=secn, sxx_norm=sxxn, se_norm_pooled=float(sigma_n / np.sqrt(sxxn)) if sxxn > 0 else np.nan)
        per.append(row)
    P = pd.DataFrame(per); big = P[P.n >= MIN_N]
    tau2 = float(max(0.0, big.beta.var(ddof=1) - (big.se ** 2).mean())) if len(big) >= 2 else 0.0
    bigN = big[big.beta_norm.notna()]; tau2n = float(max(0.0, bigN.beta_norm.var(ddof=1) - (bigN.se_norm ** 2).mean())) if len(bigN) >= 2 else 0.0
    need = {f"delta = beta/{k}": (Z ** 2) * sigma ** 2 / ((abs(b) / k) ** 2 * var_s) if b != 0 else np.nan for k in (2, 1)}
    sub = df[df.chair.isin(big.chair)].dropna(subset=["s_norm"]).reset_index(drop=True); lab = sub.chair.to_numpy(); rng = np.random.default_rng(SEED)
    F_obs, p_gld = perm_p(sub, "gld", lab, "s", rng); F_norm, p_norm = perm_p(sub, "gld", lab, "s_norm", rng)
    F_tlt, p_tlt = (perm_p(sub, "tlt", lab, "s", rng) if sub.tlt.notna().all() else (np.nan, np.nan))
    cur = P.iloc[-1]; post = None
    if np.isfinite(cur.se_pooled):
        w, mean, sd = posterior(b, cur.beta, cur.se_pooled, tau2); w_own = tau2 / (tau2 + cur.se ** 2) if (tau2 > 0 and np.isfinite(cur.se)) else 0.0
        post = dict(chair=cur.chair, n=int(cur.n), beta_hat=float(cur.beta), se_own=float(cur.se), se_pooled=float(cur.se_pooled), weight_on_own=w, weight_if_own_se=float(w_own), posterior_mean=mean, posterior_sd=sd,
                    explained_by_pooled_slope=float(b * cur.mean_s), mean_gld=float(cur.mean_gld))
        if np.isfinite(cur.se_norm_pooled):
            wn, mn, sdn = posterior(bn, cur.beta_norm, cur.se_norm_pooled, tau2n); vol_now = float(cur.mean_vol)
            post.update(sigma_units=dict(beta_hat=float(cur.beta_norm), se_pooled=float(cur.se_norm_pooled), tau=float(np.sqrt(tau2n)), weight_on_own=wn, posterior_mean=mn, posterior_sd=sdn, vol_now_bp=vol_now,
                                         posterior_per_bp=(mn / vol_now if vol_now > 0 else np.nan), posterior_sd_per_bp=(sdn / vol_now if vol_now > 0 else np.nan)))
    min_p = {k: 1 / comb(k + 8, k) for k in (3, 4, 5, 6, 8)}
    v1 = "PASS — chairs differ per bp" if p_gld < 0.05 else "FAIL — no detectable chair difference"; v1n = "PASS — chairs still differ in volatility units" if p_norm < 0.05 else "FAIL — no chair difference once the surprise is in volatility units"
    L = [f"# T-K — the few-shot chair problem (GLD on the 2-yr surprise, statement days)", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} statement days {df.date.min().date()} → {df.date.max().date()}; s = ΔDGS2 bp on the day, s/σ = the same in units of the yield's trailing two-year daily volatility; y = GLD log return on the day (%). prereg_liquidity_and_chair §3.*", "",
         f"**Pooled:** β = {b * 100:+.4f}% per bp (se {se * 100:.4f}); in volatility units β = {bn * 100:+.3f}% per σ (se {sen * 100:.3f}); residual σ = {sigma * 100:.2f}% a day; sd of the surprise {np.sqrt(var_s):.1f} bp.", "",
         "| chair | statements | mean surprise (bp) | sd (bp) | yield vol (bp/day) | mean GLD day (%) | β (% per bp) | se (own) | β (% per σ) | se |", "|---|---|---|---|---|---|---|---|---|---|"]
    for q in P.itertuples():
        f = lambda v, fmt: (fmt % v) if np.isfinite(v) else "—"
        L.append(f"| {q.chair} | {q.n} | {f(q.mean_s, '%+.1f')} | {f(q.sd_s, '%.1f')} | {f(q.mean_vol, '%.1f')} | {f(q.mean_gld * 100, '%+.2f')} | {f(q.beta * 100, '%+.4f')} | {f(q.se * 100, '%.4f')} | {f(q.beta_norm * 100, '%+.3f')} | {f(q.se_norm * 100, '%.3f')} |")
    L += ["", "**T-K0 power:** meetings needed to detect a chair-specific difference at α 5%, power 80% — " + "; ".join(f"{k}: **{v:,.0f}**" for k, v in need.items()) + ". A tenure is 8 meetings a year; a four-year term 32.", "",
          f"**T-K1 chairs differ (per bp)?** F = {F_obs:.2f} among {', '.join(big.chair)}; permutation p = **{p_gld:.3f}** → **{v1}**; between-chair τ = {np.sqrt(tau2) * 100:.4f}% per bp" + (f"; TLT cross-check F = {F_tlt:.2f}, p = {p_tlt:.3f}" if np.isfinite(p_tlt) else "") + ".", "",
          f"**T-K1′ chairs differ (per σ of the yield)?** F = {F_norm:.2f}; permutation p = **{p_norm:.3f}** → **{v1n}**; between-chair τ in these units {np.sqrt(tau2n) * 100:.3f}% per σ.", ""]
    if post:
        L += [f"**T-K2 {post['chair']} so far ({post['n']} statements), per bp:** own slope {post['beta_hat'] * 100:+.4f}% per bp; standard error from the pooled residual σ {post['se_pooled'] * 100:.4f} (the own 1-dof se was {post['se_own'] * 100:.4f}); weight on own data **{post['weight_on_own']:.0%}** (would be {post['weight_if_own_se']:.0%} on the own se); posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f} per bp. "
              f"His statement days averaged {post['mean_gld'] * 100:+.2f}% on gold; the pooled slope times his average surprise gives {post['explained_by_pooled_slope'] * 100:+.2f}% — " + ("most of it: gold fell on his days because the statements surprised hawkish, not because gold reacts to him differently." if abs(post['explained_by_pooled_slope']) > 0.5 * abs(post['mean_gld']) else "less than half of it."), ""]
        su = post.get("sigma_units")
        if su: L += [f"**T-K2σ in volatility units (the scale on which chairs are exchangeable, T-K1′):** own {su['beta_hat'] * 100:+.3f}% per σ, pooled-σ se {su['se_pooled'] * 100:.3f}, between-chair τ {su['tau'] * 100:.3f}; weight on own data **{su['weight_on_own']:.0%}**; posterior **{su['posterior_mean'] * 100:+.3f}% ± {su['posterior_sd'] * 100:.3f} per σ**, i.e. about {su['posterior_per_bp'] * 100:+.4f}% ± {su['posterior_sd_per_bp'] * 100:.4f} per bp at today's yield volatility ({su['vol_now_bp']:.1f} bp a day). **The page quotes this one.**", ""]
    L += ["**T-K3 (not run):** smallest attainable exact-permutation p for n statements against the previous chair's last 8 — " + ", ".join(f"n = {k}: {v:.4f}" for k, v in min_p.items()) + "."]
    out = DOCS / "chair_power.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")
    J = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, beta=b, se=se, beta_norm=bn, se_norm=sen, sigma=sigma, sigma_norm=sigma_n, var_s=var_s, chairs=per, tau2=tau2, tau2_norm=tau2n, need=need,
             TK1=dict(F=F_obs, p=p_gld, F_tlt=F_tlt, p_tlt=p_tlt, verdict=v1), TK1n=dict(F=F_norm, p=p_norm, verdict=v1n), TK2=post, min_p=min_p)
    (PROC / "chair_power.json").write_text(json.dumps(J, indent=1, default=float))


def _bump_tally(text: str, note: str) -> str:
    if note in text: return text
    m = re.search(r"tally (\d+) \(#40–#43 lever priors", text)
    if not m: return text
    k = int(m.group(1)) + 1; text = text.replace(m.group(0), f"tally {k} (#40–#43 lever priors", 1)
    anchor = "#78 chairs differ (p 0.016)"; return text.replace(anchor, anchor + ", " + note, 1) if anchor in text else text


def _replace_line(text: str, pattern: str, new: str) -> tuple[str, bool]:
    m = re.search(pattern, text, flags=re.M); return (text[:m.start()] + new + text[m.end():], True) if m else (text, False)


def record():
    """Write T-K1' against prior #81 and the posteriors into the register, the pre-registration and the state record; replaces rows written earlier."""
    J = json.loads((PROC / "chair_power.json").read_text()); k1n, post = J["TK1n"], J["TK2"]
    right81 = k1n["p"] > 0.05; pri = "**#81 right**" if right81 else "**#81 wrong** (chairs still differ in volatility units)"
    rows = {c["chair"]: c for c in J["chairs"]}; per_sigma = ", ".join(f"{c} {rows[c]['beta_norm'] * 100:+.2f}" for c in ("Bernanke", "Yellen", "Powell") if c in rows and np.isfinite(rows[c].get("beta_norm", np.nan)))
    res = (f"T-K1′: interaction F {k1n['F']:.2f}, permutation p {k1n['p']:.3f} → {k1n['verdict']}; β per σ of the yield — {per_sigma}% (per bp they were {rows['Bernanke']['beta'] * 100:+.3f}, {rows['Yellen']['beta'] * 100:+.3f}, {rows['Powell']['beta'] * 100:+.3f})")
    if post:
        res += f". T-K2 per bp with the pooled-σ se: {post['chair']} weight on own data {post['weight_on_own']:.0%} (was {post['weight_if_own_se']:.0%}), posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f} per bp"
        su = post.get("sigma_units")
        if su: res += (f". T-K2σ in volatility units, the scale on which chairs are exchangeable: weight on own data {su['weight_on_own']:.0%}, posterior {su['posterior_mean'] * 100:+.3f}% ± {su['posterior_sd'] * 100:.3f} per σ "
                       f"(≈ {su['posterior_per_bp'] * 100:+.4f}% per bp at today's {su['vol_now_bp']:.1f} bp/day) — the page quotes this one")
    stamp = datetime.now().strftime("%Y-%m-%d")
    p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text(); row = f"| {stamp} | T-K1′ and T-K2 (pooled σ, volatility units) | {res}. docs/chair_power.md | {pri} |"
    s, done = _replace_line(s, r"^\| \d{4}-\d{2}-\d{2} \| T-K1′ and T-K2 \(pooled σ.*$", row)
    if not done: s = s.rstrip("\n") + "\n" + row + "\n"
    p.write_text(s); print("  prereg: T-K1′ row " + ("replaced" if done else "added"))
    m = DOCS / "PROJECT_MASTER.md"; s = m.read_text(); txt = f"{res} ({pri.replace('**', '')})."
    lines = s.split("\n")
    for i, ln in enumerate(lines):      # row 52: line-wise, so the replacement can never run across other rows or sections
        if ln.startswith("| 52 |"): lines[i] = re.sub(r"T-K1′: interaction F .*? T-K3 next \|", lambda _: txt + " T-K3 next |", ln, count=1)
    s2 = "\n".join(lines).replace("[T-K1′: registered, result to be written by `chair_power record`.]", txt, 1)
    mb = re.search(r"re-asked in volatility units: (.*?) Warsh's three statement days", s2, flags=re.S)   # Block 9: one paragraph; refuse a match that crosses a blank line
    if mb and "\n\n" not in mb.group(1): s2 = s2[:mb.start()] + "re-asked in volatility units: " + txt + " Warsh's three statement days" + s2[mb.end():]
    if not right81: s2 = _bump_tally(s2, "#81 chairs in volatility units")
    m.write_text(s2); print("  MASTER: row 52 and Block 9 " + ("updated" if s2 != s else "unchanged (anchors not found)"))
    cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text(); line = f"T-K1′ result ({datetime.now():%d %b}): {res}. {pri.replace('**', '')}."
    s, done = _replace_line(s, r"^T-K1′ result \(.*$", line)
    if not done: s = s.rstrip("\n") + "\n\n" + line + "\n"
    cs.write_text(s); print("  CURRENT_STATE: T-K1′ line " + ("replaced" if done else "added"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run()
    elif cmd == "record": record()
    elif cmd == "table": print(table().tail(12))
