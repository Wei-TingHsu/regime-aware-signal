# Source expansion — `97d9bf07dd2c_n5793` against baseline `48a6c4e879a1_n2617_h2` (section 8 rule) — 2026-10-28 04:11

Primary horizon 2, close-to-close. Calls: 1,064 → 1,646; document days 1,532 → 2,486; days with at least one call 602 (39%) → 860 (35%).

Hit-rate on all own calls: 55.2% → 55.3% (naive, overlapping; the registered cell is the backfill's own scoreboard).

On the 588 days both sides called: old 55.4%, new 55.8%, difference +0.3 points, 95% block-bootstrap interval [-1.0, +1.6] (2,000 draws, block 2). Same sign on 100% of the 1,015 shared asset-day calls.

Session coverage (sessions since 2011 carrying a read document): before 38.1% (1,515 of 3,978); after 61.0% (2,427 of 3,978).

**Verdict: PASS — coverage up, hit-rate within tolerance.** Hit clause (point ≥ −2, lower bound > −5): met; coverage clause (≥ 50%): met.
