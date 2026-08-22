"""
make_gdelt_csv.py -- turn BigQuery console .xlsx exports into one clean daily CSV.

The console export puts the ENTIRE SQL query in the first row and the real
header ('day', 'monetary_count', 'stress_count', 'total_docs') in the second.
Reading it naively gives a one-column frame whose name is the query text.

    python -m src.make_gdelt_csv ~/Downloads/narrow_*.xlsx
    python -m src.make_gdelt_csv --out processed/gdelt_narrow_daily.csv <files>

Checks that matter (each has already bitten this project once):
  * 500-row console export cap -- warns on any file at exactly 500 rows.
  * Duplicate days across overlapping exports -- reported, then de-duplicated.
  * Calendar gaps -- reported explicitly, including the known 2025-06-15..07-01
    GDELT outage, so a gap is never silently interpolated.
  * total_docs level shifts -- flags year-boundary jumps, because a structural
    break in the DENOMINATOR would contaminate every share/z-score computed
    across the join.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


def read_export(path):
    df = pd.read_excel(path, skiprows=1)
    df.columns = [str(c).strip().lower() for c in df.columns]
    need = {"day", "stress_count", "total_docs"}
    if not need <= set(df.columns):
        raise SystemExit(f"{path.name}: expected {sorted(need)}, got {list(df.columns)}")
    df = df[df["day"].notna()].copy()
    df["date"] = pd.to_datetime(df["day"].astype(int).astype(str), format="%Y%m%d")
    keep = ["date", "stress_count", "total_docs"]
    if "monetary_count" in df.columns:
        keep.insert(2, "monetary_count")
    out = df[keep].copy()
    if len(df) == 500:
        print(f"  !! {path.name}: EXACTLY 500 rows -- the BigQuery console export "
              f"cap. Data is probably truncated. Re-export via 'Save to Drive'.")
    print(f"  {path.name}: {len(out)} rows, "
          f"{out['date'].min().date()} -> {out['date'].max().date()}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="processed/gdelt_narrow_daily.csv")
    args = ap.parse_args()

    frames = [read_export(Path(f)) for f in args.files]
    df = pd.concat(frames, ignore_index=True).sort_values("date")

    dup = df["date"].duplicated().sum()
    if dup:
        print(f"  {dup} duplicate day(s) across exports -- keeping the first of each.")
        df = df.drop_duplicates("date", keep="first")

    full = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    missing = full.difference(pd.DatetimeIndex(df["date"]))
    if len(missing):
        runs, start, prev = [], missing[0], missing[0]
        for d in missing[1:]:
            if (d - prev).days > 1:
                runs.append((start, prev))
                start = d
            prev = d
        runs.append((start, prev))
        print(f"  {len(missing)} missing calendar day(s) in "
              f"{len(runs)} run(s) -- NOT interpolated:")
        for a, b in runs:
            n = (b - a).days + 1
            tag = "  <- known GDELT outage" if n > 5 else ""
            print(f"      {a.date()} .. {b.date()}  ({n}d){tag}")

    yr = df.groupby(df["date"].dt.year)["total_docs"].median()
    print("  median total_docs by year (denominator continuity check):")
    prev_v = None
    for y, v in yr.items():
        flag = ""
        if prev_v is not None and abs(v - prev_v) / prev_v > 0.25:
            flag = f"  <- {100*(v-prev_v)/prev_v:+.0f}% vs prior year: A LEVEL SHIFT " \
                   f"IN THE DENOMINATOR CONTAMINATES SHARES ACROSS THE JOIN"
        print(f"      {y}: {v:,.0f}{flag}")
        prev_v = v

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\n  {len(df)} rows -> {out}")
    print(f"  coverage: {df['date'].min().date()} -> {df['date'].max().date()}")


if __name__ == "__main__":
    main()
