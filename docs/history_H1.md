# H1 — Fed decision days (statement days), split by the 2-yr yield's move that day

*2026-10-19 14:34. 132 events after the 20-session collapse, sample 1995-01-03 → 2026-10-19. Simple % medians. 'positive' = share of events with a higher price h sessions later; 'base' = the market's ordinary share. Test (prereg §1 as amended §4): |gap| ≥ 10% points, n ≥ 30, random-date null p < 0.0083. Decision dates from processed/fomc_decisions.csv (2011 on). No GAP collapse applied: meetings are ≥ 6 weeks apart.*

| market | n | 5 s | 20 s | 60 s | worst (session) | best (session) | 5 s: positive / base / gap / p | 5 s verdict | 20 s: positive / base / gap / p | 20 s verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 130 | +0.1% | +1.9% | +4.1% | -2.8% (14) | +6.0% (53) | 53% / 59% / -6% / 0.178 | FAIL | 71% / 66% / +5% / 0.226 | FAIL |
| TLT | 130 | +0.2% | +0.2% | +1.3% | -2.8% (26) | +4.1% (31) | 52% / 53% / -1% / 0.934 | FAIL | 53% / 53% / -0% / 1.000 | FAIL |
| GLD | 130 | -0.4% | +0.7% | +1.8% | -3.5% (26) | +5.5% (31) | 44% / 55% / -11% / 0.009 | FAIL | 53% / 56% / -2% / 0.588 | FAIL |
| UUP | 130 | +0.3% | +0.4% | +1.0% | -1.3% (22) | +2.5% (41) | 59% / 52% / +8% / 0.093 | FAIL | 60% / 52% / +8% / 0.079 | FAIL |
| USO | 130 | -0.0% | +1.1% | +1.3% | -8.3% (28) | +9.6% (30) | 49% / 53% / -3% / 0.485 | FAIL | 55% / 52% / +3% / 0.529 | FAIL |
| WTI_SPOT | 126 | -0.6% | +0.7% | +1.4% | -8.9% (28) | +10.1% (32) | 44% / 53% / -10% / 0.028 | FAIL | 54% / 54% / -0% / 1.000 | FAIL |

Split (H1): 2-yr yield up on the day vs down. Medians for each half; 'positive up / dn' is the share higher h sessions later; label-permutation p.

| market | n up / dn | h | up median | dn median | positive up / dn | gap | p | verdict |
|---|---|---|---|---|---|---|---|---|
| SPY | 52 / 60 | 5 | -0.2% | +0.2% | 46% / 57% | -11% | 0.274 | FAIL |
| SPY | 52 / 60 | 20 | +1.4% | +2.3% | 65% / 73% | -8% | 0.371 | FAIL |
| TLT | 52 / 60 | 5 | -0.1% | +0.1% | 48% / 52% | -4% | 0.720 | FAIL |
| TLT | 52 / 60 | 20 | +0.1% | +0.8% | 52% / 57% | -5% | 0.633 | FAIL |
| GLD | 52 / 60 | 5 | -0.5% | -0.0% | 42% / 50% | -8% | 0.446 | FAIL |
| GLD | 52 / 60 | 20 | +0.2% | +1.2% | 50% / 60% | -10% | 0.309 | FAIL |
| UUP | 52 / 60 | 5 | +0.4% | +0.1% | 65% / 55% | +10% | 0.271 | FAIL |
| UUP | 52 / 60 | 20 | +0.4% | +0.5% | 60% / 60% | -0% | 0.973 | FAIL |
| USO | 52 / 60 | 5 | -0.4% | -0.0% | 48% / 48% | -0% | 0.974 | FAIL |
| USO | 52 / 60 | 20 | +0.7% | +1.7% | 52% / 58% | -6% | 0.502 | FAIL |
| WTI_SPOT | 50 / 59 | 5 | -0.9% | -0.4% | 40% / 42% | -2% | 0.785 | FAIL |
| WTI_SPOT | 50 / 59 | 20 | -0.1% | +0.9% | 50% / 56% | -6% | 0.540 | FAIL |
