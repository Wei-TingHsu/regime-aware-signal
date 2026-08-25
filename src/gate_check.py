"""
gate_check.py -- does `specificity` discriminate between sources?

THE AMENDED CRITERION (see docs/prereg_analog_event.md section 11)
    ORIGINAL, EXECUTION_PLAN.md: "the gate passes if the SPREAD between the
    highest and lowest source mean exceeds 0.25, and decided-policy sources rank
    above opinion sources."

    AMENDED 2026-08-25: the gate passes if the LOWER BOUND of a 95% bootstrap
    confidence interval on that spread exceeds 0.25, and the ordering holds.

    *** TIMING DECLARED: the amendment was made AFTER seeing a point spread of
    0.26 on n=20 per source. It is a TIGHTENING -- a point estimate of 0.26 with
    a 95% interval of roughly [0.13, 0.39] does not distinguish passing from
    failing, and the original criterion could not say so. Requiring the lower
    bound to clear 0.25 is strictly harder to satisfy than requiring the point
    estimate to. Recorded rather than quietly applied. ***

WHY A POINT COMPARISON WAS NEVER ENOUGH
    Each source mean came from n=20. With specificity sd around 0.2 that is
    se ~ 0.045 per mean, so a difference of two means carries se ~ 0.063. A
    threshold of 0.25 sits well inside the interval around 0.26. The original
    criterion reported a coin flip as a pass.

WHAT FAILING MEANS
    prereg_analog_event.md section 2.1: `specificity` enters the content-class
    definition ONLY if this gate passes. Section 7.2: it enters the step 5
    weighting rule only if this gate passes. A failure removes it from both and
    BOTH SUBSTITUTIONS ARE REPORTED -- it does not stop the product shipping.

Run:
    python -m src.gate_check
    python -m src.gate_check --iters 20000
"""
import argparse
import glob
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "gate_check_results.md"
OUT_JSON = PROCESSED_DIR / "gate_check.json"

THRESHOLD = 0.25          # registered
CI = 95

# Registered expected ordering. Decided/operative and reported-results sources
# ABOVE deliberative, ceremonial and opinion sources.
EXPECT_HIGH = {"political_order", "earnings_8k", "fomc_statement"}
# fomc_minutes REMOVED from the low group 2026-08-25. It was my
# classification, not a registered one: EXECUTION_PLAN's low column named
# bank_research and transcripts, and neither has any documents. Minutes are
# genuinely ambiguous -- they report a decision public for three weeks, but
# their new content is deliberative -- so they must not anchor a pass/fail.
# political_other is also post-hoc, but rests on the Federal Register's own
# document type: an external taxonomy, not a judgement call.
EXPECT_LOW = {"political_other", "bank_research", "transcript"}


def load_all():
    """Every pilot CSV plus any full read, deduplicated on (source, date, doc_id).

    Reads whatever is in processed/. A source appearing in several files (a v1
    and a v2 pilot, say) keeps the LAST occurrence, so a corrected re-read
    supersedes the run it replaced."""
    frames = []
    for f in sorted(glob.glob(str(PROCESSED_DIR / "pilot*.csv"))
                    + glob.glob(str(PROCESSED_DIR / "doc_reads.csv"))):
        try:
            d = pd.read_csv(f)
            d["_file"] = f.split("/")[-1]
            frames.append(d)
        except Exception as e:
            print(f"  skipped {f}: {type(e).__name__}")
    if not frames:
        raise SystemExit("no pilot*.csv or doc_reads.csv in processed/.")
    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["specificity", "source"])
    df["doc_id"] = df.get("doc_id", "").fillna("")
    return df.drop_duplicates(subset=["source", "date", "doc_id"], keep="last")


def bootstrap_spread(groups, iters, rng):
    """Resample WITHIN each source, recompute max-min of the source means.

    Resampling within groups preserves the group sizes, so the interval reflects
    uncertainty in the means and not in how many documents each source has."""
    keys = list(groups)
    arrs = [np.asarray(groups[k], float) for k in keys]
    out = np.empty(iters)
    for i in range(iters):
        means = [a[rng.integers(0, len(a), len(a))].mean() for a in arrs]
        out[i] = max(means) - min(means)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=10000)
    args = ap.parse_args()

    df = load_all()
    groups = {s: g["specificity"].dropna().values
              for s, g in df.groupby("source") if len(g) >= 5}
    if len(groups) < 2:
        raise SystemExit("need at least two sources with n>=5.")

    rng = np.random.default_rng(42)
    print("=" * 78)
    print("SPECIFICITY GATE -- amended criterion: LOWER BOUND of the 95% CI")
    print(f"on the spread must exceed {THRESHOLD:.2f}")
    print("=" * 78)
    # Read condition per source, so a cross-source comparison that is ALSO a
    # cross-prompt comparison cannot pass unnoticed.
    vers = {}
    if "prompt_version" in df.columns:
        for s, g in df.groupby("source"):
            vv = sorted(set(g["prompt_version"].dropna().astype(str)) - {""})
            vers[s] = vv

    print(f"\n  {'source':22} {'n':>5} {'mean':>8} {'sd':>7} {'se':>7}   "
          f"{'expected':>9}   read condition")
    stats = {}
    for s in sorted(groups, key=lambda k: -np.mean(groups[k])):
        v = groups[s]
        se = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else np.nan
        exp = ("HIGH" if s in EXPECT_HIGH else
               "low" if s in EXPECT_LOW else "-")
        pv = ", ".join(vers.get(s, [])) or "(not recorded)"
        stats[s] = dict(n=int(len(v)), mean=float(v.mean()),
                        sd=float(v.std(ddof=1)), se=float(se), expected=exp,
                        prompt_versions=vers.get(s, []))
        print(f"  {s:22} {len(v):5d} {v.mean():8.3f} {v.std(ddof=1):7.3f} "
              f"{se:7.3f}   {exp:>9}   {pv}")

    allv = sorted({v for vv in vers.values() for v in vv})
    if len(allv) > 1:
        print(f"\n  ** MIXED READ CONDITIONS: {', '.join(allv)}")
        print("     Sources were not all read under the same prompt version.")
        print("     Part of any spread below may be a prompt difference rather")
        print("     than a corpus difference. Reported, not adjusted for --")
        print("     there is no way to separate the two without re-reading")
        print("     every source under one version.")
    elif allv:
        print(f"\n  read condition uniform: {allv[0]}")

    hi = max(groups, key=lambda k: np.mean(groups[k]))
    lo = min(groups, key=lambda k: np.mean(groups[k]))
    point = float(np.mean(groups[hi]) - np.mean(groups[lo]))

    boot = bootstrap_spread(groups, args.iters, rng)
    lob, hib = np.percentile(boot, [(100 - CI) / 2, 100 - (100 - CI) / 2])

    print(f"\n  widest pair: {hi} ({np.mean(groups[hi]):.3f}) "
          f"vs {lo} ({np.mean(groups[lo]):.3f})")
    print(f"  spread       {point:.3f}")
    print(f"  {CI}% CI      [{lob:.3f}, {hib:.3f}]   ({args.iters:,} bootstrap "
          f"resamples within source)")

    # --- the two clauses ---------------------------------------------------
    clause_ci = lob > THRESHOLD
    highs = [np.mean(groups[s]) for s in groups if s in EXPECT_HIGH]
    lows = [np.mean(groups[s]) for s in groups if s in EXPECT_LOW]
    clause_order = bool(highs and lows and min(highs) > max(lows))

    print(f"\n  clause 1 (CI lower bound > {THRESHOLD:.2f}): "
          f"{lob:.3f} -> {'PASS' if clause_ci else 'FAIL'}")
    if highs and lows:
        print(f"  clause 2 (every HIGH source above every low source): "
              f"min HIGH {min(highs):.3f} vs max low {max(lows):.3f} -> "
              f"{'PASS' if clause_order else 'FAIL'}")
    else:
        print("  clause 2: NOT EVALUABLE -- expected-high or expected-low "
              "sources are missing from the corpus.")

    passed = clause_ci and clause_order
    print("\n" + "=" * 78)
    print(f"GATE: {'PASS' if passed else 'FAIL'}")
    if not passed:
        print("  specificity is REMOVED from the content-class definition")
        print("  (prereg_analog_event.md 2.1) and from the step 5 weighting")
        print("  rule (7.2). Both substitutions are REPORTED. The product still")
        print("  ships -- this changes what it weighs with, not whether it runs.")
    print("=" * 78)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Specificity gate — result", "", f"*Run {ts}.*", "",
         f"**Amended criterion** (`docs/prereg_analog_event.md` §11): the lower "
         f"bound of a {CI}% bootstrap CI on the spread must exceed "
         f"{THRESHOLD:.2f}, and every expected-high source must sit above every "
         f"expected-low source.", "",
         "> **Timing declared.** The amendment was made after seeing a point "
         "spread of 0.26 on n=20 per source. It is a **tightening** — the "
         "original point comparison could not distinguish 0.26 from failing. "
         "Recorded rather than quietly applied.", "",
         "| source | n | mean specificity | sd | se | expected | read condition |",
         "|---|---|---|---|---|---|---|"]
    for s, d in sorted(stats.items(), key=lambda kv: -kv[1]["mean"]):
        pv = ", ".join(d.get("prompt_versions", [])) or "(not recorded)"
        L.append(f"| {s} | {d['n']} | {d['mean']:.3f} | {d['sd']:.3f} | "
                 f"{d['se']:.3f} | {d['expected']} | {pv} |")
    _allv = sorted({v for d in stats.values()
                    for v in d.get("prompt_versions", [])})
    if len(_allv) > 1:
        L += ["", f"> **Mixed read conditions: {', '.join(_allv)}.** Sources "
                  "were not all read under the same prompt version, so part of "
                  "the spread may be a prompt difference rather than a corpus "
                  "difference. Reported, not adjusted for — the two cannot be "
                  "separated without re-reading every source under one version."]
    L += ["", f"Widest pair: **{hi}** vs **{lo}**. Spread **{point:.3f}**, "
              f"{CI}% CI **[{lob:.3f}, {hib:.3f}]**.", "",
          f"- Clause 1 (CI lower bound > {THRESHOLD:.2f}): "
          f"**{'PASS' if clause_ci else 'FAIL'}**",
          f"- Clause 2 (ordering): **{'PASS' if clause_order else 'FAIL'}**", "",
          f"## Verdict: {'PASS' if passed else 'FAIL'}", "",
          ("`specificity` enters the content-class definition (§2.1) and the "
           "step 5 weighting rule (§7.2)." if passed else
           "`specificity` is **removed** from the content-class definition "
           "(§2.1) and from the step 5 weighting rule (§7.2). Both "
           "substitutions are reported. The product still ships — this changes "
           "what it weighs with, not whether it runs."), ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        dict(sources=stats, spread=point, ci=[float(lob), float(hib)],
             threshold=THRESHOLD, clause_ci=bool(clause_ci),
             clause_order=clause_order, passed=bool(passed),
             iters=args.iters), indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
