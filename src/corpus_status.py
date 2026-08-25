"""
corpus_status.py -- print the corpus read state from DISK, and optionally write
it into CURRENT_STATE as a dated section.

WHY THIS EXISTS
    CURRENT_STATE section 15.8 carries a hand-written table that went stale three
    runs ago -- it still cites corpus2.log and pre-truncation counts. A briefing
    with wrong counts is worse than one with none, because the next session
    starts from a false picture and only discovers it by re-checking.

    The counts here come from the filesystem, not from a log and not from
    memory: read = cached JSON files, docs = text files in the drop folder. A
    log can be truncated by a double launch; the cache cannot lie.

Run:
    python -m src.corpus_status                 # print only
    python -m src.corpus_status --append        # append a dated section to
                                                # docs/CURRENT_STATE_2026-08-23.md
"""
import argparse
from datetime import datetime
from pathlib import Path

from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
PROV = REPO / "data_provenance"
CS = REPO / "docs" / "CURRENT_STATE_2026-08-23.md"

SOURCES = ["fomc_statement", "fomc_minutes", "earnings_8k",
           "political_order", "political_other", "bank_research", "transcript"]

# Observed input tokens per document, from the read logs.
#
# earnings_8k CORRECTED 2026-08-25: 8421 was the CORPUS MEAN, and the unread
# remainder is not a random sample of the corpus. All 189 outstanding 8-K
# documents are exactly the 189 that the old cap SKIPPED for being over
# max_words -- they are unread BECAUSE they were over-cap. Every one now bills
# at the 20,000-word truncation cap, ~27,000 input tokens, not 8,421. Pricing
# them at the mean understated the cost to finish by roughly 1.8x (~$8.91 vs
# ~$16) and would have exhausted the balance mid-run for the third time.
TOK = {"fomc_statement": 1400, "fomc_minutes": 22097, "earnings_8k": 27000,
       "political_order": 3551, "political_other": 2037}
IN_RATE, OUT_RATE, OUT_TOK = 2.0, 10.0, 290      # $/M in, $/M out, tokens out


def counts():
    rows = []
    for s in SOURCES:
        d = len(list((PROV / "docs" / s).glob("*.txt"))) \
            if (PROV / "docs" / s).exists() else 0
        r = len(list((PROV / "doc_reads").glob(f"{s}__*.json"))) \
            if (PROV / "doc_reads").exists() else 0
        rows.append(dict(source=s, docs=d, read=r, unread=max(0, d - r)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--append", action="store_true")
    args = ap.parse_args()

    rows = counts()
    total_d = sum(r["docs"] for r in rows)
    total_r = sum(r["read"] for r in rows)
    total_u = sum(r["unread"] for r in rows)

    print("=" * 70)
    print("CORPUS STATE -- counted from disk, not from a log")
    print("=" * 70)
    print(f"  {'source':18} {'read':>6} {'docs':>6} {'unread':>7}  status")
    for r in rows:
        if r["docs"] == 0 and r["read"] == 0:
            status = "no documents (no free feed)"
        elif r["unread"] == 0:
            status = "COMPLETE"
        else:
            status = f"{100*r['read']/r['docs']:.0f}% read"
        print(f"  {r['source']:18} {r['read']:6d} {r['docs']:6d} "
              f"{r['unread']:7d}  {status}")
    print(f"  {'TOTAL':18} {total_r:6d} {total_d:6d} {total_u:7d}")

    cost = sum(r["unread"] * TOK.get(r["source"], 3000) for r in rows) / 1e6 * IN_RATE \
        + total_u * OUT_TOK / 1e6 * OUT_RATE
    print(f"\n  estimated cost to finish: ~${cost:.2f}")
    print("  (cached reads are never re-billed; a re-run costs only the unread)")
    print("=" * 70)

    if not args.append:
        print("\n  --append writes this into CURRENT_STATE as a dated section.")
        return

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["", "---", "",
             f"## CORPUS STATE — counted from disk {ts}",
             "",
             "*Supersedes the table in §15.8, which was written by hand and went "
             "stale. These counts come from the filesystem — cached JSON reads "
             "against text files in the drop folder — not from a log, because a "
             "log can be truncated by a double launch and the cache cannot lie.*",
             "",
             "| source | read | documents | unread | status |",
             "|---|---|---|---|---|"]
    for r in rows:
        if r["docs"] == 0 and r["read"] == 0:
            status = "no documents — no free structured feed"
        elif r["unread"] == 0:
            status = "**COMPLETE**"
        else:
            status = f"{100*r['read']/r['docs']:.0f}% read"
        lines.append(f"| `{r['source']}` | {r['read']} | {r['docs']} | "
                     f"{r['unread']} | {status} |")
    lines += [f"| **TOTAL** | **{total_r}** | **{total_d}** | **{total_u}** | |",
              "",
              f"Estimated cost to finish: **~${cost:.2f}**. Cached reads are "
              f"never re-billed — a re-run costs only the unread.", ""]
    if total_u:
        lines += ["**The read is INCOMPLETE.** It has been interrupted three "
                  "times: twice by API credit exhaustion (the second time it "
                  "aborted correctly on the first error instead of retrying) and "
                  "once by a cache file corrupted by an accidental double "
                  "launch, since fixed by atomic writes.", "",
                  "Finish with a **single** launch of `./run_corpus.sh`, then "
                  "re-run `python -m src.gate_check` — the gate was measured "
                  "before the corpus was complete and before over-cap documents "
                  "were truncated rather than skipped, so both the "
                  "`political_other` and `earnings_8k` arms will move.", ""]
    else:
        lines += ["**The read is COMPLETE.** Re-run `python -m src.gate_check` "
                  "on the full corpus — the gate was measured at n=60 per "
                  "source and before truncation, so both the `political_other` "
                  "and `earnings_8k` arms will move.", ""]

    with open(CS, "a") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n  appended to {CS}")
    print("  regenerate the briefing so it carries these counts:")
    print("    for f in docs/*.md; do echo \"===== $f =====\"; cat \"$f\"; echo; "
          "done > ~/Downloads/briefing.md")


if __name__ == "__main__":
    main()
