# Regime-Aware Signal

A daily read on five core markets, built from the policy and company documents
published that day — and, more often than not, an explicit refusal to call it.

NUS MSc Finance · BMF5391C Applied Faculty Project · Hsu Wei-Ting  
Faculty supervisor: Dr Lee Yen Teik

---

**Live:** https://regime-aware-signal.streamlit.app — the same app, redeployed automatically from each night's commit. A dormant app takes about thirty seconds to wake; the first asset lookup takes about a minute.

## Run the demonstration terminal

```bash
git clone https://github.com/Wei-TingHsu/regime-aware-signal.git
cd regime-aware-signal

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

It opens a browser tab. `Ctrl+C` in the terminal stops it.

**Nothing needs to be computed first.** The daily reports are pre-generated in
`outputs/reports/` and the app only reads them, so the Today tab loads instantly and works offline. The exception is "Look up an asset", which prices a ticker on request, needs a network connection, and takes about a minute on its first use while the expanding regime labels are computed.

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
| `docs/PROJECT_MASTER.md` | **Start here.** The whole project in one file — plain-language overview, week-by-week history, every test and its verdict, the thirteen-route roadmap, and every canonical document bound in full |
| `docs/TRACK.md` | Short daily status board: what is running, what to check, what is done |
| `docs/CURRENT_STATE_2026-08-23.md` | The append-only evidence record; §18 is the latest |
| `docs/prereg_*.md` · `docs/overlays/` | Pre-registrations — every criterion, fixed before the test |
| `docs/*_results.md` · `docs/*_scoreboard*.md` | Every registered test's output, including the failures |
| `outputs/reports/` | One decision report per completed session, written once and never regenerated (Markdown and JSON) |
| `outputs/reports_backfill/<hash>/` | As-of reports over the historical corpus, one folder per corpus version, never merged |
| `app.py` | The demonstration terminal |
| `src/analog_event.py` | The conditional estimator, frozen at commit `9062391` |
| `step5_weighting.py` · `step6_report.py` | Weighted net view and decision report |
| `src/report_scoreboard.py` · `src/report_backfill.py` | The referee that scores the report's own calls, and its historical backfill |
| `daily_run.sh` · `install_launchd.sh` | Unattended nightly run |
| `docs/archive/` | Superseded documents, kept for the record |

## How to read the evidence

Start with `docs/PROJECT_MASTER.md` — Part A reads in half an hour and assumes no finance background; Part B holds every source document in full. For the evidence behind any number, `docs/CURRENT_STATE_2026-08-23.md` is the dated record, and §18 is the latest.

The short version: the headline hypotheses were tested and rejected — gold does not reliably decouple from equities under stress; sector rotation has no stable running order — and a trend-model advantage was traced to a look-ahead. The conditional estimator survived correct inference in one cell of 45. The report's own directional calls, scored against a within-asset permutation null over 1,532 historical document days, did not beat following the market's drift. Nearly thirty plausible beliefs, each held in writing, were overturned by running code and are logged with dates. The product that ships is one that abstains and says why; the next phase, registered in the roadmap, builds exposure, expected move and unfamiliarity as its primary outputs.

## Automation

```bash
./install_launchd.sh          # weekdays 15:00 SGT
launchctl list | grep regimeaware
./daily_run.sh --no-read      # run once by hand, no API spend
```

`daily_run.sh` appends the forward-test row, fetches and reads new documents
under a nightly cap, writes each completed session's report once — never regenerated — and rebuilds the index the app serves. It never refits a frozen model. It also fetches new FOMC statements and Federal Register documents, holds a report back while any of its session's documents are unread, and commits and pushes the day's ledgers, scoreboards and reports so the record leaves the machine every night.
