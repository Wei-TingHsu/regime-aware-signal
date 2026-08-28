# Amendment 4 — the ESS knife-edge

**Registered 2026-08-28, after the step 3 unblinding completed.**

This timing is the point. The defect below was observed in the dry run on 26 August, *before* the unblinding was launched, and was deliberately **not** fixed then. Changing an abstention threshold after seeing which cells sit on either side of it — but before seeing their results — is still a change made with knowledge of what it would include. The registered rule stayed exactly as written for the whole run, the knife-edge was reported as a limitation of that run, and the correction is registered here for future runs only.

## The defect

Two clauses of `prereg_analog_event.md` interact badly:

- **§4** clips the sigma-selection target to a **minimum effective sample size of 8**.
- **§3.5** abstains whenever the realised ESS is **below 8**.

So the selection step aims at exactly the value the abstention step uses as its floor. Pools therefore land on the boundary rather than distributing around it, and the abstain/proceed decision turns on the third decimal place of a quantity that was never intended to carry that much weight.

Observed in the 26 August dry run, recorded before the run was launched:

| cell | median ESS | outcome |
|---|---|---|
| `political_order` / UUP | **7.993** | abstained |
| `earnings_8k` / UUP | **8.051** | proceeded |

A difference of 0.058 in effective sample size decided whether a cell produced a number at all. Neither outcome is wrong under the registered rule; the rule is simply making a categorical decision on a distinction it cannot support.

## What was NOT done

The rule was not changed mid-run. The unblinding ran to completion under §4 and §3.5 as originally registered, and `docs/unblind_step3_results.md` reports six abstentions at the floor without adjustment. Any cell that abstained at 7.99 stays abstained in that record.

## The corrected rule, for future runs

**A4.1 — separate the target from the floor.** The sigma-selection target ESS is raised to **12**, while the abstention floor stays at **8**. Selection then aims above the floor rather than at it, and a pool that lands at 8 is one that genuinely could not do better rather than one the selector steered there.

**A4.2 — a declared indeterminate band.** Realised ESS in **[7.5, 8.5)** is reported as `MARGINAL` rather than resolved to either side. A marginal cell prints its estimate, its ESS and the word MARGINAL, and is excluded from any count of passing cells. It is neither a pass nor an abstention, because the evidence does not distinguish those.

**A4.3 — the floor itself is unchanged.** Eight remains the abstention threshold. It was registered before any result was seen and there is no evidence-based reason to move it; moving it now would be exactly the manoeuvre this amendment exists to prevent.

## Scope

Applies to runs launched after this file is committed. It does **not** apply retrospectively to:

- the step 3 unblinding of 26 August (7 of 45 cells),
- the robustness re-test of 26 August (1 of 7 confirmed),
- any figure appearing in the business plan or the pitch deck.

Re-running the unblinding under A4.1–A4.3 and reporting the new number in place of the old would be a second look at the same data with a rule adjusted after the first look. If it is ever run, both results must be reported side by side with their registration dates, and the original remains the headline.

## Why this is recorded rather than quietly fixed

The knife-edge cost this project one thing it can name: `political_order`/UUP produced no estimate on a distinction of 0.058. That is a real limitation of a real run and it belongs in the record. A project whose entire commercial argument is calibrated refusal cannot afford to tidy away the one case where its own threshold behaved arbitrarily.
