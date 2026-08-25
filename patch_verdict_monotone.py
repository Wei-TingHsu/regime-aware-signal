#!/usr/bin/env python3
"""
patch_verdict_monotone.py -- report the STRICTLY MONOTONE adjacent-rung count.
Tracker item 1a'''.

THE DEFECT
    prereg_recency_kernel.md section 6 requires improvement "monotone or stable
    across at least three adjacent rungs". **"Stable" was never given a numeric
    definition.** recency_sweep.verdict() supplied an unregistered +/-0.02
    tolerance, and the printed count depends entirely on that undeclared number:

        tolerance          Engine A adjacent-rung count
        0.02 (as coded)    5
        0.01               4
        strictly monotone  4      <- 16y -> 8y -> 4y -> 2y

    Engine A long-history: inf 0.2526, 16y 0.2338, 8y 0.2495, 4y 0.3205,
    2y 0.4194. Ordered by increasing decay the steps are
    -0.0188, +0.0157, +0.0710, +0.0989 -- one reversal at the flat end, then
    three consecutive increases.

    The verdict is POSITIVE under every tolerance, since all counts exceed
    three. Only the REPORTED FIGURE was wrong.

    Registered correction (docs/prereg_rung_diagnostic.md section 4): the
    reported count is the strictly monotone run, with NO tolerance. Any
    tolerance-based count is reported separately and labelled as such.

TWO EARLIER READINGS, BOTH SUPERSEDED
    The code printed 5. An earlier reading in conversation gave 3. Both wrong.
    The strictly monotone run is 4. Recorded rather than quietly fixed.

NO RE-RUN
    --rederive recomputes the verdict from processed/recency_sweep.json and
    rewrites docs/recency_sweep_results.md. The ladder is not re-executed: the
    numbers are unchanged, only the count derived from them.

Run from the repo root:
    python patch_verdict_monotone.py --dry-run
    python patch_verdict_monotone.py
    python -m src.recency_sweep --rederive
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/recency_sweep.py",
    '''    # stability: >=3 adjacent rungs whose Sharpe is monotone or flat in HL
    order = [2.0, 4.0, 8.0, 16.0, float("inf")]
    sh = [res[(h, "LONG-HISTORY")]["sharpe"] for h in order
          if (h, "LONG-HISTORY") in res]
    best_run, run = 1, 1
    for i in range(1, len(sh)):
        if abs(sh[i] - sh[i - 1]) < 0.02 or (sh[i] - sh[i - 1]) * (
                sh[1] - sh[0] if len(sh) > 1 else 1) > 0:
            run += 1; best_run = max(best_run, run)
        else:
            run = 1
    if best_run < 3:
        return ("NULL", f"primary rung beats the control "
                        f"({prim['sharpe']:+.4f} vs {ctrl['sharpe']:+.4f}) but "
                        f"the longest monotone-or-stable stretch is {best_run} "
                        f"adjacent rungs, short of the registered 3. A single "
                        f"winning rung is a GRID WINNER, NOT A FINDING.")
    return ("POSITIVE", f"primary rung HL={PRIMARY_HL:g}y beats the no-decay "
                        f"control ({prim['sharpe']:+.4f} vs {ctrl['sharpe']:+.4f}) "
                        f"and the improvement is monotone or stable across "
                        f"{best_run} adjacent rungs. Criterion MET.")''',
    '''    # STABILITY. Section 6 says "monotone or stable across at least three
    # adjacent rungs" but never defines "stable" numerically. The previous
    # implementation supplied an UNREGISTERED +/-0.02 tolerance, and the printed
    # count depended entirely on it (0.02 -> 5, 0.01 -> 4, none -> 4). The
    # reported figure is now the STRICTLY MONOTONE run; tolerance-based counts
    # are computed too but LABELLED AS DIAGNOSTIC.
    # Registered in docs/prereg_rung_diagnostic.md section 4.
    order = [float("inf"), 16.0, 8.0, 4.0, 2.0]      # increasing decay
    sh = [res[(h, "LONG-HISTORY")]["sharpe"] for h in order
          if (h, "LONG-HISTORY") in res]

    def _run(tol):
        """Longest run of adjacent rungs that does not DECREASE by more than
        tol as decay increases. tol=0 is strictly monotone."""
        best, run = 1, 1
        for i in range(1, len(sh)):
            if (sh[i] - sh[i - 1]) >= -tol:
                run += 1; best = max(best, run)
            else:
                run = 1
        return best

    strict = _run(0.0)
    diag = {t: _run(t) for t in (0.01, 0.02)}
    diag_s = ", ".join(f"+/-{t}: {n}" for t, n in diag.items())

    if strict < 3:
        return ("NULL", f"primary rung beats the control "
                        f"({prim['sharpe']:+.4f} vs {ctrl['sharpe']:+.4f}) but "
                        f"the longest STRICTLY MONOTONE stretch is {strict} "
                        f"adjacent rungs, short of the registered 3. A single "
                        f"winning rung is a GRID WINNER, NOT A FINDING. "
                        f"[diagnostic, tolerance-based: {diag_s}]")
    return ("POSITIVE", f"primary rung HL={PRIMARY_HL:g}y beats the no-decay "
                        f"control ({prim['sharpe']:+.4f} vs {ctrl['sharpe']:+.4f}) "
                        f"and the improvement is STRICTLY MONOTONE across "
                        f"{strict} adjacent rungs. Criterion MET. "
                        f"[diagnostic only, tolerance-based counts: {diag_s} -- "
                        f"these depend on an unregistered tolerance and are NOT "
                        f"the reported figure]")''',
    "recency_sweep.verdict -- strictly monotone count, tolerance counts labelled diagnostic",
), (
    "src/recency_sweep.py",
    '''    ap.add_argument("--skip-control", action="store_true",''',
    '''    ap.add_argument("--rederive", action="store_true",
                    help="recompute the verdict from processed/recency_sweep.json "
                         "and rewrite the report. Does NOT re-run the ladder -- "
                         "the numbers are unchanged, only the count derived "
                         "from them.")
    ap.add_argument("--skip-control", action="store_true",''',
    "recency_sweep -- add --rederive",
), (
    "src/recency_sweep.py",
    '''    print("=" * 78)
    print("RECENCY KERNEL SWEEP -- pre-registered ladder {2, 4, 8, 16, inf}")
    print("=" * 78)''',
    '''    if args.rederive:
        if not OUT_JSON.exists():
            raise SystemExit(f"missing {OUT_JSON} -- nothing to re-derive from.")
        raw = json.loads(OUT_JSON.read_text())
        a_res, b_res = {}, {}
        for k, v in raw.items():
            eng, hl_s, uni = k.split("|")
            hl = "incumbent" if hl_s == "incumbent" else float(hl_s)
            (a_res if eng == "A" else b_res)[(hl, uni)] = v
        print("=" * 78)
        print("RE-DERIVING VERDICTS FROM processed/recency_sweep.json")
        print("  ladder NOT re-run: the numbers are unchanged, only the")
        print("  adjacent-rung count derived from them (tracker item 1a-iii).")
        print("=" * 78)
        for e, res in (("A", a_res), ("B", b_res)):
            if res:
                v, why = verdict(res, e)
                print(f"\\nENGINE {e} VERDICT: {v}\\n  {why}")
        write_report(a_res, b_res, args.iters)
        return

    print("=" * 78)
    print("RECENCY KERNEL SWEEP -- pre-registered ladder {2, 4, 8, 16, inf}")
    print("=" * 78)''',
    "recency_sweep.main -- implement --rederive",
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
    print("""NEXT -- no re-run, the numbers are unchanged:

  python -m src.recency_sweep --rederive

  Engine A must now read "STRICTLY MONOTONE across 4 adjacent rungs" with the
  tolerance-based counts (+/-0.01: 4, +/-0.02: 5) labelled DIAGNOSTIC ONLY.
  Engine B stays NULL: its primary rung 0.3200 does not beat its control
  0.3800, so stability is never evaluated.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
