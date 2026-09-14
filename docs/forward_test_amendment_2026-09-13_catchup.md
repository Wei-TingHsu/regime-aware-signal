# Forward test — amendment: catch-up entry and `logged_at`

**Registered 2026-09-13, before the first run on which it could fire (Mon 2026-09-14
15:00 SGT). Commit `2296725`. No catch-up had fired at the time of writing.**

## What changes

Until 13 Sep, `src.forward_log` entered picks for **one** signal date per run — the
latest completed US close with price coverage — and skipped if that date was already
in the ledger. Any run that did not happen (machine asleep past the launchd slot; a
vendor failure such as the AMLP empty return on 8 Sep; a crash) therefore lost that
session's row permanently.

From this amendment, each run enters picks for **every completed session with price
coverage that is later than the newest signal date already in the ledger and not
already logged**, oldest first. A new column, `logged_at` (UTC), records when each row
was written. Rows written before this amendment carry `logged_at = NaN`.

## What does not change

- The signal rule: signal = last completed US close (closing bell passed, via
  `market_calendar.last_completed_session`); entry = next US session; exit = H
  trading days later. Unchanged.
- `picks_for` is positional: a row entered late is computed only from panel data up
  to its own signal close. The only difference between a late row and an on-time row
  is that a late row's prices may carry any vendor revision (dividend or split
  adjustment) posted between the signal close and the run. This is declared, not
  hidden; `logged_at` makes late rows identifiable.
- The 5-day stale guard. A session more than five days old is still refused, so
  catch-up is bounded to roughly one missed week.
- `models.yaml`. Not touched.

## Why this is registered rather than just committed

A late-entered row is a category that did not exist in the forward test's description.
Its existence, and the fact that it can be told apart from an on-time row, belongs in
the record before any such row exists.

## Companion change, same commit

`src.download_data` no longer aborts on a single ticker's empty return: the ticker's
cached history is kept, the failure is printed, and only a majority failure (network,
not ticker) is fatal. The panel has tolerated missing assets (45/47) since the forward
test began; the harness now matches that.
