# A3b inverse — the coin-flip check

*2026-10-16. Same walk-forward as A3b; the inverse call is minus the conditional sign. Question: is 'below 50%' a real bias worth trading backwards, or binomial noise? Diagnostic only — the registered form is forward-only (prereg_blindspot 16 Oct).*

| market | n | A3b hit | inverse hit | pool-median hit | binomial p (vs 50%) | Bonferroni ×6 | inverse hit 1st half | 2nd half | reading |
|---|---|---|---|---|---|---|---|---|---|
| SPY | 67 | 42% | 58% | 55% | 0.222 | no | 48% | 68% | one half only — not stable |
| TLT | 67 | 51% | 49% | 49% | 1.000 | no | 64% | 35% | one half only — not stable |
| GLD | 59 | 44% | 56% | 56% | 0.435 | no | 55% | 57% | within noise |
| UUP | 47 | 51% | 49% | 57% | 1.000 | no | 57% | 42% | one half only — not stable |
| USO | 50 | 30% | 70% | 46% | 0.007 | yes | 68% | 72% | edge in both halves and p < 0.05/6 |
| WTI_SPOT | 65 | 45% | 55% | 55% | 0.457 | no | 53% | 58% | one half only — not stable |

How to read it: the inverse hit is 100% minus A3b's hit on the same calls. 'Binomial p' is the chance a fair coin lands this far from 50% on this many trials; six markets were tested, so the bar for any one of them is 0.05 ÷ 6 ≈ 0.008. A real bias shows in both halves of the sample. Anything else is the kind of gap that disappears on the next 60 shocks. Forward scoring of the registered inverse hypothesis starts with the first shock after 16 Oct 2026.
