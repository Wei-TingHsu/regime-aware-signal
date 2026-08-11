"""
src/short_run_events.py

Empirical test of the hypothesis: are the short regime runs (<= 2 days) REAL
macro events, or boundary noise?

Method:
  1. Fit the GMM at a chosen n, label every date (RAW labels, no smoothing).
  2. Find every contiguous run of length <= max_len days.
  3. Print the start date of each short run.
  4. Compare those dates against a reference list of known macro event dates
     (FOMC decision days, major shocks 2018-2026) and report how many short
     runs fall within +/- tolerance days of an event.

Reading:
  - If a HIGH fraction of short runs sit on/near real event dates -> the short
    runs are a genuine fast-shock detector; the raw layer is trustworthy.
  - If short runs are scattered with no event nearby -> boundary wobble; the
    raw layer needs light smoothing even for real-time use.

Run from project root:
    python -m src.short_run_events            # defaults to n=5
    python -m src.short_run_events --n 4
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from src.data_io import load_config, PROCESSED_DIR


CLUSTERING_PCS = ["PC1", "PC2", "PC3"]


# -----------------------------------------------------------------------------
# Reference macro event dates, 2018-2026
# -----------------------------------------------------------------------------
# FOMC decision days (8 per year) plus a selection of known shock/surprise dates.
# This is a REFERENCE list for eyeballing, not an exhaustive registry. Extend as
# needed. Dates are approximate to the decision/print day.
FOMC_DAYS = [
    # 2018
    "2018-03-21","2018-05-02","2018-06-13","2018-08-01","2018-09-26","2018-11-08","2018-12-19",
    # 2019
    "2019-01-30","2019-03-20","2019-05-01","2019-06-19","2019-07-31","2019-09-18","2019-10-30","2019-12-11",
    # 2020
    "2020-01-29","2020-03-03","2020-03-15","2020-04-29","2020-06-10","2020-07-29","2020-09-16","2020-11-05","2020-12-16",
    # 2021
    "2021-01-27","2021-03-17","2021-04-28","2021-06-16","2021-07-28","2021-09-22","2021-11-03","2021-12-15",
    # 2022
    "2022-01-26","2022-03-16","2022-05-04","2022-06-15","2022-07-27","2022-09-21","2022-11-02","2022-12-14",
    # 2023
    "2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
    # 2024
    "2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18",
    # 2025
    "2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10",
    # 2026 (approximate schedule)
    "2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29",
]

SHOCK_DAYS = [
    ("2018-02-05", "Volmageddon (VIX spike, XIV collapse)"),
    ("2018-10-10", "Q4-2018 selloff begins"),
    ("2018-12-24", "Christmas Eve bottom"),
    ("2020-02-24", "COVID crash begins"),
    ("2020-03-09", "Oil price war + COVID, circuit breaker"),
    ("2020-03-12", "COVID crash, circuit breaker"),
    ("2020-03-18", "COVID liquidity crisis peak"),
    ("2021-01-27", "GameStop / meme-stock vol spike"),
    ("2022-02-24", "Russia invades Ukraine"),
    ("2023-03-10", "SVB collapse"),
    ("2023-03-13", "SVB contagion / Signature"),
    ("2024-08-05", "Yen carry unwind, global selloff"),
    ("2025-04-02", "Tariff announcement shock (hypothetical placeholder)"),
]


def load_scores():
    return pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")


def fit_labels(scores, n, cfg):
    X = scores[CLUSTERING_PCS].values
    gmm = GaussianMixture(
        n_components=n,
        covariance_type=cfg["regime"]["covariance_type"],
        max_iter=cfg["regime"]["max_iter"],
        n_init=cfg["regime"]["n_init"],
        random_state=cfg["project"]["random_seed"],
    )
    labels = gmm.fit_predict(X)
    return pd.Series(labels, index=scores.index, name="regime_id")


def find_short_runs(labels, max_len=2):
    """Return list of (start_date, end_date, length, regime_id) for runs <= max_len."""
    runs = []
    idx = labels.index
    vals = labels.values
    i = 0
    n = len(vals)
    while i < n:
        j = i
        while j < n and vals[j] == vals[i]:
            j += 1
        length = j - i
        if length <= max_len:
            runs.append((idx[i], idx[j - 1], length, int(vals[i])))
        i = j
    return runs


def nearest_event(date, event_dates, tolerance_days=3):
    """Return (event_date, gap_days) for the nearest event within tolerance, else None."""
    best = None
    for ev in event_dates:
        gap = abs((date - ev).days)
        if gap <= tolerance_days and (best is None or gap < best[1]):
            best = (ev, gap)
    return best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5, help="number of regimes")
    parser.add_argument("--max_len", type=int, default=2, help="max run length to flag as 'short'")
    parser.add_argument("--tolerance", type=int, default=3, help="+/- days to count as 'near an event'")
    args = parser.parse_args()

    cfg = load_config()
    scores = load_scores()
    labels = fit_labels(scores, args.n, cfg)

    short_runs = find_short_runs(labels, max_len=args.max_len)

    fomc_dates = [pd.Timestamp(d) for d in FOMC_DAYS]
    shock_dates = [pd.Timestamp(d) for d, _ in SHOCK_DAYS]
    shock_lookup = {pd.Timestamp(d): desc for d, desc in SHOCK_DAYS}

    print(f"\n{'='*78}")
    print(f"SHORT-RUN EVENT ALIGNMENT TEST  (n={args.n}, runs <= {args.max_len} days, "
          f"tolerance +/-{args.tolerance} days)")
    print(f"{'='*78}")
    print(f"Total regime runs of <= {args.max_len} days: {len(short_runs)}\n")

    near_fomc = 0
    near_shock = 0
    near_any = 0
    unexplained = []

    print(f"{'start date':<12} {'len':>3} {'regime':>6}   nearest known event")
    print("-" * 78)
    for start, end, length, rid in short_runs:
        fomc_hit = nearest_event(start, fomc_dates, args.tolerance)
        shock_hit = nearest_event(start, shock_dates, args.tolerance)

        if shock_hit is not None:
            desc = shock_lookup[shock_hit[0]]
            tag = f"SHOCK: {desc} ({shock_hit[0].date()}, gap {shock_hit[1]}d)"
            near_shock += 1
            near_any += 1
        elif fomc_hit is not None:
            tag = f"FOMC {fomc_hit[0].date()} (gap {fomc_hit[1]}d)"
            near_fomc += 1
            near_any += 1
        else:
            tag = "— no known event nearby —"
            unexplained.append(start)

        print(f"{start.date()!s:<12} {length:>3} {rid:>6}   {tag}")

    print("-" * 78)
    total = len(short_runs)
    if total > 0:
        print(f"\nSummary:")
        print(f"  near a FOMC day:        {near_fomc:>3} / {total}  ({100*near_fomc/total:.0f}%)")
        print(f"  near a known shock:     {near_shock:>3} / {total}  ({100*near_shock/total:.0f}%)")
        print(f"  near ANY known event:   {near_any:>3} / {total}  ({100*near_any/total:.0f}%)")
        print(f"  unexplained:            {len(unexplained):>3} / {total}  "
              f"({100*len(unexplained)/total:.0f}%)")
        print(f"\nReading:")
        print(f"  High 'near any event' % -> short runs are REAL event responses;")
        print(f"     the raw layer is a genuine fast-shock detector (your hypothesis).")
        print(f"  High 'unexplained' %    -> short runs are boundary wobble;")
        print(f"     even the raw layer needs light smoothing.")
        print(f"\nNote: FOMC baseline caveat — with 8 FOMC days/year and +/-{args.tolerance}d")
        print(f"  windows, some FOMC 'hits' will occur by chance. Weigh SHOCK hits and")
        print(f"  the unexplained rate more heavily than raw FOMC proximity.")


if __name__ == "__main__":
    main()