#!/usr/bin/env python3
"""
patch_close_session.py -- the last two documents. Session-closing patch.

1. docs/prereg_analog_event.md section 11 is EMPTY. Four amendments were made
   to the registration during 2026-08-24/25 and exist only as chat text. The
   registration therefore does not currently match the code -- the single
   largest gap before a session handover. All four are written here, each with
   its timing declared.

2. docs/EXECUTION_PLAN.md gets a closure section: Step 1 done, the gate
   amendments, the live basis, and what is actually left.

After this, `docs/` is self-contained: regenerating briefing.md captures the
Track, every result, every registration and every amendment.

Run from the repo root:
    python patch_close_session.py --dry-run
    python patch_close_session.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

AMENDMENTS = """## 11. AMENDMENTS

*Four amendments, all made during 2026-08-24/25. Each records WHEN it was
decided relative to what had been seen, because that is the only thing that
distinguishes an amendment from a rationalisation.*

| date | change | reason |
|---|---|---|
| 2026-08-24 | §3.2 gains two scale-relative numerical guards: `DEGENERATE_VAR = 1e-9` (within-variance negligible against the data scale → τ²=0) and `TAU2_REL_FLOOR = 1e-6` (τ² negligible against within-variance → τ²=0). The registered `Q ≤ C−1 → τ²=0` rule is also applied **before** the division rather than after. | Blind acceptance test 6 caught the registered null path **silently failing to fire**. `np.var` of 80 identical float64 values returns 4.76e-38, so `W = n/s²_within = 4.2e38`, which amplified float noise in the cell means into `Q ≈ 4.2 > C−1 = 3` and produced `τ² = 2e-38 > 0` — a **Tier-1 label with w = 0.96 on data with no between-cell variation whatsoever**. The guards make the registered rule fire; they do not change it. Written before any real estimate. |
| 2026-08-25 | `political` split by Federal Register document type into `political_order` (executive order, presidential order, determination) and `political_other` (proclamation, notice, memorandum). The `EXECUTION_PLAN` gate criterion changes from a **point** spread > 0.25 to the **lower bound of a 95% bootstrap CI** > 0.25, with the pilot raised to n=60 per source. | **Both decided AFTER seeing a marginal point spread of 0.26 on n=20 — declared, not hidden.** The split is legitimate because the partition uses the **government's own type tag**, an external pre-existing taxonomy, and no document is reassigned by judgement; it also corrects `CURRENT_STATE` §8's claim that rhetoric is uncovered. The criterion change is a **tightening**: at n=20 the spread carried se ≈ 0.063, so 0.26 was indistinguishable from failing and the point criterion could not say so. Gate subsequently PASSED at 0.363, CI [0.279, 0.453]. |
| 2026-08-25 | §5.3's null gains a second implementation. **`permute_y`** (shuffle outcomes; Z, ages, σ, ESS and the whole weight geometry identical in every draw) becomes **PRIMARY**; **`permute_Z`** (the original) is **retained and reported permanently**. Both computed every run. Registered in advance: a rejection rate **below 0.02** means the null is conservative, and a step 3 null must then be reported as *"inconclusive at this power"*, never as *"macro conditioning has no effect"*. | `permute_Z` changes the ESS distribution — macro states are autocorrelated, so similarity and recency concentrate on the same pairs in the observed data and permuting Z breaks that alignment. Its draws are therefore **not exchangeable** with the observed fit. `permute_y` destroys the state↔outcome correspondence and nothing else, which is what §5.3 registered **in words**. **This was the THIRD change to test 5 following a failure — declared.** The defence is that both nulls are reported every run whatever they say, and disagreement between them is reported as a finding with **no tie-break**. Final: permute_y 0.066 (in band), permute_Z 0.000 (out). |
| 2026-08-25 | §2.2's conditioning switches to the **LIVE BASIS**: expanding-window feature standardisation (was full-panel) and expanding-window regime labels (was one GMM on all history), components canonically ordered by ascending mean PC1. | Step 3 is a **live daily product**; a deployed system has no future data to standardise with or fit regimes on, so the full-panel basis is something it **cannot do**, and a backtest that cannot be run live is not a backtest of the product. **Not** justified by the size of the look-ahead — `scaling_check` measured the level-basis effect at +0.012, p 0.94, small. Decided after seeing `scaling_check` — declared. **FIRST amendment that changes the estimator rather than the reporting.** No real conditional estimate had been computed, so nothing is contaminated retrospectively. Also closes PROJECT_STATE thread 3: without canonical ordering an expanding refit permutes labels across refits and the τ² cells silently mix regimes. |

### 11.1 Effect of the live-basis switch, recorded

Moving to the live basis changed the estimator's blind behaviour, and the
changes are reported rather than tuned away:

| | full-panel basis | live basis |
|---|---|---|
| test 1 kernel attenuation | 86.2% | 90.3% |
| τ²=0 degenerate fraction | 42.5% | 20.0% (32.0% at 200 reps) |
| "no planted structure" tiers 1/2/3 | 0/8/392 | 0/260/140 |
| `permute_y` rejection | 0.043 | 0.066 |

**The estimator conditions more often on the live basis** — τ² fires on data with
no planted cell structure in 260 of 400 queries where it previously fired in 8.
`permute_y` remains inside the registered band at 200 reps, so this is recorded
as a property of the basis, not a defect. It is the first thing to re-check if
any real step-3 result looks strong.
"""

EXEC_APPEND = """

---

## SESSION CLOSE 2026-08-25 — STEP 1 DONE, STEPS 3–6 REGISTERED AND BUILT BLIND

*This plan was written 2026-08-23. What follows records what actually happened,
including where the plan was wrong. Detail lives in
`docs/CURRENT_STATE_2026-08-23.md` §15; this section records only what changes
IN THIS FILE.*

### STEP 0 — CLOSED

0a was **already done** when this plan was written: `prereg_drift_existence.md`
§9 carries the amendment row. 0b's phrasing stands — FOMC→GLD, PEAD and
spillover are registered in **script docstrings committed before their runs**
(`8640d2d` / `8be9fcd` / `78419d0`), verifiable with
`git log --format='%H %cd' -- <script>`. No prereg document was back-filled.

### STEP 1 — CLOSED, SEVEN ITEMS

The plan listed four. Three more were added as earlier items surfaced them.

| item | verdict |
|---|---|
| λ ladder, **both engines** | A POSITIVE, B NULL → **reframed exploratory** |
| rung-level selection diagnostic *(added)* | **RESELECTION on both engines** |
| fine λ scan *(added)* | surface **jagged**; dip **unexplained** |
| adjacent-rung count | **4**, strictly monotone |
| `_z()` expanding-window rerun | small for level, **large for trend** |
| same-horizon level-vs-trend | **the trend advantage IS the look-ahead** |
| Engine B no-decay vs incumbent, paired *(added)* | **not distinguishable**, p 0.485 |

**Where this plan was wrong.** Its Step 1 said *"Registered expectation: little or
no improvement… the lever is σ, not λ."* That expectation was **scoped to the
macro panel** and stated as though general. The ladder produced a large change on
Engine A (0.2526 → 0.4194), which the plan itself said would be *"suspect, not
success"* — and the rung diagnostic showed why: λ **reselects** rather than
tie-breaks, so the ladder measures *"does restricting to recent history improve
returns"*, not *"does recency decay improve analog quality"*.

**λ also already existed.** `config.yaml` carries
`analog.recency_decay_lambda: 0.0008` in sessions (HL 3.44y) and
`analog_backtest.py` applies it, so the reported 0.51 / 0.25 always carried
decay. The plan, and the prereg it cited, both stated the opposite.

### STEP 2 AND THE GATE — CLOSED, WITH TWO AMENDMENTS

The plan's pilot-then-gate sequencing worked exactly as intended: a 20-document
pilot caught that the entire 307-document `earnings_8k` corpus was **SEC cover
pages**, not earnings releases, before anything was spent on the full read.

Two amendments, both after seeing a marginal 0.26 spread, both declared and
recorded in `prereg_analog_event.md` §11: the `political` split by Federal
Register type, and the criterion moving from a **point** spread to the **lower
bound of a 95% CI**. The second is a tightening.

**GATE: PASS.** n=60 × 4 sources, spread 0.363, CI [0.279, 0.453], uniform read
condition. `specificity` therefore enters §2.1 and §7.2 of the step 3
registration. **Re-run `gate_check` once the corpus read completes** — the
`political_other` arm was measured at n=60 of 816.

### STEPS 3–6 — REGISTERED, AND 3+4 BUILT BLIND

`docs/prereg_analog_event.md` (74b88dc), committed before the corpus read.

**Where this plan was wrong.** Its Step 4 registered a hard *"<10 matched
precedents → fall back"* cutoff. **Replaced** by a precision-weighted blend,
`w = ESS/(ESS+k)`, because nothing real changes between 9 and 10 precedents and a
cutoff presents a 12-precedent estimate as clean while discarding a 9-precedent
one entirely. **k is estimated, never chosen** — DerSimonian–Laird τ² across
regime cells, inside every LOO fold. The floor survives only as an **abstention**
rule at ESS < 8.

Steps 3 and 4 are therefore **one estimator**, `src/analog_event.py`, built blind
and passing **6/6** acceptance tests. Steps 5 and 6 remain unbuilt.

### WHAT IS ACTUALLY LEFT

The authoritative list is `CURRENT_STATE` §15.11. In this plan's terms:

| step | state |
|---|---|
| — | **the report — does not exist, deadline passed** |
| 2 | corpus read in progress; word cap decision outstanding |
| gate | re-run after the corpus completes |
| 3 | **unblinding authorised** — run the registered LOO test |
| 5 | not started; count same-day collisions first |
| 6 | not started — the customer-facing artifact |
| — | rebuild `app.py`; **rebuild, do not recover** |
| 7 | launchd automation not started |
| — | FOMC→GLD temporal split + cost test — the Tier-1 exemplar |

**"THINGS THAT WILL BREAK THIS IF FORGOTTEN" all held.** Power was the binding
constraint everywhere. The gate was a real gate and caught a dead corpus. Step 4
was built before step 3. σ-not-λ was right in direction and wrong in scope. And
every result that survived had its criterion written first — while **nine claims
were retired**, each by a test registered before it ran.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prereg = ROOT / "docs" / "prereg_analog_event.md"
    plan = ROOT / "docs" / "EXECUTION_PLAN.md"

    anchor = """## 11. AMENDMENTS

*(none — this section exists so any post-hoc change is visible rather than
silent)*

| date | change | reason |
|---|---|---|
| | | |"""

    print("=" * 74)
    print("PHASE 1 -- verifying (nothing written)")
    print("=" * 74)
    fail = []
    if not prereg.exists():
        fail.append(f"MISSING: {prereg}")
        print(f"  FAIL  docs/prereg_analog_event.md: not found")
    else:
        n = prereg.read_text().count(anchor)
        if n == 1:
            print("  ok    docs/prereg_analog_event.md: §11 empty table found")
        elif n == 0:
            fail.append("§11 anchor not found -- already edited?")
            print("  FAIL  docs/prereg_analog_event.md: §11 anchor not found")
            print("        (has §11 already been filled in by hand?)")
        else:
            fail.append(f"§11 anchor x{n}")
            print(f"  FAIL  docs/prereg_analog_event.md: anchor x{n}")

    if not plan.exists():
        fail.append(f"MISSING: {plan}")
        print("  FAIL  docs/EXECUTION_PLAN.md: not found")
    elif "SESSION CLOSE 2026-08-25" in plan.read_text():
        fail.append("EXECUTION_PLAN already has the closure section")
        print("  FAIL  docs/EXECUTION_PLAN.md: closure section already present")
    else:
        print("  ok    docs/EXECUTION_PLAN.md: ready to append")

    if fail:
        print("\n" + "=" * 74)
        print(f"ABORTED -- {len(fail)} failure(s). NO FILE WAS MODIFIED.")
        print("=" * 74)
        for f in fail:
            print(f"  - {f}")
        sys.exit(1)

    print("\nboth verified.")
    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    print("\n" + "=" * 74)
    print("PHASE 2 -- applying")
    print("=" * 74)
    t = prereg.read_text()
    assert t.count(anchor) == 1
    prereg.write_text(t.replace(anchor, AMENDMENTS))
    print("  written  docs/prereg_analog_event.md  (§11: 4 amendments + §11.1)")
    with open(plan, "a") as f:
        f.write(EXEC_APPEND)
    print("  written  docs/EXECUTION_PLAN.md  (session close appended)")

    print("\n" + "=" * 74)
    print("""HANDOVER -- docs/ is now self-contained. Regenerate the briefing:

  for f in docs/*.md; do echo "===== $f ====="; cat "$f"; echo; done \\
      > ~/Downloads/briefing.md
  wc -l ~/Downloads/briefing.md

  grep -c "^## 11. AMENDMENTS" docs/prereg_analog_event.md      # 1
  grep -c "| 2026-08-2" docs/prereg_analog_event.md             # 4 amendment rows
  grep -n "15.11 WHAT IS ACTUALLY LEFT" docs/CURRENT_STATE_2026-08-23.md

THE TRACK for a new session is CURRENT_STATE §15.11. Everything else --
results, registrations, amendments, the pipeline map -- is in docs/ and will be
in the briefing.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
