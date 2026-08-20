"""
Diagnostic companion to regime_event_alignment.py

Purpose
-------
Test B in the main script compares the RAW GDELT stress_count between
stress-regime days and other days. On 2024 data that ratio sat at ~1.00
for every n -- but stress_count has a huge daily baseline (~75k docs/day),
so a raw-level comparison is swamped by that baseline and cannot reveal the
small genuine excess on real stress days.

This script re-runs Test B THREE ways, on identical regime labels, to tell
apart two readings that the raw test cannot separate:

  1. raw          : stress_count            (the original, baseline-swamped)
  2. share        : stress_count/total_docs (fraction of the day's news that
                    is stress-tagged -- removes the volume baseline)
  3. rolling-z    : z-score of stress_count over a trailing window
                    (is today high RELATIVE TO its own recent baseline?)

Reading the verdict:
  * If share-ratio and rolling-z BOTH stay ~1 / ~0  -> genuine distinctness:
    the macro-PCA regimes capture a different axis than daily news attention.
    Report it as a real finding.
  * If share-ratio jumps >1 (and/or z_in>0, z_in>z_out) -> the raw test was
    just swamped; the stress regime DOES sit on high-stress-news days, and the
    n where this is strongest firms up as the event-supported choice.

It imports the loaders from the main module, so the GMM fit and the
stress-regime selection are byte-for-byte the same as the run you just did.
Your data never leaves your machine.

Run:
    python -m src.regime_event_alignment_normalized --gdelt processed/gdelt_2024_clean.csv
Optional:
    --window 20      trailing window (in available obs) for the rolling z-score
    --nlist 3,4,5    which n to test
"""
import argparse

import numpy as np
import pandas as pd
from src.stress_axis import stress_regime_id

# Reuse the EXACT loaders + GMM fit from the main script so labels are identical.
from src.regime_event_alignment import (
    load_config,
    load_gdelt,
    load_scores_range,
    fit_labels,
)


def pick_stress_regime(labels, scores):
    # data-driven: stress = regime highest on the VIX-correlated PC
    return stress_regime_id(labels, scores)


def ratio_in_out(series, stress_mask):
    """mean(series | stress days) / mean(series | other days)."""
    a = series[stress_mask].mean()
    b = series[~stress_mask].mean()
    ratio = a / b if b else float("nan")
    return a, b, ratio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdelt", required=True, help="path to gdelt 2024 clean csv")
    ap.add_argument("--window", type=int, default=20,
                    help="trailing window for the rolling z-score (default 20)")
    ap.add_argument("--nlist", default="3,4,5",
                    help="comma-separated n values to test (default 3,4,5)")
    ap.add_argument("--start", default=None, help="override window start (YYYY-MM-DD)")
    ap.add_argument("--end", default=None, help="override window end (YYYY-MM-DD)")
    args = ap.parse_args()
    nlist = [int(x) for x in args.nlist.split(",")]

    cfg = load_config()
    gdelt = load_gdelt(args.gdelt)
    start = args.start or gdelt.index.min()
    end = args.end or gdelt.index.max()
    scores = load_scores_range(start, end)

    # --- Build the three stress measures on the GDELT frame -------------------
    if "stress_count" not in gdelt.columns:
        raise SystemExit("gdelt frame has no 'stress_count' column: " + str(list(gdelt.columns)))

    g = gdelt.sort_index().copy()

    # 1) raw
    g["m_raw"] = g["stress_count"].astype(float)

    # 2) share = stress / total_docs  (guard against zero/missing total_docs)
    if "total_docs" in g.columns and (g["total_docs"] > 0).any():
        denom = g["total_docs"].replace(0, np.nan).astype(float)
        g["m_share"] = g["stress_count"].astype(float) / denom
        share_ok = True
    else:
        g["m_share"] = np.nan
        share_ok = False

    # 3) rolling z-score of raw stress_count over a trailing window
    w = max(args.window, 5)
    roll_mean = g["m_raw"].rolling(w, min_periods=max(5, w // 2)).mean()
    roll_std = g["m_raw"].rolling(w, min_periods=max(5, w // 2)).std()
    g["m_z"] = (g["m_raw"] - roll_mean) / roll_std.replace(0, np.nan)

    print("=" * 78)
    print("TEST B, DE-BASELINED  (2024) -- raw vs share vs rolling-z, identical labels")
    print("=" * 78)
    print(f"window {pd.Timestamp(start).date()} -> {pd.Timestamp(end).date()} | "
          f"GDELT days: {len(g)} | PCA-score days: {len(scores)} | "
          f"overlap: {len(scores.index.intersection(g.index))} | rolling window: {w}")
    if not share_ok:
        print("  NOTE: total_docs missing/zero -> 'share' column unavailable, showing NaN.")
    print(f"\n{'n':>3} | {'raw ratio':>10} | {'share ratio':>11} | "
          f"{'z_in':>7} {'z_out':>7} {'z_in-z_out':>10} | stress days")
    print("-" * 78)

    verdict = {}
    for n in nlist:
        labels, _ = fit_labels(scores, n, cfg)
        sr = pick_stress_regime(labels, scores)
        stress_days = (labels == sr)

        # align to the overlap the same way the main script does
        common = labels.index.intersection(g.index)
        sd = stress_days.reindex(common).fillna(False)
        gc = g.loc[common]

        _, _, r_raw = ratio_in_out(gc["m_raw"], sd)
        _, _, r_share = ratio_in_out(gc["m_share"], sd) if share_ok else (np.nan, np.nan, float("nan"))

        z_in = gc.loc[sd, "m_z"].mean()
        z_out = gc.loc[~sd, "m_z"].mean()

        verdict[n] = {"raw": r_raw, "share": r_share, "z_in": z_in, "z_diff": z_in - z_out}
        print(f"{n:>3} | {r_raw:>10.3f} | {r_share:>11.3f} | "
              f"{z_in:>7.3f} {z_out:>7.3f} {z_in - z_out:>10.3f} | {int(sd.sum())}")

    print("\n" + "=" * 78)
    print("HOW TO READ")
    print("  raw ratio    : the original Test B. ~1.00 = swamped by the ~75k/day baseline.")
    print("  share ratio  : stress as a FRACTION of the day's news. >1 = stress regime")
    print("                 really does sit on proportionally stress-heavier days.")
    print("  z_in         : mean rolling z-score of stress_count ON stress-regime days.")
    print("                 >0 means those days run hot vs their own recent baseline;")
    print("                 z_in - z_out > 0 means hotter than non-stress days.")
    print("-" * 78)
    # Auto-summary
    best_share = max(verdict, key=lambda k: (verdict[k]["share"] if not np.isnan(verdict[k]["share"]) else -1))
    any_share_signal = share_ok and any(
        (not np.isnan(v["share"])) and v["share"] > 1.03 for v in verdict.values()
    )
    any_z_signal = any(v["z_in"] > 0.10 and v["z_diff"] > 0.10 for v in verdict.values())
    if any_share_signal or any_z_signal:
        print("  VERDICT: de-baselined signal APPEARS. The raw test was swamped -- the")
        print(f"           stress regime does track news-stress once volume is removed.")
        if any_share_signal:
            print(f"           Strongest on the share measure at n={best_share} "
                  f"(share ratio {verdict[best_share]['share']:.3f}).")
        print("           => firm up that n as the event-supported choice; write up as")
        print("              'regimes track news-stress in proportion, not raw volume.'")
    else:
        print("  VERDICT: NO de-baselined signal. share ~1 and z ~0 across all n.")
        print("           This is GENUINE DISTINCTNESS, not an artifact: the macro-PCA")
        print("           regimes (rates/VIX/curve space) capture a different axis of")
        print("           market state than daily news attention. Report as a real,")
        print("           defensible finding -- the two need not coincide.")
    print(f"  CAVEAT: overlap is {len(scores.index.intersection(g.index))} days; state "
          f"the power either way.")
    print("  NOTE: this VERDICT reads point estimates only. The permutation test in")
    print("        src.regime_event_permutation is the arbiter -- if it says a measure is")
    print("        not distinguishable from chance, that overrides the wording above.")
    print("=" * 78)


if __name__ == "__main__":
    main()
