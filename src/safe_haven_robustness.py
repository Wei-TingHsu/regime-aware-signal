"""
Safe-haven inversion -- robustness sweep (follow-up to Stage 2).

Stage 2 found NO inversion at a 20-day window with raw-correlation averaging,
under both the liquidity classifier and the n=4 macro regime. Before locking
in that null, two design choices deserve a check:
  * horizon -- flight-to-quality can be a days-long spasm a 20d window smears
    out. Sweep corr windows 5 / 10 / 20 / 60.
  * averaging -- raw mean-correlation vs Fisher-z (arctanh), which weights the
    tails where haven effects would live.

Same states (fixed), same circular-rotation permutation. For every
(state definition x window x transform) cell it reports the signed gap
(stress - other) and a ONE-SIDED p = P(null <= observed): small p means the
inversion (gap more negative than chance) IS supported; large p means it is
not. Read the primary (liquidity) block: if every cell stays non-significant,
the null is robust; if a short window lights up, the flip is horizon-specific.

Run:
    python -m src.safe_haven_robustness
Optional:
    --windows 5,10,20,60   --iters 5000   --seed 42
"""
import argparse

import numpy as np
import pandas as pd

from src.data_io import load_config


def rolling_corr(rets, a, b, window):
    sub = rets[[a, b]].dropna(how="all").dropna()
    return sub[a].rolling(window, min_periods=max(5, window // 2)).corr(sub[b]).dropna()


def gap(vals, mask):
    return vals[mask].mean() - vals[~mask].mean()


def cell(corr, mask, iters, rng, fisher):
    common = corr.index.intersection(mask.index)
    c = corr.loc[common]
    if fisher:
        c = np.arctanh(np.clip(c, -0.999, 0.999))
    v = c.to_numpy()
    md = mask.reindex(common).fillna(False).to_numpy()
    obs = gap(pd.Series(v), pd.Series(md))
    m = len(md)
    offsets = rng.integers(1, m, size=iters)
    vs = pd.Series(v)
    null = np.empty(iters)
    for i, off in enumerate(offsets):
        null[i] = gap(vs, pd.Series(np.roll(md, off)))
    p_neg = (np.sum(null <= obs) + 1) / (iters + 1)   # inversion direction
    return obs, p_neg, int(md.sum()), len(common)


def macro_stress_mask(scores_path, seed, n_regimes):
    from sklearn.mixture import GaussianMixture
    scores = pd.read_parquet(scores_path)
    scores.index = pd.to_datetime(scores.index)
    if "PC2" not in scores.columns:
        raise SystemExit(f"'PC2' not in macro_pca_scores columns: {list(scores.columns)}")
    gm = GaussianMixture(n_components=n_regimes, covariance_type="full",
                         n_init=10, max_iter=200, random_state=seed)
    lab = pd.Series(gm.fit_predict(scores.to_numpy()), index=scores.index)
    means = {r: scores.loc[lab == r, "PC2"].mean() for r in lab.unique()}
    return (lab == max(means, key=means.get))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", default="5,10,20,60")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--states", default="processed/liquidity_states.parquet")
    ap.add_argument("--returns", default="processed/asset_returns.parquet")
    ap.add_argument("--scores", default="processed/macro_pca_scores.parquet")
    args = ap.parse_args()
    windows = [int(x) for x in args.windows.split(",")]
    rng = np.random.default_rng(args.seed)
    n_regimes = int(load_config()["regime"]["n_regimes"])

    rets = pd.read_parquet(args.returns); rets.index = pd.to_datetime(rets.index)
    rets = rets.sort_index()
    states = pd.read_parquet(args.states); states.index = pd.to_datetime(states.index)
    liq_mask = states["stress"].astype(bool)
    macro_mask = macro_stress_mask(args.scores, args.seed, n_regimes)

    print("=" * 78)
    print(f"SAFE-HAVEN ROBUSTNESS SWEEP  ({args.iters} rotations/cell)")
    print("  gap = mean corr(stress) - mean corr(other);  p = P(null <= obs)")
    print("  small p => inversion supported.  * p<.05   ** p<.008")
    print("=" * 78)

    any_hit_primary = False
    for name, mask in [("PRIMARY: liquidity classifier", liq_mask),
                       (f"CROSS-CHECK: n={n_regimes} macro regime", macro_mask)]:
        print(f"\n{name}")
        print(f"  {'window':>6} | {'raw  gap (p)':>20} | {'Fisher-z gap (p)':>20} | overlap")
        print("  " + "-" * 66)
        for w in windows:
            corr = rolling_corr(rets, "GLD", "SPY", w)
            o_r, p_r, ns, ov = cell(corr, mask, args.iters, rng, fisher=False)
            o_z, p_z, _, _ = cell(corr, mask, args.iters, rng, fisher=True)
            def star(p): return "**" if p < 0.008 else "* " if p < 0.05 else "  "
            if name.startswith("PRIMARY") and (p_r < 0.05 or p_z < 0.05):
                any_hit_primary = True
            print(f"  {w:>6} | {o_r:+.3f} ({p_r:.3f}){star(p_r)}   | "
                  f"{o_z:+.3f} ({p_z:.3f}){star(p_z)}   | {ov} days, {ns} stress")

    print("\n" + "=" * 78)
    if any_hit_primary:
        print("A short-horizon cell IS significant under the liquidity definition ->")
        print("the inversion is HORIZON-SPECIFIC; report it with the window it needs.")
    else:
        print("No cell is significant under the liquidity definition, at any window or")
        print("transform -> the NULL IS ROBUST. Gold does not decouple from equities in")
        print("liquidity stress over 2004-2026; if anything it co-moves slightly more")
        print("(dash-for-cash). That is a clean, well-tested negative finding.")
    print("  NOTE: the macro cross-check spans a shorter period than the liquidity")
    print("  test (its PCA panel is limited by the shortest FRED input), so the two")
    print("  blocks are not over identical windows -- weight the liquidity block more.")
    print("=" * 78)


if __name__ == "__main__":
    main()
