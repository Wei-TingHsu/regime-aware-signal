#!/usr/bin/env python3
"""
patch_atomic_cache.py -- a concurrent write corrupted the read cache.

WHAT HAPPENED
    run_corpus.sh was launched TWICE by accident. Both processes reached the
    same document and both wrote

        data_provenance/doc_reads/<source>__<stem>__<version>.json

    with a plain write_text(). The result is two JSON objects concatenated in
    one file, and every later run dies on it:

        JSONDecodeError: Extra data: line 29 column 2 (char 768)

    The crash is on a CACHE READ, not an API call -- so the run aborts before
    doing any work, and the corrupt file blocks that source permanently.

THREE FIXES

  1. ATOMIC WRITE. Write to <name>.<pid>.tmp, then os.replace(). replace() is
     atomic on POSIX, so a concurrent writer can only ever produce a whole file
     from one process or a whole file from the other -- never a splice of both.

  2. SELF-HEALING READ. A cache file that will not parse is DELETED and the
     document re-read, with a warning naming the file. A corrupt cache entry
     should cost one API call, not block a source forever.

  3. --repair-cache. Scans every cache file, reports and deletes the unparseable
     ones. Run once to clear the existing damage.

WHY NOT JUST DELETE THE BAD FILES
    That fixes today and leaves the mechanism. Anything that runs two readers at
    once -- a stray second launch, a cron overlapping a manual run -- reproduces
    it. Ninth silent-continuation defect of this session, and the first caused by
    concurrency rather than by an unchecked branch.

Run from the repo root:
    python patch_atomic_cache.py --dry-run
    python patch_atomic_cache.py
    python -m src.doc_read --repair-cache
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/doc_read.py",
    """            out_f = READS / f"{src}__{f.stem}__{PROMPT_VERSION}.json"
            if out_f.exists():
                rows.append(json.loads(out_f.read_text()))
                continue""",
    """            out_f = READS / f"{src}__{f.stem}__{PROMPT_VERSION}.json"
            if out_f.exists():
                # SELF-HEALING. A cache file that will not parse is deleted and
                # the document re-read. A concurrent double-launch on
                # 2026-08-25 spliced two JSON objects into one file, and the
                # unguarded json.loads() below aborted the whole run on a CACHE
                # READ -- before any API call -- blocking that source until the
                # file was found by hand. A corrupt entry should cost one call,
                # not a source.
                try:
                    rows.append(json.loads(out_f.read_text()))
                    continue
                except (json.JSONDecodeError, OSError) as ce:
                    print(f"    {f.stem}  CORRUPT CACHE ({type(ce).__name__}), "
                          f"deleting and re-reading: {out_f.name}")
                    try:
                        out_f.unlink()
                    except OSError:
                        pass""",
    "doc_read -- self-healing cache read",
), (
    "src/doc_read.py",
    """            out_f.write_text(json.dumps(data, indent=2))""",
    """            # ATOMIC WRITE. os.replace() is atomic on POSIX, so two writers
            # can only produce a whole file from one or a whole file from the
            # other -- never a splice. A plain write_text() here is what let a
            # double-launched run corrupt the cache on 2026-08-25.
            tmp_f = out_f.with_suffix(f".{os.getpid()}.tmp")
            tmp_f.write_text(json.dumps(data, indent=2))
            os.replace(tmp_f, out_f)""",
    "doc_read -- atomic cache write",
), (
    "src/doc_read.py",
    """    ap.add_argument("--list", action="store_true")""",
    """    ap.add_argument("--list", action="store_true")
    ap.add_argument("--repair-cache", action="store_true",
                    help="scan every cached read, report and DELETE any that "
                         "will not parse, then exit. Deleted entries are simply "
                         "re-read on the next run at the cost of one API call "
                         "each.")""",
    "doc_read -- add --repair-cache",
), (
    "src/doc_read.py",
    """    DOCS.mkdir(parents=True, exist_ok=True)""",
    """    if args.repair_cache:
        files = sorted(READS.glob("*.json")) if READS.exists() else []
        bad = []
        for p in files:
            try:
                json.loads(p.read_text())
            except Exception as e:
                bad.append((p, type(e).__name__))
        print(f"cache scan: {len(files)} entries, {len(bad)} unparseable")
        for p, e in bad:
            print(f"  DELETE {p.name}  ({e})")
            try:
                p.unlink()
            except OSError as e2:
                print(f"    could not delete: {e2}")
        # stray temp files from an interrupted atomic write
        tmps = sorted(READS.glob("*.tmp")) if READS.exists() else []
        for p in tmps:
            print(f"  DELETE {p.name}  (stray temp)")
            try:
                p.unlink()
            except OSError:
                pass
        print(f"\\n{len(bad)} deleted, {len(tmps)} temp file(s) removed. "
              f"They will be re-read at one API call each.")
        return

    DOCS.mkdir(parents=True, exist_ok=True)""",
    "doc_read -- implement --repair-cache",
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

    src = (ROOT / "src" / "doc_read.py")
    if src.exists() and "\nimport os\n" not in src.read_text():
        failures.append("doc_read.py does not import os -- needed by the "
                        "atomic write")
        print("  FAIL  src/doc_read.py: `import os` not found")

    if failures:
        print("\n" + "=" * 74)
        print(f"ABORTED -- {len(failures)} failure(s). NO FILE WAS MODIFIED.")
        print("=" * 74)
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"\nall {len(EDITS)} anchors verified, unique. `import os` present.")
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
    print("""NEXT:

  python -m src.doc_read --repair-cache      # clears the existing damage

  caffeinate -i nohup ./run_corpus.sh > corpus4.log 2>&1 &     # ONE launch
  sleep 90 && grep "read .* docs" corpus4.log

  A non-zero token count on the first source means it is running. Nothing
  already read is billed again.

SEPARATE ISSUE, NOT FIXED HERE -- worth a decision:

  earnings_8k: 189 doc(s) over 20000 words, skipped

  189 of 834 earnings documents exceed the word cap. Those are almost certainly
  6-K complete submissions, where the whole filing is one file with no separate
  exhibits. Raising the cap costs tokens on documents that are mostly boilerplate;
  leaving it drops 23% of the earnings corpus. Decide before the read finishes,
  because either way it is a coverage statement the report has to make.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
