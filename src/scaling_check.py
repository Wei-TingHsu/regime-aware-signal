"""
scaling_check.py -- STEP 1 item 2. Measure the declared `_z()` look-ahead.

THE DECLARED LOOK-AHEAD (PROJECT_STATE open thread 12)
    analog_core._z() standardises the PC features with nanmean/nanstd over the
    ENTIRE panel. An analog distance computed at 2010 is therefore measured in
    units set by moments estimated through 2026. Same class as the frozen regime
    model, but never declared -- the phrase "expanding-window walk-forward, no
    look-ahead" was too strong.

    PROJECT_STATE's own words: **"expected to be small is not measured."**

    This script measures it.

WHAT IS COMPARED
    Identical spec, identical rebalance dates, identical everything, run twice:

      full       _z()            full-panel moments      (every recorded figure)
      expanding  _z_expanding()  moments of rows 0..t     (no look-ahead)

    On ALL THREE frozen models, both universes. Registered choices:
      * min_periods = 252 -- one year. A standard deviation from fewer than
        ~250 observations is noisy enough that early distances would be scaled
        by an unstable denominator, which is a different distortion rather than
        no distortion.
      * all three frozen models, not just model_1_baseline. model_3_overfit
        (horizon 20, sigma 1.0) is the spec most sensitive to the distance
        metric, so if the look-ahead matters anywhere it is largest there -- and
        that is the control model whose job is to show what overfitting buys.

THE PAIRED TEST
    Both bases produce a spread on the SAME rebalance dates, so the series are
    paired. Difference in mean spread, with a sign-flip permutation null on the
    per-rebalance differences. Reporting two Sharpes side by side answers "how
    big"; the paired test answers "is it distinguishable from zero at all".

CANDIDATE-POOL ACCOUNTING
    Expanding scaling makes the first min_periods rows NaN, so they drop out of
    the candidate pool via the existing NaN guard. That shrinkage is COUNTED and
    reported: a Sharpe difference driven by a smaller analog pool is a different
    finding from one driven by the scaling itself.

Run:
    python -m src.scaling_check
    python -m src.scaling_check --iters 20000 --model model_1_baseline
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml

from src.analog_core import (DEFAULT, CLUSTERING_PCS, load_data, backtest,
                             feature_matrix, frozen_labels)
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
MODELS_YAML = REPO / "config" / "models.yaml"
OUT_MD = REPO / "docs" / "scaling_check_results.md"
OUT_JSON = PROCESSED_DIR / "scaling_check.json"

MIN_HISTORY_YEARS = 8.0


def frozen_specs():
    raw = yaml.safe_load(MODELS_YAML.read_text())["models"]
    out = {}
    for name, s in raw.items():
        d = dict(DEFAULT); d.update({k: v for k, v in s.items() if k != "note"})
        out[name] = d
    return out


def pool_counts(scores, spec, cfg):
    """Eligible candidates per rebalance under each scaling basis, so any
    difference driven by a SMALLER POOL is visible rather than attributed to
    the scaling itself."""
    labels = frozen_labels(scores, spec, cfg)
    H = spec["horizon"]
    dates = scores.index
    start = int(dates.get_indexer([pd.to_datetime("2010-01-01")],
                                  method="bfill")[0])
    out = {}
    for basis, exp in (("full", False), ("expanding", True)):
        X = feature_matrix(scores, dict(spec, expanding_scaling=exp))
        n = []
        for pos in range(start, len(dates) - H, H):
            if np.isnan(X[pos]).any():
                continue
            idx = np.arange(pos)
            cand = idx[(labels[:pos] == labels[pos]) & (idx + H < pos)]
            cand = cand[~np.isnan(X[cand]).any(axis=1)]
            n.append(len(cand))
        out[basis] = dict(median=float(np.median(n)) if n else float("nan"),
                          min=int(np.min(n)) if n else 0,
                          rebalances=len(n))
    return out


def paired_test(a, b, iters, rng):
    """Sign-flip permutation on the per-rebalance differences. Same dates, so
    the series are paired; a two-sample test would throw that away."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return dict(n=0, mean_diff=np.nan, p=np.nan,
                    note=f"UNPAIRABLE: {a.shape[0]} vs {b.shape[0]} rebalances")
    d = a - b
    obs = float(d.mean())
    null = np.empty(iters)
    for i in range(iters):
        null[i] = float((d * rng.choice([-1.0, 1.0], size=len(d))).mean())
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (iters + 1)
    return dict(n=int(len(d)), mean_diff=obs, p=float(p), note="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=10000)
    ap.add_argument("--perm-iters", type=int, default=1000)
    ap.add_argument("--model", default=None, help="one model instead of all three")
    args = ap.parse_args()

    cfg = load_config()
    scores, rets = load_data()
    lh = rets.notna().sum().values >= MIN_HISTORY_YEARS * 252
    universes = [("ALL", rets), ("LONG-HISTORY", rets.loc[:, lh])]
    specs = frozen_specs()
    if args.model:
        specs = {args.model: specs[args.model]}
    rng = np.random.default_rng(cfg["project"]["random_seed"])

    print("=" * 78)
    print("SCALING CHECK -- how big is the declared _z() full-panel look-ahead?")
    print("=" * 78)
    print(f"  panel {len(scores)} sessions | long-history {int(lh.sum())}/"
          f"{rets.shape[1]} assets | min_periods 252 (registered)")
    print("  PROJECT_STATE thread 12: 'expected to be small is not measured.'")

    results, rows = {}, []
    for name, spec in specs.items():
        print(f"\n{'-' * 78}\n{name}  (horizon {spec['horizon']}d | "
              f"{spec['sim_mode']} | sigma {spec['sigma']})\n{'-' * 78}")
        pc = pool_counts(scores, spec, cfg)
        print(f"  candidate pool per rebalance -- "
              f"full: median {pc['full']['median']:.0f} (min {pc['full']['min']}) | "
              f"expanding: median {pc['expanding']['median']:.0f} "
              f"(min {pc['expanding']['min']})")
        shrink = (1 - pc["expanding"]["median"] / pc["full"]["median"]) \
            if pc["full"]["median"] else np.nan
        print(f"  pool shrinkage under expanding scaling: {shrink:.1%}")

        for uname, r in universes:
            m_full = backtest(scores, r, dict(spec, expanding_scaling=False),
                              cfg, do_perm=True, iters=args.perm_iters)
            m_exp = backtest(scores, r, dict(spec, expanding_scaling=True),
                             cfg, do_perm=True, iters=args.perm_iters)
            if m_full is None or m_exp is None:
                print(f"  {uname}: no usable dates"); continue
            pt = paired_test(m_full.get("spreads", []), m_exp.get("spreads", []),
                             args.iters, rng)
            d_sharpe = m_full["sharpe"] - m_exp["sharpe"]
            results[(name, uname)] = dict(
                full_sharpe=m_full["sharpe"], exp_sharpe=m_exp["sharpe"],
                full_p=m_full["p"], exp_p=m_exp["p"],
                n_full=m_full["n"], n_exp=m_exp["n"],
                d_sharpe=float(d_sharpe), paired=pt, pool=pc)
            rows.append((name, uname, m_full, m_exp, d_sharpe, pt, pc))
            flag = ""
            if np.isfinite(pt["p"]) and pt["p"] < 0.05:
                flag = "  <- DISTINGUISHABLE FROM ZERO"
            print(f"  {uname:14} full {m_full['sharpe']:+.4f} (p {m_full['p']:.4f}, "
                  f"n {m_full['n']})  |  expanding {m_exp['sharpe']:+.4f} "
                  f"(p {m_exp['p']:.4f}, n {m_exp['n']})  |  diff "
                  f"{d_sharpe:+.4f}")
            if pt["note"]:
                print(f"                 paired test: {pt['note']}")
            else:
                print(f"                 paired mean spread diff "
                      f"{pt['mean_diff']*100:+.4f}%/reb, sign-flip p "
                      f"{pt['p']:.4f}{flag}")

    print("\n" + "=" * 78)
    print("READING")
    print("  A small, non-significant difference means the declared look-ahead")
    print("  is small ON THIS PANEL -- which is what thread 12 expected but had")
    print("  never measured. It does NOT retract the declaration: the phrase")
    print("  'no look-ahead' stays wrong, it is now wrong by a measured amount.")
    print("  A large or significant difference means every recorded figure on")
    print("  the analog_core basis carries it, and both numbers must be")
    print("  reported side by side wherever those figures appear.")
    print("=" * 78)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Scaling check — the declared `_z()` full-panel look-ahead, measured",
         "", f"*Run {ts}. PROJECT_STATE open thread 12.*", "",
         "`analog_core._z()` standardises PC features using **whole-panel** "
         "moments, so a distance computed at 2010 uses units set by data "
         "through 2026. Declared but never quantified — *\"expected to be small "
         "is not measured.\"* Both bases below are identical in every respect "
         "except the standardisation window. min_periods = 252, registered.", "",
         "| model | universe | full-panel Sharpe | expanding Sharpe | diff | "
         "paired mean spread diff | sign-flip p |", "|---|---|---|---|---|---|---|"]
    for name, uname, mf, me, d, pt, pc in rows:
        pstr = pt["note"] or f"{pt['p']:.4f}"
        L.append(f"| {name} | {uname} | {mf['sharpe']:+.4f} | {me['sharpe']:+.4f} "
                 f"| {d:+.4f} | {pt['mean_diff']*100:+.4f}% | {pstr} |")
    L += ["", "## Candidate pool", "",
          "Expanding scaling makes the first 252 rows NaN, so they leave the "
          "candidate pool through the existing NaN guard. A Sharpe difference "
          "driven by a smaller pool is a different finding from one driven by "
          "the scaling itself, so the counts are reported.", "",
          "| model | full median pool | expanding median pool | shrinkage |",
          "|---|---|---|---|"]
    seen = set()
    for name, _u, _mf, _me, _d, _pt, pc in rows:
        if name in seen:
            continue
        seen.add(name)
        sh = (1 - pc["expanding"]["median"] / pc["full"]["median"]) \
            if pc["full"]["median"] else float("nan")
        L.append(f"| {name} | {pc['full']['median']:.0f} | "
                 f"{pc['expanding']['median']:.0f} | {sh:.1%} |")
    L += ["", "## Reading", "",
          "A small, non-significant difference means the declared look-ahead is "
          "small **on this panel** — what thread 12 expected but had never "
          "measured. It does **not** retract the declaration: the phrase \"no "
          "look-ahead\" stays wrong, and is now wrong by a measured amount.", "",
          "A large or significant difference means every recorded figure on the "
          "`analog_core` basis carries it, and both numbers must appear side by "
          "side wherever those figures appear.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        {f"{k[0]}|{k[1]}": v for k, v in results.items()}, indent=2, default=str))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
