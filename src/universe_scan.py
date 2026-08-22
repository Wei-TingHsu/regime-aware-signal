"""
universe_scan.py -- ALL directed pairs in the universe, one honest test.

WHY THIS EXISTS
    Every rotation test so far was pre-registered: a basket and an order chosen
    in advance, then tested. That is the only way to get a trustworthy p-value,
    but it is LOSSY -- it can only ever test what someone thought to write down.
    A real lead-lag pair in a basket nobody imagined would never be found.

    The naive fix -- test every 5-asset basket -- is arithmetically hopeless.
    C(47,5) = 1,533,939 baskets, and at alpha=0.05 roughly 77,000 would look
    "significant" on data with no structure at all.

    The honest fix changes the UNIT from baskets to ORDERED PAIRS, and corrects
    for the search itself:

        1. Compute d_ij(k) for EVERY ordered pair at every lag k=1..K.
           C(47,2) = 1,081 pairs x K lags.
        2. Take the MAXIMUM |d| across the whole matrix.
        3. Build the null distribution OF THAT MAXIMUM by independently
           circular-rotating every series and recomputing the maximum.

    A pair is significant only if it beats the distribution of maxima -- which
    automatically accounts for having looked at all of them. This is the White
    reality-check / Westfall-Young construction, and it is far less
    conservative than Bonferroni because the pairs are heavily correlated.

WHAT IT REPORTS
    Both the NAIVE per-pair p (what you would get testing that pair alone) and
    the UNIVERSE-ADJUSTED p. The gap between the two counts is the point: it
    shows exactly how many "findings" the search itself manufactures.

STATUS
    EXPLORATORY BY CONSTRUCTION. Run after five pre-registered nulls, on the
    same data. It cannot produce a confirmatory result -- a surviving pair
    would be a candidate requiring out-of-sample confirmation, not a finding.

Run:
    python -m src.universe_scan
    python -m src.universe_scan --residualize none --lags 5 --min-history 2500
"""
import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config
from src.chain_rotation import cross_corr_by_lag
from src.episode_rotation import load_panel


def build_matrix(panel, min_history, factor_name, residualize):
    """Filter to assets with enough history, take their common window."""
    counts = panel.notna().sum()
    keep = [c for c in panel.columns if counts[c] >= min_history]
    dropped = sorted(set(panel.columns) - set(keep))
    sub = panel[keep].dropna()
    print(f"  {len(keep)}/{len(panel.columns)} assets with >= {min_history} "
          f"sessions; window {sub.index[0].date()} -> {sub.index[-1].date()} "
          f"({len(sub)} sessions)")
    if dropped:
        print(f"  dropped (short history): {', '.join(dropped)}")

    if residualize == "market":
        if factor_name not in sub.columns:
            raise SystemExit(f"--factor {factor_name} not among the kept assets")
        f = sub[factor_name].to_numpy()
        A = np.vstack([f, np.ones_like(f)]).T
        out = sub.copy()
        for c in sub.columns:
            if c == factor_name:
                continue
            beta, *_ = np.linalg.lstsq(A, sub[c].to_numpy(), rcond=None)
            out[c] = sub[c].to_numpy() - A @ beta
        out = out.drop(columns=[factor_name])
        print(f"  residualized on {factor_name} (full-sample beta -- declared "
              f"look-ahead, acceptable for an exploratory scan, flagged)")
        return out
    return sub


def max_pair_d(M, K):
    """Per-pair max |d| over lags, plus the global maximum."""
    C = cross_corr_by_lag(M, K)                 # (K, N, N)
    D = C - np.transpose(C, (0, 2, 1))          # antisymmetric per lag
    iu = np.triu_indices(M.shape[1], k=1)
    per_pair = np.max(np.abs(D[:, iu[0], iu[1]]), axis=0)
    return per_pair, float(per_pair.max()), D


def rotate_all(M, rng):
    T = M.shape[0]
    return np.column_stack([np.roll(M[:, j], int(rng.integers(1, T)))
                            for j in range(M.shape[1])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lags", type=int, default=5)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--min-history", type=int, default=2500)
    ap.add_argument("--residualize", choices=["market", "none"], default="market")
    ap.add_argument("--factor", default="SPY")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    log = []

    def say(s=""):
        print(s); log.append(s)

    panel = load_panel()
    df = build_matrix(panel, args.min_history, args.factor, args.residualize)
    names = list(df.columns)
    M = df.to_numpy()
    N = len(names)
    pairs = list(combinations(range(N), 2))

    say("=" * 78)
    say("UNIVERSE-WIDE DIRECTED-PAIR SCAN -- maximum-statistic null")
    say("=" * 78)
    say(f"assets:    {N}")
    say(f"window:    {df.index[0].date()} -> {df.index[-1].date()} "
        f"({len(df)} sessions)")
    say(f"residual:  {args.residualize}"
        + (f" (factor {args.factor}, removed from the universe)"
           if args.residualize == "market" else ""))
    say(f"pairs:     {len(pairs)} x {args.lags} lags = "
        f"{len(pairs)*args.lags} directed tests")
    say(f"iters {args.iters} | seed {seed}")
    say("")
    say("EXPLORATORY BY CONSTRUCTION: run after five pre-registered nulls, on")
    say("the same data. A surviving pair is a CANDIDATE for out-of-sample")
    say("confirmation, not a finding.")

    obs_pair, obs_max, D = max_pair_d(M, args.lags)

    null_pair = np.empty((args.iters, len(pairs)))
    null_max = np.empty(args.iters)
    for t in range(args.iters):
        pp, mx, _ = max_pair_d(rotate_all(M, rng), args.lags)
        null_pair[t] = pp
        null_max[t] = mx

    p_naive = (np.sum(null_pair >= obs_pair, axis=0) + 1) / (args.iters + 1)
    p_adj = (np.sum(null_max[:, None] >= obs_pair, axis=0) + 1) / (args.iters + 1)

    n_naive = int(np.sum(p_naive < 0.05))
    n_adj = int(np.sum(p_adj < 0.05))

    say(f"\n[1] THE COST OF SEARCHING")
    say(f"    observed maximum |d| across the universe = {obs_max:.4f}")
    say(f"    null distribution of the MAXIMUM: mean {null_max.mean():.4f}, "
        f"SD {null_max.std(ddof=1):.4f}, 95th pct {np.percentile(null_max,95):.4f}")
    say(f"    pairs significant at NAIVE p<0.05 (no correction): "
        f"{n_naive} of {len(pairs)}")
    say(f"    pairs significant after UNIVERSE-WIDE correction:  "
        f"{n_adj} of {len(pairs)}")
    say(f"    expected naive false positives under the null: "
        f"~{0.05*len(pairs):.0f}")
    say("    The gap between those counts is what the search manufactures.")

    say(f"\n[2] TOP {args.top} PAIRS BY |d|")
    say("      leader -> follower      d       lag   p(naive)  p(universe)")
    order = np.argsort(-obs_pair)[: args.top]
    C = cross_corr_by_lag(M, args.lags)
    Dk = C - np.transpose(C, (0, 2, 1))
    for c in order:
        i, j = pairs[c]
        prof = Dk[:, i, j]
        k = int(np.argmax(np.abs(prof))) + 1
        d = prof[k - 1]
        a, b = (names[i], names[j]) if d > 0 else (names[j], names[i])
        star = " *" if p_adj[c] < 0.05 else ""
        say(f"      {a:>6} -> {b:<6} {abs(d):.4f}   k={k}   "
            f"{p_naive[c]:.4f}    {p_adj[c]:.4f}{star}")

    say("\n" + "=" * 78)
    say("READING")
    if n_adj == 0:
        say(f"  NO directed pair in the universe survives correction for having")
        say(f"  searched it. {n_naive} pairs clear a naive threshold -- against")
        say(f"  ~{0.05*len(pairs):.0f} expected by chance alone -- and none clears the")
        say(f"  maximum-statistic null. This is the broad sweep the")
        say(f"  pre-registered tests could not provide: the nulls were not an")
        say(f"  artifact of testing the wrong baskets.")
    else:
        say(f"  {n_adj} pair(s) survive universe-wide correction. These are")
        say(f"  CANDIDATES, not findings: the scan is exploratory and used the")
        say(f"  same data as everything else. Next step is a pre-registered")
        say(f"  out-of-sample test on a period this scan did not see.")
    say("")
    say("  Scope: unconditional, full-sample, linear lead-lag at lags "
        f"1..{args.lags}.")
    say("  It cannot see nonlinear relationships, episode-local structure that")
    say("  averages to zero unconditionally, or lags beyond the window.")
    say("=" * 78)

    if args.out:
        p_ = Path(args.out); p_.parent.mkdir(parents=True, exist_ok=True)
        p_.write_text("# Universe-wide directed-pair scan\n\n```\n"
                      + "\n".join(log) + "\n```\n")
        print(f"\n  written -> {p_}")


if __name__ == "__main__":
    main()
