#!/usr/bin/env python3
"""
patch_engine_b_paired.py -- tracker 1e. Is Engine B's 0.38 really different
from its 0.25?

THE CLAIM UNDER TEST (prereg_rung_diagnostic.md section 3)
    Engine B (analog_backtest), long-history, 836 rebalances:
        HL = inf  (no decay)                  Sharpe 0.3800
        INCUMBENT (lambda 0.0008, HL 3.438y)  Sharpe 0.2500

    "Removing an unregistered hyperparameter with no recorded provenance raises
    Sharpe by half" is a claim someone will ask you to defend, and it currently
    rests on two numbers with no test between them.

    It also has to survive what the fine sweep found: the Sharpe surface is
    JAGGED in lambda -- 0.30 / 0.25 / 0.22 / 0.29 across steps of 1e-4. Rung-to-
    rung differences on that engine are the same order as the jitter. A paired
    test is the only thing that can separate a real gap from surface roughness.

WHAT THIS ADDS
    1. analog_backtest gains --dump-spreads PATH, writing the per-rebalance
       spread series for BOTH universes to JSON. Additive; no existing output
       or behaviour changes.
    2. src/engine_b_paired.py runs the two configurations, loads both dumps and
       applies the REGISTERED test: paired sign-flip permutation on the
       per-rebalance differences, 10,000 draws, called real at p < 0.05
       two-sided (prereg_rung_diagnostic section 3.2).

WHY PAIRED
    Both configurations run on identical rebalance dates, so the series are
    paired. A two-sample test would discard that and lose most of the power.
    Calibration of the sign-flip was checked before first use elsewhere in this
    project: 0.048 rejection with no real difference, 1.000 against a real
    0.05%/reb shift.

WHAT A NULL WOULD MEAN
    Registered in advance (section 3.2): above p = 0.05 the difference is
    reported as "not distinguishable at this sample size", NOT as evidence the
    two are equal. With 836 paired rebalances -- the largest paired sample
    anywhere in this project -- a null here is informative about the SURFACE,
    not about lambda.

Run from the repo root:
    python patch_engine_b_paired.py --dry-run
    python patch_engine_b_paired.py
    python -m src.engine_b_paired
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_backtest.py",
    '''def evaluate(records, universe, N, iters, rng, label):''',
    '''def evaluate(records, universe, N, iters, rng, label, collect=None):
    """collect: optional dict; when given, the per-rebalance spread series and
    the panel positions are stored under `label`. Added 2026-08-25 for the
    paired no-decay vs incumbent test (tracker 1e). Purely additive -- no
    existing output or behaviour changes."""''',
    "analog_backtest.evaluate -- accept an optional collector",
), (
    "src/analog_backtest.py",
    '''    print(f"  PERMUTATION vs random baskets: null {null.mean()*100:+.3f}%  p = {p:.4f}")''',
    '''    print(f"  PERMUTATION vs random baskets: null {null.mean()*100:+.3f}%  p = {p:.4f}")
    if collect is not None:
        collect[label] = dict(
            spreads=[float(x) for x in spreads],
            positions=[int(pos) for pos, _e, _r in records
                       if (universe & ~np.isnan(_e) & ~np.isnan(_r)).sum() >= 2 * N],
            n=int(len(spreads)), sharpe=float(spread_sharpe), p=float(p))''',
    "analog_backtest.evaluate -- store the spread series when collecting",
), (
    "src/analog_backtest.py",
    '''    ap.add_argument("--half-life", type=float, default=None, metavar="YEARS",''',
    '''    ap.add_argument("--dump-spreads", default=None, metavar="PATH",
                   help="write the per-rebalance spread series for both "
                        "universes to PATH as JSON. Used by "
                        "src/engine_b_paired.py for the paired no-decay vs "
                        "incumbent test. Additive: nothing else changes.")
    ap.add_argument("--half-life", type=float, default=None, metavar="YEARS",''',
    "analog_backtest -- add --dump-spreads",
), (
    "src/analog_backtest.py",
    '''    evaluate(records, np.ones(A, bool), N, args.iters, rng, f"ALL {A} ASSETS")
    evaluate(records, long_hist, N, args.iters, rng,
             f"LONG-HISTORY ONLY (>= {args.min_history:g}y)")''',
    '''    collect = {} if args.dump_spreads else None
    evaluate(records, np.ones(A, bool), N, args.iters, rng, "ALL", collect)
    evaluate(records, long_hist, N, args.iters, rng, "LONG-HISTORY", collect)
    if collect is not None:
        import json as _j
        meta = dict(lam=float(lam), lam_src=lam_src, horizon=int(H),
                    nbasket=int(N), min_history=float(args.min_history),
                    rebalances=int(len(records)))
        Path(args.dump_spreads).parent.mkdir(parents=True, exist_ok=True)
        Path(args.dump_spreads).write_text(
            _j.dumps(dict(meta=meta, universes=collect), indent=2))
        print(f"\\n  spread series -> {args.dump_spreads}")''',
    "analog_backtest.main -- write the dump",
)]

ENGINE_B_PAIRED = '''"""
engine_b_paired.py -- tracker 1e. Paired test: Engine B no-decay vs incumbent.

REGISTERED IN docs/prereg_rung_diagnostic.md section 3, written before the test
was implemented:

    Statistic  difference in mean per-rebalance spread
    Null       sign-flip permutation on the paired differences, 10,000 draws
    Criterion  real at p < 0.05 TWO-SIDED. Above that, reported as "not
               distinguishable at this sample size", NOT as evidence of equality.

WHY IT MATTERS
    Engine B long-history: no-decay 0.3800 vs incumbent lambda=0.0008 0.2500.
    "Removing an unregistered hyperparameter raises Sharpe by half" is the
    project's most attackable claim and currently rests on two numbers.

    The fine lambda sweep also found the Sharpe surface is JAGGED -- 0.30 /
    0.25 / 0.22 / 0.29 across lambda steps of 1e-4. Rung-to-rung differences are
    the same order as that jitter, so only a paired test can separate a real gap
    from surface roughness.

Run:
    python -m src.engine_b_paired
    python -m src.engine_b_paired --iters 20000
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "engine_b_paired_results.md"
OUT_JSON = PROCESSED_DIR / "engine_b_paired.json"


def run_dump(args_extra, path, iters):
    cmd = [sys.executable, "-m", "src.analog_backtest",
           "--iters", str(iters), "--dump-spreads", str(path)] + args_extra
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"analog_backtest failed:\\n{(r.stderr or r.stdout)[-1500:]}")
    return json.loads(Path(path).read_text())


def sign_flip(d, iters, rng):
    obs = float(np.mean(d))
    null = np.array([float(np.mean(d * rng.choice([-1.0, 1.0], len(d))))
                     for _ in range(iters)])
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (iters + 1)
    return obs, float(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=10000)
    ap.add_argument("--perm-iters", type=int, default=1000)
    args = ap.parse_args()
    rng = np.random.default_rng(42)

    print("=" * 78)
    print("ENGINE B PAIRED TEST -- no decay vs the incumbent lambda")
    print("=" * 78)
    print("  registered: sign-flip on paired per-rebalance differences,")
    print("  p < 0.05 two-sided. Above that -> 'not distinguishable at this")
    print("  sample size', NOT evidence of equality.")

    tmp = PROCESSED_DIR / "_tmp_spreads"
    print("\\n  running no-decay (HL = inf) ...")
    a = run_dump(["--half-life", "inf"], tmp / "inf.json", args.perm_iters)
    print("  running incumbent (config lambda) ...")
    b = run_dump([], tmp / "incumbent.json", args.perm_iters)

    print(f"\\n  no-decay : {a['meta']['lam_src']}")
    print(f"  incumbent: {b['meta']['lam_src']}")

    results = {}
    for uni in ("ALL", "LONG-HISTORY"):
        sa = np.asarray(a["universes"][uni]["spreads"], float)
        sb = np.asarray(b["universes"][uni]["spreads"], float)
        pa = a["universes"][uni]["positions"]
        pb = b["universes"][uni]["positions"]
        if len(sa) != len(sb) or pa != pb:
            print(f"\\n  {uni}: UNPAIRABLE -- {len(sa)} vs {len(sb)} rebalances")
            print("    the two runs do not share rebalance dates, so a paired")
            print("    test is not valid. Reported, not worked around.")
            results[uni] = dict(note="unpairable", n_a=len(sa), n_b=len(sb))
            continue
        d = sa - sb
        obs, p = sign_flip(d, args.iters, rng)
        sh_a = a["universes"][uni]["sharpe"]
        sh_b = b["universes"][uni]["sharpe"]
        results[uni] = dict(n=int(len(d)), mean_diff=obs, p=p,
                            sharpe_nodecay=sh_a, sharpe_incumbent=sh_b)
        verdict = ("REAL at the registered criterion" if p < 0.05 else
                   "NOT DISTINGUISHABLE at this sample size -- this is NOT "
                   "evidence the two are equal")
        print(f"\\n  {uni}  ({len(d)} paired rebalances)")
        print(f"    Sharpe   no-decay {sh_a:+.4f}   incumbent {sh_b:+.4f}   "
              f"diff {sh_a - sh_b:+.4f}")
        print(f"    mean spread difference {obs*100:+.4f}%/reb")
        print(f"    sign-flip p = {p:.4f}  ->  {verdict}")

    print("\\n" + "=" * 78)
    print("READING")
    print("  The fine lambda sweep found the Sharpe surface jagged in lambda")
    print("  (0.30 / 0.25 / 0.22 / 0.29 across steps of 1e-4). A null here")
    print("  means the 0.38-vs-0.25 gap is not separable from that roughness,")
    print("  which is a statement about the SURFACE, not about lambda.")
    print("=" * 78)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Engine B — no decay vs the incumbent lambda, paired test", "",
         f"*Run {ts}. Registered in `docs/prereg_rung_diagnostic.md` §3, "
         f"before implementation.*", "",
         "Sign-flip permutation on the paired per-rebalance differences, "
         f"{args.iters:,} draws, real at **p < 0.05 two-sided**. Above that the "
         "difference is reported as *not distinguishable at this sample size* — "
         "**not** as evidence the two are equal.", "",
         "| universe | n paired | no-decay Sharpe | incumbent Sharpe | "
         "mean spread diff | sign-flip p | verdict |",
         "|---|---|---|---|---|---|---|"]
    for uni, r in results.items():
        if r.get("note") == "unpairable":
            L.append(f"| {uni} | — | — | — | — | — | UNPAIRABLE "
                     f"({r['n_a']} vs {r['n_b']} rebalances) |")
            continue
        v = "real" if r["p"] < 0.05 else "not distinguishable"
        L.append(f"| {uni} | {r['n']} | {r['sharpe_nodecay']:+.4f} | "
                 f"{r['sharpe_incumbent']:+.4f} | {r['mean_diff']*100:+.4f}% | "
                 f"{r['p']:.4f} | {v} |")
    L += ["", "## Reading", "",
          "`docs/fine_lambda_sweep_results.md` found the Sharpe surface is "
          "**jagged** in λ — 0.30 / 0.25 / 0.22 / 0.29 across steps of 1e-4. A "
          "null here means the 0.38-vs-0.25 gap is not separable from that "
          "roughness, which is a statement about the surface rather than about "
          "λ.", ""]
    OUT_MD.write_text("\\n".join(L) + "\\n")
    OUT_JSON.write_text(json.dumps(results, indent=2))
    print(f"\\n  -> {OUT_MD}\\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
'''


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
    tgt = ROOT / "src" / "engine_b_paired.py"
    print(f"  {'ok   ' if not tgt.exists() else 'note '} src/engine_b_paired.py: "
          f"{'new file' if not tgt.exists() else 'EXISTS, will be overwritten'}")

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
    tgt.write_text(ENGINE_B_PAIRED)
    print(f"  written  src/engine_b_paired.py")

    print("\n" + "=" * 74)
    print("""VERIFY -- the default path must be unchanged:

  python -m src.analog_backtest --iters 50
      Header must still read "INCUMBENT, unregistered"; Sharpes 0.52 / 0.25.

  python -m src.engine_b_paired
      Two runs plus the paired test. ~10 minutes.

  If it reports UNPAIRABLE, the two configurations did not share rebalance
  dates and a paired test is not valid -- that is reported, not worked around.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
