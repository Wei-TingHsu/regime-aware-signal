"""
Safe-haven inversion test  (Problem 1 / original-plan Week 4) -- STAGE 2 of 2.

Hypothesis: the GLD-SPY correlation is MORE NEGATIVE in stress states than in
abundant states (gold decouples from equities when funding dries up).

Design: contemporaneous state & correlation, 20d rolling GLD-SPY correlation.
  * primary state    = the liquidity sub-classifier (Stage 1 output).
  * cross-check state = the n=4 MACRO stress regime, refit from the PCA scores.

v2 CHANGE: the macro stress regime is now selected by a DATA-DRIVEN stress
axis (the PC most correlated with VIX), not a hard-coded 'PC2'. Refitting the
PCA on a different span renumbers the components, and on the 2006+ refit the
VIX axis moved off PC2 -- hard-coding it silently mislabeled the regime. See
src/stress_axis.py.

Test statistic: gap = mean_corr(stress) - mean_corr(other); hypothesis gap<0.
Significance via circular-rotation permutation.

Run:
    python -m src.safe_haven_test
Optional:
    --corr-window 20   --iters 5000   --seed 42
"""
import argparse

import numpy as np
import pandas as pd

from src.stress_axis import find_stress_axis, describe


def rolling_corr(rets, a, b, window):
    sub = rets[[a, b]].dropna(how="all").dropna()
    return sub[a].rolling(window, min_periods=max(5, window // 2)).corr(sub[b]).dropna()


def gap(vals, mask):
    return vals[mask].mean() - vals[~mask].mean()


def perm_p(corr_vals, mask, iters, rng):
    obs = gap(pd.Series(corr_vals), pd.Series(mask))
    m = len(mask)
    null = np.empty(iters)
    offsets = rng.integers(1, m, size=iters)
    cs = pd.Series(corr_vals)
    for i, off in enumerate(offsets):
        null[i] = gap(cs, pd.Series(np.roll(mask, off)))
    p_neg = (np.sum(null <= obs) + 1) / (iters + 1)
    p_pos = (np.sum(null >= obs) + 1) / (iters + 1)
    return obs, float(np.nanmean(null)), p_neg, p_pos


def macro_stress_mask(scores_path, panel_path, seed):
    """Refit n=4 macro regimes; stress = regime with highest mean stress-axis
    score, where the stress axis is the VIX-correlated PC (data-driven)."""
    from sklearn.mixture import GaussianMixture
    scores = pd.read_parquet(scores_path); scores.index = pd.to_datetime(scores.index)
    panel = pd.read_parquet(panel_path); panel.index = pd.to_datetime(panel.index)
    vixcol = "VIXCLS" if "VIXCLS" in panel.columns else "vix"
    if vixcol not in panel.columns:
        raise SystemExit(f"no VIX column in panel: {list(panel.columns)}")
    print("  " + describe(scores, panel[vixcol]))          # log which axis was used

    col, sign, _ = find_stress_axis(scores, panel[vixcol])
    gm = GaussianMixture(n_components=4, covariance_type="full",
                         n_init=10, max_iter=200, random_state=seed)
    lab = pd.Series(gm.fit_predict(scores.to_numpy()), index=scores.index)
    axis = sign * scores[col]
    means = {r: axis[lab == r].mean() for r in lab.unique()}
    stress_r = max(means, key=means.get)
    return (lab == stress_r)


def report(name, corr, mask, iters, rng):
    common = corr.index.intersection(mask.index)
    c = corr.loc[common]
    md = mask.reindex(common).fillna(False).to_numpy()
    obs, nmean, p_neg, p_pos = perm_p(c.to_numpy(), md, iters, rng)
    ms, ma = c[md].mean(), c[~md].mean()
    ns, na = int(md.sum()), int((~md).sum())
    print(f"\n{name}  (overlap {len(common)} days)")
    print(f"  {'stress':16} mean corr = {ms:+.3f}   ({ns} days)")
    print(f"  {'abundant/other':16} mean corr = {ma:+.3f}   ({na} days)")
    print(f"  gap (stress - other) = {obs:+.3f}   (hypothesis: negative)")
    if obs < 0:
        print(f"  permutation p (stress MORE negative) = {p_neg:.4f}   [null mean {nmean:+.3f}]")
        verdict = ("SIGNIFICANT inversion (p<.05)" if p_neg < 0.05
                   else "marginal (p<.10)" if p_neg < 0.10
                   else "not distinguishable from chance")
    else:
        print(f"  gap is POSITIVE -- opposite to the hypothesis; p(this direction) = {p_pos:.4f}")
        verdict = "OPPOSITE direction (no safe-haven inversion here)"
    print(f"  --> {verdict}")
    return obs, (p_neg if obs < 0 else p_pos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corr-window", type=int, default=20)
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--states", default="processed/liquidity_states.parquet")
    ap.add_argument("--returns", default="processed/asset_returns.parquet")
    ap.add_argument("--scores", default="processed/macro_pca_scores.parquet")
    ap.add_argument("--panel", default="processed/macro_panel.parquet")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    print("=" * 74)
    print("SAFE-HAVEN INVERSION TEST -- Stage 2 v2 (data-driven stress axis)")
    print("=" * 74)
    print(f"contemporaneous | corr window {args.corr_window}d | {args.iters} rotations")

    rets = pd.read_parquet(args.returns); rets.index = pd.to_datetime(rets.index)
    rets = rets.sort_index()
    for t in ("GLD", "SPY"):
        if t not in rets.columns:
            raise SystemExit(f"{t} not in asset_returns columns")
    corr = rolling_corr(rets, "GLD", "SPY", args.corr_window)
    print(f"\nGLD-SPY {args.corr_window}d correlation: {len(corr)} days, "
          f"{corr.index.min().date()} -> {corr.index.max().date()}, overall mean {corr.mean():+.3f}")

    states = pd.read_parquet(args.states); states.index = pd.to_datetime(states.index)
    liq_mask = states["stress"].astype(bool)
    o1, p1 = report("PRIMARY -- liquidity sub-classifier", corr, liq_mask, args.iters, rng)

    print("\n(macro cross-check: identifying stress axis...)")
    macro_mask = macro_stress_mask(args.scores, args.panel, args.seed)
    o2, p2 = report("CROSS-CHECK -- n=4 macro stress regime", corr, macro_mask, args.iters, rng)

    print("\n" + "=" * 74)
    print("READING")
    print("  Negative gap + small p => gold decouples from equities in that state.")
    both = (o1 < 0 and p1 < 0.05) and (o2 < 0 and p2 < 0.05)
    if both:
        print("  BOTH definitions show a significant inversion -> corroborated.")
    elif (o1 < 0 and p1 < 0.05):
        print("  Liquidity shows it; macro does not -> LIQUIDITY-specific inversion.")
    elif (o2 < 0 and p2 < 0.05):
        print("  Macro (VIX-stress) shows it; liquidity does not -> the inversion is")
        print("     tied to broad risk-off, not the liquidity-breadth definition.")
    else:
        print("  Neither significant -> hypothesis not supported on this sample.")
    print("  CAVEAT: raw correlations averaged (not Fisher-z); 20d windows overlap.")
    print("=" * 74)


if __name__ == "__main__":
    main()
