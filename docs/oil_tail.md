# T13 A3d — the tail after an oil shock

*2026-10-16. Pool p8 (oil +8% in 5 sessions, 116 shocks since 1995; ETF rows from launch). Tail = worst 10% of paths by worst interim loss over 60 sessions for a long position. Classifier: nearest-neighbour tail share on the shock's features (dollar 5s, DGS2 5s bp, oil 5s, oil vs its trailing-year median, S&P drawdown from its 1-year high) with half weight on a regime mismatch, walk-forward from the 30th shock; PASS = at the threshold flagging ≤ 25% of shocks it finds ≥ 50% of tail cases. The severe-case line is shown on the app whatever the verdict, as history.*

Today's features: dollar 5s +0.13%, DGS2 5s +4 bp, oil 5s +0.0%, oil vs year +14.3%, S&P from 1-year high -1.2%, regime 3.

## SPY — tail = worst 12 of 116 shocks (threshold -13.8%)

**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median -19.7% (range -47.5% to -13.8%), reaching the low around session 43; the single worst was 2008-09-22: -47.5% at session 43. Still down -12.1% at 60 sessions, -3.4% at 90.

**What those shocks looked like (medians):** dollar 5s -1.79%, DGS2 5s +1 bp, oil 5s +9.8%, oil vs year -0.9%, S&P from 1-year high -22.9%, regime -1. Dates: 1998-06-22, 2001-01-05, 2001-02-07, 2001-07-06, 2002-04-19, 2002-08-15, 2003-01-15, 2008-09-22, 2008-11-04, 2008-12-11, 2009-01-21, 2022-04-14.

**Did the features predict the tail?** UNTESTED (1 tail cases in the scored window).

**Today's resemblance to those shocks:** low (nearest-neighbour tail share 2% vs base rate 10%) — measured, not a forecast.

## TLT — tail = worst 9 of 82 shocks (threshold -11.6%)

**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median -13.3% (range -21.4% to -11.7%), reaching the low around session 53; the single worst was 2022-03-01: -21.4% at session 47. Still down -11.4% at 60 sessions, -9.3% at 90.

**What those shocks looked like (medians):** dollar 5s -0.74%, DGS2 5s -3 bp, oil 5s +8.6%, oil vs year +12.2%, S&P from 1-year high -5.5%, regime 0. Dates: 2009-03-23, 2010-09-30, 2015-03-24, 2016-10-04, 2021-01-11, 2022-01-18, 2022-03-01, 2022-07-19, 2022-10-03.

**Did the features predict the tail?** UNTESTED (8 tail cases in the scored window).

**Today's resemblance to those shocks:** moderate (nearest-neighbour tail share 12% vs base rate 11%) — measured, not a forecast.

## GLD — tail = worst 8 of 74 shocks (threshold -12.5%)

**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median -14.7% (range -24.2% to -12.8%), reaching the low around session 44; the single worst was 2008-09-22: -24.2% at session 37. Still down -10.6% at 60 sessions, -8.4% at 90.

**What those shocks looked like (medians):** dollar 5s +0.26%, DGS2 5s +3 bp, oil 5s +10.7%, oil vs year +27.9%, S&P from 1-year high -7.1%, regime 1. Dates: 2006-05-02, 2008-06-06, 2008-09-22, 2009-02-20, 2022-04-14, 2026-03-03, 2026-04-01, 2026-05-04.

**Did the features predict the tail?** UNTESTED (4 tail cases in the scored window).

**Today's resemblance to those shocks:** low (nearest-neighbour tail share 9% vs base rate 11%) — measured, not a forecast.

## UUP — tail = worst 7 of 65 shocks (threshold -6.5%)

**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median -6.7% (range -7.8% to -6.5%), reaching the low around session 49; the single worst was 2008-11-04: -7.8% at session 30. Still down -4.4% at 60 sessions, -6.1% at 90.

**What those shocks looked like (medians):** dollar 5s -1.07%, DGS2 5s -6 bp, oil 5s +10.0%, oil vs year -18.3%, S&P from 1-year high -25.3%, regime 0. Dates: 2008-02-14, 2008-11-04, 2009-03-23, 2009-05-04, 2010-05-27, 2020-05-04, 2022-10-03.

**Did the features predict the tail?** UNTESTED (2 tail cases in the scored window).

**Today's resemblance to those shocks:** low (nearest-neighbour tail share 4% vs base rate 11%) — measured, not a forecast.

## USO — tail = worst 7 of 68 shocks (threshold -31.8%)

**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median -52.5% (range -93.9% to -34.7%), reaching the low around session 45; the single worst was 2008-09-22: -93.9% at session 53. Still down -38.5% at 60 sessions, -32.6% at 90.

**What those shocks looked like (medians):** dollar 5s -1.26%, DGS2 5s +1 bp, oil 5s +10.0%, oil vs year -24.7%, S&P from 1-year high -23.4%, regime 0. Dates: 2008-09-22, 2008-11-04, 2008-12-11, 2015-10-08, 2015-12-29, 2020-04-02, 2026-05-04.

**Did the features predict the tail?** UNTESTED (2 tail cases in the scored window).

**Today's resemblance to those shocks:** low (nearest-neighbour tail share 4% vs base rate 10%) — measured, not a forecast.

## WTI_SPOT — tail = worst 11 of 108 shocks (threshold -31.6%)

**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median -37.1% (range -109.5% to -31.9%), reaching the low around session 42; the single worst was 2008-09-22: -109.5% at session 53. Still down -25.2% at 60 sessions, -12.5% at 90.

**What those shocks looked like (medians):** dollar 5s -0.79%, DGS2 5s +1 bp, oil 5s +10.3%, oil vs year -6.3%, S&P from 1-year high -7.0%, regime 0. Dates: 1998-03-23, 2000-03-07, 2008-09-22, 2008-11-04, 2008-12-11, 2015-10-08, 2015-12-29, 2020-04-02, 2022-07-19, 2026-04-01, 2026-05-04.

**Did the features predict the tail?** UNTESTED (6 tail cases in the scored window).

**Today's resemblance to those shocks:** low (nearest-neighbour tail share 7% vs base rate 10%) — measured, not a forecast.

What this does not say: that the next tail will look like the past ones, or that a low resemblance means safety. The verdict column is the only tested statement; everything else is the record of what happened.
