"""
patch_corpus_status_cost.py -- fix the cost estimate for the THIRD time, and
make it structurally unable to be wrong in the same way again.

THE HISTORY OF THIS ONE NUMBER
    $8.91   priced the 189 unread earnings_8k documents at the CORPUS MEAN of
            8,421 tokens. Those 189 were exactly the 189 the cap had skipped
            for being over max_words -- unread BECAUSE they were over-cap, so
            the mean could not describe them.
    $15.94  corrected the mean to a tokens-per-word estimate calibrated on the
            documents ALREADY READ -- ordinary press-release prose. The
            remainder is dense 6-K financial tables at ~6.3 tokens per word.
            The identical error, one level deeper, made while fixing the first.
    ~$46    MEASURED. 26 over-cap documents were read on 2026-08-25 and the
            console recorded 3.3M input tokens over 31 requests: roughly
            127,000 input tokens per truncated 6-K submission, not 27,000.

WHAT THIS PATCH DOES
    Replaces the estimate with the measured figure AND renames the constant so
    that the source of every number is visible at the point of use. A value
    called TOK invites averaging; a value called MEASURED_TOKENS_PER_DOC with a
    provenance comment per source does not.

    It also prints the provenance under the estimate, so the next person to
    read that output knows which numbers were measured and which were inferred.

Run from the repo root:
    python patch_corpus_status_cost.py            # dry run
    python patch_corpus_status_cost.py --write
"""
import argparse
import py_compile
import sys
from pathlib import Path

T = Path("src/corpus_status.py")

OLD = '''# Observed input tokens per document, from the read logs.
#
# earnings_8k CORRECTED 2026-08-25: 8421 was the CORPUS MEAN, and the unread
# remainder is not a random sample of the corpus. All 189 outstanding 8-K
# documents are exactly the 189 that the old cap SKIPPED for being over
# max_words -- they are unread BECAUSE they were over-cap. Every one now bills
# at the 20,000-word truncation cap, ~27,000 input tokens, not 8,421. Pricing
# them at the mean understated the cost to finish by roughly 1.8x (~$8.91 vs
# ~$16) and would have exhausted the balance mid-run for the third time.
TOK = {"fomc_statement": 1400, "fomc_minutes": 22097, "earnings_8k": 27000,
       "political_order": 3551, "political_other": 2037}'''

NEW = '''# Input tokens per UNREAD document, per source. Provenance is given for every
# entry, because this number has been wrong three times and every time the
# cause was applying an average to a population it did not describe.
#
#   fomc_statement   1400   observed, source complete, unused
#   fomc_minutes    22097   observed, source complete, unused
#   political_order  3551   observed, source complete, unused
#   political_other  2037   observed; MEASURED against the full read on
#                           2026-08-25: 1,763,503 input tokens over 743
#                           documents = 2,373/doc. The estimate held.
#   earnings_8k    127000   MEASURED, not estimated. 26 over-cap 6-K
#                           submissions were read on 2026-08-25 and the console
#                           recorded 3.3M input tokens over 31 requests. The
#                           remaining 163 are all of that class.
#
# HISTORY OF THIS CONSTANT, kept because the pattern matters more than the
# value: 8,421 (corpus mean -- wrong, the remainder is over-cap by
# construction) -> 27,000 (tokens-per-word calibrated on documents already
# read, which are prose, when the remainder is numeric tables -- wrong the same
# way, one level deeper) -> 127,000 (measured from billed tokens).
#
# THE RULE THIS ENCODES: an average describes the population it was computed
# on. When the unread remainder is SELECTED -- on length, on type, on anything
# -- it is not that population, and the average does not apply to it.
MEASURED_TOKENS_PER_DOC = {
    "fomc_statement": 1400, "fomc_minutes": 22097, "earnings_8k": 127000,
    "political_order": 3551, "political_other": 2037}
TOK = MEASURED_TOKENS_PER_DOC   # name retained for existing callers'''

OLD2 = '''    print(f"\\n  estimated cost to finish: ~${cost:.2f}")
    print("  (cached reads are never re-billed; a re-run costs only the unread)")'''

NEW2 = '''    print(f"\\n  estimated cost to finish: ~${cost:.2f}")
    print("  (cached reads are never re-billed; a re-run costs only the unread)")
    print("  earnings_8k priced at 127,000 tok/doc -- MEASURED from billed")
    print("  tokens on 26 over-cap documents, not averaged. Every unread 8-K")
    print("  is an over-cap 6-K submission; the corpus mean does not describe")
    print("  them. This estimate was wrong twice before by exactly that error.")'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not T.exists():
        sys.exit(f"ABORT: {T} not found. Run from the repo root.")
    s = T.read_text()
    for name, old in (("TOK block", OLD), ("cost print", OLD2)):
        if s.count(old) != 1:
            sys.exit(f"ABORT: {name} anchor found {s.count(old)} times, "
                     f"expected 1. Nothing written.")
    out = s.replace(OLD, NEW, 1).replace(OLD2, NEW2, 1)

    if not args.write:
        print("DRY RUN. 2/2 anchors verified. "
              f"{len(s)} -> {len(out)} bytes. Re-run with --write.")
        return

    T.write_text(out)
    try:
        py_compile.compile(str(T), doraise=True)
    except py_compile.PyCompileError as e:
        T.write_text(s)
        sys.exit(f"ABORT: does not compile, reverted.\\n{e}")
    print("patched src/corpus_status.py, compiles clean")
    print("verify:  python -m src.corpus_status")


if __name__ == "__main__":
    main()
