# Document-read audit — every source, from cached reads

*Run 2026-08-25 17:36. 2616 cached reads. No API calls. Nothing here is a*
*registered test; a flagged line is a question, not a verdict.*

Origin: the political_other aggregate (|dir| < 0.005 across 816 documents)
was interpreted as "nothing here moves markets" without checking whether
the documents that would falsify that — Section 232 tariff proclamations —
were present and what the reader assigned them. This applies the same
question to every source.

## A. TIMING ORDER — does novelty fall with publication lag?

Expected: fomc_statement > earnings_8k > political_order ≈ political_other.
The statement IS the event; the 8-K accompanies the release; a Federal
Register document lands days after the announcement that moved the price.

| source | n | novelty mean | novelty p90 | specificity | max\|dir\| mean |
|---|---|---|---|---|---|
| fomc_statement | 131 |  0.289 |  0.550 |  0.563 |  0.261 |
| fomc_minutes | 125 |  0.339 |  0.500 |  0.494 |  0.271 |
| earnings_8k | 671 |  0.290 |  0.550 |  0.687 |  0.260 |
| political_order | 873 |  0.225 |  0.400 |  0.550 |  0.073 |
| political_other | 816 |  0.019 |  0.050 |  0.170 |  0.002 |

Observed novelty order: fomc_minutes > earnings_8k > fomc_statement > political_order > political_other
**NOT the expected order.** The novelty field may not be measuring
publication lag. Look at the landmark section before trusting it.

## B. SIGNAL CLASSES vs SOURCE BASELINE

Matched = documents whose TEXT contains the class keywords. Baseline =
the rest of the source. A matched class that reads like its baseline
means the reader is not separating operative from routine content.

### fomc_statement  (n=131)

| class | n | spec | novelty | mag | eq | dur | gold | usd | oil | max\|dir\| | expect |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *baseline (all)* | 131 |  0.563 |  0.289 |  0.350 |  0.099 |  0.079 |  0.047 | -0.029 |  0.028 |  0.261 | — |
| rate HIKE | 28 |  0.652 |  0.309 |  0.421 | -0.093 | -0.120 | -0.114 |  0.164 | -0.027 |  0.307 | dur<0, mag>base |
| rate CUT | 16 |  0.634 |  0.369 |  0.431 |  0.241 |  0.266 |  0.206 | -0.219 |  0.041 |  0.316 | dur>0, mag>base |
| emergency / intermeeting | 0 | | | | | | | | | | mag>>base, novelty>>base — **NO MATCHES** |
| QE / asset purchases start | 17 |  0.538 |  0.294 |  0.368 |  0.129 |  0.100 |  0.091 | -0.076 |  0.009 |  0.291 | dur>0, mag>base |
| taper / runoff | 9 |  0.617 |  0.206 |  0.278 |  0.089 | -0.039 | -0.083 |  0.072 |  0.022 |  0.194 | dur<0 |
| forward guidance strengthened | 21 |  0.560 |  0.288 |  0.324 |  0.150 |  0.260 |  0.183 | -0.176 |  0.045 |  0.283 | spec>base **<-- spec not above baseline** |

### fomc_minutes  (n=125)

| class | n | spec | novelty | mag | eq | dur | gold | usd | oil | max\|dir\| | expect |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *baseline (all)* | 125 |  0.494 |  0.339 |  0.392 |  0.033 |  0.056 |  0.042 | -0.007 |  0.015 |  0.271 | — |
| taper / runoff discussed | 66 |  0.517 |  0.331 |  0.405 |  0.028 |  0.002 |  0.006 |  0.026 |  0.012 |  0.275 | dur<0, dispersion>base |
| dissent recorded | 123 |  0.496 |  0.342 |  0.393 |  0.036 |  0.061 |  0.043 | -0.010 |  0.015 |  0.272 | dispersion>base |
| emergency context | 124 |  0.498 |  0.342 |  0.395 |  0.033 |  0.057 |  0.042 | -0.007 |  0.015 |  0.273 | mag>base |
| hawkish tilt language | 17 |  0.465 |  0.347 |  0.400 | -0.029 | -0.032 | -0.003 |  0.065 |  0.003 |  0.282 | dur<0 |
| dovish tilt language | 28 |  0.491 |  0.320 |  0.361 |  0.036 |  0.057 | -0.000 |  0.005 |  0.009 |  0.229 | dur>0 |

### earnings_8k  (n=671)

| class | n | spec | novelty | mag | eq | dur | gold | usd | oil | max\|dir\| | expect |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *baseline (all)* | 671 |  0.687 |  0.290 |  0.295 |  0.193 |  0.004 | -0.001 |  0.006 | -0.001 |  0.260 | — |
| guidance RAISED | 6 |  0.700 |  0.442 |  0.417 |  0.425 | -0.017 |  0.000 |  0.000 |  0.000 |  0.425 | eq>0, mag>base, guidance_change>0 |
| guidance LOWERED / withdrawn | 3 |  0.683 |  0.350 |  0.450 |  0.233 |  0.000 |  0.000 |  0.000 |  0.000 |  0.233 | eq<0, mag>base, guidance_change<0 |
| record revenue | 37 |  0.697 |  0.422 |  0.541 |  0.328 | -0.019 | -0.018 |  0.042 |  0.007 |  0.499 | eq>0 |
| net loss | 48 |  0.616 |  0.375 |  0.425 |  0.230 |  0.005 | -0.006 |  0.015 |  0.000 |  0.355 | eq<=base |
| restructuring / impairment | 231 |  0.594 |  0.373 |  0.422 |  0.273 |  0.012 |  0.000 |  0.008 | -0.004 |  0.384 | eq<=base |
| buyback / dividend raise | 201 |  0.637 |  0.332 |  0.373 |  0.244 |  0.003 | -0.005 |  0.015 |  0.001 |  0.335 | eq>0 |

### political_order  (n=873)

| class | n | spec | novelty | mag | eq | dur | gold | usd | oil | max\|dir\| | expect |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *baseline (all)* | 873 |  0.550 |  0.225 |  0.159 |  0.018 |  0.011 |  0.010 |  0.007 |  0.015 |  0.073 | — |
| TARIFF / trade action | 235 |  0.669 |  0.287 |  0.240 | -0.005 |  0.037 |  0.033 |  0.018 |  0.038 |  0.129 | spec>base, |dir|>base |
| SANCTIONS / blocking | 100 |  0.632 |  0.313 |  0.235 | -0.024 |  0.036 |  0.050 |  0.022 |  0.070 |  0.098 | spec>base, |dir|>base |
| export controls / semiconductors | 43 |  0.494 |  0.283 |  0.262 |  0.058 |  0.030 |  0.033 |  0.005 |  0.005 |  0.160 | |dir|>base |
| energy / drilling / pipelines | 49 |  0.458 |  0.249 |  0.235 |  0.102 |  0.008 |  0.007 |  0.016 |  0.044 |  0.169 | oil != 0 |
| national emergency declared | 48 |  0.638 |  0.380 |  0.357 | -0.045 |  0.070 |  0.070 |  0.024 |  0.014 |  0.229 | spec>base, mag>base |
| ceremonial / administrative | 135 |  0.475 |  0.179 |  0.106 |  0.010 |  0.002 |  0.003 |  0.001 |  0.001 |  0.037 | spec<base, |dir|~0 |

### political_other  (n=816)

| class | n | spec | novelty | mag | eq | dur | gold | usd | oil | max\|dir\| | expect |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *baseline (all)* | 816 |  0.170 |  0.019 |  0.023 |  0.001 |  0.000 |  0.000 |  0.000 | -0.001 |  0.002 | — |
| Section 232 PROCLAMATION | 1 |  0.100 |  0.000 |  0.020 |  0.000 |  0.000 |  0.000 |  0.000 |  0.000 |  0.000 | spec>base, |dir|>base  <-- THE TARIFF CASE **<-- FLAT vs baseline** **<-- spec not above baseline** |
| Section 201 safeguard | 102 |  0.233 |  0.036 |  0.039 |  0.005 |  0.000 |  0.000 |  0.001 | -0.000 |  0.006 | spec>base, |dir|>base **<-- FLAT vs baseline** |
| any tariff / duty language | 32 |  0.620 |  0.114 |  0.076 |  0.011 |  0.000 |  0.000 |  0.002 | -0.002 |  0.019 | |dir|>base **<-- FLAT vs baseline** |
| national emergency (notice / continuation) | 27 |  0.357 |  0.035 |  0.037 |  0.004 |  0.000 |  0.002 |  0.000 |  0.001 |  0.006 | spec>base |
| commemorative | 798 |  0.160 |  0.018 |  0.022 |  0.001 |  0.000 |  0.000 |  0.000 | -0.001 |  0.002 | spec<base, |dir|~0 |

## C. SIGN CONSISTENCY — where the text fixes the sign

Duration = bond PRICE in the schema, so a hike must read dur < 0 and a
cut dur > 0. This is the one place the sign is not a judgement call.

| class | n | dur mean | dur>0 | dur<0 | dur=0 | stance mean | verdict |
|---|---|---|---|---|---|---|---|
| HIKE (want dur<0) | 28 | -0.120 | 10 | 18 | 0 |  0.286 | **MIXED** |
| CUT (want dur>0) | 16 |  0.266 | 14 | 2 | 0 | -0.219 | OK |

Earnings — the reader's own `extra.surprise` and `extra.guidance_change`
against its own `dir_equity`. These are the same read; they should agree.

| pair | n | corr | agree sign | disagree | either zero |
|---|---|---|---|---|---|
| surprise vs dir_eq | 671 |  0.916 | 431 | 11 | 229 |
| guidance_change vs dir_eq | 671 |  0.823 | 264 | 14 | 393 |

## D. WITHIN-READER CONSISTENCY

`is_decided` and `specificity` are both the reader's judgement of the same
thing. If decided documents are not more specific, the field is noise.

| source | is_decided | n | specificity | novelty | max\|dir\| |
|---|---|---|---|---|---|
| political_order | True | 770 |  0.586 |  0.224 |  0.070 |
| political_order | False | 103 |  0.281 |  0.235 |  0.092 |
| political_other | True | 807 |  0.171 |  0.019 |  0.002 |
| political_other | False | 9 |  0.111 |  0.060 |  0.006 |

FOMC — `extra.stance` (hawkish +) against `dir_duration` (price). Hawkish
should mean duration DOWN, so the correlation should be NEGATIVE.

- fomc_statement: n=131, corr(stance, dir_dur) = -0.802 → OK (negative)
- fomc_minutes: n=125, corr(stance, dir_dur) = -0.527 → OK (negative)

## E. LANDMARK DOCUMENTS

Named events the reader must have seen as large. Window around the
ANNOUNCEMENT date, since Federal Register publication lags it. Absent =
a COVERAGE finding. Present but routine = a READER finding.

| source | window | expectation | found | stem | spec | novelty | mag | eq | dur | gold | usd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fomc_statement | 2008-12-16 +3d | ZIRP -- dur>0, mag high, novelty high | **ABSENT** | | | | | | | | |
| fomc_statement | 2020-03-15 +3d | COVID emergency cut -- dur>0, mag >>, novelty >> | 1 | 20200315 |  0.800 |  0.650 |  0.950 |  0.300 |  0.800 |  0.600 | -0.600 |
| fomc_statement | 2015-12-16 +3d | first hike of the cycle -- dur<0, novelty LOW (telegraphed) | 1 | 20151216 |  0.850 |  0.300 |  0.750 | -0.200 |  0.100 | -0.300 |  0.400 |
| fomc_statement | 2022-06-15 +3d | 75bp hike -- dur<0, mag high | 1 | 20220615 |  0.850 |  0.350 |  0.700 | -0.500 | -0.600 | -0.300 |  0.500 |
| fomc_statement | 2013-12-18 +3d | taper begins -- dur<0 | 1 | 20131218 |  0.800 |  0.600 |  0.700 |  0.300 | -0.300 | -0.400 |  0.300 |
| fomc_minutes | 2013-05-22 +3d | taper-tantrum minutes -- dur<0, dispersion high | 1 | 20130522_meeting20130501 |  0.350 |  0.300 |  0.350 |  0.100 |  0.200 |  0.050 | -0.100 |
| fomc_minutes | 2022-01-05 +3d | Jan-22 minutes, runoff shock -- dur<0, novelty > base | 1 | 20220105_meeting20211215 |  0.600 |  0.450 |  0.550 | -0.200 |  0.300 | -0.100 |  0.300 |
| political_order | 2025-02-01 +10d | IEEPA tariffs CA/MX/CN -- spec high, |dir| > 0 | 7 | 20250207_exec202502406 |  0.900 |  0.600 |  0.750 | -0.500 |  0.300 |  0.300 |  0.300 |
| political_order | 2025-04-02 +10d | reciprocal tariffs -- spec high, mag high, |dir| > 0 | 2 | 20250407_exec202506063 |  0.900 |  0.850 |  0.950 | -0.900 |  0.600 |  0.600 | -0.500 |
| political_other | 2018-03-08 +10d | 232 steel/aluminum -- spec high, |dir| > 0 | **ABSENT** | | | | | | | | |
| political_other | 2025-03-26 +10d | 232 autos -- spec high, |dir| > 0 | **ABSENT** | | | | | | | | |
| political_other | 2025-02-10 +10d | 232 steel/aluminum restored -- spec high, |dir| > 0 | **ABSENT** | | | | | | | | |
| earnings_8k | 2023-05-24 +3d | NVDA FQ1-24, guidance +50% -- eq>0, mag high, novelty high | 1 | 20230524_NVDA |  0.900 |  0.850 |  0.900 |  0.900 | -0.200 | -0.100 |  0.100 |

Dates in this table are from memory and should be checked against the
documents themselves. A miss may be my date, not the corpus.

## F. FIELD POPULATION — can step 5 use these reads?

| source | n | evidence≥1 | ticker | surprise | guidance_change | stance | is_decided | dispersion |
|---|---|---|---|---|---|---|---|---|
| fomc_statement | 131 | 100% | 0% | 0% | 0% | 100% | 0% | 0% |
| fomc_minutes | 125 | 100% | 0% | 0% | 0% | 100% | 0% | 100% |
| earnings_8k | 671 | 100% | 100% | 100% | 100% | 0% | 0% | 0% |
| political_order | 873 | 100% | 0% | 0% | 0% | 0% | 100% | 0% |
| political_other | 816 | 100% | 0% | 0% | 0% | 0% | 100% | 0% |

Fields the source's prompt asks for should be near 100%. A field the
prompt does not ask for is expected to be blank and is not a defect.

Truncated 8-Ks (n=26) vs whole (n=645): specificity  0.458 vs  0.696, confidence  0.431 vs  0.610, evidence≥1 100% vs 100%, ticker filled 100% vs 100%.
(Confounded with document type — 6-K complete submissions vs EX-99 — as
assess_8k.py states. Reported, not adjusted for.)

## G. FLAT-TAIL CHECK — did ANYTHING in each source read as directional?

| source | n | any\|dir\|>0.05 | >0.3 | top-5 max\|dir\| | top-5 stems |
|---|---|---|---|---|---|
| fomc_statement | 131 | 126 | 32 | 0.80, 0.70, 0.70, 0.70, 0.60 | 20200315, 20120913, 20110809, 20110921, 20220615 |
| fomc_minutes | 125 | 123 | 34 | 0.60, 0.60, 0.60, 0.50, 0.50 | 20190710_meeting20190619, 20110830_meeting20110809, 20111012_meeting20110921, 20240821_meeting20240731, 20221012_meeting20220921 |
| earnings_8k | 671 | 515 | 211 | 0.90, 0.90, 0.90, 0.90, 0.85 | 20230823_NVDA, 20240522_NVDA, 20250909_ORCL, 20230524_NVDA, 20260318_MU |
| political_order | 873 | 258 | 38 | 0.90, 0.70, 0.70, 0.70, 0.60 | 20250407_exec202506063, 20250414_exec202506378, 20260225_exec202603832, 20250521_exec202509297, 20250415_exec202506462 |
| political_other | 816 | 5 | 0 | 0.10, 0.10, 0.10, 0.10, 0.10 | 20121105_proc201227143, 20120518_proc201212220, 20121228_proc201231350, 20120309_proc20125912, 20160317_proc201606249 | **<-- essentially nothing directional in the whole source**
