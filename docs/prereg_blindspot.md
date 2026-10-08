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

