"""
Liquidity-regime sub-classifier  (Problem 1 / original-plan Week 4)

STAGE 1 of 2 -- build & validate the liquidity states.
  Stage 1 (this script): construct two asset-derived, FRED-independent
    liquidity features, fit a 2-component GMM (twinning the macro regime
    engine), label each day abundant-vs-stress, sanity-check the stress
    state against the config's crisis episodes, and SAVE the states.
  Stage 2 (next script): consume these states to run the safe-haven
    correlation test (GLD-SPY correlation, abundant vs stress).

Features (independent of the macro FRED panel AND of the GLD-SPY outcome
pair, so Stage 2's conditional test is clean):
  1. correlation breadth : trailing-window mean pairwise correlation across
     a 'state basket' of core assets that EXCLUDES gold & broad equity.
  2. realized volatility  : trailing-window annualized vol of the equal-
     weight state basket.
Stress state := the GMM component with the higher mean correlation breadth.

DATA HYGIENE (v2): the returns panel carries scattered all-NaN rows (non-
trading days left in the index). These poison any window they touch -- one
empty row makes the whole corr matrix NaN and kills the vol window -- which
silently dropped ~60% of days in v1. v2 removes all-NaN rows first, then
computes each feature on the complete-case rows inside each window, so a
stray single-asset gap can't void a whole day.

Run:
    python -m src.liquidity_classifier
Optional:
    --window 20   --min-coverage 0.95
    --outpath processed/liquidity_states.parquet
"""
import argparse

import numpy as np
import pandas as pd

from src.data_io import load_config

OUTCOME_TICKERS = {"GLD", "IAU", "SPY", "VOO"}  # gold, gold_alt, equity_broad, equity_broad_alt
CORE_CANDIDATES = [
    "TLT", "UUP", "XLP", "XLV", "XLE", "SMH", "SOXX", "IYW", "SLV", "USO", "ITA",
    "XSD", "IGN", "WCLD", "SKYY", "CIBR", "HACK", "URA", "URNM", "REMX",
    "AMLP", "MLPA", "XAR", "JETS", "FIVG", "UFO", "MAGS",
]


def load_returns(path="processed/asset_returns.parquet"):
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    med_abs = np.nanmedian(np.abs(df.to_numpy()))
    if med_abs > 0.5:
        print(f"  (input looks like PRICES, median|.|={med_abs:.3f} -> converting to returns)")
        df = df.pct_change()
    else:
        print(f"  (input looks like RETURNS, median|.|={med_abs:.4f} -> using as-is)")
    return df


def build_features(rets, basket, window):
    """complete-case correlation breadth + realized vol, robust to stray gaps."""
    B = rets[basket]
    vals = B.to_numpy()
    n = len(B)
    k = len(basket)
    iu = np.triu_indices(k, k=1)
    min_rows = max(5, window // 2)

    breadth = np.full(n, np.nan)
    for t in range(window - 1, n):
        w = vals[t - window + 1: t + 1]
        wc = w[~np.isnan(w).any(axis=1)]         # keep only fully-present rows
        if len(wc) >= min_rows:
            c = np.corrcoef(wc, rowvar=False)
            breadth[t] = np.nanmean(c[iu])

    ew = B.mean(axis=1)                            # equal-weight basket return (skips NaN)
    realvol = ew.rolling(window, min_periods=min_rows).std() * np.sqrt(252)

    out = pd.DataFrame({"breadth": breadth, "realvol": realvol.to_numpy()}, index=B.index)
    return out.dropna()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=20)
    ap.add_argument("--min-coverage", type=float, default=0.95)
    ap.add_argument("--outpath", default="processed/liquidity_states.parquet")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    from sklearn.mixture import GaussianMixture

    cfg = load_config()
    print("=" * 74)
    print("LIQUIDITY SUB-CLASSIFIER -- Stage 1 v2 (build & validate states)")
    print("=" * 74)

    rets = load_returns()
    print(f"asset_returns: {rets.shape[1]} cols, {len(rets)} rows, "
          f"{rets.index.min().date()} -> {rets.index.max().date()}")

    # HYGIENE: drop non-trading all-NaN rows before any windowing
    before = len(rets)
    rets = rets.dropna(how="all")
    print(f"dropped {before - len(rets)} all-NaN (non-trading) rows -> {len(rets)} rows remain")

    for t in ("GLD", "SPY"):
        if t not in rets.columns:
            raise SystemExit(f"outcome ticker {t} not in columns: {list(rets.columns)}")

    common = rets[["GLD", "SPY"]].dropna().index
    lo, hi = common.min(), common.max()
    print(f"common GLD&SPY window: {lo.date()} -> {hi.date()} ({len(common)} days)")

    present = [c for c in CORE_CANDIDATES if c in rets.columns and c not in OUTCOME_TICKERS]
    win = rets.loc[lo:hi, present]
    cover = win.notna().mean()
    basket = [c for c in present if cover[c] >= args.min_coverage]
    if len(basket) < 4:
        raise SystemExit(f"state basket too small ({len(basket)}): {basket}")
    print(f"\nstate basket ({len(basket)} assets, gold & broad-equity excluded):")
    print("  " + ", ".join(basket))

    feat = build_features(rets.loc[lo:hi], basket, args.window)
    kept = len(feat) / len(common)
    print(f"\nfeatures built: {len(feat)} days after warmup "
          f"({feat.index.min().date()} -> {feat.index.max().date()})  "
          f"[{kept:.0%} of the common window retained]")

    X = (feat - feat.mean()) / feat.std()
    gm = GaussianMixture(n_components=2, covariance_type="full",
                         n_init=10, max_iter=200, random_state=args.seed)
    comp = gm.fit_predict(X.to_numpy())
    stress_comp = 0 if X["breadth"][comp == 0].mean() > X["breadth"][comp == 1].mean() else 1
    stress = (comp == stress_comp)

    feat = feat.assign(state=comp, stress=stress)
    n_stress = int(stress.sum())
    print(f"\nGMM states: stress={n_stress} days ({n_stress/len(feat):.1%}), "
          f"abundant={len(feat)-n_stress} days")
    print(f"{'':10} | {'breadth':>9} | {'realvol':>9}")
    print("-" * 34)
    print(f"{'stress':10} | {feat.loc[stress,'breadth'].mean():>9.3f} | "
          f"{feat.loc[stress,'realvol'].mean():>9.3f}")
    print(f"{'abundant':10} | {feat.loc[~stress,'breadth'].mean():>9.3f} | "
          f"{feat.loc[~stress,'realvol'].mean():>9.3f}")

    episodes = cfg.get("crisis_episodes", [])
    in_crisis = pd.Series(False, index=feat.index)
    for ep in episodes:
        s, e = pd.to_datetime(ep["start"]), pd.to_datetime(ep["end"])
        in_crisis |= (feat.index >= s) & (feat.index <= e)
    base_rate = in_crisis.mean()
    stress_in_crisis = in_crisis[stress].mean()
    lift = stress_in_crisis / base_rate if base_rate else float("nan")
    print("\nCRISIS OVERLAY (sanity check):")
    print(f"  {base_rate:.1%} of all days fall in a config crisis episode.")
    print(f"  {stress_in_crisis:.1%} of STRESS-state days do  ->  lift x{lift:.2f}")

    feat.to_parquet(args.outpath)
    print(f"\nsaved states -> {args.outpath}")
    print("=" * 74)
    print("Expect ~90%+ of the window retained now, stress state higher on BOTH")
    print("features, and crisis lift > 1. If so, states are sound -> Stage 2.")
    print("=" * 74)


if __name__ == "__main__":
    main()
