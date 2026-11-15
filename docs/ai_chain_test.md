# AI-chain news test: do Claude's scores of company news tell where prices go next?

Registered in `docs/prereg_ai_chain.md` before running. Trade = sign(score) x return after the text is public (SEC stamp, New York time). Returns in bp (1 bp = 0.01%), before cost. A cell is shown only with 30+ observations. Family p = how often shuffled scores produce a best cell as strong as the real best cell. A family passes at p < 0.0071 (0.05 / 7 families) with a mean above the cost (2 bp future, 10 bp stock, assumed).

## F1. Results releases stamped 16:00-16:40 (US filers) -> the Nasdaq-100 future. One observation per day: the average score of that afternoon's releases, entry counted from the last stamp. From June 2010.

Observations: 506.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, to 16:59 | 1 min after the stamp, to the next 09:35 | 1 min after the stamp, to the next 16:00 | 5 min after the stamp, hold 15 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, to 16:59 | 5 min after the stamp, to the next 09:35 | 5 min after the stamp, to the next 16:00 | 15 min after the stamp, hold 15 min | 15 min after the stamp, hold 30 min | 15 min after the stamp, to 16:59 | 15 min after the stamp, to the next 09:35 | 15 min after the stamp, to the next 16:00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | +2.2 bp, 52%, n 305 | +2.8 bp, 56%, n 378 | +2.4 bp, 54%, n 409 | +10.4 bp, 57%, n 409 | -3.6 bp, 51%, n 409 | +2.3 bp, 60%, n 288 | +2.2 bp, 52%, n 344 | +2.0 bp, 54%, n 404 | +10.7 bp, 57%, n 404 | -1.7 bp, 51%, n 404 | +0.7 bp, 53%, n 338 | -0.3 bp, 49%, n 180 | +0.2 bp, 55%, n 371 | +6.3 bp, 55%, n 385 | -5.7 bp, 49%, n 385 |
| results_vs_prior_guidance | +1.5 bp, 51%, n 232 | +1.5 bp, 55%, n 270 | +1.2 bp, 54%, n 295 | +13.6 bp, 58%, n 295 | +2.1 bp, 54%, n 295 | +2.2 bp, 59%, n 243 | +3.0 bp, 56%, n 244 | +2.2 bp, 56%, n 294 | **+16.7 bp, 61%, n 294** | +7.2 bp, 55%, n 294 | +0.6 bp, 53%, n 270 | +0.9 bp, 56%, n 120 | +0.9 bp, 58%, n 290 | +15.1 bp, 56%, n 304 | +14.5 bp, 56%, n 304 |
| guidance_change | +1.5 bp, 48%, n 213 | +1.5 bp, 57%, n 237 | +1.4 bp, 55%, n 259 | +5.0 bp, 54%, n 259 | -5.7 bp, 53%, n 259 | +0.7 bp, 57%, n 220 | +1.4 bp, 51%, n 213 | +0.8 bp, 55%, n 259 | +4.3 bp, 54%, n 259 | -5.1 bp, 51%, n 259 | +0.7 bp, 54%, n 254 | +0.4 bp, 52%, n 111 | +0.9 bp, 57%, n 272 | +1.4 bp, 52%, n 283 | -7.5 bp, 50%, n 283 |
| fcf_trend | +0.1 bp, 48%, n 296 | +0.4 bp, 55%, n 367 | +1.0 bp, 54%, n 397 | +6.4 bp, 52%, n 397 | -2.3 bp, 51%, n 397 | +0.8 bp, 54%, n 281 | +0.4 bp, 49%, n 334 | +1.4 bp, 55%, n 394 | +8.2 bp, 54%, n 394 | +1.0 bp, 53%, n 394 | +0.2 bp, 51%, n 330 | -0.5 bp, 50%, n 177 | +0.6 bp, 57%, n 361 | +5.7 bp, 52%, n 374 | +0.8 bp, 52%, n 374 |
| market | +2.5 bp, 52%, n 240 | +2.6 bp, 57%, n 284 | +2.6 bp, 56%, n 306 | +12.8 bp, 61%, n 306 | +2.9 bp, 54%, n 306 | +3.1 bp, 60%, n 240 | +2.5 bp, 55%, n 256 | +2.7 bp, 58%, n 298 | +14.4 bp, 60%, n 298 | +5.0 bp, 54%, n 298 | +0.5 bp, 53%, n 266 | -0.8 bp, 50%, n 129 | +0.6 bp, 57%, n 288 | +11.4 bp, 58%, n 297 | +5.7 bp, 55%, n 297 |
| ai_demand | +2.3 bp, 53%, n 222 | +3.8 bp, 57%, n 244 | +5.3 bp, 58%, n 258 | +14.5 bp, 58%, n 258 | +10.0 bp, 54%, n 258 | +2.4 bp, 58%, n 224 | +3.5 bp, 57%, n 224 | +4.4 bp, 61%, n 259 | +15.2 bp, 57%, n 259 | +12.5 bp, 55%, n 259 | +1.0 bp, 54%, n 251 | +2.2 bp, 58%, n 126 | +1.9 bp, 59%, n 268 | +12.8 bp, 55%, n 272 | +12.3 bp, 54%, n 272 |

**Best cell:** results_vs_prior_guidance; 5 min after the stamp, to the next 09:35: +16.7 bp, t +3.54, right on 61% of 294. **Family p = 0.0925** -> **does not pass**.

Checks on the best cell:
- net of cost: 14.7
- four periods (mean bp; n): [[13.9, 74], [13.0, 74], [28.2, 73], [12.0, 73]]
- without the ten largest moves: 15.3
- score size: |score| 0.5+ vs below (mean bp; n): [[17.0, 198], [16.1, 96]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 334, "mean": -1.7, "t": -0.75}

## F2. Results releases (US filers) -> the company's OWN stock, extended hours included. From May 2018.

Observations: 384.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 1 min after the stamp, to the next 09:35 | 1 min after the stamp, to the next 16:00 | 5 min after the stamp, hold 15 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | 5 min after the stamp, to the next 16:00 | 15 min after the stamp, hold 15 min | 15 min after the stamp, hold 30 min | 15 min after the stamp, hold 60 min | 15 min after the stamp, to the next 09:35 | 15 min after the stamp, to the next 16:00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | +43.5 bp, 57%, n 369 | +51.2 bp, 58%, n 369 | +64.9 bp, 58%, n 365 | +62.0 bp, 56%, n 370 | +25.3 bp, 53%, n 369 | +20.6 bp, 54%, n 369 | +32.4 bp, 57%, n 370 | +40.8 bp, 54%, n 366 | +36.8 bp, 54%, n 371 | -0.1 bp, 51%, n 372 | +9.1 bp, 50%, n 369 | +15.1 bp, 51%, n 368 | +25.0 bp, 56%, n 365 | +19.9 bp, 54%, n 369 | -16.5 bp, 48%, n 370 |
| results_vs_prior_guidance | +42.7 bp, 58%, n 276 | +57.8 bp, 57%, n 277 | +56.1 bp, 56%, n 273 | +17.7 bp, 51%, n 276 | -4.3 bp, 49%, n 275 | +19.4 bp, 55%, n 276 | +31.3 bp, 55%, n 277 | +18.3 bp, 51%, n 273 | -12.2 bp, 52%, n 277 | -35.9 bp, 50%, n 278 | +14.9 bp, 52%, n 276 | +19.1 bp, 53%, n 275 | +0.6 bp, 52%, n 273 | -20.3 bp, 49%, n 275 | -46.6 bp, 45%, n 276 |
| guidance_change | +30.0 bp, 55%, n 253 | +37.5 bp, 57%, n 254 | +52.1 bp, 57%, n 251 | +47.7 bp, 54%, n 254 | +14.4 bp, 53%, n 253 | +14.3 bp, 53%, n 253 | +24.2 bp, 55%, n 253 | +36.0 bp, 53%, n 251 | +27.7 bp, 52%, n 254 | -4.5 bp, 53%, n 255 | +9.8 bp, 49%, n 253 | +15.0 bp, 51%, n 252 | +32.0 bp, 55%, n 251 | +20.4 bp, 53%, n 253 | -15.8 bp, 50%, n 254 |
| fcf_trend | +26.6 bp, 50%, n 361 | +25.2 bp, 51%, n 362 | +27.3 bp, 51%, n 357 | +34.1 bp, 55%, n 362 | +1.9 bp, 52%, n 361 | +13.2 bp, 52%, n 361 | +15.6 bp, 53%, n 361 | +9.0 bp, 48%, n 358 | +22.8 bp, 55%, n 362 | -9.9 bp, 51%, n 363 | +4.7 bp, 50%, n 361 | +15.9 bp, 51%, n 360 | -1.3 bp, 51%, n 356 | +13.0 bp, 53%, n 360 | -20.1 bp, 50%, n 361 |
| market | +55.0 bp, 58%, n 329 | +62.1 bp, 59%, n 329 | +72.8 bp, 58%, n 325 | +63.2 bp, 56%, n 329 | +30.5 bp, 53%, n 328 | +27.0 bp, 56%, n 329 | **+41.4 bp, 58%, n 330** | +47.6 bp, 56%, n 326 | +34.3 bp, 56%, n 330 | +1.3 bp, 53%, n 331 | +8.5 bp, 50%, n 329 | +18.8 bp, 51%, n 329 | +22.8 bp, 56%, n 325 | +9.6 bp, 56%, n 329 | -23.6 bp, 48%, n 330 |
| ai_demand | +28.5 bp, 53%, n 306 | +34.1 bp, 54%, n 307 | +34.0 bp, 51%, n 303 | -13.2 bp, 50%, n 307 | -28.8 bp, 50%, n 306 | -1.6 bp, 50%, n 306 | +9.2 bp, 52%, n 306 | +2.9 bp, 49%, n 304 | -41.0 bp, 49%, n 307 | -57.0 bp, 48%, n 308 | +2.7 bp, 50%, n 306 | +9.6 bp, 52%, n 307 | -2.5 bp, 50%, n 303 | -42.8 bp, 51%, n 306 | -59.5 bp, 45%, n 307 |

**Best cell:** market; 5 min after the stamp, hold 30 min: +41.4 bp, t +3.72, right on 58% of 330. **Family p = 0.0100** -> **does not pass**.

Checks on the best cell:
- net of cost: 31.4
- four periods (mean bp; n): [[48.5, 83], [33.0, 83], [61.1, 82], [23.1, 82]]
- without the ten largest moves: 24.0
- score size: |score| 0.5+ vs below (mean bp; n): [[60.2, 61], [37.1, 269]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 329, "mean": 55.0, "t": 2.89}
- price-only rule at the same cell (follow the move so far): {"n": 379, "mean": 2.4, "t": 0.23}
- score rule when the move so far AGREES with the score / DISAGREES: [{"n": 190, "mean": 37.3}, {"n": 139, "mean": 47.3}]

## F3. Results releases -> the OTHER listed companies the reader named as affected. `direction` = the reader's sign for that company; `reporter_own` = simply copy the reporter's own sign (the 'everything moves together' rule).

Observations: 1588. Unit = one event (its named companies averaged); each window's average return removed first.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 1 min after the stamp, to the next 09:35 | 1 min after the stamp, to the next 16:00 | 5 min after the stamp, hold 15 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | 5 min after the stamp, to the next 16:00 | 15 min after the stamp, hold 15 min | 15 min after the stamp, hold 30 min | 15 min after the stamp, hold 60 min | 15 min after the stamp, to the next 09:35 | 15 min after the stamp, to the next 16:00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | +1.6 bp, 51%, n 358 | +2.4 bp, 51%, n 358 | +2.8 bp, 54%, n 353 | +1.5 bp, 52%, n 360 | -9.9 bp, 49%, n 360 | +1.0 bp, 47%, n 358 | +1.8 bp, 46%, n 357 | +3.7 bp, 51%, n 351 | -0.0 bp, 49%, n 359 | -11.3 bp, 50%, n 359 | +0.4 bp, 48%, n 354 | +0.6 bp, 44%, n 356 | +3.5 bp, 51%, n 350 | +1.1 bp, 50%, n 358 | -9.4 bp, 52%, n 358 |
| reporter_own | **+6.0 bp, 56%, n 353** | +6.6 bp, 48%, n 353 | +8.2 bp, 55%, n 349 | -2.6 bp, 50%, n 355 | -21.0 bp, 49%, n 355 | +2.1 bp, 50%, n 353 | +0.6 bp, 45%, n 352 | +3.2 bp, 52%, n 347 | -8.7 bp, 48%, n 354 | -26.3 bp, 49%, n 354 | +1.1 bp, 46%, n 349 | -1.5 bp, 42%, n 351 | +1.8 bp, 55%, n 346 | -8.5 bp, 50%, n 353 | -27.4 bp, 48%, n 353 |

**Best cell:** reporter_own; 1 min after the stamp, hold 15 min: +6.0 bp, t +2.33, right on 56% of 353. **Family p = 0.2480** -> **does not pass**.

Checks on the best cell:
- net of cost: -2.6
- four periods (mean bp; n): [[2.4, 348], [11.4, 348], [15.4, 347], [0.6, 347]]
- without the ten largest moves: 6.8
- score size: |score| 0.5+ vs below (mean bp; n): [[9.1, 911], [4.3, 479]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 1451, "mean": 21.1, "t": 1.0}

## F4. Other company events (US filers, material 0.2+ / 0.3+ / 0.5+) -> the company's OWN stock. `neg_uncertainty` = sell when the event raises uncertainty. From May 2018.

Observations: 277.

| signal | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|
| own_stock | material 0.2+ | +5.2 bp, 51%, n 184 | +1.7 bp, 50%, n 177 | +15.2 bp, 51%, n 196 | +12.2 bp, 55%, n 244 | +12.1 bp, 54%, n 245 | +5.4 bp, 51%, n 245 | +18.6 bp, 53%, n 244 |
| own_stock | material 0.3+ | +4.4 bp, 52%, n 147 | +5.2 bp, 52%, n 141 | +18.8 bp, 50%, n 157 | +17.4 bp, 58%, n 186 | +19.7 bp, 57%, n 186 | +15.3 bp, 52%, n 186 | +17.9 bp, 55%, n 186 |
| own_stock | material 0.5+ | +14.4 bp, 51%, n 68 | +20.2 bp, 52%, n 67 | +25.8 bp, 51%, n 71 | +22.1 bp, 57%, n 81 | +26.7 bp, 58%, n 81 | +13.7 bp, 51%, n 81 | +33.0 bp, 60%, n 81 |
| fcf_outlook | material 0.2+ | +0.1 bp, 45%, n 177 | +7.7 bp, 52%, n 169 | +10.4 bp, 47%, n 193 | +19.7 bp, 56%, n 238 | **+22.6 bp, 58%, n 238** | +24.4 bp, 53%, n 238 | +29.6 bp, 51%, n 238 |
| fcf_outlook | material 0.3+ | -1.1 bp, 45%, n 140 | +10.5 bp, 51%, n 133 | +12.8 bp, 46%, n 151 | +21.1 bp, 55%, n 179 | +21.7 bp, 55%, n 179 | +17.6 bp, 51%, n 179 | +12.6 bp, 50%, n 179 |
| fcf_outlook | material 0.5+ | +11.7 bp, 47%, n 66 | +21.5 bp, 49%, n 65 | +38.5 bp, 54%, n 69 | +31.7 bp, 56%, n 79 | +35.4 bp, 57%, n 79 | +18.4 bp, 48%, n 79 | +24.4 bp, 57%, n 79 |
| neg_uncertainty | material 0.2+ | +5.9 bp, 46%, n 207 | +2.0 bp, 49%, n 197 | +4.8 bp, 46%, n 220 | +13.3 bp, 53%, n 272 | +8.3 bp, 52%, n 273 | +5.1 bp, 49%, n 273 | +4.5 bp, 50%, n 272 |
| neg_uncertainty | material 0.3+ | +6.7 bp, 47%, n 155 | +4.3 bp, 49%, n 148 | +12.2 bp, 46%, n 166 | +12.4 bp, 53%, n 196 | +5.9 bp, 49%, n 196 | +0.9 bp, 49%, n 196 | -14.1 bp, 48%, n 196 |
| neg_uncertainty | material 0.5+ | +15.7 bp, 44%, n 68 | +4.4 bp, 48%, n 67 | +10.5 bp, 42%, n 71 | +22.3 bp, 56%, n 81 | +12.8 bp, 49%, n 81 | +18.5 bp, 52%, n 81 | -17.7 bp, 52%, n 81 |

**Best cell:** fcf_outlook | material 0.2+; next regular session, hold 60 min: +22.6 bp, t +2.42, right on 58% of 238. **Family p = 0.3605** -> **does not pass**.

Checks on the best cell:
- net of cost: 12.6
- four periods (mean bp; n): [[18.4, 60], [9.1, 60], [21.5, 59], [41.7, 59]]
- without the ten largest moves: 16.3
- score size: |score| 0.5+ vs below (mean bp; n): [[-8.7, 18], [25.2, 220]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 188, "mean": 9.6, "t": 0.75}

## F5. Other company events (material 0.3+) -> the OTHER listed companies named as affected.

Observations: 493. Unit = one event (its named companies averaged); each window's average return removed first.

| signal | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|
| direction | +3.7 bp, 49%, n 134 | +7.3 bp, 53%, n 129 | +7.9 bp, 51%, n 138 | -7.1 bp, 45%, n 151 | -10.2 bp, 47%, n 151 | -5.9 bp, 50%, n 151 | +10.2 bp, 53%, n 150 |
| reporter_own | +0.4 bp, 53%, n 133 | -4.6 bp, 42%, n 128 | +16.7 bp, 53%, n 136 | +4.4 bp, 55%, n 149 | +8.9 bp, 48%, n 149 | **+22.3 bp, 55%, n 149** | +19.3 bp, 55%, n 148 |

**Best cell:** reporter_own; next regular session, to the next 16:00: +22.3 bp, t +1.72, right on 55% of 149. **Family p = 0.6280** -> **does not pass**.

Checks on the best cell:
- net of cost: 6.0
- four periods (mean bp; n): [[-9.7, 113], [24.1, 113], [17.3, 112], [32.4, 112]]
- without the ten largest moves: 19.2
- score size: |score| 0.5+ vs below (mean bp; n): [[5.5, 102], [19.0, 348]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 388, "mean": -2.7, "t": -0.83}

## F6. Other company events (US filers, material 0.3+ / 0.5+) -> the Nasdaq-100 future. From June 2010.

Observations: 360.

| signal | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 |
|---|---|---|---|---|---|
| market | material 0.3+ | -3.8 bp, 54%, n 70 | -5.9 bp, 54%, n 52 | +4.6 bp, 53%, n 144 | +2.2 bp, 51%, n 144 | +13.8 bp, 62%, n 139 |
| market | material 0.5+ | -6.6 bp, 53%, n 45 | -6.3 bp, 56%, n 36 | -0.8 bp, 52%, n 89 | -1.3 bp, 51%, n 89 | -3.2 bp, 59%, n 86 |
| own_stock | material 0.3+ | -1.3 bp, 53%, n 159 | **-8.7 bp, 48%, n 102** | +0.9 bp, 50%, n 334 | +0.5 bp, 50%, n 333 | +2.2 bp, 52%, n 327 |
| own_stock | material 0.5+ | -3.0 bp, 53%, n 66 | -8.2 bp, 52%, n 52 | +3.6 bp, 55%, n 130 | +3.6 bp, 53%, n 130 | +10.7 bp, 58%, n 127 |

**Best cell:** own_stock | material 0.3+; 5 min after the stamp, hold 60 min: -8.7 bp, t -1.92, right on 48% of 102. **Family p = 0.4980** -> **does not pass**.

Checks on the best cell:
- net of cost: -10.7
- four periods (mean bp; n): [[-14.0, 26], [1.2, 26], [-14.3, 25], [-7.8, 25]]
- without the ten largest moves: 0.4
- score size: |score| 0.5+ vs below (mean bp; n): [[0.1, 15], [-10.2, 87]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 203, "mean": -2.3, "t": -1.23}

## F7. Foreign filers (TSMC; SK Hynix once its prices are on disk): results, monthly revenue and material events -> own stock, entered at the next regular session because the SEC stamp can be hours after the release in Asia. From May 2018.

Observations: 99.

| signal | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|
| own_stock | +6.1 bp, 53%, n 83 | +6.8 bp, 49%, n 83 | **-17.4 bp, 43%, n 83** | -21.7 bp, 46%, n 82 |

**Best cell:** own_stock; next regular session, to the next 16:00: -17.4 bp, t -1.03, right on 43% of 83. **Family p = 0.5650** -> **does not pass**.

Checks on the best cell:
- net of cost: -27.4
- four periods (mean bp; n): [[-22.9, 21], [-9.1, 21], [-1.7, 21], [-37.0, 20]]
- without the ten largest moves: -18.0
- score size: |score| 0.5+ vs below (mean bp; n): [[-36.5, 28], [-7.7, 55]]
- before the stamp (the 30 minutes ending 5 minutes before it; should be near 0): {"n": 55, "mean": 1.8, "t": 0.32}

