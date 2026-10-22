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


def turning_points(r: pd.Series):
    """Zigzag with an adaptive threshold. Returns list of (position, 'peak'|'trough'), current trend (+1/-1/0), provisional extreme position."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy())
    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20); thr = np.maximum(FLOOR, MULT * sig)
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


def attr_curve(r: pd.Series, F: pd.DataFrame, s0, max_k: int = MAX_K):
    """For windows of 1..max_k sessions after the turning point s0: cumulative move, the reasons' explained part (pre-episode sensitivities,
    drift excluded), residual, and the explained share 1 - |resid|/|move| (NaN while the move is under 1%)."""
    avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    win = F.loc[:s0].iloc[-WINDOW - 1:-1][avail].join(r.rename("r")).dropna(); ep = F.loc[s0:][avail].join(r.rename("r")).dropna().iloc[1:max_k + 1]
    if len(win) < 250 or len(ep) < 3: return None
    b = joint_fit(win.r.to_numpy(), win[avail].to_numpy())
    cF = ep[avail].cumsum().to_numpy(); cr = ep.r.cumsum().to_numpy(); explained = cF @ b; resid = cr - explained
    score = 1 - np.abs(resid) / np.maximum(np.abs(cr), 1e-9); score[np.abs(cr) < 0.01] = np.nan
    return dict(k=np.arange(1, len(ep) + 1), move=cr, explained=explained, score=score, dates=ep.index)


def window_rules(curve, L: int, k_imp: int):
    """Scores under each rule for an episode of L sessions. R4 is chosen after the fact (a ceiling); R5 walks forward and stops when the
    score has not improved for PATIENCE sessions (causal, usable live)."""
    sc = curve["score"][:L]; n = len(sc)
    if n == 0: return None
    out = {"R1_full": (n, float(sc[n - 1])), "R2_impulse": (min(k_imp, n), float(sc[min(k_imp, n) - 1]) if k_imp >= 1 else np.nan), "R3_half": (max(n // 2, 1), float(sc[max(n // 2, 1) - 1]))}
    fin = np.where(np.isfinite(sc))[0]
    out["R4_ceiling"] = (int(fin[np.nanargmax(sc[fin])]) + 1, float(np.nanmax(sc[fin]))) if len(fin) else (n, np.nan)
    if n < MIN_K:
        out["R5_causal"] = (n, float(sc[n - 1])); return out
    best, kb, since = -np.inf, MIN_K, 0
    for k in range(MIN_K, n + 1):
        v = sc[k - 1]
        if np.isfinite(v) and v > best: best, kb, since = v, k, 0
        else: since += 1
        if since >= PATIENCE: break
    out["R5_causal"] = (kb, float(best) if np.isfinite(best) else np.nan)
    return out


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
        F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index
        if not tps: continue
        s0_pos, kind = tps[-1]; s0, s1 = idx[s0_pos], idx[-1]; direction = 1 if kind == "trough" else -1
        move = float(np.log(px[-1] / px[s0_pos])); ext_move = float(np.log(px[ext] / px[s0_pos]))
        eps = past_episodes(tps, px); same = [e for e in eps if e["direction"] == direction and e["length"] >= MIN_EP]
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
        tf = tb_all.get(a, {}).get("TF", {})
        r5_attr = attribute(r, F, s0, cv["dates"][wr["R5_causal"][0] - 1]) if wr else None
        J["assets"][a] = dict(name=NAME.get(a, a), episode=dict(start=s0.strftime("%Y-%m-%d"), kind=kind, direction=direction, sessions=int(len(idx) - 1 - s0_pos), move=move,
                                                               extreme_so_far=dict(date=idx[ext].strftime("%Y-%m-%d"), move=ext_move), threshold_now=float(thr[-1])),
                              target=tgt, attribution=ep_attr, impulse=dict(end=i1.strftime("%Y-%m-%d"), sessions=int(len(r.loc[i0:i1]) - 1), move=imp_move, attribution=imp_attr), last_session=dict(date=s1.strftime("%Y-%m-%d"), ret=float(r.iloc[-1]), attribution=day_attr),
                              stable_factors=[f for f, v in TB.items() if v.get("stable")], n_past_episodes=len(eps),
                              windows=({k: dict(sessions=int(v[0]), explained=(None if not np.isfinite(v[1]) else float(v[1])), move=float(cv["move"][v[0] - 1]), end=cv["dates"][v[0] - 1].strftime("%Y-%m-%d")) for k, v in wr.items()} if wr else None),
                              window_test=tf, r5_rows=(r5_attr["rows"][:4] if r5_attr else None), r5_unexplained=(r5_attr["unexplained_share"] if r5_attr else None))
        pc = lambda v: f"{np.expm1(v):+.1%}"
        L += [f"## {NAME.get(a, a)} ({a})", "",
              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; reversal threshold now {thr[-1]:.1%}.",
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
                     f"{pc(float(cv['move'][r5[0] - 1]))}, explained {r5[1] if np.isfinite(r5[1]) else float('nan'):.0%} — T-F {vtf}.")
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
    else: {"selftest": selftest, "run": run}[cmd]()
