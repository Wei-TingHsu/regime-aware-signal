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
