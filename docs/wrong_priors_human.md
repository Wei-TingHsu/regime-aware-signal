# Wrong priors #29–#37 — what each one means for a trader

*Appended to CURRENT_STATE as §18.15 on 8 Oct 2026. The tally alone tells a future reader
nothing; each entry carries the belief, what killed it, the rule it leaves the engine, and what
it means if you are the one holding the position. Plumbing entries (#29, 30, 31, 36) and
structure entries (#32–35, 37) are marked, because they constrain future work differently.*

| # | kind | the belief, held in writing | what overturned it | the rule the engine keeps | what it means if you are trading |
|---|---|---|---|---|---|
| 29 | plumbing | nightly reads were creeping up (7 Sep) | the counter reported the cache, not activity; no read had run since 29 Aug | a count is not a heartbeat — monitor what should change tonight | an equity curve that is flat for two weeks is not "stable," it is a dead feed |
| 30 | plumbing | the nightly job can see the Anthropic key | `set ANTHROPIC_API_KEY` in every log; the key lived in `.zshrc`, which launchd never reads | test a job from the job's own environment, never from an interactive shell | a strategy that works when you click and fails at 3 am has a 3 am problem — and 3 am is when the Fed speaks for you |
| 31 | plumbing | every source the reader loops over has a fetcher | nothing wrote to `fomc_statement/`; the files were a one-off August pull | a folder with files in it is not a pipeline; each source names its fetcher or is marked manual | data that arrived once is not a feed — half of arbitrage failures are a feed that silently stopped |
| 32 | structure | instrument flips concentrate on FOMC days (futures settle 1:30 pm, statement at 2 pm) | flips 5.8% on FOMC days vs 5.0% elsewhere | the ETF/futures settlement gap is a daily effect, not an announcement effect; the instrument choice cannot be blamed for any event-day result | for a daily strategy, ETF vs futures does not change the signal; for an intraday one, it is everything — never mix the two inside one strategy |
| 33 | structure | the 2-year yield's same-day change passes trivially as a surprise measure on TLT | coefficient ≈ 0, p 0.90 | a measure that contains the reaction predicts nothing for the asset that reacted | you cannot trade a surprise you measure after the market has absorbed it; the edge, if any, is in the first half-hour — fed funds and SOFR futures at 2:00–2:30 pm, not the close |
| 34 | structure | gold's surprise effect holds under the Fed's published 30-minute measure | p 0.49; the level-1 "effect" was the whole-day proxy continuing | only a pre-reaction measure counts as a surprise | what level 1 actually found is a few-day *continuation* after a big Fed-day move — momentum, tradeable without knowing why; registered honestly as S1/S2, not dressed up as a surprise |
| 35 | structure | the 10-year's initial FOMC reaction extends to the close (the bond-drift literature) | NULL on 292 meetings | with free daily data, rest-of-session cannot be separated from the pre-announcement drift; intraday claims need intraday bars (S5) | no free lunch chasing or fading the first 30 minutes on daily data; the documented bond drift accrues over weeks — a carry position, not a day trade |
| 36 | plumbing | the 24 Sep key fix left the job self-sufficient | 14 failed nights; `>>` onto a file with no trailing newline glued two keys into one | never append to a secrets file — write it whole; check the job's exit status weekly | operational risk is risk: fourteen nights of no data is fourteen nights a live book flies blind |
| 37 | structure | SPY passes volatility targeting (T1 prior) | gain lived in 2008–2016 and reversed after 2017; stability −0.46 | a benefit confined to one era is not a benefit — the chronological split doing its job | vol targeting on equities is a drawdown hedge you pay for in bull markets: it sells into dips; size it to the loss you cannot survive, never run it as alpha |

**The four sentences every future test is judged against** (from the structure entries):
information in a filed document is absorbed within the session; a surprise must be measured
before the reaction; the regime labels carry no information beyond volatility (three
independent tests: ranking, direction, sizing); a result that lives in one era is not a result.
