"""amend_5nov_evening.py -- the 5 Nov evening record, appended once:
  prereg_deeper_signals.md  section 5: the D1-D7 results of 17:5x (from the founder's terminal), including the nulls; a note that the
                            forward windows of the first run included the event day (fixed in v2; D1 re-run supersedes the 17:5x row);
                            section 2b: the founder's five redesigns (D1b sudden sell-off, D2b link by regime, D2c daily liquidity, D8 factor
                            combinations as an index, D5b the oil->rates->gold chain) with priors #100-#104; a second forward rule D1-5nov-b.
  TRACK.md                  a 5 Nov 20:30 paragraph.
    python scripts_applied/amend_5nov_evening.py
"""
import sys
from pathlib import Path

RESULTS = """| 2026-11-05 17:5x | D1 gold after a drawdown (first run) | long: best −6% / 20 / hold 5 / enter +3, no filter, Sharpe 4.23 vs q95 4.08, **p_family 0.045**, 2 survivors; short: 0.11 vs 2.51, p 0.94, none. **Superseded:** the forward windows of this run included the event session (fixed in deeper.py v2); the re-run's row replaces it. | #93 half right (threshold, survivor count, short side); wrong on horizon (5 not 10–20) and the gold-down filter |
| 2026-11-05 17:5x | D2 liquidity on/off meta-signal | 'on' rule Sharpe 0.93 vs q95 1.66, p_family 0.285 → **null**: the trailing t-statistic switches on too late | #94 right |
| 2026-11-05 17:5x | D3 correlation regime | last 20 sessions' GLD–SPY correlation predicts the next 20: skill 0.26 (26% of the forecast error removed vs the long-run mean) vs q95 0.09, **p_family 0.000**; the stress state adds nothing | #95 right on structure, wrong on size (said 0.05–0.15) |
| 2026-11-05 17:5x | D4 Fed-day drift | statement-day gold from the surprise alone, in high-volatility states: per-meeting Sharpe 1.34 vs q95 0.89, **p_family 0.000**; the rubric adds nothing; next-day and two-day targets inside the null. Tradeable only from 2 pm. | #96 right |
| 2026-11-05 17:5x | D5 gold after oil shocks | best cell a regime sub-cell, 2.15 vs q95 3.34, p_family 0.605 → **null** | #97 right |
| 2026-11-05 17:5x | D6 positioning | not run: the positioning series is `processed/flows.parquet` / `flows_levels.parquet`; deeper.py v2 finds it | — |
| 2026-11-05 17:5x | D7 calls learner | all calls net Sharpe 0.07 (n 1,646); best learner cell 0.28 vs q95 1.63, p_family 0.770 → **null** | #99 right |
"""

SECTION_2B = """
## 2b. The founder's redesigns (5 Nov evening; `src/deeper2.py`)

| id | the founder's reasoning | grid | statistic / null |
|---|---|---|---|
| **D1b sudden sell-off** | "6% in 20 sessions is not a sudden sell-off": the S&P down x% in ONE session and gold down y% the same session; what each does over the next 1–10 sessions | x ∈ {1.5, 2, 2.5, 3, 4}%, y ∈ {0 (no gold condition), 0.5, 1, 1.5, 2}%, h ∈ {1, 2, 3, 5, 10}, era; four readings: gold continues / reverses, S&P continues / reverses | net Sharpe from the next session's open-equivalent (event day excluded); the traded asset time-shifted |
| **D2b the link by regime** | the liquidity link is on in some years and off in others: which engine regime is it on in, so that when the regime returns the link is expected | β, t, R² per engine regime (weekly); regime × liquidity interaction, block-permutation p | p < 0.05 → the standing expectation "same regime, same link" is registered and logged forward |
| **D2c daily liquidity** | the weekly rule arrives too late; trade daily | driver: the overnight reverse-repo balance (daily, same evening) and the Wednesday balance-sheet change spread over the week (flagged as an approximation); z-bar {0.5, 1, 1.5} × h {1, 2, 5, 10} × direction × regime | net Sharpe; GLD time-shifted |
| **D8 factor combinations as an index** | not all factors explain the move: which combination explains and predicts best, as an index | every subset of up to 3 factors (+ all) × trailing 1/5/20-session changes → gold's next 1/5/20 sessions; walk-forward ridge refit every 250 sessions; train 1000/2000; ridge 10/100 | net Sharpe of trading the predicted sign; gold time-shifted (fewer null draws: the grid is large) |
| **D5b the oil → rates → gold chain** | oil up → inflation expectations → hawkish policy → higher real rates → gold down | link 1: 2-yr and 10-yr real yield change 5/10/20 sessions after each shock (mean, share up, t); link 3: gold after shocks split by whether rates rose | net Sharpe; forward paths detached from shock attributes |

**Priors (Claude, before the runs; counted if wrong).** **#100 D1b:** at 2–3% one-day S&P falls (n ≈ 150–300) the S&P shows no continuation or reversal beyond the null; gold shows a one-session reversal up after same-day falls ≥ 1% at p_family 0.05–0.20 — not a survivor; no era cell reaches 30 at x ≥ 3%. **#101 D2b:** the link differs by regime at p < 0.05, strongest in the regime that covers 2015–19 and 2022–26 (the engine's 'calm, tightening' state), β ≈ +0.2. **#102 D2c:** the RRP driver alone is null (p_family > 0.3); the interpolated series looks better only because it leaks the week's information. **#103 D8:** the best combination includes the dollar and real yields; next-1-session Sharpe 0.3–0.6 against a null q95 near 0.8 → p_family > 0.1 — the factors explain gold's move the same day, they do not forecast tomorrow's. **#104 D5b:** link 1 holds weakly (2-yr up after shocks in 55–60% of cases, t 1–2); link 3: gold after shocks where rates rose is lower than where they did not, but inside the null (p_family > 0.1) — the chain is real in sign and too slow and too diluted to trade from the shock.

**Second forward rule (5 Nov):** **D1-5nov-b** — buy GLD 3 sessions after SPY's 20-session return crosses −6%, hold 5 sessions (the D1 grid's best cell, first run). Logged beside D1-5nov; the forward log decides between them.
"""

TRACK_PARA = """
5 Nov 20:30: D1–D7 recorded with their nulls (prereg_deeper_signals §5): D3 (correlation persistence, skill 0.26, p_family 0.000) and D4 (Fed-day surprise in high-vol states, p_family 0.000) clear their nulls; D1 marginal (0.045) and superseded by the v2 re-run (the first run's forward windows included the event session — found on the sandbox stub, fixed before the founder's numbers are judged); D2, D5, D7 null; D6 now finds `flows.parquet`. Founder's redesigns registered as §2b with priors #100–#104: D1b sudden one-day sell-offs, D2b the link by engine regime, D2c daily liquidity, D8 factor combinations as a predictive index, D5b the oil→rates→gold chain measured link by link. Second forward rule D1-5nov-b. Every finding, null included, goes into the compendium next.
"""


def main():
    p = Path("docs/prereg_deeper_signals.md"); s = p.read_text()
    if "D2 liquidity on/off meta-signal | 'on' rule" in s:
        print("  prereg_deeper_signals: results rows already present -- skipped")
    else:
        anchor = "## 5. Results\n\n| date | test | result | prior |\n|---|---|---|---|\n"
        if s.count(anchor) != 1: sys.exit("results header not where expected -- nothing changed")
        s = s.replace(anchor, anchor + RESULTS, 1); print("  prereg_deeper_signals: seven result rows added")
    if "## 2b. The founder's redesigns" in s:
        print("  prereg_deeper_signals: section 2b already present -- skipped")
    else:
        anchor = "\n## 3. Priors"
        if s.count(anchor) != 1: sys.exit("section 3 anchor not unique -- nothing changed")
        s = s.replace(anchor, "\n" + SECTION_2B.rstrip("\n") + "\n" + anchor, 1); print("  prereg_deeper_signals: section 2b added (five redesigns, priors #100-#104, rule D1-5nov-b)")
    p.write_text(s)
    t = Path("docs/TRACK.md"); s = t.read_text()
    if "5 Nov 20:30: D1–D7 recorded" in s: print("  TRACK: paragraph already present -- skipped")
    else: t.write_text(s.rstrip("\n") + "\n" + TRACK_PARA); print("  TRACK: paragraph appended")
    print("done -- review `git diff docs/`")


if __name__ == "__main__":
    main()
