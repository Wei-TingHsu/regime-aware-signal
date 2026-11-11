# Pre-registration — the horizon audit (TRACK §3.51)

*Registered 2026-11-11, before any run. Origin: the founder's two standing rules of 11 Nov — **short windows first** ("news comes out every day; the
longer the span, the more unrelated news is mixed in") and **two ways to use a finding** (QUANT = still there after the information is known, held one
session to several weeks; SUBJECTIVE = on the same day only, usable intraday) — and his instruction that every earlier test be revised under them.*

## 1. What is audited

Every row of `docs/TEST_BOOK.md` Part B marked "day 0 checked? no". The events are rebuilt exactly as the original test built them.

| audit | original test(s) | events | event kind | assets |
|---|---|---|---|---|
| `selloff` | D1, T-L5b | first session the S&P's 10- or 20-session return crosses −4 / −6 / −8% | price move | gold; the S&P itself (days after only) |
| `sudden` | D1b | S&P falls ≥ 1.5 / 2 / 3 / 4% in one session | price move | gold; the S&P itself (days after only) |
| `oil` | A3a, D5 | oil-shock dates in `processed/oil_shocks.csv`, all and by size | price move | gold |
| `fomc` | row 14, T9b | Fed statement days, signed by the rate surprise; all and larger-than-median surprises | information | gold, long Treasuries |
| `calls` | rows 24/27/33, A, D7 | every report call (pooled, by asset, by tier), signed by the call | information | the called asset |
| `htables` | H1, H3, H4, H5 | the history tables' own event lists | price move (H1: information) | S&P, Treasuries, gold, dollar, oil |
| `states` | F1, Y3 | each fast state (3–8 states) and each common day-type | price move | S&P, gold, Treasuries (days after only) |
| `liquidity` | D2c | daily reverse-repo balance change beyond 0.5 / 1 / 1.5 sd | information | gold |
| `resid` | T-H | unexplained move over 1 / 5 / 20 sessions beyond 1.5 sd, five assets | price move | the asset itself (days after only) |

## 2. Measurement

For each event set and asset, the return signed in the direction the original claim predicts, on: **day −1** (the day before — a check), **day 0**
(the event day), **day +1**, **days +1…+2**, **days +1…+3**, **days +1…+5**. Mean in basis points, t-statistic, hit share, n (cells under 30 events
are not measured). Where the event is defined by the asset's own move that day, day 0 and day −1 are not measured for that asset.

Null: the asset's return series shifted in time by a random offset, 1,000 draws; event dates fixed. Three family p-values per audit — the best cell
of the group against the best cell on shifted data: **p_day0**, **p_after** (all cells on days +1 onward), **p_before**. The best day-0 and best
after cell are also shown by era.

Limit stated: for events defined over several sessions (`selloff`, `oil`, H3, H4) day −1 lies inside the event's own window, so it is not a clean
check there; it is a clean check for one-day and information events (`sudden`, `fomc`, `calls`, `liquidity`).

## 3. Label rule (fixed before running)

- p_after < 0.05 → **QUANT candidate** (then: its own registered rule with entry, exit and costs, and a forward log).
- else p_day0 < 0.05 and the event is **information** → **SUBJECTIVE grade B candidate** (then: the intraday test).
- else p_day0 < 0.05 and the event is itself a **price move** → **CONTEXT (same-day co-movement)** — two prices moving together on a day is a hedge
  ratio, not a signal; nothing was known beforehand.
- else **NEITHER**.

## 4. Priors (Claude, before any run; counted if wrong)

- **#132** no audit reaches p_after < 0.05: nothing is left on days +1…+5 in any of the nine.
- **#133** information events on day 0: `calls` p_day0 < 0.05 (the documents' direction goes with the same-day move) and `fomc` p_day0 < 0.05
  (known); `liquidity` p_day0 ≥ 0.05.
- **#134** price-move events on day 0: at least four of `selloff`, `sudden`, `oil`, `htables` show p_day0 < 0.05 — plain same-day co-movement.
- **#135** the clean day −1 checks (`sudden`, `fomc`, `calls`, `liquidity`): at most one shows p_before < 0.05.

## 5. Results

| date | audit | day 0 | days after | day −1 | label | prior |
|---|---|---|---|---|---|---|
| 2026-11-11 | `fomc` — information | all statement days → gold, day 0: +76 bp, t +7.6, n 114, hit 80%; family p 0.000 | larger-than-median rate surprise → gold, day +1: +38 bp, t +1.9, n 66, hit 53%; family p 0.403 | larger-than-median rate surprise → gold, day -1: +19 bp, t +1.9, n 66, hit 53%; family p 0.187 | **SUBJECTIVE grade B candidate**. Confirms T9b on the audit's own measure: on statement days gold moves 76 bp in the direction the rate surprise predicts, 80% of the time, in every era; nothing reliable is left on the days after (large surprises: +38 bp on day +1, p 0.40). SUBJECTIVE grade B; not QUANT. | |
| 2026-11-11 | `calls` — information | calls on SPY, day 0: +6 bp, t +2.1, n 722, hit 53%; family p 0.245 | all calls, pooled, days +1..+3: +16 bp, t +3.6, n 1646, hit 57%; family p 0.034 | tier 2.0, day -1: -25 bp, t -3.3, n 223, hit 42%; family p 0.007 | **QUANT candidate**. Label by the registered rule. Read with care: the calls are mostly 'up' calls on assets that drift up; the shift null keeps that drift and the result clears it narrowly (p 0.034, best of 3 span cells × variants). The same calls at 2 sessions did not beat drift in the scoreboard (p 0.40) and earned a Sharpe of 0.07 after costs. Day 0 itself shows nothing (p 0.245): the documents' direction does NOT go with the same-day move. The day −1 check fails for tier 2 (−25 bp, p 0.007): those calls point against the previous day's move, so part of what the call 'predicts' may be a bounce from the day before. Next: a registered, costed rule at 1 / 2 / 3 sessions with the previous day's move controlled. | |
| 2026-11-11 | `liquidity` — information | reverse-repo balance change beyond 1.5 sd → gold, day 0: +10 bp, t +1.6, n 273, hit 52%; family p 0.231 | reverse-repo balance change beyond 1.5 sd → gold, day +1: +7 bp, t +1.1, n 273, hit 51%; family p 0.838 | reverse-repo balance change beyond 0.5 sd → gold, day -1: +4 bp, t +1.2, n 1100, hit 53%; family p 0.446 | **NEITHER**. Nothing on the day, before or after. | |
| 2026-11-11 | `selloff` — price move | S&P 20-session return crosses -4% → gold, day 0: -27 bp, t -1.2, n 50, hit 50%; family p 0.704 | S&P 10-session return crosses -4% → S&P itself, days +1..+5: +128 bp, t +3.1, n 67, hit 67%; family p 0.160 | S&P 20-session return crosses -6% → gold, day -1: +30 bp, t +1.5, n 34, hit 53%; family p 0.490 | **NEITHER**. Gold shows no reliable move on the day a drawdown completes or after. The S&P itself gains 128 bp over the five sessions after a −4% ten-session fall (t 3.1) but that does not clear the family null (p 0.16) and reverses sign in 2022–26. | |
| 2026-11-11 | `sudden` — price move | S&P falls ≥ 4.0% in one session → gold, day 0: +51 bp, t +1.2, n 43, hit 60%; family p 0.613 | S&P falls ≥ 1.5% in one session → S&P itself, days +1..+3: +35 bp, t +1.9, n 362, hit 59%; family p 0.876 | S&P falls ≥ 2.0% in one session → gold, day -1: +25 bp, t +2.5, n 214, hit 56%; family p 0.062 | **NEITHER**. On days the S&P falls ≥ 4% gold is up 51 bp on average but not reliably (t 1.2): gold is not a dependable same-day hedge on crash days. Nothing after. | |
| 2026-11-11 | `oil` — price move | all oil shocks → gold, day 0: +31 bp, t +3.1, n 202, hit 60%; family p 0.009 | all oil shocks → gold, days +1..+5: +23 bp, t +1.3, n 202, hit 55%; family p 0.808 | oil +5–8% in five sessions → gold, day -1: +22 bp, t +2.6, n 120, hit 53%; family p 0.041 | **CONTEXT (same-day co-movement)**. Gold rises about 31 bp on the day an oil shock completes — two prices moving together (stronger before 2015); nothing after. CONTEXT. | |
| 2026-11-11 | `htables` — price move | H1 → UUP, day 0: -42 bp, t -8.7, n 115, hit 17%; family p 0.000 | H4dn → USO, day +1: -141 bp, t -3.1, n 30, hit 27%; family p 0.122 | H4up → TLT, day -1: -46 bp, t -2.8, n 37, hit 27%; family p 0.087 | **CONTEXT (same-day co-movement)**. The day-0 passes are market mechanics (on Fed decision days the dollar moves with the 2-year yield, −42 bp on the signed measure, t −8.7). Nothing reliable after (best: oil −141 bp the day after a 2-year yield drop, n 30, family p 0.12). CONTEXT. | |
| 2026-11-11 | `states` — price move | not measured | fast state k3:1 → SPY, days +1..+5: +31 bp, t +7.9, n 2411, hit 63%; family p 0.002 | not measured | **QUANT candidate**. Label by the registered rule. Read with care: the state covers about half of all days (n 2,411) and the S&P's ordinary five-session gain is roughly +20 bp; the excess is about +10 bp per five sessions before costs. The state flips almost daily (median run 1 session), so trading it means paying costs constantly; the costed version of this test at five sessions (F1, net Sharpe) found no survivor at three states (p 0.36). What the audit adds: calm-type days are followed by slightly better S&P returns than other days, in every era — a sizing tilt at most. Next: a registered, costed rule at 1 / 2 / 3 sessions. | |
| 2026-11-11 | `resid` — price move | not measured | SPY: unexplained move over 20 session(s) beyond 1.5 sd, days +1..+5: -55 bp, t -4.4, n 731, hit 45%; family p 0.106 | not measured | **NEITHER**. After a large unexplained 20-session move the S&P gives back about 55 bp over the next five sessions, with the same sign in every era (t −4.4), but the family null is not cleared (p 0.106). Closest miss of the audit; NEITHER as registered. | |
| 2026-11-11 | priors | | | | | **#132 wrong (counted)** (two audits clear p_after < 0.05); **#133 wrong (counted)** (the calls show no day-0 link); **#134 wrong (counted)** (gold does not co-move on S&P sell-off days; only oil and the history tables pass); **#135 right** |
