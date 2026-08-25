#!/usr/bin/env python3
"""
patch_fatal_and_path.py -- two fixes.

1. MY BUG: `Path` is used in analog_backtest.main by the --dump-spreads block
   but was never imported into that module. NameError on every dump.

2. doc_read RETRIED A CREDIT ERROR 897 TIMES.
   The 2026-08-25 overnight run exhausted the API balance partway through
   political_order and then failed every remaining document -- 141 orders and
   756 proclamations -- retrying each one first. Four hours, 897 identical
   400s, and a log that had to be grepped to discover it.

   "Your credit balance is too low" is NOT transient. Neither is an invalid
   API key, nor a permission error. Retrying them is pointless and continuing
   past them produces a run that LOOKS like it completed.

   Same class as everything else caught this session: a failure that logged
   plausibly and kept going instead of stopping loudly. doc_read now ABORTS on
   the first such error, printing how many documents remain unread.

   Transient errors -- overload, rate limits, timeouts, malformed replies --
   keep the existing one-retry-then-continue behaviour. Those genuinely are
   worth retrying.

Run from the repo root:
    python patch_fatal_and_path.py --dry-run
    python patch_fatal_and_path.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/analog_backtest.py",
    """import argparse

import numpy as np
import pandas as pd""",
    """import argparse
from pathlib import Path          # used by the --dump-spreads block in main()

import numpy as np
import pandas as pd""",
    "analog_backtest -- import Path (NameError on every --dump-spreads run)",
), (
    "src/doc_read.py",
    '''def parse_name(p):''',
    '''# Errors that will NEVER succeed on retry. Retrying these burned 897 pointless
# calls on 2026-08-25 after the API balance ran out mid-run, and produced a log
# that looked like a completed pass.
FATAL_MARKERS = (
    "credit balance is too low",
    "invalid x-api-key",
    "authentication_error",
    "permission_error",
    "insufficient_quota",
)


def is_fatal(exc):
    """Is this error permanent for the whole run, not just this document?

    Deliberately matches on the MESSAGE rather than the exception class: the
    SDK raises BadRequestError for both a malformed request (per-document, worth
    retrying) and an exhausted balance (fatal). The class cannot tell them
    apart; the message can."""
    s = f"{type(exc).__name__}: {exc}".lower()
    return any(m in s for m in FATAL_MARKERS)


def parse_name(p):''',
    "doc_read -- add is_fatal",
), (
    "src/doc_read.py",
    '''            except Exception as e:
                # ONE retry with a stricter instruction before giving up. A
                # transient formatting slip should not cost a document.
                try:''',
    '''            except Exception as e:
                if is_fatal(e):
                    remaining = len(use) - k
                    print("\\n" + "!" * 70)
                    print("FATAL -- ABORTING THE WHOLE RUN, NOT JUST THIS DOC")
                    print(f"  {type(e).__name__}: {e}")
                    print(f"\\n  {src}: {k} read this session, "
                          f"{remaining} NOT READ.")
                    print("  This error is permanent for the run. Retrying it "
                          "is pointless and")
                    print("  continuing past it produces a log that looks like "
                          "a completed pass --")
                    print("  which is exactly what happened on 2026-08-25: 897 "
                          "documents failed")
                    print("  this way over four hours.")
                    print("\\n  Everything read so far IS CACHED. Fix the cause, "
                          "re-run the same")
                    print("  command, and only the unread documents are billed.")
                    print("!" * 70)
                    raise SystemExit(1)
                # ONE retry with a stricter instruction before giving up. A
                # transient formatting slip should not cost a document.
                try:''',
    "doc_read -- abort the run on a fatal error instead of retrying it",
), (
    "src/doc_read.py",
    '''                except Exception as e2:
                    print(f"    {f.stem}  FAILED: {type(e2).__name__}: {e2}")''',
    '''                except Exception as e2:
                    if is_fatal(e2):
                        print("\\n" + "!" * 70)
                        print("FATAL ON RETRY -- ABORTING THE WHOLE RUN")
                        print(f"  {type(e2).__name__}: {e2}")
                        print(f"  {src}: {k} read this session, "
                              f"{len(use) - k} NOT READ. Cached reads are kept.")
                        print("!" * 70)
                        raise SystemExit(1)
                    print(f"    {f.stem}  FAILED: {type(e2).__name__}: {e2}")''',
    "doc_read -- also abort if the retry hits a fatal error",
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
    print("""VERIFY:

  python -c "
import sys; sys.path.insert(0,'.')
from src.doc_read import is_fatal
class E(Exception): pass
fatal = E(\\"Error code: 400 - {'type':'invalid_request_error','message':'Your credit balance is too low to access the Anthropic API.'}\\")
trans = E(\\"Error code: 529 - {'type':'overloaded_error'}\\")
json_ = E('JSONDecodeError: Expecting value: line 1 column 1')
print('credit exhausted -> fatal:', is_fatal(fatal), '(expect True)')
print('overloaded       -> fatal:', is_fatal(trans), '(expect False)')
print('bad JSON         -> fatal:', is_fatal(json_), '(expect False)')
"

  python -m src.engine_b_paired        # Path is now imported; ~10 min
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
