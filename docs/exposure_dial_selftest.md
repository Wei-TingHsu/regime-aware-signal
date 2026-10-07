# Exposure dial — acceptance tests

*Run 2026-10-07 23:40 on synthetic data only. Registered in `docs/prereg_exposure_dial.md` §7.*

Two tests were re-specified after failing on their first run (7 Oct): test 1 (vol equal to the target → half the target; original 11% at cap) and test 2 (fixed 500-session regime blocks → irregular geometric lengths; original shift-null p 0.255). The dial was not changed; the tests were wrong. Declared implementation detail: regime multipliers are refreshed every 21 sessions from data through the previous session (the registration fixes 'expanding through t−1' and no cadence).

| test | result | note |
|---|---|---|
| constant-vol series (re-specified) | PASS | dial at 100% on 100% of sessions; gross CER identical across variants 1-2: True |
| planted regime vol (re-specified) | PASS | tilt lowers exposure in the planted regime; CER gain +0.0147, shift-null p 0.010 |
| shifted labels | PASS | with scrambled labels CER gain -0.0070, p 0.820 |
| no look-ahead | PASS | sigma_hat and the tilted weight at t unchanged when data after t is deleted |
| cost accounting | PASS | two-trade path reproduced to the basis point (lag 0) |
| hysteresis | PASS | a label that flips every session never confirms |

**All pass: yes**
