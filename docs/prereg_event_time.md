# Pre-registration — T14 phase A: does the initial FOMC reaction extend or reverse? (TRACK §3.11)

*Registered 2026-09-29, before any code. This is the evidence the app's second line ("Rest of
session") must rest on before it may say anything beyond what the statement said.*

## 1. Data

FRBSF *Monetary Policy Surprises*, sheet `FOMC (update 2023)` (vintage frozen in
`data_provenance/mps/`): for each FOMC announcement 1988–Dec 2023, the 30-minute window
response of the S&P 500 futures (`SP500`, 100 × log change) and of the 10-year Treasury yield
(`TNOTE10`, percentage points), with the announcement time. Daily closes: `^GSPC` and `^TNX`
from Yahoo (fetched once, frozen alongside). Sample rules, fixed: scheduled announcements only
(`Unscheduled = 0`); 17 Sep 2001 excluded (as the authors do); announcements after 3:30 pm ET
excluded (no rest of session).

## 2. Variables

For announcement day t:

| | S&P 500 | 10-year yield |
|---|---|---|
| initial reaction `r0` | `SP500/100` | `TNOTE10` (pp) |
| day move | `log(C_t / C_{t−1})` | `y_t − y_{t−1}` |
| **rest-of-session proxy** (primary) | day move − `r0` | day move − `r0` |
| next-session (secondary, clean) | `log(C_{t+1} / C_t)` | `y_{t+1} − y_t` |

The rest-of-session proxy contains the pre-announcement move (open to the window start),
which is unobserved here. It is stated as a limitation, not corrected; the next-session
window has no such contamination and is reported beside it.

## 3. Test

Per asset and per window: OLS `y = a + b·r0 + e`. Inference by permutation of `r0` across
announcements, 10,000 draws, two-sided. Announcements are weeks apart; no block structure.

**Criterion, fixed.** On the primary (rest-of-session) window:

- `b > 0`, p < 0.05 → **EXTENDS** (the initial move continues to the close);
- `b < 0`, p < 0.05 → **REVERSES**;
- otherwise → **NULL**.

`b` is reported as the fraction of the initial move continued or given back by the close.
Sub-samples reported, not tested: 2013+ (2:00 pm announcements with press conferences) and
2006+ (the span where regime labels exist). A 2 × 2 of mean rest-of-session by sign of `r0`
is reported descriptively.

**Priors, stated.** S&P 500: NULL (post-announcement equity drift is weak in the literature).
10-year: EXTENDS with `b` small and positive (the documented post-FOMC bond drift accrues over
weeks; three hours may show only its start).

## 4. What each verdict permits on the app's second line

The "Rest of session" line on a market card, on scheduled-event days only:

| verdict for that market | what the line may say |
|---|---|
| any | *what the statement said* — the reader's stance and implied direction — always, from the moment of the read |
| EXTENDS or REVERSES | *"past meetings like this one [extended / gave back] the initial move by ≈ b·r0 by the close"*, **only when** a same-regime precedent pool reaches ESS ≥ 8 (phase A2, 2006+), with n and ESS shown |
| NULL | *"no measurable rest-of-session pattern"* — and no number |
| market not in the file (gold, oil, dollar) | *"no intraday precedents yet — collecting"* until S5's pool passes its own registered floor |

On days without a scheduled event the line reads "— no scheduled event today." Never a number.
The line's own referee: an event-time ledger scored at the close and next open, same scorer,
"too few to report" below 30 rows.

## 5. Not decided here

Whether any of this should change position sizing (that is T1), and anything about the press
conference (phase E). Nothing frozen changes.

## 6. Amendments

| date | change | reason |
|---|---|---|
| — | — | — |
| 2026-09-29 | Run. **NULL** on both markets (S&P b −0.22 p 0.10; 10-year b +0.09 p 0.28). 10-year prior wrong (#35). Proxy contamination by the pre-announcement drift acknowledged as the power limit; clean test deferred to S5's intraday pool. CURRENT_STATE §18.12 | Result, no criterion changed |
