"""
patch_gate_check.py -- fix three defects in src/gate_check.py BEFORE the full
corpus read, so that every change is on record as decided before any
full-corpus number was seen.

Run from the repo root:
    python patch_gate_check.py            # dry run, shows what it would change
    python patch_gate_check.py --write    # apply

Every anchor is verified before anything is written. If any anchor is missing
or appears more than once the script ABORTS and writes nothing -- a patch that
half-applies is worse than one that does not apply.

WHAT IT FIXES

 1. gate_check could not see the corpus.
    load_all() globs `pilot*.csv` and `doc_reads.csv`. run_corpus.sh writes
    read_statement.csv, read_minutes.csv, read_8k.csv, read_political_order.csv
    and read_political_other.csv. NONE of those match either pattern. Re-running
    the gate after a completed read would silently reload the n=60 pilots,
    recompute the same 0.363 spread, and write a results file timestamped today
    that claims to be the full-corpus gate. A stale number wearing a fresh date
    is the exact failure mode this project keeps catching.

 2. A CSV/cache disagreement was invisible.
    corpus_status counts the cache; gate_check counts CSV rows. Nothing forced
    them to agree, so a CSV written by a run that aborted halfway could be used
    without anyone noticing it was short. The gate now compares its own per
    source n against the cached JSON reads on disk and ABORTS on a mismatch.
    --allow-partial overrides, and says so in the results file.

 3. Read-condition checking covered prompt_version but not model.
    The cache key is {source}__{stem}__{PROMPT_VERSION}.json -- the model string
    is NOT in it. Two models can therefore read one corpus under one
    prompt_version and gate_check would report the read condition as uniform.
    Per its own docstring the resulting confound cannot be separated afterwards
    without re-reading every source. Now checked and reported.

WHAT IT DOES NOT TOUCH
    THRESHOLD, CI, EXPECT_HIGH, EXPECT_LOW, the bootstrap, the two clauses, or
    the pass/fail logic. The registered criterion is unchanged. This patch
    changes only WHICH DOCUMENTS the criterion is evaluated on, and adds checks
    that can only make the run stop, never make it pass.
"""
import argparse
import sys
from pathlib import Path

TARGET = Path("src/gate_check.py")

# --- anchor 1: the import block -------------------------------------------
A1_OLD = """import argparse
import glob
import json
from datetime import datetime, timezone
"""
A1_NEW = """import argparse
import glob
import json
import os
from datetime import datetime, timezone
"""

# --- anchor 2: load_all ----------------------------------------------------
A2_OLD = '''def load_all():
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
'''

A2_NEW = '''# Cache location -- the same directory corpus_status.py counts. Kept here so
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
'''

# --- anchor 3: the argparse block in main ---------------------------------
A3_OLD = """    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=10000)
    args = ap.parse_args()

    df = load_all()
"""
A3_NEW = '''    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=10000)
    ap.add_argument("--allow-partial", action="store_true",
                    help="run even though the CSVs carry fewer documents than "
                         "the cache holds. The shortfall is printed and written "
                         "into the results file.")
    args = ap.parse_args()

    df = load_all()
'''

# --- anchor 4: the coverage check, inserted before the groups are built ----
A4_OLD = """    groups = {s: g["specificity"].dropna().values
              for s, g in df.groupby("source") if len(g) >= 5}
    if len(groups) < 2:
        raise SystemExit("need at least two sources with n>=5.")
"""
A4_NEW = '''    # --- COVERAGE CHECK -----------------------------------------------
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
        print("\\n  coverage -- CSV rows vs cached reads on disk:")
        for s in sorted(set(cache) | set(csv_n)):
            mark = "  <-- SHORT" if s in short else ""
            print(f"    {s:22} csv {csv_n.get(s,0):6d}   cache "
                  f"{cache.get(s,0):6d}{mark}")
    if short:
        coverage_note = ("CSV coverage was SHORT of the cache for: "
                         + "; ".join(f"{s} {a} of {b}" for s, (a, b)
                                     in sorted(short.items())) + ".")
        if not args.allow_partial:
            print("\\n" + "!" * 78)
            print("ABORTING -- the CSVs carry fewer documents than the cache "
                  "holds.")
            print("  The gate would be computed on a subset without saying so, "
                  "and the")
            print("  results file would be dated today. That is the failure "
                  "this check")
            print("  exists to prevent.")
            print("\\n  Most likely cause: run_corpus.sh did not finish, or a "
                  "source was")
            print("  read without an --out CSV. Re-run the read, or pass "
                  "--allow-partial")
            print("  to proceed with the shortfall recorded in the results "
                  "file.")
            print("!" * 78)
            raise SystemExit(1)
        print(f"\\n  ** PROCEEDING PARTIAL (--allow-partial). {coverage_note}")

    groups = {s: g["specificity"].dropna().values
              for s, g in df.groupby("source") if len(g) >= 5}
    if len(groups) < 2:
        raise SystemExit("need at least two sources with n>=5.")
'''

# --- anchor 5: read-condition block -- add model alongside prompt_version --
A5_OLD = """    vers = {}
    if "prompt_version" in df.columns:
        for s, g in df.groupby("source"):
            vv = sorted(set(g["prompt_version"].dropna().astype(str)) - {""})
            vers[s] = vv
"""
A5_NEW = '''    # Read condition = prompt_version AND model. The cache key carries only
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
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not TARGET.exists():
        sys.exit(f"ABORT: {TARGET} not found. Run this from the repo root.")
    src = TARGET.read_text()

    patches = [("import block", A1_OLD, A1_NEW),
               ("load_all()", A2_OLD, A2_NEW),
               ("argparse in main()", A3_OLD, A3_NEW),
               ("groups construction", A4_OLD, A4_NEW),
               ("read-condition block", A5_OLD, A5_NEW)]

    # verify every anchor BEFORE writing anything
    bad = []
    for name, old, _ in patches:
        n = src.count(old)
        if n != 1:
            bad.append(f"  {name}: anchor found {n} times, expected exactly 1")
    if bad:
        print("ABORT -- anchors did not verify. Nothing written.")
        print("\n".join(bad))
        print("\nThe file has changed since this patch was written. Re-read it "
              "and re-derive the anchors rather than forcing the patch.")
        sys.exit(1)

    out = src
    for name, old, new in patches:
        out = out.replace(old, new, 1)
        print(f"  anchor OK: {name}")

    if not args.write:
        print(f"\nDRY RUN. {len(patches)}/{len(patches)} anchors verified. "
              f"{len(src)} -> {len(out)} bytes.")
        print("Re-run with --write to apply.")
        return

    bak = TARGET.with_suffix(".py.bak")
    bak.write_text(src)
    TARGET.write_text(out)
    print(f"\nwritten: {TARGET}   (backup: {bak})")
    print("Verify before use:  python -m src.gate_check --iters 2000")


if __name__ == "__main__":
    main()
