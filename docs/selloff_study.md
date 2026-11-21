# Sell-off study: under which conditions does a big sell-off bounce, and under which does it go on?

Registered in TRACK 3.92 before any outcome. Each sell-off is described by its conditions at the close of the event day; the sell-offs up to 2015 are sorted into 3, 4 or 5 groups by those conditions alone (k-means); the groups are then applied unchanged to the sell-offs from 2016 on, and what happened over the next 1, 2, 3, 5, 10 sessions is compared between groups THERE. Outcome in bp (100 bp = 1%): a stock minus the S&P 500; an index or sector fund on its own. Each day counts once however many securities fell on it. p = how often groups assigned at random differ as much as the real ones, taking the best of all group counts and horizons (2000 shuffles). A definition counts at p < 0.05 divided by the number of definitions tested. **A group becomes a candidate only if** the definition passes AND the group's average in the test years is beyond 30 bp (stocks; 10 bp for funds) in the same direction as in the train years AND it has that sign in both halves of the test years.

## stocks: 1 session, -5% or worse

Train 3457 events, test 3555 events on 1106 separate days. All test events, next sessions: +1: -3 bp, +2: +3 bp, +3: +2 bp, +5: +20 bp, +10: +51 bp.
**Largest difference between groups: 4 groups, 5 sessions after. p = 0.0120 (bar 0.0063) -> does not pass.** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened +0.115 (p 0.000).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | high results filing in the window; high volume against normal; low size in units of its own usual move | 450 | 693 (525) | -41 | -20; -29; 45% | -21; -36; 46% | -26; -39; 44% | -25; -55; 43% | -8; -45; 48% | -14 | -35 |
| 2 | low distance below the one-year high %; low run-up over the 60 sessions before %; low S&P 500 against its 200-day average % | 831 | 333 (93) | +278 | +1; +33; 53% | +36; +59; 56% | +19; +91; 57% | +252; +226; 64% | +347; +263; 63% | +198 | +308 |
| 3 | high S&P 500 against its 200-day average %; low VIX level; high run-up over the 60 sessions before % | 1095 | 1831 (734) | +7 | +7; +13; 52% | +15; -0; 50% | +19; +10; 51% | +33; +23; 52% | +68; +38; 53% | -8 | +63 |
| 4 | high share of large stocks down 3%+ that day; low the S&P 500 over the same sessions %; high VIX level | 1081 | 698 (22) | +154 | +34; +39; 57% | +47; +41; 56% | +34; +52; 55% | +38; +5; 50% | +51; +33; 53% | +21 | +65 |

## stocks: 1 session, -7% or worse

Train 1411 events, test 1368 events on 571 separate days. All test events, next sessions: +1: -4 bp, +2: +3 bp, +3: -4 bp, +5: +8 bp, +10: -8 bp.
**Largest difference between groups: 5 groups, 5 sessions after. p = 0.1175 (bar 0.0063) -> does not pass.** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened +0.144 (p 0.000).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | high other company filing in the window; low results filing in the window; low distance below the one-year high % | 108 | 71 (40) | +229 | +74; +57; 61% | +74; +90; 56% | +91; +122; 61% | +318; +184; 65% | +233; +46; 58% | +491 | +88 |
| 2 | low distance below the one-year high %; low run-up over the 60 sessions before %; low S&P 500 against its 200-day average % | 338 | 92 (17) | +509 | -171; +121; 58% | +101; +244; 64% | -22; +302; 73% | +72; +679; 75% | +269; +340; 66% | -16 | +582 |
| 3 | high volume against normal; high results filing in the window; low size in units of its own usual move | 240 | 347 (293) | -107 | -27; -42; 43% | -27; -66; 44% | -31; -36; 45% | -42; -46; 43% | -64; -58; 46% | -34 | -46 |
| 4 | high S&P 500 against its 200-day average %; low VIX level; low share of large stocks down 3%+ that day | 305 | 491 (299) | +108 | +17; +39; 54% | +18; +11; 51% | +13; -9; 49% | +27; +1; 50% | +12; +36; 52% | +55 | +12 |
| 5 | high share of large stocks down 3%+ that day; low the S&P 500 over the same sessions %; high VIX change over the same sessions % | 420 | 367 (17) | +94 | +46; +73; 60% | +110; +67; 56% | +75; +55; 55% | +79; +14; 51% | +127; +52; 55% | -79 | +365 |

## stocks: 1 session, -10% or worse

Train 517 events, test 437 events on 213 separate days. All test events, next sessions: +1: -23 bp, +2: -9 bp, +3: -10 bp, +5: +27 bp, +10: +9 bp.
**Largest difference between groups: 4 groups, 10 sessions after. p = 0.0120 (bar 0.0063) -> does not pass.** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened +0.119 (p 0.003).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | low VIX level; high S&P 500 against its 200-day average %; high volume against normal | 139 | 199 (176) | -103 | -42; -36; 44% | -31; -86; 44% | -50; -52; 46% | -27; -62; 44% | -95; -43; 48% | +97 | -157 |
| 2 | high other company filing in the window; high size in units of its own usual move; low results filing in the window | 55 | 18 (10) | +5 | +256; +294; 72% | +411; +93; 61% | +448; +64; 56% | +1070; +220; 56% | +1044; +290; 67% | +634 | +1689 |
| 3 | high size in units of its own usual move; low distance below the one-year high %; low volume against normal | 171 | 60 (31) | +662 | +36; +317; 72% | +34; +216; 60% | +132; +298; 73% | +246; +623; 75% | +477; +618; 68% | -130 | +722 |
| 4 | low the S&P 500 over the same sessions %; high share of large stocks down 3%+ that day; high VIX change over the same sessions % | 152 | 160 (11) | +87 | +5; +108; 60% | +76; +10; 50% | +86; +76; 56% | -126; +5; 51% | +54; +199; 61% | -149 | +347 |

## stocks: 5 sessions, -10% or worse

Train 1675 events, test 1839 events on 695 separate days. All test events, next sessions: +1: +7 bp, +2: +4 bp, +3: +1 bp, +5: +24 bp, +10: +39 bp.
**Largest difference between groups: 4 groups, 5 sessions after. p = 0.0970 (bar 0.0063) -> does not pass.** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened -0.016 (p 0.731).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | high VIX change over the same sessions %; low size in units of its own usual move; high share of large stocks down 3%+ that day | 132 | 303 (21) | +86 | +42; +18; 55% | +25; +35; 54% | +51; +39; 53% | +60; +6; 51% | +47; +34; 54% | +71 | +32 |
| 2 | high S&P 500 against its 200-day average %; low VIX level; low share of large stocks down 3%+ that day | 773 | 1200 (570) | +68 | +6; +18; 53% | +6; +20; 53% | +1; +3; 50% | +25; +15; 52% | +47; +79; 54% | +25 | +26 |
| 3 | high volume against normal; low gap at the open %; low last day's move % | 139 | 185 (168) | -20 | +2; -7; 49% | -23; -52; 46% | -32; -14; 48% | -21; -1; 50% | -11; +15; 51% | -57 | +5 |
| 4 | low S&P 500 against its 200-day average %; high VIX level; low distance below the one-year high % | 631 | 151 (25) | +133 | +76; +69; 57% | +153; +109; 61% | +249; +76; 62% | +377; +133; 62% | +186; +44; 54% | +442 | +174 |

## stocks: 10 sessions, -15% or worse

Train 756 events, test 768 events on 384 separate days. All test events, next sessions: +1: +7 bp, +2: +21 bp, +3: +27 bp, +5: +80 bp, +10: +95 bp.
**Largest difference between groups: 4 groups, 3 sessions after. p = 0.1900 (bar 0.0063) -> does not pass.** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened +0.018 (p 0.300).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | high volume against normal; low gap at the open %; low last day's move % | 51 | 77 (71) | -194 | -32; -43; 44% | -76; -93; 44% | -105; -119; 42% | -6; -55; 44% | -26; +103; 51% | -112 | -100 |
| 2 | high S&P 500 against its 200-day average %; low VIX level; low share of large stocks down 3%+ that day | 300 | 474 (310) | +78 | +14; +30; 57% | +32; +35; 55% | +42; +63; 56% | +85; +48; 55% | +127; +132; 57% | +56 | +32 |
| 3 | high VIX change over the same sessions %; high share of large stocks down 3%+ that day; low the S&P 500 over the same sessions % | 123 | 175 (23) | +20 | -51; -7; 49% | -14; -55; 44% | +1; -22; 48% | +19; -132; 41% | -141; -7; 50% | -15 | +58 |
| 4 | low S&P 500 against its 200-day average %; high VIX level; low distance below the one-year high % | 282 | 42 (17) | -82 | +143; +113; 60% | +321; +207; 69% | +368; +234; 67% | +521; +244; 64% | +340; +161; 69% | +716 | +78 |

## indices and sectors: 1 session, -3% or worse

Train 1669 events, test 1034 events on 318 separate days. All test events, next sessions: +1: +28 bp, +2: +27 bp, +3: +54 bp, +5: +79 bp, +10: +129 bp.
**Largest difference between groups: 4 groups, 10 sessions after. p = 0.0000 (bar 0.0063) -> PASSES; candidate group(s): group 2 (bounces), group 3 (bounces).** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened -0.080 (p 0.997).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | high VIX level; low S&P 500 against its 200-day average %; low the S&P 500 over the same sessions % | 242 | 62 (9) | +175 | +235; +211; 79% | +125; -25; 45% | +299; +166; 63% | +583; +724; 68% | +966; +878; 92% | +1001 | -87 |
| 2 **candidate** | low distance below the one-year high %; high size in units of its own usual move; low run-up over the 60 sessions before % | 549 | 130 (45) | +40 | +69; +36; 56% | +97; +175; 65% | +185; +105; 58% | +301; +142; 66% | +601; +499; 79% | +757 | +447 |
| 3 **candidate** | high S&P 500 against its 200-day average %; low VIX level; high distance below the one-year high % | 674 | 525 (267) | +68 | +20; +27; 57% | +24; +39; 53% | +47; +21; 52% | +61; +47; 54% | +85; +89; 55% | +85 | +84 |
| 4 | high VIX change over the same sessions %; low size in units of its own usual move; high volume against normal | 204 | 317 (49) | +24 | +24; +31; 55% | -23; +7; 52% | -46; +5; 50% | -62; +33; 52% | -98; +77; 52% | -332 | +260 |

## indices and sectors: 1 session, -4% or worse

Train 775 events, test 481 events on 155 separate days. All test events, next sessions: +1: +36 bp, +2: +33 bp, +3: +54 bp, +5: +125 bp, +10: +216 bp.
**Largest difference between groups: 5 groups, 5 sessions after. p = 0.0000 (bar 0.0063) -> PASSES; candidate group(s): group 3 (bounces), group 4 (bounces).** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened -0.145 (p 0.996).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | low distance below the one-year high %; low share of large stocks down 3%+ that day; high the S&P 500 over the same sessions % | 177 | 21 (12) | +49 | +155; +112; 76% | +116; +348; 81% | +332; +259; 81% | +805; +762; 95% | +1128; +799; 90% | +862 | +712 |
| 2 | low size in units of its own usual move; high VIX change over the same sessions %; high volume against normal | 108 | 170 (33) | +231 | +34; +78; 59% | -10; +42; 55% | -54; +37; 54% | -26; +122; 56% | -113; +33; 51% | -178 | +215 |
| 3 **candidate** | high S&P 500 against its 200-day average %; high run-up over the 60 sessions before %; low VIX level | 233 | 216 (121) | +27 | +11; +14; 55% | +26; +9; 50% | +43; +18; 52% | +83; +44; 54% | +178; +180; 57% | +60 | +92 |
| 4 **candidate** | low S&P 500 against its 200-day average %; high VIX level; high share of large stocks down 3%+ that day | 192 | 49 (7) | +93 | +188; +148; 73% | +328; +103; 67% | +402; +507; 59% | +841; +1061; 80% | +987; +880; 88% | +919 | +66 |
| 5 | low last day's move %; low the S&P 500 over the same sessions %; high VIX level | 65 | 25 (4) | +623 | +723; +680; 100% | -190; -236; 24% | -46; +65; 64% | -467; -606; 16% | +899; +973; 96% | -467 | +nan |

## indices and sectors: 5 sessions, -7% or worse

Train 567 events, test 337 events on 147 separate days. All test events, next sessions: +1: +27 bp, +2: +53 bp, +3: +47 bp, +5: +96 bp, +10: +113 bp.
**Largest difference between groups: 5 groups, 10 sessions after. p = 0.0005 (bar 0.0063) -> PASSES; candidate group(s): group 5 (bounces).** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened -0.053 (p 0.837).

| group | what marks it | train events | test events (days) | train average | test +1: average; middle; share up | test +2: average; middle; share up | test +3: average; middle; share up | test +5: average; middle; share up | test +10: average; middle; share up | test first half | test second half |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | high VIX change over the same sessions %; low size in units of its own usual move; high volume against normal | 9 | 12 (2) | +420 | -35; +147; 67% | +217; +196; 92% | -28; -215; 33% | +271; +113; 83% | -577; +224; 58% | -577 | +nan |
| 2 | high VIX level; low S&P 500 against its 200-day average %; high share of large stocks down 3%+ that day | 116 | 23 (6) | +16 | +279; +543; 74% | +259; +98; 57% | +321; +87; 61% | +553; +35; 52% | +1019; +1103; 96% | +1085 | +191 |
| 3 | low distance below the one-year high %; low run-up over the 60 sessions before %; high size in units of its own usual move | 115 | 17 (11) | -11 | -5; +53; 53% | -80; +155; 76% | +97; +381; 76% | +341; +555; 82% | +599; +959; 82% | +666 | +489 |
| 4 | low size in units of its own usual move; high volume against normal; high distance below the one-year high % | 94 | 100 (36) | +102 | -17; -22; 48% | +23; +6; 51% | -50; -123; 42% | +13; +81; 55% | -149; +48; 51% | -472 | +388 |
| 5 **candidate** | high S&P 500 against its 200-day average %; low VIX level; high run-up over the 60 sessions before % | 233 | 185 (105) | +90 | +32; +22; 56% | +60; +135; 64% | +61; +97; 59% | +75; +120; 61% | +119; +118; 57% | +262 | +58 |

