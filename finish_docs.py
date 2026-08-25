#!/usr/bin/env python3
"""
finish_docs.py -- do the two outstanding jobs in one pass, no patch hunting.

1. Move EXECUTION_PLAN.md from ~/Downloads into docs/ (it was written in chat
   and never saved to the repo, so briefing.md has never contained it).
2. Fill docs/prereg_analog_event.md section 11 with FIVE amendments.
3. Append the session-close section to docs/EXECUTION_PLAN.md.
4. Make doc_read TRUNCATE over-cap documents instead of skipping them.

Idempotent:每 step checks whether it has already been done and skips if so.
Safe to re-run.

    python finish_docs.py --dry-run
    python finish_docs.py
"""
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

AMENDMENTS = """## 11. AMENDMENTS

*Five amendments, all made during 2026-08-24/25. Each records WHEN it was decided
relative to what had been seen, because that is the only thing distinguishing an
amendment from a rationalisation.*

| date | change | reason |
|---|---|---|
| 2026-08-24 | §3.2 gains two scale-relative numerical guards: `DEGENERATE_VAR = 1e-9` and `TAU2_REL_FLOOR = 1e-6`, and the registered `Q ≤ C−1 → τ²=0` rule is applied **before** the division rather than after. | Blind test 6 caught the registered null path **silently failing to fire**. `np.var` of 80 identical float64 values returns 4.76e-38, so `W = 4.2e38`, which amplified float noise into `Q ≈ 4.2 > 3` and produced `τ² = 2e-38 > 0` — a **Tier-1 label with w = 0.96 on data with no between-cell variation at all**. The guards make the registered rule fire; they do not change it. Written before any real estimate. |
| 2026-08-25 | `political` split by Federal Register document type into `political_order` and `political_other`. Gate criterion changes from a **point** spread > 0.25 to the **lower bound of a 95% bootstrap CI** > 0.25; pilot raised to n=60 per source. | **Both decided AFTER seeing a marginal point spread of 0.26 on n=20 — declared, not hidden.** The split uses the **government's own type tag**, an external taxonomy, and reassigns no document by judgement. The criterion change is a **tightening**: at n=20 the spread carried se ≈ 0.063, so 0.26 was indistinguishable from failing. Gate subsequently PASSED at 0.363, CI [0.279, 0.453]. |
| 2026-08-25 | §5.3's null gains a second implementation. **`permute_y`** becomes PRIMARY; **`permute_Z`** is retained and reported permanently. Registered in advance: a rejection rate below 0.02 means the null is conservative, and a step 3 null must then be reported as *"inconclusive at this power"*, never as *"macro conditioning has no effect"*. | `permute_Z` changes the ESS distribution — macro states are autocorrelated, so permuting Z breaks the alignment between similarity and recency and its draws are **not exchangeable** with the observed fit. `permute_y` destroys the state↔outcome correspondence and nothing else, which is what §5.3 registered **in words**. **THIRD change to test 5 after a failure — declared.** Both nulls reported every run; disagreement is a finding with **no tie-break**. Final: permute_y 0.066 (in band), permute_Z 0.000 (out). |
| 2026-08-25 | §2.2's conditioning switches to the **LIVE BASIS**: expanding-window standardisation and expanding-window regime labels, canonically ordered by ascending mean PC1. | Step 3 is a **live daily product**; a deployed system has no future data, so the full-panel basis is something it **cannot do**, and a backtest that cannot be run live is not a backtest of the product. **Not** justified by effect size — `scaling_check` measured the level basis at +0.012, p 0.94. **FIRST amendment changing the estimator rather than the reporting.** No real estimate had been computed. Also closes PROJECT_STATE thread 3. |
| 2026-08-25 | Documents longer than `--max-words` are **truncated and read** rather than skipped. Each read records `truncated`, `orig_words` and `max_words`, carried into the CSV. | Skipping dropped **189 of 834** earnings documents (23%), all 6-K complete submissions where the whole filing is one file because foreign issuers file no separate EX-99. Costed at Sonnet 5 rates: skip = free with a 23% gap; raise the cap = **$17.77** for those 189 alone; truncate = **~$7.60** with no gap. An earnings release's figures sit near the top; the tail is exhibits. **This changes the model's input**, so any specificity or direction difference between truncated and whole documents is a property of the pipeline, not the source — which is why `truncated` is recorded per document rather than assumed away. |

### 11.1 Effect of the live-basis switch, recorded

| | full-panel basis | live basis |
|---|---|---|
| test 1 kernel attenuation | 86.2% | 90.3% |
| τ²=0 degenerate fraction | 42.5% | 32.0% (200 reps) |
| "no planted structure" tiers 1/2/3 | 0/8/392 | 0/260/140 |
| `permute_y` rejection | 0.043 | 0.066 |

**The estimator conditions more often on the live basis.** `permute_y` stays
inside the registered band, so this is recorded as a property of the basis, not a
defect — and it is the first thing to re-check if any real step-3 result looks
strong.
"""

EXEC_APPEND = """

---

## SESSION CLOSE 2026-08-25 — STEP 1 DONE, STEPS 3–6 REGISTERED AND BUILT BLIND

*Detail lives in `docs/CURRENT_STATE_2026-08-23.md` §15. This records only what
changes in this file, including where the plan was wrong.*

**STEP 0 — CLOSED.** 0a was already done when this plan was written. 0b's
phrasing stands: FOMC→GLD, PEAD and spillover are registered in **script
docstrings committed before their runs** (`8640d2d` / `8be9fcd` / `78419d0`).
No prereg was back-filled.

**STEP 1 — CLOSED, SEVEN ITEMS** (the plan listed four; three were added as
earlier items surfaced them):

| item | verdict |
|---|---|
| λ ladder, **both engines** | A POSITIVE, B NULL → **reframed exploratory** |
| rung-level selection diagnostic *(added)* | **RESELECTION on both engines** |
| fine λ scan *(added)* | surface **jagged**; dip **unexplained** |
| adjacent-rung count | **4**, strictly monotone |
| `_z()` expanding-window rerun | small for level, **large for trend** |
| same-horizon level-vs-trend | **the trend advantage IS the look-ahead** |
| Engine B no-decay vs incumbent *(added)* | **not distinguishable**, p 0.485 |

**Where this plan was wrong.** Its *"the lever is σ, not λ"* was scoped to the
macro panel and stated as general. And **λ already existed**: `config.yaml`
carries `analog.recency_decay_lambda: 0.0008` (HL 3.44y) and `analog_backtest.py`
applies it, so the reported 0.51 / 0.25 always carried decay. The plan and the
prereg it cited both said the opposite.

**STEP 2 AND THE GATE — CLOSED.** The pilot-then-gate sequencing worked exactly
as designed: a 20-document pilot caught that the entire 307-document
`earnings_8k` corpus was **SEC cover pages**, before anything was spent on the
full read. **GATE: PASS**, n=60×4, spread 0.363, CI [0.279, 0.453]. Two
amendments, both declared, in `prereg_analog_event.md` §11. **Re-run
`gate_check` once the corpus completes** — `political_other` was n=60 of 816.

**STEPS 3–6 — REGISTERED (74b88dc), 3+4 BUILT BLIND, 6/6 TESTS PASS.**

**Where this plan was wrong.** Step 4's hard *"<10 precedents → fall back"*
cutoff is **replaced** by a precision-weighted blend `w = ESS/(ESS+k)`, because
nothing real changes between 9 and 10 precedents. **k is estimated, never
chosen.** The floor survives only as an **abstention** rule at ESS < 8. Steps 3
and 4 are therefore one estimator, `src/analog_event.py`.

**WHAT IS LEFT** — authoritative list is `CURRENT_STATE` §15.11. The report does
not exist and the deadline has passed.

**"THINGS THAT WILL BREAK THIS" all held.** Power was binding everywhere. The
gate was a real gate and caught a dead corpus. Step 4 was built before step 3.
σ-not-λ was right in direction, wrong in scope. And every result that survived
had its criterion written first — while **nine claims were retired**, each by a
test registered before it ran.
"""

TRUNC_EDITS = [(
    """        long_ = [i for i, t in enumerate(texts)
                 if len(t.split()) > args.max_words]
        if long_:
            print(f"  {src}: {len(long_)} doc(s) over {args.max_words} words, "
                  f"skipped -- split or trim them")
        use = [i for i in range(len(pairs)) if i not in long_]""",
    """        # TRUNCATE, DO NOT SKIP (2026-08-25, prereg_analog_event section 11).
        # Skipping dropped 189 of 834 earnings documents -- 23% -- all 6-K
        # complete submissions where the whole filing is one file because
        # foreign issuers file no separate EX-99. An earnings release's figures
        # sit near the TOP; the tail is exhibits and signature pages.
        # The truncation is RECORDED, not silent.
        orig_words = {i: len(t.split()) for i, t in enumerate(texts)}
        long_ = [i for i in range(len(texts)) if orig_words[i] > args.max_words]
        for i in long_:
            texts[i] = (" ".join(texts[i].split()[:args.max_words])
                        + f"\\n\\n[DOCUMENT TRUNCATED at {args.max_words} words "
                          f"of {orig_words[i]}. The remainder is not shown. "
                          f"Judge only what is above.]\\n")
        if long_:
            print(f"  {src}: {len(long_)} doc(s) over {args.max_words} words, "
                  f"TRUNCATED and read (was: skipped)")
        use = list(range(len(pairs)))"""
), (
    """            data.update(source=src, date=dt.strftime("%Y-%m-%d"), doc_id=did,
                        prompt_version=PROMPT_VERSION, model=args.model)""",
    """            data.update(source=src, date=dt.strftime("%Y-%m-%d"), doc_id=did,
                        prompt_version=PROMPT_VERSION, model=args.model,
                        truncated=bool(i in long_),
                        orig_words=int(orig_words[i]),
                        max_words=int(args.max_words))"""
)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run
    did, skipped, failed = [], [], []

    # --- 1. EXECUTION_PLAN into docs/ ------------------------------------
    dest = DOCS / "EXECUTION_PLAN.md"
    if dest.exists():
        skipped.append("EXECUTION_PLAN.md already in docs/")
    else:
        found = None
        for c in (Path.home() / "Downloads" / "EXECUTION_PLAN.md",
                  ROOT / "EXECUTION_PLAN.md"):
            if c.exists():
                found = c; break
        if found is None:
            failed.append("EXECUTION_PLAN.md not found in ~/Downloads or repo "
                          "root -- move it into docs/ by hand")
        else:
            if not dry:
                shutil.copy2(found, dest)
            did.append(f"EXECUTION_PLAN.md  {found} -> docs/")

    # --- 2. prereg section 11 --------------------------------------------
    pre = DOCS / "prereg_analog_event.md"
    anchor = """## 11. AMENDMENTS

*(none — this section exists so any post-hoc change is visible rather than
silent)*

| date | change | reason |
|---|---|---|
| | | |"""
    if not pre.exists():
        failed.append("docs/prereg_analog_event.md not found")
    else:
        t = pre.read_text()
        if "| 2026-08-24 | §3.2 gains two scale-relative" in t:
            skipped.append("prereg section 11 already filled")
        elif t.count(anchor) == 1:
            if not dry:
                pre.write_text(t.replace(anchor, AMENDMENTS))
            did.append("prereg_analog_event.md  section 11: 5 amendments + 11.1")
        else:
            failed.append(f"prereg section 11 anchor found {t.count(anchor)}x "
                          f"-- edited by hand? fill it manually")

    # --- 3. EXECUTION_PLAN closure ---------------------------------------
    if dest.exists() or not dry:
        tgt = dest if dest.exists() else None
        if tgt is None and not dry:
            tgt = dest if dest.exists() else None
        if tgt is not None:
            t = tgt.read_text()
            if "SESSION CLOSE 2026-08-25" in t:
                skipped.append("EXECUTION_PLAN closure already appended")
            else:
                if not dry:
                    with open(tgt, "a") as f:
                        f.write(EXEC_APPEND)
                did.append("EXECUTION_PLAN.md  session-close section appended")

    # --- 4. truncation ----------------------------------------------------
    dr = ROOT / "src" / "doc_read.py"
    if not dr.exists():
        failed.append("src/doc_read.py not found")
    else:
        t = dr.read_text()
        if "TRUNCATED and read" in t:
            skipped.append("doc_read truncation already applied")
        else:
            ok = all(t.count(a) == 1 for a, _ in TRUNC_EDITS)
            if not ok:
                for a, _ in TRUNC_EDITS:
                    if t.count(a) != 1:
                        failed.append(f"doc_read anchor x{t.count(a)}: "
                                      f"{a.splitlines()[0][:60]!r}")
            else:
                for a, r in TRUNC_EDITS:
                    t = t.replace(a, r)
                # flat CSV columns
                fa = ('                         model=r.get("model", ""),')
                if t.count(fa) == 1:
                    t = t.replace(fa, fa + '\n'
                                  '                         truncated=r.get("truncated", False),\n'
                                  '                         orig_words=r.get("orig_words", None),')
                if not dry:
                    dr.write_text(t)
                did.append("doc_read.py  truncate over-cap documents, recorded")

    # --- report -----------------------------------------------------------
    print("=" * 74)
    print("DRY RUN -- nothing written" if dry else "APPLIED")
    print("=" * 74)
    for x in did:
        print(f"  {'would do' if dry else 'DONE    '}  {x}")
    for x in skipped:
        print(f"  skipped   {x}")
    for x in failed:
        print(f"  FAILED    {x}")
    if failed:
        print("\n  Some steps failed. The rest were still applied -- this script")
        print("  is idempotent, so fix the cause and re-run.")
    print("\n" + "=" * 74)
    print("""VERIFY:

  grep -c "| 2026-08-2" docs/prereg_analog_event.md      # 5
  grep -c "TRUNCATED and read" src/doc_read.py           # 1
  ls docs/EXECUTION_PLAN.md

THEN kill the running read (it is skipping the 189) and restart:

  jobs ; kill %2          # or whatever job number run_corpus.sh has
  caffeinate -i nohup ./run_corpus.sh > corpus6.log 2>&1 &

  for f in docs/*.md; do echo "===== $f ====="; cat "$f"; echo; done \\
      > ~/Downloads/briefing.md
""")
    print("=" * 74)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
