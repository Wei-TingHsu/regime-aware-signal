#!/usr/bin/env python3
"""
patch_step3_live_basis.py -- make step 3's conditioning basis MATCH WHAT A LIVE
SYSTEM CAN ACTUALLY COMPUTE.

TWO LOOK-AHEADS IN analog_event.build_blind, both found 2026-08-25 after
scaling_check, both declared here:

  1. FEATURE SCALING
         Z = (Z - np.nanmean(Z, axis=0)) / np.nanstd(Z, axis=0)
     Full-panel moments. A macro distance computed at 2010 is measured in units
     set by data through 2026 -- exactly the declared `_z()` look-ahead of
     PROJECT_STATE thread 12.

  2. REGIME LABELS
         labels_all = frozen_labels(scores, spec, cfg)
     One GMM fit on ALL history. Those labels define the DerSimonian-Laird cells
     that estimate tau2, so the shrinkage weight w = ESS/(ESS+k) carries the
     look-ahead too.

WHY THIS IS NOT "THE MEASURED EFFECT IS SMALL, SO CHANGE IT"
    scaling_check measured the level-basis look-ahead at +0.012 long-history,
    p 0.94 -- small. That is NOT the argument for changing it.

    The argument is that step 3 is meant to run as a LIVE DAILY PRODUCT. In
    production there is no future data to standardise with and no future data to
    fit regimes on. The full-panel basis is not a robustness variant here; it is
    something the deployed system CANNOT DO. Shipping it would mean the research
    basis and the live basis differ -- which is precisely the analog_core /
    analog_backtest divergence that cost a full session to untangle.

    A backtest that cannot be run live is not a backtest of the product.

WHAT IS DECLARED
    prereg_analog_event.md section 2.2 did not specify a standardisation basis.
    This change is therefore an AMENDMENT, made after seeing scaling_check, and
    it changes the ESTIMATOR rather than the reporting -- the first such
    amendment in this project. Timing declared in section 11. No real
    conditional estimate has been computed, so nothing is contaminated
    retrospectively.

THIRD PROBLEM, fixed in the same change (PROJECT_STATE open thread 3)
    GMM component ordering is ARBITRARY per fit. An expanding-window refit
    therefore permutes labels across refits, and the tau2 cells would silently
    mix regimes -- a worse error than the look-ahead it replaces. Components are
    now canonically ordered by mean PC1 at every refit, so cell identity is
    stable across the panel.

COST
    Labels are computed ONCE for the whole panel (refit every 20 sessions, ~260
    fits) and CACHED to processed/regime_labels_expanding.parquet. Refitting
    inside each LOO fold would be enormously expensive and NOT more correct: the
    fold exists to exclude the held-out event's OUTCOME, not to re-derive
    regimes.

Run from the repo root:
    python patch_step3_live_basis.py --dry-run
    python patch_step3_live_basis.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_event.py",
    '''from src.analog_core import CLUSTERING_PCS, load_data, frozen_labels, DEFAULT
from src.data_io import load_config, PROCESSED_DIR''',
    '''from src.analog_core import (CLUSTERING_PCS, load_data, frozen_labels,
                              _z_expanding, DEFAULT)
from src.data_io import load_config, PROCESSED_DIR''',
    "analog_event -- import _z_expanding",
), (
    "src/analog_event.py",
    '''def build_blind(n_events, effect, rng, cfg, seed_offset=0):''',
    '''def regime_labels_expanding(scores, cfg, refit_every=20, min_train=504,
                            cache=True):
    """Regime label at date t, using ONLY data up to t.

    WHY: frozen_labels fits ONE GMM on all history. Those labels define the
    DerSimonian-Laird cells that estimate tau2, so the shrinkage weight w
    inherits a look-ahead. A live system has no future data to fit on.

    CANONICAL ORDERING (PROJECT_STATE open thread 3). GMM component ordering is
    arbitrary per fit, so an expanding refit would permute labels across refits
    and the tau2 cells would silently mix regimes -- worse than the look-ahead
    it replaces. Components are relabelled by ascending mean PC1 at every refit,
    which is deterministic and stable across the panel.

    Computed once for the whole panel and cached. Refitting inside each LOO fold
    would be far more expensive and NOT more correct: the fold excludes the
    held-out event's OUTCOME, not the regime structure.
    """
    from sklearn.mixture import GaussianMixture
    cache_path = PROCESSED_DIR / "regime_labels_expanding.parquet"
    X = scores[CLUSTERING_PCS].values
    n, C = len(X), int(cfg["regime"]["n_regimes"])
    if cache and cache_path.exists():
        try:
            df = pd.read_parquet(cache_path)
            if len(df) == n:
                return df["label"].values
        except Exception:
            pass

    labels = np.full(n, -1, dtype=int)
    model, order, last_fit, n_fits = None, None, -10 ** 9, 0
    for t in range(min_train, n):
        if t - last_fit >= refit_every or model is None:
            model = GaussianMixture(
                n_components=C,
                covariance_type=cfg["regime"]["covariance_type"],
                max_iter=cfg["regime"]["max_iter"],
                n_init=cfg["regime"]["n_init"],
                random_state=cfg["project"]["random_seed"])
            model.fit(X[: t + 1])
            # canonical order: ascending mean PC1 of the fitted components
            order = np.argsort(model.means_[:, 0])
            remap = np.empty(C, dtype=int)
            remap[order] = np.arange(C)
            last_fit = t; n_fits += 1
            if n_fits % 50 == 0:
                print(f"      ... {n_fits} expanding GMM refits")
        labels[t] = int(remap[model.predict(X[t: t + 1])[0]])
    print(f"      {n_fits} expanding GMM refits, labels canonically ordered "
          f"by mean PC1; first {min_train} sessions unlabelled (-1)")
    if cache:
        try:
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"label": labels}, index=scores.index).to_parquet(cache_path)
        except Exception as e:
            print(f"      (label cache not written: {type(e).__name__})")
    return labels


def build_blind(n_events, effect, rng, cfg, seed_offset=0):''',
    "analog_event -- add expanding-window canonically-ordered regime labels",
), (
    "src/analog_event.py",
    '''    scores, rets = load_data()
    spec = dict(DEFAULT)
    labels_all = frozen_labels(scores, spec, cfg)
    C = int(spec["n_regimes"])

    Z = scores[CLUSTERING_PCS].values
    Z = (Z - np.nanmean(Z, axis=0)) / np.nanstd(Z, axis=0)''',
    '''    scores, rets = load_data()
    spec = dict(DEFAULT)
    C = int(spec["n_regimes"])

    # LIVE BASIS (amendment 2026-08-25). Both of these previously used the whole
    # panel, which a deployed system cannot do -- there is no future data to
    # standardise with or to fit regimes on. A backtest that cannot be run live
    # is not a backtest of the product.
    labels_all = regime_labels_expanding(scores, cfg)     # was frozen_labels
    Z = _z_expanding(scores[CLUSTERING_PCS].values)       # was full-panel z''',
    "analog_event.build_blind -- switch both to the live basis",
), (
    "src/analog_event.py",
    '''    valid = np.flatnonzero(np.isfinite(fwd) & np.isfinite(Z).all(axis=1))
    valid = valid[valid > 252]''',
    '''    # labels are -1 before min_train, and Z is NaN before min_periods, so both
    # exclusions are enforced here rather than assumed
    valid = np.flatnonzero(np.isfinite(fwd) & np.isfinite(Z).all(axis=1)
                           & (labels_all >= 0))
    valid = valid[valid > 252]''',
    "analog_event.build_blind -- exclude unlabelled and unscaled early rows",
)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("=" * 74)
    print("PHASE 1 -- verifying anchors (nothing written)")
    print("=" * 74)
    failures = []
    for path, anchor, _r, label in EDITS:
        p = ROOT / path
        if not p.exists():
            failures.append(f"MISSING FILE: {path}")
            print(f"  FAIL  {path}: not found"); continue
        n = p.read_text().count(anchor)
        if n == 0:
            failures.append(f"ANCHOR NOT FOUND in {path} [{label}]")
            print(f"  FAIL  {path}: anchor not found -- {label}")
            print(f"        sought: {anchor[:70]!r}")
        elif n > 1:
            failures.append(f"ANCHOR NOT UNIQUE ({n}x) in {path} [{label}]")
            print(f"  FAIL  {path}: anchor x{n} -- {label}")
        else:
            print(f"  ok    {path}: {label}")

    if failures:
        print("\n" + "=" * 74)
        print(f"ABORTED -- {len(failures)} failure(s). NO FILE WAS MODIFIED.")
        print("=" * 74)
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"\nall {len(EDITS)} anchors verified, unique.")
    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    print("\n" + "=" * 74)
    print("PHASE 2 -- applying")
    print("=" * 74)
    touched = {}
    for path, anchor, repl, label in EDITS:
        text = touched.get(path, (ROOT / path).read_text())
        assert text.count(anchor) == 1, f"anchor lost mid-run: {path} [{label}]"
        touched[path] = text.replace(anchor, repl)
        print(f"  applied  {path}: {label}")
    for path, text in touched.items():
        (ROOT / path).write_text(text)
        print(f"  written  {path}")

    print("\n" + "=" * 74)
    print("""VERIFY. The first run builds the label cache (~260 GMM refits, a few
minutes); later runs load it.

  python -m src.analog_event --self-test --quick

  All six tests must still pass on the new basis. If test 1's recovery or
  test 3's tier spread changes materially, that is INFORMATION about how much
  the conditioning depended on the look-ahead -- report it, do not tune it away.

  Check the labels are stable and balanced:

  python -c "
import pandas as pd, numpy as np
d = pd.read_parquet('processed/regime_labels_expanding.parquet')
l = d['label'].values; v = l[l >= 0]
print('labelled sessions:', len(v), 'of', len(l))
print('counts per regime:', np.bincount(v))
ch = int((np.diff(v) != 0).sum())
print('label changes:', ch, '-> median run length', round(len(v)/max(1,ch), 1), 'sessions')
print('(PROJECT_STATE records median run 52.5d for the frozen n=4 fit --')
print(' a much shorter run here would mean the canonical ordering is not holding)')
"

AMENDMENT for docs/prereg_analog_event.md section 11, BEFORE re-running:

| 2026-08-25 | Section 2.2's conditioning switches to the LIVE BASIS:
expanding-window feature standardisation (was full-panel) and expanding-window
regime labels (was one GMM on all history), with components canonically ordered
by mean PC1. | Step 3 is a live daily product; a deployed system has no future
data to standardise with or fit regimes on, so the full-panel basis is
something it CANNOT DO, and a backtest that cannot be run live is not a
backtest of the product. Decided after seeing scaling_check -- declared. FIRST
amendment that changes the estimator rather than the reporting. No real
conditional estimate had been computed, so nothing is contaminated
retrospectively. Also closes PROJECT_STATE thread 3: canonical component
ordering, without which an expanding refit permutes labels across refits and
the tau2 cells silently mix regimes. |
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
