"""
analog_core.py -- one parameterized engine, so all three pre-registered models
(and the live harness) run through identical code with different specs.

A spec is a dict:
    horizon     forward window in trading days
    sim_mode    'level'  (match on where the macro state IS)
                'trend'  (match on level AND recent direction = macro momentum)
    kernel      'gaussian' | 'exp'   (how analog distance -> weight)
    sigma       kernel width
    trend_window   lookback for the momentum block when sim_mode='trend'
    n_regimes   regime hard-gate count; defaults to config regime.n_regimes.
                Frozen model specs in config/models.yaml carry their own value
                and override this -- they are pre-registration evidence.
    half_life_years  recency half-life in YEARS. None (default) = no
                decay, identical to pre-2026-08-23 behaviour. Restores
                the 2026-08-18 locked design w = exp(-lam*age) * sim,
                lam = ln(2)/half_life. OPT-IN: frozen models omit it.
    topk        number of nearest analogs to weight
    nbasket     longs / shorts per side

Regime model is FROZEN (fit once on all history) -- the live-realistic setup;
the expanding-window no-look-ahead validity was already established in Stage 2.
"""
import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR

CLUSTERING_PCS = ["PC1", "PC2", "PC3"]
_CFG = load_config()
DEFAULT = dict(horizon=5, sim_mode="level", kernel="gaussian", sigma=1.5,
               trend_window=10, n_regimes=int(_CFG["regime"]["n_regimes"]),
               topk=100, nbasket=5, min_analogs=20, min_cov=10,
               half_life_years=None)


def load_data():
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    rets = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet")
    rets.index = pd.to_datetime(rets.index); rets = rets.sort_index().dropna(how="all")
    if np.nanmedian(np.abs(rets.to_numpy())) > 0.5:
        rets = rets.pct_change()
    rets = rets.reindex(scores.index)
    return scores, rets


def _z(a):
    mu = np.nanmean(a, axis=0); sd = np.nanstd(a, axis=0); sd[sd == 0] = 1.0
    return (a - mu) / sd


def frozen_labels(scores, spec, cfg):
    from sklearn.mixture import GaussianMixture
    gm = GaussianMixture(n_components=spec["n_regimes"],
                         covariance_type=cfg["regime"]["covariance_type"],
                         max_iter=cfg["regime"]["max_iter"], n_init=cfg["regime"]["n_init"],
                         random_state=cfg["project"]["random_seed"])
    return gm.fit_predict(scores[CLUSTERING_PCS].values)


def feature_matrix(scores, spec):
    lvl = _z(scores[CLUSTERING_PCS].values)
    if spec["sim_mode"] == "trend":
        d = scores[CLUSTERING_PCS].diff(spec["trend_window"]).values
        return np.hstack([lvl, _z(d)])          # NaN in first trend_window rows
    return lvl


def _kw(dist, spec, age_years=None):
    """Analog weight = similarity kernel x recency kernel.

    similarity: gaussian exp(-d^2/2s^2) or exponential exp(-d/s)
    recency:    exp(-lambda * age_years), lambda = ln(2)/half_life_years

    age_years is None, or spec has no half_life_years -> recency term is 1.0,
    which reproduces the pre-2026-08-23 behaviour EXACTLY. The frozen models in
    models.yaml carry no half_life_years and are therefore unaffected."""
    if spec["kernel"] == "exp":
        sim = np.exp(-dist / spec["sigma"])
    else:
        sim = np.exp(-(dist ** 2) / (2 * spec["sigma"] ** 2))
    hl = spec.get("half_life_years")
    if hl is None or age_years is None:
        return sim
    lam = np.log(2.0) / float(hl)
    return sim * np.exp(-lam * np.asarray(age_years, dtype=float))


def _forward(rets, H):
    return np.expm1(np.log1p(rets).rolling(H).sum().shift(-H).values)


def _expected_fwd(FWD, cand, w, min_cov, A):
    fa = FWD[cand]                              # (K, A)
    m = ~np.isnan(fa)
    w2 = w[:, None] * m
    den = w2.sum(axis=0)
    num = np.nansum(w2 * np.nan_to_num(fa), axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = num / den
    exp = np.where((den > 0) & (m.sum(axis=0) >= min_cov), ratio, np.nan)
    return exp


def backtest(scores, rets, spec, cfg, start="2010-01-01", do_perm=True, iters=1000):
    labels = frozen_labels(scores, spec, cfg)
    X = feature_matrix(scores, spec)
    H = spec["horizon"]
    FWD = _forward(rets, H)
    A = rets.shape[1]
    dates = scores.index
    start_pos = int(dates.get_indexer([pd.to_datetime(start)], method="bfill")[0])
    rebs = range(start_pos, len(dates) - H, H)
    rng = np.random.default_rng(cfg["project"]["random_seed"])

    spreads, hits, lr_, sr_ = [], [], [], []
    eligs = []
    for pos in rebs:
        r_now = labels[pos]
        x_now = X[pos]
        if np.isnan(x_now).any():
            continue
        idx = np.arange(pos)
        cand = idx[(labels[:pos] == r_now) & (idx + H < pos)]
        cand = cand[~np.isnan(X[cand]).any(axis=1)]
        if len(cand) < spec["min_analogs"]:
            continue
        dist = np.linalg.norm(X[cand] - x_now, axis=1)
        age = (pos - cand) / 252.0          # sessions -> years
        w = _kw(dist, spec, age)
        if len(cand) > spec["topk"]:
            keep = np.argsort(-w)[: spec["topk"]]
            cand, w = cand[keep], w[keep]
        w = w / w.sum()
        exp = _expected_fwd(FWD, cand, w, spec["min_cov"], A)
        realized = FWD[pos]
        ok = ~np.isnan(exp) & ~np.isnan(realized)
        elig = np.where(ok)[0]
        N = spec["nbasket"]
        if len(elig) < 2 * N:
            continue
        ranked = elig[np.argsort(-exp[elig])]
        L, S = ranked[:N], ranked[-N:]
        lr, sr = np.nanmean(realized[L]), np.nanmean(realized[S])
        spreads.append(lr - sr); lr_.append(lr); sr_.append(sr)
        hits.append(np.concatenate([realized[L] > 0, realized[S] < 0]).mean())
        eligs.append((elig, realized))

    if not spreads:
        return None
    spreads = np.array(spreads); hits = np.array(hits)
    lr_ = np.array(lr_); sr_ = np.array(sr_)
    ann = np.sqrt(52 / max(1, H // 5)) if H >= 5 else np.sqrt(52)   # scale by rebalance freq
    ann = np.sqrt(252 / H)                                          # ann. of ~(H-day) returns
    sharpe = spreads.mean() / spreads.std() * ann if spreads.std() else np.nan
    up, dn = spreads[spreads > 0], spreads[spreads < 0]
    payoff = up.mean() / abs(dn.mean()) if len(dn) and dn.mean() != 0 else np.nan
    per_yr = spreads.mean() * (252 / H)

    p = np.nan
    if do_perm:
        null = np.empty(iters)
        for it in range(iters):
            s = 0.0
            for elig, realized in eligs:
                pk = rng.permutation(elig)
                s += np.nanmean(realized[pk[:spec["nbasket"]]]) - \
                     np.nanmean(realized[pk[spec["nbasket"]:2 * spec["nbasket"]]])
            null[it] = s / len(eligs)
        p = (np.sum(null >= spreads.mean()) + 1) / (iters + 1)

    return dict(n=len(spreads), spread=spreads.mean(), per_yr=per_yr,
                sharpe=sharpe, hit=hits.mean(), payoff=payoff,
                weeks_pos=np.mean(spreads > 0), long_leg=lr_.mean(),
                short_leg=sr_.mean(), p=p)


def current_picks(scores, rets, spec, cfg, as_of=None):
    labels = frozen_labels(scores, spec, cfg)
    X = feature_matrix(scores, spec)
    H = spec["horizon"]; FWD = _forward(rets, H); A = rets.shape[1]
    dates = scores.index
    if as_of is None:
        pos = len(dates) - 1
    else:
        pos = int(dates.get_indexer([pd.to_datetime(as_of)], method="ffill")[0])
    r_now = labels[pos]; x_now = X[pos]
    idx = np.arange(pos)
    cand = idx[(labels[:pos] == r_now) & (idx + H < pos)]
    cand = cand[~np.isnan(X[cand]).any(axis=1)]
    dist = np.linalg.norm(X[cand] - x_now, axis=1)
    age = (pos - cand) / 252.0          # sessions -> years
    w = _kw(dist, spec, age)
    if len(cand) > spec["topk"]:
        keep = np.argsort(-w)[: spec["topk"]]; cand, w = cand[keep], w[keep]
    w = w / w.sum()
    exp = _expected_fwd(FWD, cand, w, spec["min_cov"], A)
    assets = np.array(rets.columns)
    ok = ~np.isnan(exp)
    ranked = np.where(ok)[0][np.argsort(-exp[ok])]
    N = spec["nbasket"]
    longs = [(assets[i], float(exp[i])) for i in ranked[:N]]
    shorts = [(assets[i], float(exp[i])) for i in ranked[-N:]]
    return dict(as_of=str(dates[pos].date()), regime=int(r_now),
                n_analogs=len(cand), longs=longs, shorts=shorts)
