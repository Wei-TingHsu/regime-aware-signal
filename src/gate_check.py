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
import os
from datetime import datetime, timezone
from pathlib import Path

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


# Cache location -- the same directory corpus_status.py counts. Kept here so
# the gate can check itself against the corpus rather than trusting a CSV.
READS_DIR = REPO / "data_provenance" / "doc_reads"

# Every read CSV the pipeline writes. `read_*.csv` was ADDED 2026-08-25:
# run_corpus.sh writes read_statement.csv / read_minutes.csv / read_8k.csv /
# read_political_order.csv / read_political_other.csv, and the original two
# patterns matched none of them, so a post-corpus gate run would have silently
# re-scored the n=60 pilots and dated the result today.
READ_GLOBS = ("pilot*.csv", "read_*.csv", "doc_reads.csv")


def cache_counts():
    """Cached reads per source, counted from disk.

    The cache filename is {source}__{stem}__{prompt_version}.json, so the source
    is the first field. This is the same count corpus_status.py reports; if the
    gate disagrees with it, one of them is reading a partial file."""
    out = {}
    if READS_DIR.exists():
        for p in READS_DIR.glob("*.json"):
            s = p.name.split("__")[0]
            out[s] = out.get(s, 0) + 1
    return out


def load_all():
    """Every read CSV in processed/, deduplicated on (source, date, doc_id).

    ORDERING IS BY MODIFICATION TIME, oldest first, so `keep="last"` keeps the
    most recently written read of a document: a corrected re-read supersedes the
    run it replaced. The previous version sorted by FILENAME, which happened to
    put pilots before full reads only because 'p' sorts before 'r' -- correct by
    accident, and it would have silently inverted under any rename."""
    paths = []
    for g in READ_GLOBS:
        paths += glob.glob(str(PROCESSED_DIR / g))
    paths = sorted(set(paths), key=os.path.getmtime)

    frames = []
    print("  loading (oldest first; later files win on duplicates):")
    for f in paths:
        try:
            d = pd.read_csv(f)
            d["_file"] = Path(f).name
            frames.append(d)
            n = len(d.dropna(subset=["specificity"])) if "specificity" in d else 0
            print(f"    {Path(f).name:34} {n:6d} rows with specificity")
        except Exception as e:
            print(f"    skipped {Path(f).name}: {type(e).__name__}")
    if not frames:
        raise SystemExit(f"no {' / '.join(READ_GLOBS)} in processed/.")
    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["specificity", "source"])
    if "doc_id" not in df.columns:
        df["doc_id"] = ""
    df["doc_id"] = df["doc_id"].fillna("")
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
    ap.add_argument("--allow-partial", action="store_true",
                    help="run even though the CSVs carry fewer documents than "
                         "the cache holds. The shortfall is printed and written "
                         "into the results file.")
    args = ap.parse_args()

    df = load_all()
    # --- COVERAGE CHECK -----------------------------------------------
    # The gate must be computed on the corpus that exists, not on whatever
    # CSVs happen to be lying in processed/. corpus_status counts the cache;
    # this counts the CSVs; if they disagree, one of them is short and the
    # spread below would be computed on an unstated subset.
    cache = cache_counts()
    csv_n = {s: int(len(g)) for s, g in df.groupby("source")}
    short = {s: (csv_n.get(s, 0), c) for s, c in cache.items()
             if csv_n.get(s, 0) < c}
    coverage_note = ""
    if cache:
        print("\n  coverage -- CSV rows vs cached reads on disk:")
        for s in sorted(set(cache) | set(csv_n)):
            mark = "  <-- SHORT" if s in short else ""
            print(f"    {s:22} csv {csv_n.get(s,0):6d}   cache "
                  f"{cache.get(s,0):6d}{mark}")
    if short:
        coverage_note = ("CSV coverage was SHORT of the cache for: "
                         + "; ".join(f"{s} {a} of {b}" for s, (a, b)
                                     in sorted(short.items())) + ".")
        if not args.allow_partial:
            print("\n" + "!" * 78)
            print("ABORTING -- the CSVs carry fewer documents than the cache "
                  "holds.")
            print("  The gate would be computed on a subset without saying so, "
                  "and the")
            print("  results file would be dated today. That is the failure "
                  "this check")
            print("  exists to prevent.")
            print("\n  Most likely cause: run_corpus.sh did not finish, or a "
                  "source was")
            print("  read without an --out CSV. Re-run the read, or pass "
                  "--allow-partial")
            print("  to proceed with the shortfall recorded in the results "
                  "file.")
            print("!" * 78)
            raise SystemExit(1)
        print(f"\n  ** PROCEEDING PARTIAL (--allow-partial). {coverage_note}")

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
    # Read condition = prompt_version AND model. The cache key carries only
    # the prompt version, so two models can read one corpus under one
    # prompt_version and nothing in the filenames would show it. Checking only
    # the prompt version would report that corpus as uniform.
    vers = {}
    if "prompt_version" in df.columns:
        for s, g in df.groupby("source"):
            vv = sorted(set(g["prompt_version"].dropna().astype(str)) - {""})
            mm = (sorted(set(g["model"].dropna().astype(str)) - {""})
                  if "model" in g.columns else [])
            vers[s] = [f"{v} / {m}" for v in (vv or ["(no prompt_version)"])
                       for m in (mm or ["(model not recorded)"])]

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
