#!/usr/bin/env python3
"""
patch_null_permute_y.py -- add a second permutation null and REPORT BOTH.

*** THIS IS THE THIRD CHANGE TO TEST 5 FOLLOWING A FAILURE. Declared, not
buried. The defence against "adjust until it passes" is that BOTH nulls are
computed and BOTH are reported, every run, whatever they say. Nothing is
replaced; a variant is added. ***

THE PRINCIPLED ARGUMENT, which predates the full-run result
    prereg_analog_event.md section 5.3 registers the null as: "Shuffle the
    macro-similarity weights across events, preserving group sizes and every
    return path, destroying only the correspondence between macro state and
    outcome."

    permute_Z (as implemented) does NOT preserve everything else. Macro states
    are autocorrelated and events close in time are close in Z, so in the
    OBSERVED data the similarity and recency kernels concentrate on the same
    pairs. Permuting Z breaks that alignment and changes the ESS distribution,
    which changes w = ESS/(ESS+k), which changes the estimator's variance. The
    permuted draws are therefore NOT exchangeable with the observed one -- the
    null differs from the observed in more than the thing it is supposed to
    isolate.

    permute_y destroys exactly the state<->outcome correspondence and NOTHING
    else. Z, ages, sigma, ESS and the whole weight geometry are identical in
    every draw. That is the registered intent, implemented literally.

WHAT IS NOT CHANGED
    The band [0.02, 0.08]. The minimum of 40 conditioning reps. The abstention
    floor. The tau2 = 0 null path. The degenerate-fraction reporting.

WHAT IS REGISTERED NOW, BEFORE THE FULL RUN RETURNS
    * permute_y becomes the PRIMARY null for section 5.3, with the timing of
      this change declared in the amendment table.
    * permute_Z is retained and reported alongside, permanently. It is not
      deleted because its result is evidence about how sensitive the null is to
      its own construction.
    * If the two disagree on the verdict, THAT DISAGREEMENT IS THE FINDING and
      is reported as such -- no tie-break, no preference exercised after the
      fact.
    * A rejection rate BELOW 0.02 means the null is CONSERVATIVE: it under-
      rejects, cannot fabricate a false positive, and costs power. Registered
      consequence: any step 3 null must then be reported as "inconclusive at
      this power", never as "macro conditioning has no effect".

Run from the repo root:
    python patch_null_permute_y.py --dry-run
    python patch_null_permute_y.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_event.py",
    '''def permutation_null(Z, ages_matrix, y, labels, sigma, C, iters, rng, hl=HL_D):
    """Shuffle macro weights across events, preserving group sizes and every
    return path, destroying only state<->outcome correspondence.  prereg 5.3"""
    pb, pu = loo_evaluate(Z, ages_matrix, y, labels, sigma, C, hl)
    mse_b, hit_b = metrics(pb, y)
    mse_u, hit_u = metrics(pu, y)
    obs = (mse_u - mse_b, hit_b - hit_u)        # positive = conditioning helps
    n = len(y)
    null_mse, null_hit = np.empty(iters), np.empty(iters)
    for it in range(iters):
        perm = rng.permutation(n)
        Zp = Z[perm]
        pbp, pup = loo_evaluate(Zp, ages_matrix, y, labels, sigma, C, hl)
        m_b, h_b = metrics(pbp, y)
        m_u, h_u = metrics(pup, y)
        null_mse[it] = m_u - m_b
        null_hit[it] = h_b - h_u
    p_mse = (np.sum(null_mse >= obs[0]) + 1) / (iters + 1)
    p_hit = (np.sum(null_hit >= obs[1]) + 1) / (iters + 1)
    return dict(obs_mse_gain=obs[0], obs_hit_gain=obs[1],
                p_mse=float(p_mse), p_hit=float(p_hit),
                mse_blend=mse_b, mse_uncond=mse_u,
                hit_blend=hit_b, hit_uncond=hit_u)''',
    '''def permutation_null(Z, ages_matrix, y, labels, sigma, C, iters, rng, hl=HL_D,
                     mode="permute_y"):
    """Destroy the state<->outcome correspondence and nothing else.  prereg 5.3

    TWO MODES, both computed and both reported (amendment 2026-08-25):

      permute_y  PRIMARY. Shuffles the OUTCOMES across events. Z, ages, sigma,
                 ESS and the entire weight geometry are IDENTICAL in every draw,
                 so the permuted draws are exchangeable with the observed one
                 and differ in exactly the thing the null is meant to isolate.

      permute_Z  ORIGINAL, retained. Shuffles the macro states. Because macro
                 states are autocorrelated and events close in time are close in
                 Z, the similarity and recency kernels concentrate on the same
                 pairs in the observed data; permuting Z breaks that alignment
                 and changes the ESS distribution, hence w = ESS/(ESS+k), hence
                 the estimator's variance. The permuted draws are therefore NOT
                 exchangeable with the observed one.

    permute_Z is kept rather than deleted: its result is evidence about how
    sensitive the null is to its own construction, which is worth reporting.
    """
    pb, pu = loo_evaluate(Z, ages_matrix, y, labels, sigma, C, hl)
    mse_b, hit_b = metrics(pb, y)
    mse_u, hit_u = metrics(pu, y)
    obs = (mse_u - mse_b, hit_b - hit_u)        # positive = conditioning helps
    n = len(y)
    null_mse, null_hit = np.empty(iters), np.empty(iters)
    for it in range(iters):
        perm = rng.permutation(n)
        if mode == "permute_y":
            yp = y[perm]
            pbp, pup = loo_evaluate(Z, ages_matrix, yp, labels, sigma, C, hl)
            m_b, h_b = metrics(pbp, yp)
            m_u, h_u = metrics(pup, yp)
        elif mode == "permute_Z":
            pbp, pup = loo_evaluate(Z[perm], ages_matrix, y, labels, sigma, C, hl)
            m_b, h_b = metrics(pbp, y)
            m_u, h_u = metrics(pup, y)
        else:
            raise ValueError(f"unknown null mode {mode!r}")
        null_mse[it] = m_u - m_b
        null_hit[it] = h_b - h_u
    p_mse = (np.sum(null_mse >= obs[0]) + 1) / (iters + 1)
    p_hit = (np.sum(null_hit >= obs[1]) + 1) / (iters + 1)
    return dict(obs_mse_gain=obs[0], obs_hit_gain=obs[1],
                p_mse=float(p_mse), p_hit=float(p_hit),
                mse_blend=mse_b, mse_uncond=mse_u,
                hit_blend=hit_b, hit_uncond=hit_u, mode=mode)''',
    "permutation_null -- add permute_y mode, keep permute_Z, default to permute_y",
), (
    "src/analog_event.py",
    '''    ps, degen = [], []
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
    rate_all = float(np.mean(ps < 0.05))''',
    '''    MODES = ("permute_y", "permute_Z")      # primary first
    ps = {m: [] for m in MODES}
    degen = []
    for i in range(reps):
        b = build_blind(60, 0.0, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        first = None
        for m in MODES:
            out = permutation_null(b["Z"], b["ages"], b["y"], b["labels"], s,
                                   b["C"], iters, rng, mode=m)
            ps[m].append(out["p_mse"])
            if first is None:
                first = out
        # degenerate <=> the blend never departed from the unconditional, so the
        # statistic is identically zero and its p-value carries no information.
        # Determined from the OBSERVED fit, which is the same for both modes.
        degen.append(bool(np.isclose(first["mse_blend"], first["mse_uncond"],
                                     rtol=0, atol=1e-18)))
        if (i + 1) % 20 == 0:
            g = ~np.asarray(degen)
            bits = []
            for m in MODES:
                a = np.asarray(ps[m])
                bits.append(f"{m} {float(np.mean(a[g] < 0.05)):.3f}"
                            if g.sum() else f"{m} n/a")
            print(f"      rep {i+1}/{reps}  degenerate {np.mean(degen):.2f}  "
                  f"rejection: " + "  ".join(bits))

    degen = np.asarray(degen)
    frac_d = float(np.mean(degen))
    live = ~degen
    n_live = int(live.sum())
    rates = {m: float(np.mean(np.asarray(ps[m])[live] < 0.05))
             if n_live else float("nan") for m in MODES}
    ps_primary = np.asarray(ps["permute_y"])
    ps = ps_primary                       # primary drives the verdict below
    rate_all = float(np.mean(ps < 0.05))''',
    "test 5 -- run both nulls per rep, track both rejection rates",
), (
    "src/analog_event.py",
    '''    rate = float(np.mean(ps[live] < 0.05))
    ok = 0.02 <= rate <= 0.08
    res.append(("5b null calibration", ok,
                f"over the {n_live} reps where the estimator conditioned: "
                f"rejection at alpha=0.05 is {rate:.3f}, registered band "
                f"[0.02, 0.08] UNCHANGED; median p {np.median(ps[live]):.3f}. "
                f"Naive rate over all {reps} reps including degenerate ones: "
                f"{rate_all:.3f}."))''',
    '''    rate = rates["permute_y"]
    rate_z = rates["permute_Z"]
    ok = 0.02 <= rate <= 0.08
    agree = (0.02 <= rate <= 0.08) == (0.02 <= rate_z <= 0.08)
    note = ("both nulls agree on the verdict" if agree else
            "** THE TWO NULLS DISAGREE ON THE VERDICT -- that disagreement is "
            "itself the finding and is reported as such, with no tie-break **")
    conservative = ("  Rate below 0.02 = the null is CONSERVATIVE: it under-"
                    "rejects, cannot fabricate a false positive, and costs "
                    "power. Registered consequence: a step 3 null must be "
                    "reported as 'inconclusive at this power', never as 'macro "
                    "conditioning has no effect'." if rate < 0.02 else "")
    res.append(("5b null calibration", ok,
                f"over the {n_live} reps where the estimator conditioned, band "
                f"[0.02, 0.08] UNCHANGED -- "
                f"PRIMARY permute_y: {rate:.3f} | permute_Z (original, "
                f"retained): {rate_z:.3f}; {note}. Median p (permute_y) "
                f"{np.median(ps[live]):.3f}. Naive rate over all {reps} reps "
                f"including degenerate ones: {rate_all:.3f}.{conservative}"))''',
    "test 5b -- report both rejection rates, flag disagreement, flag conservatism",
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
    print("""WAIT for the running self-test (PID from `jobs`) to finish first --
this edits the file it is executing from. Then:

  python -m src.analog_event --self-test --quick      # ~10 min, both nulls
  caffeinate -i nohup python -m src.analog_event --self-test > selftest3.log 2>&1 &

Test 5 now costs 2x: both nulls run on every replication.

AMENDMENT to add to docs/prereg_analog_event.md section 11 BEFORE reading the
result:

| 2026-08-25 | Section 5.3's null gains a second implementation. permute_y
(shuffle outcomes, weight geometry identical in every draw) becomes PRIMARY;
permute_Z (shuffle macro states, the original) is retained and reported
alongside. Both computed every run. | permute_Z changes the ESS distribution
because macro states are autocorrelated and similarity and recency concentrate
on the same pairs, so its draws are not exchangeable with the observed fit.
permute_y destroys the state-outcome correspondence and nothing else, which is
what 5.3 registered in words. THIRD change to test 5 after a failure --
declared. Both nulls reported permanently; disagreement between them is
reported as a finding, not tie-broken. |
| 2026-08-25 | Registered in advance: a rejection rate below 0.02 means the
null is conservative. A step 3 null must then be reported as "inconclusive at
this power", never as "macro conditioning has no effect". | Fixed before the
full run returned, so the interpretation is not chosen to suit the number. |
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
