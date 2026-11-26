# Test CDS-4: after a jump in Oracle's CDS, is Oracle's share weaker the next session?

Registered in TRACK 3.135 before running. One test, limit: chance under 0.05. 561 sessions, 2024-09-03 to 2026-11-25. The day's spread = the middle one of that day's trades whose spread is GIVEN in the public file, done before 16:00 New York (159 days have one). A jump = 5% or more above the last such day, at most 5 sessions back. Each jump day is set against the 10 other days on which Oracle's share moved most nearly the same amount that day without a jump ('look-alike days').

| | |
|---|---|
| jumps with a next session | 25 |
| Oracle's share ON the jump day, average | -1.46% |
| Oracle's share the NEXT session, average | -1.56% |
| the same after the look-alike days | -0.36% |
| **difference (jump days minus look-alike days)** | **-1.20%** |
| chance (the share of 521 copies with the jump days slid along the calendar that show a difference at least as large) | 0.1398 |
| **verdict** | **does not pass** |

## Every jump

| day | spread before -> that day, basis points (trades) | share that day | share next session | look-alike days' next session |
|---|---|---|---|---|
| 2025-09-03 | 44 -> 46 (1) | -0.82% | -0.20% | -0.57% |
| 2025-09-24 | 41 -> 50 (1) | -1.71% | -5.55% | -0.27% |
| 2025-09-30 | 50 -> 54 (2) | -0.54% | +2.76% | -0.41% |
| 2025-10-02 | 54 -> 59 (1) | -0.08% | -0.91% | +0.58% |
| 2025-10-14 | 54 -> 68 (1) | -2.93% | +1.55% | -0.29% |
| 2025-10-16 | 68 -> 73 (2) | +3.09% | -6.93% | -0.74% |
| 2025-10-31 | 75 -> 86 (2) | +2.23% | -1.81% | -1.78% |
| 2025-11-13 | 86 -> 99 (6) | -4.15% | +2.43% | -0.12% |
| 2025-11-21 | 107 -> 116 (5) | -5.66% | +0.76% | -1.39% |
| 2025-11-25 | 116 -> 125 (6) | -1.62% | +4.02% | -0.49% |
| 2025-12-12 | 136 -> 152 (1) | -4.47% | -2.66% | -0.17% |
| 2026-02-04 | 129 -> 138 (3) | -5.17% | -6.95% | -0.45% |
| 2026-02-05 | 138 -> 150 (3) | -6.95% | +4.65% | -1.48% |
| 2026-03-17 | 152 -> 162 (4) | -0.82% | -1.16% | -0.57% |
| 2026-04-09 | 160 -> 177 (1) | -3.70% | +0.17% | +1.16% |
| 2026-07-17 | 187 -> 200 (1) | +1.77% | -3.98% | +0.67% |
| 2026-08-18 | 197 -> 210 (3) | -2.63% | +0.71% | -0.21% |
| 2026-09-15 | 180 -> 194 (1) | -3.07% | +2.00% | -0.96% |
| 2026-09-22 | 191 -> 212 (1) | +0.43% | -3.11% | -0.71% |
| 2026-09-24 | 212 -> 230 (1) | -3.47% | -1.75% | -1.37% |
| 2026-10-13 | 246 -> 264 (2) | +4.23% | -8.83% | +1.04% |
| 2026-10-15 | 264 -> 302 (1) | +3.00% | -4.64% | -1.13% |
| 2026-10-20 | 302 -> 342 (1) | +1.20% | -1.53% | +0.14% |
| 2026-11-18 | 295 -> 319 (1) | -0.97% | -2.92% | -0.69% |
| 2026-11-24 | 317 -> 365 (3) | -3.68% | -5.13% | +1.16% |

What a pass would not mean: the trades are timed when done, not when made public, so it is not yet a rule that can be traded; one market condition; one company. A forward record on new days follows (`python -m src.cds_oracle forward`).
The data: public trade reports under the SEC's Regulation SBSR (DTCC), kept for our own testing, not uploaded (TRACK 3.127).
