"""faststate.py -- the fast-state discovery (docs/prereg_regime_audit.md section 3b): let the data form the day-level environments from the
MOVES of the eight macro dials and five assets (the slow regimes are built on their LEVELS), then ask whether those states carry information.

  python -m src.faststate fit        # standardised daily changes (8 dials + SPY, TLT, GLD, UUP, USO) -> PCA(3) -> mixture k = 3..8, expanding refit
                                     #   every 20 sessions (first 504 unlabelled), canonical PC1 order; per k: median run, state shares; states saved
  python -m src.faststate describe   # per k: what each fast state looks like (mean standardised move of every dial and asset on days of that state)
  python -m src.faststate test       # per k: (F1) forward 5/10/20-session returns per state x asset, both directions, best-of-search null;
                                     #   (F2) states in the 60 sessions before a slow-regime change vs elsewhere; (F3) Fed-day reaction by fast state;
                                     #   (F4) the environment -> favoured-asset map's stability (first vs second half) per k
  python -m src.faststate all
Outputs docs/faststate_*.md (+ .json), processed/fast_states.parquet. Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md
from src.deeper import returns, macro, path_stats, fwd, COST, MIN_N

PROC, DOCS = Path("processed"), Path("docs")
DIALS = ["DGS10", "DGS2", "T10Y2Y", "DFII10", "EFFR", "M2SL", "VIXCLS", "DTWEXBGS"]
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
KS = (3, 4, 5, 6, 8)


def panel() -> pd.DataFrame:
    r = returns(); m = macro(); idx = r.index
    cols = {}
    for c in [c for c in DIALS if m is not None and c in m.columns]:
        s = m[c].reindex(idx).ffill(); cols[c] = (np.log(s).diff() if c == "M2SL" else s.diff())
    for a in [a for a in ASSETS if a in r.columns]: cols[a] = r[a]
    d = pd.DataFrame(cols).dropna(); z = (d - d.rolling(504, min_periods=250).mean()) / d.rolling(504, min_periods=250).std()
    return z.dropna()


def expanding_states(Z: np.ndarray, k: int, seed: int = 0, refit_every: int = 20, min_train: int = 504) -> np.ndarray:
    from sklearn.decomposition import PCA; from sklearn.mixture import GaussianMixture
    n = len(Z); lab = np.full(n, -1); model = pca = None; last = -10 ** 9
    for t in range(min_train, n):
        if model is None or t - last >= refit_every:
            pca = PCA(3).fit(Z[: t + 1]); P = pca.transform(Z[: t + 1])
            model = GaussianMixture(k, covariance_type="full", random_state=seed, n_init=2).fit(P); order = np.argsort(model.means_[:, 0]); remap = np.empty(k, int); remap[order] = np.arange(k); last = t
        lab[t] = int(remap[model.predict(pca.transform(Z[t: t + 1]))[0]])
    return lab


def cmd_fit():
    z = panel(); Z = z.to_numpy(); out = {}
    for k in KS:
        print(f"  k = {k} ..."); lab = expanding_states(Z, k); out[f"k{k}"] = lab
        runs = np.diff(np.where(np.diff(np.concatenate([[-9], lab, [-9]])) != 0)[0]); print(f"    median run {np.median(runs):.1f}, shares " + ", ".join(f"{g}: {(lab == g).mean():.0%}" for g in sorted(set(lab[lab >= 0]))))
    df = pd.DataFrame(out, index=z.index); df.to_parquet(PROC / "fast_states.parquet"); print(f"-> processed/fast_states.parquet ({len(df):,} sessions, {len(z.columns)} inputs: {list(z.columns)})")


def _states():
    s = pd.read_parquet(PROC / "fast_states.parquet"); s.index = pd.to_datetime(s.index); return s


def cmd_describe():
    z = panel(); S = _states().reindex(z.index); L = ["# Fast states described — mean standardised move on days of each state", ""]
    for k in KS:
        lab = S[f"k{k}"].to_numpy(); L += [f"## k = {k}", "", "| state | share | median run | " + " | ".join(z.columns) + " |", "|---|---|---|" + "---|" * len(z.columns)]
        for g in sorted(set(int(x) for x in lab[np.isfinite(lab)] if x >= 0)):
            mk = lab == g; runs = np.diff(np.where(np.diff(np.concatenate([[0], mk.astype(int), [0]])) != 0)[0])[::2]
            L.append(f"| {g} | {mk.mean():.0%} | {np.median(runs):.0f} | " + " | ".join(f"{z.loc[mk, c].mean():+.2f}" for c in z.columns) + " |")
        L.append("")
    (DOCS / "faststate_describe.md").write_text("\n".join(L) + "\n"); print("-> docs/faststate_describe.md")


def cmd_test():
    z = panel(); S = _states().reindex(z.index); r = returns().reindex(z.index); assets = [a for a in ASSETS if a in r.columns]; n = len(z); rng = np.random.default_rng(0)
    data = {a: np.nan_to_num(r[a].to_numpy()) for a in assets}
    # slow labels and Fed-day table, if available
    slow = None
    try:
        import src.exposure_dial as ED
        idx, rets, lab, post, rf = ED.load_inputs(); slow = pd.Series(ED.confirmed_labels(np.asarray(lab)), index=pd.DatetimeIndex(idx)).reindex(z.index).ffill().to_numpy()
    except Exception as e:
        print(f"  slow labels unavailable ({type(e).__name__}) -- F2 skipped")
    try:
        from src.chair_power import table, interaction_F, ols
        fed = table().dropna(subset=["s_norm", "gld"]).copy()
    except Exception as e:
        fed = None; print(f"  Fed-day table unavailable ({type(e).__name__}) -- F3 skipped")
    from src.regime_describe import asset_map
    L = ["# Fast states — do they carry information?", ""]; summary = []
    for k in KS:
        lab = S[f"k{k}"].to_numpy().astype(float); lab = np.where(np.isfinite(lab), lab, -1).astype(int); states = sorted(set(lab[lab >= 0]))
        # F1 forward returns per state x asset x horizon x direction (entry at the close of the state day)
        def stat(dd, c):
            g = np.asarray(dd[c["asset"]]); cum = np.concatenate([[0], np.cumsum(g)]); ev = np.where(lab == c["state"])[0]; ev = ev[ev < n - c["h"] - 1]
            f = fwd(cum, ev, c["h"]); ps = path_stats(f, c["h"], COST, c["sign"]); return ps["sharpe"], ps["n"]
        cells = grid(state=states, asset=assets, h=[5, 10, 20], sign=[1, -1])
        def null_gen(dd, rg):
            return {a: np.roll(g, int(rg.integers(250, len(g) - 250))) for a, g in dd.items()}
        sw = run(cells, stat, data, null_gen, n_null=150, seed=k, label=f"F1 fast state (k={k}) → next sessions, net Sharpe", meta=dict(tag=f"k{k}", rows="state", cols="h"))
        write_md(sw, DOCS / f"faststate_forward_k{k}.md", axis_rows="state", axis_cols="h", fmt="{:+.2f}")
        row = dict(k=k, F1_best=sw.best, F1_sharpe=sw.best_stat, F1_q95=sw.q95, F1_p=sw.p_family, F1_survivors=len(sw.survivors))
        # F2 before slow-regime changes
        if slow is not None:
            sl = np.where(np.isfinite(slow), slow, -1).astype(int); ch = np.where((sl[1:] != sl[:-1]) & (sl[1:] >= 0) & (sl[:-1] >= 0))[0] + 1
            def pre_mask(changes):
                m = np.zeros(n, bool)
                for c in changes: m[max(0, c - 60):c] = True
                return m
            pre = pre_mask(ch); obs = {g: (lab[pre] == g).mean() - (lab[~pre] == g).mean() for g in states}; nm = []
            for _ in range(300):
                s_ = int(rng.integers(60, n - 60)); ex = pre_mask((ch + s_) % n); nm.append(max(abs((lab[ex] == g).mean() - (lab[~ex] == g).mean()) for g in states))
            best = max(obs, key=lambda g: abs(obs[g])); row.update(F2_best_state=int(best), F2_excess=float(obs[best]), F2_q95=float(np.quantile(nm, 0.95)), F2_p=float((np.array(nm) >= abs(obs[best])).mean()))
        # F3 Fed-day reaction by fast state
        if fed is not None:
            ff = fed.copy(); ff["state"] = pd.Series(lab, index=z.index).reindex(pd.DatetimeIndex(ff["date"])).to_numpy(); ff = ff[np.isfinite(ff.state) & (ff.state >= 0)]
            if len(ff) >= 40 and ff.state.nunique() > 1:
                Fv = interaction_F(ff, "gld", ff.state.to_numpy().astype(int), "s_norm"); null = [interaction_F(ff, "gld", rng.permutation(ff.state.to_numpy().astype(int)), "s_norm") for _ in range(500)]; row["F3_fed_p"] = float((np.array(null) >= Fv).mean())
        # F4 favoured-asset map stability
        am = asset_map(z.index, r, lab, f"fast k={k}", rng, n_perm=150); row.update(F4_stability=am["stability"], F4_p=am["p"], F4_sharpe=am["sharpe"])
        summary.append(row); print({kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in row.items() if kk != "F4_sharpe"})
        L += [f"## k = {k}", "", f"F1 forward: best `{sw.best}` Sharpe {sw.best_stat:+.2f} vs q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}, survivors {len(sw.survivors)}.",
              (f"F2 before slow-regime changes: state {row['F2_best_state']} excess {row['F2_excess'] * 100:+.1f} pts vs q95 {row['F2_q95'] * 100:.1f}, p {row['F2_p']:.3f}." if "F2_p" in row else "F2 skipped."),
              (f"F3 Fed-day reaction by fast state: interaction p {row['F3_fed_p']:.3f}." if "F3_fed_p" in row else "F3 skipped."),
              f"F4 favoured-asset map: stability {am['stability']:+.2f}, p {am['p']:.3f}.", ""]
    (DOCS / "faststate_tests.md").write_text("\n".join(L) + "\n"); (DOCS / "faststate_tests.json").write_text(json.dumps(summary, indent=1, default=float)); print("-> docs/faststate_tests.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fit", "describe", "test", "all"]); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    for c in (["fit", "describe", "test"] if a.cmd == "all" else [a.cmd]):
        {"fit": cmd_fit, "describe": cmd_describe, "test": cmd_test}[c]()
