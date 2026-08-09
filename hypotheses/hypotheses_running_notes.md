# Running Hypotheses Notes

Pre-registered ideas to test later. Captured as they arise so they are not lost.
These are NOT yet formalized into `hypotheses/hypotheses.yaml` — this is the holding
pen. Each entry records the idea, its origin, why it matters, and what data/phase it needs.

---

## H-X01 — Margin-call cross-asset contagion (tech drawdown → forced gold selling)

**Statement.** In liquidity-stress regimes, a large idiosyncratic drawdown in a mega-cap
technology name (e.g. Microsoft, Nvidia) can induce *correlated selling in gold*, inverting
gold's usual safe-haven behavior. Mechanism: investors facing margin calls on leveraged tech
positions sell liquid assets — including gold — to raise cash, so gold falls *with* equities
instead of rising against them.

**Origin.** Student's own reasoning during GDELT/regime-validation work (Aug 2026). Extends
the observed real-world pattern where gold fell during the March 2020 crash due to forced
liquidation for cash, rather than rising as a safe haven.

**Why it matters.** Directly relevant to Problem 1 (safe-haven inversion / conditionality):
identifies a *specific, named channel* — the margin-call/liquidity channel — under which the
gold–equity correlation flips sign. This is a distinctive, testable relationship that most
retail-facing tools cannot quantify.

**What it needs to test.**
- Asset-level (not just macro) event data — the trigger is a *company-specific* shock.
- Likely SEC EDGAR 8-K filings and/or GDELT entity-level events for the tech name.
- Regime conditioning: the effect is hypothesized to appear ONLY in liquidity-stress regimes,
  not in calm regimes — so it depends on the (validated) regime labels.
- Correlation/beta analysis of gold returns vs. the tech name's returns, conditional on regime.

**Status.** Parked for MVP. Bring back in the rotation-engine / cross-asset phase, after
(a) regime labels are validated and (b) entity-level event data (EDGAR + GDELT entities) exists.

**Caveat.** Relationship is assumed, not proven. The test must allow for the null (no inversion)
and must control for the general risk-off move (gold may fall simply because everything falls,
not specifically because of the margin-call channel). Distinguishing the margin-call channel
from generic risk-off is the hard part and must be designed for.
