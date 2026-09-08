"""
kernel_family.py -- three alternative kernels, tested as ONE FAMILY.

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.

EXPECTATION, WRITTEN FIRST
    Three nulls. Model 4 (8 Sep) showed that whatever selection skill the
    ranking has is confined to 2019-2026 and is not survivorship-robust. A
    better kernel cannot make a momentum artefact into something more. This
    family is run to CLOSE a question, not to find a model: does the similarity
    apparatus -- kernel, sigma, recency -- contribute anything at all over
    simply averaging every same-regime day?

WHY A FAMILY AND NOT THREE MODELS
    Run three and quote the best, and the selection problem that produced Model
    3's false 0.73 is back at small scale. The registered statistic is the
    BEST-OF-THREE observed Sharpe against the BEST-OF-THREE null. No single
    kernel is quoted on its own p-value. This is business plan section 3.4.1
    applied to itself.

THE THREE KERNELS -- everything else identical to model_1
    H=5, N=5, topk=100, same regime gate, same expanding refit. Only the weight
    function changes.

    K0  REGIME-ONLY, equal weight.   w = 1 for every same-regime candidate.
        The floor. What the incumbent effectively is, stated honestly: no
        similarity, no recency. If K0 matches model_1, the kernel does nothing.

    K1  SIMILARITY-ONLY, tight sigma.  w = exp(-d^2 / 2 sigma^2), sigma = 0.75
        (half the incumbent's 1.5), NO recency. The ceiling: does resemblance
        within a regime add anything? Prior: the no-decay control at sigma 1.5
        was indistinguishable from the incumbent (p 0.485). Tight sigma is the
        untested part.

    K2  MAHALANOBIS, incumbent sigma.  d^2 = (x - x_t)' S^-1 (x - x_t) with S
        the covariance of the same-regime candidate pool, then the incumbent
        kernel and recency. Tests whether Euclidean distance -- which lets PC1
        dominate -- is measuring similarity wrong.

    sigma = 0.75 for K1 is a single registered value, NOT swept. Sweeping it
    would make K1 a grid inside a family.

REGISTERED CRITERION
    F1  best-of-three Sharpe (ALL universe) exceeds the 95th percentile of the
        best-of-three block-sign null, i.e. family p < 0.05
    F2  the kernel achieving it also clears block p < 0.05 on the
        survivorship-controlled 35
    F3  and passes the chronological split at <= 3x

    All three or the family is null. A kernel that beats model_1 but fails F2
    or F3 is reported as "differs from incumbent, not a finding".

REGISTERED COMPARISON TO THE FLOOR
    Separately from F1-F3: K0 vs model_1, paired on the same rebalances. If
    |Sharpe difference| < 0.05 and the paired mean-spread difference is not
    significant at p < 0.05, the similarity apparatus is declared to add
    nothing measurable and the plan's description of the engine is simplified
    to "every same-regime day, equally weighted".

Run:
    python kernel_family.py --quick     # 200 permutations
    python kernel_family.py             # 2,000
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR
from src.analog_backtest import load_returns, CLUSTERING_PCS
from backtest_evidence import _fit_at, baskets, block_perm_p

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "kernel_family.md"
OUT_JSON = PROCESSED_DIR / "kernel_family.json"
H, N, TOPK, SIGMA_INC = 5, 5, 100, 1.5
SIGMA_TIGHT = 0.75


def walk_forward_kernel(cfg, scores, rets, kernel, lam, refit_every, start_pos,
                        min_analogs, min_cov, progress=None):
    """Identical to backtest_evidence.walk_forward except the weight function
    is injected. kernel(Xc_cand, x_now, ages) -> weights."""
    Xc = scores[CLUSTERING_PCS].values
    A = rets.shape[1]
    FWD = np.expm1(np.log1p(rets).rolling(H).sum().shift(-H).values)
    rebs = list(range(start_pos, len(scores.index) - H, H))
    last_fit, out, fit_pos = -10 ** 9, [], None
    for k_, pos in enumerate(rebs):
        if pos - last_fit >= refit_every or fit_pos is None:
            fit_pos, last_fit = pos, pos
        m_, lab_full = _fit_at(cfg, Xc, fit_pos)
        lab = lab_full[: pos + 1] if fit_pos == pos else m_.predict(Xc[: pos + 1])
        r_now, x_now = lab[-1], Xc[pos]
        cand = np.where((lab[:-1] == r_now) & (np.arange(pos) + H < pos))[0]
        if len(cand) < min_analogs:
            continue
        w = kernel(Xc[cand], x_now, (pos - cand).astype(float), lam)
        keep = np.argsort(-w)[:TOPK]
        cand, w = cand[keep], w[keep]
        if w.sum() <= 0:
            continue
        w = w / w.sum()
        fa = FWD[cand]; m = ~np.isnan(fa); cov = m.sum(axis=0)
        exp_fwd = np.full(A, np.nan)
        for j in range(A):
            if cov[j] >= min_cov:
                ww = w[m[:, j]]; ww = ww / ww.sum()
                exp_fwd[j] = np.sum(ww * fa[m[:, j], j])
        out.append((pos, exp_fwd, FWD[pos]))
        if progress and k_ % 200 == 0:
            print(f"      {progress} {k_}/{len(rebs)}", flush=True)
    return out


# ---- the three kernels, plus the incumbent for the paired comparison -------
def k_incumbent(X, x, ages, lam):
    d = np.linalg.norm(X - x, axis=1)
    return np.exp(-(d ** 2) / (2 * SIGMA_INC ** 2)) * np.exp(-lam * ages)


def k0_regime_only(X, x, ages, lam):
    return np.ones(len(X))


def k1_similarity_tight(X, x, ages, lam):
    d = np.linalg.norm(X - x, axis=1)
    return np.exp(-(d ** 2) / (2 * SIGMA_TIGHT ** 2))


def k2_mahalanobis(X, x, ages, lam):
    if len(X) < 10:
        return k_incumbent(X, x, ages, lam)
    S = np.cov(X, rowvar=False) + 1e-6 * np.eye(X.shape[1])
    Si = np.linalg.inv(S)
    diff = X - x
    d2 = np.einsum("ij,jk,ik->i", diff, Si, diff)
    return np.exp(-d2 / (2 * SIGMA_INC ** 2)) * np.exp(-lam * ages)


KERNELS = [("model_1 (incumbent)", k_incumbent),
           ("K0 regime-only", k0_regime_only),
           ("K1 similarity-only sigma=0.75", k1_similarity_tight),
           ("K2 mahalanobis", k2_mahalanobis)]


def spread_series(rec, uni):
    bk = baskets(rec, uni, N)
    return np.array([b["lr"] - b["sr"] for b in bk]), [b["pos"] for b in bk]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--start", default="2010-01-01")
    a = ap.parse_args()
    iters = 200 if a.quick else a.iters

    cfg = load_config()
    rng = np.random.default_rng(cfg["project"]["random_seed"])
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    rets = load_returns().reindex(scores.index)
    lam = float(cfg["analog"]["recency_decay_lambda"])
    dates = scores.index
    A = rets.shape[1]
    start = int(dates.get_indexer([pd.to_datetime(a.start)], method="bfill")[0])
    long_hist = rets.notna().sum().values >= 8 * 252
    ann = np.sqrt(52)

    print("=" * 74)
    print("KERNEL FAMILY -- three kernels, one family-level test")
    print("=" * 74)
    print(f"  expectation written first: three nulls. {iters} permutations.")

    res = {}
    for name, kfn in KERNELS:
        print(f"\n  running {name} ...")
        rec = walk_forward_kernel(cfg, scores, rets, kfn, lam, 20, start, 20, 10,
                                  progress=name[:8])
        row = {}
        for label, uni in (("ALL", np.ones(A, bool)), ("LONG-HISTORY", long_hist)):
            sp, pos = spread_series(rec, uni)
            sh = sp.mean() / sp.std() * ann if sp.std() else 0.0
            blk = max(2, int(round(len(sp) / 52)))
            p, exc, null = block_perm_p(sp, sh, rng, iters, blk)
            cut = len(sp) // 2
            e, l = sp[:cut].mean(), sp[cut:].mean()
            ratio = (max(abs(e), abs(l)) / min(abs(e), abs(l))
                     if min(abs(e), abs(l)) > 0 else float("inf"))
            row[label] = dict(n=len(sp), weekly=float(sp.mean()), sharpe=float(sh),
                              p=float(p), exc=int(exc), early=float(e),
                              late=float(l), ratio=float(ratio),
                              sign_ok=bool(np.sign(e) == np.sign(l)),
                              spreads=sp, pos=pos, null=null)
            print(f"    [{label:12}] n={len(sp)}  weekly {sp.mean()*100:+.3f}%  "
                  f"Sharpe {sh:+.2f}  p {p:.4f}  split {ratio:.2f}x")
        res[name] = row

    # ---- family-level test over K0,K1,K2 (incumbent excluded) ---------------
    fam = [k for k, _ in KERNELS[1:]]
    obs = {k: res[k]["ALL"]["sharpe"] for k in fam}
    best_k = max(obs, key=obs.get); best = obs[best_k]
    # best-of-3 null: for each iteration, max over the three kernels' nulls
    nulls = np.column_stack([res[k]["ALL"]["null"] for k in fam])
    best_null = nulls.max(axis=1)
    exc_f = int(np.sum(best_null >= best))
    p_fam = (exc_f + 1) / (iters + 1)
    F1 = p_fam < 0.05
    F2 = res[best_k]["LONG-HISTORY"]["p"] < 0.05
    F3 = (res[best_k]["ALL"]["sign_ok"] and res[best_k]["ALL"]["ratio"] <= 3
          and res[best_k]["LONG-HISTORY"]["sign_ok"]
          and res[best_k]["LONG-HISTORY"]["ratio"] <= 3)

    print("\n" + "=" * 74)
    print("FAMILY TEST -- best of K0/K1/K2 vs best-of-three null")
    print("=" * 74)
    for k in fam:
        print(f"  {k:32} Sharpe {obs[k]:+.2f}")
    print(f"  best: {best_k}  {best:+.2f}")
    print(f"  best-of-3 null: mean {best_null.mean():+.2f}  "
          f"95th pct {np.percentile(best_null, 95):+.2f}")
    print(f"  exceedances {exc_f}/{iters}   FAMILY p = {p_fam:.4f}")
    print(f"  F1 {F1}  F2 {F2}  F3 {F3}  -> "
          f"{'FINDING' if F1 and F2 and F3 else 'NULL -- reported, no kernel adopted'}")

    # ---- K0 vs incumbent, paired -------------------------------------------
    inc = res["model_1 (incumbent)"]["ALL"]; k0 = res["K0 regime-only"]["ALL"]
    common = sorted(set(inc["pos"]) & set(k0["pos"]))
    ia = {p: s for p, s in zip(inc["pos"], inc["spreads"])}
    ka = {p: s for p, s in zip(k0["pos"], k0["spreads"])}
    diff = np.array([ia[p] - ka[p] for p in common])
    t_paired = diff.mean() / (diff.std() / np.sqrt(len(diff))) if diff.std() else 0
    # sign-flip null on the paired difference
    fl = np.array([(diff * rng.choice([-1, 1], len(diff))).mean() for _ in range(iters)])
    p_pair = (np.sum(np.abs(fl) >= abs(diff.mean())) + 1) / (iters + 1)
    dS = inc["sharpe"] - k0["sharpe"]
    adds_nothing = abs(dS) < 0.05 and p_pair >= 0.05
    print("\n" + "=" * 74)
    print("K0 (regime-only) vs INCUMBENT, paired on the same rebalances")
    print("=" * 74)
    print(f"  Sharpe: incumbent {inc['sharpe']:+.2f}  K0 {k0['sharpe']:+.2f}  "
          f"diff {dS:+.2f}")
    print(f"  paired mean-spread diff {diff.mean()*100:+.4f}%/wk  p {p_pair:.4f}")
    print(f"  -> {'SIMILARITY APPARATUS ADDS NOTHING MEASURABLE. Plan description simplified to every same-regime day, equally weighted.' if adds_nothing else 'incumbent differs from the floor; kernel is doing something.'}")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %z")
    out = dict(run=ts, iters=iters, family_p=float(p_fam), best=best_k,
               best_sharpe=float(best), null_mean=float(best_null.mean()),
               null_p95=float(np.percentile(best_null, 95)),
               F1=bool(F1), F2=bool(F2), F3=bool(F3),
               k0_vs_incumbent=dict(dS=float(dS), p_paired=float(p_pair),
                                    adds_nothing=bool(adds_nothing)),
               kernels={k: {u: {kk: vv for kk, vv in d.items()
                                if kk not in ("spreads", "pos", "null")}
                            for u, d in res[k].items()} for k in res})
    OUT_JSON.write_text(json.dumps(out, indent=2))
    L = ["# Kernel family — result", "", f"*Run {ts}. {iters} permutations. "
         "Expectation written first: three nulls.*", "",
         "| kernel | ALL Sharpe | ALL p | LONG-HIST Sharpe | LONG-HIST p | split |",
         "|---|---|---|---|---|---|"]
    for k, _ in KERNELS:
        r = res[k]
        L.append(f"| {k} | {r['ALL']['sharpe']:+.2f} | {r['ALL']['p']:.4f} | "
                 f"{r['LONG-HISTORY']['sharpe']:+.2f} | {r['LONG-HISTORY']['p']:.4f} | "
                 f"{r['ALL']['ratio']:.2f}× |")
    L += ["", f"**Family test:** best of K0/K1/K2 = {best_k} at {best:+.2f}; "
              f"best-of-3 null mean {best_null.mean():+.2f}, 95th pct "
              f"{np.percentile(best_null,95):+.2f}; **family p = {p_fam:.4f}**. "
              f"F1 {F1} · F2 {F2} · F3 {F3} → "
              f"**{'finding' if F1 and F2 and F3 else 'null'}**.", "",
          f"**K0 vs incumbent, paired:** Sharpe diff {dS:+.2f}, paired p "
          f"{p_pair:.4f} → "
          f"{'the similarity apparatus adds nothing measurable' if adds_nothing else 'the kernel does something'}.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
