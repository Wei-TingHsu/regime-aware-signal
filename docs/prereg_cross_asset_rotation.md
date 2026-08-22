# PRE-REGISTRATION — Cross-asset rotation (flight-to-quality cascade)

**Status: REGISTERED, UNRUN.** Committed before execution. The git timestamp is
the pre-registration evidence. Any post-run edit is recorded in §8 with its reason.

---

## 1. Hypothesis, and why it is a NEW one rather than a retry

The semiconductor chain (NVDA→TSM→ASML→MU→INTC) was closed as a null on
2026-08-21/22 under four tests: unconditional (3 arms, 6,936 sessions),
shock-conditional (203 episodes, eplen ladder), and news-conditional (26 GDELT
episodes). Swapping in five *different semiconductors* would be data mining —
same theory, new tickers.

This is a different theory with an independent mechanism. Intra-sector rotation
requires supply-chain information to propagate between firms with a lag, which is
a weak mechanism the literature has largely failed to support. Cross-asset
rotation rests on **institutional capital reallocating across asset classes**:
mandate constraints, rebalancing calendars, and flows that take days to execute.

> **Registered order: TLT → UUP → GLD → SPY → USO.**
>
> Treasuries are the deepest and most liquid haven and reprice first. The dollar
> follows as global funding demand rises. Gold is a slower haven — real-money
> allocators rather than fast desks. Equities bleed over days as positioning
> unwinds. Oil is last, because demand destruction takes time to price.

**The concentration statistic is order-agnostic**, so the registered order is not
required for detection — it exists so the result can be compared against a stated
belief rather than rationalised afterward.

## 2. Assets and sample

`TLT, SPY, GLD, UUP, USO` — duration, equity, precious metal, dollar, energy.
Five distinct asset classes. `dropna()` truncates to the shortest history; UUP
(2007) sets the start, giving roughly 19 years.

Rejected and why: no credit ETF exists in the panel (no HYG/LQD); DIA is absent;
adding a sixth asset would shorten the sample without adding a distinct class.

## 3. Residualization: NONE

`--residualize none`. Registered with reasoning, because the default is wrong here:

The leave-one-out approach (correct for five semiconductors sharing a sector beta)
is **actively destructive** for a cross-asset basket. There is no shared factor —
TLT and SPY are frequently negatively correlated, so the equal-weight mean of the
others is not a common factor at all. Worse, cross-asset rotation **is** a raw-flow
phenomenon: money leaving bonds for equities appears as TLT down, SPY up.
Removing a common factor would strip out exactly the thing being tested.

## 4. Trigger: RISK-OFF ONLY

`--trigger shock --shock-on SPY --shock-sign down --z 2.0`

Registered with reasoning. Flight-to-quality is **directional by construction** —
it occurs on the way down. Pooling rallies and selloffs would average opposite
rotations toward zero even if both were real, which is the dilution the
architecture doc flags as "variable order."

Note the equal-weight chain mean is NOT used as the shock proxy here: averaging
TLT with SPY produces a series with no economic meaning. SPY is the proxy.

Expected cost: roughly half the episodes of a bidirectional trigger.

**Not registered as a cause of the chain null.** Bidirectional averaging is one
possible dilution mechanism, but the shock arm's τ = +0.004 against a null SD of
0.002 is not the signature of a real effect being cancelled. The chain null
stands on its own; this design choice is justified by the mechanism of THIS
hypothesis, not by an explanation of the previous one.

## 5. Design (inherited from `episode_rotation.py`, unchanged)

- Episode = the **eplen sessions after** the trigger; trigger day excluded (gap
  conceded, and including the day that defines the trigger would be circular).
- De-clustering gap = eplen, so episodes never overlap.
- eplen **primary 15**, ladder **{10, 15, 20}**, all rungs reported regardless of
  outcome. No rung may be promoted to primary after results are seen.
- Window integrity: every asset must have a return on every session of the episode.
- Statistics: [1] pooled within-episode lead-lag at k=1..3, max-over-k per pair,
  Holm over 10 pairs; [2] order concentration — mean pairwise Kendall τ-b of
  per-episode half-max response orders.
- Null for both: independent per-name episode shuffle. Preserves every path shape
  and the episode structure; destroys only cross-name within-episode alignment.

## 6. Success criterion — written before the answer

> **A positive verdict requires order concentration [2] to clear p < 0.05 at the
> primary rung AND at one adjacent rung of the eplen ladder, with the same sign.**

Statistic [1] is supporting evidence, not the verdict. Holm is applied *within*
each rung, not across the ladder: 30 pair-tests total across {10,15,20}, so ~1.5
false positives are expected at α=0.05. **A lone significant pair is not a
detection.**

## 7. Detection capability — demonstrated, not assumed

Before the real run, `--inject TLT,SPY,1,0.3` plants a known lead in the **real**
episodes and must be recovered. On the semiconductor basket this moved d from
−0.006 (p=0.997) to **+0.502 (p=0.0005, Holm 0.005)**. The audit is repeated per
basket because correlation structure differs.

Known limitation: the injection audit validates statistic **[1] only**. A lag-1
correlation barely moves half-max *timing*, so [2] was not exercised by it.
Statistic [2] is validated on synthetic data (identical episode orders → τ = 1.00,
random orders → −0.02) but **not on this panel**. Recorded as a limitation.

## 8. Amendments

*(none — this section exists so post-hoc changes are visible rather than silent)*

| date | change | reason |
|---|---|---|
| | | |
