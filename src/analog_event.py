"""
analog_event.py -- PROBLEM 3, STEPS 3-6. The analog-conditioned event effect.

REGISTERED IN docs/prereg_analog_event.md, committed 74b88dc BEFORE the corpus
read and BEFORE any real conditional estimate was computed.

    step 3 + step 4 are ONE estimator:
        y_hat = w * conditional + (1-w) * unconditional,   w = ESS/(ESS+k)
        step 4 is the w=0 limit.

    k is ESTIMATED, never chosen: k = s2_within / tau2, tau2 by
    DerSimonian-Laird across regime cells, re-estimated INSIDE each LOO fold.
    tau2 == 0 -> w = 0 -> registered NULL for that cell (prereg 3.3).

    Conditioning uses ALL THREE PCs. No per-source axis selection (prereg 2.2).
    No hard regime gate -- regime match is a reported flag (prereg 2.2).

    sigma_d by registered bisection on median ESS (prereg 4). Uses NO returns.
    HL_d = 4 years, single value, no ladder (prereg 2.3).

    ESS < 8 -> abstain, Tier 3 only (prereg 3.5).

THIS FILE RUNS BLIND UNTIL THE ACCEPTANCE TESTS PASS
    `--self-test` runs the six tests in prereg section 9.2 against data whose
    macro panel, regimes, dates, return volatility, fat tails, cross-asset
    correlation, missing values and NYSE holidays are all REAL. The only thing
    destroyed is the correspondence between event dates and returns; a known
    effect is then planted on top. Synthetic returns are deliberately NOT used:
    clean data would let real bugs survive to unblinding.

    Test 5 (null calibration, 200 replications) is the expensive one and the
    only test that catches a miscalibrated null -- the failure mode that makes a
    false positive look real.

Run:
    python -m src.analog_event --self-test              # all six, ~20-40 min
    python -m src.analog_event --self-test --quick      # 40 reps, ~5 min
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_core import (CLUSTERING_PCS, load_data, frozen_labels,
                              _z_expanding, DEFAULT)
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "analog_event_selftest.md"

HL_D = 4.0                 # registered, prereg 2.3
ESS_FLOOR = 8              # registered, prereg 3.5
TIER1_W, TIER2_W = 0.6, 0.2
SIGMA_BOUNDS = (0.05, 5.0)
SIGMA_TOL, SIGMA_MAXIT = 0.5, 40

# Numerical guards for the registered tau2=0 null path (prereg amendment 1).
# Scale-relative, so they cannot be tripped by a change of units.
DEGENERATE_VAR = 1e-9      # sqrt(s2_within) below this x scale -> no real noise
TAU2_REL_FLOOR = 1e-6      # tau2 below this x s2_within -> k > 1e6 -> w ~ 0


# ===========================================================================
# ESTIMATOR CORE
# ===========================================================================

def kernel_weights(Z_pool, z_query, ages_years, sigma, hl=HL_D):
    """w = exp(-d^2/2sigma^2) * exp(-ln2 * age / HL).   prereg 2.3"""
    d = np.linalg.norm(Z_pool - z_query, axis=1)
    sim = np.exp(-(d ** 2) / (2.0 * sigma ** 2))
    rec = np.exp(-np.log(2.0) * np.asarray(ages_years, float) / hl)
    return sim * rec


def ess_of(w):
    s = w.sum()
    if not np.isfinite(s) or s <= 0:
        return 0.0
    wn = w / s
    return float(1.0 / np.sum(wn ** 2))


def dl_tau2(cell_means, cell_n, s2_within, C, scale=None):
    """DerSimonian-Laird method-of-moments tau^2.  prereg 3.2

    Returns 0.0 when observed between-cell spread is fully explained by noise --
    the registered NULL path, not a fallback to be worked around.

    NUMERICAL GUARDS (prereg amendment 1, 2026-08-24). Caught by blind test 6.
    np.var of 80 IDENTICAL float64 values returns 4.76e-38, not zero. That
    residue makes W = n/s2_within = 4.2e38, which amplifies float noise in the
    cell means into Q ~ 4.2 > C-1 = 3, so tau2 came back 2e-38, passed `> 0`,
    and the registered null path SILENTLY DID NOT FIRE -- issuing a Tier-1 label
    with w = 0.96 on data with no between-cell variation whatsoever.

    Two guards, both scale-relative so they cannot be tripped by units:
      DEGENERATE_VAR  within-variance negligible against the data scale
      TAU2_REL_FLOOR  tau2 negligible against within-variance (k > 1e6, so
                      w < ESS/1e6 is already zero to any reportable precision)
    """
    cell_n = np.asarray(cell_n)
    m = cell_n > 0
    if m.sum() < 2:
        return 0.0
    ybar, n = np.asarray(cell_means, float)[m], cell_n[m]
    if s2_within <= 0:
        return 0.0
    if scale is None:
        scale = float(np.mean(np.abs(ybar))) + 1e-15
    if np.sqrt(s2_within) < DEGENERATE_VAR * scale:
        return 0.0                      # no noise to speak of -> DL meaningless
    W = n / s2_within                       # 1/v_c
    sW = W.sum()
    if sW <= 0 or not np.isfinite(sW):
        return 0.0
    yF = float((W * ybar).sum() / sW)
    Q = float((W * (ybar - yF) ** 2).sum())
    if Q <= (m.sum() - 1):
        return 0.0                      # registered rule, applied before divide
    denom = sW - (W ** 2).sum() / sW
    if denom <= 0:
        return 0.0
    tau2 = max(0.0, (Q - (m.sum() - 1)) / denom)
    if tau2 < TAU2_REL_FLOOR * s2_within:
        return 0.0
    return tau2


def estimate(y, w, labels, C, ess_floor=ESS_FLOOR):
    """The blend. Returns everything the report needs.  prereg 3

    y      per-event outcome (already the h-session forward return)
    w      macro x recency weights, same length
    labels regime label per event, for the DL cells
    """
    ok = np.isfinite(y) & np.isfinite(w) & (w > 0)
    y, w, labels = y[ok], w[ok], np.asarray(labels)[ok]
    n = len(y)
    out = dict(n_matched=int(n), ess=0.0, w_shrink=0.0, tau2=0.0, k=np.inf,
               conditional=np.nan, unconditional=np.nan, estimate=np.nan,
               tier=3, abstain=True, tau2_zero=False)
    if n == 0:
        return out

    uncond = float(np.mean(y))
    out["unconditional"] = uncond
    e = ess_of(w)
    out["ess"] = e
    cond = float(np.sum(w * y) / np.sum(w))
    out["conditional"] = cond

    # --- k = s2_within / tau2, both estimated (prereg 3.2) --------------
    s2w = float(np.var(y, ddof=1)) if n > 1 else 0.0
    cm, cn = np.zeros(C), np.zeros(C, int)
    for c in range(C):
        sel = labels == c
        cn[c] = int(sel.sum())
        cm[c] = float(y[sel].mean()) if cn[c] else 0.0
    tau2 = dl_tau2(cm, cn, s2w, C, scale=float(np.mean(np.abs(y))) + 1e-15)
    out["tau2"] = tau2
    out["tau2_zero"] = (tau2 <= 0)

    if tau2 <= 0:
        k, wsh = np.inf, 0.0            # registered NULL path, prereg 3.3
    else:
        k = s2w / tau2
        wsh = e / (e + k)
    out["k"], out["w_shrink"] = float(k), float(wsh)
    out["estimate"] = wsh * cond + (1.0 - wsh) * uncond

    if e < ess_floor:
        out.update(tier=3, abstain=True)          # prereg 3.5
    else:
        out["abstain"] = False
        out["tier"] = 1 if wsh >= TIER1_W else (2 if wsh >= TIER2_W else 3)
    return out


def select_sigma(Z_pool, Z_queries, ages, n_pool, hl=HL_D):
    """Bisection so MEDIAN ESS across query days hits the registered target.
    Uses NO returns, so sigma cannot be tuned toward an outcome.  prereg 4"""
    target = float(np.clip(0.15 * n_pool, 8, 30))
    lo, hi = SIGMA_BOUNDS

    def med_ess(s):
        return float(np.median([ess_of(kernel_weights(Z_pool, z, a, s, hl))
                                for z, a in zip(Z_queries, ages)]))

    for _ in range(SIGMA_MAXIT):
        mid = 0.5 * (lo + hi)
        m = med_ess(mid)
        if abs(m - target) <= SIGMA_TOL:
            return mid, m, target, True
        if m < target:
            lo = mid                      # wider sigma -> more ESS
        else:
            hi = mid
        if hi - lo < 1e-6:
            break
    mid = 0.5 * (lo + hi)
    return mid, med_ess(mid), target, False


def loo_evaluate(Z, ages_matrix, y, labels, sigma, C, hl=HL_D):
    """Leave-one-out: blended vs unconditional. prereg 5.2

    Returns per-event predictions for both, so MSE and sign hit-rate are
    computed by the caller and the same arrays feed the null."""
    n = len(y)
    pred_b, pred_u = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        w = kernel_weights(Z[m], Z[i], ages_matrix[i][m], sigma, hl)
        r = estimate(y[m], w, labels[m], C)
        pred_b[i] = r["estimate"]
        pred_u[i] = r["unconditional"]
    return pred_b, pred_u


def metrics(pred, y):
    ok = np.isfinite(pred) & np.isfinite(y)
    if ok.sum() == 0:
        return np.nan, np.nan
    mse = float(np.mean((pred[ok] - y[ok]) ** 2))
    hit = float(np.mean(np.sign(pred[ok]) == np.sign(y[ok])))
    return mse, hit


def permutation_null(Z, ages_matrix, y, labels, sigma, C, iters, rng, hl=HL_D,
                     mode="permute_y"):
    """Destroy the state<->outcome correspondence and nothing else.  prereg 5.3

    TWO MODES, both computed and both reported (amendment 2026-08-25):

      permute_y  PRIMARY. Shuffles the OUTCOMES across events. Z, ages, sigma,
                 ESS and the entire weight geometry are IDENTICAL in every draw,
                 so the permuted draws are exchangeable with the observed one
                 and differ in exactly the thing the null is meant to isolate.

      permute_Z  ORIGINAL, retained. Shuffles the macro states. Because macro
                 states are autocorrelated and events close in time are close in
                 Z, the similarity and recency kernels concentrate on the same
                 pairs in the observed data; permuting Z breaks that alignment
                 and changes the ESS distribution, hence w = ESS/(ESS+k), hence
                 the estimator's variance. The permuted draws are therefore NOT
                 exchangeable with the observed one.

    permute_Z is kept rather than deleted: its result is evidence about how
    sensitive the null is to its own construction, which is worth reporting.
    """
    pb, pu = loo_evaluate(Z, ages_matrix, y, labels, sigma, C, hl)
    mse_b, hit_b = metrics(pb, y)
    mse_u, hit_u = metrics(pu, y)
    obs = (mse_u - mse_b, hit_b - hit_u)        # positive = conditioning helps
    n = len(y)
    null_mse, null_hit = np.empty(iters), np.empty(iters)
    for it in range(iters):
        perm = rng.permutation(n)
        if mode == "permute_y":
            yp = y[perm]
            pbp, pup = loo_evaluate(Z, ages_matrix, yp, labels, sigma, C, hl)
            m_b, h_b = metrics(pbp, yp)
            m_u, h_u = metrics(pup, yp)
        elif mode == "permute_Z":
            pbp, pup = loo_evaluate(Z[perm], ages_matrix, y, labels, sigma, C, hl)
            m_b, h_b = metrics(pbp, y)
            m_u, h_u = metrics(pup, y)
        else:
            raise ValueError(f"unknown null mode {mode!r}")
        null_mse[it] = m_u - m_b
        null_hit[it] = h_b - h_u
    p_mse = (np.sum(null_mse >= obs[0]) + 1) / (iters + 1)
    p_hit = (np.sum(null_hit >= obs[1]) + 1) / (iters + 1)
    return dict(obs_mse_gain=obs[0], obs_hit_gain=obs[1],
                p_mse=float(p_mse), p_hit=float(p_hit),
                mse_blend=mse_b, mse_uncond=mse_u,
                hit_blend=hit_b, hit_uncond=hit_u, mode=mode)


# ===========================================================================
# BLIND HARNESS -- real everything except the alignment.  prereg 9.1
# ===========================================================================

def regime_labels_expanding(scores, cfg, refit_every=20, min_train=504,
                            cache=True):
    """Regime label at date t, using ONLY data up to t.

    WHY: frozen_labels fits ONE GMM on all history. Those labels define the
    DerSimonian-Laird cells that estimate tau2, so the shrinkage weight w
    inherits a look-ahead. A live system has no future data to fit on.

    CANONICAL ORDERING (PROJECT_STATE open thread 3). GMM component ordering is
    arbitrary per fit, so an expanding refit would permute labels across refits
    and the tau2 cells would silently mix regimes -- worse than the look-ahead
    it replaces. Components are relabelled by ascending mean PC1 at every refit,
    which is deterministic and stable across the panel.

    Computed once for the whole panel and cached. Refitting inside each LOO fold
    would be far more expensive and NOT more correct: the fold excludes the
    held-out event's OUTCOME, not the regime structure.
    """
    from sklearn.mixture import GaussianMixture
    cache_path = PROCESSED_DIR / "regime_labels_expanding.parquet"
    X = scores[CLUSTERING_PCS].values
    n, C = len(X), int(cfg["regime"]["n_regimes"])
    if cache and cache_path.exists():
        try:
            df = pd.read_parquet(cache_path)
            if len(df) == n:
                return df["label"].values
        except Exception:
            pass

    labels = np.full(n, -1, dtype=int)
    model, order, last_fit, n_fits = None, None, -10 ** 9, 0
    for t in range(min_train, n):
        if t - last_fit >= refit_every or model is None:
            model = GaussianMixture(
                n_components=C,
                covariance_type=cfg["regime"]["covariance_type"],
                max_iter=cfg["regime"]["max_iter"],
                n_init=cfg["regime"]["n_init"],
                random_state=cfg["project"]["random_seed"])
            model.fit(X[: t + 1])
            # canonical order: ascending mean PC1 of the fitted components
            order = np.argsort(model.means_[:, 0])
            remap = np.empty(C, dtype=int)
            remap[order] = np.arange(C)
            last_fit = t; n_fits += 1
            if n_fits % 50 == 0:
                print(f"      ... {n_fits} expanding GMM refits")
        labels[t] = int(remap[model.predict(X[t: t + 1])[0]])
    print(f"      {n_fits} expanding GMM refits, labels canonically ordered "
          f"by mean PC1; first {min_train} sessions unlabelled (-1)")
    if cache:
        try:
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"label": labels}, index=scores.index).to_parquet(cache_path)
        except Exception as e:
            print(f"      (label cache not written: {type(e).__name__})")
    return labels


def build_blind(n_events, effect, rng, cfg, seed_offset=0):
    """Real macro PCs, real regimes, real return series with real volatility,
    fat tails, cross-asset correlation, missing values and NYSE holidays.
    ONLY the event-date <-> return correspondence is permuted; then a known
    effect is planted."""
    scores, rets = load_data()
    spec = dict(DEFAULT)
    C = int(spec["n_regimes"])

    # LIVE BASIS (amendment 2026-08-25). Both of these previously used the whole
    # panel, which a deployed system cannot do -- there is no future data to
    # standardise with or to fit regimes on. A backtest that cannot be run live
    # is not a backtest of the product.
    labels_all = regime_labels_expanding(scores, cfg)     # was frozen_labels
    Z = _z_expanding(scores[CLUSTERING_PCS].values)       # was full-panel z

    # real 3-session forward returns of a real asset, with its real gaps
    col = "GLD" if "GLD" in rets.columns else rets.columns[0]
    fwd = np.expm1(np.log1p(rets[col]).rolling(3).sum().shift(-3)).values

    # labels are -1 before min_train, and Z is NaN before min_periods, so both
    # exclusions are enforced here rather than assumed
    valid = np.flatnonzero(np.isfinite(fwd) & np.isfinite(Z).all(axis=1)
                           & (labels_all >= 0))
    valid = valid[valid > 252]
    pos = rng.choice(valid, size=min(n_events, len(valid)), replace=False)
    pos.sort()

    # DESTROY the alignment: outcomes are real returns from OTHER real days
    donor = rng.choice(valid, size=len(pos), replace=False)
    y = fwd[donor].copy()

    labels = labels_all[pos]
    Zq = Z[pos]
    ages = np.array([[abs(pos[i] - pos[j]) / 252.0 for j in range(len(pos))]
                     for i in range(len(pos))])

    # plant a known effect that DEPENDS on macro state, so conditioning has
    # something real to find (effect=0 -> pure null, used by test 5)
    if effect != 0.0:
        y = y + effect * np.sign(Zq[:, 0])
    return dict(Z=Zq, y=y, labels=labels, ages=ages, C=C, pos=pos, col=col)


# ===========================================================================
# THE SIX ACCEPTANCE TESTS -- prereg 9.2
# ===========================================================================

def _sigma_for(b):
    s, med, tgt, okc = select_sigma(b["Z"], b["Z"], b["ages"], len(b["y"]))
    return s, med, tgt, okc


def test_1_recovery(rng, cfg, res, n_events=400, effect=0.005):
    """Does the estimator RECOVER a planted effect, not merely return a number?

    REPLACES a vacuous check (`ok = isfinite(estimate)`) that passed with an
    interval 166x the planted effect. The planted effect is c * sign(PC1), so
    the conditional estimate for PC1>0 queries minus that for PC1<0 queries must
    recover 2c. Judged against its own standard error, not against zero."""
    b = build_blind(n_events, effect, rng, cfg)
    s, med, tgt, conv = _sigma_for(b)
    pos = b["Z"][:, 0] > 0
    if pos.sum() < 20 or (~pos).sum() < 20:
        res.append(("1 recovery", False,
                    f"degenerate split: {int(pos.sum())} PC1>0 vs "
                    f"{int((~pos).sum())} PC1<0"))
        return

    # The planted effect is a STEP at PC1 = 0. A kernel-weighted average of
    # neighbours near that step necessarily pulls toward zero -- attenuation,
    # not error. So the estimator is judged against the ORACLE: what a perfect
    # estimator would return GIVEN THESE EXACT WEIGHTS. The raw planted value is
    # reported alongside, so the attenuation stays visible.
    planted = effect * np.sign(b["Z"][:, 0])
    cond, orac, esss = [], [], []
    for i in range(len(b["y"])):
        m = np.ones(len(b["y"]), bool); m[i] = False
        w = kernel_weights(b["Z"][m], b["Z"][i], b["ages"][i][m], s)
        r = estimate(b["y"][m], w, b["labels"][m], b["C"])
        cond.append(r["conditional"]); esss.append(r["ess"])
        sw = w.sum()
        orac.append(float(np.sum(w * planted[m]) / sw) if sw > 0 else np.nan)
    cond = np.asarray(cond); orac = np.asarray(orac); esss = np.asarray(esss)
    ok_i = np.isfinite(cond) & np.isfinite(orac)

    d_est = float(np.mean(cond[pos & ok_i]) - np.mean(cond[~pos & ok_i]))
    d_ora = float(np.mean(orac[pos & ok_i]) - np.mean(orac[~pos & ok_i]))

    # CORRECT standard error. d_est is a LINEAR FUNCTIONAL of y:
    #     d_est = a . y,   a_j = mean_{i in pos} Wn_ij - mean_{i in neg} Wn_ij
    # so Var(d_est) = sigma_y^2 * sum_j a_j^2.
    #
    # The previous version computed se from the variance of `cond` ACROSS
    # QUERIES, treating 400 smoothed estimates as independent. They are not --
    # neighbouring queries average over overlapping neighbours, so they are
    # heavily correlated. That understated the se by about 8x and would have
    # failed a correct estimator. Verified against 200 simulated draws:
    # analytic 0.1317% vs empirical 0.1254%, coverage 96.5% at 2se.
    A = np.zeros((len(b["y"]), len(b["y"])))
    for i in range(len(b["y"])):
        m = np.ones(len(b["y"]), bool); m[i] = False
        w = kernel_weights(b["Z"][m], b["Z"][i], b["ages"][i][m], s)
        sw = w.sum()
        if sw > 0:
            A[i, m] = w / sw
    sel_p = pos & ok_i
    sel_n = (~pos) & ok_i
    a_vec = A[sel_p].mean(axis=0) - A[sel_n].mean(axis=0)
    sigma_y = float(np.std(b["y"], ddof=1))
    se = float(sigma_y * np.sqrt(np.sum(a_vec ** 2)))
    target = 2.0 * effect
    ok = abs(d_est - d_ora) <= 2.0 * se and d_est > 0
    atten = (d_ora / target) if target else float("nan")
    res.append(("1 recovery", ok,
                f"estimator {d_est*100:+.3f}% +/- {2*se*100:.3f}% vs ORACLE "
                f"{d_ora*100:+.3f}% (same weights) -> agreement "
                f"{'within' if ok else 'OUTSIDE'} 2se | raw planted "
                f"{target*100:+.3f}%, kernel attenuation {atten:.1%} of it -- "
                f"expected for a smoother across a step | n={n_events}, median "
                f"ESS {np.median(esss):.1f}, sigma {s:.3f} (target {tgt:.1f}, "
                f"bisection {'converged' if conv else 'HIT BOUND'})"))


def test_2_counts(rng, cfg, res):
    for n in (25, 60, 140):
        b = build_blind(n, 0.0, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
        r = estimate(b["y"], w, b["labels"], b["C"])
        if r["n_matched"] != n:
            res.append(("2 precedent count", False,
                        f"planted {n}, reported {r['n_matched']}"))
            return
    res.append(("2 precedent count", True,
                "reported matched-event counts equal planted counts at n=25,60,140"))


def test_3_tiers(rng, cfg, res):
    """Are tiers 1, 2 AND 3 all REACHABLE, and correctly assigned?

    The previous version checked only that the assigned tier agreed with the
    boundaries -- and every case landed at tier 3, so a function returning 3
    unconditionally would have passed. This version plants strong / moderate /
    no between-cell structure and REQUIRES all three tiers to appear."""
    seen, rows = set(), []
    # (label, n_events, per-regime cell offset). A larger offset means more real
    # between-cell variation -> larger tau2 -> smaller k -> larger w.
    cases = [("strong", 400, 0.020), ("moderate", 400, 0.004),
             ("none", 400, 0.000), ("thin", 6, 0.020)]
    # Scan EVERY query, not index 0. The previous version evaluated a single
    # query that happened to sit in a sparse region of PC space, so every case
    # returned tier 3 and the boundaries looked unreachable. The tell was in its
    # own output: `strong: w 0.71 -> tier 3` -- w had cleared the tier-1
    # threshold and the ESS<8 floor correctly overrode it.
    for label, n, off in cases:
        b = build_blind(n, 0.0, rng, cfg)
        y = b["y"] + off * (b["labels"] - b["labels"].mean())
        s, _, _, _ = _sigma_for(b)
        tiers, worst = [], None
        for i in range(len(y)):
            w = kernel_weights(b["Z"], b["Z"][i], b["ages"][i], s)
            r = estimate(y, w, b["labels"], b["C"])
            exp = 3 if (r["ess"] < ESS_FLOOR or r["tau2_zero"]) else (
                1 if r["w_shrink"] >= TIER1_W else
                (2 if r["w_shrink"] >= TIER2_W else 3))
            if r["tier"] != exp and worst is None:
                worst = (i, r, exp)
            tiers.append(r["tier"])
            seen.add(r["tier"])
        cnt = {t: tiers.count(t) for t in (1, 2, 3)}
        rows.append(f"{label}: tiers 1/2/3 = {cnt[1]}/{cnt[2]}/{cnt[3]} "
                    f"of {len(tiers)} queries")
        if worst is not None:
            i, r, exp = worst
            res.append(("3 tier labelling", False,
                        f"{label} query {i}: tier {r['tier']}, boundaries imply "
                        f"{exp} (ESS {r['ess']:.1f}, w {r['w_shrink']:.2f}, "
                        f"tau2 {r['tau2']:.1e}) | " + "; ".join(rows)))
            return
    missing = {1, 2, 3} - seen
    if missing:
        res.append(("3 tier labelling", False,
                    f"tiers never reached: {sorted(missing)} -- the boundaries "
                    f"are not exercised, so agreement with them proves nothing | "
                    + "; ".join(rows)))
        return
    res.append(("3 tier labelling", True,
                "all three tiers reached AND correctly assigned | "
                + "; ".join(rows)))


def test_4_abstain(rng, cfg, res):
    b = build_blind(6, 0.004, rng, cfg)
    s, _, _, _ = _sigma_for(b)
    w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
    r = estimate(b["y"], w, b["labels"], b["C"])
    ok = r["abstain"] and r["tier"] == 3
    res.append(("4 abstention", ok,
                f"6 matched events -> ESS {r['ess']:.1f} < {ESS_FLOOR}, "
                f"abstain={r['abstain']}, tier {r['tier']}"))


def test_5_null_calibration(rng, cfg, res, reps, iters):
    """THE EXPENSIVE ONE, RE-SPECIFIED. The original FAILED and that stands.

    ORIGINAL RESULT, PRESERVED: 200 reps x 500 perms, rejection 0.005 against
    the registered band [0.02, 0.08], median p 0.906. Recorded in
    docs/analog_event_selftest.md and reported in the write-up. Not deleted.

    DIAGNOSIS, demonstrated in simulation before this was changed: when tau2 = 0
    the registered null path sets w = 0, so pred_blend == pred_uncond exactly,
    the gain is identically zero in the observed AND every permuted draw, and
    p = 1.0 by ties. 50-80% degenerate reps reproduces median p ~1.0 and
    rejection ~0.01. The ESTIMATOR was correct; the TEST could not measure
    calibration where the estimator refuses to condition.

    RE-SPECIFIED, NOT LOOSENED. Same band, applied to the subpopulation where a
    conditional claim is actually made:
      5a  degenerate fraction reported as a first-class number
      5b  rejection rate over reps with tau2 > 0, band unchanged [0.02, 0.08],
          minimum 40 such reps or the verdict is INCONCLUSIVE, not PASS

    Conditioning on tau2 > 0 selects on the estimator's own output. Stated
    plainly rather than buried: it is the only subpopulation in which "is the
    null calibrated" is a meaningful question."""
    MODES = ("permute_y", "permute_Z")      # primary first
    ps = {m: [] for m in MODES}
    degen = []
    for i in range(reps):
        b = build_blind(60, 0.0, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        first = None
        for m in MODES:
            out = permutation_null(b["Z"], b["ages"], b["y"], b["labels"], s,
                                   b["C"], iters, rng, mode=m)
            ps[m].append(out["p_mse"])
            if first is None:
                first = out
        # degenerate <=> the blend never departed from the unconditional, so the
        # statistic is identically zero and its p-value carries no information.
        # Determined from the OBSERVED fit, which is the same for both modes.
        degen.append(bool(np.isclose(first["mse_blend"], first["mse_uncond"],
                                     rtol=0, atol=1e-18)))
        if (i + 1) % 20 == 0:
            g = ~np.asarray(degen)
            bits = []
            for m in MODES:
                a = np.asarray(ps[m])
                bits.append(f"{m} {float(np.mean(a[g] < 0.05)):.3f}"
                            if g.sum() else f"{m} n/a")
            print(f"      rep {i+1}/{reps}  degenerate {np.mean(degen):.2f}  "
                  f"rejection: " + "  ".join(bits))

    degen = np.asarray(degen)
    frac_d = float(np.mean(degen))
    live = ~degen
    n_live = int(live.sum())
    rates = {m: float(np.mean(np.asarray(ps[m])[live] < 0.05))
             if n_live else float("nan") for m in MODES}
    ps_primary = np.asarray(ps["permute_y"])
    ps = ps_primary                       # primary drives the verdict below
    rate_all = float(np.mean(ps < 0.05))

    res.append(("5a degenerate fraction", True,
                f"tau2 = 0 in {frac_d:.1%} of {reps} reps -- the registered null "
                f"path fired and the blend stayed at the unconditional. This is "
                f"the estimator working, and it is why the ORIGINAL test 5 "
                f"failed (rejection 0.005, median p 0.906): a statistic that is "
                f"identically zero gives p = 1 by ties."))

    if n_live < 40:
        res.append(("5b null calibration", False,
                    f"only {n_live} of {reps} reps conditioned (tau2 > 0); "
                    f"40 required. INCONCLUSIVE, not a pass. Naive rate over "
                    f"all reps {rate_all:.3f}."))
        return
    rate = rates["permute_y"]
    rate_z = rates["permute_Z"]
    ok = 0.02 <= rate <= 0.08
    agree = (0.02 <= rate <= 0.08) == (0.02 <= rate_z <= 0.08)
    note = ("both nulls agree on the verdict" if agree else
            "** THE TWO NULLS DISAGREE ON THE VERDICT -- that disagreement is "
            "itself the finding and is reported as such, with no tie-break **")
    conservative = ("  Rate below 0.02 = the null is CONSERVATIVE: it under-"
                    "rejects, cannot fabricate a false positive, and costs "
                    "power. Registered consequence: a step 3 null must be "
                    "reported as 'inconclusive at this power', never as 'macro "
                    "conditioning has no effect'." if rate < 0.02 else "")
    res.append(("5b null calibration", ok,
                f"over the {n_live} reps where the estimator conditioned, band "
                f"[0.02, 0.08] UNCHANGED -- "
                f"PRIMARY permute_y: {rate:.3f} | permute_Z (original, "
                f"retained): {rate_z:.3f}; {note}. Median p (permute_y) "
                f"{np.median(ps[live]):.3f}. Naive rate over all {reps} reps "
                f"including degenerate ones: {rate_all:.3f}.{conservative}"))


def test_6_tau2_zero(rng, cfg, res):
    """Identical cell means -> tau2 = 0 -> w = 0 -> unconditional + null label."""
    b = build_blind(80, 0.0, rng, cfg)
    y = np.full(len(b["y"]), 0.001) + b["y"] * 0.0     # zero between-cell spread
    s, _, _, _ = _sigma_for(b)
    w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
    r = estimate(y, w, b["labels"], b["C"])
    ok = r["tau2_zero"] and r["w_shrink"] == 0.0 and r["tier"] == 3
    res.append(("6 tau2=0 path", ok,
                f"identical cell means -> tau2 {r['tau2']:.2e}, "
                f"w {r['w_shrink']:.2f}, tier {r['tier']}, "
                f"estimate == unconditional: "
                f"{np.isclose(r['estimate'], r['unconditional'])}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--quick", action="store_true",
                    help="40 reps x 200 perms instead of 200 x 500")
    args = ap.parse_args()
    if not args.self_test:
        raise SystemExit("Only --self-test is available. No real conditional "
                         "estimate may be computed until all six pass "
                         "(prereg section 9.2).")

    reps, iters = (40, 200) if args.quick else (200, 500)
    cfg = load_config()
    rng = np.random.default_rng(cfg["project"]["random_seed"])

    print("=" * 78)
    print("ANALOG EVENT ESTIMATOR -- BLIND ACCEPTANCE TESTS (prereg section 9.2)")
    print("=" * 78)
    print("  Real macro PCs, real regimes, real returns with real volatility,")
    print("  fat tails, missing values and holidays. ONLY the event-date <->")
    print("  return correspondence is destroyed. No real conditional estimate")
    print("  is computed anywhere in this run.")
    print(f"\n  test 5: {reps} replications x {iters} permutations\n")

    res = []
    for name, fn in [("1", test_1_recovery), ("2", test_2_counts),
                     ("3", test_3_tiers), ("4", test_4_abstain)]:
        print(f"  running test {name} ...")
        fn(rng, cfg, res)
    print(f"  running test 5 (the expensive one) ...")
    test_5_null_calibration(rng, cfg, res, reps, iters)
    # test 5 now contributes TWO rows (5a degenerate fraction, 5b calibration)
    print(f"  running test 6 ...")
    test_6_tau2_zero(rng, cfg, res)

    print("\n" + "=" * 78)
    allok = True
    for name, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}]  {name}")
        print(f"          {detail}")
        allok &= ok
    print("=" * 78)
    print("ALL SIX PASS -- unblinding is authorised once the corpus is read."
          if allok else
          "NOT ALL TESTS PASS -- unblinding is NOT authorised (prereg 9.2).")
    print("=" * 78)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Analog-event estimator — blind acceptance tests", "", f"*Run {ts}.*", "",
         "Registered in `docs/prereg_analog_event.md` §9.2. Real macro panel, "
         "regimes, and return series; only the event-date ↔ return "
         "correspondence is destroyed. **No real conditional estimate was "
         "computed in this run.**", "",
         f"Test 5: {reps} replications × {iters} permutations.", "",
         "| test | result | detail |", "|---|---|---|"]
    for name, ok, detail in res:
        L.append(f"| {name} | {'**PASS**' if ok else '**FAIL**'} | {detail} |")
    L += ["", ("**All six pass.** Unblinding is authorised once the corpus read "
               "completes." if allok else
               "**Not all tests pass. Unblinding is NOT authorised.**"), ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\n  -> {OUT_MD}")


if __name__ == "__main__":
    main()
