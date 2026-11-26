# Public single-company CDS trades of large technology companies: what the files hold

576 daily files, 2024-09-03 to 2026-11-25. Rows that name one of 24 companies: 20,752; of them new trades (action NEWT): 16,134.

| company | rows | new trades | days with a new trade | first day | new trades in the last 60 files |
|---|---|---|---|---|---|
| Oracle | 4,770 | 3,753 | 422 of 576 | 2024-09-04 | 1054 |
| Broadcom | 1,797 | 1,513 | 266 of 576 | 2024-09-06 | 707 |
| Nvidia | 1,544 | 1,340 | 131 of 576 | 2025-11-20 | 918 |
| Amazon | 1,682 | 1,322 | 316 of 576 | 2024-09-10 | 541 |
| Meta | 1,296 | 1,062 | 192 of 576 | 2025-10-30 | 448 |
| Alphabet | 1,272 | 1,013 | 203 of 576 | 2024-11-15 | 494 |
| AMD | 1,282 | 981 | 259 of 576 | 2024-09-03 | 417 |
| CoreWeave | 1,440 | 930 | 210 of 576 | 2025-09-30 | 445 |
| Dell | 984 | 769 | 285 of 576 | 2024-09-04 | 186 |
| Intel | 943 | 723 | 278 of 576 | 2024-09-18 | 223 |
| Microsoft | 966 | 717 | 186 of 576 | 2025-01-15 | 251 |
| IBM | 831 | 585 | 257 of 576 | 2024-09-04 | 122 |
| Netflix | 766 | 566 | 233 of 576 | 2024-09-04 | 126 |
| Cisco | 506 | 390 | 179 of 576 | 2024-09-04 | 116 |
| TSMC | 336 | 256 | 143 of 576 | 2024-09-13 | 50 |
| Tesla | 153 | 111 | 58 of 576 | 2024-09-04 | 60 |
| Apple | 153 | 99 | 55 of 576 | 2024-09-13 | 26 |
| Super Micro | 30 | 3 | 3 of 576 | 2025-09-22 | 0 |
| Texas Instruments | 1 | 1 | 1 of 576 | 2026-09-17 | 1 |

## Which price information the new trades carry (share of new trades with the column filled)

| column | all listed companies | Oracle | most frequent values (Oracle) |
|---|---|---|---|
| Notional amount-Leg 1 | 100% | 100% | 5,000,000+ (2907); 2,000,000 (204); 1,000,000 (202); 3,000,000 (179) |
| Fixed rate-Leg 1 | 81% | 80% | 0.01 (2982); 1 (8); 1.42712 (1); 0.05 (1) |
| Spread-Leg 1 | 20% | 20% | 0.0195 (16); 0.0164 (13); 0.0168 (13); 0.016 (12) |
| Post-priced swap indicator | 100% | 100% | false (3751); true (2) |
| Spread notation-Leg 1 | 20% | 20% | 3 (762); 4 (1) |
| Fixed rate day count convention-leg 1 | 98% | 97% | A004 (3634) |
| Other payment amount | 91% | 89% | 0.00000 (21); 117179.00000 (6); 167499.00000 (6); 4583.85000 (5) |
| Fixed rate payment frequency period-Leg 1 | 98% | 97% | MNTH (3634) |
| Fixed rate payment frequency period multiplier-Leg 1 | 98% | 97% | 3 (3565); 6 (69) |
| Other payment type | 91% | 89% | UFRO (3277); UWIN (58); UFRO;UWIN;UWIN (1); UFRO;UWIN (1) |
| Other payment currency | 91% | 89% | USD (3334); EUR (1); USD;USD;USD (1); USD;USD (1) |
| Package transaction price | 3% | 1% | 0.000001 (26); 0.004847 (2); 0 (2); 47.08 (1) |
| Package transaction price notation | 3% | 1% | 3 (55) |
| Package transaction spread | 4% | 5% | 0.0019 (14); 0.001725 (14); 0.00125 (10); 0.0016 (8) |
| Package transaction spread notation | 4% | 5% | 3 (177); 4 (17) |

Size hidden behind the cap ('+'): 72% of the new trades.
