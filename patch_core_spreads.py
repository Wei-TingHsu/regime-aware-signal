#!/usr/bin/env python3
"""
patch_core_spreads.py -- expose the per-rebalance spread series from
analog_core.backtest().

WHY
    backtest() computes `spreads` (one number per rebalance, ~836 of them) and
    returns only aggregates derived from it. The array is discarded on return.

    The recency ladder's control rung must prove that the sweep harness matches
    the frozen model's code path BEFORE any decayed rung is trusted. Comparing
    Sharpe alone compares one float at two decimal places: two genuinely
    different runs can both print +0.40, and a mismatch tells you THAT it failed,
    not WHERE. Comparing the spread arrays element-wise settles it, and names the
    rebalance that diverged.

SAFETY -- verified before writing this patch
    * forward_log imports DEFAULT, load_data, frozen_labels, feature_matrix,
      _kw, _forward, _expected_fwd from analog_core. It does NOT import
      backtest. The live harness cannot be affected.
    * model_grid reads the returned dict by key (m['sharpe'], m['spread'], ...).
      An ADDED key is invisible to it.
    * The edit adds one key. No existing value changes. No control flow changes.

Run from the repo root:
    python patch_core_spreads.py --dry-run
    python patch_core_spreads.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_core.py",
    """    return dict(n=len(spreads), spread=spreads.mean(), per_yr=per_yr,
                sharpe=sharpe, hit=hits.mean(), payoff=payoff,
                weeks_pos=np.mean(spreads > 0), long_leg=lr_.mean(),
                short_leg=sr_.mean(), p=p)""",
    """    return dict(n=len(spreads), spread=spreads.mean(), per_yr=per_yr,
                sharpe=sharpe, hit=hits.mean(), payoff=payoff,
                weeks_pos=np.mean(spreads > 0), long_leg=lr_.mean(),
                short_leg=sr_.mean(), p=p,
                # Per-rebalance spread series, added 2026-08-24. Aggregates
                # above are all derived from it; exposing it lets a caller
                # assert two runs are THE SAME RUN rather than merely agreeing
                # to two decimal places. Used by src/recency_sweep.py to verify
                # its harness against the frozen model before any decayed rung
                # is read. Additive: model_grid reads this dict by key and is
                # unaffected; forward_log does not import backtest at all.
                spreads=spreads,
                rebalance_pos=np.array(reb_pos))""",
    "analog_core.backtest -- return the per-rebalance spread series",
), (
    "src/analog_core.py",
    """    spreads, hits, lr_, sr_ = [], [], [], []
    eligs = []
    for pos in rebs:""",
    """    spreads, hits, lr_, sr_ = [], [], [], []
    eligs = []
    reb_pos = []          # index of every rebalance that actually produced a
                          # spread, so a caller can name WHICH one diverged
    for pos in rebs:""",
    "analog_core.backtest -- track which rebalances produced a spread",
), (
    "src/analog_core.py",
    """        spreads.append(lr - sr); lr_.append(lr); sr_.append(sr)
        hits.append(np.concatenate([realized[L] > 0, realized[S] < 0]).mean())
        eligs.append((elig, realized))""",
    """        spreads.append(lr - sr); lr_.append(lr); sr_.append(sr)
        hits.append(np.concatenate([realized[L] > 0, realized[S] < 0]).mean())
        eligs.append((elig, realized))
        reb_pos.append(pos)""",
    "analog_core.backtest -- record the rebalance position alongside the spread",
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
            failures.append(f"MISSING FILE: {path}"); print(f"  FAIL  {path}: not found"); continue
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
    print("""VERIFY:

  python -c "
from src.analog_core import DEFAULT, load_data, backtest
from src.data_io import load_config
s, r = load_data()
m = backtest(s, r, dict(DEFAULT), load_config(), do_perm=False)
print('n', m['n'], 'spreads', m['spreads'].shape, 'sharpe', round(m['sharpe'],4))
assert len(m['spreads']) == m['n'] == len(m['rebalance_pos'])
assert abs(m['spreads'].mean() - m['spread']) < 1e-15
print('OK -- array length matches n, mean matches reported spread')
"

  python -m src.model_grid --iters 50     # must still run unchanged
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
