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
