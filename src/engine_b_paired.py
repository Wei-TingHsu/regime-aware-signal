"""
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
        raise SystemExit(f"analog_backtest failed:\n{(r.stderr or r.stdout)[-1500:]}")
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
    print("\n  running no-decay (HL = inf) ...")
    a = run_dump(["--half-life", "inf"], tmp / "inf.json", args.perm_iters)
    print("  running incumbent (config lambda) ...")
    b = run_dump([], tmp / "incumbent.json", args.perm_iters)

    print(f"\n  no-decay : {a['meta']['lam_src']}")
    print(f"  incumbent: {b['meta']['lam_src']}")

    results = {}
    for uni in ("ALL", "LONG-HISTORY"):
        sa = np.asarray(a["universes"][uni]["spreads"], float)
        sb = np.asarray(b["universes"][uni]["spreads"], float)
        pa = a["universes"][uni]["positions"]
        pb = b["universes"][uni]["positions"]
        if len(sa) != len(sb) or pa != pb:
            print(f"\n  {uni}: UNPAIRABLE -- {len(sa)} vs {len(sb)} rebalances")
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
        print(f"\n  {uni}  ({len(d)} paired rebalances)")
        print(f"    Sharpe   no-decay {sh_a:+.4f}   incumbent {sh_b:+.4f}   "
              f"diff {sh_a - sh_b:+.4f}")
        print(f"    mean spread difference {obs*100:+.4f}%/reb")
        print(f"    sign-flip p = {p:.4f}  ->  {verdict}")

    print("\n" + "=" * 78)
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
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(results, indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
