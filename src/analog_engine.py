"""
Problem 1 engine -- STAGE 1: the analog + factor-attribution directional core.

Given TODAY's macro state, produce a factor-attributed directional call:
  1. ANALOG MATCH   -- find historical days that are (a) in the SAME n=4 regime
     as now AND (b) nearest to now in PCA-score space, weighted by config
     similarity_sigma and recency_decay_lambda.
  2. FORWARD READ   -- for those analogs, read what happened NEXT: each asset's
     H-day forward return. Weighted-average -> expected move + hit-rate.
  3. FACTOR ATTRIB  -- rolling regression of each focus asset on the macro PCs
     over a trailing window -> % of its recent variance each macro factor drives.
Output: ranked long / short candidates, each with expected H-day move, a
confidence (hit-rate), and the macro-factor breakdown.

No look-ahead in the CALL: analogs use only past data, and forward windows of
the analogs are fully realized before the as-of date.

Refits n=4 regimes on the fly (the documented count) rather than reading the
BIC-selected n=5 regime_labels.parquet.

Run:
    python -m src.analog_engine
Optional:
    --asof 2026-07-06     as-of date (default: latest available)
    --horizon 5           forward horizon in trading days
    --topk 100            number of nearest analogs to weight
    --reg-window 60       trailing window for the factor attribution
    --n-show 6            how many long / short candidates to print
"""
import argparse

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR

CLUSTERING_PCS = ["PC1", "PC2", "PC3"]          # regime lives in the top-3 PCs
ATTRIB_PCS = ["PC1", "PC2", "PC3", "PC4", "PC5"]
PROXY_MEANING = {
    "DGS2": "rates", "EFFR": "rates", "DGS10": "long-rates", "VIXCLS": "stress",
    "T10Y2Y": "curve", "M2SL": "money", "DTWEXBGS": "USD", "DFII10": "real-rates",
}


def load_returns(path=None):
    p = path or (PROCESSED_DIR / "asset_returns.parquet")
    df = pd.read_parquet(p); df.index = pd.to_datetime(df.index)
    df = df.sort_index().dropna(how="all")
    if np.nanmedian(np.abs(df.to_numpy())) > 0.5:
        df = df.pct_change()
    return df


def pc_names(scores, macro):
    """Best proxy per PC (data-driven), so factor labels survive PCA renumbering."""
    proxies = [p for p in PROXY_MEANING if p in macro.columns]
    common = scores.index.intersection(macro.index)
    names = {}
    for pc in scores.columns:
        best, br = None, 0.0
        for p in proxies:
            r = abs(np.corrcoef(scores.loc[common, pc].values, macro.loc[common, p].values)[0, 1])
            if r > br:
                best, br = p, r
        names[pc] = f"{pc}:{PROXY_MEANING.get(best, '?')}"
    return names


def factor_attribution(r_asset, scores, as_of, window, pcs):
    """% of the asset's trailing-window variance driven by each macro PC."""
    end = scores.index.get_indexer([as_of], method="ffill")[0]
    idx = scores.index[max(0, end - window + 1): end + 1]
    y = r_asset.reindex(idx)
    X = scores.reindex(idx)[pcs]
    df = pd.concat([y, X], axis=1).dropna()
    if len(df) < window // 2:
        return {}
    yy = df.iloc[:, 0].values
    XX = df[pcs].values
    A = np.hstack([XX, np.ones((len(XX), 1))])
    beta, *_ = np.linalg.lstsq(A, yy, rcond=None)
    contrib = {pcs[i]: (beta[i] ** 2) * np.var(XX[:, i]) for i in range(len(pcs))}
    tot = sum(contrib.values()) or 1.0
    return {k: v / tot for k, v in contrib.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=None)
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--topk", type=int, default=100)
    ap.add_argument("--reg-window", type=int, default=60)
    ap.add_argument("--n-show", type=int, default=6)
    args = ap.parse_args()
    from sklearn.mixture import GaussianMixture

    cfg = load_config()
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    rets = load_returns()
    try:
        macro = pd.read_parquet(PROCESSED_DIR / "macro_panel.parquet")
        macro.index = pd.to_datetime(macro.index)
        names = pc_names(scores, macro)
    except Exception:
        names = {pc: pc for pc in scores.columns}

    H = args.horizon
    as_of = pd.to_datetime(args.asof) if args.asof else scores.index.max()

    # --- refit n=4 regimes on the clustering PCs ---------------------------
    Xc = scores[CLUSTERING_PCS]
    gm = GaussianMixture(n_components=4, covariance_type=cfg["regime"]["covariance_type"],
                         max_iter=cfg["regime"]["max_iter"], n_init=cfg["regime"]["n_init"],
                         random_state=cfg["project"]["random_seed"])
    labels = pd.Series(gm.fit_predict(Xc.values), index=scores.index)

    if as_of not in labels.index:
        as_of = labels.index[labels.index.get_indexer([as_of], method="ffill")[0]]
    r_now = labels.loc[as_of]
    x_now = Xc.loc[as_of].values

    print("=" * 76)
    print("PROBLEM 1 ENGINE -- Stage 1 (analog + factor-attribution directional call)")
    print("=" * 76)
    print(f"as-of: {as_of.date()}   |   current regime: {int(r_now)} (n=4)   |   horizon: {H}d")

    # --- analog candidates: same regime, forward window fully realized -----
    cutoff = labels.index[labels.index.get_indexer([as_of], method="ffill")[0]]
    cand = labels.index[(labels == r_now) & (labels.index < cutoff)]
    # need the H-day-ahead date to exist strictly before as_of
    pos = scores.index.get_indexer(cand)
    end_pos = scores.index.get_indexer([as_of])[0]
    cand = cand[(pos + H) < end_pos]
    if len(cand) < 20:
        raise SystemExit(f"only {len(cand)} same-regime analogs with realized forward windows.")

    # similarity weight (PCA distance) x recency
    dist = np.linalg.norm(Xc.loc[cand].values - x_now, axis=1)
    sigma = float(cfg["analog"]["similarity_sigma"])
    lam = float(cfg["analog"]["recency_decay_lambda"])
    w_sim = np.exp(-(dist ** 2) / (2 * sigma ** 2))
    age = (as_of - cand).days.values.astype(float)
    w = w_sim * np.exp(-lam * age)
    order = np.argsort(-w)[: args.topk]
    cand, w = cand[order], w[order]
    w = w / w.sum()
    print(f"analogs used: {len(cand)} (same regime, nearest in PCA space, recency-weighted)")

    # --- forward returns at analog dates -----------------------------------
    logret = np.log1p(rets)
    fwd = pd.DataFrame(index=cand, columns=rets.columns, dtype=float)
    ip = {d: i for i, d in enumerate(rets.index)}
    ridx = rets.index
    for t in cand:
        if t not in ip:
            continue
        i = ip[t]
        if i + H >= len(ridx):
            continue
        window = logret.iloc[i + 1: i + 1 + H]
        fwd.loc[t] = np.expm1(window.sum(min_count=1))

    # weighted expected forward move + hit-rate, per asset
    rows = []
    for a in rets.columns:
        col = fwd[a].astype(float)
        mask = col.notna().values
        if mask.sum() < 10:
            continue
        ww = w[mask]; ww = ww / ww.sum()
        vals = col.values[mask]
        exp_fwd = float(np.sum(ww * vals))
        hit = float(np.sum(ww * (vals > 0)))
        rows.append({"asset": a, "exp_fwd": exp_fwd, "hit": hit, "n": int(mask.sum())})
    tab = pd.DataFrame(rows).set_index("asset").sort_values("exp_fwd", ascending=False)

    def show(block, title, sign):
        print(f"\n{title}")
        for a, row in block.iterrows():
            attr = factor_attribution(rets[a], scores, as_of, args.reg_window, ATTRIB_PCS)
            top = sorted(attr.items(), key=lambda kv: -kv[1])[:2]
            fac = ", ".join(f"{names.get(k, k)} {v:.0%}" for k, v in top) if top else "n/a"
            conf = row["hit"] if sign > 0 else 1 - row["hit"]
            print(f"  {a:5} exp {row['exp_fwd']*100:+5.2f}%  "
                  f"conf {conf:0.0%} ({int(row['n'])} analogs)  | {fac}")

    show(tab.head(args.n_show), f"LONG candidates (highest expected {H}d move):", +1)
    show(tab.tail(args.n_show).iloc[::-1], f"SHORT candidates (lowest expected {H}d move):", -1)

    print("\n" + "=" * 76)
    print("READING")
    print("  exp = weighted-average forward move across the analogs.")
    print("  conf = share of analogs that agreed with the direction (hit-rate).")
    print("  factor % = share of the asset's recent variance driven by each macro PC.")
    print("  This is the CALL as-of the date. Whether the calls are actually right")
    print("  is Stage 2 (walk-forward backtest) -- do not trust it until validated.")
    print("=" * 76)


if __name__ == "__main__":
    main()
