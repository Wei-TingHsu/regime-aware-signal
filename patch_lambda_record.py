#!/usr/bin/env python3
"""
patch_lambda_record.py -- correct the recency-kernel (lambda) record across docs.

WHY THIS EXISTS
    prereg_recency_kernel.md §1 and PROJECT_STATE's gap note both assert that no
    lambda existed anywhere in the codebase, explicitly including config.yaml.
    That is false. config/config.yaml has carried
        analog.recency_decay_lambda: 0.0008
    and src/analog_backtest.py applies it:
        w = exp(-d^2 / 2 sigma^2) * exp(-lam * (pos - cand))
    with age in SESSIONS, i.e. half-life = ln2/0.0008 = 866 sessions = 3.44 years.

    analog_backtest.py is the script that produced the headline 0.51 / 0.25
    (835 rebalances, 2010-01-04 -> 2026-08-11, 35-asset >=8y cut). Those numbers
    were therefore computed WITH recency decay, not without it.

DISCIPLINE
    Every replacement below asserts its anchor is present and unique BEFORE
    writing anything. If any anchor is missing the script raises and NO file is
    modified. The previous patch script in this repo used bare str.replace with
    no assertions, silently missed two of three anchors, and printed success.

Run from the repo root:
    python patch_lambda_record.py --dry-run
    python patch_lambda_record.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Every edit: (path, anchor, replacement, label)
# Anchors are verbatim from the committed files.
# ---------------------------------------------------------------------------

EDITS = []

# --- 1. prereg_recency_kernel.md §1 -- the false premise -------------------
EDITS.append((
    "docs/prereg_recency_kernel.md",
    """`analog_core._kw()` implemented only the similarity half. No λ existed anywhere
in the codebase. The gap was found 2026-08-23, five days after the design was
locked, and only because it was asked about directly.""",
    """`analog_core._kw()` implemented only the similarity half. The gap was found
2026-08-23, five days after the design was locked, and only because it was asked
about directly.

> **CORRECTED 2026-08-24 (see §7, Amendment 1).** The original text of this
> section read *"No λ existed anywhere in the codebase."* **That was false.**
> `config/config.yaml` carries `analog.recency_decay_lambda: 0.0008` and
> `src/analog_backtest.py` applies it as
> `exp(-lam * (pos - cand))` with age in **sessions** — an effective half-life of
> ln2/0.0008 = 866 sessions = **3.44 years**.
>
> `analog_backtest.py` is the script that produced the reported **0.51 / 0.25**
> (835 rebalances, 2010-01-04 → 2026-08-11, 35-asset ≥8y cut). **Those figures
> were computed WITH recency decay at HL ≈ 3.44y, not without it.**
>
> The gap was real but narrower than stated: λ was missing from `analog_core`
> (the frozen-model and live-harness path), not from the project. The two engines
> differ in three further respects — `analog_core` z-scores the PCs, freezes one
> GMM on all history, and applies no decay; `analog_backtest` uses raw PC values
> so PC1 dominates the distance, refits the GMM expanding-window every 20
> sessions, and decays. They are different estimators and legitimately report
> different numbers (0.40 vs 0.25).
>
> **Consequence for this registration: the ladder runs on BOTH engines.** See §7.
> The value 0.0008 has no recorded provenance anywhere in `docs/`; it is off the
> registered ladder and is reported as **the incumbent, not a rung**.""",
    "prereg §1 -- false 'no lambda existed' premise corrected",
))

# --- 2. prereg_recency_kernel.md §2 -- scope of the diagnostic -------------
EDITS.append((
    "docs/prereg_recency_kernel.md",
    """`recency = exp(-ln2 · age_years / HL)`, with age measured in years (sessions/252).""",
    """`recency = exp(-ln2 · age_years / HL)`, with age measured in years (sessions/252).

> **SCOPE NOTE (2026-08-24).** `recency_diagnostic.py` characterised
> `analog_core`, whose default is genuinely no-decay. It did **not** characterise
> `analog_backtest`, which already decays at HL ≈ 3.44y. Every "no decay" column
> in §4 therefore describes the frozen-model engine, **not** the engine behind
> the reported 0.51 / 0.25.""",
    "prereg §2 -- diagnostic scope limited to analog_core",
))

# --- 3. prereg_recency_kernel.md §7 -- the amendment record ----------------
EDITS.append((
    "docs/prereg_recency_kernel.md",
    """## 7. Amendments

*(none)*

| date | change | reason |
|---|---|---|
| | | |""",
    """## 7. Amendments

*One amendment, recorded below. Written BEFORE any rung of the ladder was run,
and before any Sharpe under decay was observed.*

| date | change | reason |
|---|---|---|
| 2026-08-24 | §1's claim that "no λ existed anywhere in the codebase" is retracted as **false**. λ has been present in `config/config.yaml` as `analog.recency_decay_lambda: 0.0008` and applied in `src/analog_backtest.py`, giving HL ≈ 3.44y in session units. The reported 0.51 / 0.25 carry that decay. | The premise was wrong on a checkable fact. Recording it as an amendment rather than editing §1 silently, so the error and its correction are both visible. |
| 2026-08-24 | **The ladder now runs on BOTH engines.** Engine A = `analog_core` (frozen-model path, genuine no-decay default); Engine B = `analog_backtest` (headline path, incumbent λ=0.0008). Rungs {2,4,8,16,∞} on each. On Engine B, HL is converted to per-session λ as `ln2/(HL×252)` and ∞ is `λ=0`. | One engine's ladder cannot speak for the other. Engine B at ∞ is a number that has never been computed, and it is the only way to learn what the headline result owes to an unregistered hyperparameter. |
| 2026-08-24 | λ=0.0008 (HL≈3.44y) is reported as **the incumbent, off-ladder**, never as a rung and never promotable. | §3 forbids promoting a rung after the fact; an unregistered value with no recorded provenance has weaker standing still. Its only role is reproducing the recorded 0.51 / 0.25. |

**Unchanged by this amendment:** the functional form (exponential), the primary
half-life (4y, presidential-term grounds), the ladder values, and the §6 success
criterion. Only the count of engines the ladder runs on has changed.

**Note on 4y vs 3.44y.** The primary rung was fixed on stated economic grounds
before this discovery, and it sits close to the incumbent's effective half-life.
That proximity is **coincidence, not corroboration** — 0.0008 has no recorded
reasoning behind it. Neither value may be cited as evidence for the other.""",
    "prereg §7 -- amendment record written before any rung is read",
))

# --- 4. PROJECT_STATE.md -- the gap note ----------------------------------
EDITS.append((
    "docs/PROJECT_STATE.md",
    """`analog_core._kw()` implements ONLY the similarity kernel. There is no lambda
and no time term anywhere in the codebase; a 2008 analog and a 2024 analog at
equal macro distance receive equal weight. Not in config.yaml, not in
models.yaml, not in any open thread. It fell through the gap between design
and build and went unnoticed for five days.""",
    """`analog_core._kw()` implements ONLY the similarity kernel; within THAT engine a
2008 analog and a 2024 analog at equal macro distance receive equal weight. It
fell through the gap between design and build and went unnoticed for five days.

> **CORRECTED 2026-08-24.** The original text continued: *"There is no lambda and
> no time term anywhere in the codebase... Not in config.yaml, not in
> models.yaml, not in any open thread."* **The config.yaml clause was false.**
> `config/config.yaml` carries `analog.recency_decay_lambda: 0.0008`, and
> `src/analog_backtest.py` applies it as `exp(-lam * (pos - cand))` with age in
> **sessions** — HL = ln2/0.0008 = 866 sessions = **3.44 years**.
>
> `analog_backtest.py` is the engine behind the reported **0.51 / 0.25**, so
> **those numbers carry recency decay.** The gap was real for `analog_core` (the
> frozen-model and live-harness path) and false for the project as a whole.
>
> Recorded as a **wrong prior**: an absence was asserted across the whole
> codebase on the evidence of one file. The check that would have caught it is
> the one already in this document's working principles — *when a hazard is fixed
> in one script, grep for every other consumer in the same commit*. Applied to a
> claimed absence it reads: **grep before asserting a negative.**""",
    "PROJECT_STATE gap note -- config.yaml clause retracted",
))

# --- 5. PROJECT_STATE.md -- the headline engine block ---------------------
EDITS.append((
    "docs/PROJECT_STATE.md",
    """### Problem 1 ENGINE (macro analog) — REVISED DOWN
835 rebalances, 2010-01-04 → 2026-08-11:""",
    """### Problem 1 ENGINE (macro analog) — REVISED DOWN
835 rebalances, 2010-01-04 → 2026-08-11:

> **Basis note added 2026-08-24.** These figures come from
> `src/analog_backtest.py`, which applies recency decay at
> `analog.recency_decay_lambda = 0.0008` per session (**HL ≈ 3.44 years**). They
> are **not** no-decay numbers. `analog_core`/`model_grid` — the frozen-model
> path, genuinely decay-free — reports **0.40** for `model_1_baseline` on a
> different feature basis (z-scored PCs, frozen GMM). Two engines, two bases, two
> legitimate numbers. Do not compare them as though one were a rung of the
> other's ladder.""",
    "PROJECT_STATE headline block -- decay basis declared",
))

# --- 6. CURRENT_STATE §7 -- scope of the characterisation table -----------
EDITS.append((
    "docs/CURRENT_STATE_2026-08-23.md",
    """**Measured before any return was computed:**""",
    """> **SCOPE CORRECTION 2026-08-24.** The table below characterises
> **`analog_core`** only. `analog_backtest.py` — the engine behind the reported
> 0.51 / 0.25 — has decayed all along at `recency_decay_lambda = 0.0008`/session
> (HL ≈ 3.44y). Its "no decay" behaviour has never been measured; that is the
> ∞ rung of Engine B and it is the point of running the sweep. The claim in §9
> that the kernel was merely "BUILT, sweep unrun" understates this: the sweep is
> also a **correction to the record**, not only an extension of it.

**Measured before any return was computed:**""",
    "CURRENT_STATE §7 -- characterisation table scoped to analog_core",
))

# --- 7. CURRENT_STATE §2.3 -- wrong-prior tally ---------------------------
EDITS.append((
    "docs/CURRENT_STATE_2026-08-23.md",
    """- **Wrong-prior tally: nine.** Several are Claude's. Pattern across the first
  three: results are more *basis-carried* and less *phenomenon-carried* than
  expected. The fourth showed that correction can be over-applied.""",
    """- **Wrong-prior tally: ten.** Several are Claude's. Pattern across the first
  three: results are more *basis-carried* and less *phenomenon-carried* than
  expected. The fourth showed that correction can be over-applied.
  **Tenth (2026-08-24):** "no λ existed anywhere in the codebase, not in
  config.yaml" — asserted in `prereg_recency_kernel.md` §1 and in PROJECT_STATE's
  gap note, **false**; λ was in `config.yaml` and applied in
  `analog_backtest.py`, the engine behind the headline numbers. The lesson is
  narrower than the earlier basis-carried pattern and worth stating separately:
  **a negative claim about a codebase requires a grep, not a reading of the file
  you happen to have open.**
  *(Note: PROJECT_STATE's working-principles list still says "five so far" — it
  stopped being updated at five while this count went to ten. Reconcile.)*""",
    "CURRENT_STATE §2.3 -- tenth wrong prior recorded",
))

# --- 8. config.yaml -- provenance of the incumbent lambda -----------------
EDITS.append((
    "config/config.yaml",
    """analog:
  recency_decay_lambda: 0.0008""",
    """analog:
  # PROVENANCE UNKNOWN -- flagged 2026-08-24. This value is applied by
  # src/analog_backtest.py as exp(-lam * (pos - cand)) with age in SESSIONS,
  # giving a half-life of ln2/0.0008 = 866 sessions = 3.44 YEARS.
  #
  # It is NOT no-decay. The reported 0.51 / 0.25 (835 rebalances) carry it.
  # No document in docs/ records who chose 0.0008 or why. It is:
  #   * OFF the registered ladder {2,4,8,16,inf} in docs/prereg_recency_kernel.md
  #   * NEVER promotable to a live model (see that file, section 3)
  #   * ABSENT from the live forward test, which runs analog_core via
  #     models.yaml, where model_1/2/3 carry no half_life_years at all
  #
  # KEEP THIS VALUE. It is the reproduction constant for the recorded headline
  # figures; setting it to 0 makes 0.51 / 0.25 unreproducible from this repo.
  # The lambda sweep passes its own value per rung and does NOT read this key.
  recency_decay_lambda: 0.0008""",
    "config.yaml -- incumbent lambda provenance recorded",
))

# --- 9. PIPELINE.md -- the analog_backtest row ---------------------------
EDITS.append((
    "docs/PIPELINE.md",
    """| `src/analog_backtest.py` | Expanding-window walk-forward backtest (no look-ahead), non-overlapping weekly rebalances. Reports spread, Sharpe, hit-rate, win/loss asymmetry, permutation p — for **all assets** and for a **long-history-only** universe (the survivorship-bias check). |""",
    """| `src/analog_backtest.py` | Expanding-window walk-forward backtest (no look-ahead), non-overlapping weekly rebalances. Reports spread, Sharpe, hit-rate, win/loss asymmetry, permutation p — for **all assets** and for a **long-history-only** universe (the survivorship-bias check). **Applies recency decay** at `analog.recency_decay_lambda` (0.0008/session, HL ≈ 3.44y) and matches on **raw** PC values, not z-scored — so it is a different estimator from `analog_core`/`model_grid` and reports different numbers (0.25 vs 0.40 on the frozen baseline spec). The reported headline 0.51 / 0.25 come from **this** script. |""",
    "PIPELINE.md -- analog_backtest decay and feature basis documented",
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="verify every anchor, write nothing")
    args = ap.parse_args()

    # ---- PHASE 1: verify EVERY anchor before touching ANY file ----------
    print("=" * 74)
    print("PHASE 1 -- verifying anchors (no file is written in this phase)")
    print("=" * 74)
    failures = []
    for path, anchor, _repl, label in EDITS:
        p = ROOT / path
        if not p.exists():
            failures.append(f"MISSING FILE: {path}  [{label}]")
            print(f"  FAIL  {path}: file not found")
            continue
        text = p.read_text()
        n = text.count(anchor)
        if n == 0:
            failures.append(f"ANCHOR NOT FOUND in {path}  [{label}]")
            print(f"  FAIL  {path}: anchor not found -- {label}")
            print(f"        first 70 chars sought: {anchor[:70]!r}")
        elif n > 1:
            failures.append(f"ANCHOR NOT UNIQUE ({n}x) in {path}  [{label}]")
            print(f"  FAIL  {path}: anchor appears {n}x, must be unique -- {label}")
        else:
            print(f"  ok    {path}: {label}")

    if failures:
        print("\n" + "=" * 74)
        print(f"ABORTED -- {len(failures)} anchor failure(s). NO FILE WAS MODIFIED.")
        print("=" * 74)
        for f in failures:
            print(f"  - {f}")
        print("\nFix the anchors against the committed text and re-run.")
        sys.exit(1)

    print(f"\nall {len(EDITS)} anchors verified, unique.")

    if args.dry_run:
        print("\n--dry-run: nothing written. Re-run without the flag to apply.")
        return

    # ---- PHASE 2: apply ------------------------------------------------
    print("\n" + "=" * 74)
    print("PHASE 2 -- applying")
    print("=" * 74)
    touched = {}
    for path, anchor, repl, label in EDITS:
        p = ROOT / path
        text = touched.get(path, p.read_text())
        assert text.count(anchor) == 1, f"anchor lost mid-run in {path}: {label}"
        touched[path] = text.replace(anchor, repl)
        print(f"  applied  {path}: {label}")

    for path, text in touched.items():
        (ROOT / path).write_text(text)
        print(f"  written  {path}")

    print("\n" + "=" * 74)
    print(f"{len(EDITS)} edits across {len(touched)} files.")
    print("=" * 74)
    print("""
Suggested commit:

  git add docs/prereg_recency_kernel.md docs/PROJECT_STATE.md \\
          docs/CURRENT_STATE_2026-08-23.md docs/PIPELINE.md config/config.yaml
  git commit -m "docs: retract false 'no lambda in codebase' claim; record
  incumbent lambda=0.0008 (HL 3.44y) in analog_backtest as the basis of the
  reported 0.51/0.25; amend recency prereg to run the ladder on both engines;
  log tenth wrong prior. Written before any rung was run."

VERIFY, do not assume:
  git diff --stat
  # the only remaining hit should be the quoted retraction in the prereg:
  grep -rn "No λ existed\\|no lambda" docs/
  grep -rn "recency_decay_lambda" config/ src/ docs/
""")


if __name__ == "__main__":
    main()
