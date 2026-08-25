#!/usr/bin/env python3
"""
patch_political_split.py -- split `political` by the Federal Register's OWN
document-type taxonomy, and add a neutral reader profile for each half.

WHY THE SPLIT IS DEFENSIBLE, AND THE TIMING DECLARED
    `--types "executive order"` never filtered. The corpus holds 923 documents
    across every presidential document type the API returns:

        [determination] Suspension of Limitations Under the Jerusalem Embassy Act
        [proclamation]  Honoring the Victims of the Tragedy in Tucson, Arizona
        [proclamation]  National Teen Dating Violence Awareness Month, 2011
        [notice]        Continuation of the National Emergency ...
        [memorandum]    Delegation of Reporting and Other Authorities
        [executive order] Blocking Property ... Related to Libya

    Pooling a commemorative-month proclamation with a sanctions order and
    reporting ONE mean is the error. They are different document classes and
    the Federal Register already says so.

    *** THIS WAS NOTICED AFTER SEEING THE GATE SPREAD OF 0.26. That is declared,
    not hidden. What makes the split legitimate rather than goalpost-moving is
    that the partition uses the GOVERNMENT'S OWN type tag -- an external,
    pre-existing taxonomy assigned at publication, not a grouping invented by
    us after seeing a number. No document is reassigned by judgement. ***

    It also corrects a registered factual claim: CURRENT_STATE section 8 states
    "the political source is biased toward DECIDED policy ... rhetoric is not
    covered." The corpus falsifies that. Ceremonial and administrative documents
    were there all along, mislabelled as decided policy.

THE PROMPTS ARE DELIBERATELY NEUTRAL
    Neither new profile tells the model that its documents are high or low
    specificity. Priming the reader toward the answer the gate needs would make
    the gate measure the prompt instead of the corpus. Each profile describes
    the document class factually and lets `specificity` fall where it falls.

CACHED READS ARE PRESERVED
    doc_reads JSONs are keyed `<source>__<stem>__<version>.json`. Renaming the
    source folder would orphan the 20 political documents already read and make
    them cost a second time. This script renames the cached reads to match.

Run from the repo root:
    python patch_political_split.py --dry-run
    python patch_political_split.py
"""
import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "data_provenance" / "docs"
READS = ROOT / "data_provenance" / "doc_reads"

# Federal Register's own type tags, as written into the first line of each file
# by fetch_sources. Partition fixed BEFORE any file is inspected individually.
ORDER_TYPES = {"executive order", "presidential order", "determination"}
OTHER_TYPES = {"proclamation", "notice", "memorandum", "other"}

PROFILE_EDIT = (
    "src/doc_read.py",
    '''    "political": ("You classify a political or policy communication (executive''',
    '''    "political_order": (
        "You classify a United States presidential EXECUTIVE ORDER, "
        "PRESIDENTIAL ORDER or PRESIDENTIAL DETERMINATION as published in the "
        "Federal Register. Separate what has been DECIDED from what has been "
        "merely SAID or planned, and judge the text on its own terms.",
        '"extra": {"actor": string, "is_decided": true/false, '
        '"sectors": [string]}'),
    "political_other": (
        "You classify a United States presidential PROCLAMATION, NOTICE or "
        "MEMORANDUM as published in the Federal Register. Separate what has "
        "been DECIDED from what has been merely SAID or planned, and judge the "
        "text on its own terms. Note that this document class spans a wide "
        "range: some are administrative or commemorative, others carry "
        "operative trade or emergency measures. Judge each document by its own "
        "content, not by its class.",
        '"extra": {"actor": string, "is_decided": true/false, '
        '"sectors": [string]}'),
    "political": ("You classify a political or policy communication (executive''',
    "doc_read.PROFILES -- add political_order and political_other, neutrally worded",
)


def read_type(p):
    """First bracketed tag on line 1, written by fetch_sources."""
    try:
        first = p.read_text(errors="replace").lstrip()[:200]
    except Exception:
        return None
    if not first.startswith("["):
        return None
    return first[1:first.find("]")].strip().lower() if "]" in first else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = DOCS / "political"
    if not src.exists():
        raise SystemExit(f"{src} not found -- nothing to split.")

    files = sorted(src.glob("*.txt"))
    print("=" * 74)
    print(f"PHASE 1 -- classifying {len(files)} political documents by "
          f"Federal Register type")
    print("=" * 74)

    plan, types, unknown = {}, Counter(), []
    for f in files:
        t = read_type(f)
        types[t or "(no tag)"] += 1
        if t in ORDER_TYPES:
            plan[f] = "political_order"
        elif t in OTHER_TYPES:
            plan[f] = "political_other"
        else:
            unknown.append(f.name)

    for t, n in types.most_common():
        dest = ("political_order" if t in ORDER_TYPES else
                "political_other" if t in OTHER_TYPES else "UNASSIGNED")
        print(f"  {t:24} {n:5d}  -> {dest}")

    n_order = sum(1 for v in plan.values() if v == "political_order")
    n_other = sum(1 for v in plan.values() if v == "political_other")
    print(f"\n  political_order  {n_order:5d}")
    print(f"  political_other  {n_other:5d}")
    print(f"  unassigned       {len(unknown):5d}")
    if unknown:
        print(f"    {', '.join(unknown[:8])}"
              + (" ..." if len(unknown) > 8 else ""))
        print("    Unassigned files STAY in political/ -- they are not guessed at.")

    # --- the PROFILES edit -------------------------------------------------
    path, anchor, repl, label = PROFILE_EDIT
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f"MISSING FILE: {path}")
    n = p.read_text().count(anchor)
    if n != 1:
        print(f"\n  FAIL  {path}: anchor appears {n}x, must be exactly 1")
        print(f"        sought: {anchor[:70]!r}")
        print("\nABORTED -- NO FILE WAS MODIFIED.")
        sys.exit(1)
    print(f"\n  ok    {path}: {label}")

    if args.dry_run:
        print("\n--dry-run: nothing moved, nothing written.")
        return

    # --- PHASE 2 ------------------------------------------------------------
    print("\n" + "=" * 74)
    print("PHASE 2 -- applying")
    print("=" * 74)
    for d in ("political_order", "political_other"):
        (DOCS / d).mkdir(parents=True, exist_ok=True)

    moved = Counter()
    for f, dest in plan.items():
        shutil.move(str(f), str(DOCS / dest / f.name))
        moved[dest] += 1
    print(f"  moved  {moved['political_order']} -> docs/political_order/")
    print(f"  moved  {moved['political_other']} -> docs/political_other/")

    # cached reads: rename so already-read documents are not paid for twice
    renamed = 0
    if READS.exists():
        for j in sorted(READS.glob("political__*.json")):
            stem = j.name.split("__")[1]
            for dest in ("political_order", "political_other"):
                if (DOCS / dest / f"{stem}.txt").exists():
                    new = j.name.replace("political__", f"{dest}__", 1)
                    j.rename(READS / new)
                    renamed += 1
                    break
    print(f"  renamed {renamed} cached read(s) so they are not re-billed")

    txt = p.read_text()
    assert txt.count(anchor) == 1
    p.write_text(txt.replace(anchor, repl))
    print(f"  written  {path}")

    print("\n" + "=" * 74)
    print("""NEXT -- the n=60 pilot across all five sources, then the gate:

  python -m src.doc_read --source fomc_minutes     --limit 60 --with-prev \\
      --out processed/pilot60_minutes.csv
  python -m src.doc_read --source earnings_8k      --limit 60 \\
      --out processed/pilot60_8k.csv
  python -m src.doc_read --source political_order  --limit 60 \\
      --out processed/pilot60_political_order.csv
  python -m src.doc_read --source political_other  --limit 60 \\
      --out processed/pilot60_political_other.csv

  python -m src.gate_check

REGISTER THE AMENDMENT BEFORE READING THE GATE OUTPUT. Both changes -- the
split and the confidence-interval criterion -- were decided after seeing a
spread of 0.26, and both must say so in docs/prereg_analog_event.md section 11
and in EXECUTION_PLAN.md.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
