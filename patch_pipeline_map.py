#!/usr/bin/env python3
"""
patch_pipeline_map.py -- PIPELINE.md documents none of the ten scripts written
on 2026-08-23/25. Open thread 13.

PIPELINE.md calls itself "purely a map of the code". A map missing ten files --
including the entire Problem 3 document layer and every script that closed
Step 1 -- is not a map. This adds:

  * Section 3a: the corpus read, a second API-bound process
  * Section 4: two new subsections (Step 1 closure, Problem 3 document layer)
  * Section 6: the data_provenance/ tree, which exists in no table
  * Section 8d: the two document-layer facts a reviewer needs

Edited in place rather than appended. PROJECT_STATE and CURRENT_STATE have
append conventions; PIPELINE is a navigation map, and a map with an appendix is
a worse map.

Run from the repo root:
    python patch_pipeline_map.py --dry-run
    python patch_pipeline_map.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "docs/PIPELINE.md",
    """---

## 5. Shared helpers (imported by the above, not run directly)""",
    """**Step 1 closure — what λ, σ and the scaling basis actually do (2026-08-24/25)**

*Every script below writes a `docs/*_results.md` and a `processed/*.json`. Read
the results files, not this table, for the numbers.*

| File | What it shows |
|---|---|
| `src/recency_sweep.py` | The pre-registered λ ladder {2,4,8,16,∞} on **both engines**. Runs the ∞ control first and asserts it reproduces `model_1_baseline` **element-wise on the spread series**, refusing to run a decayed rung otherwise. `--rederive` recomputes verdicts from the saved JSON without re-running. Engine A POSITIVE, Engine B NULL — **reframed exploratory**, see `rung_diagnostic`. |
| `src/rung_diagnostic.py` | What λ does to *selection*: weighted mean analog age, ESS, and top-k overlap against the no-decay control, per rung, per engine. **No forward return enters any quantity**, so nothing here can be tuned to an outcome. Registered threshold ≥0.90 overlap = tie-breaking. Measured 0.765 / 0.850 → **RESELECTION on both engines**. |
| `src/fine_lambda_sweep.py` | Exploratory, post-hoc, **no registered criterion** — maps the Sharpe surface across λ 0.0004–0.0014 to characterise the unexplained dip at the incumbent. Surface is **jagged**: 0.30 / 0.25 / 0.22 / 0.29 across steps of 1e-4. |
| `src/scaling_check.py` | Quantifies the **declared `_z()` full-panel look-ahead** (open thread 12) by running both scaling bases side by side on all three frozen models, paired sign-flip on the spread series, with candidate-pool counts so a smaller pool cannot be mistaken for a scaling effect. Small for level, **large for both trend models**. |
| `src/trend_check.py` | Isolates the trend effect at **fixed horizon** (thread 8's confound), on both scaling bases. Trend advantage +0.1137 full-panel, **−0.1213** with the look-ahead removed: on this panel **the trend advantage IS the look-ahead**. |
| `src/engine_b_paired.py` | Paired sign-flip on 836 shared rebalances: `analog_backtest` no-decay vs the incumbent λ. **p = 0.485 — not distinguishable**, retiring the claim that removing λ raised Sharpe 0.25→0.38. Uses `analog_backtest --dump-spreads`. |

**Problem 3 — the LLM document layer (steps 1–2 built; 3–6 registered, unbuilt)**

| File | What it shows |
|---|---|
| `src/fetch_sources.py` | Fetches every document source into the drop folder. **EDGAR**: for Item 2.02 the release text is in **EX-99**, not the primary document — the primary is a one-page cover page. Two passes: filename match, then a **content scan** of every other document in the accession keeping whatever contains reported figures, because issuers share no naming convention. Prints the accession's filenames when both fail. **Federal Register**: presidential documents by type. Filed/publication date is the **public** date, which is the correct event date. |
| `src/doc_read.py` | Reads any source into **ONE common schema** (direction per asset class, magnitude, horizon, specificity, novelty, confidence, evidence) via source-specific prompts. **The model never predicts returns** — it classifies content; what a direction *did* is answered by data in step 3. Aborts the whole run on a credit or auth error rather than retrying it; transient errors get one retry. Cached reads are keyed by prompt version and never re-billed. |
| `src/gate_check.py` | Does `specificity` **discriminate between sources**? Amended criterion: lower bound of a 95% bootstrap CI on the between-source spread must exceed 0.25, plus an ordering clause. Reports the **read condition per source**, so a cross-source comparison that is also a cross-prompt comparison cannot pass unnoticed. **PASS** at n=60×4: spread 0.363, CI [0.279, 0.453]. |
| `src/analog_event.py` | **Steps 3+4 as ONE estimator.** `ŷ = w·conditional + (1−w)·unconditional`, `w = ESS/(ESS+k)`; step 4 is the `w=0` limit. **k is estimated, not chosen** (DerSimonian–Laird τ² across regime cells, re-estimated inside every LOO fold); τ²=0 → w=0 is a **registered null**. Abstains below ESS 8. Runs on the **live basis** — expanding-window scaling and expanding canonically-ordered regime labels — because a deployed system has no future data. `--self-test` only: no real conditional estimate is computed until all six blind acceptance tests pass. |

---

## 5. Shared helpers (imported by the above, not run directly)""",
    "PIPELINE §4 -- add Step 1 closure and Problem 3 document-layer subsections",
), (
    "docs/PIPELINE.md",
    """Outputs: `processed/forward_ledger.csv` (machine state, gitignored) and
`docs/forward_scoreboard.md` (readable table, committed).""",
    """Outputs: `processed/forward_ledger.csv` (machine state, gitignored) and
`docs/forward_scoreboard.md` (readable table, committed).

**Regime labels are canonically ordered by ascending mean PC1 from 2026-08-25**
(open thread 3). Rows logged before that date carry the old arbitrary GMM
component ordering, so the `regime` column is comparable **within each era and
not across the boundary**. Historical rows are not retro-relabelled. Picks are
unaffected — candidate selection uses label *equality*, which is invariant under
relabelling, verified bit-identical on 826 rebalances.

`config/models.frozen.sha256` holds a canonical checksum of the frozen `models:`
block (yaml → sorted JSON → sha256, so comments and key order may change but a
hyperparameter may not). `forward_log` and `model_grid` **verify it and refuse to
run on mismatch**, and refuse any entry carrying `half_life_years` under
`models:`. This replaced a comment reading "never edit this file" — an invariant
already broken on 08-23, when four backtest-only recency variants were added
under `models:` where the live harness would have logged them.

### 3a. The corpus read (API-bound, not daily)

`./run_corpus.sh` reads every unread document through `doc_read`. **Not part of
the reproduce chain and not a daily job** — run it when new documents are
fetched. Cached reads are skipped and never re-billed, so a re-run costs only
the remainder. The script uses `set -e`: `doc_read` exits 1 on a fatal error, and
without it the script would proceed to the next source against the same
exhausted balance.""",
    "PIPELINE §3 -- record the label boundary, the checksum, and the corpus read",
), (
    "docs/PIPELINE.md",
    """| `outputs/` | Fitted models, diagnostics (CSVs), figures. | gitignored |""",
    """| `outputs/` | Fitted models, diagnostics (CSVs), figures. | gitignored |
| `data_provenance/docs/<source>/` | The **drop folder**: dated source text as `YYYYMMDD[_id].txt`, one directory per source type. Anything in that layout is readable — fetched by a script or saved by hand. Files are dated by **publication date**, not event date; dating FOMC minutes by meeting date would build look-ahead into a filename. `earnings_8k_coverpages/` retains the 307 SEC cover pages fetched before the EX-99 fix, as evidence. | gitignored, re-fetchable |
| `data_provenance/doc_reads/` | One JSON per document per prompt version, `<source>__<stem>__<version>.json`. **Committed** — these cost API spend and are not deterministically regenerable, so unlike the raw documents they cannot simply be re-pulled. Also the cache: a hit means zero tokens. | **yes** |""",
    "PIPELINE §6 -- add the data_provenance tree",
), (
    "docs/PIPELINE.md",
    """**(c) Data vendor gaps are expected.**""",
    """**(d) The document corpus has two properties that decide what it can support.**

*Dating.* Every file is dated by when the document became **public**, never by
when the event occurred. FOMC minutes are released about three weeks after the
meeting; dating them by meeting date would build look-ahead into a filename.

*Coverage.* Federal Register carries presidential documents only. Executive
orders and determinations (`political_order`) are decided policy;
proclamations, notices and memoranda (`political_other`) are largely ceremonial
or administrative — that split uses the **government's own type tag**, not a
judgement applied per document. Statements, posts and rhetoric outside the
Federal Register are **not covered**, and their absence in any result is a
**coverage gap, not evidence** that rhetoric does not move markets. Closing it is
a purchasing decision. `bank_research` and `transcript` have no free structured
feed and stand at zero documents.

*Foreign issuers* file 6-K with the whole submission as a single document and no
separate exhibits, so the EX-99 route that works for domestic 8-K yields little
for TSM and ASML. Cross-firm comparison must account for the asymmetry.

**(c) Data vendor gaps are expected.**""",
    "PIPELINE §8 -- add the document-layer facts a reviewer needs",
)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("=" * 74)
    print("PHASE 1 -- verifying anchors (nothing written)")
    print("=" * 74)
    failures = []
    for path, anchor, _r, label in EDITS:
        p = ROOT / path
        if not p.exists():
            failures.append(f"MISSING FILE: {path}")
            print(f"  FAIL  {path}: not found"); continue
        n = p.read_text().count(anchor)
        if n == 0:
            failures.append(f"ANCHOR NOT FOUND in {path} [{label}]")
            print(f"  FAIL  {path}: anchor not found -- {label}")
            print(f"        sought: {anchor[:70]!r}")
        elif n > 1:
            failures.append(f"ANCHOR NOT UNIQUE ({n}x) in {path} [{label}]")
            print(f"  FAIL  {path}: anchor x{n} -- {label}")
        else:
            print(f"  ok    {path}: {label}")

    if failures:
        print("\n" + "=" * 74)
        print(f"ABORTED -- {len(failures)} failure(s). NO FILE WAS MODIFIED.")
        print("=" * 74)
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"\nall {len(EDITS)} anchors verified, unique.")
    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    print("\n" + "=" * 74)
    print("PHASE 2 -- applying")
    print("=" * 74)
    touched = {}
    for path, anchor, repl, label in EDITS:
        text = touched.get(path, (ROOT / path).read_text())
        assert text.count(anchor) == 1, f"anchor lost mid-run: {path} [{label}]"
        touched[path] = text.replace(anchor, repl)
        print(f"  applied  {path}: {label}")
    for path, text in touched.items():
        (ROOT / path).write_text(text)
        print(f"  written  {path}")

    print("\n" + "=" * 74)
    print("""VERIFY:

  grep -c '| \\`src/' docs/PIPELINE.md          # script rows, was 24, now 34
  grep -n "^### 3a\\|^\\*\\*Step 1 closure\\|^\\*\\*Problem 3\\|^\\*\\*(d)" docs/PIPELINE.md

Still outstanding in thread 13: `src/analog_engine.py`, `src/conditional_order.py`,
`src/spillover_test.py`, `src/macro_event_test.py`, `src/pead_test.py` and the
GDELT panel builder are referenced elsewhere but absent or stale here. This patch
covers the ten scripts written on 2026-08-23/25, not the whole backlog.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
