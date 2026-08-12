"""
Rotation-chain tracker  (Problem 2) -- STAGE 1: discover the lead-lag order.

Goal of the whole module: given where capital is in the semiconductor chain NOW,
predict the next link, and detect when the cycle has ruptured. Stage 1 lays the
foundation -- it asks whether a stable, ordered lead-lag sequence even EXISTS to
predict along, because a predictor needs a stable order.

Method
------
Chain = NVDA, TSM, ASML, MU, INTC. The dominant driver of all five is the shared
semiconductor beta -- raw cross-correlations would just measure that common move
and manufacture spurious lead-lag. So each name is RESIDUALIZED against a
leave-one-out sector factor (the equal-weight mean of the OTHER four), isolating
its intra-chain relative move. Lead-lag is then measured on the residuals:
  net_lead(i) = sum_j [ mean_k corr(resid_i[t], resid_j[t+k])
                        - mean_k corr(resid_j[t], resid_i[t+k]) ], k=1..K
Ranking names by net_lead gives the DISCOVERED order (most-leading first).

Stage 1 reports:
  1. discovered order vs the thesis order (NVDA->TSM->ASML->MU->INTC)
  2. rank agreement (Spearman) + a permutation p (circular-rotate each residual
     independently to break cross-series timing) -- is the match beyond chance?
  3. STABILITY: re-discover the order in sub-periods; low agreement across
     sub-periods => the order reshuffles => prediction (Stage 2) is not viable.

Run:
    python -m src.chain_rotation
Optional: --lags 10  --iters 2000  --subperiods 4
"""
import argparse

import numpy as np
import pandas as pd

CHAIN = ["NVDA", "TSM", "ASML", "MU", "INTC"]
THESIS = ["NVDA", "TSM", "ASML", "MU", "INTC"]   # your order: leads -> lags


def load_returns(path="processed/asset_returns.parquet"):
    df = pd.read_parquet(path); df.index = pd.to_datetime(df.index)
    df = df.sort_index().dropna(how="all")
    if np.nanmedian(np.abs(df.to_numpy())) > 0.5:
        print("  (input looks like PRICES -> converting to returns)")
        df = df.pct_change()
    return df


def residualize(rets, names):
    """Each name residualized on the equal-weight mean of the OTHER names (OLS)."""
    out = {}
    for i in names:
        others = [n for n in names if n != i]
        factor = rets[others].mean(axis=1).values
        y = rets[i].values
        A = np.vstack([factor, np.ones_like(factor)]).T
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        out[i] = pd.Series(y - A @ beta, index=rets.index)
    return pd.DataFrame(out)


def net_lead(R, names, K):
    """net_lead(i): how much i's residual leads the others, averaged over lags 1..K."""
    net = {}
    for i in names:
        s = 0.0
        for j in names:
            if i == j:
                continue
            fwd = np.nanmean([R[i].corr(R[j].shift(-k)) for k in range(1, K + 1)])  # i leads j
            bwd = np.nanmean([R[j].corr(R[i].shift(-k)) for k in range(1, K + 1)])  # j leads i
            s += fwd - bwd
        net[i] = s
    return pd.Series(net)


def order_from_net(net):
    return list(net.sort_values(ascending=False).index)   # most-leading first


def spearman_vs_thesis(order):
    pos = {n: r for r, n in enumerate(order)}
    thesis_pos = {n: r for r, n in enumerate(THESIS)}
    a = np.array([pos[n] for n in CHAIN])
    b = np.array([thesis_pos[n] for n in CHAIN])
    return pd.Series(a).corr(pd.Series(b), method="spearman")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lags", type=int, default=10)
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--subperiods", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    rets = load_returns()
    missing = [c for c in CHAIN if c not in rets.columns]
    if missing:
        raise SystemExit(f"missing chain tickers: {missing}")
    sub = rets[CHAIN].dropna()
    print("=" * 74)
    print("ROTATION-CHAIN TRACKER -- Stage 1 (discover the lead-lag order)")
    print("=" * 74)
    print(f"chain: {', '.join(CHAIN)}")
    print(f"window: {sub.index.min().date()} -> {sub.index.max().date()} ({len(sub)} days)")
    print(f"lead-lag window: {args.lags} trading days")

    R = residualize(sub, CHAIN)

    # --- discovered order (full sample) ------------------------------------
    net = net_lead(R, CHAIN, args.lags)
    order = order_from_net(net)
    rho = spearman_vs_thesis(order)
    print("\n[1] DISCOVERED ORDER (residualized, full sample)")
    print("    net-lead score (higher = leads the others more):")
    for n in order:
        print(f"      {n:5} {net[n]:+.4f}")
    print(f"    discovered:  {' -> '.join(order)}")
    print(f"    your thesis: {' -> '.join(THESIS)}")
    print(f"    rank agreement (Spearman) = {rho:+.3f}   (+1 = identical order)")

    # --- permutation: is the agreement beyond chance? ----------------------
    Rv = {n: R[n].to_numpy() for n in CHAIN}
    m = len(sub)
    null = np.empty(args.iters)
    for t in range(args.iters):
        Rr = pd.DataFrame({n: np.roll(Rv[n], int(rng.integers(1, m))) for n in CHAIN},
                          index=sub.index)
        null[t] = spearman_vs_thesis(order_from_net(net_lead(Rr, CHAIN, args.lags)))
    p = (np.sum(null >= rho) + 1) / (args.iters + 1)
    print(f"\n[2] PERMUTATION ({args.iters} rotations): p(match >= observed) = {p:.4f}")
    print("    small p => the discovered order matches your thesis beyond chance.")

    # --- stability across sub-periods --------------------------------------
    print(f"\n[3] STABILITY across {args.subperiods} sub-periods (the Stage-2 gate)")
    chunks = np.array_split(np.arange(len(sub)), args.subperiods)
    orders = []
    for c in chunks:
        Rc = R.iloc[c]
        o = order_from_net(net_lead(Rc, CHAIN, args.lags))
        orders.append(o)
        lab = f"{R.index[c[0]].date()}..{R.index[c[-1]].date()}"
        print(f"    {lab}:  {' -> '.join(o)}")
    # mean pairwise Spearman between sub-period orders
    def rank(o): return {n: r for r, n in enumerate(o)}
    agrs = []
    for a in range(len(orders)):
        for b in range(a + 1, len(orders)):
            ra, rb = rank(orders[a]), rank(orders[b])
            agrs.append(pd.Series([ra[n] for n in CHAIN]).corr(
                        pd.Series([rb[n] for n in CHAIN]), method="spearman"))
    mean_agr = float(np.nanmean(agrs))
    print(f"    mean pairwise agreement across sub-periods = {mean_agr:+.3f}")

    print("\n" + "=" * 74)
    print("READING")
    if p < 0.05 and mean_agr > 0.5:
        print("  Order matches thesis beyond chance AND is stable across time ->")
        print("  a predictable rotation exists. Proceed to Stage 2 (positioning +")
        print("  next-link prediction + rupture detection).")
    elif mean_agr <= 0.5:
        print("  Order is NOT stable across sub-periods (agreement <= 0.5). Even if")
        print("  the full-sample order matches the thesis, 'predict the next link'")
        print("  is not viable as-is -- the sequence reshuffles over time. This is a")
        print("  key finding and must be resolved before Stage 2 (e.g. condition the")
        print("  rotation on regime, or accept it only holds in some periods).")
    else:
        print("  Stable-ish but the thesis match is within chance -> the data-driven")
        print("  order differs from the supply-chain thesis. Report the divergence;")
        print("  predict along the DISCOVERED order, not the thesis.")
    print("  CAVEAT: lead-lag in financial residuals is noisy; treat the ordering as")
    print("  a tendency, not a deterministic sequence.")
    print("=" * 74)


if __name__ == "__main__":
    main()
