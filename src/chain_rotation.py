"""
Rotation-chain tracker  (Problem 2) -- STAGE 1: does a stable lead-lag order EXIST?

Chain = NVDA, TSM, ASML, MU, INTC. The dominant driver of all five is the shared
semiconductor beta, so raw cross-correlations would measure that common move and
manufacture spurious lead-lag. Each name is therefore RESIDUALIZED against a
leave-one-out sector factor (equal-weight mean of the OTHER four), and lead-lag
is measured on the residuals:

    d_ij      = mean_k [ corr(resid_i[t], resid_j[t+k]) - corr(resid_j[t], resid_i[t+k]) ]
    net_lead(i) = sum_{j != i} d_ij                                        k = 1..K

Ranking by net_lead gives the DISCOVERED order (most-leading first).

WHAT CHANGED (2026-08-21) AND WHY
---------------------------------
1. LOOK-AHEAD REMOVED (correctness). `residualize()` previously fit ONE beta over
   the whole 1999-2026 sample and `main()` then sliced those residuals per
   sub-period -- so 1999-2005 residuals were built from betas estimated through
   2026, inside a test whose entire purpose is stability OVER TIME. Sub-period
   residualization is now done WITHIN each sub-period.

   The old (contaminated) sub-period orders are still computed and printed beside
   the corrected ones. Keeping the old numbers in view is what caught the
   hard-coded-2024 bug, and it makes this commit auditable despite touching more
   than one thing.

   NOTE: the FULL-SAMPLE beta was always correct for the full-sample test, so
   sections [1] and [2] are unaffected by this fix. Only section [4] moves.

2. EXISTENCE TEST ADDED, distinct from the thesis-match test. The old permutation
   asked "does the discovered order match MY THESIS beyond chance?" A real chain
   with a different order still returns p ~ 0.6 there. Section [3] now asks
   whether ANY ordering structure exists at all, by testing the dispersion of the
   net_lead vector against a null that destroys cross-series timing.

3. PERMUTATION NULL ADDED for the sub-period agreement statistic. The reported
   mean pairwise agreement (-0.250) is a mean of 6 Spearmans on n=5 rankings;
   random reshuffles of 5 items have SD ~ 0.5, so the statistic's standard error
   is ~0.25 and -0.250 sits about ONE SE from zero. It has never had a
   significance test. Now it does, and "anti-stable" is not claimed without one.

4. PER-LAG PROFILE (diagnostic, not a test). net_lead averages k=1..K
   unconditionally. If a real cascade completes in 2 days, lags 3..10 contribute
   noise and dilute it by ~80% -- and widening K makes that WORSE. Section [5]
   prints d_ij per lag so the dilution is visible rather than assumed.

WHAT THIS SCRIPT STILL CANNOT SEE
---------------------------------
It measures UNCONDITIONAL, full-period, single-order lead-lag. Per PROJECT_STATE,
rotation is believed to be EPISODE-LOCAL: event-triggered, with per-episode order
and speed, and interrupted by ruptures. Averaging over episodes with different
orders yields ~0 whether or not chains exist. So a null here does NOT establish
that no chain exists -- it establishes that no chain exists IN THIS ESTIMAND.
That distinction is the whole reason Problem 2 Stage 2 is conditional.

Run:
    python -m src.chain_rotation
    python -m src.chain_rotation --lags 10 --iters 2000 --subperiods 4
    python -m src.chain_rotation --out docs/chain_rotation_results.md
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR

CHAIN = ["NVDA", "TSM", "ASML", "MU", "INTC"]
THESIS = ["NVDA", "TSM", "ASML", "MU", "INTC"]   # supply-chain thesis: leads -> lags


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def load_returns():
    df = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().dropna(how="all")
    if np.nanmedian(np.abs(df.to_numpy())) > 0.5:
        print("  (input looks like PRICES -> converting to returns)")
        df = df.pct_change()
    return df


def residualize(rets, names):
    """Each name residualized on the equal-weight mean of the OTHER names (OLS).

    Fit on EXACTLY the rows passed in. Callers that want sub-period residuals
    must slice the RETURNS and call this per slice -- never slice residuals that
    were fit on a longer span.
    """
    out = {}
    for i in names:
        others = [n for n in names if n != i]
        factor = rets[others].mean(axis=1).values
        y = rets[i].values
        A = np.vstack([factor, np.ones_like(factor)]).T
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        out[i] = pd.Series(y - A @ beta, index=rets.index)
    return pd.DataFrame(out)[names]


# --------------------------------------------------------------------------- #
# lead-lag core (vectorized; verified against the original pandas implementation)
# --------------------------------------------------------------------------- #
def cross_corr_by_lag(Rmat, K):
    """C[k-1][i, j] = corr(R_i[t], R_j[t+k]) for k = 1..K.

    Exactly reproduces R[i].corr(R[j].shift(-k)): pandas drops the trailing k
    NaNs pairwise, which is the same truncation used here, and the ddof=1 in the
    standard deviations cancels against the covariance denominator.
    """
    T, N = Rmat.shape
    C = np.empty((K, N, N))
    for k in range(1, K + 1):
        A, B = Rmat[:-k], Rmat[k:]
        n = A.shape[0]
        Ac, Bc = A - A.mean(0), B - B.mean(0)
        sA, sB = A.std(0, ddof=1), B.std(0, ddof=1)
        cov = Ac.T @ Bc / (n - 1)
        C[k - 1] = cov / np.outer(sA, sB)
    return C


def lead_matrix(Rmat, K):
    """D[i, j] = mean_k [ corr(R_i[t], R_j[t+k]) - corr(R_j[t], R_i[t+k]) ]."""
    Cbar = cross_corr_by_lag(Rmat, K).mean(axis=0)
    return Cbar - Cbar.T


def net_lead_vec(Rmat, K):
    """net_lead(i) = sum_{j != i} D[i, j].  (D has a zero diagonal.)"""
    return lead_matrix(Rmat, K).sum(axis=1)


def _net_lead_pandas(R, names, K):
    """Original implementation, kept ONLY as the reference for the self-test."""
    net = {}
    for i in names:
        s = 0.0
        for j in names:
            if i == j:
                continue
            fwd = np.nanmean([R[i].corr(R[j].shift(-k)) for k in range(1, K + 1)])
            bwd = np.nanmean([R[j].corr(R[i].shift(-k)) for k in range(1, K + 1)])
            s += fwd - bwd
        net[i] = s
    return np.array([net[n] for n in names])


def selftest(R, K):
    """Behaviour-preserving check on real input. Fails loud on any drift."""
    a = net_lead_vec(R[CHAIN].to_numpy(), K)
    b = _net_lead_pandas(R, CHAIN, K)
    err = float(np.max(np.abs(a - b)))
    if err > 1e-10:
        raise SystemExit(
            f"SELF-TEST FAILED: vectorized net_lead differs from the original "
            f"pandas implementation by {err:.3e}. Refusing to report numbers.")
    print(f"  self-test OK: vectorized net_lead matches original to {err:.1e}")


# --------------------------------------------------------------------------- #
# orders and agreement
# --------------------------------------------------------------------------- #
def order_from_net(net, names=CHAIN):
    return [names[i] for i in np.argsort(-np.asarray(net))]


def _rank(order):
    return {n: r for r, n in enumerate(order)}


def spearman_orders(o1, o2):
    r1, r2 = _rank(o1), _rank(o2)
    return pd.Series([r1[n] for n in CHAIN]).corr(
           pd.Series([r2[n] for n in CHAIN]), method="spearman")


def spearman_vs_thesis(order):
    return spearman_orders(order, THESIS)


def mean_pairwise_agreement(orders):
    agr = [spearman_orders(orders[a], orders[b])
           for a in range(len(orders)) for b in range(a + 1, len(orders))]
    return float(np.nanmean(agr)), agr


def rotate(Rmat, rng):
    """Independently circular-rotate each column: destroys CROSS-series timing
    while preserving each series' own autocorrelation and distribution."""
    T = Rmat.shape[0]
    return np.column_stack([np.roll(Rmat[:, j], int(rng.integers(1, T)))
                            for j in range(Rmat.shape[1])])


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (step-down), order preserved."""
    p = np.asarray(pvals, float)
    m = len(p)
    idx = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(idx):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lags", type=int, default=10)
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--subperiods", type=int, default=4)
    ap.add_argument("--seed", type=int, default=None,
                    help="default: config project.random_seed")
    ap.add_argument("--out", type=str, default=None,
                    help="also write a Markdown record to this path")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    K, ITERS, NSUB = args.lags, args.iters, args.subperiods
    log = []

    def say(s=""):
        print(s)
        log.append(s)

    rets = load_returns()
    missing = [c for c in CHAIN if c not in rets.columns]
    if missing:
        raise SystemExit(f"missing chain tickers: {missing}")
    sub = rets[CHAIN].dropna()

    say("=" * 78)
    say("ROTATION-CHAIN TRACKER -- Stage 1 (does a stable lead-lag order exist?)")
    say("=" * 78)
    say(f"chain:   {', '.join(CHAIN)}")
    say(f"window:  {sub.index.min().date()} -> {sub.index.max().date()} "
        f"({len(sub)} days)")
    say(f"lags:    k = 1..{K} trading days | iters {ITERS} | seed {seed}")

    R_full = residualize(sub, CHAIN)
    Rm = R_full.to_numpy()
    selftest(R_full, K)

    # ---- [1] full-sample discovered order ---------------------------------
    net = net_lead_vec(Rm, K)
    order = order_from_net(net)
    rho = spearman_vs_thesis(order)
    say("\n[1] DISCOVERED ORDER (residualized, full sample)")
    say("    net-lead score (higher = leads the others more):")
    for n in order:
        say(f"      {n:5} {net[CHAIN.index(n)]:+.4f}")
    say(f"    discovered:  {' -> '.join(order)}")
    say(f"    thesis:      {' -> '.join(THESIS)}")
    say(f"    rank agreement (Spearman) = {rho:+.3f}   (+1 = identical order)")

    # ---- [2] thesis-match permutation -------------------------------------
    null_rho = np.empty(ITERS)
    for t in range(ITERS):
        null_rho[t] = spearman_vs_thesis(order_from_net(net_lead_vec(rotate(Rm, rng), K)))
    p_thesis = (np.sum(null_rho >= rho) + 1) / (ITERS + 1)
    say(f"\n[2] THESIS-MATCH permutation ({ITERS} rotations): "
        f"p(match >= observed) = {p_thesis:.4f}")
    say("    Tests ONLY whether the discovered order matches the supply-chain")
    say("    thesis. A real chain running in a DIFFERENT order also returns a")
    say("    large p here. Existence is tested in [3], not here.")

    # ---- [3] EXISTENCE test (order-agnostic) ------------------------------
    # Statistic: dispersion of the net_lead vector. If no name systematically
    # leads any other, every net_lead ~ 0 and the spread is small.
    disp = float(np.std(net, ddof=1))
    rng_e = np.random.default_rng(seed + 1)
    D_obs = lead_matrix(Rm, K)
    null_disp = np.empty(ITERS)
    pairs = [(i, j) for i in range(len(CHAIN)) for j in range(i + 1, len(CHAIN))]
    null_pair = np.empty((ITERS, len(pairs)))
    for t in range(ITERS):
        Rr = rotate(Rm, rng_e)
        Dn = lead_matrix(Rr, K)
        null_disp[t] = np.std(Dn.sum(axis=1), ddof=1)
        null_pair[t] = [Dn[i, j] for i, j in pairs]
    p_exist = (np.sum(null_disp >= disp) + 1) / (ITERS + 1)

    say(f"\n[3] EXISTENCE test -- is there ANY ordering structure?")
    say(f"    dispersion of net_lead (SD across the 5 names) = {disp:.4f}")
    say(f"    permutation p (dispersion >= observed)         = {p_exist:.4f}")
    say("    Null: each residual series independently circular-rotated, which")
    say("    destroys cross-series timing but preserves each series' own")
    say("    autocorrelation. This test is agnostic to WHICH order appears.")

    obs_pair = np.array([D_obs[i, j] for i, j in pairs])
    p_pair = [(np.sum(np.abs(null_pair[:, c]) >= abs(obs_pair[c])) + 1) / (ITERS + 1)
              for c in range(len(pairs))]
    p_adj = holm(p_pair)
    say("\n    pairwise directional statistic d_ij (positive = i leads j):")
    say("      pair            d_ij      p      p(Holm)")
    for c, (i, j) in enumerate(pairs):
        star = " *" if p_adj[c] < 0.05 else ""
        say(f"      {CHAIN[i]:>5} -> {CHAIN[j]:<5} {obs_pair[c]:+.4f}  "
            f"{p_pair[c]:.4f}  {p_adj[c]:.4f}{star}")
    n_sig = int(np.sum(p_adj < 0.05))
    say(f"    {n_sig} of {len(pairs)} pairs significant after Holm correction.")

    # ---- [4] stability across sub-periods ---------------------------------
    say(f"\n[4] STABILITY across {NSUB} sub-periods")
    chunks = np.array_split(np.arange(len(sub)), NSUB)

    orders_fixed, orders_bug, labels = [], [], []
    for c in chunks:
        labels.append(f"{sub.index[c[0]].date()}..{sub.index[c[-1]].date()}")
        # CORRECTED: residualize WITHIN the sub-period (no look-ahead)
        Rc = residualize(sub.iloc[c], CHAIN).to_numpy()
        orders_fixed.append(order_from_net(net_lead_vec(Rc, K)))
        # OLD, CONTAMINATED: slice residuals fit on the full 1999-2026 sample
        orders_bug.append(order_from_net(net_lead_vec(Rm[c], K)))

    say("    CORRECTED -- betas fit within each sub-period:")
    for lab, o in zip(labels, orders_fixed):
        say(f"      {lab}:  {' -> '.join(o)}")
    say("    OLD (look-ahead) -- betas fit through 2026, kept for comparison:")
    for lab, o in zip(labels, orders_bug):
        say(f"      {lab}:  {' -> '.join(o)}")
    moved = sum(a != b for of, ob in zip(orders_fixed, orders_bug)
                for a, b in zip(of, ob))
    say(f"    name-slots changed by removing the look-ahead: {moved} / "
        f"{NSUB * len(CHAIN)}")

    agr_fixed, _ = mean_pairwise_agreement(orders_fixed)
    agr_bug, _ = mean_pairwise_agreement(orders_bug)
    say(f"    mean pairwise agreement  CORRECTED = {agr_fixed:+.3f}   "
        f"(old, look-ahead = {agr_bug:+.3f})")

    # permutation null for the agreement statistic
    rng_s = np.random.default_rng(seed + 2)
    sub_rets = [sub.iloc[c] for c in chunks]
    null_agr = np.empty(ITERS)
    Rc_list = [residualize(s, CHAIN).to_numpy() for s in sub_rets]
    for t in range(ITERS):
        os_ = [order_from_net(net_lead_vec(rotate(Rc, rng_s), K)) for Rc in Rc_list]
        null_agr[t], _ = mean_pairwise_agreement(os_)
    # two-sided: is the observed agreement distinguishable from reshuffling at all?
    p_agr = (np.sum(np.abs(null_agr) >= abs(agr_fixed)) + 1) / (ITERS + 1)
    say(f"    permutation null: mean {null_agr.mean():+.3f}, "
        f"SD {null_agr.std(ddof=1):.3f}")
    say(f"    p(|agreement| >= observed) = {p_agr:.4f}")
    say("    This is the test the statistic never had. Without it, a value near")
    say("    zero cannot be called 'anti-stable' -- with 5-item rankings the")
    say("    sampling SD alone is of the same size as the observed value.")

    # ---- [5] per-lag profile (diagnostic) ---------------------------------
    say(f"\n[5] PER-LAG PROFILE (diagnostic, not a test)")
    C = cross_corr_by_lag(Rm, K)
    say("    d_ij by lag k -- if a cascade completes fast, lags beyond its length")
    say("    contribute noise and DILUTE the k=1..K average that [1] reports.")
    header = "      pair          " + "".join(f"  k={k:<2}" for k in range(1, K + 1))
    say(header)
    for i, j in pairs:
        prof = C[:, i, j] - C[:, j, i]
        say(f"      {CHAIN[i]:>5} -> {CHAIN[j]:<5} " +
            "".join(f" {v:+.3f}" for v in prof))
    peak = {}
    for i, j in pairs:
        prof = C[:, i, j] - C[:, j, i]
        peak[f"{CHAIN[i]}->{CHAIN[j]}"] = int(np.argmax(np.abs(prof))) + 1
    say(f"    peak |d_ij| lag per pair: " +
        ", ".join(f"{k}:{v}d" for k, v in peak.items()))

    # ---- reading ----------------------------------------------------------
    say("\n" + "=" * 78)
    say("READING")
    say(f"  Existence  [3]: p = {p_exist:.4f}, {n_sig}/{len(pairs)} pairs after Holm.")
    say(f"  Thesis     [2]: p = {p_thesis:.4f} (agreement {rho:+.3f}).")
    say(f"  Stability  [4]: agreement {agr_fixed:+.3f}, p = {p_agr:.4f}.")
    say("")
    if p_exist < 0.05 and n_sig > 0:
        say("  Ordering structure EXISTS in this estimand. Whether it matches the")
        say("  supply-chain thesis is a separate question, answered in [2].")
    else:
        say("  NO ordering structure detectable in this estimand. Note what that")
        say("  does and does not mean: this test measures UNCONDITIONAL, single-")
        say("  order, full-period lead-lag. If rotation is episode-local with")
        say("  per-episode order and speed, averaging across episodes yields ~0")
        say("  whether or not chains exist. A null here is consistent with both")
        say("  'no chain' and 'chains that this instrument cannot see'.")
    say("")
    if p_agr >= 0.05:
        say("  Sub-period orders are INDISTINGUISHABLE FROM RANDOM RESHUFFLING.")
        say("  That is the defensible claim. 'Anti-stable' is NOT supported and")
        say("  is not claimed.")
    else:
        say("  Sub-period agreement is distinguishable from random reshuffling.")
        say(f"  Sign matters: {agr_fixed:+.3f} -- positive means a persistent")
        say("  order, negative means systematic reversal. Report which.")
    say("")
    say("  Literature context: Molchanov & Stangl tested cross-sector")
    say("  predictability across 2,640 t-statistics and found scant evidence of")
    say("  sector rotation; Jacobsen, Stangl & Visaltanachoti granted perfect")
    say("  foresight of cycle stages and still got at best ~2.3%/yr. An")
    say("  unconditional null here REPLICATES published findings. The")
    say("  differentiated angle is the conditioning, not a better unconditional")
    say("  chain search.")
    say("=" * 78)

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Rotation chain -- Stage 1 results\n\n```\n"
                     + "\n".join(log) + "\n```\n")
        print(f"\n  written -> {p}")


if __name__ == "__main__":
    main()
