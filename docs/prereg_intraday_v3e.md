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
