"""
model_grid.py -- define model_3_overfit by an EXPLICIT in-sample grid search,
and record every configuration tried (honesty: the winner is a cherry-pick).

Also prints the two pre-registered principled models under the same frozen-
regime methodology so all three are comparable:
    model_1_baseline        horizon 5,  level similarity, gaussian, sigma 1.5
    model_2_horizon_trend   horizon 10, level+trend similarity, gaussian, 1.5
    model_3_overfit         = best in-sample Sharpe across the grid below

Writes the full grid table to docs/model_grid_results.md for the report.

Run:
    python -m src.model_grid
Optional: --iters 1000   (permutation iters for the 3 chosen models)
"""
import argparse
import itertools

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR
from src.analog_core import DEFAULT, load_data, backtest


def spec(**kw):
    s = dict(DEFAULT); s.update(kw); return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=1000)
    args = ap.parse_args()
    cfg = load_config()
    scores, rets = load_data()

    GRID = dict(horizon=[5, 10, 15, 20], sim_mode=["level", "trend"],
                kernel=["gaussian", "exp"], sigma=[1.0, 1.5, 2.0], nbasket=[5])
    keys = list(GRID)
    combos = list(itertools.product(*[GRID[k] for k in keys]))
    print("=" * 78)
    print(f"MODEL GRID -- {len(combos)} configurations (frozen n=4 regimes)")
    print("=" * 78)

    rows = []
    for i, vals in enumerate(combos, 1):
        s = spec(**dict(zip(keys, vals)))
        m = backtest(scores, rets, s, cfg, do_perm=False)
        if m is None:
            continue
        rows.append({**{k: s[k] for k in keys}, **m})
        if i % 8 == 0:
            print(f"  ... {i}/{len(combos)} done")
    df = pd.DataFrame(rows).sort_values("sharpe", ascending=False).reset_index(drop=True)

    best = df.iloc[0]
    print("\nTOP 5 IN-SAMPLE (by spread-Sharpe):")
    cols = ["horizon", "sim_mode", "kernel", "sigma", "sharpe", "spread", "hit", "payoff"]
    print(df[cols].head(5).to_string(index=False))
    print(f"\n=> model_3_overfit = horizon {int(best.horizon)}, {best.sim_mode}, "
          f"{best.kernel}, sigma {best.sigma} (best-in-sample, CHERRY-PICKED)")

    # the three chosen models, with full permutation p, comparable methodology
    chosen = {
        "model_1_baseline": spec(horizon=5, sim_mode="level", kernel="gaussian", sigma=1.5),
        "model_2_horizon_trend": spec(horizon=10, sim_mode="trend", kernel="gaussian", sigma=1.5),
        "model_3_overfit": spec(horizon=int(best.horizon), sim_mode=best.sim_mode,
                                kernel=best.kernel, sigma=float(best.sigma)),
    }
    print("\n" + "=" * 78)
    print("THE THREE PRE-REGISTERED MODELS (frozen regimes, full permutation):")
    print("=" * 78)
    summary = []
    for name, s in chosen.items():
        m = backtest(scores, rets, s, cfg, do_perm=True, iters=args.iters)
        summary.append((name, s, m))
        print(f"\n{name}")
        print(f"  spec: horizon {s['horizon']}d | {s['sim_mode']} | {s['kernel']} | "
              f"sigma {s['sigma']} | n={s['n_regimes']} | basket {s['nbasket']}/side")
        print(f"  spread {m['spread']*100:+.3f}%/reb (~{m['per_yr']*100:+.1f}%/yr)  "
              f"Sharpe {m['sharpe']:+.2f}  hit {m['hit']:.1%}  payoff {m['payoff']:.2f}  "
              f"p {m['p']:.4f}")

    # write the full grid + chosen specs to docs for the report
    out = PROCESSED_DIR.parent / "docs" / "model_grid_results.md"
    with open(out, "w") as f:
        f.write("# Model grid search results (pre-registration record)\n\n")
        f.write("Every configuration tried, in-sample, frozen n=4 regimes. "
                "`model_3_overfit` is the best-Sharpe row -- **explicitly cherry-picked** "
                "as the overfit control group.\n\n")
        f.write("## The three pre-registered models\n\n")
        f.write("| model | horizon | similarity | kernel | sigma | Sharpe | spread/reb | ~/yr | hit | payoff | p |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
        for name, s, m in summary:
            f.write(f"| {name} | {s['horizon']}d | {s['sim_mode']} | {s['kernel']} | "
                    f"{s['sigma']} | {m['sharpe']:+.2f} | {m['spread']*100:+.3f}% | "
                    f"{m['per_yr']*100:+.1f}% | {m['hit']:.1%} | {m['payoff']:.2f} | {m['p']:.4f} |\n")
        f.write("\n## Full grid (all configs tried)\n\n")
        f.write(df[cols + ["per_yr", "weeks_pos"]].to_markdown(index=False))
        f.write("\n")
    print(f"\nfull record written -> {out}")
    print("=" * 78)


if __name__ == "__main__":
    main()
