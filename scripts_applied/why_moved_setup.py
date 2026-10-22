"""23 Oct: (1) fix BEA error reporting + key names, BTC fetch reporting, silver (SLV) as an attribution asset; (2) src/why_moved.py — nightly
turning points, current-episode and last-session attribution, episode-size target (TRACK 3.33); (3) registration + nightly hook.
Run from the repo root:  python scripts_applied/why_moved_setup.py ; python -m src.why_moved selftest ; python -m src.why_moved run ; python -m src.issuer_pool build 2>&1 | tail -12"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. fixes
ip = Path("src/issuer_pool.py"); s = ip.read_text()
if "BEA_KEY" in s: print("  issuer_pool fixes: already")
else:
    s = s.replace('    key = os.environ.get("BEA_API_KEY") or _env("BEA_API_KEY")',
                  '    key = next((v for v in (os.environ.get(n) or _env(n) for n in ("BEA_API_KEY", "BEA_KEY", "BEA_USERID", "BEA_USER_ID", "BEAKEY")) if v), "")\n'
                  '    if not key: raise RuntimeError("no BEA key found in .env (tried BEA_API_KEY, BEA_KEY, BEA_USERID, BEA_USER_ID, BEAKEY)")', 1)
    s = s.replace('    rows = js["BEAAPI"]["Results"]["Data"]',
                  '    res = js.get("BEAAPI", {}).get("Results", {})\n    if "Data" not in res: raise RuntimeError("BEA said: " + json.dumps(res or js)[:300])\n    rows = res["Data"]', 1)
    s = s.replace('        q, d = bea_contributions(year - 1); print(f"  BEA {year} unavailable ({type(e).__name__}); using {q}")',
                  '        print(f"  BEA {year}: {e}")\n        q, d = bea_contributions(year - 1); print(f"  using {q}")', 1)
    ip.write_text(s); print("  issuer_pool fixes: BEA error text, key names")

fa = Path("src/factor_attribution.py"); s = fa.read_text()
if "extra_returns.parquet" in s: print("  factor_attribution fixes: already")
else:
    s = s.replace('        except Exception: pass\n    if bp.exists():', '        except Exception as e: print(f"  BTC fetch failed: {type(e).__name__}: {str(e)[:80]}")\n    if bp.exists():', 1)
    s = s.replace('    if missing: L.append(f"Proxies unavailable on disk: {\', \'.join(missing)} (run fetch-gpr for the war factor).\\n")',
                  '    if missing: L.append(f"Proxies unavailable on disk: {\', \'.join(missing)}.\\n")', 1)
    old = s[s.index("def returns(asset: str) -> pd.Series:"):s.index("# ---------------------------------------------------------------- the decomposition")]
    new = '''EXTRA = {"SLV": "SLV", "SILVER": "SI=F", "GOLD": "GC=F", "COPPER": "HG=F", "BRENT": "BZ=F"}


def returns(asset: str) -> pd.Series:
    """Daily log returns: the panel's assets, or an extra instrument (silver etc.) fetched once from Yahoo into processed/extra_returns.parquet."""
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if asset in r.columns: return r[asset]
    cache = PROC / "extra_returns.parquet"; ex = pd.read_parquet(cache) if cache.exists() else pd.DataFrame()
    if cache.exists(): ex.index = pd.to_datetime(ex.index)
    if asset not in ex.columns or (len(ex) and (r.index[-1] - ex[asset].dropna().index[-1]).days > 3):
        import yfinance as yf
        h = yf.Ticker(EXTRA.get(asset, asset)).history(period="max", interval="1d", auto_adjust=True)["Close"]
        h.index = pd.to_datetime(h.index).tz_localize(None).normalize(); lr = np.log(h).diff().rename(asset)
        ex = ex.drop(columns=[asset], errors="ignore").join(lr, how="outer") if len(ex) else lr.to_frame(); ex.to_parquet(cache)
    return ex[asset].reindex(r.index)


'''
    s = s.replace(old, new, 1); fa.write_text(s); print("  factor_attribution fixes: BTC error text, extra instruments (SLV, SILVER, GOLD, COPPER, BRENT)")

# ---------------------------------------------------------------- 2. why_moved
wm = Path("src/why_moved.py")
if wm.exists(): print("  why_moved.py: already")
else:
    wm.write_text(r'''"""
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
from src.factor_attribution import factors, returns, joint_fit, ORDER_DEFAULT, LABEL, WINDOW

PROC, DOCS = Path("processed"), Path("docs")
ASSETS = ["SPY", "TLT", "GLD", "SLV", "UUP", "USO"]
NAME = {"SPY": "US equities", "TLT": "long Treasuries", "GLD": "gold", "SLV": "silver", "UUP": "the dollar", "USO": "oil"}
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
    if len(win) < 250 or len(ep) < 1: return None
    b = joint_fit(win.r.to_numpy(), win[avail].to_numpy()); sums = ep[avail].sum().to_numpy(); contrib = b * sums; actual = float(ep.r.sum())
    drift = float((win.r.mean() - win[avail].mean().to_numpy() @ b) * len(ep)); resid = actual - contrib.sum() - drift
    rows = [dict(factor=f, label=LABEL[f], beta=float(bb), move=float(sm), contrib=float(c), share=(float(c / actual) if actual else 0.0))
            for f, bb, sm, c in zip(avail, b, sums, contrib)]
    rows.sort(key=lambda d: -abs(d["contrib"]))
    return dict(actual=actual, sessions=int(len(ep)), rows=rows, drift=drift, resid=float(resid), unexplained_share=(float(resid / actual) if actual else 0.0))


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
                       share_of_typical=float(abs(move) / q50) if q50 > 0 else None, status="base rate of past episodes, UNTESTED as a conditional claim")
        ep_attr = attribute(r, F, s0, s1); day_attr = attribute(r, F, s1, s1)
        TB = tb_all.get(a, {}).get("TB", {})
        J["assets"][a] = dict(name=NAME.get(a, a), episode=dict(start=s0.strftime("%Y-%m-%d"), kind=kind, direction=direction, sessions=int(len(idx) - 1 - s0_pos), move=move,
                                                               extreme_so_far=dict(date=idx[ext].strftime("%Y-%m-%d"), move=ext_move), threshold_now=float(thr[-1])),
                              target=tgt, attribution=ep_attr, last_session=dict(date=s1.strftime("%Y-%m-%d"), ret=float(r.iloc[-1]), attribution=day_attr),
                              stable_factors=[f for f, v in TB.items() if v.get("stable")], n_past_episodes=len(eps))
        pc = lambda v: f"{np.expm1(v):+.1%}"
        L += [f"## {NAME.get(a, a)} ({a})", "",
              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; reversal threshold now {thr[-1]:.1%}.",
              (f"- Typical {'rise' if direction > 0 else 'fall'} of this kind for {NAME.get(a, a)}: {pc(direction * tgt['med_size'])} from the start [{pc(direction * tgt['q25'])}, {pc(direction * tgt['q75'])}], "
               f"median {tgt['med_length']:.0f} sessions, n {tgt['n']} — this one is at {tgt['share_of_typical']:.0%} of the typical size; from here that is {pc(tgt['target_from_now'])} "
               f"(band {pc(tgt['band_from_now'][0])} to {pc(tgt['band_from_now'][1])}). Base rate, UNTESTED as a conditional target." if tgt else "- Fewer than 5 past episodes of this kind: no target."),
              ]
        if ep_attr:
            top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in ep_attr["rows"][:4])
            L.append(f"- Episode attribution (joint fit): {top}; prior-trend drift {ep_attr['drift'] / ep_attr['actual'] if ep_attr['actual'] else 0:+.0%}; **unexplained {ep_attr['unexplained_share']:+.0%}**. Stable sensitivities: {', '.join(LABEL[f] for f in J['assets'][a]['stable_factors']) or 'none on record'}.")
        if day_attr:
            top = ", ".join(f"{d['label']} {d['contrib']:+.2%}" for d in day_attr["rows"][:3])
            L.append(f"- Last session {s1.date()}: {pc(float(r.iloc[-1]))}; reasons {top}; unexplained {day_attr['resid']:+.2%}.")
        L.append("")
    (PROC / "why_moved.json").write_text(json.dumps(J, indent=1)); (DOCS / "why_moved_latest.md").write_text("\n".join(L) + "\n")
    print("\n".join(L)); print("-> processed/why_moved.json, docs/why_moved_latest.md")


def selftest():
    idx = pd.bdate_range("2010-01-01", periods=400); r = pd.Series(0.0, index=idx)
    r.iloc[1:101] = 0.002; r.iloc[101:201] = -0.003; r.iloc[201:301] = 0.0025; r.iloc[301:] = -0.001
    tps, trend, ext, px, thr = turning_points(r)
    kinds = [k for _, k in tps]; assert kinds[:3] == ["peak", "trough", "peak"], kinds; print("  T1 peak/trough sequence: PASS")
    assert tps[0][0] == 100 and tps[1][0] == 200, tps[:2]; print("  T2 turning points at the true extremes: PASS")
    assert trend == -1 and ext == 399, (trend, ext); print("  T3 current episode down since the last peak, provisional trough at the last session: PASS")
    eps = past_episodes(tps, px); assert eps[0]["direction"] == -1 and abs(eps[0]["size"] + 0.30) < 1e-9; print("  T4 episode sizes: PASS")
    print("selftest: 4/4")


if __name__ == "__main__":
    {"selftest": selftest, "run": run}[sys.argv[1] if len(sys.argv) > 1 else "run"]()
''')
    print("  why_moved.py: written")

d = Path("daily_run.sh"); s = d.read_text()
if "src.why_moved" in s: print("  daily_run why_moved: already")
else:
    old = 'python -m src.latency_audit || echo "  latency audit failed -- continuing"\n'
    if old not in s: print("  daily_run latency anchor not found -- add by hand: python -m src.why_moved run || echo \"  why_moved failed -- continuing\"")
    else: d.write_text(s.replace(old, old + '# TRACK 3.33: turning points, episode and last-session attribution, base-rate target, every asset incl. silver\npython -m src.why_moved run > /dev/null || echo "  why_moved failed -- continuing"\n', 1)); print("  daily_run why_moved: hooked")

# ---------------------------------------------------------------- 3. registration
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "## 4. Daily" in s: print("  prereg §4: already")
else:
    s = s.replace("## Amendments\n", """## 4. Daily "why it moved" block and the target (registered 2026-10-23, before code)
- **Turning points** per asset by an adaptive reversal rule: a peak or trough is confirmed when price moves against the trend by more than
  max(8%, 1.5 × the asset's 20-session volatility scaled to a month). Both constants are grid variables (SPEC_GRID). The current episode runs
  from the last confirmed turning point to the last session. Assets: the five model markets and silver (SLV).
- **Attribution** of the current episode and of the last session (joint fit, sensitivities from the 504 sessions before the episode start),
  unexplained share stated; factor dollars quotable only where T-A has passed and T-B marks the factor stable.
- **Target.** Base rate: the median size of this asset's past episodes in the same direction (quartile band, n ≥ 5) → "from here" distance and
  level; labelled base rate. **T-D (the conditional claim):** does the episode's attribution profile at the current point predict its remaining
  size better than the base rate? Walk-forward ridge on past episodes' profiles at their midpoint; criterion MAE ≥ 10% below the base rate on
  ≥ 60% of held-out episodes, n ≥ 30 per asset. **Prior #62 (Claude):** FAIL or INCONCLUSIVE — the profile adds little to the size base rate.
- Nightly: `src/why_moved.py`; app: the "Why it moved" paragraph beside the day's Up/Down pill, every sentence tagged.

## Amendments
""", 1)
    p.write_text(s); print("  prereg §4: added")
t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "## 4. Potential upgrades — not registered, not costed\n"
if "### 3.33 Why it moved" in s: print("  TRACK 3.33: already")
else:
    add = """### 3.33 Why it moved — daily reasons, episode and target on the app (registered 23 Oct; built, app wiring next)

Founder's picture: an investor opens the site, sees why today's move happened, what the current trend has typically run to, and the day's
wind direction, and decides for themselves. Nightly per asset incl. silver: adaptive turning points (reversal > max(8%, 1.5 × monthly vol)),
current episode and last-session attribution with the unexplained share, base-rate target from past episode sizes (labelled), T-D registered
for the conditional target (prior #62). `src/why_moved.py`, prereg_factor_attribution §4; hooked in daily_run.

"""
    t.write_text(s.replace(anchor, add + anchor, 1)); print("  TRACK 3.33: done")
print("done -- python -m src.why_moved selftest ; python -m src.why_moved run")
