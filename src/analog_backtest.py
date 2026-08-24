"""
Problem 1 engine -- STAGE 2: walk-forward backtest (v2, risk-adjusted).

Same honest walk-forward as v1 (expanding-window regime refit, no look-ahead,
non-overlapping weekly rebalances), but now reports the metrics that actually
judge signal quality, and runs TWO universes side by side:

  * ALL assets
  * LONG-HISTORY only (assets with >= --min-history years of data) -- the
    robustness check: does the edge survive after dropping recent-inception
    tickers (SNDK/DRAM/ARM...) that live only in the recent AI-semi bull run?

Metrics per universe:
  * mean weekly long-short SPREAD (+ ~annualized) and % weeks positive
  * long-leg / short-leg mean returns
  * directional HIT-RATE
  * SHARPE (annualized): spread-Sharpe (pure selection skill, ~market-neutral)
    AND long-leg Sharpe (deployable long-tilt, incl. market beta)
  * WIN/LOSS asymmetry: avg up-week vs avg down-week spread, payoff ratio
  * PERMUTATION p vs random baskets from the same eligible set

The expensive regime-refit walk-forward runs ONCE; both universes reuse it.

Run:
    python -m src.analog_backtest
Optional:
    --horizon 5  --nbasket 5  --topk 100  --start 2010-01-01
    --refit-every 20  --iters 1000  --min-history 8
"""
import argparse

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR

CLUSTERING_PCS = ["PC1", "PC2", "PC3"]


def load_returns():
    df = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet")
    df.index = pd.to_datetime(df.index); df = df.sort_index().dropna(how="all")
    if np.nanmedian(np.abs(df.to_numpy())) > 0.5:
        df = df.pct_change()
    return df


def evaluate(records, universe, N, iters, rng, label):
    """records: list of (pos, exp_fwd[A], realized[A]); universe: bool mask over assets."""
    spreads, hits, long_r, short_r = [], [], [], []
    eligs = []
    for pos, exp_fwd, realized in records:
        ok = universe & ~np.isnan(exp_fwd) & ~np.isnan(realized)
        elig = np.where(ok)[0]
        if len(elig) < 2 * N:
            continue
        ranked = elig[np.argsort(-exp_fwd[elig])]
        longs, shorts = ranked[:N], ranked[-N:]
        lr, sr = np.nanmean(realized[longs]), np.nanmean(realized[shorts])
        spreads.append(lr - sr); long_r.append(lr); short_r.append(sr)
        h = np.concatenate([realized[longs] > 0, realized[shorts] < 0])
        hits.append(h.mean())
        eligs.append((elig, realized))
    if not spreads:
        print(f"\n[{label}] no usable dates."); return
    spreads = np.array(spreads); hits = np.array(hits)
    long_r = np.array(long_r); short_r = np.array(short_r)

    ann = np.sqrt(52)
    spread_sharpe = spreads.mean() / spreads.std() * ann if spreads.std() else float("nan")
    long_sharpe = long_r.mean() / long_r.std() * ann if long_r.std() else float("nan")
    up, dn = spreads[spreads > 0], spreads[spreads < 0]
    payoff = up.mean() / abs(dn.mean()) if len(dn) and dn.mean() != 0 else float("nan")

    # permutation vs random baskets
    null = np.empty(iters)
    for it in range(iters):
        s = 0.0
        for elig, realized in eligs:
            pk = rng.permutation(elig)
            s += np.nanmean(realized[pk[:N]]) - np.nanmean(realized[pk[N:2 * N]])
        null[it] = s / len(eligs)
    p = (np.sum(null >= spreads.mean()) + 1) / (iters + 1)

    print(f"\n[{label}]  ({len(spreads)} rebalances)")
    print(f"  mean weekly spread = {spreads.mean()*100:+.3f}%  (~{spreads.mean()*5200:+.1f}%/yr)"
          f"   weeks positive {np.mean(spreads>0):.1%}")
    print(f"  long leg {long_r.mean()*100:+.3f}%   short leg {short_r.mean()*100:+.3f}%   "
          f"hit-rate {hits.mean():.1%}")
    print(f"  SHARPE (ann.): spread {spread_sharpe:+.2f}   long-leg {long_sharpe:+.2f}")
    print(f"  WIN/LOSS: avg up-week {up.mean()*100:+.3f}%  avg down-week "
          f"{dn.mean()*100:+.3f}%  payoff ratio {payoff:.2f}")
    print(f"  PERMUTATION vs random baskets: null {null.mean()*100:+.3f}%  p = {p:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--nbasket", type=int, default=5)
    ap.add_argument("--topk", type=int, default=100)
    ap.add_argument("--start", default="2010-01-01")
    ap.add_argument("--refit-every", type=int, default=20)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--min-history", type=float, default=8.0)
    ap.add_argument("--min-analogs", type=int, default=20)
    ap.add_argument("--min-cov", type=int, default=10)
    ap.add_argument("--half-life", type=float, default=None, metavar="YEARS",
                    help="recency half-life in YEARS. Converted to a per-session "
                         "lambda as ln2/(HL*252). Pass 'inf' for NO decay. "
                         "DEFAULT None = read analog.recency_decay_lambda from "
                         "config.yaml (0.0008/session, HL 3.44y), so a "
                         "no-argument run is BIT-IDENTICAL to the run that "
                         "produced the recorded 0.51 / 0.25.")
    args = ap.parse_args()
    from sklearn.mixture import GaussianMixture

    cfg = load_config()
    H, N = args.horizon, args.nbasket
    sigma = float(cfg["analog"]["similarity_sigma"])

    # --- recency decay ----------------------------------------------------
    # config's recency_decay_lambda is a PER-SESSION lambda with UNKNOWN
    # provenance: 0.0008 => HL = ln2/0.0008 = 866 sessions = 3.44 years. It is
    # off the registered ladder in docs/prereg_recency_kernel.md and is reported
    # as THE INCUMBENT, never as a rung. The recorded 0.51 / 0.25 carry it.
    # --half-life overrides it for the ladder sweep; the default path is
    # untouched so the headline figures stay reproducible from this repo.
    if args.half_life is None:
        lam = float(cfg["analog"]["recency_decay_lambda"])
        lam_src = (f"config recency_decay_lambda={lam:g}/session "
                   f"(HL {np.log(2)/lam/252:.2f}y) -- INCUMBENT, unregistered")
    elif np.isinf(args.half_life):
        lam = 0.0
        lam_src = "NO DECAY (HL = inf) -- ladder control rung"
    else:
        if args.half_life <= 0:
            raise SystemExit("--half-life must be positive, or inf for no decay.")
        lam = float(np.log(2.0) / (args.half_life * 252.0))
        lam_src = (f"HL {args.half_life:g}y -> lambda {lam:.6g}/session "
                   f"-- ladder rung")
    rng = np.random.default_rng(cfg["project"]["random_seed"])

    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    rets = load_returns().reindex(scores.index)
    Xc = scores[CLUSTERING_PCS].values
    dates = scores.index
    assets = list(rets.columns)
    A = len(assets)

    logret = np.log1p(rets)
    FWD = np.expm1(logret.rolling(H).sum().shift(-H).values)

    # long-history universe
    valid_ct = rets.notna().sum().values
    long_hist = valid_ct >= args.min_history * 252
    dropped = [assets[j] for j in range(A) if not long_hist[j]]

    print("=" * 78)
    print("PROBLEM 1 ENGINE -- Stage 2 v2 (risk-adjusted walk-forward)")
    print("=" * 78)
    print(f"horizon {H}d | basket {N}/side | expanding window, refit every "
          f"{args.refit_every}d | {args.iters} permutations")
    print(f"recency:  {lam_src}")
    print(f"features: RAW PC values (not z-scored) -- a different basis from "
          f"analog_core/model_grid")
    print(f"long-history cut: >= {args.min_history:g}y -> keeps {int(long_hist.sum())}/{A} assets; "
          f"drops: {', '.join(dropped) if dropped else '(none)'}")

    start_pos = int(dates.get_indexer([pd.to_datetime(args.start)], method="bfill")[0])
    rebs = list(range(start_pos, len(dates) - H, H))

    model, last_fit = None, -10 ** 9
    records = []
    for pos in rebs:
        if pos - last_fit >= args.refit_every or model is None:
            model = GaussianMixture(n_components=int(cfg["regime"]["n_regimes"]),
                                    covariance_type=cfg["regime"]["covariance_type"],
                                    max_iter=cfg["regime"]["max_iter"],
                                    n_init=cfg["regime"]["n_init"],
                                    random_state=cfg["project"]["random_seed"])
            model.fit(Xc[: pos + 1]); last_fit = pos
        lab = model.predict(Xc[: pos + 1])
        r_now, x_now = lab[-1], Xc[pos]
        cand = np.where((lab[:-1] == r_now) & (np.arange(pos) + H < pos))[0]
        if len(cand) < args.min_analogs:
            continue
        d = np.linalg.norm(Xc[cand] - x_now, axis=1)
        w = np.exp(-(d ** 2) / (2 * sigma ** 2)) * np.exp(-lam * (pos - cand))
        keep = np.argsort(-w)[: args.topk]
        cand, w = cand[keep], w[keep]; w = w / w.sum()
        fa = FWD[cand]; m = ~np.isnan(fa); cov = m.sum(axis=0)
        exp_fwd = np.full(A, np.nan)
        for j in range(A):
            if cov[j] >= args.min_cov:
                ww = w[m[:, j]]; ww = ww / ww.sum()
                exp_fwd[j] = np.sum(ww * fa[m[:, j], j])
        records.append((pos, exp_fwd, FWD[pos]))

    if not records:
        raise SystemExit("no usable rebalance dates.")
    print(f"\nwalk-forward complete: {len(records)} rebalances "
          f"({dates[records[0][0]].date()} -> {dates[records[-1][0]].date()})")

    evaluate(records, np.ones(A, bool), N, args.iters, rng, f"ALL {A} ASSETS")
    evaluate(records, long_hist, N, args.iters, rng,
             f"LONG-HISTORY ONLY (>= {args.min_history:g}y)")

    print("\n" + "=" * 78)
    print("READING")
    print("  Compare the two blocks: if spread, Sharpe, and p survive in the")
    print("  LONG-HISTORY block, the edge is NOT just recent AI-boom tickers.")
    print("  Spread-Sharpe = selection skill (market-neutral). payoff ratio > 1 with")
    print("  a ~50% win-rate = the fat-tail asymmetry we expected. Judge quality by")
    print("  Sharpe, not hit-rate.")
    print("=" * 78)


if __name__ == "__main__":
    main()
