# Same-day document collisions

*Run 2026-08-27 12:03:48 +0800. No API calls.*

*Registered precondition for step 5: `prereg_analog_event.md` §10 — collisions < 50 means §7.3 is not attempted and step 5 ships on the fixed rule.*

| asset | docs above floor | sessions | collisions | size 2 | size 3 | size 4+ | cross-source | opposite signs |
|---|---|---|---|---|---|---|---|---|
| GLD | 304 | 286 | **17** | 16 | 1 | 0 | 7 | 6 |
| SPY | 985 | 803 | **119** | 92 | 15 | 12 | 74 | 48 |
| TLT | 380 | 354 | **23** | 21 | 1 | 1 | 15 | 12 |
| UUP | 315 | 294 | **20** | 19 | 1 | 0 | 11 | 8 |
| USO | 245 | 227 | **15** | 13 | 1 | 1 | 4 | 3 |

**Total collisions: 194** against a registered threshold of 50.

**Step 5 branch: ESTIMATED weights are admissible (section 7.3 attempted)**

A weighting rule only changes the answer where colliding documents disagree in sign — agreeing documents give the same net direction under any non-negative weights. The opposite-signs column is the real sample size for estimating a rule.

