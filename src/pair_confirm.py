"""
pair_confirm.py -- deeper test of a PRE-SPECIFIED directed pair.

Two pairs survived the rotation runs as ladder-stable observations:
    SPY -> GLD  at k=1  (cross-asset, risk-off trigger, no residualization)
    SOXX -> XAR at k=3  (sector, bidirectional trigger, SPY-factor residual)

Both were DISCOVERED after seeing the data. This module asks the two questions
that discovery cannot answer.

  [1] DOES IT HOLD OUT OF SAMPLE?
      Episodes are split TEMPORALLY in half and the pair is tested separately
      in each. A pair that lives in one half is a period artifact. Because the
      pair is now pre-specified, only ONE test is run per half -- no Holm
      burden across 10 pairs, which is a large power gain over the discovery
      runs.

      This is NOT a clean out-of-sample test: the pair was chosen after seeing
      the full sample, so both halves are contaminated by the selection. It
      tests STABILITY, which is weaker than replication and is reported as such.

  [2] IS IT WORTH MORE THAN THE SPREAD?
      d = 0.17 is a correlation, not money. The economic test takes the
      tradeable version: on each day t of an episode, take the leader's sign
      and hold the follower for the next k sessions. Mean payoff per trade is
      reported in bps against a round-trip cost estimate, with a BLOCK
      bootstrap (resampling whole episodes) so the within-episode clustering
      is not thrown away.

      A statistically real effect that nets below costs is not a product.

Run:
    python -m src.pair_confirm --chain TLT,SPY,GLD,UUP,USO --residualize none \
        --shock-on SPY --shock-sign down --pair SPY,GLD --lag 1 --eplen 15

    python -m src.pair_confirm --chain SOXX,XAR,XLE,XLV,XLP --residualize market \
        --factor SPY --shock-on SPY --shock-sign both --pair SOXX,XAR --lag 3 --eplen 15
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config
from src.episode_rotation import (load_panel, load_chain_returns, trigger_shock,
                                  trigger_stress, trigger_file, decluster,
                                  build_episodes, pooled_lead, shuffle_names)

COST_BPS = 4.0          # round-trip estimate for liquid ETFs (2bps each way)


def pair_d(T, i, j, k):
    return pooled_lead(T, k)[i, j]


def pair_p(T, i, j, k, iters, rng):
    """One-sided p on |d| for a PRE-SPECIFIED pair -- no Holm, one test."""
    obs = abs(pair_d(T, i, j, k))
    null = np.empty(iters)
    for t in range(iters):
        null[t] = abs(pair_d(shuffle_names(T, rng), i, j, k))
    return (np.sum(null >= obs) + 1) / (iters + 1), null


def economic(T, i, j, k, rng, iters=5000):
    """Sign-of-leader -> hold follower k sessions. Block bootstrap by episode."""
    sig = np.sign(T[:, :-k, i])
    pay = sig * T[:, k:, j]                       # (E, L-k)
    per_ep = pay.mean(axis=1)                     # episode-level mean payoff
    obs = float(per_ep.mean())
    E = len(per_ep)
    boot = np.array([per_ep[rng.integers(0, E, E)].mean() for _ in range(iters)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    p = (np.sum(boot <= 0) + 1) / (iters + 1) if obs > 0 else \
        (np.sum(boot >= 0) + 1) / (iters + 1)
    return dict(mean=obs, lo=lo, hi=hi, p=p, hit=float((pay > 0).mean()),
                n=int(pay.size), n_ep=E)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain", required=True)
    ap.add_argument("--pair", required=True, help="LEADER,FOLLOWER")
    ap.add_argument("--lag", type=int, required=True)
    ap.add_argument("--trigger", choices=["shock", "stress", "file"], default="shock")
    ap.add_argument("--gdelt"); ap.add_argument("--dates")
    ap.add_argument("--shock-on"); ap.add_argument("--shock-sign", default="both")
    ap.add_argument("--residualize", choices=["loo", "market", "none"], default="loo")
    ap.add_argument("--factor", default="SPY")
    ap.add_argument("--z", type=float, default=None)
    ap.add_argument("--eplen", type=int, default=15)
    ap.add_argument("--beta-win", type=int, default=250)
    ap.add_argument("--min-beta-obs", type=int, default=120)
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    chain = [c.strip() for c in args.chain.split(",")]
    lead, foll = [s.strip() for s in args.pair.split(",")]
    i, j = chain.index(lead), chain.index(foll)
    k = args.lag
    z = args.z if args.z is not None else (2.0 if args.trigger == "shock" else 1.5)
    log = []

    def say(s=""):
        print(s); log.append(s)

    panel = load_panel()
    rets = load_chain_returns(chain, panel)
    factor = panel[args.factor] if args.residualize == "market" else None

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

    say("=" * 78)
    say(f"PAIR CONFIRMATION -- {lead} -> {foll} at lag {k}")
    say("=" * 78)
    say(f"chain:     {', '.join(chain)}")
    say(f"detector:  {info['detector']}")
    say(f"residual:  {args.residualize}"
        + (f" (factor {args.factor})" if args.residualize == "market" else ""))
    say(f"episodes:  {len(T)} (eplen {args.eplen}) | iters {args.iters} | seed {seed}")
    say("")
    say("The pair is PRE-SPECIFIED, so each test below is a SINGLE test -- no")
    say("Holm correction over 10 pairs. But the pair was CHOSEN after seeing the")
    say("full sample, so this measures STABILITY, not replication.")

    if len(T) < 20:
        say(f"\nONLY {len(T)} EPISODES. Split-half leaves <10 per half; "
            f"nothing below is interpretable.")
        return

    # ---- [1] full sample ---------------------------------------------------
    d_all = pair_d(T, i, j, k)
    p_all, _ = pair_p(T, i, j, k, args.iters, rng)
    say(f"\n[1] FULL SAMPLE:  d = {d_all:+.4f}   p = {p_all:.4f}   "
        f"({len(T)} episodes)")

    # ---- [2] temporal split ------------------------------------------------
    half = len(T) // 2
    say(f"\n[2] TEMPORAL SPLIT (episodes are in date order)")
    dates = [m["trigger"] for m in meta]
    res = {}
    for name, sl in [("FIRST half", slice(0, half)), ("SECOND half", slice(half, None))]:
        Ts = T[sl]
        d = pair_d(Ts, i, j, k)
        p, _ = pair_p(Ts, i, j, k, args.iters, rng)
        span = f"{dates[sl][0]} .. {dates[sl][-1]}"
        res[name] = (d, p)
        star = " *" if p < 0.05 else ""
        say(f"    {name:12} {span}  n={len(Ts):3d}   "
            f"d = {d:+.4f}   p = {p:.4f}{star}")

    d1, d2 = res["FIRST half"][0], res["SECOND half"][0]
    same_sign = np.sign(d1) == np.sign(d2)
    ratio = abs(d1 / d2) if d2 != 0 else np.inf
    say(f"    sign agreement: {'YES' if same_sign else 'NO'} | "
        f"magnitude ratio {ratio:.2f} (1.0 = identical)")
    if not same_sign:
        say("    SIGN FLIPS ACROSS HALVES -- the effect is not stable in time.")
    elif max(ratio, 1 / ratio) > 3:
        say("    Same sign but magnitudes differ by >3x -- concentrated in one period.")

    # ---- [3] economic significance ----------------------------------------
    say(f"\n[3] ECONOMIC SIGNIFICANCE")
    say(f"    Rule: on each episode day t, take sign({lead}) and hold {foll}")
    say(f"    for {k} session(s). Block bootstrap resamples whole episodes.")
    e = economic(T, i, j, k, rng)
    say(f"    mean payoff   = {e['mean']*1e4:+.2f} bps per trade "
        f"(95% CI {e['lo']*1e4:+.2f} .. {e['hi']*1e4:+.2f})")
    say(f"    hit rate      = {e['hit']:.1%}   trades = {e['n']} "
        f"across {e['n_ep']} episodes")
    say(f"    bootstrap p   = {e['p']:.4f}")
    net = e['mean'] * 1e4 - COST_BPS
    say(f"    round-trip cost assumption {COST_BPS:.1f} bps -> "
        f"NET {net:+.2f} bps per trade")
    if net <= 0:
        say(f"    NET NEGATIVE. Statistically detectable, not economically")
        say(f"    tradeable at this cost assumption. A signal that does not")
        say(f"    clear the spread is not a product.")
    elif e['lo'] * 1e4 - COST_BPS <= 0:
        say(f"    Net positive at the point estimate, but the 95% CI lower")
        say(f"    bound does not clear costs. Not established.")
    else:
        say(f"    Net positive with the CI lower bound clearing costs.")

    # ---- reading -----------------------------------------------------------
    say("\n" + "=" * 78)
    say("READING")
    stable = same_sign and max(ratio, 1 / ratio) <= 3
    say(f"  Stability [2]: {'PASS' if stable else 'FAIL'} "
        f"(sign {'agrees' if same_sign else 'FLIPS'}, ratio {ratio:.2f})")
    say(f"  Economics [3]: net {net:+.2f} bps vs {COST_BPS:.1f} bps cost")
    say("")
    if stable and net > 0 and e['lo'] * 1e4 - COST_BPS > 0:
        say("  The pair is time-stable AND clears costs. This is the only")
        say("  configuration in which it is a candidate product component.")
        say("  Next: forward-test it live, pre-registered, before any claim.")
    elif stable:
        say("  Time-stable but does not clear costs. Report as a documented")
        say("  market-structure observation, NOT as a tradeable signal.")
    else:
        say("  Not time-stable. The ladder consistency seen at discovery came")
        say("  from overlapping episodes, not from a persistent effect.")
    say("=" * 78)

    if args.out:
        p_ = Path(args.out); p_.parent.mkdir(parents=True, exist_ok=True)
        p_.write_text(f"# Pair confirmation: {lead} -> {foll} lag {k}\n\n```\n"
                      + "\n".join(log) + "\n```\n")
        print(f"\n  written -> {p_}")


if __name__ == "__main__":
    main()
