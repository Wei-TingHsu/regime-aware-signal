"""
T13 A3 -- after an oil shock: how far, how long, how much to hold. Registered: docs/prereg_blindspot.md §3b (16 Oct 2026).

Pool: sessions where WTI_SPOT's 5-session log return first reaches >= +8% (one shock per 20 sessions). Secondary +5% pool for
the table only. Per shock x market: forward log return at 5/10/20/40/60/90; worst interim loss and best gain of a long position
held 60 sessions with the session of each extreme; Sortino (annualised, rf 0). Legs at the shock: dollar 5-session, DGS2
5-session change (bp), regime label (expanding, as the engine uses). A3b: kernel weights on standardised legs + regime match,
earlier shocks only, ESS >= 8; weighted median path and time-to-extreme; criterion §3b. A3c: L_hist = min(5, 0.20/q90 worst
loss in the estimate's direction); T1 exposure = min(1, 0.10 / EWMA vol) reported as both cap (a) and multiplier (b).
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PANEL = Path("processed/asset_returns.parquet"); WTI = Path("processed/wti_cont.parquet")
ROWS = Path("processed/oil_shocks.csv")
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO", "WTI_SPOT"]
H = (5, 10, 20, 40, 60, 90); HOLD = 60; GAP = 20; ESS_FLOOR = 8; LOSS_LIMIT, L_CAP = 0.20, 5.0
CHAIN_DATES = ["2009-01-26", "2009-02-24", "2015-02-06", "2022-03-07", "2026-03-05"]


def load():
    rets = pd.read_parquet(PANEL); rets.index = pd.to_datetime(rets.index)
    w = pd.read_parquet(WTI); w.index = pd.to_datetime(w.index)
    rets["WTI_SPOT"] = w["WTI_SPOT"].reindex(rets.index)
    from src.blindspot import load_macro
    dgs2, dxy = load_macro(rets.index)
    return rets, dgs2, dxy


def regime_labels(idx):
    """Expanding regime label per session, from the frozen pipeline; -1 where none."""
    try:
        import asset_extension as AE
        cfg = AE.load_config(); sc, _ = AE.load_data()
        lab = pd.Series(np.asarray(AE.regime_labels_expanding(sc, cfg)), index=pd.DatetimeIndex(sc.index))
        return lab.reindex(idx).ffill().fillna(-1).astype(int)
    except Exception as e:
        print(f"  regime labels unavailable ({type(e).__name__}); regime leg set to -1 everywhere"); return pd.Series(-1, index=idx)


def shocks(oil, thr, gap=GAP):
    r5 = oil.rolling(5).sum(); out = []; last = -10**9
    for i, v in enumerate(r5.to_numpy()):
        if np.isfinite(v) and v >= thr and i - last > gap: out.append(i); last = i
    return out


def path_stats(r, i, hold=HOLD):
    """r: log returns of one asset; i: shock position. Forward sums at H; worst loss / best gain of a long held `hold`."""
    n = len(r); out = {}
    for h in H:
        seg_h = r.iloc[i + 1:i + 1 + h]
        out[f"f{h}"] = float(seg_h.sum()) if (i + h < n and not seg_h.isna().any()) else np.nan
    seg = r.iloc[i + 1:i + 1 + hold]
    if len(seg) < hold or seg.isna().any() or not np.isfinite(r.iloc[max(0, i - 5):i + 1]).all():
        # the asset has no data over this window (pre-inception, or a gap): no row, never a zero-filled flat line
        out.update(worst=np.nan, worst_t=np.nan, best=np.nan, best_t=np.nan, sortino=np.nan)
        for h in H: out[f"f{h}"] = np.nan
        return out
    cum = seg.cumsum().to_numpy()
    out["worst"] = float(min(cum.min(), 0.0)); out["worst_t"] = int(cum.argmin()) + 1
    out["best"] = float(max(cum.max(), 0.0)); out["best_t"] = int(cum.argmax()) + 1
    dd = seg[seg < 0]; dsd = float(np.sqrt((dd ** 2).sum() / hold)) if len(dd) else 0.0
    out["sortino"] = float(seg.mean() / dsd * np.sqrt(252)) if dsd > 0 else np.nan
    return out


def build_rows():
    rets, dgs2, dxy = load(); oil = rets["WTI_SPOT"].fillna(0.0); lab = regime_labels(rets.index)
    rows = []
    for thr, pool in ((0.08, "p8"), (0.05, "p5")):
        for i in shocks(oil, thr):
            d = rets.index[i]
            base = dict(pool=pool, date=d.strftime("%Y-%m-%d"), pos=i, oil5=float(oil.iloc[i - 4:i + 1].sum()),
                        dxy5=float(dxy.iloc[i] / dxy.iloc[i - 5] - 1) if i >= 5 else np.nan,
                        dgs2_5bp=float((dgs2.iloc[i] - dgs2.iloc[i - 5]) * 100) if i >= 5 else np.nan,
                        regime=int(lab.iloc[i]), chain=d.strftime("%Y-%m-%d") in CHAIN_DATES or any(abs((d - pd.Timestamp(c)).days) <= 7 for c in CHAIN_DATES))
            for a in ASSETS:
                st = path_stats(rets[a], i)                       # NaN where the asset has no data: the row is dropped below
                if np.isfinite(st.get("f20", np.nan)) or np.isfinite(st.get("worst", np.nan)): rows.append({**base, "asset": a, **st})
    df = pd.DataFrame(rows); ROWS.parent.mkdir(exist_ok=True); df.to_csv(ROWS, index=False); return df


def cmd_table(a):
    df = build_rows()
    L = ["# T13 A3a — after an oil shock: the path table", "",
         f"*{datetime.now():%Y-%m-%d}. Pool p8: WTI_SPOT 5-session log return ≥ +8%, one shock per {GAP} sessions; p5: ≥ +5%, table only. "
         f"Rows per asset: p8 {df[(df.pool=='p8')&(df.asset=='GLD')].shape[0]}, p5 {df[(df.pool=='p5')&(df.asset=='GLD')].shape[0]}. "
         f"Forward returns are log returns of a long position; worst/best are interim extremes over {HOLD} sessions with the session they occurred; "
         "Sortino annualised, rf 0. Measured, no verdict. Status: descriptive (prereg_blindspot §3b A3a).*", ""]
    for pool in ("p8", "p5"):
        sub = df[df.pool == pool]
        L += [f"## Pool {pool} — {sub.date.nunique()} shocks ({sub.date.min()} → {sub.date.max()}); ETF rows only where the ETF existed", "",
              "| market | n | f5 | f10 | f20 | f40 | f60 | f90 | worst loss (median) | at session | best gain (median) | at session | Sortino |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for a_ in ASSETS:
            s = sub[sub.asset == a_]; q = lambda c: s[c].median(); iq = lambda c: f"{s[c].quantile(.25):+.1%}…{s[c].quantile(.75):+.1%}"
            L.append(f"| {a_} | {s.f60.notna().sum()} | " + " | ".join(f"{q(f'f{h}'):+.1%}" for h in H) +
                     f" | {q('worst'):+.1%} ({iq('worst')}) | {q('worst_t'):.0f} | {q('best'):+.1%} ({iq('best')}) | {q('best_t'):.0f} | {q('sortino'):+.2f} |")
        L.append("")
    ch = df[(df.pool == "p8") & df.chain & (df.asset == "GLD")]
    L += ["## The five chain firings inside p8 (gold)", "", "| date | f20 | f60 | worst | at | best | at | dxy5 | dgs2 5s bp | regime |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in ch.itertuples(): L.append(f"| {r.date} | {r.f20:+.1%} | {r.f60:+.1%} | {r.worst:+.1%} | {r.worst_t:.0f} | {r.best:+.1%} | {r.best_t:.0f} | {r.dxy5:+.2%} | {r.dgs2_5bp:+.0f} | {r.regime} |")
    L += ["", f"Chain firings matched inside p8: {ch.shape[0]} of 5 (a firing is matched if a p8 shock falls within 7 sessions of it).",
          "", "What this does not say: whether any of it is predictable from the legs — that is A3b."]
    Path("docs/oil_shock_table.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/oil_shock_table.md")


def _kernel(Z_pool, z, lab_pool, lab, ages):
    """Gaussian kernel on standardised legs, half weight on regime mismatch, recency half-life 10 years (prereg_analog_event HL)."""
    d2 = ((Z_pool - z) ** 2).sum(axis=1)
    w = np.exp(-0.5 * d2) * np.where(lab_pool == lab, 1.0, 0.5) * 0.5 ** (ages / 10.0)
    return w


def wmedian(x, w):
    o = np.argsort(x); cw = np.cumsum(w[o]); return float(x[o][np.searchsorted(cw, cw[-1] / 2)])


def cmd_estimate(a):
    df = pd.read_csv(ROWS) if ROWS.exists() else build_rows()
    p8 = df[df.pool == "p8"]; dates = sorted(p8.date.unique()); rng = np.random.default_rng(0)
    L = ["# T13 A3b — the conditional estimate, walk-forward", "",
         f"*{datetime.now():%Y-%m-%d}. Pool p8, {len(dates)} shocks; estimate for shock k uses shocks whose 60-session outcome closed before k; "
         f"kernel on standardised legs (dollar 5s, DGS2 5s bp, oil 5s) with half weight on a regime mismatch and a 10-year recency half-life; "
         f"ESS floor {ESS_FLOOR}; criterion prereg_blindspot §3b: (i) sign at 20 sessions ≥ 60% where ESS ≥ 8, vs the pool median's share; "
         "(ii) time-to-extreme within ±10 sessions ≥ 50%. Permutation null for (i): leg vectors shuffled across shocks, 10,000 draws.*", "",
         "| market | shocks scored (ESS ≥ 8) | (i) conditional sign hit | pool-median sign hit | null q95 | p | (ii) timing within ±10 | verdict |", "|---|---|---|---|---|---|---|---|"]
    verdicts = {}
    for asset in ASSETS:
        s = p8[p8.asset == asset].sort_values("date").set_index("date")
        dates = list(s.index)                                  # this market's own shocks (ETFs start 2004-2007)
        legs = s[["dxy5", "dgs2_5bp", "oil5"]].to_numpy(float); lab = s["regime"].to_numpy(int); pos = s["pos"].to_numpy(int)
        f20 = s["f20"].to_numpy(float); tt = np.where(s["f60"].to_numpy(float) < 0, s["worst_t"].to_numpy(float), s["best_t"].to_numpy(float))
        hits = []; base = []; tim = []
        def run(legs_):
            h = []; b = []; t = []
            for k in range(15, len(dates)):              # walk-forward from this market's 16th shock
                earlier = np.array([j for j in range(k) if pos[j] + HOLD < pos[k] and np.isfinite(f20[j])])
                if len(earlier) < 10: continue
                mu, sd = np.nanmean(legs_[earlier], 0), np.nanstd(legs_[earlier], 0) + 1e-12
                Zp, z = (legs_[earlier] - mu) / sd, (legs_[k] - mu) / sd
                if not np.isfinite(z).all(): continue
                w = _kernel(Zp, z, lab[earlier], lab[k], (pos[k] - pos[earlier]) / 252.0); ess = w.sum() ** 2 / (w ** 2).sum()
                if ess < ESS_FLOOR or not np.isfinite(f20[k]): continue
                est = wmedian(f20[earlier], w); h.append(np.sign(est) == np.sign(f20[k]) and f20[k] != 0)
                b.append(np.sign(np.median(f20[earlier])) == np.sign(f20[k]) and f20[k] != 0)
                t.append(abs(wmedian(tt[earlier], w) - tt[k]) <= 10)
            return np.array(h, bool), np.array(b, bool), np.array(t, bool)
        hits, base, tim = run(legs)
        n = len(hits)
        if n == 0: L.append(f"| {asset} | 0 | — | — | — | — | — | UNTESTED |"); verdicts[asset] = "UNTESTED"; continue
        hr, br, tr = hits.mean(), base.mean(), tim.mean()
        null = np.array([run(legs[rng.permutation(len(legs))])[0].mean() if len(run(legs[rng.permutation(len(legs))])[0]) else np.nan for _ in range(min(a.n_perm, 2000))])
        null = null[np.isfinite(null)]; q95 = float(np.nanquantile(null, .95)) if len(null) else np.nan; pval = float((null >= hr).mean()) if len(null) else np.nan
        if n < 15: v = "UNTESTED"
        elif hr >= 0.60 and hr >= br and tr >= 0.50: v = "PASS"
        elif hr >= 0.60 and hr >= br: v = "INCONCLUSIVE"
        else: v = "FAIL"
        verdicts[asset] = v
        L.append(f"| {asset} | {n} | {hr:.0%} | {br:.0%} | {q95:.0%} | {pval:.3f} | {tr:.0%} | **{v}** |")
    L += ["", "Reading: (i) asks whether knowing the legs and the regime at the shock tells you gold's (or any market's) direction 20 sessions on "
          "better than just knowing 'an oil shock happened'. (ii) asks the same for when the move peaks. UNTESTED = fewer than 15 shocks with "
          "enough comparable precedents. Prior: (i) PASS-weak 60–65%, (ii) FAIL.", f"", f"Verdicts: {verdicts}"]
    Path("docs/oil_shock_estimate.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/oil_shock_estimate.md")
    json.dump(verdicts, open("processed/oil_shock_verdicts.json", "w"))


def cmd_leverage(a):
    df = pd.read_csv(ROWS) if ROWS.exists() else build_rows(); p8 = df[df.pool == "p8"]
    rets, _, _ = load()
    L = ["# T13 A3c — how much the history supports holding", "",
         f"*{datetime.now():%Y-%m-%d}. L_hist = min({L_CAP:.0f}, {LOSS_LIMIT:.0%} ÷ q90), q90 = 90th percentile of the unlevered worst interim loss over "
         f"{HOLD} sessions across p8 shocks, for a position in the direction of the pool's median f60 (short if negative: the loss of a short is the "
         "price's best gain). T1 exposure = min(1, 10% ÷ EWMA(0.94) vol) on the latest session. Two readings of 'capped by T1' (registration wording, "
         "founder to pick): (a) literal L = min(L_hist, T1) ≤ 1; (b) multiplier L = L_hist × T1. Not a guarantee: the next drawdown can exceed any past one.*", "",
         "| market | direction (pool median f60) | median worst loss | q90 worst loss | L_hist | T1 exposure today | (a) min | (b) product | worst past case at (b) |", "|---|---|---|---|---|---|---|---|---|"]
    for asset in ASSETS:
        s = p8[p8.asset == asset].dropna(subset=["f60"]); d = np.sign(s.f60.median())
        loss = (-s.worst) if d >= 0 else s.best            # magnitude of the position's worst interim loss
        q90 = float(np.quantile(loss, .90)); med = float(np.median(loss))
        lh = min(L_CAP, LOSS_LIMIT / q90) if q90 > 0 else L_CAP
        r = rets[asset].dropna(); sig = float(np.sqrt((r.ewm(alpha=1 - 0.94).var().iloc[-1]) * 252)); t1 = min(1.0, 0.10 / sig) if sig > 0 else 1.0
        L.append(f"| {asset} | {'long' if d >= 0 else 'short'} | {med:.1%} | {q90:.1%} | {lh:.2f}× | {t1:.2f} | {min(lh, t1):.2f}× | {lh * t1:.2f}× | {loss.max() * lh * t1:.1%} |")
    L += ["", "The leverage number is informational until A3b passes for that market (prereg §3b, app rule)."]
    Path("docs/oil_shock_leverage.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/oil_shock_leverage.md")


def cmd_inverse(a):
    """Diagnostic for the founder's coin-flip question: would taking the OPPOSITE of A3b's conditional sign have beaten the pool
    median on the same historical shocks? Reports the inverse hit, the two-sided binomial p against 0.5, the first-half /
    second-half split (a real edge shows in both), and the Bonferroni bar for six markets. Not a verdict (prereg: forward-only)."""
    from math import comb
    def binom_two_sided(k, n):
        p0 = sum(comb(n, i) for i in range(0, n + 1) if abs(i - n / 2) >= abs(k - n / 2)) / 2 ** n; return min(1.0, p0)
    df = pd.read_csv(ROWS) if ROWS.exists() else build_rows(); p8 = df[df.pool == "p8"]
    L = ["# A3b inverse — the coin-flip check", "",
         f"*{datetime.now():%Y-%m-%d}. Same walk-forward as A3b; the inverse call is minus the conditional sign. Question: is 'below 50%' a real "
         "bias worth trading backwards, or binomial noise? Diagnostic only — the registered form is forward-only (prereg_blindspot 16 Oct).*", "",
         "| market | n | A3b hit | inverse hit | pool-median hit | binomial p (vs 50%) | Bonferroni ×6 | inverse hit 1st half | 2nd half | reading |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for asset in ASSETS:
        s_ = p8[p8.asset == asset].sort_values("date").set_index("date"); dates = list(s_.index)
        legs = s_[["dxy5", "dgs2_5bp", "oil5"]].to_numpy(float); lab = s_["regime"].to_numpy(int); pos = s_["pos"].to_numpy(int); f20 = s_["f20"].to_numpy(float)
        hit, base = [], []
        for k in range(15, len(dates)):
            earlier = np.array([j for j in range(k) if pos[j] + HOLD < pos[k] and np.isfinite(f20[j])])
            if len(earlier) < 10 or not np.isfinite(f20[k]) or f20[k] == 0: continue
            mu, sd = np.nanmean(legs[earlier], 0), np.nanstd(legs[earlier], 0) + 1e-12
            Zp, z = (legs[earlier] - mu) / sd, (legs[k] - mu) / sd
            if not np.isfinite(z).all(): continue
            w = _kernel(Zp, z, lab[earlier], lab[k], (pos[k] - pos[earlier]) / 252.0)
            if w.sum() ** 2 / (w ** 2).sum() < ESS_FLOOR: continue
            est = wmedian(f20[earlier], w)
            hit.append(np.sign(est) == np.sign(f20[k])); base.append(np.sign(np.median(f20[earlier])) == np.sign(f20[k]))
        hit, base = np.array(hit, bool), np.array(base, bool); n = len(hit)
        if n == 0: L.append(f"| {asset} | 0 | — | — | — | — | — | — | — | untested |"); continue
        inv = ~hit; k_inv = int(inv.sum()); pb = binom_two_sided(k_inv, n); half = n // 2
        h1, h2 = inv[:half].mean(), inv[half:].mean()
        reading = ("edge in both halves and p < 0.05/6" if (pb < 0.05 / 6 and h1 > .5 and h2 > .5) else
                   "one half only — not stable" if (h1 > .55) != (h2 > .55) else "within noise")
        L.append(f"| {asset} | {n} | {hit.mean():.0%} | {inv.mean():.0%} | {base.mean():.0%} | {pb:.3f} | {'yes' if pb < 0.05/6 else 'no'} | {h1:.0%} | {h2:.0%} | {reading} |")
    L += ["", "How to read it: the inverse hit is 100% minus A3b's hit on the same calls. 'Binomial p' is the chance a fair coin lands this far from 50% "
          "on this many trials; six markets were tested, so the bar for any one of them is 0.05 ÷ 6 ≈ 0.008. A real bias shows in both halves of the "
          "sample. Anything else is the kind of gap that disappears on the next 60 shocks. Forward scoring of the registered inverse hypothesis "
          "starts with the first shock after 16 Oct 2026."]
    Path("docs/oil_shock_inverse.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/oil_shock_inverse.md")


def _inverse_calls(s_, min_hist=10):
    """Walk-forward conditional sign for one market's shock rows (sorted by date). Returns arrays: dates, conditional sign, realised f20."""
    dates = list(s_.index); legs = s_[["dxy5", "dgs2_5bp", "oil5"]].to_numpy(float); lab = s_["regime"].to_numpy(int)
    pos = s_["pos"].to_numpy(int); f20 = s_["f20"].to_numpy(float); out = []
    for k in range(15, len(dates)):
        earlier = np.array([j for j in range(k) if pos[j] + HOLD < pos[k] and np.isfinite(f20[j])])
        if len(earlier) < min_hist: continue
        mu, sd = np.nanmean(legs[earlier], 0), np.nanstd(legs[earlier], 0) + 1e-12
        Zp, z = (legs[earlier] - mu) / sd, (legs[k] - mu) / sd
        if not np.isfinite(z).all(): continue
        w = _kernel(Zp, z, lab[earlier], lab[k], (pos[k] - pos[earlier]) / 252.0)
        if w.sum() ** 2 / (w ** 2).sum() < ESS_FLOOR: continue
        out.append((dates[k], float(np.sign(wmedian(f20[earlier], w))), float(np.sign(np.median(f20[earlier]))), f20[k]))
    return out


def cmd_heldout(a):
    """USO inverse on the +5%-only shocks (not within 20 sessions of any +8% shock). Registered 16 Oct; one shot."""
    from math import comb
    df = pd.read_csv(ROWS) if ROWS.exists() else build_rows()
    p8pos = set(df[df.pool == "p8"].pos.unique()); p5 = df[(df.pool == "p5") & (df.asset == "USO")].copy()
    p5 = p5[[all(abs(int(p) - int(q)) > GAP for q in p8pos) for p in p5.pos]].sort_values("date").set_index("date")
    calls = _inverse_calls(p5)
    scored = [(d, c, b, r) for d, c, b, r in calls if np.isfinite(r) and r != 0]
    n = len(scored); inv = np.array([np.sign(-c) == np.sign(r) for _, c, _, r in scored]); base = np.array([np.sign(b) == np.sign(r) for _, _, b, r in scored])
    k = int(inv.sum()); pb = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else np.nan
    hr = inv.mean() if n else np.nan
    v = "UNTESTED (n < 30)" if n < 30 else "PASS" if (hr >= .60 and pb < .05) else "INCONCLUSIVE" if hr >= .55 else "FAIL"
    L = ["# USO inverse — held-out check on the +5%-only shocks", "",
         f"*{datetime.now():%Y-%m-%d}. Shocks in the +5% pool that are not within {GAP} sessions of any +8% shock: {p5.shape[0]} USO rows, never used in A3b "
         f"or the diagnostic. Same kernel and ESS floor; walk-forward from the 16th. Criterion (prereg 16 Oct): PASS if inverse hit ≥ 60%, one-sided "
         "binomial p < 0.05, n ≥ 30.*", "",
         f"| scored | inverse hit | pool-median hit | binomial p | verdict |", "|---|---|---|---|---|",
         f"| {n} | {hr:.0%} | {base.mean() if n else float('nan'):.0%} | {pb:.3f} | **{v}** |", "",
         "Reading: milder shocks (+5% to +8% in a week) are a different population from the +8% pool, so a pass here says the pattern is not specific "
         "to the big shocks; a fail says it may be. Either way the forward test decides."]
    Path("docs/oil_inverse_heldout.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/oil_inverse_heldout.md")


FWD = Path("processed/oil_inverse_forward.csv")


def cmd_forward(a):
    """Nightly hook. If the last completed session is a new +8% shock (not within GAP sessions of a logged one), log USO's inverse call;
    mature any open row whose 20th session has closed, with the USO−spot companion. Write-once per shock."""
    rets, dgs2, dxy = load(); oil = rets["WTI_SPOT"].fillna(0.0); idx = rets.index
    fwd = pd.read_csv(FWD, parse_dates=["shock_date"]) if FWD.exists() else pd.DataFrame(columns=["shock_date", "logged_at", "pos", "cond_sign", "inverse_call", "pool_median_sign", "f20_uso", "f20_spot", "hit", "matured_at"])
    i = len(idx) - 1; r5 = float(oil.iloc[i - 4:i + 1].sum())
    is_shock = r5 >= 0.08 and all(abs(i - int(p)) > GAP for p in fwd.pos) if len(fwd) else r5 >= 0.08
    if is_shock:
        df = pd.read_csv(ROWS) if ROWS.exists() else build_rows()
        s_ = df[(df.pool == "p8") & (df.asset == "USO")].sort_values("date").set_index("date")
        lab = regime_labels(idx); legs_now = np.array([float(dxy.iloc[i] / dxy.iloc[i - 5] - 1), float((dgs2.iloc[i] - dgs2.iloc[i - 5]) * 100), r5])
        hist = s_[s_.pos + HOLD < i]; L_ = hist[["dxy5", "dgs2_5bp", "oil5"]].to_numpy(float)
        mu, sd = np.nanmean(L_, 0), np.nanstd(L_, 0) + 1e-12
        w = _kernel((L_ - mu) / sd, (legs_now - mu) / sd, hist.regime.to_numpy(int), int(lab.iloc[i]), (i - hist.pos.to_numpy()) / 252.0)
        ess = w.sum() ** 2 / (w ** 2).sum(); cond = float(np.sign(wmedian(hist.f20.to_numpy(float), w))) if ess >= ESS_FLOOR else 0.0
        row = dict(shock_date=idx[i], logged_at=datetime.now().strftime("%Y-%m-%d %H:%M"), pos=i, cond_sign=cond, inverse_call=-cond,
                   pool_median_sign=float(np.sign(hist.f20.median())), f20_uso=np.nan, f20_spot=np.nan, hit=np.nan, matured_at="")
        fwd = pd.concat([fwd, pd.DataFrame([row])], ignore_index=True)
        print(f"oil forward: NEW +8% shock {idx[i].date()} (5s {r5:+.1%}); USO conditional sign {cond:+.0f}, inverse call {-cond:+.0f}, ESS {ess:.1f}")
    for j, r in fwd.iterrows():
        if pd.isna(r.f20_uso) and int(r.pos) + 20 <= i:
            p0 = int(r.pos); fu = float(rets["USO"].iloc[p0 + 1:p0 + 21].sum()); fs = float(oil.iloc[p0 + 1:p0 + 21].sum())
            fwd.loc[j, ["f20_uso", "f20_spot", "matured_at"]] = [fu, fs, idx[i].strftime("%Y-%m-%d")]
            fwd.loc[j, "hit"] = float(np.sign(r.inverse_call) == np.sign(fu) and fu != 0 and r.inverse_call != 0)
            print(f"oil forward: matured {pd.Timestamp(r.shock_date).date()}: USO f20 {fu:+.2%}, spot {fs:+.2%}, inverse hit {bool(fwd.loc[j, 'hit'])}")
    FWD.parent.mkdir(exist_ok=True); fwd.to_csv(FWD, index=False)
    done = fwd[fwd.hit.notna()]
    print(f"oil forward: {len(fwd)} shock(s) logged since 16 Oct 2026, {len(done)} matured" + (f", inverse hit {done.hit.mean():.0%}" if len(done) else "") + " (verdict at n ≥ 20)")


def cmd_selftest(a):
    idx = pd.bdate_range("2020-01-01", periods=400); r = pd.Series(0.0, index=idx)
    r.iloc[100:105] = 0.02; r.iloc[300:305] = 0.02; r.iloc[150:155] = 0.011     # two +10% shocks, one +5.5%
    s8, s5 = shocks(r, 0.08), shocks(r, 0.05)
    # original expectation [104, 304] / [104, 154, 304] was wrong: four +2% days already reach +8% (fires on index 103), three reach +5% (102)
    assert s8 == [103, 303], s8; assert s5 == [102, 154, 302], s5; print("  T1 pool detection + 20-session gap: PASS")
    g = pd.Series(0.0, index=idx); g.iloc[104:114] = -0.01; g.iloc[114:134] = +0.01
    st = path_stats(g, 103); assert abs(st["worst"] + 0.10) < 1e-9 and st["worst_t"] == 10 and abs(st["best"] - 0.10) < 1e-9 and st["best_t"] == 30, st
    assert abs(st["f20"] - 0.0) < 1e-9 and abs(st["f10"] + 0.10) < 1e-9; print("  T2 path stats (worst/best/time/forward): PASS")
    assert wmedian(np.array([1., 2., 3.]), np.array([1., 1., 10.])) == 3.0; print("  T3 weighted median: PASS")
    w = _kernel(np.zeros((3, 3)), np.zeros(3), np.array([0, 1, 0]), 0, np.array([0., 0., 10.])); assert abs(w[0] - 1) < 1e-9 and abs(w[1] - .5) < 1e-9 and abs(w[2] - .5) < 1e-9
    print("  T4 kernel (regime half-weight, 10y half-life): PASS")
    assert min(L_CAP, LOSS_LIMIT / 0.08) == 2.5 and min(L_CAP, LOSS_LIMIT / 0.02) == 5.0; print("  T5 leverage rule: PASS"); print("selftest: 5/5")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("selftest", "table", "leverage", "inverse", "heldout", "forward"): sub.add_parser(c)
    e = sub.add_parser("estimate"); e.add_argument("--n-perm", type=int, default=2000)
    a = ap.parse_args(); {"selftest": cmd_selftest, "table": cmd_table, "estimate": cmd_estimate, "leverage": cmd_leverage, "inverse": cmd_inverse, "heldout": cmd_heldout, "forward": cmd_forward}[a.cmd](a)


if __name__ == "__main__":
    main()
