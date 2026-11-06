"""regime_describe.py -- the regime audit R1-R4 (docs/prereg_regime_audit.md section 2).

  python -m src.regime_describe describe      # R1: the four regimes in words -- mean standardised level of the eight dials, asset returns inside each
  python -m src.regime_describe lag           # R2: how late the live (expanding) labeller confirms a change in the hindsight labels
  python -m src.regime_describe conditioning  # R3: do the labels sharpen the Fed-day reaction, the factor model, the report's calls?
  python -m src.regime_describe kbytime       # R4: at each year-end, which k (3..8) wins on stability / persistence / separation
  python -m src.regime_describe all
Inputs: src.exposure_dial.load_inputs() (idx, rets, expanding labels, posteriors, rf), processed/macro_panel.parquet, asset_extension (hindsight labels
if it exposes them), src.chair_power.table(), src.factor_attribution.factors/returns, the backfill CSV. Outputs docs/regime_<part>.md (+ .json).
Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
DIALS = ["DGS10", "DGS2", "T10Y2Y", "DFII10", "EFFR", "M2SL", "VIXCLS", "DTWEXBGS"]
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
ANN = 252


def inputs():
    import src.exposure_dial as ED
    idx, rets, lab, post, rf = ED.load_inputs(); idx = pd.DatetimeIndex(idx); lab = ED.confirmed_labels(np.asarray(lab))   # v2: the product's confirmed label, not the raw expanding one
    m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); m = m.reindex(idx).ffill()
    return idx, rets, np.asarray(lab), post, m


def hindsight_labels(idx):
    """Full-sample labels if the engine exposes them; else None (R2 then reports only run lengths)."""
    try:
        import asset_extension as AE
        cfg = AE.load_config(); sc, _ = AE.load_data()
        for name in ("regime_labels", "regime_labels_full", "labels_full"):
            if hasattr(AE, name):
                lab = np.asarray(getattr(AE, name)(sc, cfg)); return pd.Series(lab, index=pd.DatetimeIndex(sc.index)).reindex(idx).to_numpy()
    except Exception as e:
        print(f"  hindsight labels unavailable ({type(e).__name__}: {e})")
    return None


# ------------------------------------------------------------------------------------------------ R1
def cmd_describe():
    idx, rets, lab, post, m = inputs(); ok = lab >= 0
    dials = [c for c in DIALS if c in m.columns]; z = (m[dials] - m[dials].mean()) / m[dials].std()
    if "M2SL" in z.columns: z["M2SL"] = ((m["M2SL"].pct_change(252) - m["M2SL"].pct_change(252).mean()) / m["M2SL"].pct_change(252).std())   # M2 as yearly growth, not level
    rows = []
    for g in sorted(set(int(x) for x in lab[ok])):
        mk = ok & (lab == g); r = dict(regime=g, sessions=int(mk.sum()), share=float(mk.mean()))
        runs = np.diff(np.where(np.diff(np.concatenate([[0], mk.astype(int), [0]])) != 0)[0])[::2]; r["median_run"] = float(np.median(runs)) if len(runs) else np.nan; r["n_runs"] = int(len(runs))
        for c in dials: r[c] = float(z.loc[mk, c].mean())
        for a in [x for x in ASSETS if x in rets.columns]:
            x = rets[a].to_numpy()[mk]; x = x[np.isfinite(x)]; r[f"{a}_ret"] = float(x.mean() * ANN) if len(x) else np.nan; r[f"{a}_vol"] = float(x.std(ddof=1) * np.sqrt(ANN)) if len(x) > 2 else np.nan
        rows.append(r)
    tab = pd.DataFrame(rows)
    out = DOCS / "regime_describe.md"
    L = ["# R1 — the four regimes described", "", f"{int(ok.sum()):,} labelled sessions {idx[ok][0].date()} → {idx[ok][-1].date()}. Dials in standard deviations from their 2006–26 mean (M2 as year-on-year growth); asset returns annualised inside the regime.", "",
         "| regime | sessions | share | runs | median run | " + " | ".join(dials) + " |", "|---|---|---|---|---|" + "---|" * len(dials)]
    for _, r in tab.iterrows(): L.append(f"| {r['regime']} | {r['sessions']} | {r['share']:.0%} | {r['n_runs']} | {r['median_run']:.0f} | " + " | ".join(f"{r[c]:+.2f}" for c in dials) + " |")
    L += ["", "| regime | " + " | ".join(f"{a} ret / vol" for a in ASSETS if a in rets.columns) + " |", "|---|" + "---|" * len([a for a in ASSETS if a in rets.columns])]
    for _, r in tab.iterrows(): L.append(f"| {r['regime']} | " + " | ".join(f"{r[f'{a}_ret']:+.1%} / {r[f'{a}_vol']:.0%}" for a in ASSETS if a in rets.columns) + " |")
    L += ["", "A plain-words name for each regime belongs to the founder, written from this table — the engine never had one."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(orient="records", indent=1)); print(tab[["regime", "sessions", "median_run"] + dials].round(2).to_string(index=False)); print(f"-> {out}")


# ------------------------------------------------------------------------------------------------ R2
def cmd_lag():
    idx, rets, lab, post, m = inputs(); hind = hindsight_labels(idx)
    out = DOCS / "regime_lag.md"; L = ["# R2 — how late the live labeller confirms a change", ""]
    live_changes = np.where((lab[1:] != lab[:-1]) & (lab[1:] >= 0) & (lab[:-1] >= 0))[0] + 1
    L += [f"Live (expanding) labels: {len(live_changes)} changes over {int((lab >= 0).sum()):,} labelled sessions; median run {np.median(np.diff(live_changes)):.0f} sessions." if len(live_changes) > 1 else "Live labels: fewer than two changes.", ""]
    res = dict(live_changes=int(len(live_changes)))
    if hind is not None:
        hc = np.where((hind[1:] != hind[:-1]) & np.isfinite(hind[1:]) & np.isfinite(hind[:-1]))[0] + 1; lags = []
        for c in hc:
            later = live_changes[live_changes >= c]; lags.append(int(later[0] - c) if len(later) and (later[0] - c) <= 120 else np.nan)
        lags = np.array(lags, float); okl = np.isfinite(lags)
        res.update(hindsight_changes=int(len(hc)), median_lag=float(np.nanmedian(lags)) if okl.any() else np.nan, p75_lag=float(np.nanpercentile(lags[okl], 75)) if okl.any() else np.nan, never_confirmed=float(1 - okl.mean()) if len(lags) else np.nan,
                   agreement=float((hind[(lab >= 0) & np.isfinite(hind)] == lab[(lab >= 0) & np.isfinite(hind)]).mean()))
        L += [f"Hindsight (full-sample) labels: {len(hc)} changes. Sessions from a hindsight change to the live labeller's next change: **median {res['median_lag']:.0f}**, 75th percentile {res['p75_lag']:.0f}; "
              f"{res['never_confirmed']:.0%} of hindsight changes have no live change within 120 sessions. Live and hindsight labels agree on {res['agreement']:.0%} of sessions (label numbers may be permuted between fits; agreement is the raw match).", ""]
    else:
        L += ["No hindsight labels exposed by the engine; only the live run lengths are reported. To measure the lag, expose the full-sample labels in asset_extension and re-run.", ""]
    L.append("Reading: a label that confirms a change 15–30 sessions into a ~52-session regime describes the season after it has arrived.")
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(res, indent=1, default=float)); print(res); print(f"-> {out}")


# ------------------------------------------------------------------------------------------------ R3
def cmd_conditioning(csv: str):
    idx, rets, lab, post, m = inputs(); labs = pd.Series(lab, index=idx); rng = np.random.default_rng(0); out_rows = []
    def perm_blocks(x, b=20):
        n = len(x); starts = np.arange(0, n, b); order = rng.permutation(len(starts)); return x[np.concatenate([np.arange(s, min(s + b, n)) for s in starts[order]])]
    # (a) Fed-day reaction by regime
    try:
        from src.chair_power import table, ols, interaction_F
        t = table().dropna(subset=["s_norm", "gld"]).copy(); t["regime"] = labs.reindex(pd.DatetimeIndex(t["date"])).ffill().to_numpy(); t = t[t.regime >= 0]
        for g, sub in t.groupby("regime"):
            if len(sub) < 8: continue
            _, b, se, _, _ = ols(sub["s_norm"].to_numpy(), sub["gld"].to_numpy()); out_rows.append(dict(relationship="Fed-day β per σ", regime=int(g), n=len(sub), value=b * 100, t=(b / se if se else np.nan)))
        F = interaction_F(t, "gld", t["regime"].to_numpy(), "s_norm"); null = [interaction_F(t, "gld", rng.permutation(t["regime"].to_numpy()), "s_norm") for _ in range(1000)]
        fed_p = float((np.array(null) >= F).mean())
    except Exception as e:
        fed_p = np.nan; print(f"  Fed-day by regime skipped ({type(e).__name__}: {e})")
    # (b) factor model R² by regime
    try:
        from src.factor_attribution import factors, returns as fret; from src.era_factors import fit
        r = fret("GLD"); r.index = pd.to_datetime(r.index); F = factors(r.index); F.index = pd.to_datetime(F.index); F = F.drop(columns=[c for c in F.columns if c == "btc"])
        d = pd.concat([r.rename("y"), F], axis=1).dropna(); d["regime"] = labs.reindex(d.index).ffill().to_numpy(); d = d[d.regime >= 0]; names = [c for c in d.columns if c not in ("y", "regime")]
        r2 = {}
        for g, sub in d.groupby("regime"):
            if len(sub) < 250: continue
            _, rr, _ = fit(sub[names].to_numpy(float), sub["y"].to_numpy(float)); r2[int(g)] = rr; out_rows.append(dict(relationship="factor R² (GLD)", regime=int(g), n=len(sub), value=rr, t=np.nan))
        spread = max(r2.values()) - min(r2.values()) if len(r2) > 1 else np.nan; null = []
        for _ in range(300):
            lp = perm_blocks(d["regime"].to_numpy()); vals = []
            for g in r2:
                mk = lp == g
                if mk.sum() >= 250: _, rr, _ = fit(d[names].to_numpy(float)[mk], d["y"].to_numpy(float)[mk]); vals.append(rr)
            null.append(max(vals) - min(vals) if len(vals) > 1 else np.nan)
        fac_p = float((np.array(null) >= spread).mean())
    except Exception as e:
        fac_p = np.nan; print(f"  factor R² by regime skipped ({type(e).__name__}: {e})")
    # (c) the report's calls by regime (backfill CSV carries its own regime column)
    try:
        df = pd.read_csv(csv); df["date"] = pd.to_datetime(df["date"]); df = df[(df.h == 2) & (df.kind == "call")].dropna(subset=["call", "ret_primary"])
        df["hit"] = (np.sign(df.call) == np.sign(df.ret_primary)) & (df.ret_primary != 0); hits = {}
        for g, sub in df.groupby("regime"):
            if len(sub) < 30: continue
            hits[g] = float(sub.hit.mean()); out_rows.append(dict(relationship="call hit-rate", regime=g, n=len(sub), value=float(sub.hit.mean()), t=np.nan))
        spread = max(hits.values()) - min(hits.values()) if len(hits) > 1 else np.nan; null = []
        calls = df.call.to_numpy(); rets_ = df.ret_primary.to_numpy(); reg = df.regime.to_numpy()
        for _ in range(500):
            c2 = perm_blocks(calls, 2); h2 = (np.sign(c2) == np.sign(rets_)) & (rets_ != 0); vals = [h2[reg == g].mean() for g in hits]; null.append(max(vals) - min(vals))
        call_p = float((np.array(null) >= spread).mean())
    except Exception as e:
        call_p = np.nan; print(f"  calls by regime skipped ({type(e).__name__}: {e})")
    tab = pd.DataFrame(out_rows); out = DOCS / "regime_conditioning.md"
    L = ["# R3 — do the regime labels sharpen the confirmed relationships?", "", "| relationship | regime | n | value | t |", "|---|---|---|---|---|"]
    for _, r in tab.iterrows(): L.append(f"| {r['relationship']} | {r['regime']} | {r['n']} | {r['value']:+.3f} | {r['t']:+.2f} |" if np.isfinite(r["t"]) else f"| {r['relationship']} | {r['regime']} | {r['n']} | {r['value']:+.3f} | — |")
    L += ["", f"Do the regimes differ? Fed-day reaction: regime × surprise interaction p **{fed_p:.3f}**. Factor R²: spread across regimes vs block-permuted labels p **{fac_p:.3f}**. Call hit-rate: spread vs block-permuted calls p **{call_p:.3f}**.", "",
          "p < 0.05 on a line means the labels carry information about that relationship; otherwise the regime is a description, not a conditioner."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(dict(rows=json.loads(tab.to_json(orient="records")), fed_p=fed_p, factor_p=fac_p, call_p=call_p), indent=1, default=float))
    print(tab.to_string(index=False)); print(f"interaction p: fed {fed_p:.3f}, factor {fac_p:.3f}, calls {call_p:.3f} -> {out}")


# ------------------------------------------------------------------------------------------------ R4
def cmd_kbytime():
    try:
        from sklearn.decomposition import PCA; from sklearn.mixture import GaussianMixture; from sklearn.metrics import silhouette_score, adjusted_rand_score
    except ImportError:
        print("scikit-learn not installed in the venv: pip install scikit-learn, then re-run"); return
    idx, rets, lab, post, m = inputs(); dials = [c for c in DIALS if c in m.columns]; X = m[dials].dropna()
    if "M2SL" in X.columns: X = X.assign(M2SL=X["M2SL"].pct_change(252)).dropna()
    rows = []
    for year in range(2010, idx[-1].year + 1):
        sub = X[X.index <= f"{year}-12-31"]; Z = (sub - sub.mean()) / sub.std(); P = PCA(3).fit_transform(Z.to_numpy())
        for k in range(3, 9):
            labs = []
            for seed in range(5):
                g = GaussianMixture(k, covariance_type="full", random_state=seed, n_init=1).fit(P); labs.append(g.predict(P))
            ari = float(np.mean([adjusted_rand_score(labs[i], labs[j]) for i in range(5) for j in range(i + 1, 5)]))
            l0 = labs[0]; runs = np.diff(np.where(np.diff(np.concatenate([[-1], l0, [-1]])) != 0)[0]); sil = float(silhouette_score(P, l0, sample_size=min(3000, len(P)), random_state=0))
            rows.append(dict(year=year, k=k, ari=ari, median_run=float(np.median(runs)), silhouette=sil, n=len(P)))
    tab = pd.DataFrame(rows)
    win = tab.loc[tab.groupby("year").apply(lambda g: (g.ari.rank() + g.median_run.rank() + g.silhouette.rank()).idxmax()).to_numpy()][["year", "k", "ari", "median_run", "silhouette"]]
    out = DOCS / "regime_kbytime.md"
    L = ["# R4 — which regime count wins, year by year", "", "At each year-end the mixture is refit on data to date for k = 3…8 (5 seeds). Stability = mean adjusted Rand index across seeds; persistence = median run length; separation = silhouette. Winner = best summed rank.", "",
         "| year | winning k | stability | median run | silhouette |", "|---|---|---|---|---|"] + [f"| {int(r.year)} | **{int(r.k)}** | {r.ari:.3f} | {r.median_run:.0f} | {r.silhouette:.3f} |" for _, r in win.iterrows()]
    L += ["", "Full table in the JSON. A switch of k is a founder decision (it relabels history and the precedent pools are keyed by label)."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(orient="records", indent=1)); print(win.to_string(index=False)); print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["describe", "lag", "conditioning", "kbytime", "all"]); ap.add_argument("--csv", default="processed/report_backfill_97d9bf07dd2c_n5793.csv")
    a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    for c in (["describe", "lag", "conditioning", "kbytime"] if a.cmd == "all" else [a.cmd]):
        try:
            {"describe": cmd_describe, "lag": cmd_lag, "conditioning": lambda: cmd_conditioning(a.csv), "kbytime": cmd_kbytime}[c]()
        except Exception as e:
            print(f"{c}: did not run -- {type(e).__name__}: {e}")
            if a.cmd != "all": raise
