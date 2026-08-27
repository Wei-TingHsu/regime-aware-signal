# Step 5 — weighted net view

*Run 2026-08-27 12:11:58 +0800. No API calls.*

**Rule implemented: `prereg_analog_event.md` §7.2, fixed.** `weight = magnitude · specificity · novelty · confidence`; `net = Σ(weight · direction) / Σ(weight)`. A straight product, so any near-zero field vetoes the document. `specificity²` is not used — §7.2 forbids it by name. The §4 gate passed, so `specificity` stays in and no substitution is reported.

**§7.1 registered count: 279 days carry documents from two or more different sources**, against a threshold of 50 fixed on 2026-08-24 before any counting. §7.3, the estimated alternative, is therefore *admissible* — but it is **not authorised by that document** and is not implemented here. It needs its own pre-registration.

*(An earlier script counted per-asset collisions and summed them to 194. That is a different statistic from the one §7.1 registers; both are reported so the correction is visible rather than silent.)*

| asset | net views | from ≥2 docs | sign disagreements | mean \|net\| | mean weight |
|---|---|---|---|---|---|
| GLD | 286 | 17 | 6 | 0.173 | 0.087 |
| SPY | 803 | 119 | 48 | 0.268 | 0.071 |
| TLT | 354 | 23 | 12 | 0.220 | 0.090 |
| USO | 227 | 15 | 3 | 0.149 | 0.082 |
| UUP | 294 | 20 | 8 | 0.188 | 0.091 |

Abstentions (every document vetoed by a near-zero field): **0**. These are recorded as abstentions, not as a zero view — the distinction the product turns on.

**A weighting rule only changes the sign of the net view where the documents disagree.** Where they agree, every non-negative scheme gives the same answer. The 77 disagreement days are the real sample size for any estimated rule, and that is a thin base — thinner than the step 3 cells that failed re-testing.

