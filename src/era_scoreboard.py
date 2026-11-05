"""era_scoreboard.py -- the report's directional calls by era, from any backfill CSV (prereg_subperiod_audit.md, group A).

Rows 24/27/33 (the calls beat drift), 25 (the tiers grade confidence), 26 (`fomc_minutes`-driven calls) and the E-lever folders were
judged on the whole span. This splits them by the registered eras and by the median date, with the scoreboard's own definitions
(hit: sign agreement, zero return = miss; asymmetry: mean |ret| on hits / mean |ret| on misses; profit factor), a block-permutation
null of the call signs within each era, the S1-S3 split rule, and a sweep over eras x sources x tiers judged against the
best-of-sweep null -- so "the era / source / tier in which the calls work best" is found and judged in one pass.

  python -m src.era_scoreboard --csv processed/report_backfill_97d9bf07dd2c_n5793.csv            # primary horizon 2, close-to-close
  python -m src.era_scoreboard --csv ... --h 3 --ret ret_tradeable --n-null 1000 --out docs/era_scoreboard_<tag>.md

Nothing here writes the register; the markdown and JSON carry the numbers for the audit's results table.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md

ERAS = [("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"), ("2015-19", "2015-01-01", "2019-12-31"),
        ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]
BLOCK = 2                       # block length in rows per asset for the permutation null (= primary horizon)
MIN_N = 30


def era_of(d: pd.Timestamp) -> str:
    for name, a, b in ERAS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b):
            return name
    return "other"


def load(csv: Path, h: int, ret_col: str) -> pd.DataFrame:
    df = pd.read_csv(csv); df["date"] = pd.to_datetime(df["date"])
    df = df[(df["h"] == h) & (df["kind"] == "call") & df["call"].notna() & df[ret_col].notna()].copy()
    df = df.rename(columns={ret_col: "ret"}).sort_values(["asset", "date"]).reset_index(drop=True)
    df["era"] = df["date"].map(era_of); df["hit"] = (np.sign(df["call"]) == np.sign(df["ret"])) & (df["ret"] != 0)
    med = df["date"].median(); df["half"] = np.where(df["date"] <= med, "first", "second")
    for c in ("tier", "dominant_source"):
        if c not in df.columns:
            df[c] = "n/a"
        df[c] = df[c].fillna("n/a").astype(str)
    return df


def metrics(call: np.ndarray, ret: np.ndarray) -> dict:
    """The scoreboard's definitions (report_scoreboard.metrics)."""
    n = len(call)
    if n == 0:
        return dict(n=0, hit=np.nan, asym=np.nan, mean_signed=np.nan, pf=np.nan)
    hit = (np.sign(call) == np.sign(ret)) & (ret != 0)
    m_h = np.abs(ret[hit]).mean() if hit.any() else np.nan; m_m = np.abs(ret[~hit]).mean() if (~hit).any() else np.nan
    asym = (m_h / m_m) if (hit.any() and (~hit).any() and m_m > 0) else np.nan
    signed = call * ret; gains = signed[signed > 0].sum(); losses = -signed[signed < 0].sum()
    return dict(n=int(n), hit=float(hit.mean()), asym=float(asym) if np.isfinite(asym) else np.nan, mean_signed=float(signed.mean()),
                pf=float(gains / losses) if losses > 0 else np.nan)


def perm_calls(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Permute the call signs in blocks of BLOCK rows within each asset: the null of 'the calls carry no information about the sign'."""
    d = df.copy(); out = np.empty(len(d))
    for _, idx in d.groupby("asset").indices.items():
        x = d["call"].to_numpy()[idx]; n = len(x); starts = np.arange(0, n, BLOCK); order = rng.permutation(len(starts))
        perm = np.concatenate([np.arange(starts[j], min(starts[j] + BLOCK, n)) for j in order])
        out[idx] = x[perm]
    d["call"] = out; return d


def by_group(df: pd.DataFrame, col: str, rng: np.random.Generator, n_null: int) -> pd.DataFrame:
    rows = []
    groups = [g for g in df[col].dropna().unique()]
    nulls = {g: [] for g in groups}
    for _ in range(n_null):
        d2 = perm_calls(df, rng)
        for g, sub in d2.groupby(col):
            if g in nulls:
                nulls[g].append(metrics(sub["call"].to_numpy(float), sub["ret"].to_numpy(float))["hit"])
    for g in groups:
        sub = df[df[col] == g]; m = metrics(sub["call"].to_numpy(float), sub["ret"].to_numpy(float))
        nl = np.array(nulls[g], float); nl = nl[np.isfinite(nl)]
        m.update(group=str(g), first=str(sub["date"].min().date()), last=str(sub["date"].max().date()),
                 null_q95=float(np.quantile(nl, 0.95)) if len(nl) else np.nan, p=float((nl >= m["hit"]).mean()) if len(nl) else np.nan,
                 verdict=("UNDERPOWERED (n < 30)" if m["n"] < MIN_N else ("beats null" if (len(nl) and m["hit"] > np.quantile(nl, 0.95)) else "inside null")))
        rows.append(m)
    return pd.DataFrame(rows)


def split_rule(df: pd.DataFrame) -> dict:
    """Rule C: S1 sign agreement of mean signed return across halves; S2 neither half > 3x the other in |mean signed|; hit-rates beside."""
    a, b = df[df.half == "first"], df[df.half == "second"]
    ma, mb = metrics(a["call"].to_numpy(float), a["ret"].to_numpy(float)), metrics(b["call"].to_numpy(float), b["ret"].to_numpy(float))
    s1 = np.sign(ma["mean_signed"]) == np.sign(mb["mean_signed"]) != 0
    lo, hi = sorted([abs(ma["mean_signed"]), abs(mb["mean_signed"])])
    s2 = bool(lo > 0 and hi / lo <= 3)
    return dict(first=ma, second=mb, median_date=str(df["date"].median().date()), S1_sign=bool(s1), S2_magnitude=s2, ratio=(hi / lo if lo > 0 else np.inf))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True); ap.add_argument("--h", type=int, default=2); ap.add_argument("--ret", default="ret_primary")
    ap.add_argument("--n-null", type=int, default=500); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out")
    a = ap.parse_args()
    csv = Path(a.csv); tag = csv.stem.replace("report_backfill_", "")
    df = load(csv, a.h, a.ret)
    if df.empty:
        raise SystemExit("no calls at that horizon / return column")
    rng = np.random.default_rng(a.seed)
    overall = metrics(df["call"].to_numpy(float), df["ret"].to_numpy(float))
    eras = by_group(df, "era", rng, a.n_null)
    tiers = by_group(df, "tier", rng, a.n_null) if df["tier"].nunique() > 1 else None
    srcs = by_group(df, "dominant_source", rng, a.n_null) if df["dominant_source"].nunique() > 1 else None
    assets = by_group(df, "asset", rng, a.n_null)
    split = split_rule(df)
    # the sweep: era x source x asset, statistic = hit-rate (n >= 30), judged against the best-of-sweep null
    cells = grid(era=[e[0] for e in ERAS if (df.era == e[0]).any()] + ["all"], source=sorted(df["dominant_source"].unique()) + ["all"], asset=sorted(df["asset"].unique()) + ["all"])
    def stat(d, c):
        m = np.ones(len(d), bool)
        if c["era"] != "all": m &= (d["era"] == c["era"]).to_numpy()
        if c["source"] != "all": m &= (d["dominant_source"] == c["source"]).to_numpy()
        if c["asset"] != "all": m &= (d["asset"] == c["asset"]).to_numpy()
        if m.sum() < MIN_N: return np.nan, int(m.sum())
        return float(df_hit(d[m])), int(m.sum())
    sw = run(cells, stat, df, lambda d, r: perm_calls(d, r), n_null=min(a.n_null, 300), seed=a.seed + 1, label=f"calls by era x source x asset — {tag} h{a.h} {a.ret}")
    out = Path(a.out) if a.out else Path("docs") / f"era_scoreboard_{tag}_h{a.h}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    def tbl(t: pd.DataFrame, name: str) -> list[str]:
        L = [f"## By {name}", "", "| group | n | first | last | hit-rate | null q95 | p | asymmetry | mean signed | PF | verdict |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in t.iterrows():
            L.append(f"| {r['group']} | {r['n']} | {r['first']} | {r['last']} | {r['hit']:.1%} | {r['null_q95']:.1%} | {r['p']:.3f} | {r['asym']:.3f} | {r['mean_signed'] * 100:+.3f}% | {r['pf']:.2f} | {r['verdict']} |")
        return L + [""]
    L = [f"# The report's calls by era — `{tag}`, horizon {a.h}, {a.ret}", "",
         f"{overall['n']:,} calls {df['date'].min().date()} → {df['date'].max().date()}; pooled hit-rate {overall['hit']:.1%}, asymmetry {overall['asym']:.3f}, mean signed {overall['mean_signed'] * 100:+.3f}%, PF {overall['pf']:.2f}. "
         f"Null: call signs permuted in blocks of {BLOCK} within asset, {a.n_null} draws; a group 'beats null' when its hit-rate exceeds the null's 95th percentile. Rows with n < {MIN_N} are UNDERPOWERED, not verdicts.", ""]
    L += tbl(eras, "era (registered boundaries)")
    L += [f"## Split rule C at the median date ({split['median_date']})", "",
          f"First half: n {split['first']['n']}, hit {split['first']['hit']:.1%}, mean signed {split['first']['mean_signed'] * 100:+.3f}%; second half: n {split['second']['n']}, hit {split['second']['hit']:.1%}, mean signed {split['second']['mean_signed'] * 100:+.3f}%. "
          f"S1 sign agreement: {'PASS' if split['S1_sign'] else 'FAIL'}; S2 magnitude (ratio {split['ratio']:.2f} ≤ 3): {'PASS' if split['S2_magnitude'] else 'FAIL'}.", ""]
    if tiers is not None: L += tbl(tiers, "tier (row 25)")
    if srcs is not None: L += tbl(srcs, "dominant source (row 26)")
    L += tbl(assets, "asset")
    L += [f"## Sweep — era × source × asset (hit-rate, cells with n ≥ {MIN_N})", "",
          f"Best cell `{sw.best}`: hit-rate {sw.best_stat:.1%} on n = {int(sw.surface.loc[sw.surface['stat'].idxmax(), 'n'])}; best-of-sweep null 95th percentile {sw.q95:.1%}; **p_family = {sw.p_family:.3f}**; survivors {len(sw.survivors)}.",
          "A survivor here is a candidate for a forward test, not a finding: the whole surface is in the JSON beside this file.", ""]
    out.write_text("\n".join(L) + "\n")
    write_md(sw, out.with_name(out.stem + "_sweep.md"), axis_rows="era", axis_cols="asset", fmt="{:.1%}")
    J = dict(tag=tag, h=a.h, ret=a.ret, overall=overall, eras=json.loads(eras.to_json(orient="records")), split=split,
             tiers=json.loads(tiers.to_json(orient="records")) if tiers is not None else None, sources=json.loads(srcs.to_json(orient="records")) if srcs is not None else None,
             assets=json.loads(assets.to_json(orient="records")), sweep=sw.to_json())
    out.with_suffix(".json").write_text(json.dumps(J, indent=1, default=float))
    print(f"-> {out}  (+ _sweep.md, .json)")
    print(eras[["group", "n", "hit", "null_q95", "p", "asym", "verdict"]].to_string(index=False))
    print(f"split C: S1 {'PASS' if split['S1_sign'] else 'FAIL'}, S2 {'PASS' if split['S2_magnitude'] else 'FAIL'} (ratio {split['ratio']:.2f}); sweep best {sw.best} {sw.best_stat:.1%}, q95 {sw.q95:.1%}, p_family {sw.p_family:.3f}")


def df_hit(d: pd.DataFrame) -> float:
    c, r = d["call"].to_numpy(float), d["ret"].to_numpy(float)
    return float(((np.sign(c) == np.sign(r)) & (r != 0)).mean())


if __name__ == "__main__":
    main()
