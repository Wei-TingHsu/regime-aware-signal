# PRE-REGISTRATION — document reader schema v2

**Written 2026-08-26. No v2 read has been performed. No v2 data exists.**

*This document is written from the measured deficiencies of v1
(`v1-2026-08-23`, 2,616 documents, one prompt version, one model), recorded in
`docs/read_audit_results.md` on 2026-08-25. It specifies v2 before any v2 output
can influence its design. If v2 is never funded, this file is the roadmap
artifact; if it is funded, this file is the registration.*

---

## 1. WHY v1 IS NOT BEING PATCHED

v1 is the schema the step 3 estimator was built blind against and the schema the
specificity gate passed on. Changing it now would break the blind build and
invalidate a gate result already recorded. Re-reading 2,616 documents under a
new schema costs an estimated **$200–400** at measured token rates.

Therefore: **v1 ships with its limitation declared and diagnosed. v2 is
registered now and executed only if funded.** Any partial adoption — v2 on new
documents, v1 on old — is explicitly rejected in §6.

## 2. THE MEASURED DEFICIENCIES v2 ADDRESSES

Each is a number from the audit, not an impression.

### D1 — Five macro axes cannot represent a sector shock

`direction` has exactly five axes: equity, duration, gold, dollar, oil. A
Section 232 steel tariff's first-order effect is on steel and aluminium
equities and on downstream input costs. There is no axis for that.

The evidence that this is a *schema* limit and not a *reader* failure:

| `political_order` class | n | specificity | max\|dir\| |
|---|---|---|---|
| baseline (all) | 873 | 0.550 | 0.073 |
| TARIFF / trade action | 235 | **0.669** | 0.129 |
| SANCTIONS / blocking | 100 | 0.632 | 0.098 |
| ceremonial / administrative | 135 | 0.475 | 0.037 |

The reader identifies tariff documents as markedly more specific than baseline
and more specific than ceremonial documents — it knows what it is looking at.
Its direction barely moves because it has nowhere to point.

### D2 — FOMC `direction` is guidance-net and this is undocumented

Six genuine rate hikes read with positive `direction.duration`. Every one
carried softening forward guidance in its own evidence quotes: "only gradual
increases", "spending and production have softened", "cumulative tightening…
the lags", "the extent to which". `stance` was correctly hawkish on all six.

The reader is putting the decision in `stance` and the net of the guidance in
`direction`. That is coherent and arguably correct, and no document said so
until the audit found it. `corr(stance, dir_duration)` = **−0.802** on
statements and **−0.527** on minutes, confirming the fields are consistent.

### D3 — Truncation degrades the read, measurably

| | n | specificity | confidence |
|---|---|---|---|
| whole (EX-99 press releases) | 645 | 0.696 | 0.610 |
| truncated at 20,000 words (6-K submissions) | 26 | **0.458** | **0.431** |

Confounded with document type, as stated in `assess_8k.py`. Reported, not
adjusted for.

### D4 — `novelty` tracks content, not publication lag — and this is correct

FOMC statements read at the *lowest* novelty of the market sources (0.289),
which is right: they are the most telegraphed documents in finance. **This is
not a deficiency and v2 must not "fix" it.** It is recorded here because a test
built on the opposite assumption was run in Week 15 and its premise, not the
field, was wrong. v2 documents the intended meaning so the mistake is not
repeated.

## 3. THE v2 CHANGES

**C1 — Add a sector object, do not add fixed sector axes.**

```
"sector": {"name": <string or null>, "direction": <float -1..+1>}
```

`name` is drawn from a closed list fixed in the prompt (semiconductors, steel
and aluminium, energy, defence and aerospace, autos, agriculture, pharma,
financials, retail and consumer, transport and logistics, utilities), or `null`
when no single sector dominates. A fixed axis per sector was rejected: it
inflates the schema, most axes are null on most documents, and the closed list
can be extended in v3 without changing the shape.

**C2 — Split FOMC direction into decision and guidance.**

```
"direction_decision": {...}, "direction_guidance": {...}
```
on FOMC sources only. `direction` is retained as the guidance-net figure so that
v1 and v2 remain comparable on it. This makes D2 explicit rather than emergent.

**C3 — Document `novelty` in the prompt** as "how much of this document's
content was not already public", explicitly not "how recent is it".

**C4 — Lower `max_words` for `earnings_8k` to a value chosen by measurement,**
not by guess. Registered procedure: read 15 uncached over-cap documents at each
of 3,000 / 6,000 / 12,000 words, compare specificity and confidence against the
whole-document arm (0.696 / 0.610), and take the smallest cap whose mean
specificity is within 0.05 of it. If no cap qualifies, keep 20,000 and report
the degradation as a limitation.

**C5 — The five macro axes are unchanged.** Their definitions, sign conventions
and negligibility floor stay exactly as v1. This is what makes v1 and v2
comparable at all.

## 4. ACCEPTANCE CRITERIA, REGISTERED BEFORE ANY v2 READ

v2 is adopted only if all three hold on a **100-document paired pilot** — the
same 100 documents read under v1 and v2, stratified across all five sources.

- **A1 — Backward compatibility.** On the five macro axes, mean absolute
  difference between v1 and v2 direction < 0.10, and sign agreement ≥ 85% on
  documents where both are non-negligible. If v2 moves the macro axes, it is not
  an extension, it is a different instrument, and the v1 results cannot stand
  beside it.
- **A2 — The deficiency is actually fixed.** On the TARIFF / trade action class,
  v2 `sector.direction` is non-negligible (|value| > 0.05) on ≥ 60% of
  documents, against v1's max\|dir\| mean of 0.129. If v2 also reads them flat,
  the schema was not the binding constraint and D1 was misdiagnosed.
- **A3 — No degradation elsewhere.** v2 mean specificity on `fomc_statement`
  and `earnings_8k` is not below v1's by more than 0.05.

**Failure of any criterion means v2 is not adopted and the pilot cost is
reported as spent.** A pilot that fails is a result.

## 5. WHAT v2 DOES NOT CHANGE

- The specificity gate result (PASS, spread 0.517, CI [0.494, 0.539]) stands on
  v1 and is not re-run on v2 unless v2 is adopted in full.
- The step 3 estimator, built blind against v1, is not rebuilt. If v2 is
  adopted, the estimator is **re-run**, not re-specified — its code is frozen.
- λ = 0.0008 in `config.yaml` remains the reproduction constant.

## 6. THE MIXED-CORPUS PROHIBITION

**v2 on some documents and v1 on others is forbidden.** A cross-source
comparison that is also a cross-schema comparison cannot be interpreted, and
`gate_check` would report the read condition as mixed with no way to separate
schema from corpus — the same confound the read-condition check exists to
detect. Either the whole corpus is re-read under v2, or none of it is.

The one exception is the 100-document paired pilot in §4, which is *designed* to
be cross-schema, is never merged into the production CSVs, and is written to
`processed/pilot_v2/` outside every glob `gate_check` reads.

## 7. COST AND TRIGGER

| item | documents | estimated cost |
|---|---|---|
| paired pilot (§4) | 100 | ~$5–10 |
| full re-read, if adopted | 2,616 + 163 deferred | ~$200–400 |
| political corpus, if read at all | 2,921 newly fetched | separate decision |

**Trigger:** the pilot runs only when there is budget to run the full re-read if
it passes. Running the pilot without that budget produces a validated schema
that cannot be used and spends money to learn nothing actionable.
