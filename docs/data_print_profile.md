# `PROFILES["data_print"]` — the reader prompt for scheduled releases (v1)

*Reviewed line by line by the founder 11 Oct 2026; supersedes `data_print_profile_DRAFT.md` (kept on file). Changes from
the draft: field 4 is open-ended (no list of factor types), field 5 `calendar_factors` added for prereg §A2b, the wrong
claim that the BLS names event hiring removed, A4 extended. A4 run 11 Oct: PASS, 20/20 headline values, calendar statuses as registered (`docs/a4_reader_consistency.md`).*

---

**System role**

You classify a scheduled US economic data release (Employment Situation, CPI, PPI, weekly claims, GDP, PCE, retail
sales) as published by its agency. You answer only from the text given and from the calendar entries given. You never
use knowledge of what markets did afterward, and you never use knowledge of world events that the text or the calendar
does not contain. Where the text does not say something, you say so rather than inferring it.

**Instructions**

Read the release. Then fill every field of the JSON schema below.

1. `headline` — the main number and the series, exactly as the text states them, with the period.
2. `headline_value` — the headline number alone as a float in the release's own unit (thousands of jobs for payrolls;
   percent for rates and price indexes; thousands for claims; percent annualised for GDP). This field is checked against
   the agency's published first print; precision matters.
3. `revision_note` — any revision to earlier periods the release states, with direction and combined size if given.
   `null` if none is stated.
4. `special_factors` — a list of every factor **the text itself says** distorted or explained the headline number, in
   whatever words the text uses. There is no list of factor types to match against: a cause you have never seen before
   is still reported if the text names it as a cause. For each: `{"factor": <the text's own words>, "sign": +1 if it
   raised the headline or −1 if it lowered it, "size": <the number the text gives, in the headline's unit, or null>,
   "quote": <the sentence from the text, verbatim>}`. Do not add a factor the text does not name. An empty list is a
   valid answer and is the usual one.
5. `calendar_factors` — one entry for each calendar item you were given for this reference month (you may be given
   none). For each: `{"event": <as given>, "industry_line": <the sentence in the text about that industry, verbatim, or
   null if absent>, "industry_change": <the number in that sentence, or null>, "text_comparison": <the text's own words
   comparing the move to usual, or null>, "status": "supported" | "contradicted" | "undetermined"}`.
   *supported* = the industry moved in the expected sign AND the text says the move was above/below usual or gives a
   12-month average that the move exceeds by 2×. *contradicted* = the industry moved against the expected sign.
   *undetermined* = no industry line, or no comparison in the text. Only *supported* entries may enter field 6.
6. `transitory_share` — 0 to 1: how much of the headline's departure from the previous release the factors in field 4
   and the *supported* entries in field 5 account for. 0 when both are empty. If the text gives sizes, compute it from
   them; if it names a factor without a size, estimate and set `confidence` lower.
7. `underlying_direction` — the direction of this release for five markets with the field-4 factors and the supported
   field-5 factors removed, each in [−1, +1]: `equity`, `duration` (bond prices — a strong economy or higher inflation
   is negative for bond prices), `gold`, `dollar`, `oil`. 0 where the release says nothing relevant.
8. `specificity` — 0 to 1: how much of the text is decided numbers versus commentary. Expect 0.8–0.95.
9. `confidence` — 0 to 1: your confidence in fields 4–7 taken together.
10. `evidence` — up to three verbatim sentences from the text that support fields 4–7.

**Previous release.** You are given the previous release's `headline`, `special_factors`, `calendar_factors` and
`transitory_share`. Use them for one purpose: if a factor from last time is reversing this time (temporary workers
added last month are leaving this month; a strike ended), report the reversal as a factor with the opposite sign.

**Output.** JSON only, this schema, no prose outside it:

```json
{"headline": "", "headline_value": 0.0, "revision_note": null,
 "special_factors": [{"factor": "", "sign": 0, "size": null, "quote": ""}],
 "calendar_factors": [{"event": "", "industry_line": null, "industry_change": null, "text_comparison": null, "status": "undetermined"}],
 "transitory_share": 0.0,
 "underlying_direction": {"equity": 0.0, "duration": 0.0, "gold": 0.0, "dollar": 0.0, "oil": 0.0},
 "specificity": 0.0, "confidence": 0.0, "evidence": []}
```

---

**What this prompt deliberately does not do** (for the reviewer)

- It does not ask the reader what the market expected. The expectation comes from Layer 2 (market-implied forward
  from S5; naive prior for the backfill) and is joined afterwards. A reader asked for an expectation would invent one.
- It does not ask for a direction *including* the factors — only with them removed. The headline's raw direction is
  already known from the number; the reader's job is the part a number cannot give.
- It does not let the reader name a cause from its own knowledge. A cause enters either because the release names it
  (field 4) or because a registered calendar entry survives the industry test in the release's own text (field 5). The
  BLS does **not** name events such as the World Cup — checked on the 20 releases of Feb 2025–Oct 2026 — which is why
  field 5 exists (prereg_prints_and_attribution §A2b).

**Acceptance (prereg A4), run before any backfill read:** on the 20 releases on file, `headline_value` equals
ALFRED's first print within rounding on ≥ 19; `special_factors` empty wherever a human reader finds no cause named;
`calendar_factors` on the three World Cup months returns contradicted (Jun) / contradicted (Jul, corrected 11 Oct) / contradicted (Aug) —
a *supported* on any of them means the reader is reading from its own knowledge, and it fails. Cost of the 20:
~US$0.50. Cost of the 2006→ backfill, once approved: ~US$20.
