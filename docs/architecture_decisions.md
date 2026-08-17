# Architecture decisions — engine timing, aggregation, and event-engine scope

*Design principles agreed before building the multi-engine ensemble. Recorded so
the reasoning survives, and so the forward-test harness is built extensible
rather than baked to macro-only assumptions.*

---

## 1. One shared execution clock — not one clock per engine

An earlier draft proposed giving each engine its own trading clock (slow for
macro, fast/event-anchored for the news engine). **That was rejected as
over-complex and out of scope.** The corrected principle:

> **All engines share ONE daily execution clock, with next-open entry.**

- **Signal date** = the last completed US (NYSE) close in the data.
- **Entry** = the *next* US session — never the same bar the signal was computed
  from (that would be look-ahead and untradeable in reality).
- **Exit** = H trading days after entry, H set per engine.

The local timezone (SGT) is irrelevant except to know whether a new US close has
landed. Run the daily command any time after ~05:00 SGT (US close is ~04:00 SGT)
to reliably capture the prior US session. If no new US close exists since the
last run, the harness **skips** rather than logging a duplicate row.

Engines differ in **how often their target exposure updates**, not in when they
trade:

| Engine | Target-exposure update | Horizon | Overnight gap |
|---|---|---|---|
| Macro analog | daily, slow drift | 5–20d | immaterial |
| Rotation chain | when a rotation is active, else flat | multi-week | immaterial |
| Event / GDELT | spikes on a daily-detected trigger, then decays | days | conceded, not traded |

---

## 2. Aggregation happens in POSITION space, not trade-time space

The question "how do you combine engines that fire at different times?" dissolves
once signal is separated from execution:

- Each engine emits, for each asset, a **target position** in `[-1, +1]`
  (desired exposure), **not** a discrete "trade now" instruction.
- Between its own updates, an engine's target simply **persists**.
- A **combiner** sums the engines' targets (weighted by track record / Sharpe)
  into **one net target position per asset**, and that net position drives the
  single daily trade.

Consequences:

- Fast and slow signals coexist naturally — the event engine's spike simply adds
  to the macro engine's slow drift at the moment the combiner looks.
- Agreement between engines → reinforced conviction (larger net position).
  Disagreement → partial cancellation (small net position). This is the
  noise-cancellation that lifts *ensemble* Sharpe above any component's.
- This is the standard multi-strategy architecture: strategies keep books of
  target exposures; a risk layer nets them; execution runs on one schedule.

**Why this matters for the project's headline number:** a standalone signal
Sharpe of ~0.4–0.5 is not a fundable product on its own, but combining several
weakly-correlated signals of that quality is the normal route to a materially
higher ensemble Sharpe. The macro engine is one ingredient, not the finished
recipe.

---

## 3. Event-engine scope: trade the post-gap drift, do NOT model the overnight gap

Events (earnings line-items, fireside chats, technology breakpoints) often land
**after** the US close, and the close→open gap prices much of the move in before
anyone can trade it.

Quantifying *what fraction of an event move survives the overnight gap* would
require microstructure and company-valuation modelling — a research topic in its
own right, **beyond this project's scope**, and not validatable on daily bars.

**Decision: do not model the gap. Define the strategy so it does not depend on
the gap.**

- Concede the overnight pop as uncapturable; make no claim on it.
- Trade only the **multi-day continuation after the market has reopened and
  repriced**, entered at the next open like every other engine.
- This is the **Post-Earnings-Announcement Drift (PEAD)** phenomenon: documented
  by Ball & Brown (1968), formalised by Bernard & Thomas (1989–90), and
  replicated widely since — prices under-react to news and keep drifting in the
  same direction for weeks.

Two honest caveats attached to that literature:

1. Classic PEAD is measured on **earnings surprises vs analyst estimates**. Our
   trigger is **GDELT news density** — broader and fuzzier. Whether PEAD-like
   drift extends to GDELT-detected narrative events is an **open empirical
   question**, not an assumption. (It is also a legitimate research contribution
   in its own right.)
2. PEAD has **weakened since the 1990s** as it became widely traded. Expect a
   modest effect at best.

### Consequence: the event engine's Stage 1 is a drift-existence test

Before building any event trader, run the same discipline used everywhere else:

1. Identify GDELT event days (event-density spikes on the focus assets).
2. Measure focus-asset returns over the following 1 / 5 / 10 / 20 days,
   **entered at the next open** (conceding the gap).
3. Permutation-test that drift against matched random non-event days.

- **Significant post-gap drift** → PEAD-like behaviour exists in the GDELT
  signal; the event engine is viable on a daily clock, and a textbook anomaly has
  been shown to extend to news-density triggers.
- **No drift** → events fully price in overnight; a daily-clock event trader is
  not viable, which cleanly caps the scope. This is an honest finding too.

Either way the conclusion is earned from the data, not borrowed from the
literature.

### Bonus: this also solves the token-cost problem

Because the engine trades multi-day drift on a daily clock, it needs to check for
events **once per day**, alongside the macro data pull — not a continuous,
always-on news stream. No real-time monitoring, no per-moment LLM/API burn.

---

## 4. Summary of what this means for the build

- The forward-test harness runs **one daily command**, shared by all engines.
- Its timing logic is **modular**, so additional engines slot in without changing
  the execution convention.
- The scoreboard records per-engine picks now, and is extensible to a **combined
  net position** row once more than one engine is live.
- The event engine, when built, must pass its **drift-existence test** before any
  trading claim is made.
