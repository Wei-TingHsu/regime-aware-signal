# Specificity gate — result

*Run 2026-08-25 15:45:26 +0800.*

**Amended criterion** (`docs/prereg_analog_event.md` §11): the lower bound of a 95% bootstrap CI on the spread must exceed 0.25, and every expected-high source must sit above every expected-low source.

> **Timing declared.** The amendment was made after seeing a point spread of 0.26 on n=20 per source. It is a **tightening** — the original point comparison could not distinguish 0.26 from failing. Recorded rather than quietly applied.

| source | n | mean specificity | sd | se | expected | read condition |
|---|---|---|---|---|---|---|
| earnings_8k | 60 | 0.631 | 0.122 | 0.016 | HIGH | v1-2026-08-23 |
| political_order | 60 | 0.603 | 0.255 | 0.033 | HIGH | v1-2026-08-23 |
| fomc_minutes | 60 | 0.489 | 0.133 | 0.017 | - | v1-2026-08-23 |
| political_other | 60 | 0.268 | 0.316 | 0.041 | low | v1-2026-08-23 |

Widest pair: **earnings_8k** vs **political_other**. Spread **0.363**, 95% CI **[0.281, 0.455]**.

- Clause 1 (CI lower bound > 0.25): **PASS**
- Clause 2 (ordering): **PASS**

## Verdict: PASS

`specificity` enters the content-class definition (§2.1) and the step 5 weighting rule (§7.2).

