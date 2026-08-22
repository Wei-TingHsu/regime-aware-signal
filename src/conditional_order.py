"""
conditional_order.py -- does the ROTATION ORDER depend on the MACRO ENVIRONMENT?

THE HYPOTHESIS
    Every rotation test so far assumed ONE universal sequence. Statistic [2] of
    episode_rotation asks whether the same order recurs across ALL episodes --
    so if bonds lead in one macro environment and equities lead in another, the
    pooled statistic returns ~0 even when BOTH sequences are real and perfectly
    repeatable within their own environment. That is the "variable order"
    dilution recorded in architecture_decisions.md, and it has never been
    tested because there was no conditioning variable in the rotation engine.

    This module conditions on the GMM macro regime holding on the trigger date.

WHY THIS IS ONE TEST AND NOT TWELVE
    The tempting design -- test each regime separately, report whichever is
    significant -- is a fishing licence, especially having already seen the
    pooled result fail. The hypothesis instead makes ONE falsifiable prediction:

        If environment determines order, then grouping episodes by regime
        raises WITHIN-GROUP order agreement above the POOLED agreement.

    Statistic [A] is that single quantity, with a null that shuffles regime
    labels ACROSS episodes -- preserving group sizes and every episode path,
    destroying only the correspondence between environment and order.

    Statistic [B] tests "bonds lead first" -- the significance test the
    first-mover counts have never had. Null is the same per-name episode
    shuffle used elsewhere: each name keeps its own response-timing
    distribution, but cross-name alignment within an episode is destroyed.

    Per-regime order tables are printed as DESCRIPTIVE output. They are not
    tested and must not be reported as findings.

REGIME LABELS ARE CANONICAL
    Components are re-indexed by their mean coordinate on the data-driven
    stress axis (the PC most correlated with VIX), so R0 is always the calmest
    state and R(n-1) the most stressed on every run. Raw GMM component indices
    are NOT comparable across refits (label permutation, diagnosed 2026-08-21).

Run:
    python -m src.conditional_order --chain TLT,SPY,GLD,UUP,USO \
        --residualize none --shock-on SPY --shock-sign down --eplen 15 \
        --out docs/cond_order_crossasset.md
"""
import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from src.data_io import load_config, PROCESSED_DIR
from src.episode_rotation import (load_panel, load_chain_returns, trigger_shock,
                                  trigger_stress, trigger_file, decluster,
                                  build_episodes, half_max_times, shuffle_names,
                                  _sign_matrix)

CLUSTERING_PCS = ["PC1", "PC2", "PC3"]


def canonical_regimes(cfg):
    """Fit once; re-index components calm -> stressed along the stress axis."""
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    macro = pd.read_parquet(PROCESSED_DIR / "macro_panel.parquet")
    macro.index = pd.to_datetime(macro.index)
    n = int(cfg["regime"]["n_regimes"])
    X = scores[CLUSTERING_PCS].values
    gm = GaussianMixture(n_components=n,
                         covariance_type=cfg["regime"]["covariance_type"],
                         max_iter=cfg["regime"]["max_iter"],
                         n_init=cfg["regime"]["n_init"],
                         random_state=cfg["project"]["random_seed"]).fit(X)
    raw = gm.predict(X)
    common = scores.index.intersection(macro.index)
    vix = macro.loc[common, "VIXCLS"]
    corrs = {pc: abs(scores.loc[common, pc].corr(vix)) for pc in CLUSTERING_PCS}
    spc = max(corrs, key=corrs.get)
    axis = CLUSTERING_PCS.index(spc)
    sign = np.sign(scores.loc[common, spc].corr(vix)) or 1.0
    order = np.argsort(gm.means_[:, axis] * sign)
    remap = np.empty(n, int); remap[order] = np.arange(n)
    return pd.Series(remap[raw], index=scores.index), n, spc, float(corrs[spc])


def tau_matrix(times):
    S = _sign_matrix(times)
    nz = (S != 0).sum(axis=1).astype(float)
    P = S @ S.T
    den = np.sqrt(np.outer(nz, nz))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, P / den, np.nan)


def pooled_tau(tau):
    iu = np.triu_indices(tau.shape[0], k=1)
    return float(np.nanmean(tau[iu]))


def within_tau(tau, groups):
    """Mean pairwise tau among episodes SHARING a regime label."""
    num, den = 0.0, 0
    for g in np.unique(groups):
        idx = np.where(groups == g)[0]
        if len(idx) < 2:
            continue
        sub = tau[np.ix_(idx, idx)]
        iu = np.triu_indices(len(idx), k=1)
        v = sub[iu]
        num += np.nansum(v); den += int(np.sum(~np.isnan(v)))
    return num / den if den else np.nan


def first_mover_stat(times):
    """Concentration of the first-mover distribution vs uniform."""
    E, N = times.shape
    c = np.bincount(times.argmin(axis=1), minlength=N) / E
    return float(np.sum((c - 1.0 / N) ** 2)), c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain", required=True)
    ap.add_argument("--trigger", choices=["shock", "stress", "file"], default="shock")
    ap.add_argument("--gdelt"); ap.add_argument("--dates")
    ap.add_argument("--shock-on"); ap.add_argument("--shock-sign", default="both")
    ap.add_argument("--residualize", choices=["loo", "market", "none"], default="loo")
    ap.add_argument("--factor", default="SPY")
    ap.add_argument("--z", type=float, default=None)
    ap.add_argument("--eplen", type=int, default=15)
    ap.add_argument("--beta-win", type=int, default=250)
    ap.add_argument("--min-beta-obs", type=int, default=120)
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    chain = [c.strip() for c in args.chain.split(",")]
    z = args.z if args.z is not None else (2.0 if args.trigger == "shock" else 1.5)
    log = []

    def say(s=""):
        print(s); log.append(s)

    panel = load_panel()
    rets = load_chain_returns(chain, panel)
    factor = panel[args.factor] if args.residualize == "market" else None
    reg, NREG, spc, scorr = canonical_regimes(cfg)

    if args.trigger == "shock":
        proxy = panel[args.shock_on] if args.shock_on else None
        raw, info = trigger_shock(rets, z, proxy, args.shock_on or "eq-weight chain",
                                  args.shock_sign)
    elif args.trigger == "stress":
        raw, info = trigger_stress(args.gdelt, rets.index, z)
    else:
        raw, info = trigger_file(args.dates, rets.index)

    kept = decluster(raw, rets.index, gap=args.eplen)
    T, meta, dropped = build_episodes(rets, kept, args.eplen, args.beta_win,
                                      args.min_beta_obs, chain,
                                      mode=args.residualize, factor=factor)
    if len(T) < 20:
        raise SystemExit(f"only {len(T)} episodes -- not enough to condition on.")

    trig = pd.DatetimeIndex([pd.Timestamp(m["trigger"]) for m in meta])
    g = reg.reindex(trig, method="ffill")
    ok = ~g.isna().values
    T, groups = T[ok], g.values[ok].astype(int)
    trig = trig[ok]

    say("=" * 78)
    say("ENVIRONMENT-CONDITIONAL ORDER -- does the sequence depend on the regime?")
    say("=" * 78)
    say(f"chain:     {', '.join(chain)}")
    say(f"detector:  {info['detector']}")
    say(f"residual:  {args.residualize}")
    say(f"episodes:  {len(T)} (eplen {args.eplen}) | iters {args.iters} | seed {seed}")
    say(f"regimes:   {NREG}, canonically ordered calm->stressed by {spc} "
        f"(|corr| VIX {scorr:.2f})")
    cnt = pd.Series(groups).value_counts().sort_index()
    say("    episodes per regime: " +
        ", ".join(f"R{k}={v}" for k, v in cnt.items()))
    thin = [f"R{k}" for k, v in cnt.items() if v < 10]
    if thin:
        say(f"    THIN GROUPS (<10 episodes): {', '.join(thin)} -- these "
            f"contribute little and their per-regime tables mean nothing.")

    times = half_max_times(T)
    tau = tau_matrix(times)
    pt, wt = pooled_tau(tau), within_tau(tau, groups)
    obs = wt - pt

    say(f"\n[A] DOES CONDITIONING ON REGIME RAISE ORDER AGREEMENT?")
    say(f"    pooled  mean pairwise tau = {pt:+.4f}")
    say(f"    within-regime  mean tau   = {wt:+.4f}")
    say(f"    lift (within - pooled)    = {obs:+.4f}")
    null = np.empty(args.iters)
    for t in range(args.iters):
        null[t] = within_tau(tau, rng.permutation(groups)) - pt
    p_a = (np.sum(null >= obs) + 1) / (args.iters + 1)
    say(f"    null (regime labels shuffled across episodes): "
        f"mean {null.mean():+.4f}, SD {null.std(ddof=1):.4f}")
    say(f"    p(lift >= observed) = {p_a:.4f}")
    say("    Null preserves group SIZES and every episode path; it destroys")
    say("    only the correspondence between environment and order. ONE test.")

    say(f"\n[B] IS THERE A CONSISTENT FIRST MOVER?")
    s_obs, c_obs = first_mover_stat(times)
    nb = np.empty(args.iters)
    for t in range(args.iters):
        nb[t] = first_mover_stat(half_max_times(shuffle_names(T, rng)))[0]
    p_b = (np.sum(nb >= s_obs) + 1) / (args.iters + 1)
    say("    first-mover share (uniform would be "
        f"{100.0/len(chain):.0f}%):")
    for n_, c_ in sorted(zip(chain, c_obs), key=lambda x: -x[1]):
        say(f"      {n_:6} {c_:6.1%}")
    say(f"    concentration statistic = {s_obs:.5f}")
    say(f"    null mean {nb.mean():.5f}, SD {nb.std(ddof=1):.5f}")
    say(f"    p(concentration >= observed) = {p_b:.4f}")

    say(f"\n[C] PER-REGIME ORDERS -- DESCRIPTIVE ONLY, NOT TESTED")
    say("    Median half-max response day per asset, by regime. Do NOT report")
    say("    these as findings: no significance test is applied, and with a")
    say(f"    handful of episodes per regime the orders are unstable.")
    for k in sorted(np.unique(groups)):
        idx = np.where(groups == k)[0]
        med = np.median(times[idx], axis=0)
        order = [chain[i] for i in np.argsort(med)]
        say(f"      R{k} (n={len(idx):3d}): {' -> '.join(order)}   "
            f"median days {np.sort(med).astype(int).tolist()}")

    say("\n" + "=" * 78)
    say("READING")
    say(f"  Conditioning lift [A]: {obs:+.4f}, p = {p_a:.4f}")
    say(f"  First-mover       [B]: p = {p_b:.4f}")
    say("")
    if p_a < 0.05:
        say("  ORDER IS ENVIRONMENT-CONDITIONAL. Grouping by regime raises")
        say("  agreement beyond what shuffled labels produce. The pooled nulls")
        say("  were a dilution artifact, and per-regime sequences are worth")
        say("  estimating -- with a fresh pre-registration and an out-of-sample")
        say("  split, since these episodes are now spent.")
    else:
        say("  NO conditioning lift. Grouping episodes by macro regime does not")
        say("  raise order agreement above shuffled labels. The pooled nulls")
        say("  were NOT a dilution artifact: there is no environment-specific")
        say("  sequence hiding inside them, at this regime resolution and this")
        say("  episode count.")
    if p_b < 0.05:
        say("  A consistent first mover EXISTS -- see the shares above. Note")
        say("  this is weaker than a full sequence: knowing who moves first")
        say("  does not tell you the order of everyone else.")
    else:
        say("  No consistent first mover. The observed shares are within what")
        say("  the shuffle null produces.")
    say("=" * 78)

    if args.out:
        p_ = Path(args.out); p_.parent.mkdir(parents=True, exist_ok=True)
        p_.write_text("# Environment-conditional order\n\n```\n"
                      + "\n".join(log) + "\n```\n")
        print(f"\n  written -> {p_}")


if __name__ == "__main__":
    main()
