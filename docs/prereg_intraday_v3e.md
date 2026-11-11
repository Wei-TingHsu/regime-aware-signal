# Pre-registration — v3e: the intraday tests (TRACK §3.55)

*Registered 2026-11-12, before any run on the intraday data. Origin: the founder's two-category rule (11 Nov) — a finding that lives only on the day
of the information is SUBJECTIVE; **grade B** when seen at daily closes, **grade A** when minute prices show the move can still be caught after the
release — and his proposal that the price just before a scheduled release is the value investors agreed on, so the first minutes after it measure the
surprise.*

## 1. Data

CME futures, 1-minute bars, 7 Jun 2010 → 11 Nov 2026 (Databento GLBX.MDP3): Nasdaq-100 (NQ), S&P 500 (ES), gold (GC), 10-year Treasury note (ZN);
one contract per day chosen by `processed/intraday_quality_final.parquet`; session minutes 08:00–16:15 New York. Data-treatment rules: TRACK §3.54.
P(m) = the last traded price before clock minute m; a price older than 5 minutes is missing. Returns in basis points. Cost 2 bp round trip.

## 2. E1 — Fed statement days (the grade-A question for "gold moves with the rate surprise on statement days", T9b)

- **Days:** every statement day in `processed/fomc_decisions.csv` and the corpus from June 2010.
- **Release time:** whichever of 12:30, 14:00, 14:15 shows the largest 5-minute move in the 10-year note that day (the price dates the news).
- **(a) When does the move happen?** Each asset's move signed by the direction of the note's whole-day move (note up = yields down → gold and
  equities counted as predicted up), cut into: prior close → release; first 5 minutes; minutes 5–30; 30 minutes after → close. Descriptive.
- **(b) Is anything left to catch? — the test.** Watch the note for k minutes after the release (k = 1, 5, 15, 30); enter the asset at that minute in
  the direction the note moved; hold 15, 30, 60 minutes or to the close (16 cells per asset). Nothing later than the entry minute is used to choose
  the direction. Two nulls: (i) the notes' directions shuffled across days, best cell vs best cell, 2,000 draws (family p); (ii) placebo — the same
  rule at 14:00 on days with no statement.
- **(c) Signed by the document's own score** (what the statement means for stocks, from the v3 read): Nasdaq future, all scored statement days and
  those within ten sessions after a ≥ 4% semiconductor fall (the v3d finding at the minute level). Tested only where n ≥ 20.

## 3. E2 — the 08:30 data releases

- **Days:** release days of the BLS documents already read (jobs, CPI, PPI, JOLTS, import/export prices; those within ten sessions after a ≥ 4% move).
- **Rules, each on the S&P and Nasdaq futures, entries 1 / 5 / 15 / 30 minutes, holds 15 / 30 / 60 minutes / to the close:** *continuation* (enter in
  the direction of the S&P future's own first k minutes; negative = the first move reverses), *score* (enter in the direction of the document's
  composition score), *score disagrees* (only days where the first 5 minutes went against the score; entries from 5 minutes).
- Also measured: how often the first 5 minutes agree in sign with the score.

## 4. Verdict rule (fixed before running)

- **Primary — gold in E1(b).** GRADE A candidate if family p < 0.05 AND the best cell differs from the placebo days at p < 0.05 AND its mean exceeds
  the 2 bp cost. Otherwise the gold–Fed finding stays grade B, with (a) saying whether the move sits before, at, or after the release.
- **Secondary — the other eleven families** (E1b S&P, Nasdaq, note; E1c two sets; E2 three rules × two futures): reported; one counts only at family
  p < 0.005 (0.05 ÷ 11). Code check on synthetic noise before delivery returned family p of 0.025 and 0.052 in two of twelve families — as chance
  allows — which is why the secondary bar is strict.
- Any candidate then needs its own registered rule and a forward log before it is called a signal.

## 5. Priors (Claude, before any run; counted if wrong)

- **#136** E1(a), gold: more than half of the whole-day signed move sits in the first 30 minutes after the release, and less than 20% in the stretch
  from 30 minutes after to the close.
- **#137** E1(b), gold: not a grade A candidate — after waiting even one minute for the note's direction, no cell clears family p < 0.05.
- **#138** E2: no secondary family reaches p < 0.005; the first 5 minutes agree with the composition score on 50–60% of days.
- **#139** release-time detection: 14:00 on at least 90% of statement days from 2013.

## 6. Limits stated

Futures, not the ETFs or single stocks; the Nasdaq future is an imperfect stand-in for semiconductors (daily correlation 0.86). Speeches are not in
this round (their release minutes are not yet collected). Unscheduled statements (for example March 2020's emergency actions) fall outside the three
candidate times; the detected time on such a day is the best of the three, not the true one. E2 covers only release days that follow a ≥ 4% move.

## 7. Results

| date | test | result | verdict | prior |
|---|---|---|---|---|
| 2026-11-12 | E1 release-time detection | 132 statement days 2011-01-26 → 2026-10-28; from 2013 the note's largest 5-minute move falls at 14:00 on 78% of days, at 14:15 or 12:30 on the rest — on quiet days the largest of three small moves is arbitrary, so the detected time is noisy. | the detection rule is imperfect; amendment below fixes 14:00 from March 2013 | **#139 wrong (counted)** |
| 2026-11-12 | E1(a) when the move happens (signed by the note's whole-day direction) | gold: whole day +48.3 bp (n 130) = before the release +11.2 + first 5 minutes +10.1 + minutes 5–30 +9.1 + 30 minutes after → close +17.9. So 23% is in before the release, 21% in the first five minutes, and 56% after the first five minutes. The 10-year note itself: +35.7 = +15.1 + +5.1 + +4.0 + +11.6. | The day's link is spread over the whole day; most of it comes AFTER the release, and the largest piece after 14:30, when the Chair's press conference brings new information. Caution: this cut is signed by where the note ended the day, which is not known at the release. | **#136 wrong (counted)** — predicted over half in the first 30 minutes and under 20% later; found 40% and 37% |
| 2026-11-12 | E1(b) **primary: gold, entering after the release in the direction of the note's first minutes** | best cell enter 1 min, hold 15: +5.9 bp, t +1.98, hit 52%, n 132; family p 0.359; placebo days mean +0.5 bp. S&P: enter 30 min, hold 60: -9.6 bp, t -1.44, hit 43%, n 132; family p 0.805. Nasdaq: enter 30 min, hold 60: -12.6 bp, t -1.68, hit 46%, n 132; family p 0.617. Note: enter 15 min, hold 60: +2.5 bp, t +1.29, hit 54%, n 132; family p 0.830. | **Gold is NOT a grade A candidate** on this rule: the note's first minutes do not tell which way gold (or anything else) goes for the rest of the day. The gold–Fed finding stays SUBJECTIVE grade B. What (a) adds: the move is not over at the release, so a reader of the statement and press conference could in principle still act — but following the first minutes is not the way. | **#137 right** |
| 2026-11-12 | E1(c) signed by the statement's own score, Nasdaq future | all statement days with a score (n 45): enter 1 min, hold close: +45.0 bp, t +2.40, hit 53%, n 45; family p 0.136; statement days within 10 sessions after a ≥ 4% semiconductor fall (n 29): enter 1 min, hold close: +55.7 bp, t +2.42, hit 52%, n 29; family p 0.124 | Large in size, not established (secondary bar p < 0.005; these are above 0.05 too) and only the 45 statements that had been scored. Hindsight in the reader cannot be excluded. Follow-up registered below: score all statements. | — |
| 2026-11-12 | E2 the 08:30 releases (303 days) | first 5 minutes agree in sign with the composition score on 57% of days. Continuation — S&P: enter 30 min, hold close: -11.3 bp, t -1.87, hit 47%, n 303; family p 0.537; Nasdaq: enter 30 min, hold close: -15.4 bp, t -2.04, hit 45%, n 303; family p 0.390. Score — S&P: enter 5 min, hold 30: +2.9 bp, t +2.45, hit 38%, n 303; family p 0.115; Nasdaq: enter 5 min, hold 30: +4.1 bp, t +2.78, hit 38%, n 303; family p 0.052. First move against the score (91 days) — S&P: enter 5 min, hold 60: +8.2 bp, t +2.10, hit 63%, n 91; family p 0.220; Nasdaq: enter 5 min, hold 60: +14.6 bp, t +3.23, hit 62%, n 91; family p 0.017. | No secondary family reaches p < 0.005. Closest: when the first five minutes went against what the document's composition says, the Nasdaq future moved toward the document over the next hour (p 0.017) — a candidate for a larger sample, not a finding. The first move neither continues nor reverses reliably. | **#138 right** |
| 2026-11-12 | **Amendment registered before running — v3e-2** | (1) **Release time by schedule:** from March 2013 the statement time is fixed at 14:00 (the published schedule); earlier days keep the note-dated rule. E1 is rerun whole (`fed --schedule`); the first run stays on record beside it. (2) **Every statement scored:** the same reader, prompt and cache (n1-doc-v3) applied to all statements in the corpus, so E1(c) runs on about 130 days instead of 45 (≈ US$1–2; `score`). Verdict rule unchanged. Priors: **#140** with the fixed time gold is still not a grade A candidate (family p ≥ 0.05). **#141** with every statement scored, the Nasdaq rule signed by the score does not reach family p < 0.05 on all statement days — the +45 bp shrinks by more than half. | — | — |
