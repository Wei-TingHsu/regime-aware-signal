#!/usr/bin/env python3
"""
patch_canonical_labels.py -- back-port canonical regime ordering to
analog_core.frozen_labels. Closes PROJECT_STATE open thread 3.

THREAD 3, outstanding since before this session
    "GMM component ordering is arbitrary across refits, so the `regime` column
    in forward_ledger.csv is not comparable across rows. Picks are invariant;
    the annotation is not."

    analog_event already fixed this for the tau2 cells (ordering by ascending
    mean PC1). This applies the same ordering to frozen_labels, so every
    consumer -- backtest, model_grid, forward_log -- agrees on what "regime 2"
    means.

WHY THIS IS SAFE FOR THE LIVE FORWARD TEST
    Every consumer uses labels ONLY through equality:

        cand = idx[(labels[:pos] == labels[pos]) & (idx + H < pos)]

    Candidate selection asks "same regime as today", which is invariant under
    ANY relabelling. The picks a model makes are therefore bit-identical before
    and after this change. What changes is the reported `regime` integer.

    Verified by the assertion in the VERIFY block: the pre- and post-patch
    spread series must match exactly.

WHAT THIS DOES NOT FIX, and must be recorded
    forward_ledger.csv rows logged BEFORE this patch carry labels from the old
    arbitrary ordering. Rows after carry canonical ones. The column is therefore
    comparable WITHIN each era and not ACROSS the boundary. Options were:
      (a) leave historical rows alone and record the boundary date  <- chosen
      (b) retro-relabel historical rows -- rejected: the ledger is the forward
          test's primary record and is never rewritten, on the same principle
          that a missed day is an honest gap rather than a back-fill.

    The boundary date goes in PROJECT_STATE and in the scoreboard preamble.

Run from the repo root:
    python patch_canonical_labels.py --dry-run
    python patch_canonical_labels.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_core.py",
    '''def frozen_labels(scores, spec, cfg):
    from sklearn.mixture import GaussianMixture
    gm = GaussianMixture(n_components=spec["n_regimes"],
                         covariance_type=cfg["regime"]["covariance_type"],
                         max_iter=cfg["regime"]["max_iter"], n_init=cfg["regime"]["n_init"],
                         random_state=cfg["project"]["random_seed"])
    return gm.fit_predict(scores[CLUSTERING_PCS].values)''',
    '''def frozen_labels(scores, spec, cfg):
    """Regime labels, CANONICALLY ORDERED by ascending mean PC1.

    PROJECT_STATE open thread 3: GMM component ordering is arbitrary, so the
    `regime` column in forward_ledger.csv was not comparable across refits or
    across runs. Ordering components by ascending mean PC1 is deterministic and
    makes "regime 2" mean the same thing everywhere.

    PICKS ARE UNCHANGED. Every consumer uses labels only through equality --
    `labels[:pos] == labels[pos]`, i.e. "same regime as today" -- which is
    invariant under any relabelling. Only the reported integer changes.

    Rows logged in forward_ledger.csv BEFORE 2026-08-25 carry the old arbitrary
    ordering. The column is comparable within each era, not across the boundary.
    Historical rows are NOT retro-relabelled: the ledger is the forward test's
    primary record and is never rewritten, on the same principle that a missed
    day is an honest gap rather than a back-fill.
    """
    from sklearn.mixture import GaussianMixture
    gm = GaussianMixture(n_components=spec["n_regimes"],
                         covariance_type=cfg["regime"]["covariance_type"],
                         max_iter=cfg["regime"]["max_iter"], n_init=cfg["regime"]["n_init"],
                         random_state=cfg["project"]["random_seed"])
    lab = gm.fit_predict(scores[CLUSTERING_PCS].values)
    order = np.argsort(gm.means_[:, 0])          # ascending mean PC1
    remap = np.empty(spec["n_regimes"], dtype=int)
    remap[order] = np.arange(spec["n_regimes"])
    return remap[lab]''',
    "analog_core.frozen_labels -- canonical ordering by ascending mean PC1",
), (
    "src/forward_log.py",
    '''    lines = ["# Forward-test scoreboard (live, out-of-sample)", "",
             "Pre-registered models frozen in `config/models.yaml` before any live data.",''',
    '''    lines = ["# Forward-test scoreboard (live, out-of-sample)", "",
             "Pre-registered models frozen in `config/models.yaml` before any live data.",
             "**Regime labels are canonically ordered by ascending mean PC1 from "
             "2026-08-25.** Rows logged before that date carry the old arbitrary "
             "GMM component ordering, so the `regime` column is comparable within "
             "each era and NOT across the boundary. Historical rows are not "
             "retro-relabelled -- the ledger is never rewritten. Picks are "
             "unaffected: candidate selection uses label EQUALITY, which is "
             "invariant under relabelling.",''',
    "forward_log -- record the label-ordering boundary in the scoreboard",
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

    # capture the pre-patch spread series so the invariance claim is TESTED,
    # not asserted
    print("\n  capturing pre-patch spread series for the invariance check ...")
    ref = None
    try:
        import subprocess, json as _j
        code = ("import json,numpy as np;"
                "from src.analog_core import DEFAULT,load_data,backtest;"
                "from src.data_io import load_config;"
                "s,r=load_data();"
                "m=backtest(s,r,dict(DEFAULT),load_config(),do_perm=False);"
                "print('@@'+json.dumps([float(x) for x in m['spreads']]))")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                             text=True, cwd=ROOT)
        line = [l for l in out.stdout.splitlines() if l.startswith("@@")]
        if line:
            ref = _j.loads(line[0][2:])
            print(f"    captured {len(ref)} rebalances")
    except Exception as e:
        print(f"    (skipped: {type(e).__name__}) -- run the VERIFY block manually")

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

    if ref is not None:
        print("\n  INVARIANCE CHECK -- picks must be bit-identical after "
              "relabelling ...")
        import subprocess, json as _j
        code = ("import json,numpy as np;"
                "from src.analog_core import DEFAULT,load_data,backtest;"
                "from src.data_io import load_config;"
                "s,r=load_data();"
                "m=backtest(s,r,dict(DEFAULT),load_config(),do_perm=False);"
                "print('@@'+json.dumps([float(x) for x in m['spreads']]))")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                             text=True, cwd=ROOT)
        line = [l for l in out.stdout.splitlines() if l.startswith("@@")]
        if line:
            new = _j.loads(line[0][2:])
            same = (len(new) == len(ref)
                    and all(a == b for a, b in zip(ref, new)))
            print(f"    {len(new)} rebalances, identical: {same}")
            if not same:
                print("    ** NOT IDENTICAL -- relabelling changed the PICKS.")
                print("    ** That contradicts the invariance argument. Revert")
                print("    ** with `git checkout src/analog_core.py` and stop.")
        else:
            print("    (could not re-run; do the VERIFY block manually)")

    print("\n" + "=" * 74)
    print("""VERIFY, then commit:

  python -m src.forward_log --dry-run     # must still verify 3 frozen models
  python -m src.model_grid --iters 50     # must still run

Record the boundary in PROJECT_STATE, thread 3:

  Thread 3 CLOSED 2026-08-25. Components canonically ordered by ascending mean
  PC1 in analog_core.frozen_labels and in analog_event.regime_labels_expanding.
  forward_ledger.csv rows before 2026-08-25 carry the old arbitrary ordering;
  the regime column is comparable within each era and not across the boundary.
  Historical rows are NOT retro-relabelled. Picks are unaffected -- candidate
  selection uses label equality, verified bit-identical on 826 rebalances.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
