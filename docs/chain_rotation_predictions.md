# Predictions recorded BEFORE running the corrected chain_rotation.py

Registered 2026-08-21, before `src/chain_rotation.py` was installed or executed.
Purpose: a result that can be explained after the fact teaches nothing. Fixing
the expected values first makes the outcome capable of being wrong.

No prediction is recorded for Steven. The inputs the questions turn on -- the
gaps between adjacent net_lead scores -- have not been observed, so any number
would be arbitrary rather than a prior. Recorded as declined, not as zero.

## Predictions

1. Name-slots changed by removing the look-ahead: **8-14 of 20**.
   Sub-period betas rest on ~1,670 days vs ~6,700 full-sample, so ~2x noisier,
   and 5-item rankings reshuffle easily when adjacent net_lead scores are close.
2. Mean pairwise agreement: **moves, plausibly changes sign, lands within +-0.35**.
3. Agreement distinguishable from random reshuffling: **NO**. The statistic's
   sampling SD is ~0.25; the observed -0.250 sits about one SE from zero.
4. Any pairwise lead-lag surviving Holm correction: **NO**.

Implied claim: the numbers change, the conclusion does not.

## Invariance check (this one is not a prediction but a correctness requirement)

Sections [1] and [2] are untouched by the fix -- the full-sample beta was always
correct for the full-sample test. Spearman -0.100 and p=0.605 must reproduce
EXACTLY. If they do not, something other than the look-ahead has moved and the
run is not trustworthy.

## Outcome

*(filled in after the run)*

## Outcome (run 2026-08-21, seed 42, 2000 iters, window -> 2026-08-20)

| # | predicted | actual | verdict |
|---|---|---|---|
| 1 | 8-14 of 20 slots move | 8 | correct, bottom edge |
| 2 | moves, plausibly changes sign, within +-0.35 | -0.250 -> -0.217 | WRONG on magnitude |
| 3 | not distinguishable from reshuffling | p = 0.2659 | correct |
| 4 | no pair survives Holm | 0 / 10 | correct |

Invariance check PASSED on the deterministic statistic: Spearman = -0.100 exactly.
The permutation p is 0.5947 vs 0.605 recorded -- a gap of 0.0103 against a Monte
Carlo SE of ~0.011 at 2000 iterations, and the window is longer than when 0.605
was recorded, so every rotation draw differs. Within noise. To be confirmed at
--iters 20000.

WRONG PRIOR (fourth recorded). Predicted the agreement statistic would move
substantially and possibly flip sign, applying the correction drawn from the
first three wrong priors -- that results are more basis-carried than expected.
It moved 0.033. The correction was over-applied.

The refinement: the PRESENTATION layer is basis-sensitive (8 of 20 order slots
changed) while the TEST STATISTIC is not (-0.250 -> -0.217, both ~1 SD below a
null centred at -0.007, SD 0.200). Reshuffling 40% of positions barely moved the
number precisely BECAUSE both versions are noise realisations. Robustness of a
statistic under a basis change is not evidence of signal when the statistic sits
at its null.

Also wrong, separately: predicted the per-lag profile would peak at 1-2 days,
showing the k=1..10 average diluting a fast cascade. Peaks are scattered
(5,6,6,1,2,10,10,8,10,4) with three at the k=10 boundary, which is where argmax
lands on a flat profile. Per-lag magnitudes reach +-0.06 while the average is
~0.008, so the averaging dilutes sign-flipping NOISE. This strengthens the null.
