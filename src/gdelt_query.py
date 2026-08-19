"""
src/gdelt_query.py -- generate the GDELT GKG daily-counts BigQuery SQL from
`config/gdelt_theme_mapping.yaml`, so the theme lists have ONE source of truth.

Why this exists
---------------
The 2024 pull was a manual console run whose query text survived only inside the
.xlsx export metadata. Recovering it (2026-08-20) exposed a discrepancy:

  * `gdelt_theme_mapping.yaml` documents market_stress with EIGHT themes.
  * `processed/gdelt_2024_clean.csv` was built from a SIX-theme variant that
    omits EPU_ECONOMY_HISTORIC and EPU_ECONOMY -- confirmed by an exact match
    against `raw/UNNEST EPU_ECO one-year.xlsx`.

The two differ by ~5.5x in stress_count. Every regime<->event alignment result
to date used the NARROW definition while the config described the BROAD one.
Intent is undocumented; the narrow export is timestamped later, which is
consistent with a deliberate refinement, but that is inference, not a record.

Both variants are therefore emitted explicitly:
  --variant broad   all themes in the config's market_stress block
  --variant narrow  minus EPU_ECONOMY_HISTORIC and EPU_ECONOMY (as actually used)

Print the SQL, paste into the BigQuery console (or pipe to the bq CLI), export,
then convert with `src.gdelt_ingest`.

Run:
    python -m src.gdelt_query --start 2025-01-01 --end 2026-08-19 --variant narrow
    python -m src.gdelt_query --start 2024-01-01 --end 2024-12-31 --variant broad
"""
import argparse

import yaml

from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
MAPPING = REPO / "config" / "gdelt_theme_mapping.yaml"

# Themes present in the config's market_stress block but ABSENT from the pull
# that produced gdelt_2024_clean.csv. Kept explicit so the deviation is visible.
NARROW_EXCLUDES = ["EPU_ECONOMY_HISTORIC", "EPU_ECONOMY"]

TEMPLATE = """SELECT
  SUBSTR(CAST(DATE AS STRING), 1, 8) AS day,
  COUNTIF(
    theme IN ({monetary})
  ) AS monetary_count,
  COUNTIF(
    theme IN ({stress})
  ) AS stress_count,
  COUNT(DISTINCT DocumentIdentifier) AS total_docs
FROM
  `gdelt-bq.gdeltv2.gkg_partitioned`,
  UNNEST(SPLIT(V2Themes, ';')) AS theme_with_offset,
  UNNEST([SPLIT(theme_with_offset, ',')[OFFSET(0)]]) AS theme
WHERE
  _PARTITIONTIME BETWEEN TIMESTAMP('{start}') AND TIMESTAMP('{end}')
  AND V2Themes IS NOT NULL
GROUP BY day
ORDER BY day;"""


def theme_list(cfg, factor):
    try:
        return list(cfg["factors"][factor]["themes"])
    except KeyError:
        raise SystemExit(f"factor '{factor}' not found in {MAPPING}")


def fmt(themes, indent=14):
    pad = " " * indent
    return ("\n" + pad).join(",".join(f"'{t}'" for t in themes[i:i + 3])
                             + ("," if i + 3 < len(themes) else "")
                             for i in range(0, len(themes), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="inclusive, YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="inclusive, YYYY-MM-DD")
    ap.add_argument("--variant", choices=["broad", "narrow"], default="narrow",
                    help="narrow = the definition actually used for the 2024 pull")
    args = ap.parse_args()

    cfg = yaml.safe_load(MAPPING.read_text())
    monetary = theme_list(cfg, "monetary_rates")
    stress = theme_list(cfg, "market_stress")
    if args.variant == "narrow":
        stress = [t for t in stress if t not in NARROW_EXCLUDES]

    print(f"-- GDELT GKG daily counts | variant={args.variant} "
          f"| {args.start} -> {args.end}")
    print(f"-- monetary themes: {len(monetary)}   stress themes: {len(stress)}")
    if args.variant == "narrow":
        print(f"-- narrow variant EXCLUDES: {', '.join(NARROW_EXCLUDES)}")
    print(f"-- theme lists generated from {MAPPING.relative_to(REPO)}")
    print()
    print(TEMPLATE.format(monetary=fmt(monetary), stress=fmt(stress),
                          start=args.start, end=args.end))


if __name__ == "__main__":
    main()
