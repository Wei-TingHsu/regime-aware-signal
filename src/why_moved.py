"""
Why it moved — nightly, per asset (TRACK 3.33, prereg_factor_attribution §4).
  1. Turning points by an adaptive reversal rule: a peak/trough is confirmed when price moves against the trend by more than
     max(FLOOR, MULT × the asset's own 20-session volatility scaled to a month). The current episode runs from the last confirmed turning
     point to the last session; its extreme so far is provisional.
  2. Attribution (joint fit, sensitivities from the 504 sessions before the episode start) of the episode and of the last session;
     the unexplained share stated.
  3. Target: the level this asset's past episodes in the same direction have typically run to (median size, quartile band, n) — a base rate,
     labelled as such; the factor-conditioned version is the registered test (prior #62).
Writes processed/why_moved.json and docs/why_moved_latest.md. The app reads the json.

  python -m src.why_moved selftest
  python -m src.why_moved run
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.factor_attribution import factors, returns, joint_fit, ORDER_DEFAULT, LABEL, WINDOW, impulse_window, tests as fa_tests

PROC, DOCS = Path("processed"), Path("docs")
ASSETS = ["SPY", "TLT", "GLD", "SLV", "UUP", "USO", "NVDA", "META"]   # the five markets, silver, two tech names as the founder asked
NAME = {"SPY": "US equities", "TLT": "long Treasuries", "GLD": "gold", "SLV": "silver", "UUP": "the dollar", "USO": "oil", "NVDA": "Nvidia", "META": "Meta"}
MULT, FLOOR, MIN_EP = 1.5, 0.08, 5


def turning_points(r: pd.Series, mult: float = MULT, floor: float = FLOOR):
    """Zigzag with an adaptive threshold. Returns list of (position, 'peak'|'trough'), current trend (+1/-1/0), provisional extreme position."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy())
    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20); thr = np.maximum(floor, mult * sig)
    hi = lo = 0; trend = 0; tps = []
    for i in range(1, len(px)):
        if trend >= 0 and px[i] > px[hi]: hi = i
        if trend <= 0 and px[i] < px[lo]: lo = i
        if trend >= 0 and px[i] <= px[hi] * np.exp(-thr[i]):
            tps.append((hi, "peak")); trend = -1; lo = i
        elif trend <= 0 and px[i] >= px[lo] * np.exp(thr[i]):
            tps.append((lo, "trough")); trend = 1; hi = i
    return tps, trend, (hi if trend > 0 else lo), px, thr


def past_episodes(tps, px):
    """Completed episodes between consecutive turning points: direction, size (log), length."""
    out = []
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        out.append(dict(start=a, end=b, direction=(1 if ka == "trough" else -1), size=float(np.log(px[b] / px[a])), length=int(b - a)))
    return out


def attribute(r: pd.Series, F: pd.DataFrame, s0, s1):
    """Joint-fit attribution of r over [s0, s1] with sensitivities from the WINDOW sessions before s0."""
    avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename("r")).dropna(); ep = F.loc[s0:s1][avail].join(r.rename("r")).dropna()
    if s1 != s0: ep = ep.iloc[1:]   # the move starts after the turning point
    if len(win) < 250 or len(ep) < 1: return None
    b = joint_fit(win.r.to_numpy(), win[avail].to_numpy()); sums = ep[avail].sum().to_numpy(); contrib = b * sums; actual = float(ep.r.sum())
    drift = float((win.r.mean() - win[avail].mean().to_numpy() @ b) * len(ep)); resid = actual - contrib.sum() - drift
    rows = [dict(factor=f, label=LABEL[f], beta=float(bb), move=float(sm), contrib=float(c), share=(float(c / actual) if actual else 0.0))
            for f, bb, sm, c in zip(avail, b, sums, contrib)]
    rows.sort(key=lambda d: -abs(d["contrib"]))
    return dict(actual=actual, sessions=int(len(ep)), rows=rows, drift=drift, resid=float(resid), unexplained_share=(float(resid / actual) if actual else 0.0))


# ---------------------------------------------------------------- explained-share curve and window rules (founder, 23 Oct)
PATIENCE, MIN_K, MAX_K = 5, 5, 120


def attr_curve(r: pd.Series, F: pd.DataFrame, s0, max_k: int = MAX_K, window: int = WINDOW):
    """For windows of 1..max_k sessions after the turning point s0: cumulative move, the reasons' explained part (pre-episode sensitivities,
    drift excluded), residual, and the explained share 1 - |resid|/|move| (NaN while the move is under 1%)."""
    avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    win = F.loc[:s0].iloc[-window - 1:-1][avail].join(r.rename("r")).dropna(); ep = F.loc[s0:][avail].join(r.rename("r")).dropna().iloc[1:max_k + 1]
    if len(win) < 250 or len(ep) < 3: return None
    b = joint_fit(win.r.to_numpy(), win[avail].to_numpy())
    cF = ep[avail].cumsum().to_numpy(); cr = ep.r.cumsum().to_numpy(); explained = cF @ b; resid = cr - explained
    score = 1 - np.abs(resid) / np.maximum(np.abs(cr), 1e-9); score[np.abs(cr) < 0.01] = np.nan
    return dict(k=np.arange(1, len(ep) + 1), move=cr, explained=explained, score=score, dates=ep.index)


def window_rules(curve, L: int, k_imp: int, patience: int = PATIENCE, min_k: int = MIN_K):
    """Scores under each rule for an episode of L sessions. R4 is chosen after the fact (a ceiling); R5 walks forward and stops when the
    score has not improved for PATIENCE sessions (causal, usable live)."""
    sc = curve["score"][:L]; n = len(sc)
    if n == 0: return None
    out = {"R1_full": (n, float(sc[n - 1])), "R2_impulse": (min(k_imp, n), float(sc[min(k_imp, n) - 1]) if k_imp >= 1 else np.nan), "R3_half": (max(n // 2, 1), float(sc[max(n // 2, 1) - 1]))}
    fin = np.where(np.isfinite(sc))[0]
    out["R4_ceiling"] = (int(fin[np.nanargmax(sc[fin])]) + 1, float(np.nanmax(sc[fin]))) if len(fin) else (n, np.nan)
    if n < min_k:
        out["R5_causal"] = (n, float(sc[n - 1])); return out
    best, kb, since = -np.inf, min_k, 0
    for k in range(min_k, n + 1):
        v = sc[k - 1]
        if np.isfinite(v) and v > best: best, kb, since = v, k, 0
        else: since += 1
        if since >= patience: break
    out["R5_causal"] = (kb, float(best) if np.isfinite(best) else np.nan)
    return out


# ---------------------------------------------------------------- T-G: the window rule's own variables, swept (founder's rule, 23 Oct)
GRID_PATIENCE = (2, 3, 5, 7, 10, 15, 20, 30)
GRID_MINK = (3, 5, 10)
GRID_WINDOW = (252, 504, 756)
GRID_REVERSAL = ((1.0, 0.05), (1.5, 0.08), (2.0, 0.12))


def _r5_cells(r, F, cells, idx):
    """Median R5 share and share-beating-R1 for every cell; episodes depend on the reversal rule, curves on the look-back; rules are cheap on top."""
    out = {}; cache = {}
    for (mult, floor, window, patience, min_k) in cells:
        key = (mult, floor)
        if key not in cache:
            tps, _, _, px, thr = turning_points(r, mult, floor)
            cache[key] = [(a, b, 1 if ka == "trough" else -1, float(thr[a])) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP]
        eps = cache[key]; ckey = (mult, floor, window)
        if ckey not in cache:
            cache[ckey] = [(attr_curve(r, F, idx[a], max_k=min(b - a, MAX_K), window=window), a, b, d, t) for a, b, d, t in eps if a >= window + 10]
        v5, v1 = [], []
        for cv, a, b, d, t in cache[ckey]:
            if cv is None: continue
            i0, i1, _ = impulse_window(r, idx[a], d, t); wr = window_rules(cv, min(b - a, MAX_K), max(len(r.loc[i0:i1]) - 1, 1), patience, min_k)
            if wr and np.isfinite(wr["R5_causal"][1]): v5.append(wr["R5_causal"][1]); v1.append(wr["R1_full"][1])
        v5, v1 = np.array(v5), np.array(v1)
        out[(mult, floor, window, patience, min_k)] = dict(n=int(len(v5)), r5=float(np.median(v5)) if len(v5) else np.nan, beat=float((v5 > v1).mean()) if len(v5) else np.nan)
    return out


def window_grid(asset, n_shift: int = 10, seed: int = 0):
    """Every cell of the window rule's variables; the best cell judged against the best cell of the same sweep on time-shifted factors."""
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index
    cells = [(m, f, w, p, k) for (m, f) in GRID_REVERSAL for w in GRID_WINDOW for p in GRID_PATIENCE for k in GRID_MINK]
    real = _r5_cells(r, F, cells, idx); df = pd.DataFrame([dict(mult=c[0], floor=c[1], window=c[2], patience=c[3], min_k=c[4], **v) for c, v in real.items()]).dropna(subset=["r5"])
    best = df.loc[df.r5.idxmax()]; rng = np.random.default_rng(seed); mx = []; mx_rule = {k: [] for k in GRID_REVERSAL}
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns); nc = _r5_cells(r, Fx, cells, idx)
        vals = [v["r5"] for v in nc.values() if np.isfinite(v["r5"])]
        if vals: mx.append(max(vals))
        for (m, f) in GRID_REVERSAL:
            vr = [v["r5"] for c, v in nc.items() if (c[0], c[1]) == (m, f) and np.isfinite(v["r5"])]
            if vr: mx_rule[(m, f)].append(max(vr))
    mx = np.array(mx); p = float((mx >= best.r5).mean()) if len(mx) else np.nan; reg = real.get((MULT, FLOOR, WINDOW, PATIENCE, MIN_K), {})
    by_rule = {}   # best cell within each leg definition, judged against the null of ITS sub-grid: the app uses the one for its registered rule, so legs are never re-cut
    for (m, f) in GRID_REVERSAL:
        sub = df[(df.mult == m) & (df.floor == f)]
        if sub.empty: continue
        b = sub.loc[sub.r5.idxmax()]; arr = np.array(mx_rule[(m, f)]); pr = float((arr >= b.r5).mean()) if len(arr) else np.nan
        by_rule[f"{m},{f}"] = dict(mult=m, floor=f, window=int(b.window), patience=int(b.patience), min_k=int(b.min_k), r5=float(b.r5), beat=float(b.beat), n=int(b.n), p=pr, null_median=(float(np.median(arr)) if len(arr) else None))
    L = [f"# T-G window-rule grid — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {len(df)} cells: reversal rule (mult, floor) × look-back × patience × min window. "
         f"Statistic: median R5 explained share over past episodes. Best cell judged against the best cell of the same sweep on {len(mx)} time-shifted factor series (SPEC_GRID rule 2).*", "",
         f"**Registered cell** (1.5, 8%, 504, patience 5, min 5): median {reg.get('r5', float('nan')):.0%}, beats full leg in {reg.get('beat', float('nan')):.0%} (n {reg.get('n', 0)}).", "",
         f"**Best cell:** mult {best.mult}, floor {best.floor:.0%}, look-back {int(best.window)}, patience {int(best.patience)}, min window {int(best.min_k)} → median **{best.r5:.0%}**, beats full leg in {best.beat:.0%} (n {int(best.n)}); "
         f"best-of-sweep null median {np.median(mx) if len(mx) else float('nan'):.0%}, **p = {p:.2f}** → " + ("survives the sweep" if p < 0.05 else "does not beat the best noise cell"), "",
         "| rank | mult | floor | look-back | patience | min k | median R5 | beats full | n |", "|---|---|---|---|---|---|---|---|---|"]
    L += ["", "**Best cell within each leg definition** (the app uses the one for its registered rule — legs are never re-cut to fit a cell):", "",
          "| leg definition | look-back | patience | min k | median R5 | beats full | n | p (sub-grid null) |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {v['mult']}× / {v['floor']:.0%} | {v['window']} | {v['patience']} | {v['min_k']} | {v['r5']:.0%} | {v['beat']:.0%} | {v['n']} | {v['p']:.2f} |" for v in by_rule.values()]
    L += ["", "All cells, top 15:", ""]
    for i, (_, q) in enumerate(df.sort_values("r5", ascending=False).head(15).iterrows(), 1):
        L.append(f"| {i} | {q.mult} | {q.floor:.0%} | {int(q.window)} | {int(q.patience)} | {int(q.min_k)} | {q.r5:.0%} | {q.beat:.0%} | {int(q.n)} |")
    L += ["", "By patience (median over the other variables): " + ", ".join(f"{int(pp)}: {df[df.patience == pp].r5.median():.0%}" for pp in GRID_PATIENCE),
          "By look-back: " + ", ".join(f"{int(w)}: {df[df.window == w].r5.median():.0%}" for w in GRID_WINDOW),
          "By reversal rule: " + ", ".join(f"({m}, {f:.0%}): {df[(df.mult == m) & (df.floor == f)].r5.median():.0%}" for m, f in GRID_REVERSAL),
          "", "Reading: the registered 5/5 cell stays the recorded verdict; a surviving best cell is promoted (dated amendment) as the rule the app uses, with its p shown."]
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TG"] = dict(best=dict(mult=float(best.mult), floor=float(best.floor), window=int(best.window), patience=int(best.patience), min_k=int(best.min_k), r5=float(best.r5), beat=float(best.beat), n=int(best.n)),
                                                               null_median=(float(np.median(mx)) if len(mx) else None), p=p, n_cells=int(len(df)), by_rule=by_rule, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"window_grid_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")


def ceiling_null(r, F, s0, L, n_shift: int = 20, seed: int = 0):
    """What the after-the-fact best window (R4) scores on time-shifted factors for the same leg — the noise part of a chosen-after-the-fact share."""
    rng = np.random.default_rng(seed); vals = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns)
        cv = attr_curve(r, Fx, s0, max_k=min(L, MAX_K))
        if cv is None: continue
        sc = cv["score"][:L]; fin = sc[np.isfinite(sc)]
        if len(fin): vals.append(float(np.nanmax(fin)))
    return float(np.median(vals)) if vals else np.nan



# ---------------------------------------------------------------- alternative turning-point rules (founder, 23 Oct) — T-I
def turning_points_persist(r: pd.Series, n_days: int = 3, x: float = 0.02, mode: str = "time"):
    """Founder's rule: a reversal is a trend, not one bounce. mode='time' (the meant reading): the price has stayed off its extreme for n_days sessions
    AND is at least x against it. mode='closes' (the first, literal reading, withdrawn 23 Oct): n_days CONSECUTIVE closes against the trend and x —
    it never confirmed gold's Aug 2026 peak because the fall had no five-day losing streak."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); d = np.sign(rr.to_numpy())
    hi = lo = 0; trend = 0; tps = []; run_ = 0
    for i in range(1, len(px)):
        if trend >= 0 and px[i] > px[hi]: hi = i
        if trend <= 0 and px[i] < px[lo]: lo = i
        if mode == "closes":
            against = (d[i] < 0) if trend >= 0 else (d[i] > 0); run_ = run_ + 1 if against else 0
            ok_up, ok_dn = run_ >= n_days, run_ >= n_days
        else:
            ok_up, ok_dn = (i - hi) >= n_days, (i - lo) >= n_days          # sessions since the extreme, up days inside allowed
        if trend >= 0 and ok_up and px[i] <= px[hi] * np.exp(-x):
            tps.append((hi, "peak")); trend = -1; lo = i; run_ = 0
        elif trend <= 0 and ok_dn and px[i] >= px[lo] * np.exp(x):
            tps.append((lo, "trough")); trend = 1; hi = i; run_ = 0
    return tps, trend, (hi if trend > 0 else lo), px


def missed_reversals(tps, px, r: pd.Series):
    """Fidelity: inside each leg, the largest counter-move against the leg's direction; a counter-move above the zigzag threshold (max(FLOOR, MULT x monthly vol))
    is a turning point the rule failed to see. Returns the count and the worst one."""
    rr = r.fillna(0.0); thr = np.maximum(FLOOR, MULT * rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20))
    missed, worst = 0, 0.0
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        seg = px[a:b + 1]
        if ka == "trough":   # up leg: largest drawdown inside
            dd = (seg / np.maximum.accumulate(seg) - 1).min()
        else:                # down leg: largest rally inside
            dd = -(seg / np.minimum.accumulate(seg) - 1).max()
        if -dd >= thr[b]: missed += 1
        worst = min(worst, dd)
    return missed, float(-worst)


def turning_points_swing(r: pd.Series, k: int = 10):
    """Swing highs/lows: a peak is the highest close within k sessions either side (confirmed k sessions later); alternation enforced."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); n = len(px); cand = []
    for i in range(k, n - k):
        w = px[i - k:i + k + 1]
        if px[i] == w.max(): cand.append((i, "peak"))
        elif px[i] == w.min(): cand.append((i, "trough"))
    tps = []
    for i, kind in cand:
        if tps and tps[-1][1] == kind:
            j, _ = tps[-1]
            if (kind == "peak" and px[i] > px[j]) or (kind == "trough" and px[i] < px[j]): tps[-1] = (i, kind)
        else: tps.append((i, kind))
    trend = 0 if not tps else (-1 if tps[-1][1] == "peak" else 1)
    return tps, trend, (int(np.argmax(px[tps[-1][0]:])) + tps[-1][0] if trend > 0 else int(np.argmin(px[tps[-1][0]:])) + tps[-1][0]) if tps else 0, px


SEGMENTERS = [("zigzag 1.5× / 8% (registered)", lambda r: turning_points(r)[:4])] + \
             [(f"persist-time N={n}, X={x:.0%}", (lambda n, x: (lambda r: turning_points_persist(r, n, x, "time")))(n, x)) for n in (2, 3, 5, 10) for x in (0.02, 0.04, 0.08)] + \
             [(f"persist-closes N={n}, X={x:.0%}", (lambda n, x: (lambda r: turning_points_persist(r, n, x, "closes")))(n, x)) for n in (2, 3, 5) for x in (0.0, 0.02, 0.04, 0.08)] + \
             [(f"swing k={k}", (lambda k: (lambda r: turning_points_swing(r, k)))(k)) for k in (5, 10, 20)] + \
             [(f"retrace f={f:.0%}, N={n}, c={c}", (lambda f, n, c: (lambda r: turning_points_retrace(r, f, n, c)))(f, n, c)) for f in (0.25, 0.382, 0.5) for n in (3, 5) for c in (0.5, 1.0)]


def segmenter_test(asset, patience=None, min_k=None, window=None):
    """T-I: every turning-point rule side by side — legs found, median length, share of legs under 5 sessions, and the explained share the
    promoted window rule reaches on each rule's legs. Descriptive comparison (same factor series for all); the registered zigzag stays the
    recorded rule unless another beats it by >= 5 points on median explained share with at least as many legs."""
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; HL = ohlc(asset)
    SEGS = SEGMENTERS + ([(f"retrace-hl f=38%, N={n}, c={c}", (lambda n, c: (lambda rr_: turning_points_retrace(rr_, 0.382, n, c, True, HL, "close")))(n, c)) for n in (3, 5) for c in (0.5, 1.0)]
                        + [(f"retrace-hl-oc f=38%, N={n}, c={c}", (lambda n, c: (lambda rr_: turning_points_retrace(rr_, 0.382, n, c, True, HL, "oc")))(n, c)) for n in (3, 5) for c in (0.5, 1.0)] if HL is not None else [])
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    bb = ((J.get("tests", {}).get(asset, {}).get("TG", {}) or {}).get("by_rule") or {}).get(f"{MULT},{FLOOR}") or {}
    patience = patience or bb.get("patience", 20); min_k = min_k or bb.get("min_k", 3); window = window or bb.get("window", 252)
    rows = []
    for name, fn in SEGS:
        res = fn(r); tps, trend, ext, px = res[:4]; lags = res[4] if len(res) > 4 else None
        legs = [(a, b, 1 if ka == "trough" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:])]
        if not legs: rows.append(dict(rule=name, legs=0)); continue
        lengths = np.array([b - a for a, b, _ in legs]); sizes = np.array([abs(np.log(px[b] / px[a])) for a, b, _ in legs]); shares = []
        missed, worst = missed_reversals(tps, px, r)
        for a, b, d_ in legs:
            if b - a < MIN_EP or a < window + 10: continue
            cv = attr_curve(r, F, idx[a], max_k=min(b - a, MAX_K), window=window)
            if cv is None: continue
            wr = window_rules(cv, min(b - a, MAX_K), 1, patience, min_k)
            if wr and np.isfinite(wr["R5_causal"][1]): shares.append(wr["R5_causal"][1])
        rows.append(dict(rule=name, legs=len(legs), med_len=float(np.median(lengths)), short=float((lengths < 5).mean()), med_size=float(np.median(sizes)),
                         scored=len(shares), r5=float(np.median(shares)) if shares else np.nan, missed=int(missed), worst_missed=float(worst), lag=(float(np.median(lags)) if lags else np.nan)))
    df = pd.DataFrame(rows); reg = df.iloc[0]
    better = df[(df.r5 >= reg.r5 + 0.05) & (df.scored >= reg.scored) & (df.missed <= reg.missed)] if np.isfinite(reg.r5) else df.iloc[0:0]   # replaces the zigzag outright
    fine_ok = df[(df.rule.str.startswith("retrace")) & (df.missed == 0) & (df.lag <= 10) & (df.r5 >= reg.r5 - 0.05) & (df.legs >= reg.legs)] if np.isfinite(reg.r5) else df.iloc[0:0]   # T-J fine scale: sees every turn, confirms fast, explains nearly as well
    fine_best = fine_ok.sort_values(["missed", "lag", "r5"], ascending=[True, True, False]).iloc[0] if len(fine_ok) else None
    L = [f"# T-I turning-point rules — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Window rule used on every segmentation: patience {patience}, min window {min_k}, look-back {window} "
         f"(the promoted cell). 'short' = share of legs under 5 sessions (noise legs); 'missed' = legs hiding a counter-move above the zigzag threshold (a reversal the rule did not see — fidelity, added 23 Oct after the "
         f"consecutive-closes rule missed gold's August peak). Verdict rule: another segmentation replaces the zigzag only if its median explained share is ≥ 5 points higher, with at least as many scored legs, and no more missed reversals.*", "", f"**{'PASS for ' + ', '.join(better.rule) if len(better) else 'FAIL — no rule beats the registered zigzag by 5 points'}**", "",
         (f"**T-J fine scale: PASS — {fine_best.rule}** (0 missed, lag {fine_best.lag:.0f} sessions, {fine_best.legs} legs, explained {fine_best.r5:.0%}); promoted as the fine scale inside the zigzag's legs." if fine_best is not None else "**T-J fine scale: no retracement rule meets 0 missed, lag ≤ 10, share within 5 points, legs ≥ zigzag.**"), "",
         "| rule | legs since 2006 | median length | share < 5 sessions | median size | legs scored | median explained share | missed reversals (worst) | confirmation lag (sessions) |", "|---|---|---|---|---|---|---|---|---|"]
    for _, q in df.iterrows():
        L.append(f"| {q.rule} | {q.legs} | {q.get('med_len', float('nan')):.0f} | {q.get('short', float('nan')):.0%} | {np.expm1(q.get('med_size', 0)):.1%} | {q.get('scored', 0)} | {q.r5 if 'r5' in q and np.isfinite(q.r5) else float('nan'):.0%} | {int(q.get('missed', 0)) if 'missed' in q and pd.notna(q.get('missed')) else '—'} ({q.get('worst_missed', 0) if pd.notna(q.get('worst_missed', 0)) else 0:.0%}) | {q.get('lag', float('nan')) if 'lag' in q and pd.notna(q.get('lag')) else float('nan'):.0f} |")
    L += ["", "Reading: X = 0% is the pure gradient rule — direction flips with N consecutive closes; its legs are counted in days and mostly noise. Adding a minimum counter-move X "
          "turns it into a zigzag with a persistence condition; swing k is the local-extremum family. The founder's point stands as a rule in the grid; the data says which scale is useful."]
    J.setdefault("tests", {}).setdefault(asset, {})["TI"] = dict(rows=rows, better=list(better.rule), params=dict(patience=patience, min_k=min_k, window=window), run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    if fine_best is not None:
        import re as _re; mm = _re.match(r"retrace(-hl)?(-oc)? f=(\d+)%, N=(\d+), c=([\d.]+)", fine_best.rule)
        (PROC / "fine_rule.json").write_text(json.dumps(dict(rule="retrace", hl=bool(mm.group(1)), daysign=("oc" if mm.group(2) else "close"), f={25: 0.25, 38: 0.382, 50: 0.5}.get(int(mm.group(3)), int(mm.group(3)) / 100), n=int(mm.group(4)), c=float(mm.group(5)), promoted=datetime.now().strftime("%Y-%m-%d"),
                                                             asset_tested=asset, legs=int(fine_best.legs), lag=float(fine_best.lag), r5=float(fine_best.r5)), indent=1))
        J["tests"][asset]["TJ"] = dict(rule=fine_best.rule, legs=int(fine_best.legs), lag=float(fine_best.lag), r5=float(fine_best.r5), verdict="PASS")
    else:
        J["tests"][asset]["TJ"] = dict(verdict="FAIL")
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"segmenter_test_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")



# ---------------------------------------------------------------- T-J: the founder's gradient method as a retracement rule; two-scale legs
def ohlc(asset: str):
    """Open/High/Low/Close ratios to the close for the panel's assets (raw Yahoo cache, adjusted consistently); None where only closes exist."""
    p = Path("raw/yfinance") / f"{asset}.parquet"
    if not p.exists(): return None
    try:
        d = pd.read_parquet(p); d.index = pd.to_datetime(d.index)
        cols = {str(c).split("'")[1] if str(c).startswith("(") else str(c): c for c in d.columns}
        need = {k: cols[k] for k in ("Open", "High", "Low", "Close") if k in cols}
        if len(need) < 4: return None
        o = pd.DataFrame({k: d[v].astype(float) for k, v in need.items()}).dropna()
        return pd.DataFrame({"hi": o.High / o.Close, "lo": o.Low / o.Close, "oc": np.sign(o.Close - o.Open)}, index=o.index)
    except Exception:
        return None


def turning_points_retrace(r: pd.Series, f: float = 0.382, n: int = 5, c: float = 1.0, cap: bool = True, hl=None, daysign: str = "close"):
    """Founder's gradient test made operational: the sign of every back-gradient from today equals the sign of (today - that day), so 'all one sign'
    means today is the leg's extreme; a change of sign is a drawdown from the extreme. A turn is confirmed when that drawdown exceeds
    max(f x the leg's own move so far, c x monthly volatility) — capped at the coarse zigzag threshold (cap=True; without it a 50% retracement of a
    long trend is unreachable and the rule freezes) — and has persisted n sessions since the extreme (daysign='close') or n open-to-close days
    against the trend (daysign='oc'). hl: ratios High/Close, Low/Close (and the open-to-close sign) so extremes are the intraday ones.
    Returns tps, trend, extreme, px (closes), lags."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); lp = np.log(px)
    if hl is not None:
        h = hl.reindex(r.index); hi_r = h.hi.fillna(1.0).to_numpy(); lo_r = h.lo.fillna(1.0).to_numpy(); oc = h.oc.fillna(0.0).to_numpy()
    else:
        hi_r = lo_r = np.ones(len(px)); oc = np.sign(rr.to_numpy())
    pxh, pxl = np.log(px * hi_r), np.log(px * lo_r)                      # intraday extremes in log units (== closes when hl is None)
    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20); coarse = np.maximum(FLOOR, MULT * sig)
    hi = lo = 0; trend = 0; start = 0; tps = []; lags = []; run_ = 0
    for i in range(1, len(px)):
        if trend >= 0 and pxh[i] > pxh[hi]: hi = i
        if trend <= 0 and pxl[i] < pxl[lo]: lo = i
        if daysign == "oc":
            against = (oc[i] < 0) if trend >= 0 else (oc[i] > 0); run_ = run_ + 1 if against else 0
        if trend >= 0:
            leg = pxh[hi] - pxl[start]; dd = pxh[hi] - lp[i]; thr = max(f * max(leg, 0.0), c * sig[i]); thr = min(thr, coarse[i]) if cap else thr
            persisted = (run_ >= n) if daysign == "oc" else (i - hi >= n)
            if dd >= thr and persisted:
                tps.append((hi, "peak")); lags.append(i - hi); trend = -1; start = hi; lo = i; run_ = 0; continue
        if trend <= 0:
            leg = pxh[start] - pxl[lo]; up = lp[i] - pxl[lo]; thr = max(f * max(leg, 0.0), c * sig[i]); thr = min(thr, coarse[i]) if cap else thr
            persisted = (run_ >= n) if daysign == "oc" else (i - lo >= n)
            if up >= thr and persisted:
                tps.append((lo, "trough")); lags.append(i - lo); trend = 1; start = lo; hi = i; run_ = 0
    return tps, trend, (hi if trend > 0 else lo), px, lags


def two_scale(r: pd.Series, fine=None, hl=None, daysign: str = "close"):
    """Coarse legs by the zigzag (the big picture); fine legs by the promoted fine rule inside the current coarse leg (where the move is now).
    fine = (f, n, c) or None (then fine == coarse)."""
    tps_c, trend_c, ext_c, px, thr = turning_points(r); idx = r.index
    if not tps_c or fine is None: return dict(coarse=(tps_c, trend_c, ext_c), fine=None)
    c0 = tps_c[-1][0]; sub = r.iloc[c0:]
    tps_f, trend_f, ext_f, _, lags = turning_points_retrace(sub, *fine, hl=hl, daysign=daysign)
    tps_f = [(p + c0, k) for p, k in tps_f]
    return dict(coarse=(tps_c, trend_c, ext_c), fine=(tps_f, trend_f, ext_f + c0, lags))



# ---------------------------------------------------------------- promoted leg rule (T-I) and the dispatcher every nightly step uses
LEG_RULE = PROC / "leg_rule.json"


def segment(r: pd.Series):
    """Turning points under the promoted leg rule if one is on file (processed/leg_rule.json), else the registered zigzag.
    Returns tps, trend, extreme position, price path, per-session reversal threshold array, and the rule's label for the page."""
    if LEG_RULE.exists():
        j = json.loads(LEG_RULE.read_text())
        if j.get("rule") == "persist":
            n, x, mode = int(j["n"]), float(j["x"]), j.get("mode", "time"); tps, trend, ext, px = turning_points_persist(r, n, x, mode)
            thr = np.full(len(r), x if x > 0 else FLOOR)
            how = (f"{n} consecutive sessions against the trend" if mode == "closes" else f"the price staying off its extreme for {n} sessions")
            return tps, trend, ext, px, thr, f"a reversal needs {how} and a counter-move of at least {x:.0%} (persistence rule, promoted {j.get('promoted', '')})"
    tps, trend, ext, px, thr = turning_points(r)
    return tps, trend, ext, px, thr, "a reversal needs a counter-move of 1.5 × the asset's own monthly volatility, floor 8% (zigzag rule)"


def segmenter_null(asset, rule_name=None, n_shift: int = 20, seed: int = 0):
    """T-I′: the winning segmentation's median explained share on time-shifted factors (legs do not depend on the factors; the attribution does).
    PASS if the real share beats the null median by >= 10 points and its 95th percentile -> the rule is promoted (processed/leg_rule.json)."""
    J = json.loads((PROC / "factor_attribution.json").read_text()); TI = J["tests"][asset]["TI"]
    rule_name = rule_name or (TI["better"][0] if TI.get("better") else None)
    if not rule_name: print("  no rule passed T-I; nothing to test"); return
    import re
    mm = re.match(r"persist-(time|closes) N=(\d+), X=(\d+)%", rule_name)
    if not mm: print(f"  only persistence rules are promotable here ({rule_name})"); return
    mode_, n_, x_ = mm.group(1), int(mm.group(2)), int(mm.group(3)) / 100; P = TI["params"]
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; tps, trend, ext, px = turning_points_persist(r, n_, x_, mode_)
    legs = [(a, b) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP and a >= P["window"] + 10]
    def med_share(Fx):
        v = []
        for a, b in legs:
            cv = attr_curve(r, Fx, idx[a], max_k=min(b - a, MAX_K), window=P["window"])
            if cv is None: continue
            wr = window_rules(cv, min(b - a, MAX_K), 1, P["patience"], P["min_k"])
            if wr and np.isfinite(wr["R5_causal"][1]): v.append(wr["R5_causal"][1])
        return float(np.median(v)) if v else np.nan, len(v)
    real, n = med_share(F); rng = np.random.default_rng(seed); nulls = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns); nulls.append(med_share(Fx)[0])
    nulls = np.array([v for v in nulls if np.isfinite(v)]); med0, p95 = float(np.median(nulls)), float(np.quantile(nulls, .95))
    verdict = "PASS" if (real - med0 >= 0.10 and real > p95) else "FAIL"
    L = [f"# T-I′ null for the winning leg rule — {asset}: {rule_name}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Real median explained share {real:.0%} over {n} legs; on {len(nulls)} time-shifted factor series: median {med0:.0%}, 95th pct {p95:.0%}.*",
         "", f"**{verdict}** — the rule's share on noise is {med0:.0%}; the real series adds {real - med0:+.0%} points." + (f" **Promoted**: legs are cut by this rule from the next run (processed/leg_rule.json); the zigzag stays on record as the superseded rule." if verdict == "PASS" else "")]
    J["tests"][asset]["TInull"] = dict(rule=rule_name, real=real, null_median=med0, null_p95=p95, n_shift=int(len(nulls)), verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    if verdict == "PASS":
        LEG_RULE.write_text(json.dumps(dict(rule="persist", mode=mode_, n=n_, x=x_, promoted=datetime.now().strftime("%Y-%m-%d"), asset_tested=asset, real=real, null_median=med0, superseded="zigzag 1.5x / 8%"), indent=1))
    out = DOCS / f"segmenter_null_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")



def window_test(asset):
    """T-F (prereg_factor_attribution §4): does the causal window rule (R5) explain more than the full episode (R1) on past episodes?
    PASS if R5 > R1 in >= 60% of episodes (n >= 15). R4 is reported as the after-the-fact ceiling, never as a result."""
    r = returns(asset).dropna(); F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index; rows = []
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        if b - a < MIN_EP or a < WINDOW + 10: continue
        direction = 1 if ka == "trough" else -1; s0 = idx[a]; L = b - a
        cv = attr_curve(r, F, s0, max_k=min(L, MAX_K))
        if cv is None: continue
        i0, i1, _ = impulse_window(r, s0, direction, float(thr[a])); k_imp = len(r.loc[i0:i1]) - 1
        wr = window_rules(cv, min(L, MAX_K), k_imp)
        if wr is None: continue
        rows.append(dict(start=s0.strftime("%Y-%m-%d"), L=int(L), **{f"{k}_k": v[0] for k, v in wr.items()}, **{f"{k}_s": v[1] for k, v in wr.items()}))
    df = pd.DataFrame(rows); n = len(df)
    share = float((df.R5_causal_s > df.R1_full_s).mean()) if n else np.nan
    verdict = "INCONCLUSIVE" if n < 15 else ("PASS" if share >= 0.6 else "FAIL")
    med = {k: float(df[f"{k}_s"].median()) for k in ("R1_full", "R2_impulse", "R3_half", "R4_ceiling", "R5_causal")} if n else {}
    L_ = [f"# T-F window rules — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {n} past episodes. Explained share = 1 − |residual| / |move|, reasons only (drift excluded), "
          f"pre-episode sensitivities. R4 is chosen after seeing every window — an in-sample ceiling, shown so the gap to the usable rules is visible.*", "",
          (f"**R5 (causal stop) beats R1 (full episode) in {share:.0%} of episodes → {verdict}**" if n >= 15 else f"**{verdict}** (n {n} < 15)"), "",
          "| rule | median explained share | median window (sessions) |", "|---|---|---|"]
    for k, lab in (("R1_full", "R1 full episode"), ("R2_impulse", "R2 impulse (quarter-threshold)"), ("R3_half", "R3 first half"), ("R5_causal", "R5 causal stop (patience 5)"), ("R4_ceiling", "R4 ceiling — after the fact, not a result")):
        if n: L_.append(f"| {lab} | {med[k]:.0%} | {df[f'{k}_k'].median():.0f} |")
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TF"] = dict(n=n, share=share, verdict=verdict, medians=med, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    out = DOCS / f"window_test_{asset}.md"; out.write_text("\n".join(L_) + "\n"); print("\n".join(L_)); print(f"-> {out}")



def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M"); J = {"run": now, "rule": dict(mult=MULT, floor=FLOOR), "assets": {}}
    tb_all = (json.loads((PROC / "factor_attribution.json").read_text()).get("tests", {}) if (PROC / "factor_attribution.json").exists() else {})
    L = [f"# Why it moved — {now}", "", f"*Turning points: reversal > max({FLOOR:.0%}, {MULT} × 20-session volatility scaled to a month). Attribution: joint fit, "
         "sensitivities from the two years before the episode. Target: base rate of this asset's past episodes in the same direction (median size; quartiles), "
         "UNTESTED as a conditional claim (prereg_factor_attribution §4, prior #62).*", ""]
    for a in ASSETS:
        try:
            r = returns(a).dropna()
        except Exception as e:
            print(f"  {a}: returns unavailable ({type(e).__name__})"); continue
        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r); idx = r.index
        if not tps: continue
        tps_hist = tps                                  # legs used for the base-rate target: whole history at the scale the page describes
        FINE = PROC / "fine_rule.json"; big = None
        if FINE.exists():
            fj = json.loads(FINE.read_text()); ts = two_scale(r, (fj["f"], fj["n"], fj["c"]), hl=(ohlc(a) if fj.get("hl") else None), daysign=fj.get("daysign", "close"))
            if ts["fine"] and ts["fine"][0]:
                c_pos, c_kind = ts["coarse"][0][-1]; big = dict(start=idx[c_pos].strftime("%Y-%m-%d"), direction=(1 if c_kind == "trough" else -1), move=float(np.log(px[-1] / px[c_pos])), sessions=int(len(idx) - 1 - c_pos))
                tps_f, trend_f, ext_f, lags_f = ts["fine"]; tps, trend, ext = tps_f, trend_f, ext_f
                tps_hist = turning_points_retrace(r, fj["f"], fj["n"], fj["c"], True, (ohlc(a) if fj.get("hl") else None), fj.get("daysign", "close"))[0]
                rule_label = (f"big picture by the zigzag; the current leg by the founder's retracement rule — a turn is confirmed when the price has given back "
                              f"{fj['f']:.0%} of the leg's own move (floor {fj['c']}× monthly volatility, never more than the zigzag's threshold) and "
                              f"{'stayed there ' + str(fj['n']) + ' sessions' if fj.get('daysign', 'close') == 'close' else str(fj['n']) + ' open-to-close days have gone against the trend'}"
                              f"{'; extremes taken from the high and low of the day' if fj.get('hl') else ''} (promoted {fj['promoted']})")
        s0_pos, kind = tps[-1]; s0, s1 = idx[s0_pos], idx[-1]; direction = 1 if kind == "trough" else -1
        move = float(np.log(px[-1] / px[s0_pos])); ext_move = float(np.log(px[ext] / px[s0_pos]))
        eps = past_episodes(tps_hist, px); same = [e for e in eps if e["direction"] == direction and e["length"] >= MIN_EP]
        sizes = np.array([abs(e["size"]) for e in same]); lengths = np.array([e["length"] for e in same])
        tgt = None
        if len(sizes) >= 5:
            q25, q50, q75 = np.quantile(sizes, [.25, .5, .75])
            tgt = dict(n=int(len(sizes)), med_size=float(q50), q25=float(q25), q75=float(q75), med_length=float(np.median(lengths)),
                       target_from_start=float(direction * q50), target_from_now=float(direction * q50 - move), band_from_now=[float(direction * q25 - move), float(direction * q75 - move)],
                       share_of_typical=float(abs(move) / q50) if q50 > 0 else None, pct_rank=float((sizes <= abs(move)).mean()), status="base rate of past episodes, UNTESTED as a conditional claim")
        if a not in tb_all:
            try: fa_tests(a); tb_all = json.loads((PROC / "factor_attribution.json").read_text()).get("tests", {})
            except Exception as e: print(f"  {a}: tests failed ({type(e).__name__})")
        ep_attr = attribute(r, F, s0, s1); day_attr = attribute(r, F, s1, s1)
        i0, i1, imp_move = impulse_window(r, s0, direction, float(thr[s0_pos])); imp_attr = attribute(r, F, i0, i1) if i1 != i0 else None
        TB = tb_all.get(a, {}).get("TB", {})
        cv = attr_curve(r, F, s0, max_k=MAX_K); Lnow = len(idx) - 1 - s0_pos
        wr = window_rules(cv, min(Lnow, MAX_K), max(len(r.loc[i0:i1]) - 1, 1)) if cv is not None else None
        tg = tb_all.get(a, {}).get("TG", {}); wr_best = None
        best_leg = None
        bb = (tg.get("by_rule") or {}).get(f"{MULT},{FLOOR}")       # best cell under the registered leg definition -> no re-cut
        if wr and bb and bb.get("p") is not None and bb["p"] < 0.05:
            if (bb["mult"], bb["floor"]) != (MULT, FLOOR):      # the cell's legs are cut by its own reversal rule: re-cut the current leg with it
                tps_b, trend_b, ext_b, px_b, thr_b = turning_points(r, bb["mult"], bb["floor"])
                if tps_b:
                    pb, kb_ = tps_b[-1]; s0b, db = idx[pb], (1 if kb_ == "trough" else -1); Lb = len(idx) - 1 - pb
                    best_leg = dict(start=s0b.strftime("%Y-%m-%d"), direction=db, sessions=int(Lb), move=float(np.log(px_b[-1] / px_b[pb])))
                else: s0b, db, Lb = s0, direction, Lnow
            else: s0b, db, Lb = s0, direction, Lnow
            cvb = attr_curve(r, F, s0b, max_k=MAX_K, window=bb["window"])
            if cvb is not None:
                ib0, ib1, _ = impulse_window(r, s0b, db, float(max(bb["floor"], bb["mult"] * r.rolling(20).std().iloc[-1] * np.sqrt(20))))
                wr_best = window_rules(cvb, min(Lb, MAX_K), max(len(r.loc[ib0:ib1]) - 1, 1), bb["patience"], bb["min_k"])
                if wr_best: wr_best["_attr"] = attribute(r, F, s0b, cvb["dates"][wr_best["R5_causal"][0] - 1])
        c_null = ceiling_null(r, F, s0, min(Lnow, MAX_K)) if cv is not None else np.nan
        tf = tb_all.get(a, {}).get("TF", {})
        r5_attr = attribute(r, F, s0, cv["dates"][wr["R5_causal"][0] - 1]) if wr else None
        J["assets"][a] = dict(name=NAME.get(a, a), episode=dict(start=s0.strftime("%Y-%m-%d"), kind=kind, direction=direction, sessions=int(len(idx) - 1 - s0_pos), move=move,
                                                               extreme_so_far=dict(date=idx[ext].strftime("%Y-%m-%d"), move=ext_move), threshold_now=float(thr[-1]), rule=rule_label, big_picture=big),
                              target=tgt, attribution=ep_attr, impulse=dict(end=i1.strftime("%Y-%m-%d"), sessions=int(len(r.loc[i0:i1]) - 1), move=imp_move, attribution=imp_attr), last_session=dict(date=s1.strftime("%Y-%m-%d"), ret=float(r.iloc[-1]), attribution=day_attr),
                              stable_factors=[f for f, v in TB.items() if v.get("stable")], n_past_episodes=len(eps),
                              windows=({k: dict(sessions=int(v[0]), explained=(None if not np.isfinite(v[1]) else float(v[1])), move=float(cv["move"][v[0] - 1]), end=cv["dates"][v[0] - 1].strftime("%Y-%m-%d")) for k, v in wr.items()} if wr else None),
                              window_test=tf, ceiling_null=(None if not np.isfinite(c_null) else float(c_null)), best_rule=(dict(sessions=int(wr_best['R5_causal'][0]), explained=float(wr_best['R5_causal'][1]), params=bb, p=bb['p'], leg=best_leg, rows=(wr_best['_attr']['rows'][:4] if wr_best.get('_attr') else None)) if wr_best and np.isfinite(wr_best['R5_causal'][1]) else None), r5_rows=(r5_attr["rows"][:4] if r5_attr else None), r5_unexplained=(r5_attr["unexplained_share"] if r5_attr else None))
        pc = lambda v: f"{np.expm1(v):+.1%}"
        L += [f"## {NAME.get(a, a)} ({a})", "",
              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; {rule_label}."
              + (f" Big picture (zigzag): {'up' if big['direction'] > 0 else 'down'} since {big['start']} ({big['sessions']} sessions, {pc(big['move'])})." if big else ""),
              (f"- Typical {'rise' if direction > 0 else 'fall'} of this kind for {NAME.get(a, a)}: {pc(direction * tgt['med_size'])} from the start (middle half of past episodes {pc(direction * tgt['q25'])} to {pc(direction * tgt['q75'])}), "
               f"median {tgt['med_length']:.0f} sessions, n {tgt['n']} — this one is at {tgt['share_of_typical']:.0%} of the typical size; "
               + (f"the typical level is {pc(tgt['target_from_now'])} from here (band {pc(tgt['band_from_now'][0])} to {pc(tgt['band_from_now'][1])})." if tgt['share_of_typical'] < 1
                  else f"it is already beyond the typical size — larger than {tgt['pct_rank']:.0%} of past episodes of this kind; the base rate gives no further level.")
               + " Base rate, UNTESTED as a conditional target." if tgt else "- Fewer than 5 past episodes of this kind: no target."),
              ]
        if imp_attr:
            top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in imp_attr["rows"][:3])
            L.append(f"- **The impulse** (purest stretch, {s0.date()} → {i1.date()}, {len(r.loc[i0:i1]) - 1} sessions, {pc(imp_move)}): {top}; unexplained {imp_attr['unexplained_share']:+.0%}.")
        if wr:
            r4, r5 = wr["R4_ceiling"], wr["R5_causal"]; vtf = tf.get("verdict", "not run")
            L.append(f"- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first {r4[0]} sessions to {cv['dates'][r4[0] - 1].date()}, "
                     f"{pc(float(cv['move'][r4[0] - 1]))}, explained {r4[1]:.0%}. Causal rule (stop after {PATIENCE} sessions without improvement): first {r5[0]} sessions, "
                     f"{pc(float(cv['move'][r5[0] - 1]))}, explained {r5[1] if np.isfinite(r5[1]) else float('nan'):.0%} — T-F {vtf}. "
                     f"Noise calibration of the ceiling: a time-shifted series reaches {c_null:.0%} by the same after-the-fact choice, so the ceiling's excess over noise is {r4[1] - c_null:+.0%} points."
                     + (f" Best swept rule (same leg definition; look-back {bb['window']}, patience {bb['patience']}, min {bb['min_k']}; sub-grid p {bb['p']:.2f})"
                        + (f" cuts the leg as {'up' if best_leg['direction'] > 0 else 'down'} since {best_leg['start']} ({best_leg['sessions']} sessions, {pc(best_leg['move'])})" if best_leg else "")
                        + f": first {wr_best['R5_causal'][0]} sessions, explained {wr_best['R5_causal'][1]:.0%}"
                        + (": " + ", ".join(f"{d['label']} {d['share']:+.0%}" for d in wr_best['_attr']['rows'][:3]) if wr_best.get('_attr') else "") + "." if wr_best else ""))
        if ep_attr:
            top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in ep_attr["rows"][:4])
            L.append(f"- Episode attribution (joint fit): {top}; prior-trend drift {ep_attr['drift'] / ep_attr['actual'] if ep_attr['actual'] else 0:+.0%}; **unexplained {ep_attr['unexplained_share']:+.0%}**. Stable sensitivities: {', '.join(LABEL[f] for f in J['assets'][a]['stable_factors']) or 'none on record'}.")
        if day_attr:
            top = ", ".join(f"{d['label']} {d['contrib']:+.2%}" for d in day_attr["rows"][:3])
            L.append(f"- Last session {s1.date()}: {pc(float(r.iloc[-1]))}; reasons {top}; unexplained {day_attr['resid']:+.2%}.")
        L.append("")
    (PROC / "why_moved.json").write_text(json.dumps(J, indent=1)); (DOCS / "why_moved_latest.md").write_text("\n".join(L) + "\n")
    print("\n".join(L)); print("-> processed/why_moved.json, docs/why_moved_latest.md")


def impulse_test(asset):
    """T-E (prereg_factor_attribution §4): is the impulse window better explained than the whole episode? Past episodes with >= 5 sessions;
    unexplained share |resid/actual| at the impulse vs the full episode, same sensitivities. PASS if the impulse is lower in >= 60% of episodes (n >= 15)."""
    r = returns(asset).dropna(); F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index; rows = []
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        if b - a < MIN_EP or a < WINDOW + 10: continue
        direction = 1 if ka == "trough" else -1; s0, s1 = idx[a], idx[b]
        i0, i1, imp_move = impulse_window(r, s0, direction, float(thr[a])); full = attribute(r, F, s0, s1); imp = attribute(r, F, i0, i1) if i1 != i0 else None
        if not full or not imp: continue
        rows.append(dict(start=s0.strftime("%Y-%m-%d"), end=s1.strftime("%Y-%m-%d"), direction=direction, full_move=full["actual"], imp_sessions=int(len(r.loc[i0:i1]) - 1), imp_move=imp["actual"],
                         full_unexpl=abs(full["unexplained_share"]), imp_unexpl=abs(imp["unexplained_share"])))
    df = pd.DataFrame(rows); n = len(df)
    if n < 15: verdict, share = "INCONCLUSIVE", float("nan")
    else: share = float((df.imp_unexpl < df.full_unexpl).mean()); verdict = "PASS" if share >= 0.6 else "FAIL"
    L = [f"# T-E impulse vs full episode — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {n} past episodes. Unexplained share = |residual / actual| with the same pre-episode sensitivities. "
         f"PASS if the impulse's share is lower in ≥ 60% of episodes.*", "", f"**Impulse better in {share:.0%} of episodes → {verdict}**" if n >= 15 else f"**{verdict}** (n {n} < 15)", "",
         f"Median unexplained share: impulse {df.imp_unexpl.median():.0%} vs full {df.full_unexpl.median():.0%}; median impulse length {df.imp_sessions.median():.0f} sessions, median impulse move {np.expm1(df.imp_move.abs().median()):.1%} of a full move {np.expm1(df.full_move.abs().median()):.1%}." if n else "",
         "", "| start | end | dir | full move | impulse sessions | impulse move | unexplained full | unexplained impulse |", "|---|---|---|---|---|---|---|---|"]
    for _, q in df.tail(25).iterrows():
        L.append(f"| {q.start} | {q.end} | {'up' if q.direction > 0 else 'down'} | {np.expm1(q.full_move):+.1%} | {q.imp_sessions} | {np.expm1(q.imp_move):+.1%} | {q.full_unexpl:.0%} | {q.imp_unexpl:.0%} |")
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TE"] = dict(n=n, share=share, verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M")); (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    out = DOCS / f"impulse_test_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")


def window_null(asset, n_shift: int = 20, seed: int = 0):
    """T-F' (prereg §4): the causal rule picks the best of several windows, so it scores something on noise. Re-run R5 on every past episode with
    the factor series shifted in time (no real relation to the returns), n_shift times. PASS if the real median R5 share exceeds the median of the
    shifted medians by >= 10 points and the 95th percentile of them."""
    r = returns(asset).dropna(); F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index
    eps = [(a, b, 1 if ka == "trough" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP and a >= WINDOW + 10]
    def r5_median(Fx):
        vals = []
        for a, b, d in eps:
            cv = attr_curve(r, Fx, idx[a], max_k=min(b - a, MAX_K))
            if cv is None: continue
            i0, i1, _ = impulse_window(r, idx[a], d, float(thr[a])); wr = window_rules(cv, min(b - a, MAX_K), max(len(r.loc[i0:i1]) - 1, 1))
            if wr and np.isfinite(wr["R5_causal"][1]): vals.append(wr["R5_causal"][1])
        return float(np.median(vals)) if vals else np.nan, len(vals)
    real, n = r5_median(F); rng = np.random.default_rng(seed); nulls = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns); nulls.append(r5_median(Fx)[0])
    nulls = np.array([v for v in nulls if np.isfinite(v)]); med0, p95 = float(np.median(nulls)), float(np.quantile(nulls, .95))
    verdict = "PASS" if (real - med0 >= 0.10 and real > p95) else "FAIL"
    L = [f"# T-F' causal-rule null — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Real median R5 explained share {real:.0%} over {n} episodes; with time-shifted factors ({len(nulls)} shifts): "
         f"median {med0:.0%}, 95th percentile {p95:.0%}. PASS if real ≥ null median + 10 pts and > 95th pct.*", "", f"**{verdict}** — the rule's score on noise is {med0:.0%}; the real series adds {real - med0:+.0%} points."]
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TFnull"] = dict(real=real, null_median=med0, null_p95=p95, n_shift=int(len(nulls)), verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"window_null_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")



def selftest():
    idx = pd.bdate_range("2010-01-01", periods=400); r = pd.Series(0.0, index=idx)
    r.iloc[1:101] = 0.002; r.iloc[101:201] = -0.003; r.iloc[201:301] = 0.0025; r.iloc[301:] = -0.001
    tps, trend, ext, px, thr = turning_points(r)
    kinds = [k for _, k in tps]; assert kinds[:4] == ["trough", "peak", "trough", "peak"], kinds; print("  T1 trough-at-start, peak, trough, peak: PASS")
    assert [p for p, _ in tps[:4]] == [0, 100, 200, 300], tps[:4]; print("  T2 turning points at the true extremes: PASS")
    assert trend == -1 and ext == 399, (trend, ext); print("  T3 current episode down since the last peak, provisional trough at the last session: PASS")
    eps = past_episodes(tps, px); assert eps[1]["direction"] == -1 and abs(eps[1]["size"] + 0.30) < 1e-9; print("  T4 episode sizes: PASS")
    i0, i1, mv = impulse_window(r, idx[100], -1, 0.08); assert abs(mv + 0.12) < 1e-9 and i1 == idx[140], (i1, mv); print("  T5 impulse window runs to the extreme within max_len (40 sessions x -0.3%): PASS")
    print("selftest: 4/4")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "impulse-test": impulse_test(sys.argv[2])
    elif cmd == "window-test": window_test(sys.argv[2])
    elif cmd == "window-null": window_null(sys.argv[2])
    elif cmd == "window-grid": window_grid(sys.argv[2])
    elif cmd == "segmenter-test": segmenter_test(sys.argv[2])
    elif cmd == "segmenter-null": segmenter_null(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else: {"selftest": selftest, "run": run}[cmd]()
