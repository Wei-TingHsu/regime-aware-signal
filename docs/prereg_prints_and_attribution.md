# Pre-registration — T16: scheduled data prints as a source, and the attribution engine

*Registered 2026-10-08, before any code. Two things in one registration because neither is
testable without the other: (A) the scheduled releases that drive most of Treasuries' and the
dollar's big days enter the engine as a structured source, read against what was expected and
against what the release itself says caused the number; (B) an attribution engine apportions
each day's move among the events that landed, so "the document read the wrong way" can be told
apart from "the document was not the driver" — the misattribution the 8 Oct coverage table
could not separate.*

## Part A — the structured-event source class `data_print`

### A1. Sources and fetch routes

| release | agency | time ET | route | archive | first-print numbers |
|---|---|---|---|---|---|
| Employment Situation (payrolls, unemployment, earnings) | BLS | first Friday 08:30 | news-release archive page | 2006→ | ALFRED `PAYEMS`, `UNRATE`, `CES0500000003` |
| CPI | BLS | mid-month 08:30 | same | 2006→ | ALFRED `CPIAUCSL`, `CPILFESL` |
| PPI | BLS | mid-month 08:30 | same | 2006→ | ALFRED `PPIFIS` |
| Weekly initial claims | DOL | Thursday 08:30 | DOL newsroom PDF / text | 2006→ (archive) | ALFRED `ICSA` (vintages from 2009; Thursday rule before) |
| GDP (advance, second, third) | BEA | 08:30 | BEA release archive | 2006→ | ALFRED `GDP` |
| PCE price index | BEA | 08:30 | same | 2006→ | ALFRED `PCEPI`, `PCEPILFE` |
| Retail sales | Census | 08:30 | Census archive | 2006→ | ALFRED `RSAFS` |
| EIA Weekly Petroleum Status | EIA | Wednesday 10:30 | EIA archive + API | 2006→ | EIA API (crude stocks change) |
| Treasury auctions (2y/5y/10y/30y) | Treasury | 13:00 | TreasuryDirect auction query API | 2006→ | tail vs when-issued, bid-to-cover |

All US government works; no copyright constraint. Fetch cost $0. ISM PMI is excluded (copyrighted release); its headline enters later only via a licensed route or not at all.

### A2. What each print carries into the engine — three layers

**Layer 1, structured (from ALFRED/EIA/Treasury, $0, no LLM):** release timestamp; headline
value as first published; the previous first-print value; the revision to the previous month
(first print of last month vs its value in this release).

**Layer 2, expectation.** The surprise is `actual − expected`. Expectation sources, in a fixed
order of preference, with the one used recorded on every row:

1. **market-implied, pre-release** — the move in the 2-year yield (and, forward from S5, the
   fed funds / SOFR futures) over the 60 minutes *before* 08:30 is not the expectation; the
   expectation is what was *priced*, and the cleanest free measure of the surprise is the move
   in the 5 minutes *after* 08:30 (the Fed-series method, applied to prints). Forward only (S5
   bars), so it is the measure the live engine uses from the next release on;
2. **published consensus** — paid (Bloomberg/Refinitiv); not purchased now; the slot exists;
3. **naive expectation** — the previous first-print value (random-walk); free; used for the
   whole 2006–2026 backfill, and labelled as such on every row.

A surprise computed under (3) is a different, weaker quantity than under (1) or (2); results
are reported by expectation source and never pooled across them.

**Layer 3, the reader (the LLM), on the release text only — the part a number cannot give.**
The release itself usually names what composed the number. The reader is asked, under a fixed
schema, for:

| field | what it holds | example from a real release |
|---|---|---|
| `headline` | the number and the series, as the text states them | "nonfarm payroll employment rose by 254,000" |
| `special_factors[]` | each factor the release names as distorting the number, with sign and size where stated | "the strike at Boeing reduced manufacturing employment by 33,000"; "temporary hiring for the World Cup added an estimated 20,000"; "the government shutdown"; "weather" |
| `transitory_share` | the reader's estimate of how much of the surprise the named factors explain, 0–1 | 0.6 |
| `underlying_direction` | the direction of the number with the named factors removed, on the five axes, −1…+1 | equity −0.2, duration +0.3 … |
| `revision_note` | whether the previous month was revised and which way | "July and August revised down by a combined 86,000" |
| `specificity`, `confidence` | as in the existing schema | — |

The reader is given the previous release's read (as it is for novelty) so "temporary workers
added last month are leaving this month" is readable. It is **not** given the price reaction.
The reader does not estimate the expectation; that is layer 2's job.

**The net reading of a print** that reaches the estimator is: surprise sign and size from
layer 2, scaled down by `(1 − transitory_share)` from layer 3 — a surprise the release itself
explains as temporary counts for less. That rule is fixed here and not tuned.

### A3. Read cost, stated up front

From a 20-release token sample before any paid read (TRACK §3.11 step 7 rule). Expected:
~2,500 releases over 2006–2026 at ~2,500 tokens each ≈ 6M input tokens — the order of US$20
at current rates, under the founder's current balance. Reads use the existing prompt version
with a new `PROFILES["data_print"]` entry, reviewed by the founder line by line before the
first paid read; mixed corpora are not pooled.

### A4. Acceptance before real data

| test | what it checks |
|---|---|
| planted surprise | a synthetic release with actual = expected + k produces a net reading of sign k and size ∝ k |
| transitory discount | the same release with `transitory_share` 1.0 produces net 0 |
| revision isolation | a revision to last month with no surprise this month produces no direction from the surprise term |
| timestamp | every print carries 08:30 (or its own time) and lands in the *overnight* bin of Part B's two-bin attribution, never the intraday bin |
| reader consistency | on 20 real releases the reader's `headline` number equals ALFRED's first print within rounding, 19 of 20 or better |

### A5. Criterion for the source (the registered source-expansion rule, prereg_report_scoreboard §8)

The corpus hash changes; the backfill re-runs; the pooled 3-session hit-rate on shared days must
not fall by more than 2 points and the lower bound must exceed −5. **And a second, source-specific
criterion:** on the print days themselves, the engine's covered share (state C + state D below)
must rise from its current level by at least 30 percentage points on TLT and UUP. Prior: it
will — these days are blind now because nothing is fetched, not because the reading fails.

## Part B — the attribution engine

### B1. The question

On a day with a big move and several documents, which document (if any) moved the market? The
engine's original design weighted documents by their own fields (magnitude × specificity ×
novelty × confidence). That weights *what the document says*; it does not measure *what the
market did when it landed*. Attribution adds the second.

### B2. Historical attribution (2006–2026): two bins from daily open and close

Every event class has a fixed timestamp; daily data gives two windows:

| bin | window | events it contains |
|---|---|---|
| **overnight** | previous close → open (the gap) | all 08:30 prints; pre-market 8-Ks; executive orders signed after the prior close; foreign events |
| **intraday** | open → close | FOMC statement 14:00 and press conference 14:30; 8-Ks filed during the session; EIA 10:30; Treasury auctions 13:00; intraday news |

An event is *attributed* the bin it falls in. On a day with one event per bin, attribution is
exact at the bin level. On a day with two events in one bin (an 8-K at 07:00 and NFP at 08:30),
the bin's move is split by the fixed rule: scheduled macro release first (it is the known
driver), the rest to the others in proportion to their `magnitude × specificity` — recorded as
"shared bin", never as a clean attribution.

**The refined coverage states**, replacing the three of prereg_blindspot §1:

| state | condition |
|---|---|
| A blind | big move, no document on that axis in either bin |
| **B misread** | big move, a document in the *same bin* as the move, reading against it |
| **D not-the-driver** | big move, the only document on that axis is in the *other* bin, reading against it |
| C seen | big move, a document in the same bin, reading with it |

The "31% wrong" of 8 Oct was B + D together. The two are reported separately from the first
run of this engine onward, and the sentence that describes them changes accordingly (TRACK §7
figure rule).

### B3. Forward attribution: minute bins from S5

From 29 Sep 2026 the 1-minute bars give the move in `[t − 5 min, t + 30 min]` around every
event's timestamp — the Fed-series window, applied to every event class. That is the clean
attribution; the two-bin history is its coarse backfill, and the two are reported as different
instruments.

### B4. The influence weights — what the engine ranks

Per source class *s* and regime *r*, over all events of that class with a known bin:

- **hit share** `h(s,r)` — share of events whose bin move has the sign of the document's
  reading, with a within-asset permutation null (events' readings shuffled across the class's
  own event dates, 10,000 draws);
- **influence** `β(s,r)` — the slope of the bin move on the document's signed net reading,
  block-bootstrapped;
- a class earns an influence weight > 0 for a regime only when `h` beats its null at p < 0.05
  on **≥ 30 events**; otherwise its weight is 0 and the class is marked "no measured
  influence in this regime".

These weights are a **second, parallel weighting scheme** beside the registered §7.2 rule.
They do not replace it: the report continues to run on §7.2; the attribution weights are
displayed ("on days like this, in this regime, a Fed statement has moved Treasuries with its
reading 71% of the time (n=84); an executive order has not (n=52, 49%)") and are promoted to
the estimator only through a registered comparison on the backfill under the source-expansion
rule — never by being better-looking.

### B5. Priors, stated

- Prints will dominate the overnight bin on TLT and UUP big days; state A on those markets
  falls by more than half once prints are a source.
- The split of the current "wrong" into B and D: D (not-the-driver) will be the larger share
  on SPY and GLD; B (misread) will be concentrated on FOMC days, where the reading-vs-surprise
  problem (#33–34) lives.
- Influence: FOMC statements earn a weight on TLT and UUP in every regime; earnings 8-Ks earn
  one on SPY only in the low-volatility regimes; executive orders earn none anywhere on the
  current corpus (they are telegraphed; the surprise is small by construction).

## C. What the app may show

- On a print day: the print's headline, the expectation used and its source, the surprise, the
  special factors the release names, and the discounted net reading — on the cards of the
  markets it touches, in the "What landed today" section, visually distinct from the text
  documents.
- The coverage line (prereg_blindspot §5) says *misread* or *not the driver*, never "wrong".
- The influence table under "How this works", per source class × regime, with n and the null,
  labelled "measured on history; not used in the 3-day line".

## D. Amendments

| date | change | reason |
|---|---|---|
| — | — | — |
