# Pre-registration — T13 case A: the blind-spot flag, and the commodity-shock chain

*Registered 2026-10-08, before any code. From the two-wars review (TRACK §3.14): the engine held
no document on 28 Feb–9 Mar 2026 while gold fell 4% in two sessions and oil jumped; a strike is
not a filing. The engine must say, each day, how much of the move its sources can account for.*

## 1. What is measured, every session

For each of the five markets, after the close:

- `z_t` — the day's log return divided by its own EWMA volatility (λ 0.94, through t−1). A
  *big move* is |z_t| > 2.
- `covered_t` — whether any document the engine read, dated to session t, carries a non-zero
  direction on that market's axis (|direction| > 0.05).
- The flag, three states, per market:

| state | condition | meaning |
|---|---|---|
| **A — blind** | big move, no covering document | the engine did not see the cause |
| **B — wrong** | big move, covering document, sign of `net_view` opposite to the move | the engine saw a cause and read it backwards — the dangerous case |
| **C — seen** | big move, covering document, same sign | the engine's sources account for it |
| — | no big move | nothing to flag |

Forward haircut (roadmap T13): `haircut_a = 1 − 0.5 · B_rate_a`, where `B_rate_a` is the
exponentially weighted share of that market's big-move days in state B (half-life 20
sessions). Multiplies the *displayed* confidence only; never the estimate, never the
abstention floor.

## 2. The commodity-shock chain — a named detection template

The two wars moved gold through one chain: oil up → inflation expectations up → expected policy
rate up → dollar up → gold down. Every link but the first is already in the macro panel. The
template fires a **chain alert** when, within any 5-session window:

1. oil (`USO`, and `WTI_CONT` once added) has a big move up (|z| > 2, positive), and
2. DGS2 rises ≥ 10 bp over the window, and
3. DTWEXBGS rises over the window.

On a chain alert the app shows, on the gold card: *"Oil shock chain: oil, the 2-year yield and
the dollar all rose this week. On the two named precedents (2022, 2026) gold fell over the
following months. The engine has no document explaining the oil move."* — plus the three
numbers. **No direction number is issued from the template**; it is a flag with two precedents,
and the registered test below decides whether it ever earns more.

## 3. Test on the backfill — criterion, fixed

Over 2006–2026 daily data (no documents needed for part 2):

- **A1.** Share of big-move days per market in each state; reported. Expected: state A
  dominates for gold and oil (their drivers are rarely filings), state C is largest for TLT.
- **A2 — does the chain alert predict?** For every chain-alert date, gold's forward 20- and
  60-session return versus the unconditional distribution, permutation null over random dates
  with the same calendar spacing, 10,000 draws. **PASS** if the 60-session mean is negative at
  p < 0.05 with ≥ 10 alerts; **INCONCLUSIVE** if negative but p ≥ 0.05 or fewer than 10 alerts;
  **FAIL** otherwise. Prior: INCONCLUSIVE — the chain is plausible, two cases are two cases, and
  2008 (oil up, then everything down) will dirty it.
- Only a PASS allows the gold card's chain alert to carry a direction; otherwise it stays a
  flag with its precedents named.

## 3b. A3 — after an oil shock: how far, how long, how much to hold (registered 2026-10-16, before code)

**Why.** The chain alarm fires five times in thirty years — enough to notice, not enough to fit. The founder's question
(16 Oct) is whether, once the pattern starts, the engine can say how far the remaining move goes, how long it lasts, and
how much leverage the history supports. That needs a larger pool: the alarm's first leg alone.

**A3a — the pool and the path table (descriptive, no verdict).**
- *Primary pool:* every session on which WTI_SPOT's 5-session log return first reaches ≥ +8% (a new event only after 20
  sessions without one, so one shock is one row). Expected size 1995→2026: 40–60. *Secondary pool, table only, never for the
  estimate:* the same at ≥ +5%.
- *For each shock and each of the five markets (SPY, TLT, GLD, UUP, USO — plus WTI_SPOT itself):* the forward log return at
  5, 10, 20, 40, 60 and 90 sessions; the **worst interim loss** and the **best interim gain** of a position taken at the
  shock close and held 60 sessions, with the session on which each extreme occurred (the duration measure); the **Sortino**
  of that 60-session position (mean daily return ÷ downside deviation, annualised, risk-free 0).
- *Reported:* median and inter-quartile range of each quantity across the pool; the five chain firings marked as a subset;
  the three legs at the shock (dollar 5-session, two-year 5-session change, regime label) listed per row.
- *Status:* measured. The table may be shown on the app as history under the alarm, labelled with n and the pool rule.

**A3b — the conditional estimate (nearest-neighbour, honestly named).** For a shock on day t: the estimator of
prereg_analog_event — kernel weights on the three legs and the regime, recency half-life as registered there, ESS floor 8 —
applied to the earlier shocks only, gives a weighted median path and a weighted median time-to-extreme for each market.
*Criterion, walk-forward over every shock after the 15th:* PASS if (i) the conditional estimate's sign at 20 sessions
matches the realised sign on ≥ 60% of shocks where ESS ≥ 8, against the unconditional pool median's share; and (ii) the
estimated time-to-extreme is within ±10 sessions of the realised one on ≥ 50% of those shocks. INCONCLUSIVE if (i) holds
and (ii) does not; FAIL otherwise; UNTESTED if fewer than 15 shocks reach ESS ≥ 8. Permutation null for (i): shuffle the
leg vectors across shocks, 10,000 draws.

**A3c — the leverage rule (fixed here, not fitted).** For a market with a conditional estimate: *L = min(5, 0.20 ÷ q90)*,
where q90 is the 90th percentile of the unlevered worst interim loss across the pool's past shocks in the estimate's
direction, and 5× is the hard ceiling (founder, 16 Oct). The loss limit 0.20 = 20% of capital (founder, 16 Oct, raised from a first draft of 10% before any code). L is
further capped by the T1 vol-target exposure for that market on that day. Reported with the past worst case at that L.
What the rule does not claim: the next drawdown can exceed any past one; L is "what this history supports", never a
guarantee. Costs: the T1 cost table applied at the entry and exit.

**What the app may show.** Nothing from A3b or A3c until A3b PASSES and today's ESS ≥ 8; then one line under the gold
card's alarm: "after past oil shocks like this one: median −x% by session N (IQR), worst past interim loss y%, history
supports ≤ L× (n, ESS)". The A3a table may be shown as history at any time.

**Priors, stated.** A3a: median gold path after the +8% pool is negative at 20 and 60 sessions but smaller than after the
five chain firings (the rebounds dilute the wars); worst interim loss median 3–5%, so q90 near 8–10% → L near 2–2.5×, below the 5× ceiling. A3b: (i) PASS-weak around 60–65%; (ii) FAIL — timing is harder than sign. A3c: a number, not a
verdict. Contamination: the five chain dates and their gold paths were seen before this was written; the +8% pool was not.

## 4. Provisional source pool — first admissions

Admitted with today's date, scored only on later days, per roadmap T13:

| class | fetch | what it would have carried on 28 Feb 2026 |
|---|---|---|
| `treasury_ofac` | Treasury press releases + OFAC recent actions (public RSS/JSON) | sanctions designations, the same day |
| `whitehouse_statement` | whitehouse.gov briefing-room statements and releases | the strike announcement itself |
| `commodity_shock` | not a document source — the chain template above, logged as a pseudo-document when it fires | "oil shock, no filing" |

Read cost per class stated from a 20-document token sample before any paid read; each needs a
`PROFILES` entry reviewed by the founder line by line.

## 5. What the app shows (registration §4 of prereg_event_time applies by analogy)

Per market card, a third line: *"Coverage: this market moved 2.8σ today; the engine's sources
carry no document on it (blind)"* / *"… read it backwards (wrong)"* / *"… account for it"*. On
quiet days the line is absent. The displayed confidence carries the haircut, shown as "confidence
62% (haircut 0.9 from recent misreads)". The chain alert appears on the gold card as in §2.

## 6. Amendments

| date | change | reason |
|---|---|---|
| 2026-10-08 | **Chain rule replaced: v0 → W2-seq**, after calibration against the two wars (founder's requirement: fire inside both, not outside). v0 fired 23 times in 2006–2026 and A2 was FAIL on it (gold +0.85% after 60 sessions, p 0.28) — recorded, not hidden. W2-seq: oil 5-session return ≥ +8% **and** dollar 5-session ≥ +0.9% **with the 2-year's 5-session change < +10 bp at that session** (the shock arrives through oil, not rates), then the 2-year reaching ≥ +10 bp within 5 sessions. Fires on Ukraine (shock 1 Mar 2022, confirm 7 Mar) and Iran (shock 3 Mar 2026, confirm 5 Mar) and on the May 2026 re-escalation; drops the two rates-first episodes (4 Oct 2024 — Iran missile strikes on Israel; 12 May 2025 — US–China tariff truce), after both of which gold rose. Mechanism: an oil-exporter war moves oil first and rates follow; a macro print moves rates first and oil follows. Calibration record: `docs/chain_calibration.md`, `docs/chain_calibration_round2.md`. **A2 re-runs on W2-seq**; its prior is now contaminated (the rule was chosen with the two wars' gold path in view) and is declared so: expected PASS on the named cases, n too small for p < 0.05 — INCONCLUSIVE | Founder's requirement; rule chosen from the calibration tables, with the mechanism stated |
| 2026-10-12 | **Chain-rule input: USO → WTI_SPOT (FRED DCOILWTICO).** The rule W2-seq is about an oil-price shock; USO is a proxy whose roll drag (−8.7%/yr vs spot over 2006–2026; 2020: USO −68% vs spot −21%) kept its 5-session return under +8% in early 2009, hiding two firings. On spot the rule fires 4× (26 Jan 2009, 24 Feb 2009, 7 Mar 2022, 5 Mar 2026); gold was lower 60 sessions after every firing (−1.8%, −2.6%, −7.6%, −11.8%; mean −6.0%, p 0.009, n 4 → still INCONCLUSIVE by the n ≥ 10 bar). USO's two-firing record stays on file beside it. **Contamination stated:** the mechanism argument (read the commodity, not the ETF) is clean; the decision was taken after seeing that gold also fell after the 2009 firings, so the timing is not. A2's prior stays INCONCLUSIVE; forward firings are the test. **Live rule:** FRED publishes spot with a lag of up to a week, so the nightly alarm evaluates on WTI_SPOT where published and on CL=F (Yahoo, same day; daily correlation 0.93) for the unpublished tail; an alert raised on the CL=F tail is marked *provisional* and confirmed or withdrawn when spot lands. Implementation in blindspot.py is the next step. | Founder's decision 12 Oct (option 2 of two offered), instrument correction |
| 2026-10-13 | **A2 on WTI_SPOT, full panel (1995→), implemented.** 5 firings (26 Jan 2009, 24 Feb 2009, 6 Feb 2015, 7 Mar 2022, 5 Mar 2026); gold −5.7% at 60 sessions, p 0.0066; INCONCLUSIVE (n < 10), prior held. Live rule in `blindspot.py`: spot where published, CL=F tail, alerts on the tail marked provisional; spot lag observed one session. USO's record printed beside. | Result, rule as amended 12 Oct |
| 2026-10-16 | **§3b A3 added before code:** oil-shock pool (+8% primary, +5% table only), path table with worst interim loss / best gain / time-to-extreme / Sortino, nearest-neighbour conditional estimate with walk-forward criterion, leverage rule L = min(5, 0.20 / q90) capped by T1. Founder set the loss limit (20%, raised from a 10% draft before code) and the ceiling (5×). | Founder's question 16 Oct: how far, how long, how much to hold |
