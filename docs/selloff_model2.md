# Sell-off study, stage C2: is the price HIGHER a few sessions after the sell-off?

Registered in TRACK 3.95 before running. Outcome: the close of session +h is above the sell-off day's close ('price'), or -- stocks only -- the stock did better than the S&P 500 over those sessions. h = 1, 2, 3, 5, 7, 10, each on its own. Same conditions, same year-by-year training on earlier years only, same check as stage C. Skill = how much smaller the model's error is than that of always quoting the historical frequency; range and p from resampling whole calendar months 2000 times. 78 tests, so skill counts at p < 0.00064. **Usable only if** skill passes AND where the model said at least 10% points above (or below) history the outcome was at least 5 points more (or less) frequent than history, in 20 or more separate months.

| sell-off | outcome | after | predicted sell-offs (months) | happened | skill (range) | p | said 10+ points ABOVE history: said / history / happened (months); price after | said 10+ points BELOW history: said / history / happened (months); price after | verdict |
|---|---|---|---|---|---|---|---|---|---|
| stocks; 1 session, -5% or worse | price | +1 | 5312 (214) | 51% | +0.2% (-1.0% to +1.3%) | 0.3960 | 62% / 49% / 59% (87); +70 bp | 35% / 49% / 43% (153); -28 bp | no better than history |
| stocks; 1 session, -5% or worse | price | +2 | 5309 (214) | 50% | -0.5% (-1.6% to +0.6%) | 0.7550 | 63% / 50% / 57% (59); +176 bp | 35% / 50% / 43% (140); -74 bp | no better than history |
| stocks; 1 session, -5% or worse | price | +3 | 5307 (214) | 49% | -0.9% (-1.9% to +0.2%) | 0.9165 | 64% / 50% / 58% (66); +176 bp | 33% / 50% / 46% (83); +24 bp | no better than history |
| stocks; 1 session, -5% or worse | price | +5 | 5297 (214) | 50% | -0.6% (-1.8% to +0.5%) | 0.8370 | 65% / 50% / 63% (71); +200 bp | 35% / 50% / 47% (127); -7 bp | no better than history |
| stocks; 1 session, -5% or worse | price | +7 | 5294 (214) | 52% | -1.0% (-2.2% to +0.2%) | 0.9110 | 66% / 50% / 53% (39); +160 bp | 37% / 51% / 52% (123); +21 bp | no better than history |
| stocks; 1 session, -5% or worse | price | +10 | 5293 (214) | 54% | -1.8% (-3.3% to -0.5%) | 0.9860 | 63% / 48% / 52% (16); +529 bp | 32% / 49% / 52% (68); +67 bp | no better than history |
| stocks; 1 session, -5% or worse | against the S&P 500 | +1 | 5312 (214) | 50% | +0.7% (-0.4% to +2.0%) | 0.1600 | 64% / 49% / 53% (84); +21 bp | 35% / 50% / 40% (163); -43 bp | no better than history |
| stocks; 1 session, -5% or worse | against the S&P 500 | +2 | 5309 (214) | 49% | +0.6% (-0.7% to +1.8%) | 0.2490 | 61% / 48% / 55% (102); +112 bp | 33% / 48% / 38% (173); -58 bp | no better than history |
| stocks; 1 session, -5% or worse | against the S&P 500 | +3 | 5307 (214) | 47% | -0.0% (-1.4% to +1.2%) | 0.5035 | 64% / 49% / 57% (85); +196 bp | 34% / 49% / 42% (159); -33 bp | no better than history |
| stocks; 1 session, -5% or worse | against the S&P 500 | +5 | 5297 (214) | 47% | +0.1% (-1.1% to +1.3%) | 0.4120 | 62% / 48% / 60% (66); +195 bp | 33% / 48% / 43% (150); -27 bp | no better than history |
| stocks; 1 session, -5% or worse | against the S&P 500 | +7 | 5294 (214) | 48% | +0.2% (-0.8% to +1.2%) | 0.3490 | 63% / 49% / 57% (66); +238 bp | 35% / 49% / 47% (141); -2 bp | no better than history |
| stocks; 1 session, -5% or worse | against the S&P 500 | +10 | 5293 (214) | 50% | -0.2% (-1.1% to +0.8%) | 0.6210 | 64% / 51% / 52% (30); +365 bp | 36% / 50% / 45% (77); +23 bp | no better than history |
| stocks; 1 session, -7% or worse | price | +1 | 2026 (203) | 49% | +0.0% (-1.9% to +1.9%) | 0.4760 | 62% / 47% / 59% (59); +49 bp | 32% / 47% / 44% (107); -16 bp | no better than history |
| stocks; 1 session, -7% or worse | price | +2 | 2025 (203) | 49% | -0.6% (-2.3% to +1.4%) | 0.6870 | 61% / 48% / 62% (60); +194 bp | 34% / 48% / 42% (83); -47 bp | no better than history |
| stocks; 1 session, -7% or worse | price | +3 | 2024 (203) | 50% | -1.8% (-3.3% to -0.3%) | 0.9750 | 64% / 50% / 52% (37); +102 bp | 36% / 50% / 60% (65); +98 bp | no better than history |
| stocks; 1 session, -7% or worse | price | +5 | 2019 (203) | 52% | -1.7% (-3.4% to +0.2%) | 0.9365 | 67% / 50% / 59% (31); +327 bp | 37% / 51% / 54% (92); -27 bp | no better than history |
| stocks; 1 session, -7% or worse | price | +7 | 2018 (203) | 51% | -1.2% (-3.5% to +0.6%) | 0.8545 | 68% / 50% / 53% (14); +439 bp | 38% / 51% / 53% (63); +77 bp | no better than history |
| stocks; 1 session, -7% or worse | price | +10 | 2018 (203) | 53% | -1.9% (-3.7% to -0.3%) | 0.9730 | 65% / 48% / 55% (5); +930 bp | 34% / 50% / 56% (52); +46 bp | no better than history |
| stocks; 1 session, -7% or worse | against the S&P 500 | +1 | 2026 (203) | 48% | +0.4% (-1.9% to +2.6%) | 0.3790 | 64% / 47% / 53% (62); -3 bp | 32% / 48% / 40% (125); -53 bp | no better than history |
| stocks; 1 session, -7% or worse | against the S&P 500 | +2 | 2025 (203) | 47% | -0.4% (-2.7% to +1.9%) | 0.6005 | 59% / 44% / 53% (74); +118 bp | 29% / 45% / 38% (131); -75 bp | no better than history |
| stocks; 1 session, -7% or worse | against the S&P 500 | +3 | 2024 (203) | 47% | -2.1% (-4.4% to +0.3%) | 0.9295 | 63% / 48% / 53% (57); +80 bp | 33% / 48% / 45% (136); -48 bp | no better than history |
| stocks; 1 session, -7% or worse | against the S&P 500 | +5 | 2019 (203) | 47% | -1.3% (-3.5% to +0.8%) | 0.8600 | 67% / 48% / 56% (38); +212 bp | 33% / 49% / 44% (132); -58 bp | no better than history |
| stocks; 1 session, -7% or worse | against the S&P 500 | +7 | 2018 (203) | 46% | -1.0% (-3.0% to +1.1%) | 0.7670 | 67% / 49% / 55% (27); +273 bp | 35% / 48% / 43% (114); -34 bp | no better than history |
| stocks; 1 session, -7% or worse | against the S&P 500 | +10 | 2018 (203) | 49% | -0.6% (-2.2% to +0.9%) | 0.7590 | 67% / 51% / 52% (18); +544 bp | 38% / 51% / 49% (89); -3 bp | no better than history |
| stocks; 1 session, -10% or worse | price | +1 | 515 (131) | 47% | -0.5% (-4.7% to +3.9%) | 0.5645 | 64% / 49% / 56% (31); +17 bp | 33% / 49% / 40% (60); -81 bp | no better than history |
| stocks; 1 session, -10% or worse | price | +2 | 515 (131) | 45% | -2.0% (-7.3% to +3.1%) | 0.7360 | 60% / 44% / 51% (29); +40 bp | 30% / 45% / 41% (57); -79 bp | no better than history |
| stocks; 1 session, -10% or worse | price | +3 | 514 (131) | 51% | -1.6% (-4.9% to +1.6%) | 0.7675 | 63% / 50% / 44% (23); -67 bp | 36% / 50% / 43% (28); -79 bp | no better than history |
| stocks; 1 session, -10% or worse | price | +5 | 514 (131) | 52% | -2.0% (-5.6% to +1.5%) | 0.8255 | 65% / 51% / 58% (25); +108 bp | 37% / 51% / 53% (36); +20 bp | no better than history |
| stocks; 1 session, -10% or worse | price | +7 | 514 (131) | 51% | -2.3% (-5.7% to +0.8%) | 0.8885 | 65% / 52% / 47% (11); +412 bp | 37% / 52% / 52% (41); +28 bp | no better than history |
| stocks; 1 session, -10% or worse | price | +10 | 514 (131) | 54% | -3.0% (-6.4% to +0.4%) | 0.9265 | 65% / 53% / 68% (16); +498 bp | 39% / 53% / 58% (33); +115 bp | no better than history |
| stocks; 1 session, -10% or worse | against the S&P 500 | +1 | 515 (131) | 46% | -0.3% (-5.3% to +4.8%) | 0.5305 | 66% / 49% / 54% (30); -9 bp | 32% / 49% / 39% (73); -58 bp | no better than history |
| stocks; 1 session, -10% or worse | against the S&P 500 | +2 | 515 (131) | 45% | -1.2% (-7.4% to +4.9%) | 0.5895 | 60% / 43% / 52% (30); +3 bp | 26% / 43% / 41% (81); -81 bp | no better than history |
| stocks; 1 session, -10% or worse | against the S&P 500 | +3 | 514 (131) | 49% | -0.4% (-4.4% to +3.7%) | 0.5710 | 64% / 48% / 45% (16); -182 bp | 35% / 49% / 45% (45); -64 bp | no better than history |
| stocks; 1 session, -10% or worse | against the S&P 500 | +5 | 514 (131) | 47% | -1.3% (-5.0% to +2.1%) | 0.7490 | 62% / 48% / 60% (15); +153 bp | 32% / 48% / 49% (48); +38 bp | no better than history |
| stocks; 1 session, -10% or worse | against the S&P 500 | +7 | 514 (131) | 48% | -0.7% (-5.6% to +4.5%) | 0.5885 | 64% / 50% / 66% (31); +162 bp | 31% / 51% / 48% (59); +38 bp | no better than history |
| stocks; 1 session, -10% or worse | against the S&P 500 | +10 | 514 (131) | 51% | -1.3% (-5.5% to +3.0%) | 0.6845 | 66% / 51% / 63% (24); +229 bp | 35% / 51% / 50% (37); -89 bp | no better than history |
| stocks; 5 sessions, -10% or worse | price | +1 | 2704 (207) | 51% | -1.4% (-2.9% to -0.1%) | 0.9590 | 68% / 54% / 50% (37); +7 bp | 40% / 54% / 51% (53); +48 bp | no better than history |
| stocks; 5 sessions, -10% or worse | price | +2 | 2700 (207) | 53% | -0.5% (-2.0% to +1.0%) | 0.6910 | 69% / 53% / 63% (61); +93 bp | 37% / 52% / 48% (83); +8 bp | no better than history |
| stocks; 5 sessions, -10% or worse | price | +3 | 2691 (207) | 54% | -0.4% (-1.6% to +0.8%) | 0.6905 | 69% / 53% / 59% (44); +122 bp | 41% / 53% / 50% (47); +41 bp | no better than history |
| stocks; 5 sessions, -10% or worse | price | +5 | 2691 (207) | 54% | -0.9% (-2.1% to +0.2%) | 0.9110 | 68% / 53% / 69% (25); +172 bp | 40% / 53% / 55% (49); +103 bp | no better than history |
| stocks; 5 sessions, -10% or worse | price | +7 | 2690 (207) | 54% | -1.1% (-2.2% to +0.1%) | 0.9395 | 67% / 53% / 57% (28); -110 bp | 38% / 53% / 56% (40); +205 bp | no better than history |
| stocks; 5 sessions, -10% or worse | price | +10 | 2689 (207) | 55% | -2.4% (-4.0% to -1.0%) | 0.9970 | 65% / 51% / 46% (9); -132 bp | 35% / 51% / 61% (43); +397 bp | no better than history |
| stocks; 5 sessions, -10% or worse | against the S&P 500 | +1 | 2704 (207) | 50% | -1.6% (-2.7% to -0.6%) | 0.9960 | 66% / 53% / 40% (28); -64 bp | 38% / 53% / 48% (42); -43 bp | no better than history |
| stocks; 5 sessions, -10% or worse | against the S&P 500 | +2 | 2700 (207) | 51% | -0.7% (-2.8% to +1.3%) | 0.7115 | 66% / 52% / 57% (107); +63 bp | 34% / 51% / 42% (121); -47 bp | no better than history |
| stocks; 5 sessions, -10% or worse | against the S&P 500 | +3 | 2691 (207) | 50% | -0.6% (-2.0% to +0.9%) | 0.7405 | 67% / 52% / 56% (82); +114 bp | 38% / 52% / 41% (86); -40 bp | no better than history |
| stocks; 5 sessions, -10% or worse | against the S&P 500 | +5 | 2691 (207) | 51% | -0.4% (-1.6% to +0.8%) | 0.6930 | 65% / 51% / 54% (34); +33 bp | 37% / 51% / 43% (85); +32 bp | no better than history |
| stocks; 5 sessions, -10% or worse | against the S&P 500 | +7 | 2690 (207) | 51% | -1.3% (-2.4% to -0.2%) | 0.9735 | 66% / 51% / 54% (23); +33 bp | 37% / 51% / 50% (70); +130 bp | no better than history |
| stocks; 5 sessions, -10% or worse | against the S&P 500 | +10 | 2689 (207) | 52% | -1.6% (-3.1% to -0.2%) | 0.9655 | 66% / 52% / 43% (13); -197 bp | 36% / 52% / 51% (72); +175 bp | no better than history |
| stocks; 10 sessions, -15% or worse | price | +1 | 994 (152) | 52% | -1.1% (-3.0% to +0.7%) | 0.8280 | 63% / 50% / 43% (25); -69 bp | 37% / 51% / 46% (36); +2 bp | no better than history |
| stocks; 10 sessions, -15% or worse | price | +2 | 992 (152) | 52% | -2.1% (-4.1% to -0.3%) | 0.9720 | 65% / 50% / 50% (27); -116 bp | 38% / 50% / 46% (31); +8 bp | no better than history |
| stocks; 10 sessions, -15% or worse | price | +3 | 990 (152) | 55% | -2.3% (-4.7% to -0.1%) | 0.9580 | 69% / 54% / 53% (25); -95 bp | 41% / 53% / 53% (24); +77 bp | no better than history |
| stocks; 10 sessions, -15% or worse | price | +5 | 989 (152) | 51% | -2.7% (-5.0% to -0.6%) | 0.9840 | 65% / 51% / 42% (20); -148 bp | 39% / 51% / 52% (38); +102 bp | no better than history |
| stocks; 10 sessions, -15% or worse | price | +7 | 989 (152) | 54% | -1.4% (-3.3% to +0.4%) | 0.9005 | 67% / 54% / 58% (22); -96 bp | 41% / 54% / 56% (43); +248 bp | no better than history |
| stocks; 10 sessions, -15% or worse | price | +10 | 988 (152) | 58% | -2.3% (-4.9% to +0.4%) | 0.9265 | 66% / 53% / 61% (21); +167 bp | 37% / 52% / 57% (57); +42 bp | no better than history |
| stocks; 10 sessions, -15% or worse | against the S&P 500 | +1 | 994 (152) | 50% | -1.6% (-4.0% to +0.6%) | 0.8810 | 62% / 50% / 45% (39); +50 bp | 34% / 50% / 43% (55); +11 bp | no better than history |
| stocks; 10 sessions, -15% or worse | against the S&P 500 | +2 | 992 (152) | 52% | -0.9% (-3.0% to +1.1%) | 0.7655 | 64% / 51% / 55% (24); +75 bp | 36% / 51% / 43% (48); +2 bp | no better than history |
| stocks; 10 sessions, -15% or worse | against the S&P 500 | +3 | 990 (152) | 51% | -1.9% (-3.6% to -0.3%) | 0.9720 | 63% / 51% / 46% (20); -18 bp | 38% / 51% / 43% (40); -55 bp | no better than history |
| stocks; 10 sessions, -15% or worse | against the S&P 500 | +5 | 989 (152) | 51% | -1.0% (-3.4% to +1.5%) | 0.7645 | 63% / 50% / 56% (48); +107 bp | 34% / 50% / 44% (71); +58 bp | no better than history |
| stocks; 10 sessions, -15% or worse | against the S&P 500 | +7 | 989 (152) | 51% | +0.0% (-2.4% to +2.4%) | 0.4980 | 63% / 51% / 55% (37); +228 bp | 35% / 51% / 44% (79); -133 bp | no better than history |
| stocks; 10 sessions, -15% or worse | against the S&P 500 | +10 | 988 (152) | 53% | -1.7% (-4.3% to +0.8%) | 0.8685 | 65% / 52% / 56% (30); -46 bp | 37% / 53% / 46% (75); -55 bp | no better than history |
| indices and sectors; 1 session, -3% or worse | price | +1 | 2059 (193) | 55% | -0.6% (-2.3% to +1.2%) | 0.7025 | 65% / 51% / 59% (47); +20 bp | 40% / 52% / 69% (18); +87 bp | no better than history |
| indices and sectors; 1 session, -3% or worse | price | +2 | 2059 (193) | 53% | -1.5% (-3.6% to +0.6%) | 0.8980 | 65% / 50% / 57% (45); +71 bp | 36% / 49% / 44% (36); -8 bp | no better than history |
| indices and sectors; 1 session, -3% or worse | price | +3 | 2058 (193) | 54% | -2.3% (-4.5% to -0.2%) | 0.9665 | 68% / 51% / 53% (43); -32 bp | 39% / 52% / 63% (28); +136 bp | no better than history |
| indices and sectors; 1 session, -3% or worse | price | +5 | 2055 (193) | 57% | -2.1% (-4.1% to -0.1%) | 0.9580 | 70% / 55% / 50% (50); -76 bp | 41% / 53% / 59% (26); +192 bp | no better than history |
| indices and sectors; 1 session, -3% or worse | price | +7 | 2054 (193) | 58% | -2.5% (-4.8% to -0.3%) | 0.9705 | 70% / 55% / 57% (64); +36 bp | 42% / 54% / 73% (16); +324 bp | no better than history |
| indices and sectors; 1 session, -3% or worse | price | +10 | 2054 (193) | 57% | -2.9% (-5.0% to -0.7%) | 0.9900 | 67% / 51% / 48% (32); -21 bp | 38% / 51% / 54% (20); -41 bp | no better than history |
| indices and sectors; 1 session, -4% or worse | price | +1 | 955 (119) | 56% | -2.7% (-7.1% to +1.5%) | 0.8490 | 69% / 52% / 58% (50); +85 bp | 36% / 52% / 43% (15); +15 bp | no better than history |
| indices and sectors; 1 session, -4% or worse | price | +2 | 955 (119) | 54% | -4.1% (-9.1% to +0.8%) | 0.9205 | 71% / 50% / 53% (32); +76 bp | 37% / 51% / 51% (31); -12 bp | no better than history |
| indices and sectors; 1 session, -4% or worse | price | +3 | 955 (119) | 55% | -4.1% (-8.3% to -0.2%) | 0.9595 | 74% / 55% / 54% (34); +43 bp | 42% / 55% / 63% (13); +113 bp | no better than history |
| indices and sectors; 1 session, -4% or worse | price | +5 | 953 (119) | 60% | -5.0% (-10.0% to -0.0%) | 0.9500 | 74% / 54% / 60% (42); +55 bp | 41% / 55% / 56% (31); +94 bp | no better than history |
| indices and sectors; 1 session, -4% or worse | price | +7 | 953 (119) | 59% | -1.9% (-5.3% to +1.7%) | 0.8175 | 70% / 54% / 52% (34); -89 bp | 43% / 55% / 41% (14); -162 bp | no better than history |
| indices and sectors; 1 session, -4% or worse | price | +10 | 953 (119) | 60% | -2.6% (-5.1% to -0.1%) | 0.9570 | 72% / 56% / 51% (11); -1 bp | 46% / 57% / 55% (6); -81 bp | no better than history |
| indices and sectors; 5 sessions, -7% or worse | price | +1 | 504 (89) | 56% | +1.7% (-3.7% to +7.2%) | 0.3035 | 69% / 53% / 63% (46); +84 bp | 35% / 53% / 44% (27); -117 bp | no better than history |
| indices and sectors; 5 sessions, -7% or worse | price | +2 | 503 (89) | 57% | -1.6% (-5.8% to +2.4%) | 0.7320 | 73% / 58% / 58% (25); +32 bp | 43% / 58% / 55% (21); +79 bp | no better than history |
| indices and sectors; 5 sessions, -7% or worse | price | +3 | 501 (89) | 59% | +0.6% (-4.3% to +5.7%) | 0.4075 | 73% / 57% / 67% (49); +107 bp | 41% / 56% / 41% (15); -142 bp | no better than history |
| indices and sectors; 5 sessions, -7% or worse | price | +5 | 501 (89) | 64% | -0.2% (-6.2% to +5.5%) | 0.4925 | 74% / 58% / 69% (34); +199 bp | 42% / 57% / 53% (12); +55 bp | no better than history |
| indices and sectors; 5 sessions, -7% or worse | price | +7 | 501 (89) | 63% | +0.8% (-4.0% to +5.7%) | 0.3910 | 71% / 56% / 67% (33); +130 bp | 40% / 54% / 59% (10); +71 bp | no better than history |
| indices and sectors; 5 sessions, -7% or worse | price | +10 | 501 (89) | 59% | -1.8% (-5.0% to +1.3%) | 0.8345 | 65% / 51% / 60% (13); +246 bp | 37% / 50% / 62% (13); +164 bp | no better than history |
