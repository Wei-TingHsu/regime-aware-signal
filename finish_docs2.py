#!/usr/bin/env python3
"""
finish_docs2.py -- record app.py in the two documents that currently contradict
the repo. Idempotent; safe to re-run.

  1. CURRENT_STATE section 16 -- app.py exists, what it shows, what it does not,
     and why its specimen tab is the step 6 specification.
  2. PIPELINE section 3 -- a row for app.py under the live/demo processes.

Run:
    python finish_docs2.py --dry-run
    python finish_docs2.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

CS_APPEND = """

---

## 16. DEMONSTRATION TERMINAL — `app.py` (2026-08-25)

*Supersedes §15.11's line "rebuild `app.py` — not started". A minimal version now
exists. The full version still waits on steps 5–6.*

### 16.1 What it is

`app.py` at the repo root, Streamlit, eight tabs. Run with
`pip install streamlit && streamlit run app.py`.

It shows **no predictions and no signal**, because steps 3–6 are registered but
not unblinded and any signal display would be fabricated. What it shows instead
is the project's actual argument: an instrument that grades its own evidence,
prints what it cannot see, and keeps the record of what it got wrong.

**Every number on every live tab is read from the repository at run time** —
`processed/*.json`, `forward_ledger.csv`, file counts under `data_provenance/`.
If a results file is missing the tab says so rather than showing a stale figure.
Ten figures are hard-coded, all from committed `docs/*_results.md` files.

| tab | source of its numbers |
|---|---|
| What this is | narrative + three counts |
| **Today's report (SPECIMEN)** | **invented — see §16.2** |
| Universe | `config/config.yaml`; live screening logic |
| Engines | `recency_sweep.json`, `rung_diagnostic.json`, `scaling_check` figures |
| Document layer | file counts on disk, `gate_check.json` |
| Forward test | `forward_ledger.csv` |
| What we got wrong | the wrong-prior tally, §15.10 |
| Behind the scenes | narrative; working principles and commercial read |

### 16.2 The specimen tab — a labelled mockup, and the step 6 spec

Tab 2 is a **UI mockup with invented numbers**. It carries a red banner, a
fictional date (2027-03-15), and the word SPECIMEN eighteen times, because a
fabricated figure that escapes its context becomes a claimed result — and an
untraceable number is the one thing that would genuinely damage this submission.

**It doubles as the specification for step 6.** Its fields are exactly those
registered in `prereg_analog_event.md` §8, so building the real decision report
becomes filling a shape that already exists rather than designing from a
paragraph:

- macro regime and **posterior confidence** (below 0.60 prints as a warning)
- every document read: source, direction, magnitude, specificity, novelty,
  evidence quote
- per asset: estimate, precedent count, **ESS**, **precedent strength w**, tier,
  dominant source, reader-vs-history agreement flag
- one **abstention** (ESS 4.1 < 8) shown as an abstention, not a thin number
- one **divergence** where reader and history disagree in sign: both numbers
  shown, **no combined figure issued**
- the coverage-gap block
- **no performance number, specimen or real**

**The guardrails survive the mockup deliberately.** Even the invented report
abstains, flags divergence, prints what it cannot see, and shows no performance
figure. A demo whose fake version behaves better than the real one would be worth
nothing.

### 16.3 What it does not do

No conditional estimate, no source weighing, no report emission to
`outputs/reports/`, no scheduling. Those are steps 3, 5, 6 and 7. The Universe
tab screens a ticker against the real ≥8y rule but does not fetch it or write to
`config.yaml`.

### 16.4 Revised remaining list

§15.11 stands with one line changed:

| # | item | state |
|---|---|---|
| 1 | **the report** | **does not exist; deadline passed** |
| 2 | corpus read | in progress; over-cap documents now truncated, not skipped |
| 3 | re-run `gate_check` with the full corpus | after 2 |
| 4 | unblind step 3 — the registered LOO test | **authorised**, after 2 |
| 5 | step 5 source weighing | not started; count same-day collisions first |
| 6 | step 6 decision report | not started — **spec exists as `app.py` tab 2** |
| 7 | `app.py` full version | **minimal version DONE**; wire to steps 3–6 |
| 8 | step 7 launchd automation | not started |
| + | FOMC→GLD temporal split + cost test | not started — the Tier-1 exemplar |
"""

PIPE_ANCHOR = """Run once daily, any time after ~05:00 SGT (so the prior US close has landed)."""

PIPE_ADD = """Run once daily, any time after ~05:00 SGT (so the prior US close has landed).

| File | Role | Run as |
|---|---|---|
| `app.py` | **Demonstration terminal** (repo root, not `src/`). Eight tabs; every live tab reads its numbers from `processed/*.json`, `forward_ledger.csv` and file counts under `data_provenance/` at run time, and says so when a results file is missing rather than showing a stale figure. **Shows no predictions** — steps 3–6 are registered but not unblinded. Tab 2 is a **labelled UI specimen** with invented numbers that doubles as the step 6 specification (`prereg_analog_event.md` §8). See `CURRENT_STATE` §16. | `streamlit run app.py` |"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    dry = a.dry_run
    did, skipped, failed = [], [], []

    cs = DOCS / "CURRENT_STATE_2026-08-23.md"
    if not cs.exists():
        failed.append("docs/CURRENT_STATE_2026-08-23.md not found")
    elif "## 16. DEMONSTRATION TERMINAL" in cs.read_text():
        skipped.append("CURRENT_STATE §16 already present")
    else:
        if not dry:
            with open(cs, "a") as f:
                f.write(CS_APPEND)
        did.append("CURRENT_STATE_2026-08-23.md  §16 appended")

    pp = DOCS / "PIPELINE.md"
    if not pp.exists():
        failed.append("docs/PIPELINE.md not found")
    else:
        t = pp.read_text()
        if "`app.py` | **Demonstration terminal**" in t:
            skipped.append("PIPELINE app.py row already present")
        elif t.count(PIPE_ANCHOR) != 1:
            failed.append(f"PIPELINE anchor found {t.count(PIPE_ANCHOR)}x "
                          f"-- add the app.py row by hand")
        else:
            if not dry:
                pp.write_text(t.replace(PIPE_ANCHOR, PIPE_ADD))
            did.append("PIPELINE.md  app.py row added to §3")

    print("=" * 74)
    print("DRY RUN -- nothing written" if dry else "APPLIED")
    print("=" * 74)
    for x in did:
        print(f"  {'would do' if dry else 'DONE    '}  {x}")
    for x in skipped:
        print(f"  skipped   {x}")
    for x in failed:
        print(f"  FAILED    {x}")
    print("\n" + "=" * 74)
    print("""THEN regenerate the briefing -- this is the file to upload:

  for f in docs/*.md; do echo "===== $f ====="; cat "$f"; echo; done \\
      > ~/Downloads/briefing.md
  wc -l ~/Downloads/briefing.md

  grep -c "| 2026-08-2" docs/prereg_analog_event.md    # 5 amendments
  grep -c "## 16. DEMONSTRATION" docs/CURRENT_STATE_2026-08-23.md   # 1
  ls docs/EXECUTION_PLAN.md
""")
    print("=" * 74)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
