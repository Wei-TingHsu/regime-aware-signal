#!/usr/bin/env python3
"""
patch_prompt_version.py -- make the read condition visible in every CSV.

WHY
    The gate will compare `fomc_statement` (131 documents read 2026-08-23 under
    prompt v1) against sources read 2026-08-25. If the prompt or model differs
    at all, that is a comparison across READ CONDITIONS, not across sources.

    doc_read's flat CSV drops `prompt_version` and `model`, so the mixture would
    be invisible. The decision was to INCLUDE the older reads and REPORT the
    version alongside -- which requires the version to actually be in the file.

    This is the same class of problem as the 8-K cover pages: a comparison that
    looks clean because the thing that would reveal it was never written down.

Run from the repo root:
    python patch_prompt_version.py --dry-run
    python patch_prompt_version.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/doc_read.py",
    """        flat.append(dict(date=r.get("date"), source=r.get("source"),
                         doc_id=r.get("doc_id", ""),""",
    """        flat.append(dict(date=r.get("date"), source=r.get("source"),
                         doc_id=r.get("doc_id", ""),
                         # Read condition, carried into the CSV so any
                         # cross-source comparison can show whether it is also a
                         # cross-prompt or cross-model comparison. Without these
                         # two columns that mixture is invisible.
                         prompt_version=r.get("prompt_version", ""),
                         model=r.get("model", ""),""",
    "doc_read -- carry prompt_version and model into the flat CSV",
), (
    "src/gate_check.py",
    """    print(f"\\n  {'source':22} {'n':>5} {'mean':>8} {'sd':>7} {'se':>7}   expected")
    stats = {}
    for s in sorted(groups, key=lambda k: -np.mean(groups[k])):
        v = groups[s]
        se = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else np.nan
        exp = ("HIGH" if s in EXPECT_HIGH else
               "low" if s in EXPECT_LOW else "—")
        stats[s] = dict(n=int(len(v)), mean=float(v.mean()),
                        sd=float(v.std(ddof=1)), se=float(se), expected=exp)
        print(f"  {s:22} {len(v):5d} {v.mean():8.3f} {v.std(ddof=1):7.3f} "
              f"{se:7.3f}   {exp}")""",
    """    # Read condition per source, so a cross-source comparison that is ALSO a
    # cross-prompt comparison cannot pass unnoticed.
    vers = {}
    if "prompt_version" in df.columns:
        for s, g in df.groupby("source"):
            vv = sorted(set(g["prompt_version"].dropna().astype(str)) - {""})
            vers[s] = vv

    print(f"\\n  {'source':22} {'n':>5} {'mean':>8} {'sd':>7} {'se':>7}   "
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
        print(f"\\n  ** MIXED READ CONDITIONS: {', '.join(allv)}")
        print("     Sources were not all read under the same prompt version.")
        print("     Part of any spread below may be a prompt difference rather")
        print("     than a corpus difference. Reported, not adjusted for --")
        print("     there is no way to separate the two without re-reading")
        print("     every source under one version.")
    elif allv:
        print(f"\\n  read condition uniform: {allv[0]}")""",
    "gate_check -- report prompt version per source and flag mixed conditions",
), (
    "src/gate_check.py",
    """         "| source | n | mean specificity | sd | se | expected |",
         "|---|---|---|---|---|---|"]
    for s, d in sorted(stats.items(), key=lambda kv: -kv[1]["mean"]):
        L.append(f"| {s} | {d['n']} | {d['mean']:.3f} | {d['sd']:.3f} | "
                 f"{d['se']:.3f} | {d['expected']} |")""",
    """         "| source | n | mean specificity | sd | se | expected | read condition |",
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
                  "separated without re-reading every source under one version."]""",
    "gate_check -- carry read condition into the written report",
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
    print("""NEXT -- rebuild the fomc_statement CSV from cache (FREE, all 131 are
already read), so the gate can include them with their version visible:

  python -m src.doc_read --source fomc_statement --limit 131 \\
      --out processed/fomc_statement_all.csv

Then the n=60 pilots and the gate.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
