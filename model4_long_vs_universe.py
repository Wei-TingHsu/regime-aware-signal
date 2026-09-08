"""
model4_long_vs_universe.py -- MODEL 4: does ranking add anything over holding
everything?

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.

WHY THIS MODEL, AND WHY NOW
    The 28 August backtest evidence found the largest single effect in the
    record on the SHORT leg: the five names ranked worst returned +0.169%/week.
    They went UP. Model 1's spread of +0.295% is a long leg of +0.464% minus
    shorts that fought it. That is not a small correction; it is the leg that
    was supposed to make the strategy market-neutral doing the opposite.

    This model removes the short leg WITHOUT removing market neutrality. It
    holds the top N and benchmarks against the equal-weight universe. Both legs
    carry roughly one unit of beta, so the difference is beta-free, and it
    isolates the one question an allocator asks first: is there selection
    skill, or is the long leg riding the market while the shorts fail?

    It is designed from the BACKTEST RECORD ONLY. The live forward ledger holds
    two non-overlapping trades at the time of writing and contributes nothing
    to this design. A model designed after reading its own forward test is not
    out-of-sample, and the point of the frozen models is that model_4 can run
    beside them on data none has seen.

SPECIFICATION -- one cell, no grid
    Score       identical to model_1: H=5, N=5, topk=100, sigma=1.5, lambda from
                config (0.0008/session). Nothing re-tuned. If model_4 differs
                from model_1 in anything but the benchmark, the comparison is
                confounded.
    Long        top N by expected forward return.
    Benchmark   equal-weight mean of every eligible asset at that rebalance.
    Statistic   spread = mean(realised, top N) - mean(realised, all eligible).
    Universes   ALL 47 and LONG-HISTORY 35, both reported.

REGISTERED CRITERIA -- all must hold, fixed before any number is seen
    R1  spread > 0 at block-permutation p < 0.05 (block ~1 year, sign-flip),
        on the ALL universe
    R2  the same on the LONG-HISTORY universe -- the survivorship-controlled
        block, which the incumbent FAILED at p 0.184
    R3  chronological split at the median date: both halves same sign,
        magnitude ratio <= 3x

    Meeting R1 alone is what the incumbent does and is NOT a pass. This model
    has to clear the bar the incumbent could not.

REGISTERED FALSIFICATION, written first
    If top-N minus universe is indistinguishable from zero, then there is no
    selection skill in the ranking at all. Model 1's +0.295% was the long leg
    riding beta while the shorts lost, and the "edge" was an artefact of a bad
    short construction. That would be a finding, and the plan's language about
    ranking would have to be retired.

WHAT IS DELIBERATELY NOT TESTED HERE
    Whether the short leg could be fixed (a different bottom-N rule, a
    beta-neutral short). That is a separate hypothesis and would be model_5.
    Bundling it here would make a failure uninterpretable.

FORWARD REGISTRATION
    If R1-R3 hold, model_4 is frozen into config/models.yaml with a dated
    entry and added to the forward ledger. Its spread column is top-N minus
    universe, not top-N minus bottom-N, and the scoreboard says so.

Run:
    python model4_long_vs_universe.py --quick     # 200 permutations
    python model4_long_vs_universe.py             # 2,000, registered
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR
from src.analog_backtest import load_returns
from backtest_evidence import walk_forward, block_perm_p

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "model4_long_vs_universe.md"
OUT_JSON = PROCESSED_DIR / "model4_long_vs_universe.json"
H, N, TOPK, SIGMA = 5, 5, 100, 1.5          # identical to model_1


def long_vs_universe(records, universe, N):
    """Per-rebalance spread: top-N realised minus equal-weight eligible."""
    out = []
    for pos, exp_fwd, realized in records:
        ok = universe & ~np.isnan(exp_fwd) & ~np.isnan(realized)
        elig = np.where(ok)[0]
        if len(elig) < 2 * N:
            continue
        top = elig[np.argsort(-exp_fwd[elig])][:N]
        out.append((pos, float(np.mean(realized[top])),
                    float(np.mean(realized[elig]))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--start", default="2010-01-01")
    a = ap.parse_args()
    iters = 200 if a.quick else a.iters

    cfg = load_config()
    rng = np.random.default_rng(cfg["project"]["random_seed"])
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    rets = load_returns().reindex(scores.index)
    lam = float(cfg["analog"]["recency_decay_lambda"])
    dates = scores.index
    A = rets.shape[1]
    start = int(dates.get_indexer([pd.to_datetime(a.start)], method="bfill")[0])
    long_hist = rets.notna().sum().values >= 8 * 252

    print("=" * 74)
    print("MODEL 4 -- long top-N vs equal-weight universe")
    print("=" * 74)
    print(f"  score identical to model_1 (H={H} N={N} topk={TOPK} sigma={SIGMA})")
    print(f"  {iters} permutations, seed {cfg['project']['random_seed']}")
    rec = walk_forward(cfg, scores, rets, H, N, TOPK, SIGMA, lam, 20, start,
                       20, 10, progress="walk-forward")

    R = {}
    ann = np.sqrt(52)
    for label, uni in (("ALL", np.ones(A, bool)), ("LONG-HISTORY", long_hist)):
        rows = long_vs_universe(rec, uni, N)
        top = np.array([r[1] for r in rows]); base = np.array([r[2] for r in rows])
        sp = top - base
        sharpe = sp.mean() / sp.std() * ann if sp.std() else float("nan")
        blk = max(2, int(round(len(sp) / 52)))
        p_blk, exc, _ = block_perm_p(sp, sharpe, rng, iters, blk)
        # split
        cut = len(sp) // 2
        e, l = sp[:cut].mean(), sp[cut:].mean()
        sign_ok = np.sign(e) == np.sign(l) == np.sign(sp.mean())
        lo, hi = sorted((abs(e), abs(l)))
        ratio = hi / lo if lo > 0 else float("inf")
        R1 = sharpe > 0 and p_blk < 0.05
        R3 = sign_ok and ratio <= 3.0
        print(f"\n[{label}]  {len(sp)} rebalances, "
              f"{dates[rows[0][0]].date()} -> {dates[rows[-1][0]].date()}")
        print(f"  top-{N} weekly      {top.mean()*100:+.3f}%")
        print(f"  universe weekly   {base.mean()*100:+.3f}%")
        print(f"  SPREAD weekly     {sp.mean()*100:+.3f}%   Sharpe {sharpe:+.2f}")
        print(f"  block p ({blk}/blk) {p_blk:.4f}   exceedances {exc}/{iters}")
        print(f"  split: EARLY {e*100:+.3f}%  LATE {l*100:+.3f}%  "
              f"sign {'agree' if sign_ok else 'DISAGREE'}  ratio {ratio:.2f}x")
        print(f"  R1 {'PASS' if R1 else 'FAIL'}   R3 {'PASS' if R3 else 'FAIL'}")
        R[label] = dict(n=int(len(sp)), top_weekly=float(top.mean()),
                        universe_weekly=float(base.mean()),
                        spread_weekly=float(sp.mean()), sharpe=float(sharpe),
                        p_block=float(p_blk), exceedances=int(exc),
                        early=float(e), late=float(l), ratio=float(ratio),
                        R1=bool(R1), R3=bool(R3))
    R2 = R["LONG-HISTORY"]["R1"]
    verdict = (R["ALL"]["R1"] and R2 and R["ALL"]["R3"] and R["LONG-HISTORY"]["R3"])
    print("\n" + "=" * 74)
    print(f"  R1 ALL {R['ALL']['R1']}  R2 LONG-HIST {R2}  "
          f"R3 split {R['ALL']['R3'] and R['LONG-HISTORY']['R3']}")
    print(f"  MODEL 4: {'PASS -- freeze into models.yaml and add to the forward ledger' if verdict else 'FAIL -- reported, not adopted'}")
    if not verdict:
        print("  If the spread is ~0: no selection skill exists in the ranking.")
        print("  Model 1's +0.295% was beta on the long side and a failing short.")
    print("=" * 74)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %z")
    R.update(run=ts, iters=iters, verdict="PASS" if verdict else "FAIL")
    OUT_JSON.write_text(json.dumps(R, indent=2))
    L = ["# Model 4 — long top-N against the equal-weight universe", "",
         f"*Run {ts}. {iters} permutations. Score identical to model_1; only "
         f"the benchmark changes.*", "",
         f"**Verdict: {R['verdict']}.**", "",
         "| | ALL 47 | LONG-HISTORY 35 |", "|---|---|---|"]
    for k, lab_ in (("spread_weekly", "Spread (top-5 − universe), weekly"),
                    ("sharpe", "Sharpe"), ("p_block", "Block-permutation p"),
                    ("exceedances", "Exceedances"), ("ratio", "Split ratio")):
        f = ("{:+.3%}" if k == "spread_weekly" else "{:+.2f}" if k == "sharpe"
             else "{:.4f}" if k == "p_block" else "{:.2f}×" if k == "ratio" else "{}")
        L.append(f"| {lab_} | {f.format(R['ALL'][k])} | {f.format(R['LONG-HISTORY'][k])} |")
    L += ["", "Criteria: R1 ALL p<0.05 · R2 LONG-HISTORY p<0.05 · R3 split "
              "sign-agree and ≤3× on both. All three or nothing.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
