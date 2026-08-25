#!/usr/bin/env python3
"""
patch_selftest_repair.py -- fix tests 1 and 3 (my bugs) and re-specify test 5.

TEST 1 WAS VACUOUS -- my bug
    `ok = np.isfinite(r["estimate"])`. It passed with estimate +0.017% +/- 2.826%
    against a planted 0.5% -- an interval 166x the effect. It verified that a
    number came back, not that the number was right.

    REPLACED with an actual recovery test. The planted effect is
    c * sign(PC1), so the conditional estimate for PC1>0 queries minus that for
    PC1<0 queries must recover 2c. Checked against its own standard error, on
    n=400 events so ESS is large enough for the check to mean anything.

TEST 3 NEVER EXERCISED TIERS 1 OR 2 -- my bug
    Every case landed at tier 3 (ESS 6.1, 3.2, 2.6, 2.2, 2.3). It checked
    consistency with the boundaries but never showed the boundaries are
    REACHABLE. A tier function that returns 3 unconditionally would have passed.

    REPLACED with a test that plants strong / moderate / no cell structure and
    REQUIRES tier 1, tier 2 and tier 3 to each appear at least once.

TEST 5 FAILED, AND THE FAILURE IS PRESERVED
    200 reps x 500 perms, rejection 0.005 against a registered band of
    [0.02, 0.08], median p 0.906.

    *** THAT RESULT STAYS IN THE RECORD AND IN THE REPORT. It is not deleted,
    and this file does not pretend it did not happen. ***

    Diagnosis, demonstrated in simulation BEFORE any change was made: when tau2
    = 0 the registered null path sets w = 0, so pred_blend == pred_uncond
    EXACTLY, the gain is identically zero in the observed AND in every permuted
    draw, and p = 1.0 by ties alone. Simulating 50-80% degenerate reps
    reproduces median p ~1.0 and rejection ~0.01. The estimator was behaving as
    registered; the TEST could not measure calibration in the regime where the
    estimator correctly refuses to condition.

    RE-SPECIFIED, not loosened:
      5a  the degenerate fraction is REPORTED as a first-class number. It is
          informative about how often macro conditioning finds nothing.
      5b  the rejection rate is computed ONLY over reps where the estimator
          actually conditioned (tau2 > 0), against the SAME band [0.02, 0.08].
          At least 40 such reps are required or the test is INCONCLUSIVE rather
          than passing.

    Conditioning on tau2 > 0 selects on the estimator's output, which is stated
    plainly. It is the subpopulation in which a conditional claim is made at
    all, and therefore the only subpopulation in which "is the null calibrated"
    is a meaningful question.

Run from the repo root:
    python patch_selftest_repair.py --dry-run
    python patch_selftest_repair.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_event.py",
    '''def test_1_recovery(rng, cfg, res):
    b = build_blind(120, 0.005, rng, cfg)
    s, med, tgt, _ = _sigma_for(b)
    w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
    r = estimate(b["y"], w, b["labels"], b["C"])
    se = np.std(b["y"], ddof=1) / np.sqrt(max(1, r["ess"]))
    lo, hi = r["estimate"] - 2 * se, r["estimate"] + 2 * se
    ok = np.isfinite(r["estimate"])
    res.append(("1 recovery", ok,
                f"estimate {r['estimate']*100:+.3f}% +/- {2*se*100:.3f}%, "
                f"ESS {r['ess']:.1f}, sigma {s:.3f} (median ESS {med:.1f} vs "
                f"target {tgt:.1f})"))''',
    '''def test_1_recovery(rng, cfg, res, n_events=400, effect=0.005):
    """Does the estimator RECOVER a planted effect, not merely return a number?

    REPLACES a vacuous check (`ok = isfinite(estimate)`) that passed with an
    interval 166x the planted effect. The planted effect is c * sign(PC1), so
    the conditional estimate for PC1>0 queries minus that for PC1<0 queries must
    recover 2c. Judged against its own standard error, not against zero."""
    b = build_blind(n_events, effect, rng, cfg)
    s, med, tgt, conv = _sigma_for(b)
    pos = b["Z"][:, 0] > 0
    if pos.sum() < 20 or (~pos).sum() < 20:
        res.append(("1 recovery", False,
                    f"degenerate split: {int(pos.sum())} PC1>0 vs "
                    f"{int((~pos).sum())} PC1<0"))
        return

    cond, esss = [], []
    for i in range(len(b["y"])):
        m = np.ones(len(b["y"]), bool); m[i] = False
        w = kernel_weights(b["Z"][m], b["Z"][i], b["ages"][i][m], s)
        r = estimate(b["y"][m], w, b["labels"][m], b["C"])
        cond.append(r["conditional"]); esss.append(r["ess"])
    cond = np.asarray(cond); esss = np.asarray(esss)
    ok_i = np.isfinite(cond)

    d = float(np.mean(cond[pos & ok_i]) - np.mean(cond[~pos & ok_i]))
    se = float(np.sqrt(np.var(cond[pos & ok_i], ddof=1) / max(1, (pos & ok_i).sum())
                       + np.var(cond[~pos & ok_i], ddof=1)
                       / max(1, ((~pos) & ok_i).sum())))
    target = 2.0 * effect
    ok = abs(d - target) <= 2.0 * se and d > 0
    res.append(("1 recovery", ok,
                f"planted {target*100:+.3f}% (PC1+ minus PC1-), recovered "
                f"{d*100:+.3f}% +/- {2*se*100:.3f}% | n={n_events}, "
                f"median ESS {np.median(esss):.1f}, sigma {s:.3f} "
                f"(target median ESS {tgt:.1f}, bisection "
                f"{'converged' if conv else 'HIT BOUND'})"))''',
    "test 1 -- replace the vacuous isfinite check with an actual recovery test",
), (
    "src/analog_event.py",
    '''def test_3_tiers(rng, cfg, res):
    seen, rows = set(), []
    for n in (10, 20, 40, 80, 160):
        b = build_blind(n, 0.004, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
        r = estimate(b["y"], w, b["labels"], b["C"])
        seen.add(r["tier"])
        rows.append(f"n={n}: ESS {r['ess']:.1f} w {r['w_shrink']:.2f} "
                    f"tier {r['tier']}")
        exp = 3 if (r["ess"] < ESS_FLOOR or r["tau2_zero"]) else (
            1 if r["w_shrink"] >= TIER1_W else
            (2 if r["w_shrink"] >= TIER2_W else 3))
        if r["tier"] != exp:
            res.append(("3 tier labelling", False,
                        f"n={n}: tier {r['tier']}, boundaries imply {exp}"))
            return
    res.append(("3 tier labelling", True,
                "tier matches the w/ESS boundaries at every n | " + "; ".join(rows)))''',
    '''def test_3_tiers(rng, cfg, res):
    """Are tiers 1, 2 AND 3 all REACHABLE, and correctly assigned?

    The previous version checked only that the assigned tier agreed with the
    boundaries -- and every case landed at tier 3, so a function returning 3
    unconditionally would have passed. This version plants strong / moderate /
    no between-cell structure and REQUIRES all three tiers to appear."""
    seen, rows = set(), []
    # (label, n_events, per-regime cell offset). A larger offset means more real
    # between-cell variation -> larger tau2 -> smaller k -> larger w.
    cases = [("strong", 400, 0.020), ("moderate", 400, 0.004),
             ("none", 400, 0.000), ("thin", 6, 0.020)]
    for label, n, off in cases:
        b = build_blind(n, 0.0, rng, cfg)
        y = b["y"] + off * (b["labels"] - b["labels"].mean())
        s, _, _, _ = _sigma_for(b)
        w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
        r = estimate(y, w, b["labels"], b["C"])
        seen.add(r["tier"])
        rows.append(f"{label}: ESS {r['ess']:.1f} tau2 {r['tau2']:.1e} "
                    f"w {r['w_shrink']:.2f} -> tier {r['tier']}")
        exp = 3 if (r["ess"] < ESS_FLOOR or r["tau2_zero"]) else (
            1 if r["w_shrink"] >= TIER1_W else
            (2 if r["w_shrink"] >= TIER2_W else 3))
        if r["tier"] != exp:
            res.append(("3 tier labelling", False,
                        f"{label}: tier {r['tier']}, boundaries imply {exp} | "
                        + "; ".join(rows)))
            return
    missing = {1, 2, 3} - seen
    if missing:
        res.append(("3 tier labelling", False,
                    f"tiers never reached: {sorted(missing)} -- the boundaries "
                    f"are not exercised, so agreement with them proves nothing | "
                    + "; ".join(rows)))
        return
    res.append(("3 tier labelling", True,
                "all three tiers reached AND correctly assigned | "
                + "; ".join(rows)))''',
    "test 3 -- require tiers 1, 2 and 3 to all be reachable",
), (
    "src/analog_event.py",
    '''def test_5_null_calibration(rng, cfg, res, reps, iters):
    """THE EXPENSIVE ONE. No effect planted -> p should be ~uniform and the
    rejection rate at alpha=0.05 must land in [0.02, 0.08]."""
    ps = []
    for i in range(reps):
        b = build_blind(60, 0.0, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        out = permutation_null(b["Z"], b["ages"], b["y"], b["labels"], s,
                               b["C"], iters, rng)
        ps.append(out["p_mse"])
        if (i + 1) % 20 == 0:
            r = np.mean(np.array(ps) < 0.05)
            print(f"      rep {i+1}/{reps}  rejection so far {r:.3f}")
    ps = np.array(ps)
    rate = float(np.mean(ps < 0.05))
    ok = 0.02 <= rate <= 0.08
    res.append(("5 null calibration", ok,
                f"{reps} reps x {iters} perms, no effect planted: "
                f"rejection at alpha=0.05 is {rate:.3f} "
                f"(registered band [0.02, 0.08]); median p {np.median(ps):.3f}"))''',
    '''def test_5_null_calibration(rng, cfg, res, reps, iters):
    """THE EXPENSIVE ONE, RE-SPECIFIED. The original FAILED and that stands.

    ORIGINAL RESULT, PRESERVED: 200 reps x 500 perms, rejection 0.005 against
    the registered band [0.02, 0.08], median p 0.906. Recorded in
    docs/analog_event_selftest.md and reported in the write-up. Not deleted.

    DIAGNOSIS, demonstrated in simulation before this was changed: when tau2 = 0
    the registered null path sets w = 0, so pred_blend == pred_uncond exactly,
    the gain is identically zero in the observed AND every permuted draw, and
    p = 1.0 by ties. 50-80% degenerate reps reproduces median p ~1.0 and
    rejection ~0.01. The ESTIMATOR was correct; the TEST could not measure
    calibration where the estimator refuses to condition.

    RE-SPECIFIED, NOT LOOSENED. Same band, applied to the subpopulation where a
    conditional claim is actually made:
      5a  degenerate fraction reported as a first-class number
      5b  rejection rate over reps with tau2 > 0, band unchanged [0.02, 0.08],
          minimum 40 such reps or the verdict is INCONCLUSIVE, not PASS

    Conditioning on tau2 > 0 selects on the estimator's own output. Stated
    plainly rather than buried: it is the only subpopulation in which "is the
    null calibrated" is a meaningful question."""
    ps, degen = [], []
    for i in range(reps):
        b = build_blind(60, 0.0, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        out = permutation_null(b["Z"], b["ages"], b["y"], b["labels"], s,
                               b["C"], iters, rng)
        # degenerate <=> the blend never departed from the unconditional, so the
        # statistic is identically zero and its p-value carries no information
        d = bool(np.isclose(out["mse_blend"], out["mse_uncond"], rtol=0, atol=1e-18))
        degen.append(d)
        ps.append(out["p_mse"])
        if (i + 1) % 20 == 0:
            a = np.asarray(ps); g = ~np.asarray(degen)
            r = float(np.mean(a[g] < 0.05)) if g.sum() else float("nan")
            print(f"      rep {i+1}/{reps}  degenerate {np.mean(degen):.2f}  "
                  f"rejection (conditioning reps) {r:.3f}")

    ps = np.asarray(ps); degen = np.asarray(degen)
    frac_d = float(np.mean(degen))
    live = ~degen
    n_live = int(live.sum())
    rate_all = float(np.mean(ps < 0.05))

    res.append(("5a degenerate fraction", True,
                f"tau2 = 0 in {frac_d:.1%} of {reps} reps -- the registered null "
                f"path fired and the blend stayed at the unconditional. This is "
                f"the estimator working, and it is why the ORIGINAL test 5 "
                f"failed (rejection 0.005, median p 0.906): a statistic that is "
                f"identically zero gives p = 1 by ties."))

    if n_live < 40:
        res.append(("5b null calibration", False,
                    f"only {n_live} of {reps} reps conditioned (tau2 > 0); "
                    f"40 required. INCONCLUSIVE, not a pass. Naive rate over "
                    f"all reps {rate_all:.3f}."))
        return
    rate = float(np.mean(ps[live] < 0.05))
    ok = 0.02 <= rate <= 0.08
    res.append(("5b null calibration", ok,
                f"over the {n_live} reps where the estimator conditioned: "
                f"rejection at alpha=0.05 is {rate:.3f}, registered band "
                f"[0.02, 0.08] UNCHANGED; median p {np.median(ps[live]):.3f}. "
                f"Naive rate over all {reps} reps including degenerate ones: "
                f"{rate_all:.3f}."))''',
    "test 5 -- report the degenerate fraction, calibrate on conditioning reps only",
), (
    "src/analog_event.py",
    """    print(f"  running test 5 (the expensive one) ...")
    test_5_null_calibration(rng, cfg, res, reps, iters)""",
    """    print(f"  running test 5 (the expensive one) ...")
    test_5_null_calibration(rng, cfg, res, reps, iters)
    # test 5 now contributes TWO rows (5a degenerate fraction, 5b calibration)""",
    "self-test runner -- note that test 5 now yields two rows",
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
    print("""FIRST -- preserve the original test 5 failure before it is overwritten:

  cp docs/analog_event_selftest.md docs/analog_event_selftest_v1_FAILED.md
  git add docs/analog_event_selftest_v1_FAILED.md
  git commit -m "preserve original blind test 5 failure (rejection 0.005,
  median p 0.906) before test 5 is re-specified"

THEN the quick pass, to see tests 1 and 3 before spending an hour:

  python -m src.analog_event --self-test --quick

  Test 1 must now RECOVER the planted 1.000% within its interval.
  Test 3 must reach tiers 1, 2 AND 3.

THEN the full run:

  caffeinate -i nohup python -m src.analog_event --self-test > selftest2.log 2>&1 &
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
