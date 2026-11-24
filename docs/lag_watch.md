# Lag watch: how late each news route is

83 new items timed over 1 run(s), 120 minutes in total. Lag = the moment this machine first saw the item minus the time the source states (for SEC filings: minus the SEC's own acceptance time). Only items published after a run began are counted. Nothing was scored.

## SEC: the same filings on the two free addresses

| address | filings | fastest | middle | nine in ten within | slowest |
|---|---|---|---|---|---|
| one list for all companies (checked every 5 s) | 16 | 17 s | 36 s | 49 s | 78 s |
| the company's own list (what the listener uses; here checked every 5 s) | 16 | 27 s | 73 s | 86 s | 100 s |

On the same 16 filings the single list was first on 100%; the middle gap is +27 s (positive = the single list is earlier). 0 filings never showed on the company's own list within 10 minutes or were still waiting at the end.

## The feeds the listener reads

| source | new items | fastest | middle | nine in ten within | slowest |
|---|---|---|---|---|---|
| PR Newswire: all releases | 67 | 48 s | 132 s | 188 s | 229 s |

A feed's stated time is often the planned release minute, so a lag of under a minute can be the feed's own rounding.

## Did any source refuse the more frequent checks?

| run | source | checked every | answered | refused (403/429) | other failures | left alone |
|---|---|---|---|---|---|---|
| 2026-11-24T17:35Z | SEC: one list for all companies (8-K) | 5 s | 912 | 0 | 4 | no |
| 2026-11-24T17:35Z | SEC: one list for all companies (6-K) | 5 s | 866 | 0 | 4 | no |
| 2026-11-24T17:35Z | PR Newswire: all releases | 15 s | 408 | 0 | 0 | no |
| 2026-11-24T17:35Z | PR Newswire: earnings | 15 s | 407 | 0 | 0 | no |
| 2026-11-24T17:35Z | NVIDIA newsroom | 15 s | 406 | 0 | 0 | no |
| 2026-11-24T17:35Z | AMD investor page | 15 s | 405 | 0 | 0 | no |
| 2026-11-24T17:35Z | Meta investor page | 15 s | 403 | 0 | 0 | no |
| 2026-11-24T17:35Z | SK Hynix newsroom | 15 s | 402 | 0 | 0 | no |
| 2026-11-24T17:35Z | Hunterbrook | 15 s | 400 | 0 | 0 | no |
| 2026-11-24T17:35Z | SemiAnalysis | 15 s | 2 | 3 | 0 | yes |
| 2026-11-24T17:35Z | TrendForce | 15 s | 396 | 0 | 0 | no |
| 2026-11-24T17:35Z | SEC: a company's own list | 5 s | 64 | 0 | 0 | no |
