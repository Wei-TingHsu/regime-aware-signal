"""era_adapters.py (v2: index mask fix; missing forward returns dropped) -- the last two era adapters of the sub-period audit (prereg_subperiod_audit.md group B, items B6 and B10).

  python -m src.era_adapters t1          # B6: the exposure dial (T1) by era -- certainty-equivalent return of always-in (v1), vol-targeting (v2) and
                                         #     regime-tilted (v3) per asset per era, with the paired bootstrap test v2/v3 vs v1 inside each era
  python -m src.era_adapters htables     # B10: the history tables H0-H5 by era -- the recorded events re-cut by era, the sign share vs that era's own
                                         #     base rate, random-date null; rows under 30 events measured only
Uses src.exposure_dial (load_inputs, run_asset, cer, paired_cer_test) and src.history_tables (OUT json, paths, cond_test) as they stand.
Outputs docs/era_t1.md, docs/era_htables.md (+ .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

DOCS = Path("docs")
ERAS = [("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"), ("2015-19", "2015-01-01", "2019-12-31"),
        ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]


def era_mask(idx: pd.DatetimeIndex, name: str) -> np.ndarray:
    a, b = [e for e in ERAS if e[0] == name][0][1:]
    return np.asarray((idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b)))


# ------------------------------------------------------------------------------------------------ B6 T1 by era
def cmd_t1(cost_bp: float, n_boot: int):
    import src.exposure_dial as ED
    idx, rets, lab, post, rf = ED.load_inputs(); rng = np.random.default_rng(0); rows = []
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a].to_numpy(float); ok = np.isfinite(r)
        if ok.sum() < 500: continue
        r0 = np.where(ok, r, 0.0)
        out = ED.run_asset(r0, rf, lab, cost_bp, post)
        for name, _, _ in ERAS + [("all", "1900-01-01", "2099-12-31")]:
            m = ok if name == "all" else (era_mask(idx, name) & ok)
            if m.sum() < 250: continue
            v1 = out["ret"][(1, "1x")][m]; row = dict(asset=a, era=name, n=int(m.sum()), cer_v1=ED.cer(v1))
            for v, label in ((2, "vol_target"), (3, "regime_tilt")):
                key = (v, "1x")
                if key not in out["ret"]: continue
                x = out["ret"][key][m]; row[f"cer_{label}"] = ED.cer(x)
                try:
                    t = ED.paired_cer_test(x, v1, rng, n_boot); row[f"p_{label}"] = t.get("p", t.get("p_value", np.nan)); row[f"d_{label}"] = t.get("diff", t.get("delta", row[f"cer_{label}"] - row["cer_v1"]))
                except Exception as e:
                    row[f"p_{label}"] = np.nan; row[f"d_{label}"] = row[f"cer_{label}"] - row["cer_v1"]; row["note"] = f"{type(e).__name__}"
            rows.append(row)
    tab = pd.DataFrame(rows)
    out = DOCS / "era_t1.md"
    L = ["# T1 — the exposure dial by era (certainty-equivalent return, annualised; 1× cost)", "",
         f"v1 always-in, v2 vol-targeting, v3 regime-tilted; paired stationary-bootstrap test of v2 and v3 against v1 inside each era ({n_boot} draws). Rows under 250 sessions are omitted.", "",
         "| asset | era | n | CER v1 | CER vol-target | Δ | p | CER regime-tilt | Δ | p |", "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r_ in tab.iterrows():
        f = lambda k: (f"{r_[k]:+.2%}" if k in r_ and np.isfinite(r_[k]) else "·"); g = lambda k: (f"{r_[k]:.3f}" if k in r_ and np.isfinite(r_[k]) else "·")
        L.append(f"| {r_['asset']} | {r_['era']} | {r_['n']} | {f('cer_v1')} | {f('cer_vol_target')} | {f('d_vol_target')} | {g('p_vol_target')} | {f('cer_regime_tilt')} | {f('d_regime_tilt')} | {g('p_regime_tilt')} |")
    L += ["", "Reading: vol-targeting that helps only in one era (2008, 2020) is a crisis tool, not a standing improvement; the pooled verdict (1 of 5 assets, oil) stands unless an era row beats v1 at p < 0.05 in both halves of the record."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(orient="records", indent=1)); print(tab.to_string(index=False)); print(f"-> {out}")


# ------------------------------------------------------------------------------------------------ B10 history tables by era
def cmd_htables():
    import src.history_tables as HT
    J = json.loads(Path(HT.OUT).read_text()) if Path(HT.OUT).exists() else None
    if J is None: print(f"history tables json not found at {HT.OUT} -- run `python -m src.history_tables` first"); return
    rets = pd.read_parquet("processed/asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    rows = []
    for tid, res in J.items():
        dates = pd.to_datetime(res.get("dates", [])); pos_all = rets.index.searchsorted(dates); pos_all = pos_all[pos_all < len(rets)]
        for a in [x for x in ASSETS if x in rets.columns and x in res.get("markets", {})]:
            r = rets[a]
            for name, lo, hi in ERAS + [("all", "1900-01-01", "2099-12-31")]:
                pos = [p for p in pos_all if pd.Timestamp(lo) <= rets.index[p] <= pd.Timestamp(hi)]
                prow = [dict(HT.paths(r, p), pos=p) for p in pos]; prow = [d for d in prow if d]
                if len(prow) < 5: continue
                df = pd.DataFrame(prow); r_era = (r[(r.index >= lo) & (r.index <= hi)] if name != "all" else r).dropna()
                for h in (5, 20):
                    col = f"f{h}"
                    if col not in df: continue
                    dh = df[np.isfinite(df[col])]                         # v2: events with no forward return (asset history not yet started) are dropped,
                    if len(dh) < 5: continue                             #     not counted as 'not positive' -- the v1 bug that printed spurious PASSes
                    te = HT.cond_test(dh, r_era, h) if len(dh) >= HT.MIN_N else dict(verdict="measured (n < 30)", n=len(dh))
                    rows.append(dict(table=tid, asset=a, era=name, h=h, n=len(dh), median=float(dh[col].median()), positive=float((dh[col] > 0).mean()),
                                     base=te.get("base", np.nan), gap=te.get("gap", np.nan), p=te.get("p", np.nan), verdict=te["verdict"]))
    tab = pd.DataFrame(rows)
    out = DOCS / "era_htables.md"
    L = ["# History tables H0–H5 by era", "", "Each table's recorded events re-cut by era; 'positive' = share of events with a higher price h sessions later; 'base' = that era's own share; random-date null. Under 30 events: measured, not judged.", ""]
    for tid, g in tab.groupby("table"):
        L += [f"## {tid}", "", "| asset | era | h | n | median | positive | base | gap | p | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
        for _, r_ in g.iterrows():
            f = lambda v, fmt: (fmt.format(v) if isinstance(v, float) and np.isfinite(v) else "·")
            L.append(f"| {r_['asset']} | {r_['era']} | {r_['h']} | {r_['n']} | {f(np.expm1(r_['median']) if np.isfinite(r_['median']) else np.nan, '{:+.1%}')} | {f(r_['positive'], '{:.0%}')} | {f(r_['base'], '{:.0%}')} | {f(r_['gap'], '{:+.0%}')} | {f(r_['p'], '{:.3f}')} | {r_['verdict']} |")
        L.append("")
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(orient="records", indent=1))
    print(tab[tab.verdict.str.startswith("PASS")].to_string(index=False) if (tab.verdict == "PASS").any() else "no era cell PASSes"); print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["t1", "htables"]); ap.add_argument("--cost-bp", type=float, default=5.0); ap.add_argument("--n-boot", type=int, default=1000)
    a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    cmd_t1(a.cost_bp, a.n_boot) if a.cmd == "t1" else cmd_htables()
