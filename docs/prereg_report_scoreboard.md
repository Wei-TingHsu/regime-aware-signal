# Pre-registration — report-level scoreboard

*Draft 2026-09-08; committed 2026-09-14 with three placeholders, filled the same
day by amendment (§11) so the order of decisions stays visible. No `[FILL]`
remains. No code exists; every threshold below precedes `src/report_scoreboard.py`.*

**Why this exists.** `docs/forward_scoreboard.md` scores the three frozen
price models. Nothing scores the decision report itself — the artefact the
business plan sells. Source expansion (TRACK §3.1, §3.2 and any addition) will
change what the report says on what days, and without a registered metric there
is no way to state whether an expansion helped, hurt, or did nothing. This
document registers that metric before any source is added.

**What it does not do.** It does not touch `models.yaml`, the forward ledger,
`prereg_analog_event.md` §5 (the pooled LOO test, already run), or the reader
prompts. It scores the *emitted* report, as a user would read it.

---

## 1. UNIT OF OBSERVATION

One row per **(report date `t`, asset `a`, horizon `h`)** where the report at
`outputs/reports/YYYYMMDD.json` emitted a **net view** for `a` — i.e. a signed
`net_direction[a]` with a tier.

Rows are **excluded** when the report:
- abstained (`ESS < 8`), or
- flagged divergence and issued no combined figure (§6.2 of the analog-event
  registration), or
- carried no document that day.

Those three exclusions are not dropped silently: they are counted and reported
as **coverage** (§4).

## 2. THE CALL AND THE OUTCOME

- **Call** = `sign(net_direction[a])` from the report. A net direction of
  exactly zero is not a call and is excluded (counted under coverage).
- **Realised return, PRIMARY** = log close-to-close return of `a` from the
  **close of `t`** to the close `h` sessions later, NYSE sessions via
  `trading_days()`. This is the estimand the estimator was built on (analog
  event §2, close-of-document-date entry) and is what the report's number claims.
- **Realised return, TRADEABLE** = log return from the **open of `t+1`** to the
  close `h` sessions after `t+1`. This is what a reader of the report could
  actually do (architecture decisions §1, next-open entry). Reported beside the
  primary on every table, never substituted for it.
- A realised return of exactly zero counts as a **miss**.

Horizons: **`h ∈ {3, 5, 20}`** — the set registered in `unblind_step3.py`
(`HORIZONS = (3, 5, 20)`), so the scoreboard and the estimator it scores share
one clock. Primary horizon **`h* = 3`**, matching the estimator's own registered
primary. Nothing at any other horizon is a
primary result.

## 3. METRICS

For a set of rows `R`:

| metric | definition |
|---|---|
| **hit-rate** | fraction of rows where `sign(call) == sign(realised)` |
| **asymmetry** | `mean(|realised| over hits) / mean(|realised| over misses)` — the win/loss magnitude ratio |
| mean signed return | `mean(call · realised)` — reported so a hit-rate can be read against a mean (a hit-rate above 50% with a negative mean is possible and would be said so) |
| profit factor | `Σ(call·realised, hits) / |Σ(call·realised, misses)|` — descriptive only |

Both **hit-rate** and **asymmetry** are the registered pair. Mean signed return
and profit factor are reported, never tested.

### 3.1 Overlap

Daily reports at horizon `h` share `h−1` sessions. Every table carries two
columns, as the forward scoreboard does:

- **naive** — every row;
- **non-overlap** — every `h`-th report date per asset, first date fixed at the
  first report. **Only non-overlap rows enter any test.**

### 3.2 Minimum count before a figure is printed

**No hit-rate or asymmetry is printed for any cell with fewer than 30
non-overlap rows.** Below 30 the cell prints its row count and the words "too
few to report". This is the rule the forward scoreboard already applies to
matured trades and it is not relaxed here.

## 4. COVERAGE — reported before any metric

Per calendar window, before any hit-rate:

- sessions in window;
- sessions with ≥1 document read;
- sessions where the report emitted ≥1 net view;
- per asset: count of net views, abstentions, divergences, tier 1 / 2 / 3.

Coverage is the number source expansion is expected to move first. A source
that raises coverage and leaves hit-rate unchanged has still done something;
a source that raises hit-rate on a coverage that fell has done something worse.
Both are only visible if coverage is printed first.

## 5. THE NULL

Hit-rate has no natural 50% baseline: most equity assets drift positive, so a
report that said "up" every day would clear 50%. The null must preserve the
return paths and destroy only the correspondence between the report's call and
the date.

> **Null:** within each asset, permute the vector of calls across report dates
> in **contiguous blocks of `h*` report dates**, keeping every realised return
> in place. 10,000 draws. Hit-rate and asymmetry recomputed on each draw on the
> non-overlap rows.

Block permutation rather than free permutation because calls are serially
correlated (the same regime and the same documents persist for days). Free
permutation would understate the null's spread.

This is the same construction as `conditional_order.py` and the analog-event
§5.3 null, with calls in the role of weights.

## 6. THE CRITERION

Pooled across all assets, at `h*`, non-overlap rows, ≥ 30 rows:

> **The report passes if hit-rate exceeds the 95th percentile of the null AND
> asymmetry exceeds 1.0 with a 95% block-bootstrap lower bound above 1.0.**
>
> One of two is **not** a pass. Reported as **inconclusive**, with both numbers.

Per-asset, per-tier, per-source, per-regime and per-horizon breakdowns are
**reported in full and tested in none**. A breakdown that looks good is a
hypothesis for a later registration, not a finding.

### 6.1 Tier check — registered expectation

The tiers exist to grade evidence. If they mean anything, tier 1 rows should
show a higher hit-rate than tier 3 rows. **Registered expectation: tier 1 ≥
tier 3 on hit-rate.** If tier 3 beats tier 1, that is reported as the tiers
failing to grade, and the report's tier language is reviewed. Not a test —
an expectation whose reversal is a finding in its own right.

## 7. TWO LEDGERS

### 7.1 Forward ledger — primary, never rewritten

Every report emitted **write-once** under `outputs/reports/`, scored as it
matures. Appended by the nightly run; a row is never edited after it matures.
Same discipline as `forward_ledger.csv`.

**Start date — corrected 2026-09-14.** Reports dated 27 Aug–11 Sep were
regenerated nightly until the freeze of 13 Sep (`e740751`); their "as emitted"
versions do not exist, and they are treated as backfill. Nightly document reads
are paused for API credit as of 14 Sep, and a report written while its session's
documents sit fetched-but-unread would be frozen incomplete. The forward ledger
therefore starts at **the first session whose report is written with all of its
fetched documents read** — i.e. the first session after reads resume. That date
is recorded in §11 when it happens; it is not chosen in advance.

### 7.2 Backfilled ledger — how source expansion is judged

The forward ledger will not reach 30 non-overlap rows per cell for months.
Source expansion needs a verdict sooner than that, so a second ledger is
registered:

- Run the **full live-basis pipeline** (expanding-window standardisation,
  expanding regime labels, step 3 estimator with **leave-one-out on the query
  document**, §7.2 fixed weighting, step 6 report) on **every historical
  document date in the corpus**, emitting a report per date to
  `outputs/reports_backfill/<corpus_hash>/`.
- Score it with §1–§6 exactly as the forward ledger.
- **The backfilled ledger is regenerated whenever the corpus changes** and is
  versioned by a hash of the read cache. Ledgers with different hashes are
  compared, never merged.

It is out-of-sample in the leave-one-out sense and not in the forward sense;
every table says which ledger it came from.

## 8. SOURCE EXPANSION — the rule this document is for

Before any source is added, its own short pre-registration states, against
the **current** backfilled ledger:

1. expected change in coverage (sessions with ≥1 net view), as a number;
2. which axis the source is expected to load on;
3. the expected direction of change in pooled hit-rate at `h*` — including
   "none expected", which is a legitimate registration.

After the read, the new backfilled ledger is scored and compared to the old one
**on the days both cover** (paired) and **on the new days only** (unpaired):

> **A source is retained in the pooled corpus if coverage rose by at least the
> registered amount AND, on the shared days, pooled hit-rate at `h*` did not
> fall by more than 2 percentage points (point estimate) AND the block-bootstrap
> 95% lower bound of the change is above −5 points.**
>
> The point-estimate part catches real degradation; the lower-bound part stops
> the rule firing on noise alone at small n (hit-rate SE ≈ 0.5/√n: ~5 points at
> n=100, ~3 at n=300).

**Revising the tolerance.** These two numbers are a first setting, not a
finding. They may be changed by a dated §11 amendment recorded **before** any
source comparison is run against them. Once a comparison has been run, the
tolerance in force at that time is frozen for that comparison; a later change
applies only to later sources. A tolerance moved after a result has been seen
is not a criterion, and this document does not permit it.
> Otherwise it is kept in the corpus but **reported separately**, not pooled —
> the same treatment the specificity gate prescribes for a source that fails.

The specificity gate is re-run on every enlarged corpus regardless.

## 9. WHAT WOULD MAKE THIS FAIL, STATED IN ADVANCE

- The backfilled ledger has fewer than 30 non-overlap rows at `h*` after
  exclusions — the report abstains too often to score. Then coverage is the
  only figure and this document says so.
- Hit-rate clears the null and asymmetry does not — the report is right more
  often than chance and loses more when wrong. Inconclusive, and the size of
  the losses is the number to publish.
- Tier 3 beats tier 1 — the evidence grading is not grading. Reported; the
  report's tier language is amended, not the tiers' thresholds.
- The primary and tradeable columns disagree in sign on hit-rate — the
  report's number describes a window a reader cannot enter. Both stay on the
  table; the business plan's language is corrected toward the tradeable one.

## 10. WHAT IS NOT CLAIMED

- No claim that the report is a return stream. Hit-rate and asymmetry describe
  the report's calls; they are not a backtest of a strategy and carry no costs.
- No per-cell significance. Ever.
- No figure from the forward ledger until it clears §3.2 on its own.

## 11. AMENDMENTS

| date | change | reason |
|---|---|---|
| 2026-09-14 | File committed with three `[FILL]` placeholders open: horizon set, primary horizon `h*`, source-expansion tolerance (§2, §8) | The draft is recorded before the decisions are made, not after; each fill is its own row here |
| 2026-09-14 | §7.1 start date changed from 27 Aug to "first session after nightly reads resume" | Reports before 13 Sep were rewritten nightly (no as-emitted version exists); reads paused for credit from 14 Sep |
| 2026-09-14 | §2 filled: horizon set `{3, 5, 20}`; primary `h* = 3` | Set and primary taken from `unblind_step3.py` (`HORIZONS = (3, 5, 20)`, 3 primary) so the scoreboard scores the estimator on the estimator's own clock. An earlier proposal of 5 (to match Model 1) was withdrawn once the estimator's registration was read |
| 2026-09-14 | §8 filled: two-part tolerance — point-estimate drop ≤ 2 pts AND bootstrap lower bound > −5 pts | Founder's choice, 2 / −5. Revisable only by a prior dated amendment, per §8; frozen for any comparison already run |

*Amendments are recorded here before results are read. An amendment after a
result is read is declared as such.*
