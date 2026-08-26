"""
rebuild_csv.py -- regenerate a source's read CSV from the CACHED reads.

WHY THIS EXISTS
    doc_read.py writes its CSV once, at the END of a run. Its fatal-error path
    raises SystemExit(1) from inside the document loop, so an aborted run leaves
    every document it read safely CACHED but writes NO CSV. The cache and the
    CSV then disagree, and gate_check's coverage check -- correctly -- refuses
    to run.

    That happened on 2026-08-25: earnings_8k reached 671 cached reads while
    read_8k.csv still carried 645 from an earlier complete run.

    Re-running doc_read to regenerate the CSV would bill the 163 documents that
    are still unread. This rebuilds it from disk instead, at no cost. The cache
    holds everything the CSV needs -- the CSV is a projection of it, never the
    other way round.

Run from the repo root:
    python rebuild_csv.py earnings_8k processed/read_8k.csv
    python rebuild_csv.py --all
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

READS = Path("data_provenance/doc_reads")
PROMPT_VERSION = "v1-2026-08-23"

# source -> the CSV path run_corpus.sh writes for it
DEFAULT_OUT = {
    "fomc_statement":  "processed/read_statement.csv",
    "fomc_minutes":    "processed/read_minutes.csv",
    "earnings_8k":     "processed/read_8k.csv",
    "political_order": "processed/read_political_order.csv",
    "political_other": "processed/read_political_other.csv",
}


def flatten(r):
    """Identical column set to doc_read.py's own flattening, including the
    dir_* prefixes (a column named `eq` collides with DataFrame.eq)."""
    d = r.get("direction", {}) or {}
    return dict(date=r.get("date"), source=r.get("source"),
                doc_id=r.get("doc_id", ""),
                prompt_version=r.get("prompt_version", ""),
                model=r.get("model", ""),
                truncated=r.get("truncated", False),
                orig_words=r.get("orig_words", None),
                dir_eq=d.get("equity"), dir_dur=d.get("duration"),
                dir_gold=d.get("gold"), dir_usd=d.get("dollar"),
                dir_oil=d.get("oil"),
                magnitude=r.get("magnitude"),
                horizon_days=r.get("horizon_days"),
                specificity=r.get("specificity"),
                novelty=r.get("novelty"),
                confidence=r.get("confidence"))


def rebuild(src, out):
    files = sorted(READS.glob(f"{src}__*.json"))
    rows, bad = [], 0
    for p in files:
        try:
            rows.append(flatten(json.loads(p.read_text())))
        except Exception:
            bad += 1
    if not rows:
        print(f"  {src:18} no cached reads found -- SKIPPED")
        return 0
    df = pd.DataFrame(rows).sort_values(["date", "source"])
    outp = Path(out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outp, index=False)
    note = f"  ({bad} unparseable, skipped)" if bad else ""
    ntr = int(df["truncated"].fillna(False).astype(bool).sum())
    print(f"  {src:18} {len(df):6d} rows -> {out}   "
          f"({ntr} truncated){note}")
    return len(df)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", choices=sorted(DEFAULT_OUT))
    ap.add_argument("out", nargs="?")
    ap.add_argument("--all", action="store_true",
                    help="rebuild every source that has cached reads")
    args = ap.parse_args()

    if not READS.exists():
        sys.exit(f"ABORT: {READS} not found. Run from the repo root.")

    print("rebuilding read CSVs from cached JSON (no API calls):")
    if args.all:
        total = sum(rebuild(s, o) for s, o in sorted(DEFAULT_OUT.items()))
        print(f"\n  {total} rows total")
    elif args.source:
        rebuild(args.source, args.out or DEFAULT_OUT[args.source])
    else:
        sys.exit("give a source, or --all")
    print("\nverify with:  python -m src.gate_check --iters 2000")


if __name__ == "__main__":
    main()
