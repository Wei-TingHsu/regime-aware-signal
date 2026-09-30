# T14 phase A — does the initial FOMC reaction extend or reverse?

*Run 2026-09-29 17:32. Registered in `docs/prereg_event_time.md`. 292 scheduled announcements 1988-02-11 → 2023-12-13; initial reaction from the FRBSF 30-minute window; 10,000 permutations. The rest-of-session proxy contains the unobserved pre-announcement move.*

## S&P 500

| sample | window | n | b (fraction of initial move) | p | reading |
|---|---|---|---|---|---|
| all | rest of session (primary) | 261 | -0.219 | 0.0992 | NULL |
| all | next session | 261 | -0.079 | 0.6183 | NULL |
| 2006+ (regime span) | rest of session (primary) | 112 | -0.323 | 0.1142 | NULL |
| 2006+ (regime span) | next session | 112 | +0.048 | 0.8391 | NULL |
| 2013+ (2 pm, press conf.) | rest of session (primary) | 56 | +0.170 | 0.4320 | NULL |
| 2013+ (2 pm, press conf.) | next session | 56 | +0.222 | 0.4746 | NULL |

Descriptive: after an initial *up* move, mean rest-of-session +0.143% (n=119); after an initial *down* move, +0.324% (n=140).

## 10-year yield

| sample | window | n | b (fraction of initial move) | p | reading |
|---|---|---|---|---|---|
| all | rest of session (primary) | 292 | +0.087 | 0.2826 | NULL |
| all | next session | 292 | +0.033 | 0.7683 | NULL |
| 2006+ (regime span) | rest of session (primary) | 143 | +0.196 | 0.0764 | NULL |
| 2006+ (regime span) | next session | 143 | -0.005 | 0.9686 | NULL |
| 2013+ (2 pm, press conf.) | rest of session (primary) | 87 | -0.088 | 0.6018 | NULL |
| 2013+ (2 pm, press conf.) | next session | 87 | +0.125 | 0.5688 | NULL |

Descriptive: after an initial *up* move, mean rest-of-session -0.009pp (n=145); after an initial *down* move, -0.003pp (n=136).

## Verdicts (primary window, full sample)

- **S&P 500: NULL** (registered prior: NULL — prior held)
- **10-year yield: NULL** (registered prior: EXTENDS — prior wrong)

Per §4 of the registration, an EXTENDS or REVERSES verdict permits the app's rest-of-session line for that market only with a same-regime precedent pool of ESS ≥ 8 (phase A2); NULL permits no number.
