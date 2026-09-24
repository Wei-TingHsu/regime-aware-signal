# Specificity gate — result

*Run 2026-09-24 16:26:35 +0800.*

**Amended criterion** (`docs/prereg_analog_event.md` §11): the lower bound of a 95% bootstrap CI on the spread must exceed 0.25, and every expected-high source must sit above every expected-low source.

> **Timing declared.** The amendment was made after seeing a point spread of 0.26 on n=20 per source. It is a **tightening** — the original point comparison could not distinguish 0.26 from failing. Recorded rather than quietly applied.

| source | n | mean specificity | sd | se | expected | read condition |
|---|---|---|---|---|---|---|
| earnings_8k | 671 | 0.687 | 0.201 | 0.008 | HIGH | v1-2026-08-23 / claude-sonnet-5 |
| fomc_statement | 132 | 0.574 | 0.174 | 0.015 | HIGH | v1-2026-08-23 / claude-sonnet-5 |
| political_order | 873 | 0.550 | 0.240 | 0.008 | HIGH | v1-2026-08-23 / claude-sonnet-5 |
| fomc_minutes | 125 | 0.494 | 0.127 | 0.011 | - | v1-2026-08-23 / claude-sonnet-5 |
| political_other | 816 | 0.170 | 0.241 | 0.008 | low | v1-2026-08-23 / claude-sonnet-5 |

Widest pair: **earnings_8k** vs **political_other**. Spread **0.517**, 95% CI **[0.494, 0.539]**.

- Clause 1 (CI lower bound > 0.25): **PASS**
- Clause 2 (ordering): **PASS**

## Verdict: PASS

`specificity` enters the content-class definition (§2.1) and the step 5 weighting rule (§7.2).

