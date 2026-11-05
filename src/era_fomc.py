"""era_fomc.py -- T9b by era: gold's (and TLT's) statement-day reaction to the 2-year-yield surprise in each policy era, in basis
points and in units of the yield's own volatility (prereg_subperiod_audit.md, group B, item B5). T-K1/T-K1' cut the same
131 days by chair; this cuts them by era (zero bound / normalisation / pandemic / hiking) and runs the same interaction test.

  python -m src.era_fomc            # per era: n, beta per bp, beta per sigma, t; era x surprise interaction F with permutation p, both scales
Inputs: src.chair_power.table() (date, chair, s, vol, gld, tlt, s_norm). Output docs/era_fomc.md (+ .json). Nothing here writes the register.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.chair_power import table, ols, interaction_F, NPERM

DOCS = Path("docs")
ERAS = [("2011-15 zero bound", "2011-01-01", "2015-12-15"), ("2015-19 normalisation", "2015-12-16", "2019-12-31"),
        ("2020-21 pandemic", "2020-01-01", "2021-12-31"), ("2022-26 hiking & after", "2022-01-01", "2026-12-31")]


def era_of(d) -> str:
    for name, a, b in ERAS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def main():
    df = table().dropna(subset=["s", "gld"]).copy(); df["era"] = df["date"].map(era_of); df = df[df.era != "other"]
    rows = []
    for e in [e[0] for e in ERAS]:
        sub = df[df.era == e]
        if len(sub) < 8: continue
        _, b, se, _, _ = ols(sub["s"].to_numpy(), sub["gld"].to_numpy()); _, bn, sen, _, _ = ols(sub["s_norm"].to_numpy(), sub["gld"].to_numpy())
        _, bt, set_, _, _ = ols(sub["s"].to_numpy(), sub["tlt"].to_numpy()) if sub["tlt"].notna().sum() >= 8 else (np.nan,) * 5
        rows.append(dict(era=e, n=len(sub), first=str(sub["date"].min().date()), last=str(sub["date"].max().date()), sd_s_bp=float(sub["s"].std(ddof=1)),
                         beta_bp=b * 100, t_bp=(b / se if se else np.nan), beta_sigma=bn * 100, t_sigma=(bn / sen if sen else np.nan), tlt_beta_bp=(bt * 100 if np.isfinite(bt) else np.nan)))
    tab = pd.DataFrame(rows)
    rng = np.random.default_rng(0); lab = df["era"].to_numpy(); res = {}
    for xcol, name in (("s", "per bp"), ("s_norm", "per σ")):
        F = interaction_F(df, "gld", lab, xcol); null = np.array([interaction_F(df, "gld", rng.permutation(lab), xcol) for _ in range(NPERM)])
        res[name] = dict(F=float(F), p=float((null >= F).mean()))
    out = DOCS / "era_fomc.md"
    L = [f"# T9b by era — gold's statement-day reaction to the 2-year surprise ({df['date'].min().date()} → {df['date'].max().date()}, {len(df)} statements)", "",
         "β per bp = GLD's log return (%) per 1 bp change in DGS2 on the statement day; β per σ = per one trailing-two-year standard deviation of daily DGS2 changes (the scale on which T-K1′ found chairs exchangeable).", "",
         "| era | n | first | last | sd(surprise) bp | β per bp (%) | t | β per σ (%) | t | TLT β per bp |", "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r_ in tab.iterrows():
        L.append(f"| {r_['era']} | {r_['n']} | {r_['first']} | {r_['last']} | {r_['sd_s_bp']:.1f} | {r_['beta_bp']:+.3f} | {r_['t_bp']:+.2f} | {r_['beta_sigma']:+.2f} | {r_['t_sigma']:+.2f} | {r_['tlt_beta_bp']:+.3f} |")
    L += ["", f"Era × surprise interaction (do the eras differ?), {NPERM} permutations of the era labels: per bp F {res['per bp']['F']:.2f}, p {res['per bp']['p']:.3f}; "
          f"per σ F {res['per σ']['F']:.2f}, p {res['per σ']['p']:.3f}.", "",
          "Reading: a difference per bp that vanishes per σ is the yield era's scale (T-K1 → T-K1′); a difference that survives per σ is a change in gold's reaction itself."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(dict(eras=json.loads(tab.to_json(orient="records")), interaction=res), indent=1, default=float))
    print(tab[["era", "n", "sd_s_bp", "beta_bp", "t_bp", "beta_sigma", "t_sigma"]].to_string(index=False)); print("interaction:", res); print(f"-> {out}")


if __name__ == "__main__":
    main()
