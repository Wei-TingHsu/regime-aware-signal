"""register_tk3_and_political.py -- 28 Oct 2026: the record edits that go with the new files, applied once, with anchors.

New files this session (already in place, written as new files, nothing existing overwritten):
    src/chair_style.py              T-K3: rubric read, exact permutation, acceptance check, record
    src/political_route.py          the Federal Register backlog -> the two folders the report reads; measured cost
    src/source_compare.py           session coverage; the section-8 comparison against the baseline backfill
    docs/prereg_political_backfill.md   registration of TRACK 3.1 with criteria C1-C3 and prior #83
    overnight.sh                    the runner:  caffeinate -is ./overnight.sh
    scripts_applied/patch_edgar_cik_fallback.py   optional: the nightly 8-K fetch (sec.gov 403 since 19 Oct)

This script: (1) py_compile the new modules; (2) append two amendment rows to docs/prereg_liquidity_and_chair.md section 4
(the 16 Sep correction; T-K3's implementation and the acceptance check with prior #82) BEFORE any rubric read runs;
(3) append the status paragraph to docs/TRACK.md section 3.35. Anchors verified; nothing rewritten.
    python scripts_applied/register_tk3_and_political.py
"""
import py_compile
import sys
from pathlib import Path

NEW_FILES = ["src/chair_style.py", "src/political_route.py", "src/source_compare.py",
             "docs/prereg_political_backfill.md", "overnight.sh", "scripts_applied/patch_edgar_cik_fallback.py"]

ROW_A = ("| 2026-10-28 | **Correction to section 3 'Units':** the 16 Sep 2026 statement IS on disk "
         "(`data_provenance/docs/fomc_statement/20260916.txt`, 131 words in the 2026 format) and IS read under v1 (132 texts, 132 reads); "
         "CURRENT_STATE 18.8 recorded that re-read on 24 Sep. The 27 Oct sentence 'not yet fetched — a feed gap to close' and TRACK 3.35's "
         "'not in the corpus' were wrong: written from the T-K0 sample count, not from a listing. Wrong-prior candidate, founder to decide "
         "(#10's rule: a negative claim about the repo needs a grep). T-K3 therefore runs on all three Warsh statements today and on four after 28 Oct. "
         "| found by `ls` on 28 Oct, before any T-K3 read |")

ROW_B = ("| 2026-10-28 | **T-K3 implemented** in `src/chair_style.py`, before any read: every statement on disk read on the registered rubric "
         "(hawkish–dovish, guidance strength, balance-sheet language, inflation-vs-labour emphasis, hedging density, dissents, novelty vs the "
         "previous statement; length change computed from the texts), with its own cache folder `data_provenance/doc_reads_style/` and prompt "
         "version `style-v1-2026-10-28` — never pooled with v1; features z-scored on all statements; energy distance; exact permutation over "
         "all C(n+8, n) arrangements; per-dimension distances reported descriptively (eight dimensions, no single one is a finding). "
         "**Acceptance check, registered before the first run:** the same test on Yellen's last 8 vs Powell's first 8 and Bernanke's last 8 vs "
         "Yellen's first 8 (C(16,8) = 12,870 arrangements each). If neither transition separates at p < 0.05 the rubric has no discriminating "
         "power and a Warsh null is UNINFORMATIVE, not FAIL. It shows the rubric can see a change at a transition, not that the change was the "
         "person — T-K1's era confound applies. Synthetic selftest (planted 3.5-sd shift on one of eight dimensions at n = 4 vs 8 detected in ≥ 90%; "
         "no shift rejected in 2–8%) must PASS before the read. Reading order: n = 3 today (reported, not judged), n = 4 after the 28 Oct statement "
         "(prior #79 judged there, as written). Cost measured on disk before the read (`chair_style cost`). "
         "**Prior #82 (Claude):** Yellen→Powell separates at p < 0.05, on hedging density and balance-sheet language; Bernanke→Yellen does not (p > 0.05). "
         "| the next script after T-K0–K2; the instrument-first rule (every null from an instrument shown to catch a known effect) |")

TRACK_PARA = ("\n28 Oct 00:45: T-K3 built as `src/chair_style.py` (synthetic selftest PASS: a planted 3.5-sd shift at n = 4 vs 8 detected 98%, "
              "no-shift rejection 4%); the acceptance check on Bernanke→Yellen and Yellen→Powell is registered before any read (prior #82). "
              "The 16 Sep statement is on disk and read (132/132) — the 'feed gap' line above is wrong (amendment row in the prereg). "
              "TRACK 3.1 registered as `docs/prereg_political_backfill.md` (C1 coverage ≥ 50%, C2 gate, C3 section-8 rule; prior #83) with "
              "`src/political_route.py`, `src/source_compare.py` and `overnight.sh` (cost measured on disk, cap US$40, lock and fatal-abort via "
              "run_corpus.sh). Found in the nightly logs: the automated 8-K fetch has failed on a sec.gov 403 every night since 19 Oct while manual "
              "runs succeed — `scripts_applied/patch_edgar_cik_fallback.py` caches the CIK map and prints the UA; cause open. Thu 29 Oct 01:45 SGT: "
              "the 2 pm reader's first live FOMC (the launcher has fired on every scheduled night this month); then T-K3 at n = 4 and T-K2σ refreshed.\n")


def main():
    missing = [f for f in NEW_FILES if not Path(f).exists()]
    if missing:
        sys.exit("missing new file(s): " + ", ".join(missing))
    for f in NEW_FILES:
        if f.endswith(".py"):
            py_compile.compile(f, doraise=True)
    print("  all new modules parse")
    p = Path("docs/prereg_liquidity_and_chair.md"); s = p.read_text()
    if "**T-K3 implemented** in `src/chair_style.py`" in s:
        print("  prereg: amendment rows already present -- skipped")
    else:
        anchor = "\n\n## 5. Results"
        if s.count(anchor) != 1:
            sys.exit("prereg anchor '## 5. Results' not unique -- nothing changed")
        s = s.replace(anchor, "\n" + ROW_A + "\n" + ROW_B + anchor, 1)
        p.write_text(s); print("  prereg: two amendment rows added (16 Sep correction; T-K3 + acceptance check, prior #82)")
    t = Path("docs/TRACK.md"); s = t.read_text()
    if "28 Oct 00:45: T-K3 built" in s:
        print("  TRACK: status paragraph already present -- skipped")
    else:
        if "### 3.35" not in s:
            sys.exit("TRACK anchor '### 3.35' missing -- nothing changed")
        t.write_text(s.rstrip("\n") + "\n" + TRACK_PARA); print("  TRACK: 3.35 status paragraph appended")
    print("done -- review `git diff`, then:  caffeinate -is ./overnight.sh")


if __name__ == "__main__":
    main()
