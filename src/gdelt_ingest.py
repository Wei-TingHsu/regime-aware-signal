"""
src/gdelt_ingest.py -- turn a GDELT BigQuery console export (.xlsx) into a clean
daily counts CSV.

Closes a reproducibility gap: until 2026-08-20 nothing in the repo produced
`processed/gdelt_2024_clean.csv`. It came from a manual BigQuery console run
exported to .xlsx, then cleaned by hand. The query text survived only inside the
xlsx metadata row; it is now recovered and parameterised in `src/gdelt_query.py`.

The console export has a metadata row above the header (it carries the "Custom
query: ..." string and the export timestamp), so the real header is row 2.

Run:
    python -m src.gdelt_ingest --xlsx "raw/UNNEST EPU_ECO one-year.xlsx" \
                               --out processed/gdelt_2024_clean.csv
Optional:
    --expect-rows 366     fail loud if the row count differs
"""
import argparse

import pandas as pd

from src.data_io import PROCESSED_DIR

COLS = ["day", "monetary_count", "stress_count", "total_docs"]
REPO = PROCESSED_DIR.parent


def read_export(path):
    """Read a BigQuery console .xlsx export; row 1 is metadata, row 2 the header."""
    df = pd.read_excel(path, skiprows=1).dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"{path}: missing expected columns {missing}; got {list(df.columns)}")
    out = df[COLS].copy()
    for c in COLS:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["day"]).astype({c: "int64" for c in COLS})
    return out.sort_values("day").reset_index(drop=True)


def query_text(path):
    """Recover the embedded 'Custom query: ...' string from the metadata row."""
    head = pd.read_excel(path, nrows=1, header=None)
    for v in head.iloc[0].tolist():
        s = str(v)
        if "SELECT" in s.upper():
            return s
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="path to the BigQuery console export")
    ap.add_argument("--out", required=True, help="output CSV path (repo-relative)")
    ap.add_argument("--expect-rows", type=int, default=None)
    ap.add_argument("--show-query", action="store_true",
                    help="print the query recovered from the export metadata")
    args = ap.parse_args()

    src = REPO / args.xlsx if not str(args.xlsx).startswith("/") else args.xlsx
    df = read_export(src)

    if args.show_query:
        q = query_text(src)
        print("-" * 70)
        print(q.replace("\\n", "\n") if q else "(no query string found in metadata row)")
        print("-" * 70)

    dup = int(df["day"].duplicated().sum())
    if dup:
        raise SystemExit(f"{dup} duplicate day values -- refusing to write.")
    if args.expect_rows is not None and len(df) != args.expect_rows:
        raise SystemExit(f"expected {args.expect_rows} rows, got {len(df)} -- refusing to write.")

    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    print(f"rows {len(df)}  |  {df['day'].min()} -> {df['day'].max()}")
    print(f"stress_count  mean {df['stress_count'].mean():,.0f}  "
          f"min {df['stress_count'].min():,}  max {df['stress_count'].max():,}")
    print(f"total_docs    mean {df['total_docs'].mean():,.0f}")
    print(f"written -> {out}")


if __name__ == "__main__":
    main()
