"""
model_grid.py -- run the explicit in-sample grid, score the three FROZEN
pre-registered models on identical footing, and record every configuration
tried (honesty: model_3_overfit was chosen as a cherry-pick).

CHANGED 2026-08-19. This script used to *re-derive* model_3_overfit as whatever
currently won the grid. That was wrong once the pre-registration existed: on the
session-calendar basis the grid winner moved to horizon 15 / sigma 2.0, while
config/models.yaml freezes model_3_overfit at horizon 20 / sigma 1.0 -- so the
written record contradicted the frozen spec and the live forward test.

All three specs are now read from **config/models.yaml**, the single source of
truth. The current grid winner is still reported, but as a SEPARATE diagnostic
labelled for what it is: what the same search would pick today. It never
redefines a frozen model.

Writes the full grid table to docs/model_grid_results.md for the report.

Run:
    python -m src.model_grid
Optional:
    --iters 1000     permutation iters for the three frozen models
    --out PATH       write the record elsewhere (use this for re-runs so the
                     original pre-registration record is not overwritten)
"""
import argparse
import itertools

import numpy as np
import pandas as pd
import yaml

from src.data_io import load_config, PROCESSED_DIR
from src.analog_core import DEFAULT, load_data, backtest

MODELS_YAML = PROCESSED_DIR.parent / "config" / "models.yaml"


def spec(**kw):
    s = dict(DEFAULT); s.update(kw); return s


def load_frozen_models():
    """Read the frozen pre-registered specs. Same parsing as forward_log.load_models,
    so the grid scores exactly what the live harness trades. NEVER edit models.yaml
    to match a new grid winner -- it is pre-registration evidence."""
    if not MODELS_YAML.exists():
        raise SystemExit(f"missing {MODELS_YAML} -- the frozen model registry.")
    raw = yaml.safe_load(MODELS_YAML.read_text())["models"]
    out = {}
    for name, s in raw.items():
        d = dict(DEFAULT); d.update({k: v for k, v in s.items() if k != "note"})
        out[name] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--out", default=None,
                    help="output path (default docs/model_grid_results.md)")
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

    # --- DIAGNOSTIC ONLY: what this search would pick today ------------------
    # This does NOT define model_3_overfit. That spec is frozen in models.yaml.
    print(f"\n[diagnostic] grid winner on the CURRENT data: horizon {int(best.horizon)}, "
          f"{best.sim_mode}, {best.kernel}, sigma {best.sigma}")

    chosen = load_frozen_models()
    frozen3 = chosen.get("model_3_overfit")
    if frozen3 is not None:
        same = (int(best.horizon) == int(frozen3["horizon"])
                and best.sim_mode == frozen3["sim_mode"]
                and best.kernel == frozen3["kernel"]
                and float(best.sigma) == float(frozen3["sigma"]))
        if same:
            print("             matches the frozen model_3_overfit spec.")
        else:
            print(f"             DIFFERS from frozen model_3_overfit "
                  f"(horizon {frozen3['horizon']}, {frozen3['sim_mode']}, "
                  f"{frozen3['kernel']}, sigma {frozen3['sigma']}).")
            print("             The frozen spec WINS. models.yaml is pre-registration")
            print("             evidence and is not edited to match a new winner. That the")
            print("             winner moves is itself a finding about in-sample selection.")

    print("\n" + "=" * 78)
    print("THE THREE FROZEN PRE-REGISTERED MODELS (from config/models.yaml,")
    print("frozen regimes, full permutation):")
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

    # write the full grid + frozen specs to docs for the report
    out = (PROCESSED_DIR.parent / "docs" / "model_grid_results.md") if args.out is None \
        else PROCESSED_DIR.parent / args.out
    with open(out, "w") as f:
        f.write("# Model grid search results\n\n")
        f.write("Every configuration tried, in-sample, frozen n=4 regimes.\n\n")
        f.write("The three model specs below are read from `config/models.yaml` and are "
                "**frozen pre-registration evidence**. `model_3_overfit` was chosen as the "
                "best-Sharpe row of this grid at pre-registration time and is "
                "**explicitly a cherry-pick**, forward-tested as an overfit control.\n\n")
        f.write(f"On the current data the grid winner is horizon {int(best.horizon)}, "
                f"{best.sim_mode}, {best.kernel}, sigma {best.sigma}. If that differs from "
                "the frozen `model_3_overfit`, the frozen spec stands: `models.yaml` is "
                "never edited to match a new winner, and the fact that the winner moves is "
                "itself evidence about in-sample selection instability.\n\n")
        f.write("## The three frozen pre-registered models\n\n")
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
