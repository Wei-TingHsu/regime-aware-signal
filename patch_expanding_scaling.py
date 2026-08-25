#!/usr/bin/env python3
"""
patch_expanding_scaling.py -- STEP 1 item 2: make the declared `_z()`
full-panel look-ahead measurable instead of asserted-to-be-small.

THE DECLARED LOOK-AHEAD (PROJECT_STATE, open thread 12)
    analog_core._z() standardises the PC features with nanmean/nanstd over the
    ENTIRE panel. Analog distances at 2010 are therefore measured in units set
    by moments estimated through 2026. Same class as the frozen regime model,
    but never declared -- the phrase "expanding-window walk-forward, no
    look-ahead" was too strong.

    PROJECT_STATE's own words: "expected to be small is not measured."

WHAT THIS PATCH ADDS
    A spec key `expanding_scaling`, DEFAULT False. When True, feature_matrix
    standardises each row against the moments of rows 0..t only -- no future
    data enters the distance metric.

    DEFAULT FALSE. Every existing call, including the frozen models and the live
    harness, is bit-identical to before. The flag exists so the two can be run
    side by side and BOTH NUMBERS REPORTED, which is what thread 12 asks for.

WHY A FLAG AND NOT A SEPARATE SCRIPT
    A standalone diagnostic would duplicate feature construction. Two copies
    drift, and the drift would silently invalidate exactly the comparison the
    check exists to make. One estimator, one file, one switch.

SAFETY
    * `expanding_scaling` is absent from every models.yaml spec, so
      dict(DEFAULT) supplies False everywhere.
    * feature_matrix uses spec.get(), so a spec dict built by hand without the
      key still works.
    * forward_log imports feature_matrix. With the flag False its output is
      unchanged; verified by the assertion in the VERIFY block below.

ddof NOTE
    numpy's nanstd defaults to ddof=0; pandas' expanding().std() defaults to
    ddof=1. The expanding path passes ddof=0 explicitly so the two paths differ
    only in the WINDOW, never in the estimator.

Run from the repo root:
    python patch_expanding_scaling.py --dry-run
    python patch_expanding_scaling.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_core.py",
    """    trend_window=10, n_regimes=int(_CFG["regime"]["n_regimes"]),
               topk=100, nbasket=5, min_analogs=20, min_cov=10,
               half_life_years=None)""",
    """    trend_window=10, n_regimes=int(_CFG["regime"]["n_regimes"]),
               topk=100, nbasket=5, min_analogs=20, min_cov=10,
               half_life_years=None, expanding_scaling=False)""",
    "analog_core.DEFAULT -- add expanding_scaling, default False",
), (
    "src/analog_core.py",
    """def _z(a):
    mu = np.nanmean(a, axis=0); sd = np.nanstd(a, axis=0); sd[sd == 0] = 1.0
    return (a - mu) / sd""",
    """def _z(a):
    \"\"\"Full-panel standardisation. DECLARED LOOK-AHEAD: moments are estimated
    over the whole panel, so a distance computed at 2010 uses units set by data
    through 2026. Retained as the default because it is the basis every recorded
    figure was produced on. See _z_expanding for the no-look-ahead variant and
    PROJECT_STATE open thread 12.\"\"\"
    mu = np.nanmean(a, axis=0); sd = np.nanstd(a, axis=0); sd[sd == 0] = 1.0
    return (a - mu) / sd


def _z_expanding(a, min_periods=252):
    \"\"\"Expanding-window standardisation: row t uses moments of rows 0..t only.

    No future data enters the distance metric. Rows before min_periods are NaN
    and are filtered out downstream by the existing
    `cand[~np.isnan(X[cand]).any(axis=1)]` guard -- they are dropped from the
    candidate pool rather than silently mis-scaled, which is the fail-safe
    direction.

    ddof=0 matches numpy's nanstd, so this differs from _z ONLY in the window.
    \"\"\"
    df = pd.DataFrame(a)
    mu = df.expanding(min_periods=min_periods).mean()
    sd = df.expanding(min_periods=min_periods).std(ddof=0)
    sd = sd.where(sd > 0)                 # zero variance -> NaN -> row dropped
    return ((df - mu) / sd).values""",
    "analog_core -- add _z_expanding",
), (
    "src/analog_core.py",
    """def feature_matrix(scores, spec):
    lvl = _z(scores[CLUSTERING_PCS].values)
    if spec["sim_mode"] == "trend":
        d = scores[CLUSTERING_PCS].diff(spec["trend_window"]).values
        return np.hstack([lvl, _z(d)])          # NaN in first trend_window rows
    return lvl""",
    """def feature_matrix(scores, spec):
    # expanding_scaling defaults False -> _z, bit-identical to every recorded
    # run. True -> _z_expanding, which removes the declared full-panel
    # look-ahead. Both are reported side by side; neither replaces the other.
    zf = _z_expanding if spec.get("expanding_scaling", False) else _z
    lvl = zf(scores[CLUSTERING_PCS].values)
    if spec["sim_mode"] == "trend":
        d = scores[CLUSTERING_PCS].diff(spec["trend_window"]).values
        return np.hstack([lvl, zf(d)])          # NaN in first trend_window rows
    return lvl""",
    "analog_core.feature_matrix -- dispatch on expanding_scaling",
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
            print(f"        sought: {anchor[:60]!r}")
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
    print("""VERIFY -- the default path must be untouched:

  python -c "
import numpy as np
from src.analog_core import DEFAULT, load_data, feature_matrix, backtest, _z
from src.data_io import load_config
s, r = load_data()
spec = dict(DEFAULT)
X0 = feature_matrix(s, spec)
assert np.array_equal(np.nan_to_num(X0), np.nan_to_num(_z(s[['PC1','PC2','PC3']].values)))
print('default path bit-identical to _z: OK')
X1 = feature_matrix(s, dict(spec, expanding_scaling=True))
print('expanding NaN rows:', int(np.isnan(X1).any(axis=1).sum()), 'of', len(X1))
"

Then the side-by-side comparison (STEP 1 item 2):

  python -m src.scaling_check --iters 1000
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
