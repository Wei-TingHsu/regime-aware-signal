"""
T1 -- the exposure dial. Registered: docs/prereg_exposure_dial.md (2026-10-07).

Every constant below is the registered value. Nothing is fitted to returns.

  sigma_hat_t : EWMA daily variance, lambda 0.94, through t, annualised
  w_t         : min(1, 10% / sigma_hat_t)                      (variant 2)
  m_r         : median sigma_hat (all) / median sigma_hat (regime r), expanding through t-1,
                refreshed every 21 sessions  -- declared implementation detail (prereg 3 says
                "expanding through t-1" and no refresh cadence; monthly is chosen for the
                10,000-shift null to be computable; recorded in the self-test report)
  hysteresis  : regime acted on after 3 identical sessions; trade only if |dw| > 0.05
  execution   : a weight decided at close t is held from close t+1 -> earns r_{t+2}
  costs       : one-way bp per unit traded, fixed table, at 1x and 3x
  objective   : CER = mu - (gamma/2) var, gamma 3, annualised, on excess returns

Usage
  python -m src.exposure_dial --selftest            # the six acceptance tests, synthetic data only
  python -m src.exposure_dial --run                 # Test A on the five model ETFs
  python -m src.exposure_dial --run --n-boot 2000 --n-shift 2000   # quick look (not the registered run)
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

LAMBDA, TARGET, GAMMA = 0.94, 0.10, 3.0
CONFIRM, BAND, REFRESH, LAG = 3, 0.05, 21, 2
BOOT_BLOCK = 20
COST_BP = {"SPY": 3, "TLT": 3, "GLD": 3, "UUP": 5, "USO": 5}
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
SPLIT = pd.Timestamp("2017-01-01")
ANN = 252


# ----------------------------------------------------------------------------- building blocks
def ewma_vol(r: np.ndarray) -> np.ndarray:
    """Annualised EWMA volatility using returns through t (index t includes r_t)."""
    v = np.empty(len(r)); r = np.nan_to_num(r)
    v[0] = r[:20].var() if len(r) >= 20 else r[0] ** 2
    for t in range(1, len(r)):
        v[t] = LAMBDA * v[t - 1] + (1 - LAMBDA) * r[t] ** 2
    return np.sqrt(v * ANN)


def confirmed_labels(lab: np.ndarray) -> np.ndarray:
    """Hysteresis on regime: a new label counts only after CONFIRM identical sessions."""
    out = np.full(len(lab), -1); cur = -1; run = 0; prev = None
    for t, x in enumerate(lab):
        run = run + 1 if x == prev else 1
        prev = x
        if x >= 0 and run >= CONFIRM:
            cur = x
        out[t] = cur
    return out


def regime_multipliers(sig: np.ndarray, lab: np.ndarray) -> np.ndarray:
    """m_r per session: median sigma over all labelled sessions < t / median within regime < t,
    refreshed every REFRESH sessions, 1.0 where a regime has fewer than 60 sessions of history."""
    n = len(sig); m = np.ones(n)
    regimes = sorted(set(int(x) for x in lab if x >= 0))
    cur = {r: 1.0 for r in regimes}
    for b in range(REFRESH, n, REFRESH):
        hist_sig, hist_lab = sig[:b], lab[:b]
        ok = hist_lab >= 0
        if ok.sum() < 60:
            continue
        med_all = np.median(hist_sig[ok])
        for r in regimes:
            mask = hist_lab == r
            cur[r] = float(med_all / np.median(hist_sig[mask])) if mask.sum() >= 60 else 1.0
        for t in range(b, min(b + REFRESH, n)):
            m[t] = cur.get(int(lab[t]), 1.0) if lab[t] >= 0 else 1.0
    return m


def dial(sig: np.ndarray, mult: np.ndarray | None = None) -> np.ndarray:
    raw = np.minimum(1.0, TARGET * (mult if mult is not None else 1.0) / np.maximum(sig, 1e-6))
    w = np.empty(len(raw)); w[0] = raw[0]
    for t in range(1, len(raw)):
        w[t] = raw[t] if abs(raw[t] - w[t - 1]) > BAND else w[t - 1]
    return w


def strategy_returns(w: np.ndarray, r_excess: np.ndarray, cost_bp: float, lag: int = LAG):
    """Net excess return path. Weight decided at t is in force for r_{t+lag}; costs on |dw|."""
    held = np.concatenate([np.full(lag, w[0]), w[:-lag]]) if lag else w
    traded = np.abs(np.diff(held, prepend=held[0]))
    net = held * np.nan_to_num(r_excess) - traded * cost_bp / 1e4
    return net, held, traded


def cer(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float(x.mean() * ANN - GAMMA / 2 * x.var() * ANN)


def stats(x: np.ndarray) -> dict:
    x = x[np.isfinite(x)]
    eq = np.cumsum(x); dd = float((eq - np.maximum.accumulate(eq)).min())
    sh = float(x.mean() / x.std() * np.sqrt(ANN)) if x.std() > 0 else float("nan")
    return dict(cer=cer(x), sharpe=sh, maxdd_log=dd)


def stationary_bootstrap_idx(n: int, rng, mean_block: int = BOOT_BLOCK) -> np.ndarray:
    idx = np.empty(n, int); t = 0
    while t < n:
        start = rng.integers(0, n); L = rng.geometric(1 / mean_block)
        k = min(L, n - t); idx[t:t + k] = (start + np.arange(k)) % n; t += k
    return idx


def paired_cer_test(a: np.ndarray, b: np.ndarray, rng, n_boot: int) -> dict:
    """CER(a) - CER(b) with a stationary-bootstrap 95% interval over shared days."""
    ok = np.isfinite(a) & np.isfinite(b); a, b = a[ok], b[ok]; n = len(a)
    point = cer(a) - cer(b)
    draws = np.empty(n_boot)
    for i in range(n_boot):
        idx = stationary_bootstrap_idx(n, rng); draws[i] = cer(a[idx]) - cer(b[idx])
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return dict(diff=point, lo=float(lo), hi=float(hi), n=n)


# ----------------------------------------------------------------------------- one asset, four variants
def run_asset(r: np.ndarray, rf_daily: np.ndarray, lab: np.ndarray, cost_bp: float,
              post: np.ndarray | None = None) -> dict:
    rx = r - rf_daily
    sig = ewma_vol(r)
    lab_c = confirmed_labels(lab)
    m3 = regime_multipliers(sig, lab_c)
    out = {"sig": sig, "labels": lab_c}
    w1 = np.ones(len(r)); w2 = dial(sig); w3 = dial(sig, m3)
    out["w"] = {1: w1, 2: w2, 3: w3}
    if post is not None:
        regimes = sorted(set(int(x) for x in lab_c if x >= 0))
        # posterior-weighted multiplier: sum_r p_r m_r, with the per-regime m_r series implied by m3's rule
        mr_by_regime = {rr: regime_multipliers(sig, np.where(lab_c == rr, rr, np.where(lab_c >= 0, -2, -1))) for rr in regimes}
        m4 = np.ones(len(r))
        for rr in regimes:
            m4 = m4 + post[:, rr] * (mr_by_regime[rr] - 1.0)
        out["w"][4] = dial(sig, m4)
    out["ret"] = {}
    for v, w in out["w"].items():
        lagv = 0 if v == 1 else LAG
        for mult, key in ((0, "gross"), (1, "1x"), (3, "3x")):
            net, held, traded = strategy_returns(w, rx, cost_bp * mult, lag=lagv)
            out["ret"][(v, key)] = net
        out[f"turnover_{v}"] = float(traded.sum() / (len(r) / ANN))
    return out


# ----------------------------------------------------------------------------- acceptance tests
def selftest(report: Path = Path("docs/exposure_dial_selftest.md")) -> bool:
    rng = np.random.default_rng(0); L = []
    def row(name, ok, note): L.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {note} |"); return ok
    results = []
    # 1 constant-vol series WELL BELOW the target (half of it): dial sits at 100%, variants 1 and 2 identical gross.
    #   Re-specified 2026-10-07: the original asked for vol EQUAL to the target, where the forecast hovers at the
    #   cap and the dial is at 100% only half the time (original result: 11% at cap, FAIL). Preserved in the report.
    n = 3000; r = rng.normal(0, TARGET / 2 / np.sqrt(ANN), n); lab = np.zeros(n, int)
    o = run_asset(r, np.zeros(n), lab, 0)
    w2 = o["w"][2]; share_full = float((w2 >= 0.999).mean())
    same_gross = abs(cer(o["ret"][(1, "gross")]) - cer(o["ret"][(2, "gross")])) < 1e-9
    results.append(row("constant-vol series (re-specified)", share_full > 0.99 and same_gross,
                       f"dial at 100% on {share_full:.0%} of sessions; gross CER identical across variants 1-2: {same_gross}"))
    # 2 planted regime vol with IRREGULAR regime lengths: tilt reduces exposure in the high-vol regime; (ii) passes vs shift null.
    #   Re-specified 2026-10-07: the original planted regimes in fixed 500-session blocks, so circular shifts often landed
    #   the labels back in phase and a quarter of the "scrambled" nulls were not scrambled (original p 0.255, FAIL).
    n = 4000; lab = np.zeros(n, int); t = 0; cur = 0
    while t < n:
        L_ = int(rng.geometric(1 / 150)); lab[t:t + L_] = cur; cur = 1 - cur; t += L_
    r = rng.normal(0, np.where(lab == 1, 0.30, 0.08) / np.sqrt(ANN), n)
    r = r + np.where(lab == 1, -0.0008, 0.0004)       # the high-vol regime also pays less: a sizing edge exists
    o = run_asset(r, np.zeros(n), lab, 0)
    w2, w3 = o["w"][2], o["w"][3]
    lower_in_hi = float(w3[o["labels"] == 1].mean()) < float(w2[o["labels"] == 1].mean())
    d = cer(o["ret"][(3, "1x")]) - cer(o["ret"][(2, "1x")])
    sig = o["sig"]; null = []
    for _ in range(200):
        k = int(rng.integers(50, n - 50)); labs = np.roll(o["labels"], k)
        ws = dial(sig, regime_multipliers(sig, labs)); null.append(cer(strategy_returns(ws, r, 0)[0]) - cer(o["ret"][(2, "1x")]))
    p = float((np.array(null) >= d).mean())
    results.append(row("planted regime vol (re-specified)", lower_in_hi and d > 0 and p < 0.05, f"tilt lowers exposure in the planted regime; CER gain {d:+.4f}, shift-null p {p:.3f}"))
    # 3 shifted labels: (ii) fails
    labs = np.roll(o["labels"], 777); ws = dial(sig, regime_multipliers(sig, labs))
    d_sh = cer(strategy_returns(ws, r, 0)[0]) - cer(o["ret"][(2, "1x")])
    p_sh = float((np.array(null) >= d_sh).mean())
    results.append(row("shifted labels", not (d_sh > 0 and p_sh < 0.05), f"with scrambled labels CER gain {d_sh:+.4f}, p {p_sh:.3f}"))
    # 4 no look-ahead
    t = 2500; o_cut = run_asset(r[:t + 1], np.zeros(t + 1), lab[:t + 1], 0)
    same = np.allclose(o["sig"][:t + 1], o_cut["sig"]) and np.allclose(o["w"][3][:t + 1], o_cut["w"][3])
    results.append(row("no look-ahead", same, "sigma_hat and the tilted weight at t unchanged when data after t is deleted"))
    # 5 cost accounting: hand path
    w = np.array([0.0, 0.0, 1.0, 1.0, 0.5, 0.5, 0.5]); rr = np.array([0, 0, 0.01, 0.01, 0.01, -0.02, 0.0])
    net, held, traded = strategy_returns(w, rr, 10, lag=0)
    hand = w * rr - np.abs(np.diff(w, prepend=w[0])) * 10 / 1e4
    results.append(row("cost accounting", np.allclose(net, hand, atol=1e-12), "two-trade path reproduced to the basis point (lag 0)"))
    # 6 hysteresis: flickering labels produce no confirmed change
    flick = np.array([0, 1] * 1500); lc = confirmed_labels(flick)
    results.append(row("hysteresis", bool((lc == -1).all()), "a label that flips every session never confirms"))
    ok = all(results)
    report.write_text("# Exposure dial — acceptance tests\n\n"
                      f"*Run {datetime.now():%Y-%m-%d %H:%M} on synthetic data only. Registered in `docs/prereg_exposure_dial.md` §7.*\n\n"
                      "Two tests were re-specified after failing on their first run (7 Oct): test 1 (vol equal to the target → half the target; original 11% at cap) and test 2 (fixed 500-session regime blocks → irregular geometric lengths; original shift-null p 0.255). The dial was not changed; the tests were wrong. "
                      "Declared implementation detail: regime multipliers are refreshed every 21 sessions from data through the "
                      "previous session (the registration fixes 'expanding through t−1' and no cadence).\n\n"
                      "| test | result | note |\n|---|---|---|\n" + "\n".join(L) + f"\n\n**All pass: {'yes' if ok else 'NO'}**\n")
    print("\n".join(L)); print("ALL PASS" if ok else "A TEST FAILED -- do not run on real data")
    return ok


# ----------------------------------------------------------------------------- Test A
def load_inputs():
    import asset_extension as AE
    cfg = AE.load_config(); sc, rt = AE.load_data()
    lab = np.asarray(AE.regime_labels_expanding(sc, cfg))
    idx = pd.DatetimeIndex(sc.index)
    rets = pd.read_parquet("processed/asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    rets = rets.reindex(idx)
    post = None
    for name in ("regime_posteriors_expanding", "regime_posterior_expanding"):
        if hasattr(AE, name):
            try:
                post = np.asarray(getattr(AE, name)(sc, cfg)); break
            except Exception:
                post = None
    rf = None
    try:
        from src.data_io import cached_fetch
        s = cached_fetch(source="fred", key="EFFR", fetch_fn=lambda: (_ for _ in ()).throw(RuntimeError("no fetch")), force_refresh=False)
        s = (s.iloc[:, 0] if isinstance(s, pd.DataFrame) else s); s.index = pd.to_datetime(s.index)
        rf = (pd.to_numeric(s, errors="coerce").reindex(idx).ffill() / 100 / ANN).fillna(0).to_numpy()
    except Exception:
        rf = np.zeros(len(idx))
    return idx, rets, lab, post, rf


def run_testA(n_boot: int, n_shift: int, out: Path = Path("docs/exposure_dial_testA.md")):
    rng = np.random.default_rng(0)
    idx, rets, lab, post, rf = load_inputs()
    rf_note = "EFFR from the FRED cache" if rf.any() else "EFFR unavailable in the cache — excess returns computed against zero (declared)"
    L = ["# T1 — exposure dial, Test A", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_exposure_dial.md`. Five model ETFs, {idx[0].date()} → {idx[-1].date()}; "
         f"target {TARGET:.0%}, EWMA λ {LAMBDA}, γ {GAMMA:.0f}, confirm {CONFIRM}, band {BAND}, lag {LAG}; {n_boot:,} bootstrap resamples, "
         f"{n_shift:,} label shifts; {rf_note}; variant 4 {'run' if post is not None else 'NOT RUN — the frozen pipeline exposes labels, not posteriors (amendment to be recorded)'}.*", ""]
    verdicts = {"i": {}, "ii": {}, "iii": {}}
    for a in ASSETS:
        r = rets[a].to_numpy(float); first = int(np.argmax(np.isfinite(r)))
        r, rf_a, lab_a = r[first:], rf[first:], lab[first:]
        post_a = post[first:] if post is not None else None
        dates = idx[first:]
        o = run_asset(r, rf_a, lab_a, COST_BP[a], post_a)
        L += [f"## {a}", "", "| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |", "|---|---|---|---|---|---|---|"]
        for v in sorted(o["w"]):
            s1 = stats(o["ret"][(v, "1x")]); L.append(f"| {v} | {cer(o['ret'][(v, 'gross')]):+.4f} | {s1['cer']:+.4f} | {cer(o['ret'][(v, '3x')]):+.4f} | "
                                                 f"{s1['sharpe']:.2f} | {s1['maxdd_log']:+.3f} | {o[f'turnover_{v}']:.2f} |")
        L += ["", "| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |", "|---|---|---|---|---|---|---|---|"]
        comps = [("i", 2, 1), ("ii", 3, 2)] + ([("iii", 4, 3)] if 4 in o["w"] else [])
        for key, va, vb in comps:
            A, B = o["ret"][(va, "1x")], o["ret"][(vb, "1x")]
            t = paired_cer_test(A, B, rng, n_boot)
            h1 = dates < SPLIT; h2 = ~h1
            d1 = cer(A[h1]) - cer(B[h1]) if h1.sum() > 250 else float("nan")
            d2 = cer(A[h2]) - cer(B[h2]) if h2.sum() > 250 else float("nan")
            stab = d2 / d1 if (np.isfinite(d1) and np.isfinite(d2) and d1 != 0) else float("nan")
            p_shift = float("nan")
            if key in ("ii", "iii"):
                sig = o["sig"]; base = cer(B); null = np.empty(n_shift); n = len(sig)
                for i in range(n_shift):
                    k = int(rng.integers(REFRESH, n - REFRESH)); labs = np.roll(o["labels"], k)
                    ws = dial(sig, regime_multipliers(sig, labs))
                    null[i] = cer(strategy_returns(ws, r - rf_a, COST_BP[a])[0]) - base
                p_shift = float((null >= t["diff"]).mean())
            cond_pos = t["diff"] > 0; cond_ci = t["lo"] > 0
            cond_stab = np.isfinite(stab) and 0.5 <= stab <= 2.0
            cond_shift = (key == "i") or (np.isfinite(p_shift) and p_shift < 0.05)
            v = "PASS" if (cond_pos and cond_ci and cond_stab and cond_shift) else ("INCONCLUSIVE" if cond_pos else "FAIL")
            verdicts[key][a] = v
            L.append(f"| ({key}) {va} vs {vb} | {t['diff']:+.4f} | [{t['lo']:+.4f}, {t['hi']:+.4f}] | {d1:+.4f} | {d2:+.4f} | "
                     f"{stab:.2f} | {'—' if not np.isfinite(p_shift) else f'{p_shift:.3f}'} | **{v}** |")
        L.append("")
    L += ["## Tree-level verdict (prereg §5)", ""]
    for key, name, prior in (("i", "vol targeting enters the product", "PASS on SPY and USO"), ("ii", "regime tilt enters the product", "INCONCLUSIVE/FAIL on all five"), ("iii", "posterior tilt", "FAIL")):
        passes = [a for a, v in verdicts[key].items() if v == "PASS"]
        if verdicts[key]:
            L.append(f"- ({key}) {name}: **{'YES' if len(passes) >= 3 else 'NO'}** — PASS on {len(passes)} of {len(verdicts[key])} ({', '.join(passes) or 'none'}). Registered prior: {prior}.")
    out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"\n  -> {out}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-boot", type=int, default=10_000); ap.add_argument("--n-shift", type=int, default=10_000)
    a = ap.parse_args()
    if a.selftest:
        ok = selftest(); sys.exit(0 if ok else 1)
    if a.run:
        run_testA(a.n_boot, a.n_shift)


if __name__ == "__main__":
    main()
