"""
fine_lambda_sweep.py -- map the unexplained interior dip at the incumbent lambda.

STATUS: EXPLORATORY, POST-HOC. Declared, not disguised.
    This is a fine-grained scan run AFTER seeing the ladder results, chosen to
    bracket one anomalous point. It has no registered criterion and CANNOT
    produce a finding. Its only job is to answer a descriptive question:
    is the dip a single-point artifact, or is the Sharpe surface genuinely
    jagged in lambda?

    Nothing here may be promoted to a model, a rung, or a claim.

THE ANOMALY
    Engine B (analog_backtest), long-history universe, 836 rebalances:

        HL 4y     (lambda 0.000688)   Sharpe 0.3200
        INCUMBENT (lambda 0.000800)   Sharpe 0.2500   <- between its neighbours
        HL 2y     (lambda 0.001375)   Sharpe 0.3000

    A 0.07 Sharpe drop across a lambda change of ~0.0001, sitting BELOW both
    neighbours. Sharpe is deterministic given lambda, so a smooth parameter
    cannot produce an interior dip by itself.

    docs/prereg_rung_diagnostic.md section 3.3 registered the discriminating
    check in advance: if top-k overlap changes sharply between HL=2y and HL=4y,
    the dip is attributable to discrete top-k membership changes. It does NOT --
    Engine B overlap runs 0.950 / 0.910 / 0.850 / 0.800, smooth, no break. So
    per the registration the dip is UNEXPLAINED, and this scan describes it
    rather than explaining it away.

WHAT WOULD SETTLE IT
    * isolated spike at 0.0008 only        -> single-point artifact; the
                                              incumbent happens to sit in a hole
    * several neighbouring dips            -> the surface is jagged in lambda;
                                              topk=100 membership is unstable and
                                              ANY single-lambda result is fragile
    * smooth curve through 0.0008          -> the earlier 0.25 was a measurement
                                              error and must be re-run and
                                              corrected in the record

    The third outcome would be the most important, and is the reason the
    incumbent lambda is re-run here rather than reused from the ladder output.

Run:
    python -m src.fine_lambda_sweep                  # 11 points, 1000 perms
    python -m src.fine_lambda_sweep --iters 200      # faster first look
    python -m src.fine_lambda_sweep --lambdas 0.0006,0.0008,0.0010
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np

from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "fine_lambda_sweep_results.md"
OUT_JSON = REPO / "processed" / "fine_lambda_sweep.json"

# Brackets the incumbent and both adjacent registered rungs.
DEFAULT_LAMBDAS = [0.0004, 0.0005, 0.0006, 0.0007, 0.0008,
                   0.0009, 0.0010, 0.0011, 0.0012, 0.0013, 0.0014]

INCUMBENT_LAMBDA = 0.0008
# Registered ladder rungs, in lambda terms, for reference lines in the output.
RUNG_LAMBDAS = {2.0: np.log(2) / (2 * 252), 4.0: np.log(2) / (4 * 252),
                8.0: np.log(2) / (8 * 252), 16.0: np.log(2) / (16 * 252)}

_SHARPE = re.compile(r"SHARPE \(ann\.\): spread ([+-][\d.]+)\s+long-leg ([+-][\d.]+)")
_SPREAD = re.compile(r"mean weekly spread = ([+-][\d.]+)%")
_P = re.compile(r"p = ([\d.]+)")
_N = re.compile(r"walk-forward complete: (\d+) rebalances")


def lam_to_hl(lam):
    """Per-session lambda -> half-life in years. analog_backtest takes years."""
    return float(np.log(2.0) / (lam * 252.0))


def parse(out):
    sh, sp, ps, n = (_SHARPE.findall(out), _SPREAD.findall(out),
                     _P.findall(out), _N.findall(out))
    if len(sh) != 2 or len(sp) != 2 or len(ps) != 2 or len(n) != 1:
        raise SystemExit(
            f"could not parse analog_backtest output: expected 2 universe "
            f"blocks, found sharpe={len(sh)} spread={len(sp)} p={len(ps)} "
            f"n={len(n)}.\n--- tail ---\n" + out[-1200:])
    names = ["ALL", "LONG-HISTORY"]
    return {names[i]: dict(sharpe=float(sh[i][0]), spread=float(sp[i]) / 100.0,
                           p=float(ps[i]), n=int(n[0])) for i in range(2)}


def run_one(hl, iters):
    r = subprocess.run(
        [sys.executable, "-m", "src.analog_backtest",
         "--half-life", f"{hl:.12g}", "--iters", str(iters)],
        capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"analog_backtest --half-life {hl:.12g} failed:\n"
                         f"{(r.stderr or r.stdout)[-1500:]}")
    return parse(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--lambdas", type=str, default=None,
                    help="comma-separated per-session lambdas")
    args = ap.parse_args()

    lams = ([float(x) for x in args.lambdas.split(",")] if args.lambdas
            else list(DEFAULT_LAMBDAS))
    lams = sorted(set(lams))

    print("=" * 78)
    print("FINE LAMBDA SWEEP -- EXPLORATORY, POST-HOC, NO REGISTERED CRITERION")
    print("=" * 78)
    print("  Mapping the unexplained interior dip at the incumbent lambda.")
    print("  Nothing here may be promoted to a model, a rung, or a claim.")
    print(f"\n  {len(lams)} lambdas, {args.iters} permutations each "
          f"(~{len(lams) * 2} minutes)")
    print("  registered rung reference points:")
    for hl, lam in sorted(RUNG_LAMBDAS.items()):
        print(f"    HL {hl:>4.0f}y  = lambda {lam:.6f}")
    print(f"    INCUMBENT = lambda {INCUMBENT_LAMBDA:.6f}  "
          f"(HL {lam_to_hl(INCUMBENT_LAMBDA):.3f}y)")

    res = {}
    print(f"\n  {'lambda':>10} {'HL (y)':>8}  {'ALL':>28}  {'LONG-HISTORY':>28}")
    for lam in lams:
        hl = lam_to_hl(lam)
        m = run_one(hl, args.iters)
        res[lam] = m
        tag = ""
        if abs(lam - INCUMBENT_LAMBDA) < 1e-12:
            tag = "  <- INCUMBENT"
        for rhl, rlam in RUNG_LAMBDAS.items():
            if abs(lam - rlam) < 5e-6:
                tag = f"  <- near registered HL {rhl:g}y"
        a, l = m["ALL"], m["LONG-HISTORY"]
        print(f"  {lam:10.6f} {hl:8.3f}  "
              f"Sh {a['sharpe']:+.4f} p {a['p']:.4f}  "
              f"Sh {l['sharpe']:+.4f} p {l['p']:.4f}{tag}")

    # ---- description, not explanation ----------------------------------
    lh = np.array([res[l]["LONG-HISTORY"]["sharpe"] for l in lams])
    print("\n" + "=" * 78)
    print("DESCRIPTION (long-history universe)")
    print("=" * 78)
    print(f"  range {lh.min():+.4f} .. {lh.max():+.4f}   "
          f"spread {lh.max() - lh.min():.4f}")
    d = np.abs(np.diff(lh))
    print(f"  largest step between adjacent lambdas: {d.max():.4f} "
          f"(between {lams[int(np.argmax(d))]:.6f} and "
          f"{lams[int(np.argmax(d)) + 1]:.6f})")
    # local minima, strictly interior
    mins = [i for i in range(1, len(lh) - 1) if lh[i] < lh[i - 1] and lh[i] < lh[i + 1]]
    if mins:
        print(f"  interior local minima at lambda: "
              f"{', '.join(f'{lams[i]:.6f} ({lh[i]:+.4f})' for i in mins)}")
    else:
        print("  no interior local minimum -- the curve is monotone or flat "
              "across this range")
    if abs(INCUMBENT_LAMBDA - min(lams, key=lambda x: abs(x - INCUMBENT_LAMBDA))) < 1e-12:
        i = lams.index(INCUMBENT_LAMBDA)
        print(f"\n  INCUMBENT re-run: Sharpe {lh[i]:+.4f}  "
              f"(ladder run reported +0.2500)")
        if abs(lh[i] - 0.25) > 0.02:
            print("  ** RE-RUN DISAGREES WITH THE LADDER RESULT BY MORE THAN 0.02.")
            print("     The earlier 0.25 may be a measurement error. Investigate")
            print("     before anything in docs/ repeats it.")
    print("\n  This scan DESCRIBES the surface. It does not license a claim about")
    print("  which lambda is better -- that question is answered by the")
    print("  registered ladder, and its verdict stands regardless of what is")
    print("  above.")
    print("=" * 78)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Fine lambda sweep — the interior dip", "",
         f"*Run {ts}.*", "",
         "> **EXPLORATORY, POST-HOC, NO REGISTERED CRITERION.** Run after seeing "
         "the ladder, chosen to bracket one anomalous point. It cannot produce a "
         "finding and nothing in it may be promoted to a model, a rung, or a "
         "claim. The registered ladder's verdict "
         "(`docs/recency_sweep_results.md`) stands regardless of what is here.", "",
         "## The anomaly", "",
         "Engine B, long-history, 836 rebalances: HL 4y → 0.3200, incumbent "
         "λ=0.0008 (HL 3.438y) → 0.2500, HL 2y → 0.3000. The incumbent sits "
         "**below both neighbours**. `docs/prereg_rung_diagnostic.md` §3.3 "
         "registered the discriminating check: Engine B top-k overlap runs "
         "0.950 / 0.910 / 0.850 / 0.800 — smooth, no break between 4y and 2y — "
         "so the dip is **unexplained**, not attributable to selection "
         "discreteness.", "",
         "| λ /session | HL (y) | ALL Sharpe | ALL p | long-history Sharpe | "
         "long-history p |", "|---|---|---|---|---|---|"]
    for lam in lams:
        a, l = res[lam]["ALL"], res[lam]["LONG-HISTORY"]
        tag = " **← incumbent**" if abs(lam - INCUMBENT_LAMBDA) < 1e-12 else ""
        for rhl, rlam in RUNG_LAMBDAS.items():
            if abs(lam - rlam) < 5e-6:
                tag = f" *(≈ registered HL {rhl:g}y)*"
        L.append(f"| {lam:.6f}{tag} | {lam_to_hl(lam):.3f} | {a['sharpe']:+.4f} | "
                 f"{a['p']:.4f} | {l['sharpe']:+.4f} | {l['p']:.4f} |")
    L += ["", "## Description", "",
          f"Long-history Sharpe ranges {lh.min():+.4f} to {lh.max():+.4f} across "
          f"this λ interval (spread {lh.max() - lh.min():.4f}). Largest step "
          f"between adjacent λ values: {d.max():.4f}.", "",
          ("Interior local minima at λ = " +
           ", ".join(f"{lams[i]:.6f}" for i in mins) + "."
           if mins else "No interior local minimum across this range."), "",
          "**Reading.** A Sharpe surface that moves materially between adjacent "
          "λ values differing by 1e-4 is a surface on which any single-λ result "
          "is fragile. That fragility is a property of `topk=100` selecting after "
          "weighting, and it applies to every rung of the registered ladder as "
          "much as to the incumbent.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps({f"{l:.6f}": v for l, v in res.items()},
                                   indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
