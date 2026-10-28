# Source expansion — `97d9bf07dd2c_n5793` against baseline `48a6c4e879a1_n2617_h2` (section 8 rule) — 2026-10-28 15:45

Primary horizon 2, close-to-close. Calls: 1,064 → 1,646; document days 1,532 → 2,486; days with at least one call 602 (39%) → 860 (35%).

Hit-rate on all own calls: 55.2% → 55.3% (naive, overlapping; the registered cell is the backfill's own scoreboard).

**Excluded from the registered comparison:** 163 session(s) listed in `processed/newdoc_dates_earnings_8k_2026-10-28.txt` — days carrying a document outside the registered expansion. Of the 588 days both sides called, 16 fall on those days and are set aside.

On the 572 days both sides called (excluded days removed): old 55.4%, new 56.2%, difference +0.7 points, 95% block-bootstrap interval [-0.5, +2.0] (2,000 draws, block 2). Same sign on 100% of the 995 shared asset-day calls.

Calls the new corpus added on days the baseline had none: 441, hit-rate 56.2%; by asset: SPY 127, TLT 90, USO 82, GLD 81, UUP 61.

**Excluded days, reported not judged (unregistered observation):** 163 day(s); calls 31 → 210 (190 added); hit-rate old 54.8%, new 50.5%; same sign on 100% of 20 shared asset-days.

Session coverage (sessions since 2011 carrying a read document): before 38.1% (1,515 of 3,978); after 61.0% (2,427 of 3,978).

Gate (C2) as passed in: **PASS**.  Hit clause (point ≥ −2, lower bound > −5): met.  Coverage clause (≥ 50%): met.

**Verdict: PASS — C1 coverage, C2 gate and C3 hit-rate all met.**
