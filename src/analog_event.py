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

from src.analog_core import CLUSTERING_PCS, load_data, frozen_labels, DEFAULT
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


def permutation_null(Z, ages_matrix, y, labels, sigma, C, iters, rng, hl=HL_D):
    """Shuffle macro weights across events, preserving group sizes and every
    return path, destroying only state<->outcome correspondence.  prereg 5.3"""
    pb, pu = loo_evaluate(Z, ages_matrix, y, labels, sigma, C, hl)
    mse_b, hit_b = metrics(pb, y)
    mse_u, hit_u = metrics(pu, y)
    obs = (mse_u - mse_b, hit_b - hit_u)        # positive = conditioning helps
    n = len(y)
    null_mse, null_hit = np.empty(iters), np.empty(iters)
    for it in range(iters):
        perm = rng.permutation(n)
        Zp = Z[perm]
        pbp, pup = loo_evaluate(Zp, ages_matrix, y, labels, sigma, C, hl)
        m_b, h_b = metrics(pbp, y)
        m_u, h_u = metrics(pup, y)
        null_mse[it] = m_u - m_b
        null_hit[it] = h_b - h_u
    p_mse = (np.sum(null_mse >= obs[0]) + 1) / (iters + 1)
    p_hit = (np.sum(null_hit >= obs[1]) + 1) / (iters + 1)
    return dict(obs_mse_gain=obs[0], obs_hit_gain=obs[1],
                p_mse=float(p_mse), p_hit=float(p_hit),
                mse_blend=mse_b, mse_uncond=mse_u,
                hit_blend=hit_b, hit_uncond=hit_u)


# ===========================================================================
# BLIND HARNESS -- real everything except the alignment.  prereg 9.1
# ===========================================================================

def build_blind(n_events, effect, rng, cfg, seed_offset=0):
    """Real macro PCs, real regimes, real return series with real volatility,
    fat tails, cross-asset correlation, missing values and NYSE holidays.
    ONLY the event-date <-> return correspondence is permuted; then a known
    effect is planted."""
    scores, rets = load_data()
    spec = dict(DEFAULT)
    labels_all = frozen_labels(scores, spec, cfg)
    C = int(spec["n_regimes"])

    Z = scores[CLUSTERING_PCS].values
    Z = (Z - np.nanmean(Z, axis=0)) / np.nanstd(Z, axis=0)

    # real 3-session forward returns of a real asset, with its real gaps
    col = "GLD" if "GLD" in rets.columns else rets.columns[0]
    fwd = np.expm1(np.log1p(rets[col]).rolling(3).sum().shift(-3)).values

    valid = np.flatnonzero(np.isfinite(fwd) & np.isfinite(Z).all(axis=1))
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


def test_1_recovery(rng, cfg, res):
    b = build_blind(120, 0.005, rng, cfg)
    s, med, tgt, _ = _sigma_for(b)
    w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
    r = estimate(b["y"], w, b["labels"], b["C"])
    se = np.std(b["y"], ddof=1) / np.sqrt(max(1, r["ess"]))
    lo, hi = r["estimate"] - 2 * se, r["estimate"] + 2 * se
    ok = np.isfinite(r["estimate"])
    res.append(("1 recovery", ok,
                f"estimate {r['estimate']*100:+.3f}% +/- {2*se*100:.3f}%, "
                f"ESS {r['ess']:.1f}, sigma {s:.3f} (median ESS {med:.1f} vs "
                f"target {tgt:.1f})"))


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
    seen, rows = set(), []
    for n in (10, 20, 40, 80, 160):
        b = build_blind(n, 0.004, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        w = kernel_weights(b["Z"], b["Z"][0], b["ages"][0], s)
        r = estimate(b["y"], w, b["labels"], b["C"])
        seen.add(r["tier"])
        rows.append(f"n={n}: ESS {r['ess']:.1f} w {r['w_shrink']:.2f} "
                    f"tier {r['tier']}")
        exp = 3 if (r["ess"] < ESS_FLOOR or r["tau2_zero"]) else (
            1 if r["w_shrink"] >= TIER1_W else
            (2 if r["w_shrink"] >= TIER2_W else 3))
        if r["tier"] != exp:
            res.append(("3 tier labelling", False,
                        f"n={n}: tier {r['tier']}, boundaries imply {exp}"))
            return
    res.append(("3 tier labelling", True,
                "tier matches the w/ESS boundaries at every n | " + "; ".join(rows)))


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
    """THE EXPENSIVE ONE. No effect planted -> p should be ~uniform and the
    rejection rate at alpha=0.05 must land in [0.02, 0.08]."""
    ps = []
    for i in range(reps):
        b = build_blind(60, 0.0, rng, cfg)
        s, _, _, _ = _sigma_for(b)
        out = permutation_null(b["Z"], b["ages"], b["y"], b["labels"], s,
                               b["C"], iters, rng)
        ps.append(out["p_mse"])
        if (i + 1) % 20 == 0:
            r = np.mean(np.array(ps) < 0.05)
            print(f"      rep {i+1}/{reps}  rejection so far {r:.3f}")
    ps = np.array(ps)
    rate = float(np.mean(ps < 0.05))
    ok = 0.02 <= rate <= 0.08
    res.append(("5 null calibration", ok,
                f"{reps} reps x {iters} perms, no effect planted: "
                f"rejection at alpha=0.05 is {rate:.3f} "
                f"(registered band [0.02, 0.08]); median p {np.median(ps):.3f}"))


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
