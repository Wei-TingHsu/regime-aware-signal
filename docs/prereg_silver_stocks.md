# Pre-registration — T-S1: deliverable silver at the COMEX depositories and silver's price (DRAFT v2, grids)

*Drafted 2026-10-28 from the founder's hypothesis of 28 Oct; v2 the same afternoon under the grid-by-default rule (prereg_subperiod_audit §1):
every fixed number below is a grid axis, the whole surface is published, and the strongest cell is judged against the strongest cell the
same search finds on time-shifted data. It becomes a registration when the founder commits it; the first run needs ≥ 250 sessions of
warehouse data (section 2).*

**The founder's sentence.** The main silver holders (JP Morgan and others) sometimes take silver out of the warehouse, or "lock it up", so
that it can no longer be used to deliver against futures contracts. The correlation of those actions — in amount and in frequency — with
silver's price trend, allowing that the action may lead or lag the price.

## 1. What is observable, and what is not

CME publishes a daily depository report for COMEX silver: for each depository (the vault operator — JPMorgan, Brink's, CNT, Loomis, HSBC,
Manfra Tordella & Brookes, Asahi, Delaware Depository, Malca-Amit and others), the ounces held as **registered** (a warrant has been issued; the
metal can be delivered against a futures contract) and **eligible** (meets the contract's specification, no warrant; cannot be delivered until a
warrant is issued), with the day's receipts, withdrawals and adjustments between the two categories.

- "Lock up" has two observable forms, both in the report: a **warrant cancellation** (registered → eligible: the metal stays but leaves the
  deliverable pool) and a **withdrawal** (the metal leaves the vault).
- **The owner is not observable.** The report names the vault, not whose metal sits in it; a JPMorgan-depository move may be a client's. Every statement
  below is about *depository-level deliverable stock*; "JP Morgan" means the JPMorgan depository. The bank's own book cannot be tested with public data.

## 2. Data (free; forward collection from the first successful probe)

`src/fetch_comex_stocks.py` downloads CME's daily silver (and gold) depository file once a day into `data_provenance/comex_stocks/raw/YYYYMMDD_<metal>.xls`
(write-once by date) and appends parsed rows to `processed/comex_<metal>_stocks.csv`. **28 Oct probe: the host answered HTTP 403 (a JSON denial) to a
plain Python client**; v2 of the fetcher sends full browser headers and falls back to `curl`. If the host still refuses scripted access, the options are
a hand-downloaded history file (accepted under the SPDR rule of 27 Oct, labelled with its source) and a browser-driven daily save; the one third-party
API found (MetalCharts, history to 1992) prices COMEX data at US$99/month and is **ruled out by the free-feed rule**. Floor: ≥ 250 sessions before the
first run. Price: SLV close-to-close (Apr 2006 →), SI=F continuous beside it as the instrument check.

## 3. Variables and the grid

- `R_t` registered oz (total; per depository); `E_t` eligible; `S_t = R_t/(R_t+E_t)` the deliverable share.
- Lock-up flow `L_t = max(0, −ΔR_t)`, split into adjustments and withdrawals where the report allows.

| axis | registered cell | grid |
|---|---|---|
| stock measure | total registered | {total registered, registered share S, per-depository registered (each ≥ 5% of total)} |
| aggregation | weekly (Friday) | {daily, weekly, 2-weekly} |
| lead–lag window | ±12 weeks | {±3, ±6, ±12, ±26} (the cross-correlation is reported at every lag inside the window; the window sets the search width and the bands) |
| event size θ (total) | 1 Moz in a day | {0.25, 0.5, 1, 2, 3} Moz; per depository {0.1, 0.25, 0.5, 1} |
| event cooling | 10 sessions | {5, 10, 20} |
| forward horizon h | 20 sessions | {5, 7, 10, 13, 15, 20, 30, 60} |
| frequency window | 20 sessions | {10, 20, 40}; cut {top 33%, top 20%, top 10%} |
| reverse direction: rally | +10% over 20 sessions | {4, 5, 6, 7, 8, 9, 10}% over {10, 20, 40} sessions; both signs |
| era | all | {all, 2006–08, 2009–14, 2015–19, 2020–21, 2022–26} (where ≥ 30 events / 250 sessions) |

## 4. Tests (one family null each; `src/sweep.py`)

| test | statistic per cell | family null | registered cell's criterion |
|---|---|---|---|
| **T-S1a lead–lag** | the largest \|ρ\| inside the window and its lag (negative = stocks move first) | SLV returns time-shifted by ≥ 52 weeks, best-of-grid over all cells, 300 draws | at ±12 weeks, weekly, total registered: "stocks lead" supported only if the peak sits at a negative lag, clears the null's 95th percentile, and holds in both halves (rule C) |
| **T-S1b lock-up → price** | share of positive SLV forward returns after an event − base rate (points) | SLV time-shifted (≥ 250 sessions); best-of-grid | θ 1 Moz, h 20, cooling 10: the H-table standard (n ≥ 30, gap ≥ 10 points, p < 0.05); INCONCLUSIVE below n 30 |
| **T-S1c frequency as a state** | SLV forward return (mean, share positive) in the high-frequency state − the rest | same | window 20, top 20%, h 20: the H-table standard |
| **T-S1d price → lock-up** | share of rally windows followed by a lock-up event − base rate; and Δlog R over the next h sessions vs unconditional | registered-stock series time-shifted | +10% / 20 sessions, h 20: the H-table standard; the asymmetry between T-S1b and T-S1d is the finding |
| **T-S1e the ML form** (after a–d) | walk-forward ridge and gradient-boosted trees with the grid variables as features; out-of-sample rank IC for SLV's h-session return | targets shifted, best-of-grid over h | registered per family by dated amendment before it runs |
| cross-check | gold's registered stock through the same grid | — | reported |

**Prior #84 (Claude, before any data; v2 wording).** T-S1a: the best cell's peak \|ρ\| sits at lag 0 to +4 weeks with stocks *following* price,
\|ρ\| 0.10–0.20, and no cell with a negative-lag peak clears the null. T-S1b: no survivor in the "price up after lock-up" direction; INCONCLUSIVE at the
registered cell. T-S1c: no survivor. T-S1d: at least one survivor (registered stock falls after rallies of 6–10%); the asymmetry is the result. In
words: the vault data is a consequence of the price, not a cause; the 2021 and 2025 "lock-up" readings are the same mechanism seen twice.

## 5. What this does not do

It does not name owners; it uses no paid feed; nothing enters the app or the model ledger before a registered PASS and a forward test. The
per-depository series are kept for the founder's reading of them, labelled "depository, not owner".

## 6. Results

| date | test | result | prior |
|---|---|---|---|
