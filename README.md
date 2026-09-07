# Regime-Aware Signal

A daily read on five core markets, built from the policy and company documents
published that day — and, more often than not, an explicit refusal to call it.

NUS MSc Finance · BMF5391C Applied Faculty Project · Hsu Wei-Ting
Faculty supervisor: Dr Lee Yen Teik

---

## Run the demonstration terminal

```bash
git clone <this repo>
cd regime-aware-signal

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

It opens a browser tab. `Ctrl+C` in the terminal stops it.

**Nothing needs to be computed first.** The daily reports are pre-generated in
`outputs/reports/` and the app only reads them, so it loads instantly and works
offline. The one exception is the "Look up an asset" tab, which prices a ticker
on request and needs a network connection.

### What you should expect to see

**Most days, most markets say "No view."** That is the product working, not a
bug. A view is withheld unless at least eight genuinely comparable past
situations exist, and that threshold was fixed in writing before any result was
looked at. The reason for each refusal is printed on the card.

Three things worth trying:

- Tick **"Only days with a signal"** to jump to the days the system did speak.
- Open **2025-04-07** (the reciprocal-tariff announcement) to see several
  documents landing at once and being weighted into one view per market.
- In **"Look up an asset"**, type any listed ticker — not only the 47 in the
  project universe. Prices are fetched on request, eligibility is checked
  (enough history, and history spanning more than one market condition), and
  the same estimator runs on that asset's own record.

---

## Repository map

| Path | What it is |
|---|---|
| `app.py` | The demonstration terminal |
| `docs/prereg_*.md` | Pre-registrations — every criterion, fixed before the test |
| `docs/CURRENT_STATE_2026-08-23.md` | The authoritative project record; §17 is the latest |
| `docs/*_results.md` | Every registered test's output, including the failures |
| `outputs/reports/` | One decision report per document session, Markdown and JSON |
| `src/analog_event.py` | The conditional estimator, frozen at commit `9062391` |
| `step5_weighting.py` · `step6_report.py` | Weighted net view and decision report |
| `daily_run.sh` · `install_launchd.sh` | Unattended nightly run |

## How to read the evidence

Start with `docs/CURRENT_STATE_2026-08-23.md` §17. It records what was tested,
what failed, and what the failures cost — including 27 logged cases where a
plausible belief was overturned by running code, and the claims retired as a
result.

The short version: two headline hypotheses were tested and rejected (gold does
not reliably decouple from equities under stress; sector rotation has no stable
running order), the conditional estimator survived correct inference in one cell
of 45, and the product that ships is one that abstains and says why.

## Automation

```bash
./install_launchd.sh          # weekdays 15:00 SGT
launchctl list | grep regimeaware
./daily_run.sh --no-read      # run once by hand, no API spend
```

`daily_run.sh` appends the forward-test row, fetches and reads new documents
under a nightly cap, and regenerates the reports the app serves. It never
refits a frozen model.
