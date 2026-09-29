# Surprise conditioning — stage A, level 3

*Run 2026-09-29 16:34. Registered in `docs/prereg_surprise.md` (§2b). 132 FOMC statements; surprise = published FRBSF Bauer–Swanson 30-minute surprise (bp), used continuously; 23 statement(s) after the series end use the ΔDGS2 proxy; outcome = 3-session forward log return; 10,000 permutations of the surprise.*

| asset | n | b(stance) | b(surprise per bp) | b(run-up) | p(surprise) | expected sign | sign ok | significant |
|---|---|---|---|---|---|---|---|---|
| TLT | 132 | +0.0000 | **-0.0003** | +0.0055 | 0.5649 | − | yes | no |
| GLD | 132 | -0.0036 | **-0.0005** | -0.0011 | 0.4877 | − | yes | no |
| SPY | 132 | -0.0015 | **+0.0001** | -0.0081 | 0.8874 | − | no | no |
| UUP | 132 | +0.0009 | **-0.0001** | -0.0002 | 0.6971 | + | no | no |
| USO | 132 | -0.0020 | **-0.0005** | -0.0085 | 0.7119 | − | yes | no |

## Verdict: **FAIL** (criterion assets: TLT, GLD; met on: none)

### GLD: mean 3-session return by reader stance (rows) × surprise bucket (columns) — descriptive only

| stance \ surprise | dovish (−1) | neutral (0) | hawkish (+1) |
|---|---|---|---|
| dovish | -0.70% (n=5) | -0.04% (n=57) | +2.61% (n=3) |
| neutral | — | +0.09% (n=1) | — |
| hawkish | -0.30% (n=5) | -0.34% (n=55) | -4.24% (n=6) |

### TLT: mean 3-session return by reader stance (rows) × surprise bucket (columns) — descriptive only

| stance \ surprise | dovish (−1) | neutral (0) | hawkish (+1) |
|---|---|---|---|
| dovish | -0.17% (n=5) | -0.00% (n=57) | -0.11% (n=3) |
| neutral | — | -1.41% (n=1) | — |
| hawkish | +0.51% (n=5) | -0.13% (n=55) | -0.48% (n=6) |

*Reading.* TLT is close to tautological here — the 2-year change on the day is the bond market's own reaction — so GLD is the informative row. If only TLT passes, the proxy is measuring the bond market, not the surprise, and the published Swanson / Bauer–Swanson series is the next registration (level 3).
