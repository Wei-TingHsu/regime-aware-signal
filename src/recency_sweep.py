"""
recency_sweep.py -- PROBLEM 3 STEP 1, item 1: the pre-registered recency ladder.

REGISTERED IN docs/prereg_recency_kernel.md (committed BEFORE this ran):
    form      exponential, recency = exp(-ln2 * age_years / HL)
    ladder    HL in {2, 4, 8, 16, inf}
    primary   HL = 4y, on US-presidential-term grounds
    criterion beats the no-decay control on the LONG-HISTORY universe at the
              primary rung, AND improvement is monotone or stable across at
              least three adjacent rungs.
    reporting ALL rungs, both universes, no cherry-picking. A single winning
              rung is a GRID WINNER, NOT A FINDING.

REGISTERED EXPECTATION: little or no improvement. With no decay the weighted
mean analog age is already 0.40y and median ESS is 100/100 -- the engine
averages the recent same-regime past with near-uniform weights rather than
locating distinctive analogs. The lever is sigma, not lambda, and sigma is
frozen. A LARGE SHARPE CHANGE WOULD BE SUSPECT, NOT SUCCESS.

TWO ENGINES, because they are two different estimators (prereg amendment
2026-08-24):

  ENGINE A  src/analog_core.py via model_grid's code path
            z-scored PC features, ONE GMM frozen on all history, no decay by
            default. This is the frozen-model and live-harness engine.
            model_1_baseline reports Sharpe ~0.40 here.

  ENGINE B  src/analog_backtest.py
            RAW PC features (PC1 dominates the distance), GMM refit
            expanding-window every 20 sessions, and decay applied ALL ALONG at
            config's recency_decay_lambda = 0.0008/session = HL 3.44y.
            This is the engine behind the reported 0.51 / 0.25.

            Engine B at HL=inf is a number that has NEVER been computed. It is
            the only way to learn what the headline result owes to an
            unregistered hyperparameter with no recorded provenance.

THE CONTROL RUNG RUNS FIRST AND IS ASSERTED, NOT INSPECTED
    HL=inf on Engine A is bit-identically model_1_baseline: _kw() short-circuits
    on `hl is None` and returns the bare similarity kernel. If this harness
    matches the frozen model's code path, the two spread SERIES are equal
    element-wise at zero tolerance. If they are not, the ladder is meaningless
    and this script exits without running a single decayed rung.

    Asserted on the ~836-element spread array, not the Sharpe. Two genuinely
    different runs can both print +0.40; two identical runs cannot differ in
    836 floats. A mismatch names the rebalance that diverged.

    NOTE ON RECORDED FIGURES: the control is asserted against a baseline run
    IN THIS SESSION ON THIS PANEL, never against the numbers written in docs/.
    The panel has grown since those were recorded -- 2026-08-24 reproduction
    gave 836 rebalances and ALL-47 Sharpe 0.52 where docs record 835 and 0.51.
    Comparing against a stale record would fail for the wrong reason.

Run:
    python -m src.recency_sweep                    # both engines, full ladder
    python -m src.recency_sweep --engine A         # analog_core only
    python -m src.recency_sweep --engine B         # analog_backtest only
    python -m src.recency_sweep --iters 200        # faster, wider p resolution
    python -m src.recency_sweep --skip-control     # NOT ALLOWED for a reported
                                                   # run; refuses to write output
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.analog_core import DEFAULT, load_data, backtest
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
MODELS_YAML = REPO / "config" / "models.yaml"
OUT_MD = REPO / "docs" / "recency_sweep_results.md"
OUT_JSON = REPO / "processed" / "recency_sweep.json"

# The registered ladder. inf FIRST: it is the control, and nothing else is
# trusted until it reproduces the frozen model exactly.
LADDER = [float("inf"), 16.0, 8.0, 4.0, 2.0]
PRIMARY_HL = 4.0
MIN_HISTORY_YEARS = 8.0          # same cut as analog_backtest --min-history


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def load_baseline_spec():
    """model_1_baseline, read from the FROZEN block of models.yaml.

    Reads `models:` only. Verifies the frozen-block checksum first, for the
    same reason forward_log and model_grid do: the ladder is defined relative
    to this spec, so a silently altered baseline would move every rung.
    """
    raw = yaml.safe_load(MODELS_YAML.read_text())
    if "models" not in raw:
        raise SystemExit(f"{MODELS_YAML} has no `models:` key.")
    frozen = raw["models"]

    sha_path = MODELS_YAML.parent / "models.frozen.sha256"
    if not sha_path.exists():
        raise SystemExit(f"missing {sha_path} -- cannot verify the frozen block.")
    import hashlib
    got = hashlib.sha256(json.dumps(frozen, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()
    want = sha_path.read_text().split()[0].strip()
    if got != want:
        raise SystemExit(
            f"FROZEN MODEL REGISTRY ALTERED.\n  expected {want}\n  got      {got}\n"
            "  The ladder is defined relative to model_1_baseline. Refusing to run\n"
            "  against an altered baseline.")

    if "model_1_baseline" not in frozen:
        raise SystemExit("model_1_baseline missing from the frozen block.")
    s = dict(DEFAULT)
    s.update({k: v for k, v in frozen["model_1_baseline"].items() if k != "note"})
    print(f"  frozen registry verified (sha {got[:12]}), baseline: "
          f"horizon {s['horizon']}d | {s['sim_mode']} | {s['kernel']} | "
          f"sigma {s['sigma']} | n={s['n_regimes']}")
    return s


def long_history_mask(rets):
    """Assets with >= MIN_HISTORY_YEARS of data. Same rule as analog_backtest's
    --min-history, so the two engines' long-history universes are the same set."""
    return rets.notna().sum().values >= MIN_HISTORY_YEARS * 252


def spec_for(base, hl):
    """Baseline spec with one rung's half-life. inf -> None, which makes _kw()
    short-circuit and return the bare similarity kernel -- the genuine control."""
    s = dict(base)
    s["half_life_years"] = None if np.isinf(hl) else float(hl)
    return s


def fmt_hl(hl):
    return "inf (no decay)" if np.isinf(hl) else f"{hl:g}y"


# ---------------------------------------------------------------------------
# ENGINE A -- analog_core
# ---------------------------------------------------------------------------

def run_engine_a(iters, skip_control):
    print("\n" + "=" * 78)
    print("ENGINE A -- analog_core (z-scored PCs, frozen GMM, no-decay default)")
    print("=" * 78)
    cfg = load_config()
    base = load_baseline_spec()
    scores, rets = load_data()

    lh = long_history_mask(rets)
    rets_lh = rets.loc[:, lh]
    print(f"  panel: {len(scores)} sessions, {rets.shape[1]} assets | "
          f"long-history (>={MIN_HISTORY_YEARS:g}y): {int(lh.sum())} assets")
    print(f"  dropped from long-history: "
          f"{', '.join(rets.columns[~lh])}")

    universes = [("ALL", rets), ("LONG-HISTORY", rets_lh)]
    results = {}

    # ---- CONTROL RUNG FIRST -------------------------------------------
    if not skip_control:
        print("\n  CONTROL RUNG (HL=inf) -- must reproduce model_1_baseline "
              "element-wise")
        for uname, r in universes:
            ctrl = backtest(scores, r, spec_for(base, float("inf")), cfg,
                            do_perm=False)
            ref = backtest(scores, r, dict(base), cfg, do_perm=False)
            if ctrl is None or ref is None:
                raise SystemExit(f"  control rung produced no result on {uname}.")
            if "spreads" not in ctrl:
                raise SystemExit(
                    "  analog_core.backtest() does not return `spreads`.\n"
                    "  Run patch_core_spreads.py first -- the control rung cannot\n"
                    "  be asserted on aggregates alone.")
            a, b = np.asarray(ctrl["spreads"]), np.asarray(ref["spreads"])
            if a.shape != b.shape:
                raise SystemExit(
                    f"  CONTROL FAILED on {uname}: {a.shape[0]} rebalances vs "
                    f"{b.shape[0]}. Harness does not match the frozen path.")
            if not np.array_equal(a, b):
                bad = np.flatnonzero(a != b)
                pos = np.asarray(ctrl["rebalance_pos"])
                raise SystemExit(
                    f"  CONTROL FAILED on {uname}: {len(bad)} of {len(a)} "
                    f"rebalances differ.\n"
                    f"    first at index {bad[0]} (panel pos {pos[bad[0]]}, "
                    f"{scores.index[pos[bad[0]]].date()}): "
                    f"{a[bad[0]]:.17g} vs {b[bad[0]]:.17g}\n"
                    "  The ladder is meaningless until this is zero. NOT RUNNING "
                    "the decayed rungs.")
            print(f"    {uname:14} {len(a)} rebalances, spread series identical "
                  f"(max |diff| = 0.0)")
        print("  CONTROL PASSED -- harness matches the frozen model exactly.")
    else:
        print("\n  !! --skip-control: the ladder is NOT verified against the "
              "frozen model.")

    # ---- the ladder ----------------------------------------------------
    print(f"\n  running the ladder ({iters} permutations per cell)")
    for hl in LADDER:
        for uname, r in universes:
            m = backtest(scores, r, spec_for(base, hl), cfg,
                         do_perm=True, iters=iters)
            if m is None:
                print(f"    HL {fmt_hl(hl):14} {uname:14} no usable dates")
                continue
            results[(hl, uname)] = m
            star = "  <- PRIMARY" if (hl == PRIMARY_HL and uname == "LONG-HISTORY") else ""
            print(f"    HL {fmt_hl(hl):14} {uname:14} n={m['n']:4d}  "
                  f"Sharpe {m['sharpe']:+.4f}  spread {m['spread']*100:+.4f}%  "
                  f"p {m['p']:.4f}{star}")
    return results


# ---------------------------------------------------------------------------
# ENGINE B -- analog_backtest, via its CLI
# ---------------------------------------------------------------------------

_SHARPE_RE = re.compile(r"SHARPE \(ann\.\): spread ([+-][\d.]+)\s+long-leg ([+-][\d.]+)")
_SPREAD_RE = re.compile(r"mean weekly spread = ([+-][\d.]+)%")
_P_RE = re.compile(r"p = ([\d.]+)")
_N_RE = re.compile(r"walk-forward complete: (\d+) rebalances")


def _parse_backtest_output(out):
    """Parse analog_backtest's stdout. STRICT: the expected shape is exactly two
    universe blocks. Anything else raises rather than returning a partial read --
    a regex that quietly finds one block would report half a ladder as a whole one.
    """
    sh = _SHARPE_RE.findall(out)
    sp = _SPREAD_RE.findall(out)
    ps = _P_RE.findall(out)
    n = _N_RE.findall(out)
    if len(sh) != 2 or len(sp) != 2 or len(ps) != 2 or len(n) != 1:
        raise SystemExit(
            "could not parse analog_backtest output: expected 2 universe blocks, "
            f"found sharpe={len(sh)} spread={len(sp)} p={len(ps)} n={len(n)}.\n"
            "Its output format changed; fix this parser rather than trusting a "
            "partial read.\n--- output tail ---\n" + out[-1200:])
    names = ["ALL", "LONG-HISTORY"]
    return {names[i]: dict(sharpe=float(sh[i][0]), long_leg_sharpe=float(sh[i][1]),
                           spread=float(sp[i]) / 100.0, p=float(ps[i]),
                           n=int(n[0]))
            for i in range(2)}


def run_engine_b(iters):
    print("\n" + "=" * 78)
    print("ENGINE B -- analog_backtest (raw PCs, expanding refit, incumbent decay)")
    print("=" * 78)
    results = {}

    # incumbent first -- the basis of the recorded 0.51 / 0.25
    print("\n  INCUMBENT (config lambda=0.0008/session, HL 3.44y) "
          "-- off-ladder, never a rung")
    r = subprocess.run([sys.executable, "-m", "src.analog_backtest",
                        "--iters", str(iters)],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"analog_backtest failed:\n{(r.stderr or r.stdout)[-1500:]}")
    inc = _parse_backtest_output(r.stdout)
    for u, m in inc.items():
        print(f"    {u:14} n={m['n']:4d}  Sharpe {m['sharpe']:+.4f}  "
              f"spread {m['spread']*100:+.4f}%  p {m['p']:.4f}")
    results[("incumbent", "ALL")] = inc["ALL"]
    results[("incumbent", "LONG-HISTORY")] = inc["LONG-HISTORY"]

    print(f"\n  running the ladder ({iters} permutations per cell)")
    for hl in LADDER:
        arg = "inf" if np.isinf(hl) else f"{hl:g}"
        r = subprocess.run([sys.executable, "-m", "src.analog_backtest",
                            "--half-life", arg, "--iters", str(iters)],
                           capture_output=True, text=True, cwd=REPO)
        if r.returncode != 0:
            raise SystemExit(f"analog_backtest --half-life {arg} failed:\n"
                             f"{(r.stderr or r.stdout)[-1500:]}")
        parsed = _parse_backtest_output(r.stdout)
        for uname, m in parsed.items():
            results[(hl, uname)] = m
            star = "  <- PRIMARY" if (hl == PRIMARY_HL and uname == "LONG-HISTORY") else ""
            note = "  <- NEVER COMPUTED BEFORE" if np.isinf(hl) else ""
            print(f"    HL {fmt_hl(hl):14} {uname:14} n={m['n']:4d}  "
                  f"Sharpe {m['sharpe']:+.4f}  spread {m['spread']*100:+.4f}%  "
                  f"p {m['p']:.4f}{star}{note}")
    return results


# ---------------------------------------------------------------------------
# verdict + report
# ---------------------------------------------------------------------------

def verdict(res, engine):
    """Apply the registered criterion. LONG-HISTORY only -- that is what the
    registration names as primary. ALL-47 is reported as a diagnostic."""
    ctrl = res.get((float("inf"), "LONG-HISTORY"))
    prim = res.get((PRIMARY_HL, "LONG-HISTORY"))
    if ctrl is None or prim is None:
        return ("INCONCLUSIVE", "control or primary rung missing on the "
                                "long-history universe.")

    beats = prim["sharpe"] > ctrl["sharpe"]
    if not beats:
        return ("NULL", f"primary rung HL={PRIMARY_HL:g}y Sharpe "
                        f"{prim['sharpe']:+.4f} does not beat the no-decay "
                        f"control {ctrl['sharpe']:+.4f}. The registered "
                        f"criterion requires BOTH conditions; the first fails, "
                        f"so stability is not evaluated.")

    # STABILITY. Section 6 says "monotone or stable across at least three
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
                        f"the reported figure]")


def write_report(a_res, b_res, iters):
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = [f"# Recency kernel sweep -- results", "",
         f"*Run {ts}. Registered in `docs/prereg_recency_kernel.md` "
         f"(ladder, primary rung and criterion committed BEFORE this ran; "
         f"two-engine amendment 2026-08-24).*", "",
         f"Permutations per cell: {iters}.", "",
         "**Every rung is reported. A single winning rung is a grid winner, "
         "not a finding.**", "",
         "**Registered expectation: little or no improvement.** With no decay "
         "the weighted mean analog age is already 0.40y and median ESS is "
         "100/100. The lever is sigma, not lambda, and sigma is frozen. A large "
         "Sharpe change would be suspect, not success.", ""]

    for engine, res, desc in [
        ("A", a_res, "`analog_core` -- z-scored PCs, one GMM frozen on all "
                     "history, genuinely no-decay by default. The frozen-model "
                     "and live-harness engine."),
        ("B", b_res, "`analog_backtest` -- raw PCs, GMM refit expanding-window "
                     "every 20 sessions, decayed all along at "
                     "`recency_decay_lambda=0.0008`/session (HL 3.44y). **The "
                     "engine behind the reported 0.51 / 0.25.**")]:
        if not res:
            continue
        L += [f"## Engine {engine}", "", desc, "",
              "| rung | universe | n | Sharpe | spread/reb | p |",
              "|---|---|---|---|---|---|"]
        keys = ["incumbent"] + LADDER if ("incumbent", "ALL") in res else LADDER
        for hl in keys:
            for u in ["ALL", "LONG-HISTORY"]:
                if (hl, u) not in res:
                    continue
                m = res[(hl, u)]
                label = ("incumbent (HL 3.44y, **off-ladder**)"
                         if hl == "incumbent" else fmt_hl(hl))
                tag = ""
                if hl == PRIMARY_HL and u == "LONG-HISTORY":
                    tag = " **<- PRIMARY**"
                elif not isinstance(hl, str) and np.isinf(hl):
                    tag = " (control)"
                L.append(f"| {label}{tag} | {u} | {m['n']} | {m['sharpe']:+.4f} | "
                         f"{m['spread']*100:+.4f}% | {m['p']:.4f} |")
        v, why = verdict(res, engine)
        L += ["", f"**VERDICT against the registered criterion: {v}**", "",
              why, ""]

    L += ["## Reading", "",
          "The two engines are different estimators and legitimately report "
          "different numbers. Neither is a rung of the other's ladder.", "",
          "Engine B's `inf` rung is the number that had never been computed: "
          "the headline engine with its unregistered decay removed. The gap "
          "between it and the incumbent row is what the reported 0.51 / 0.25 "
          "owe to a hyperparameter with no recorded provenance.", ""]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L) + "\n")

    ser = {f"{e}|{k[0]}|{k[1]}": {kk: (float(vv) if isinstance(vv, (int, float, np.floating)) else vv)
                                  for kk, vv in m.items() if kk not in ("spreads", "rebalance_pos")}
           for e, res in [("A", a_res), ("B", b_res)] for k, m in res.items()}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(ser, indent=2))
    print(f"\n  -> {OUT_MD}")
    print(f"  -> {OUT_JSON}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["A", "B", "both"], default="both")
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--rederive", action="store_true",
                    help="recompute the verdict from processed/recency_sweep.json "
                         "and rewrite the report. Does NOT re-run the ladder -- "
                         "the numbers are unchanged, only the count derived "
                         "from them.")
    ap.add_argument("--skip-control", action="store_true",
                    help="skip the control-rung assertion. NOT ALLOWED for a "
                         "reported run: no output file is written.")
    args = ap.parse_args()

    if args.rederive:
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
                print(f"\nENGINE {e} VERDICT: {v}\n  {why}")
        write_report(a_res, b_res, args.iters)
        return

    print("=" * 78)
    print("RECENCY KERNEL SWEEP -- pre-registered ladder {2, 4, 8, 16, inf}")
    print("=" * 78)
    print(f"  primary rung: HL={PRIMARY_HL:g}y, LONG-HISTORY universe")
    print(f"  permutations: {args.iters} per cell")

    a_res = run_engine_a(args.iters, args.skip_control) \
        if args.engine in ("A", "both") else {}
    b_res = run_engine_b(args.iters) if args.engine in ("B", "both") else {}

    print("\n" + "=" * 78)
    for e, res in [("A", a_res), ("B", b_res)]:
        if res:
            v, why = verdict(res, e)
            print(f"ENGINE {e} VERDICT: {v}")
            print(f"  {why}")
    print("=" * 78)

    if args.skip_control:
        print("\n--skip-control was used: NO OUTPUT WRITTEN. An unverified "
              "ladder is not a reportable result.")
        return
    write_report(a_res, b_res, args.iters)


if __name__ == "__main__":
    main()
