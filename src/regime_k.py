"""regime_k.py -- R6b and R2 (docs/prereg_regime_audit.md): the regime count chosen on usefulness with the engine's OWN expanding refit, and
the live labeller's confirmation lag against hindsight labels.

  python -m src.regime_k compare       # R6b: k = 3..6 through analog_event.regime_labels_expanding (no look-ahead; canonical PC1 order; confirmed
                                       #      as the product applies them); judged on (a) the Fed-day regime x surprise interaction p, (b) the spread of the
                                       #      factor model's R² across regimes, (c) the asset-ranking stability of the favoured-asset map
  python -m src.regime_k lag           # R2: for the live k, a single full-sample fit (hindsight) vs the expanding labels: sessions from each hindsight change
                                       #      to the live labeller's matching change; agreement share
Outputs docs/regime_kcompare_expanding.md, docs/regime_lag.md (+ .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd

DOCS = Path("docs")


def engine():
    import asset_extension as AE
    import src.analog_event as AEV
    cfg = AE.load_config(); sc, rt = AE.load_data(); return AE, AEV, cfg, sc


def labels_for_k(AEV, cfg, sc, k: int) -> np.ndarray:
    c = copy.deepcopy(cfg); c["regime"]["n_regimes"] = int(k)
    return np.asarray(AEV.regime_labels_expanding(sc, c, refit_every=20, min_train=504, cache=False))


def hindsight_labels(AEV, cfg, sc, k: int) -> np.ndarray:
    """One mixture on the whole panel, components in ascending mean-PC1 order -- the same convention as the live labeller."""
    from sklearn.mixture import GaussianMixture
    X = sc[AEV.CLUSTERING_PCS].values
    g = GaussianMixture(n_components=k, covariance_type=cfg["regime"]["covariance_type"], max_iter=cfg["regime"]["max_iter"], n_init=cfg["regime"]["n_init"], random_state=cfg["project"]["random_seed"]).fit(X)
    order = np.argsort(g.means_[:, 0]); remap = np.empty(k, int); remap[order] = np.arange(k); return remap[g.predict(X)]


def cmd_compare():
    import src.exposure_dial as ED
    from src.regime_describe import asset_map, ASSETS
    from src.chair_power import table, interaction_F
    from src.factor_attribution import factors, returns as fret
    from src.era_factors import fit
    AE, AEV, cfg, sc = engine(); idx = pd.DatetimeIndex(sc.index)
    rets = pd.read_parquet("processed/asset_returns.parquet"); rets.index = pd.to_datetime(rets.index); rets = rets.reindex(idx)
    t = table().dropna(subset=["s_norm", "gld"]).copy(); r = fret("GLD"); r.index = pd.to_datetime(r.index); F = factors(r.index); F.index = pd.to_datetime(F.index); F = F.drop(columns=[c for c in F.columns if c == "btc"])
    d = pd.concat([r.rename("y"), F], axis=1).dropna(); names = [c for c in d.columns if c != "y"]; rng = np.random.default_rng(0); rows = []; all_labels = {}
    for k in (3, 4, 5, 6):
        print(f"  k = {k}: expanding refit ...")
        raw = labels_for_k(AEV, cfg, sc, k); lab = ED.confirmed_labels(raw); all_labels[k] = lab; labs = pd.Series(lab, index=idx)
        runs = np.diff(np.where(np.diff(np.concatenate([[-9], lab, [-9]])) != 0)[0]); shares = {int(g): float((lab == g).mean()) for g in sorted(set(lab[lab >= 0]))}
        tt = t.copy(); tt["regime"] = labs.reindex(pd.DatetimeIndex(tt["date"])).ffill().to_numpy(); tt = tt[tt.regime >= 0]
        Fv = interaction_F(tt, "gld", tt["regime"].to_numpy(), "s_norm"); null = [interaction_F(tt, "gld", rng.permutation(tt["regime"].to_numpy()), "s_norm") for _ in range(500)]; fed_p = float((np.array(null) >= Fv).mean())
        dd = d.copy(); dd["regime"] = labs.reindex(dd.index).ffill().to_numpy(); dd = dd[dd.regime >= 0]; r2 = {}
        for g, sub in dd.groupby("regime"):
            if len(sub) >= 250: _, rr, _ = fit(sub[names].to_numpy(float), sub["y"].to_numpy(float)); r2[int(g)] = rr
        spread = max(r2.values()) - min(r2.values()) if len(r2) > 1 else np.nan
        am = asset_map(idx, rets, lab, f"k={k}", rng, n_perm=150)
        rows.append(dict(k=k, median_run=float(np.median(runs)), n_runs=int(len(runs)), shares=shares, fed_interaction_p=fed_p, factor_r2=r2, factor_r2_spread=spread, asset_stability=am["stability"], asset_stability_p=am["p"]))
        print({kk: v for kk, v in rows[-1].items() if kk not in ("shares", "factor_r2")})
    tab = pd.DataFrame(rows); out = DOCS / "regime_kcompare_expanding.md"
    L = ["# R6b — the regime count on usefulness, with the engine's own expanding refit (no look-ahead)", "",
         "Each k through `regime_labels_expanding` (refit every 20 sessions, first 504 unlabelled, components ordered by mean PC1), then confirmed as the product applies labels. Jobs: (a) Fed-day — lower p = the labels condition gold's reaction to a rate surprise; (b) factor R² spread — wider = the labels separate 'gold is a macro asset' from 'it is not'; (c) favoured-asset map — ranking stability between each regime's first and second half, with its block-permutation p.", "",
         "| k | median run | runs | Fed-day interaction p | factor R² by regime | spread | asset-map stability | p |", "|---|---|---|---|---|---|---|---|"]
    for _, r_ in tab.iterrows(): L.append(f"| {int(r_.k)} | {r_.median_run:.0f} | {r_.n_runs} | {r_.fed_interaction_p:.3f} | " + ", ".join(f"{g}: {v:.2f}" for g, v in r_.factor_r2.items()) + f" | {r_.factor_r2_spread:.3f} | {r_.asset_stability:+.2f} | {r_.asset_stability_p:.3f} |")
    L += ["", "The count is chosen on this table by dated amendment (prereg_regime_audit §2); a switch relabels history and the precedent pools are rebuilt."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(rows, indent=1, default=float))
    pd.DataFrame({f"k{k}": v for k, v in all_labels.items()}, index=idx).to_parquet("processed/regime_labels_by_k.parquet"); print(f"-> {out}; labels saved to processed/regime_labels_by_k.parquet")


def cmd_lag():
    import src.exposure_dial as ED
    AE, AEV, cfg, sc = engine(); idx = pd.DatetimeIndex(sc.index); k = int(cfg["regime"]["n_regimes"])
    live_raw = np.asarray(AEV.regime_labels_expanding(sc, cfg)); live = ED.confirmed_labels(live_raw); hind = hindsight_labels(AEV, cfg, sc, k)
    ok = live >= 0; agree = float((live[ok] == hind[ok]).mean())
    hc = np.where(hind[1:] != hind[:-1])[0] + 1; hc = hc[hc >= 504]; lc = np.where((live[1:] != live[:-1]) & (live[1:] >= 0))[0] + 1
    lags = []
    for c in hc:
        target = hind[c]; later = lc[(lc >= c - 10) & (lc <= c + 120)]; match = [x for x in later if live[x] == target]
        lags.append(int(match[0] - c) if match else np.nan)
    lags = np.array(lags, float); okl = np.isfinite(lags)
    res = dict(k=k, hindsight_changes=int(len(hc)), live_changes=int(len(lc)), agreement=agree, median_lag=float(np.nanmedian(lags)) if okl.any() else np.nan,
               p75_lag=float(np.nanpercentile(lags[okl], 75)) if okl.any() else np.nan, never_matched=float(1 - okl.mean()) if len(lags) else np.nan,
               hindsight_median_run=float(np.median(np.diff(hc))) if len(hc) > 1 else np.nan)
    out = DOCS / "regime_lag.md"
    L = ["# R2 — how late the live labeller confirms a change", "", f"k = {k}. Hindsight = one mixture on the whole panel (canonical order); live = the expanding refit, confirmed. Labels agree on **{agree:.0%}** of labelled sessions.", "",
         f"{res['hindsight_changes']} hindsight changes (median run {res['hindsight_median_run']:.0f} sessions); {res['live_changes']} live changes. Sessions from a hindsight change to the live labeller's matching change (−10 … +120 window): **median {res['median_lag']:.0f}**, 75th percentile {res['p75_lag']:.0f}; {res['never_matched']:.0%} of hindsight changes never matched inside the window.", "",
         "Reading: the lag is the time the product spends labelling the previous season after the new one has begun; a negative median would mean the live label leads hindsight, which cannot happen systematically."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(res, indent=1, default=float)); print(res); print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["compare", "lag"]); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    cmd_compare() if a.cmd == "compare" else cmd_lag()
