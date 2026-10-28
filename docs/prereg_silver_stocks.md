# Pre-registration — T-S1: deliverable silver at the COMEX depositories and silver's price (DRAFT)

*Drafted 2026-10-28 from the founder's hypothesis of 28 Oct, before any data is on disk. It becomes a registration when the founder
commits it; the first run needs ≥ 250 sessions of warehouse data (section 2).*

**The founder's sentence.** The main silver holders (JP Morgan and others) sometimes take silver out of the warehouse, or "lock it up",
so that it can no longer be used to deliver against futures contracts. The correlation of those actions — in amount and in frequency —
with silver's price trend, allowing that the action may lead or lag the price.

## 1. What is observable, and what is not

The CME Group publishes a daily depository report for COMEX silver: for each depository (the vault operator — JPMorgan, Brink's, CNT,
Loomis, HSBC, Manfra Tordella & Brookes, Asahi, Delaware Depository, Malca-Amit and others), the ounces held as **registered** (a
warrant has been issued; the metal can be delivered against a futures contract) and **eligible** (meets the contract's specification, no
warrant; cannot be delivered until a warrant is issued), with the day's receipts, withdrawals and adjustments between the two categories.

- "Lock up" in the founder's sense has two observable forms: a **warrant cancellation** (registered → eligible: the metal stays in the vault
  but leaves the deliverable pool) and a **withdrawal** (the metal leaves the vault). Both are in the report. Both are measured.
- **The owner is not observable.** The report names the vault, not whose metal sits in it: a JPMorgan-depository move may be a client's. Every
  statement below is about *depository-level deliverable stock*; "JP Morgan" means the JPMorgan depository. The hypothesis about the bank's
  own book cannot be tested with public data and is not claimed.
- Metal can also leave deliverability without leaving the report (an eligible→registered reversal later), so the stock level, not only the
  flow, is carried.

## 2. Data (free; forward collection from the first probe)

`src/fetch_comex_stocks.py` downloads CME's daily silver (and gold, for the cross-check) depository file once a day into
`data_provenance/comex_stocks/raw/YYYYMMDD_<metal>.xls` (write-once by date) and appends the parsed rows to
`processed/comex_<metal>_stocks.csv` (date, depository, registered, eligible, total, received, withdrawn, adjustment). The URL and the
file layout are **unverified from the sandbox** (the CME host is not on its allow-list): `--probe` reports status and content type first,
and the parser keeps the raw file and prints the sheet when the layout is not what it expects. History: a hand-downloaded archive is
accepted under the same rule as the SPDR file (27 Oct) — a third-party series only if labelled as such, with its source and terms in the
provenance note. **Floor:** the first run needs ≥ 250 sessions; from forward collection alone that is about November 2027, with a history
file it is now. Price: SLV (Apr 2006 →) close-to-close; SI=F continuous beside it as the instrument check.

## 3. Variables

- `R_t` total registered ounces; `R_{d,t}` per depository; `E_t` eligible; `S_t = R_t / (R_t + E_t)` the deliverable share.
- Daily lock-up flow `L_t = max(0, −ΔR_t)`, split into adjustments (registered → eligible) and withdrawals where the report allows.
- **Events:** a session with `L_t ≥ θ`, θ ∈ {0.5, 1, 2} million oz for the total, {0.25, 0.5, 1} per depository (the registered cell is θ = 1 Moz
  total; the others are the sweep, standing rule of 23 Oct). One event per 10 sessions (non-overlap).
- **Frequency:** the count of events in the trailing 20 sessions, `F_t`.
- Weekly aggregates (Friday) for the lead–lag test: `Δlog R` and SLV's weekly log return.

## 4. Tests and criteria (fixed before the first run)

| test | statistic | criterion |
|---|---|---|
| **T-S1a lead–lag** | cross-correlation of weekly `Δlog R` with weekly SLV returns at lags −12 … +12 weeks (negative lag = stocks move first); 95% bands from a circular block bootstrap (block 8 weeks, 1,000 draws); the lag of the largest \|ρ\| and its sign are the result | reported; "stocks lead price" is supported only if the largest \|ρ\| sits at a negative lag, outside the bands, and the same sign holds in both halves of the sample (rule C) |
| **T-S1b lock-up → price** | SLV forward return 5 / 20 / 60 sessions after an event; share positive vs the base rate; random-date null, 1,000 draws | the H-table standard: PASS if n ≥ 30, gap ≥ 10 points and p < 0.05 at the registered cell (θ = 1 Moz, 20 sessions); INCONCLUSIVE if n < 30 |
| **T-S1c frequency as a state** | SLV forward 20-session return when `F_t` is in its top quintile vs the rest; same null | same standard |
| **T-S1d price → lock-up (the reverse direction, registered now)** | after a +10% / −10% 20-session move in SLV: `Δlog R` over the next 20 sessions vs the unconditional distribution; share of such windows with a lock-up event vs the base rate | same standard; the asymmetry between T-S1b and T-S1d is the finding |
| sub-periods | every statistic above for 2006–2019 and 2020–2026 (the pandemic and the 2021 retail episode begin the second), rule C (S1–S3) applied | reported |
| cross-check | gold's registered stock through the same machinery | reported; no criterion |

**Prior #84 (Claude, before any data).** T-S1a: the largest \|ρ\| sits at lag 0 to +4 weeks with stocks *following* price (a rally brings
deliveries and withdrawals, so registered stock falls after the price rises), \|ρ\| 0.10–0.20. T-S1b FAIL or INCONCLUSIVE at θ = 1 Moz
(fewer than 30 non-overlapping events in the data available at the first run, or a gap under 10 points). T-S1c FAIL. T-S1d PASS in the
measured direction (registered stock falls in the 20 sessions after a +10% rally more often than the base rate). In words: the vault data is a
consequence of the price, not a cause of it; the 2021 and 2025 "lock-up" readings are the same mechanism seen twice. If T-S1a puts the peak at a
negative lag outside the bands in both halves, the prior is wrong and the forward test is registered the same day.

## 5. What this does not do

It does not name owners; it does not use any paid feed; it does not enter the app or the model ledger until a registered PASS and a forward
test. The per-depository series are kept for the founder's reading of them, labelled "depository, not owner".

## 6. Results

| date | test | result | prior |
|---|---|---|---|
