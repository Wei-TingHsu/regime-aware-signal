"""record_5nov_audit.py -- the 5 Nov results of the first sub-period batch and of T-K3 at n = 4, written into the record once, anchored.

Appends: docs/prereg_subperiod_audit.md section 4 (one row per item, from the docs/era_*.md and .json files the runs wrote --
numbers copied from the terminal output of 5 Nov 17:11-17:16 SGT); docs/TRACK.md a 5 Nov paragraph. Nothing is rewritten; the
prior judgments are proposals for the founder ("counted if the founder agrees"), the tally is not bumped here.
    python scripts_applied/record_5nov_audit.py
"""
import sys
from pathlib import Path

ROWS = """| 2026-11-05 | A — calls by era (`97d9bf07dd2c_n5793`, h 2) | 2009–14 hit 57.0% (n 263, null q95 58.6%), 2015–19 54.6% (421; 57.2%), 2020–21 58.6% (263; 60.1%), 2022–26 53.8% (699; 56.4%): no era beats its null. Rule C: S1 PASS, S2 PASS (ratio 1.30). Sweep era × source × asset: best 2020–21 × earnings_8k 63.4% vs best-of-sweep q95 75.0%, p_family 0.957. docs/era_scoreboard_97d9bf07dd2c_n5793_h2.md | **#85** right on 'no era beats its null' and on the sweep; wrong on S2 (predicted FAIL) — counted if the founder agrees |
| 2026-11-05 | B1 — T-L6 liquidity–gold by era | β by era: 2004–08 +0.05 (t 0.5), 2009–14 +0.04 (0.4), 2015–19 +0.20 (2.7, R² 0.027), 2020–21 −0.01 (−0.1), 2022–26 +0.23 (2.0, R² 0.016). Sequential sup-F: one break, 2008-09-24 (p 0.008, β 0.62 → 0.03), none after; no registered watershed within 26 weeks. Recent-window sweep: best W 312, z +1.80 vs q95 +2.87, p_family 0.183. Liquidity's weekly volatility: 2022–26 1.41% vs 2015–19 1.37%, 2009–14 1.60%, 2004–08 2.61%. Reading: the link is present in 2015–19 and 2022–26 and absent in 2009–14 and 2020–21 — on-and-off, not 'absent then present'; no break survives. docs/era_liquidity_liquidity.md | **#86** right on no break and on 2022–26 inside the range; wrong on the volatility clause (predicted ≥ 1.5× 2009–19; measured ≈ 1×) — counted if the founder agrees |
| 2026-11-05 | B2 — P1 by era | Stress-minus-abundant gap in 20-session GLD–SPY correlation: 2004–08 +0.04, 2009–14 **−0.34**, 2015–19 −0.10, 2020–21 +0.04, 2022–26 **+0.21**; pooled +0.007. Sweep era × window × lag: best 2009–14 \\|gap\\| 0.344 vs q95 0.510, p_family 0.350 — the state labels are so persistent that block-permuted labels produce gaps this large by chance. Reading: the sign flips from safe-haven (2009–14) to dash-for-cash (2022–26), the shape the founder asked about, but the instrument cannot tell it from chance with this few independent stress episodes. docs/era_liquidity_p1.md | **#87** right on 'no era beyond its null' and the sweep; wrong on 'every gap within ±0.05' — counted if the founder agrees |
| 2026-11-05 | B3 — T-L5b grid (147 cells × eras, both directions) | 'Gold sold after a sell-off': best cell −4% / 10 sessions / look 10 / all, gap +4.8 pts (n 67) vs q95 +20.9, p_family 0.865, no survivor. 'Gold bought after a sell-off': best cell **−6% / 15 sessions / look 20 / all, gap +17.9 pts (n 34) vs q95 +17.6, p_family 0.050, one survivor** — by 0.3 points, at the bar. Every era-specific cell under 30 events ('·'). docs/era_liquidity_selloff_sold.md, _bought.md | **#88** right on 'sold'; wrong on 'bought' (predicted no survivor) — counted if the founder agrees. Under the standing rule the survivor is a candidate for a forward test by dated amendment, not a finding |
| 2026-11-05 | B4 — factor sensitivities by era (GLD) | The factor panel starts in 2014 (a late-starting proxy truncates it: 3,046 sessions), so only 2015–19, 2020–21, 2022–26 are measured: in-sample R² 0.33, 0.26, 0.22. T-A by era × window: best W 1008 × 2015–19 median OOS R² 0.437 vs q95 −0.007, p_family 0.000 (survives). The 2026 fall re-attributed: pre-episode 504 sessions explain 2%, **2009–21 betas 29%**, 2022→ betas 11%, all 25% — the old sensitivities explain more of the fall than the recent ones; none explains most of it. docs/era_factors_GLD.md | **#89** right on the sweep surviving and on '< 0.3 under 2022→'; wrong on the era ranking (2015–19 is the highest, not the lowest) and on '< 0.2 under 2009–21' — counted if the founder agrees. Follow-up: re-run with the late-starting proxy dropped so 2004–14 enter |
| 2026-11-05 | B5 — T9b by era | β per σ: zero bound (39) −0.40 (t −4.4), normalisation (34) −0.39 (−4.7), **pandemic (19) −1.12 (−4.2)**, hiking (40) −0.42 (−4.4). Era × surprise interaction: per bp F 5.10, p 0.005; **per σ F 3.06, p 0.026 — the eras differ even in volatility units**, carried by 2020–21: gold reacted about 2.7× more per unit of surprise in the pandemic era, on 19 statements. By chair (T-K1′) this was invisible because the era sits inside Powell's tenure. A closed era cannot be forward-tested; it is recorded as measured. docs/era_fomc.md | **#90 wrong** (predicted no difference per σ) — counted if the founder agrees |
| 2026-11-05 | B7 — oil shocks by era | Measured only (every era under 30 shocks in p8; p5 reaches 31–37): GLD's 20-session median after a shock positive in every era but 2015–19 (p5: +2.2%, +1.1%, −0.3%, +0.3%, +0.4%). docs/era_events_oil.md | **#91** judged by the founder from the f60 column of the table |
| 2026-11-05 | T-K3 at n = 4 (28 Oct statement in) | Warsh's 4 vs Powell's last 8: energy 2.41, exact p **0.061** (30 of 495 arrangements) → does not separate at 0.05; at n = 3 it had (0.042). Dimensions: inflation-vs-labour 0.010, hedging density 0.038, balance sheet 0.275. Acceptance unchanged (both past transitions separate). Chair posterior refreshed: weight on his own 4 days 20% per σ, posterior −0.50% ± 0.16 per σ; his days averaged −0.53% on gold against −0.43% implied by his +3.8 bp hawkish surprises. The 2 pm reader fired live for the first time (02:00:37 SGT, reaction file 02:20). docs/chair_style.md, chair_power.md | **#79** right on the verdict (no separation at n = 4), wrong on the dimension (balance sheet named; inflation emphasis measured) — counted if the founder agrees |
"""

TRACK_PARA = """
5 Nov 17:20: first sub-period batch run and recorded (prereg_subperiod_audit §4). Nothing beats its null by era; two shapes worth the founder's eye: P1's gap flips sign between 2009–14 (−0.34, safe haven) and 2022–26 (+0.21, dash for cash) but sits inside a null built from persistent states; T9b per σ differs by era (p 0.026) because the pandemic era's gold reaction was ~2.7× the others on 19 statements. One sweep survivor at the bar: gold *bought* after a −6% / 20-session SPY drawdown, 15 sessions forward (+17.9 pts vs q95 +17.6, p_family 0.050) — a forward-test candidate, the opposite of the 27 Oct hypothesis. The 2026 gold fall is explained better by 2009–21 sensitivities (29%) than by 2022→ ones (11%). T-K3 at n = 4: p 0.061, not distinguishable; inflation emphasis the dimension both times. **CME has blocked this IP for suspected scraping** after the three probes of 28 Oct–5 Nov (the response names its Data Terms of Use): no further scripted requests to cmegroup.com; the silver registration waits for a hand-downloaded history or is shelved. Routing patch applied 5 Nov; verify in the 6 Nov log. Next: the era_factors re-run without the late-starting proxy; adapters B6, B8–B12; group C; the forward registration for the −6% survivor if the founder wants it.
"""


def main():
    p = Path("docs/prereg_subperiod_audit.md"); s = p.read_text()
    if "| 2026-11-05 | A — calls by era" in s:
        print("  prereg_subperiod_audit: 5 Nov rows already present -- skipped")
    else:
        anchor = "## 4. Results\n\n| date | item | result | prior |\n|---|---|---|---|\n"
        if s.count(anchor) != 1:
            sys.exit("prereg_subperiod_audit: results header not where expected -- nothing changed")
        p.write_text(s.replace(anchor, anchor + ROWS, 1)); print("  prereg_subperiod_audit: eight result rows added")
    t = Path("docs/TRACK.md"); s = t.read_text()
    if "5 Nov 17:20: first sub-period batch" in s:
        print("  TRACK: 5 Nov paragraph already present -- skipped")
    else:
        t.write_text(s.rstrip("\n") + "\n" + TRACK_PARA); print("  TRACK: 5 Nov paragraph appended")
    print("done -- review `git diff docs/`")


if __name__ == "__main__":
    main()
