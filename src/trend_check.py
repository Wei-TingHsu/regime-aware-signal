"""
trend_check.py -- STEP 1 item 3. Isolate the trend effect at FIXED horizon.

THE CONFOUND (PROJECT_STATE open thread 8)
    model_1_baseline is horizon 5 + level. model_2_horizon_trend is horizon 10 +
    trend. They differ in TWO things at once, so neither the original claim that
    trend helps NOR its later retirement is supported by that comparison. The
    confound invalidates it in BOTH directions.

    PROJECT_STATE: "The grid contains same-horizon level-vs-trend cells; run
    those before any claim."

WHAT THIS RUNS
    level vs trend at the SAME horizon, SAME kernel, SAME sigma. Only sim_mode
    differs. Horizons {5, 10, 15, 20}, sigma {1.0, 1.5} (the frozen models' two
    values), gaussian kernel, both universes.

THE SECOND QUESTION, added 2026-08-25 after scaling_check
    docs/scaling_check_results.md found the declared `_z()` full-panel
    look-ahead is small for the LEVEL model (+0.012 long-history, p 0.94) and
    large for BOTH TREND models (model_2 long-history +0.261, 0.4131 -> 0.1522,
    p 0.057).

    Mechanism: sim_mode='trend' z-scores the DIFFERENCED PCs, and macro momentum
    volatility varies enormously across the panel -- 2008 and 2020 dominate it.
    A full-panel sd for that block encodes future volatility regimes far more
    than the level block's does.

    So "does trend beat level" cannot be answered on the full-panel basis alone.
    Every cell is therefore run on BOTH bases:

        full       the basis every recorded figure uses
        expanding  no look-ahead

    If trend beats level on the full basis and not on the expanding one, the
    trend effect IS the look-ahead. That is the question this script exists to
    answer, and it is stated before the run.

THE TEST
    Paired sign-flip permutation on the per-rebalance spread differences. Same
    rebalance dates within a cell, so the series are paired. Calibration checked
    before use: 0.048 rejection with no real difference, 1.000 against a real
    0.05%/reb shift.

    NO MULTIPLICITY CORRECTION IS APPLIED and none is claimed. This is 16 cells
    x 2 bases; at alpha 0.05 roughly 1.6 would clear by chance. Individual cells
    are ESTIMATES. The claim, if any, is the PATTERN across horizons -- the
    project's own rule after the 148-vs-28 universe scan.

Run:
    python -m src.trend_check
    python -m src.trend_check --horizons 5,10 --sigmas 1.5
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_core import DEFAULT, load_data, backtest
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "trend_check_results.md"
OUT_JSON = PROCESSED_DIR / "trend_check.json"
MIN_HISTORY_YEARS = 8.0


def paired_signflip(a, b, iters, rng):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or len(a) == 0:
        return dict(n=int(min(len(a), len(b))), mean_diff=np.nan, p=np.nan,
                    note=f"UNPAIRABLE: {len(a)} vs {len(b)} rebalances")
    d = a - b
    obs = float(d.mean())
    null = np.array([float((d * rng.choice([-1.0, 1.0], len(d))).mean())
                     for _ in range(iters)])
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (iters + 1)
    return dict(n=int(len(d)), mean_diff=obs, p=float(p), note="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", default="5,10,15,20")
    ap.add_argument("--sigmas", default="1.0,1.5")
    ap.add_argument("--iters", type=int, default=5000)
    args = ap.parse_args()

    horizons = [int(x) for x in args.horizons.split(",")]
    sigmas = [float(x) for x in args.sigmas.split(",")]
    cfg = load_config()
    scores, rets = load_data()
    lh = rets.notna().sum().values >= MIN_HISTORY_YEARS * 252
    universes = [("ALL", rets), ("LONG-HISTORY", rets.loc[:, lh])]
    rng = np.random.default_rng(cfg["project"]["random_seed"])

    print("=" * 78)
    print("TREND CHECK -- level vs trend at FIXED horizon, on BOTH scaling bases")
    print("=" * 78)
    print("  thread 8: model_1 and model_2 differ in horizon AND sim_mode, so")
    print("  neither the original claim nor its retirement is supported.")
    print("  Added question: scaling_check found the _z() look-ahead is small")
    print("  for LEVEL (+0.012 long-history, p 0.94) and large for TREND")
    print("  (model_2 long-history +0.261, 0.4131 -> 0.1522). If trend beats")
    print("  level only on the full basis, the trend effect IS the look-ahead.")
    print(f"\n  {len(horizons)}x{len(sigmas)} cells x 2 bases x 2 universes, "
          f"gaussian kernel")
    print(f"  NO multiplicity correction; individual cells are ESTIMATES, the "
          f"claim is the PATTERN.\n")

    results, rows = {}, []
    for basis, expand in (("full", False), ("expanding", True)):
        print(f"{'=' * 78}\nBASIS: {basis}"
              f"{'  (no look-ahead)' if expand else '  (every recorded figure)'}"
              f"\n{'=' * 78}")
        for sig in sigmas:
            for H in horizons:
                base = dict(DEFAULT)
                base.update(horizon=H, sigma=sig, kernel="gaussian",
                            expanding_scaling=expand)
                for uname, r in universes:
                    ml = backtest(scores, r, dict(base, sim_mode="level"), cfg,
                                  do_perm=False)
                    mt = backtest(scores, r, dict(base, sim_mode="trend"), cfg,
                                  do_perm=False)
                    if ml is None or mt is None:
                        print(f"  H={H:2d} sigma {sig} {uname:14} no usable dates")
                        continue
                    pt = paired_signflip(mt.get("spreads", []),
                                         ml.get("spreads", []), args.iters, rng)
                    d = mt["sharpe"] - ml["sharpe"]
                    key = (basis, sig, H, uname)
                    results[key] = dict(level=ml["sharpe"], trend=mt["sharpe"],
                                        d_sharpe=float(d), n_level=ml["n"],
                                        n_trend=mt["n"], paired=pt)
                    rows.append((basis, sig, H, uname, ml, mt, d, pt))
                    star = " <-" if (np.isfinite(pt["p"]) and pt["p"] < 0.05) else ""
                    print(f"  H={H:2d} sigma {sig} {uname:14} "
                          f"level {ml['sharpe']:+.4f}  trend {mt['sharpe']:+.4f}  "
                          f"trend-level {d:+.4f}  paired p {pt['p']:.4f}{star}")

    # --- the pattern, which is the only thing allowed to carry a claim -----
    print("\n" + "=" * 78)
    print("PATTERN -- trend minus level, averaged over sigma and horizon")
    print("=" * 78)
    summary = {}
    for basis in ("full", "expanding"):
        for uname in ("ALL", "LONG-HISTORY"):
            ds = [v["d_sharpe"] for k, v in results.items()
                  if k[0] == basis and k[3] == uname]
            wins = sum(1 for x in ds if x > 0)
            summary[f"{basis}|{uname}"] = dict(
                mean_d=float(np.mean(ds)) if ds else float("nan"),
                cells=len(ds), trend_wins=wins)
            print(f"  {basis:10} {uname:14} mean trend-level "
                  f"{np.mean(ds):+.4f}  |  trend ahead in {wins}/{len(ds)} cells")

    fl = summary.get("full|LONG-HISTORY", {}).get("mean_d", np.nan)
    ex = summary.get("expanding|LONG-HISTORY", {}).get("mean_d", np.nan)
    print(f"\n  long-history: trend advantage {fl:+.4f} on the full basis, "
          f"{ex:+.4f} with the look-ahead removed.")
    if np.isfinite(fl) and np.isfinite(ex):
        if fl > 0 and ex <= 0:
            print("  -> the trend advantage does NOT survive removing the "
                  "look-ahead. On this panel the trend effect IS the "
                  "look-ahead.")
        elif fl > 0 and ex > 0:
            print("  -> a trend advantage survives on both bases, though "
                  "reduced. Report both numbers side by side.")
        else:
            print("  -> no trend advantage on either basis. The confound in "
                  "thread 8 resolves as a null, in both directions.")
    print("=" * 78)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Trend check — level vs trend at fixed horizon", "",
         f"*Run {ts}. PROJECT_STATE open thread 8.*", "",
         "`model_1_baseline` (horizon 5, level) and `model_2_horizon_trend` "
         "(horizon 10, trend) differ in **two** things, so that comparison "
         "supports neither the original claim that trend helps nor its later "
         "retirement. Every cell below fixes horizon, kernel and sigma and "
         "varies **only** `sim_mode`.", "",
         "Every cell is also run on both scaling bases, because "
         "`docs/scaling_check_results.md` found the declared `_z()` look-ahead "
         "is small for the level model and large for both trend models — so "
         "\"does trend beat level\" cannot be answered on the full-panel basis "
         "alone.", "",
         "> **No multiplicity correction is applied and none is claimed.** "
         "These are 16 cells × 2 bases; at α = 0.05 roughly 1.6 clear by "
         "chance. Individual cells are estimates; the claim is the pattern.", "",
         "| basis | sigma | horizon | universe | level | trend | trend−level | "
         "paired mean spread diff | sign-flip p |",
         "|---|---|---|---|---|---|---|---|---|"]
    for basis, sig, H, uname, ml, mt, d, pt in rows:
        pstr = pt["note"] or f"{pt['p']:.4f}"
        L.append(f"| {basis} | {sig} | {H} | {uname} | {ml['sharpe']:+.4f} | "
                 f"{mt['sharpe']:+.4f} | {d:+.4f} | {pt['mean_diff']*100:+.4f}% "
                 f"| {pstr} |")
    L += ["", "## Pattern", "",
          "| basis | universe | mean trend−level | trend ahead in |",
          "|---|---|---|---|"]
    for k, v in summary.items():
        b, u = k.split("|")
        L.append(f"| {b} | {u} | {v['mean_d']:+.4f} | "
                 f"{v['trend_wins']}/{v['cells']} cells |")
    L += ["", f"Long-history: trend advantage **{fl:+.4f}** on the full basis, "
              f"**{ex:+.4f}** with the look-ahead removed.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        {"|".join(map(str, k)): v for k, v in results.items()},
        indent=2, default=str))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
