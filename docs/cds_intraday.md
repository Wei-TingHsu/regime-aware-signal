# Test CDS-2: inside the day, do shares move after a CDS trade -- or before it?

Registered in TRACK 3.130 before running. 595 events on 170 days (2025-03-20 to 2026-11-10). An event = a 5-year CDS trade whose spread is given in the public file and differs from the company's previous such trade. 'After' = the share's move over the next H minutes, times the direction of the spread change, averaged, in basis points: NEGATIVE = shares fall after a widening and rise after a tightening (the CDS trade came first). 'Before' = the same over the H minutes before the trade: negative = shares had already moved that way (shares came first). 'Chance' = the share of 5,000 copies, with each event day moved to another day within 20 sessions at the same minute, that show an 'after' at least as large. **PASSES** = chance under 0.00156 (0.05 / 32 tests); under 30 events: too few.

| events | spread change of at least | share measured | minutes H | events (of them wider) | after, basis points (chance) | before, basis points | verdict |
|---|---|---|---|---|---|---|---|
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | its own share | 5 | 310 (211) | +0.0 (0.9962) | +1.0 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | its own share | 15 | 306 (211) | -4.7 (0.1442) | -4.4 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | its own share | 30 | 299 (211) | -0.2 (0.9664) | -3.7 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | its own share | 60 | 291 (211) | -1.8 (0.7544) | -6.1 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 5 | 310 (211) | -2.0 (0.3445) | -0.2 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 15 | 306 (211) | -4.4 (0.2224) | -3.0 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 30 | 299 (211) | -4.9 (0.3191) | -4.3 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 60 | 291 (211) | -8.1 (0.2016) | -8.0 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | its own share | 5 | 103 (72) | -1.5 (0.6319) | -1.4 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | its own share | 15 | 102 (72) | -1.2 (0.8080) | -0.3 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | its own share | 30 | 99 (72) | -0.6 (0.9338) | +10.8 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | its own share | 60 | 98 (72) | -9.7 (0.2791) | +3.7 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 5 | 103 (72) | -0.6 (0.8496) | -0.8 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 15 | 102 (72) | +0.4 (0.9496) | -0.5 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 30 | 99 (72) | +5.5 (0.4881) | -0.9 | no |
| the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet) | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 60 | 98 (72) | -5.6 (0.5581) | -9.5 | no |
| Oracle alone | 1% | its own share | 5 | 102 (63) | +1.3 (0.7353) | -1.4 | no |
| Oracle alone | 1% | its own share | 15 | 99 (63) | -1.9 (0.7502) | -5.9 | no |
| Oracle alone | 1% | its own share | 30 | 94 (63) | +6.8 (0.4795) | -6.6 | no |
| Oracle alone | 1% | its own share | 60 | 90 (63) | +4.8 (0.6995) | -12.8 | no |
| Oracle alone | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 5 | 102 (63) | -0.6 (0.7920) | -0.2 | no |
| Oracle alone | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 15 | 99 (63) | +2.6 (0.5259) | +0.3 | no |
| Oracle alone | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 30 | 94 (63) | +9.5 (0.0878) | -5.7 | no |
| Oracle alone | 1% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 60 | 90 (63) | +7.0 (0.3809) | -11.4 | no |
| Oracle alone | 5% | its own share | 5 | 25 (17) | -6.6 (too few) | +1.5 | too few |
| Oracle alone | 5% | its own share | 15 | 25 (17) | +6.1 (too few) | +20.8 | too few |
| Oracle alone | 5% | its own share | 30 | 23 (17) | +3.3 (too few) | +37.0 | too few |
| Oracle alone | 5% | its own share | 60 | 23 (17) | -10.3 (too few) | +19.7 | too few |
| Oracle alone | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 5 | 25 (17) | -2.7 (too few) | -6.4 | too few |
| Oracle alone | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 15 | 25 (17) | +9.6 (too few) | -0.7 | too few |
| Oracle alone | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 30 | 23 (17) | +24.7 (too few) | -9.6 | too few |
| Oracle alone | 5% | the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM) | 60 | 23 (17) | +17.7 (too few) | -3.4 | too few |

**0 of 32 tests pass.**

What a pass would NOT mean: the trade's time is when it was done; the rule allows it to be reported up to a day later and the files do not say when it became public. Whether it could have been seen in time needs live collection of the files.
The data: public trade reports under the SEC's Regulation SBSR (DTCC), kept for our own testing, not uploaded (TRACK 3.127); 1-minute share prices from Databento (XNAS.ITCH), not uploaded.
