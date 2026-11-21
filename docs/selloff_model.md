# Sell-off study, stage C: how likely is a rebound or a further slide after THIS sell-off?

Registered in TRACK 3.94 before running. **Founder's definitions:** REBOUND = each of the next 2 sessions closes above its own open; FURTHER SLIDE = each of the next 2 sessions closes below its own open; anything else is MIXED. For every year the model is trained only on sell-offs of earlier years and gives each sell-off of that year two probabilities. 'Always quote history' = the frequency seen in those earlier years, the same number for every sell-off. **Skill** = how much smaller the model's error is than that of always quoting history (0% = no better; error = the squared gap between the probability given and what happened). Its range and p come from resampling whole months 2000 times (all sell-offs of one calendar month are one piece of evidence, because neighbouring days move together); p = how often the model was no better than history. 16 tests, so skill counts at p < 0.0031. **The probability is usable only if** skill passes AND, among the sell-offs where the model said at least 10% points above history, the event really happened at least 5 points more often than history, in 20 or more separate months. Price moves are the price itself (not against the market), in bp: 100 bp = 1%.

## stocks; 1 session, -5% or worse

7028 sell-offs in 262 separate months; predicted out of sample from 2009: 5309 sell-offs on 1663 days, 214 months. What happened: REBOUND 23%, FURTHER SLIDE 26%, MIXED 51%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +330 bp | +520 bp | +565 bp | +534 bp | +510 bp | +676 bp |
| SLIDE | -229 bp | -469 bp | -444 bp | -364 bp | -259 bp | -227 bp |
| MIXED | +65 bp | +33 bp | +68 bp | +118 bp | +149 bp | +183 bp |

### Probability of a REBOUND

**Skill -0.9%** (range -1.7% to -0.2%; p 0.9825; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high share of large stocks down 3%+ that day; less likely with high S&P 500 against its 200-day average %; less likely with high other company filing in the window; less likely with high the S&P 500 over the same sessions %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 551 | 125 | 11% | 19% |
| 15% to 25% | 2851 | 211 | 21% | 24% |
| 25% to 35% | 1813 | 134 | 27% | 22% |
| 35% to 45% | 94 | 8 | 37% | 10% |

Where the model said at least 10% points above history: 293 sell-offs in 25 separate months; it said 34%, history said 21%, it happened 18%. Price after: +1: +150 bp, +2: +51 bp, +3: +262 bp, +5: +463 bp, +7: +556 bp, +10: +485 bp.

### Probability of a FURTHER SLIDE

**Skill -0.2%** (range -1.1% to +0.7%; p 0.6190; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high gap at the open %; more likely with high last day's move %; less likely with high distance below the one-year high %; less likely with high VIX change over the same sessions %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 220 | 34 | 14% | 9% |
| 15% to 25% | 3648 | 205 | 21% | 25% |
| 25% to 35% | 1288 | 206 | 29% | 27% |
| 35% to 45% | 152 | 92 | 37% | 31% |
| 45% to 100% | 1 | 1 | 45% | 100% |

Where the model said at least 10% points above history: 106 sell-offs in 70 separate months; it said 38%, history said 26%, it happened 33%. Price after: +1: -87 bp, +2: -78 bp, +3: -84 bp, +5: -141 bp, +7: -165 bp, +10: -79 bp.

## stocks; 1 session, -7% or worse

2786 sell-offs in 247 separate months; predicted out of sample from 2009: 2025 sell-offs on 851 days, 203 months. What happened: REBOUND 23%, FURTHER SLIDE 27%, MIXED 49%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +465 bp | +587 bp | +658 bp | +561 bp | +531 bp | +808 bp |
| SLIDE | -243 bp | -571 bp | -560 bp | -471 bp | -336 bp | -218 bp |
| MIXED | +124 bp | +39 bp | +96 bp | +149 bp | +183 bp | +244 bp |

### Probability of a REBOUND

**Skill -1.6%** (range -3.0% to -0.2%; p 0.9695; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high share of large stocks down 3%+ that day; less likely with high S&P 500 against its 200-day average %; less likely with high the S&P 500 over the same sessions %; less likely with high where it closed in the day's range.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 259 | 98 | 12% | 20% |
| 15% to 25% | 1006 | 187 | 20% | 23% |
| 25% to 35% | 682 | 105 | 28% | 29% |
| 35% to 45% | 76 | 13 | 38% | 2% |
| 45% to 100% | 2 | 2 | 51% | 0% |

Where the model said at least 10% points above history: 171 sell-offs in 27 separate months; it said 35%, history said 21%, it happened 19%. Price after: +1: +377 bp, +2: +25 bp, +3: +312 bp, +5: +388 bp, +7: +519 bp, +10: +665 bp.

### Probability of a FURTHER SLIDE

**Skill -1.1%** (range -3.0% to +0.8%; p 0.8450; bar 0.0031) -> **no better than always quoting history**. In the latest model: more likely with high the S&P 500 over the same sessions %; less likely with high size in units of its own usual move; less likely with high gap at the open %; more likely with high last day's move %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 167 | 32 | 12% | 19% |
| 15% to 25% | 1176 | 155 | 21% | 28% |
| 25% to 35% | 571 | 171 | 30% | 27% |
| 35% to 45% | 108 | 70 | 39% | 33% |
| 45% to 100% | 3 | 3 | 47% | 0% |

Where the model said at least 10% points above history: 72 sell-offs in 50 separate months; it said 40%, history said 27%, it happened 26%. Price after: +1: -15 bp, +2: +39 bp, +3: +66 bp, +5: +35 bp, +7: +3 bp, +10: +2 bp.

## stocks; 1 session, -10% or worse

955 sell-offs in 179 separate months; predicted out of sample from 2011: 515 sell-offs on 277 days, 131 months. What happened: REBOUND 21%, FURTHER SLIDE 30%, MIXED 49%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +616 bp | +537 bp | +620 bp | +422 bp | +494 bp | +1018 bp |
| SLIDE | -212 bp | -587 bp | -592 bp | -555 bp | -435 bp | -325 bp |
| MIXED | +228 bp | -46 bp | +14 bp | +115 bp | +166 bp | +294 bp |

### Probability of a REBOUND

**Skill -2.6%** (range -5.2% to +0.2%; p 0.9425; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high the S&P 500 over the same sessions %; more likely with high volume against normal; more likely with high run-up over the 60 sessions before %; less likely with high S&P 500 against its 200-day average %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 110 | 70 | 13% | 22% |
| 15% to 25% | 339 | 98 | 19% | 23% |
| 25% to 35% | 50 | 18 | 28% | 14% |
| 35% to 45% | 16 | 5 | 37% | 3% |

Where the model said at least 10% points above history: 37 sell-offs in 12 separate months; it said 33%, history said 19%, it happened 22%. Price after: +1: +532 bp, +2: -23 bp, +3: +85 bp, +5: +83 bp, +7: +340 bp, +10: +600 bp.

### Probability of a FURTHER SLIDE

**Skill -5.7%** (range -9.8% to -1.6%; p 0.9905; bar 0.0031) -> **no better than always quoting history**. In the latest model: more likely with high the S&P 500 over the same sessions %; less likely with high volume against normal; less likely with high size in units of its own usual move; less likely with high run-up over the 60 sessions before %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 13 | 9 | 14% | 72% |
| 15% to 25% | 295 | 70 | 21% | 27% |
| 25% to 35% | 160 | 84 | 31% | 33% |
| 35% to 45% | 42 | 37 | 38% | 20% |
| 45% to 100% | 5 | 5 | 48% | 20% |

Where the model said at least 10% points above history: 21 sell-offs in 18 separate months; it said 42%, history said 28%, it happened 19%. Price after: +1: -49 bp, +2: -42 bp, +3: -12 bp, +5: +244 bp, +7: +153 bp, +10: +80 bp.

## stocks; 5 sessions, -10% or worse

3525 sell-offs in 250 separate months; predicted out of sample from 2009: 2700 sell-offs on 1032 days, 207 months. What happened: REBOUND 22%, FURTHER SLIDE 25%, MIXED 53%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +290 bp | +515 bp | +514 bp | +494 bp | +477 bp | +592 bp |
| SLIDE | -201 bp | -422 bp | -399 bp | -349 bp | -252 bp | -229 bp |
| MIXED | +79 bp | +82 bp | +104 bp | +166 bp | +186 bp | +177 bp |

### Probability of a REBOUND

**Skill -1.7%** (range -2.7% to -0.7%; p 0.9970; bar 0.0031) -> **no better than always quoting history**. In the latest model: more likely with high the S&P 500 over the same sessions %; more likely with high share of large stocks down 3%+ that day; more likely with high gap at the open %; less likely with high other company filing in the window.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 207 | 71 | 12% | 17% |
| 15% to 25% | 1797 | 193 | 20% | 22% |
| 25% to 35% | 550 | 101 | 28% | 23% |
| 35% to 45% | 112 | 20 | 39% | 20% |
| 45% to 100% | 34 | 6 | 47% | 12% |

Where the model said at least 10% points above history: 289 sell-offs in 32 separate months; it said 37%, history said 22%, it happened 19%. Price after: +1: +38 bp, +2: +120 bp, +3: +154 bp, +5: +196 bp, +7: +17 bp, +10: -106 bp.

### Probability of a FURTHER SLIDE

**Skill -1.6%** (range -2.8% to -0.6%; p 0.9935; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high VIX change over the same sessions %; less likely with high the S&P 500 over the same sessions %; less likely with high VIX level; more likely with high other company filing in the window.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 249 | 59 | 13% | 19% |
| 15% to 25% | 1684 | 187 | 20% | 26% |
| 25% to 35% | 716 | 153 | 29% | 25% |
| 35% to 45% | 50 | 24 | 38% | 25% |
| 45% to 100% | 1 | 1 | 45% | 0% |

Where the model said at least 10% points above history: 75 sell-offs in 33 separate months; it said 36%, history said 23%, it happened 26%. Price after: +1: +136 bp, +2: +55 bp, +3: +141 bp, +5: +427 bp, +7: +582 bp, +10: +612 bp.

## stocks; 10 sessions, -15% or worse

1528 sell-offs in 199 separate months; predicted out of sample from 2010: 992 sell-offs on 513 days, 152 months. What happened: REBOUND 26%, FURTHER SLIDE 27%, MIXED 47%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +326 bp | +509 bp | +501 bp | +507 bp | +403 bp | +563 bp |
| SLIDE | -152 bp | -428 bp | -375 bp | -333 bp | -308 bp | -266 bp |
| MIXED | +117 bp | +65 bp | +206 bp | +183 bp | +155 bp | +173 bp |

### Probability of a REBOUND

**Skill -1.8%** (range -3.3% to -0.3%; p 0.9830; bar 0.0031) -> **no better than always quoting history**. In the latest model: more likely with high distance below the one-year high %; less likely with high VIX change over the same sessions %; more likely with high gap at the open %; less likely with high last day's move %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 139 | 37 | 13% | 12% |
| 15% to 25% | 643 | 129 | 20% | 29% |
| 25% to 35% | 208 | 79 | 28% | 23% |
| 35% to 45% | 2 | 2 | 37% | 0% |

Where the model said at least 10% points above history: 12 sell-offs in 10 separate months; it said 33%, history said 21%, it happened 11%. Price after: +1: -9 bp, +2: -115 bp, +3: -146 bp, +5: +81 bp, +7: -10 bp, +10: +92 bp.

### Probability of a FURTHER SLIDE

**Skill -2.6%** (range -4.4% to -0.8%; p 0.9910; bar 0.0031) -> **no better than always quoting history**. In the latest model: more likely with high last day's move %; less likely with high S&P 500 against its 200-day average %; less likely with high gap at the open %; less likely with high distance below the one-year high %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 11 | 9 | 13% | 46% |
| 15% to 25% | 359 | 95 | 22% | 30% |
| 25% to 35% | 582 | 132 | 29% | 25% |
| 35% to 45% | 39 | 24 | 38% | 23% |
| 45% to 100% | 1 | 1 | 48% | 0% |

Where the model said at least 10% points above history: 19 sell-offs in 9 separate months; it said 41%, history said 28%, it happened 17%. Price after: +1: +149 bp, +2: +207 bp, +3: +319 bp, +5: +561 bp, +7: +480 bp, +10: +263 bp.

## indices and sectors; 1 session, -3% or worse

2708 sell-offs in 240 separate months; predicted out of sample from 2004: 2059 sell-offs on 610 days, 193 months. What happened: REBOUND 24%, FURTHER SLIDE 23%, MIXED 53%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +208 bp | +356 bp | +378 bp | +342 bp | +287 bp | +365 bp |
| SLIDE | -140 bp | -302 bp | -303 bp | -260 bp | -180 bp | -274 bp |
| MIXED | +35 bp | +19 bp | +11 bp | +71 bp | +54 bp | +67 bp |

### Probability of a REBOUND

**Skill -2.3%** (range -3.8% to -0.8%; p 0.9940; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high the S&P 500 over the same sessions %; less likely with high share of large stocks down 3%+ that day; more likely with high run-up over the 60 sessions before %; more likely with high volume against normal.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 41 | 27 | 14% | 25% |
| 15% to 25% | 938 | 167 | 21% | 25% |
| 25% to 35% | 711 | 103 | 28% | 23% |
| 35% to 45% | 293 | 24 | 39% | 18% |
| 45% to 100% | 76 | 7 | 49% | 37% |

Where the model said at least 10% points above history: 453 sell-offs in 36 separate months; it said 38%, history said 23%, it happened 27%. Price after: +1: +148 bp, +2: +57 bp, +3: +15 bp, +5: -8 bp, +7: -69 bp, +10: -113 bp.

### Probability of a FURTHER SLIDE

**Skill -0.7%** (range -2.0% to +0.7%; p 0.7795; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high VIX level; less likely with high gap at the open %; less likely with high last day's move %; less likely with high VIX change over the same sessions %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 525 | 41 | 13% | 17% |
| 15% to 25% | 1323 | 161 | 20% | 24% |
| 25% to 35% | 203 | 84 | 28% | 23% |
| 35% to 45% | 8 | 8 | 37% | 11% |

Where the model said at least 10% points above history: 26 sell-offs in 19 separate months; it said 34%, history said 22%, it happened 38%. Price after: +1: +8 bp, +2: +47 bp, +3: +93 bp, +5: +207 bp, +7: +144 bp, +10: +200 bp.

## indices and sectors; 1 session, -4% or worse

1258 sell-offs in 164 separate months; predicted out of sample from 2005: 955 sell-offs on 285 days, 119 months. What happened: REBOUND 24%, FURTHER SLIDE 23%, MIXED 53%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +298 bp | +448 bp | +467 bp | +452 bp | +374 bp | +462 bp |
| SLIDE | -145 bp | -353 bp | -385 bp | -350 bp | -227 bp | -379 bp |
| MIXED | +47 bp | +21 bp | +22 bp | +85 bp | +68 bp | +79 bp |

### Probability of a REBOUND

**Skill -4.2%** (range -7.6% to -0.6%; p 0.9730; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high the S&P 500 over the same sessions %; less likely with high share of large stocks down 3%+ that day; more likely with high volume against normal; less likely with high where it closed in the day's range.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 13 | 9 | 13% | 0% |
| 15% to 25% | 206 | 80 | 21% | 28% |
| 25% to 35% | 428 | 79 | 29% | 23% |
| 35% to 45% | 147 | 26 | 39% | 20% |
| 45% to 100% | 161 | 10 | 52% | 26% |

Where the model said at least 10% points above history: 304 sell-offs in 28 separate months; it said 44%, history said 25%, it happened 23%. Price after: +1: +142 bp, +2: +24 bp, +3: -19 bp, +5: -25 bp, +7: -69 bp, +10: -147 bp.

### Probability of a FURTHER SLIDE

**Skill -0.8%** (range -4.3% to +2.5%; p 0.6535; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high S&P 500 against its 200-day average %; less likely with high gap at the open %; less likely with high VIX level; more likely with high the S&P 500 over the same sessions %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 292 | 49 | 11% | 20% |
| 15% to 25% | 433 | 85 | 20% | 21% |
| 25% to 35% | 194 | 47 | 29% | 27% |
| 35% to 45% | 27 | 9 | 39% | 30% |
| 45% to 100% | 9 | 1 | 53% | 14% |

Where the model said at least 10% points above history: 73 sell-offs in 18 separate months; it said 36%, history said 22%, it happened 30%. Price after: +1: +121 bp, +2: +258 bp, +3: +185 bp, +5: +286 bp, +7: +317 bp, +10: +360 bp.

## indices and sectors; 5 sessions, -7% or worse

906 sell-offs in 159 separate months; predicted out of sample from 2009: 503 sell-offs on 215 days, 89 months. What happened: REBOUND 27%, FURTHER SLIDE 23%, MIXED 50%.

What each outcome meant for the price (average change from the sell-off day's close):

| outcome | +1 | +2 | +3 | +5 | +7 | +10 |
|---|---|---|---|---|---|---|
| REBOUND | +226 bp | +394 bp | +390 bp | +353 bp | +386 bp | +503 bp |
| SLIDE | -123 bp | -314 bp | -268 bp | -168 bp | -169 bp | -321 bp |
| MIXED | +40 bp | +65 bp | +47 bp | +120 bp | +171 bp | +125 bp |

### Probability of a REBOUND

**Skill -3.7%** (range -8.2% to +0.3%; p 0.9355; bar 0.0031) -> **no better than always quoting history**. In the latest model: less likely with high last day's move %; less likely with high VIX level; more likely with high gap at the open %; more likely with high distance below the one-year high %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 26 | 14 | 12% | 20% |
| 15% to 25% | 122 | 44 | 21% | 30% |
| 25% to 35% | 239 | 66 | 30% | 27% |
| 35% to 45% | 93 | 31 | 39% | 25% |
| 45% to 100% | 23 | 9 | 47% | 19% |

Where the model said at least 10% points above history: 83 sell-offs in 28 separate months; it said 42%, history said 27%, it happened 22%. Price after: +1: +57 bp, +2: -63 bp, +3: -44 bp, +5: +2 bp, +7: +20 bp, +10: -184 bp.

### Probability of a FURTHER SLIDE

**Skill +0.0%** (range -3.8% to +4.0%; p 0.5005; bar 0.0031) -> **no better than always quoting history**. In the latest model: more likely with high last day's move %; less likely with high S&P 500 against its 200-day average %; less likely with high size in units of its own usual move; less likely with high VIX change over the same sessions %.

| the model said | sell-offs | separate months | average said | actually happened |
|---|---|---|---|---|
| 0% to 15% | 244 | 60 | 11% | 19% |
| 15% to 25% | 216 | 55 | 19% | 25% |
| 25% to 35% | 38 | 16 | 29% | 33% |
| 35% to 45% | 5 | 3 | 37% | 36% |

Where the model said at least 10% points above history: 13 sell-offs in 7 separate months; it said 33%, history said 19%, it happened 46%. Price after: +1: -291 bp, +2: +200 bp, +3: +26 bp, +5: +299 bp, +7: +361 bp, +10: +302 bp.

