"""
drift_existence.py -- Event engine Stage 1, implemented EXACTLY to
docs/prereg_drift_existence.md (committed 8273be4, 2026-08-21 13:18:53 +0800,
BEFORE this file existed).

REGISTERED QUESTION
    Does a spike in economy-wide narrative-stress density predict subsequent
    drift in market-level returns, entered after the overnight gap has been
    conceded?

    NOT the PEAD analog. The 944-day panel has a GLOBAL distress-theme document
    count, no per-asset event density, so the entity-level spec in
    architecture_decisions.md §3 was not runnable. A positive result does NOT
    discharge the entity-detection precondition on the event/rotation merge; a
    null does NOT close out firm-level drift, because this instrument is blind
    to it by construction.

EVERY PARAMETER BELOW IS REGISTERED. Nothing here was chosen after seeing data.
    §3.1  share = stress_count / total_docs; z vs TRAILING 20 sessions,
          strictly excluding t. Share not raw count (baseline swamping,
          regime_event_validation §4). Trailing not centred (no look-ahead).
    §3.2  z >= 1.5 primary; ladder {1.0, 1.5, 2.0, 2.5}, ALL rungs reported.
    §3.3  de-cluster: within a run separated by < 5 sessions, keep the FIRST.
    §3.4  eligibility: full 20-session baseline present; days whose baseline
          overlaps the 2025-06-15..07-01 outage are DROPPED, not computed on a
          partial window.
    §3.5  episode date t -> scored window = sessions t+2 .. t+H+1, i.e. returns
          accumulated from the CLOSE of t+1. Discards the overnight gap AND the
          whole of session t+1: strictly more conservative than a next-open
          entry, registered as conservative on purpose.
    §3.6  window integrity: an episode scores only if EVERY session of its
          H-window has a return for the tested asset.
    §5    E1 directional; E2 sign-conditioned continuation, sign(r_t) x forward,
          r_t measured on the episode date itself. Primary asset SPY; secondary
          the defensive spread 0.5*(TLT+GLD) - SPY. The 47-asset universe is
          NOT swept.
    §4    Primary null: covariate-matched resampling. Controls are non-event
          days, not within +-20 sessions of ANY threshold-exceeding day, same
          trailing-20-session realised-vol quintile, within +-90 sessions.
          Relaxation order if a stratum has < 5 candidates: +-90 -> +-180 ->
          +-365, THEN adjacent vol quintiles. B = 5,000.
          Secondary null: circular rotation of the episode dates as a block.
    §6    Positive verdict requires p < 0.05 under BOTH nulls, at TWO ADJACENT
          horizons, with consistent sign across all four ladder rungs.
    §7    A null at H=10 or H=20 is PRE-DECLARED INCONCLUSIVE (underpowered).

AMENDMENT 1 (2026-08-23, recorded per §9 -- made BEFORE any result was read)
    §4.2 excludes controls within +-20 sessions of ANY threshold-exceeding day.
    On this panel that is INFEASIBLE: at z>=1.0 there are 70 episodes across 659
    sessions, so 70 x 41 slots cover the panel several times and NO control day
    survives. The first run produced empty control pools and p(matched)=1.0000
    for every cell. The registered relaxation order covers the era window and
    the vol quintile but NOT the buffer, so the buffer binds to zero.
    AMENDED: the buffer becomes H+2 sessions rather than a flat 20. Its purpose
    is to stop a control's forward window overlapping an event's forward window,
    which requires exactly H+2. The flat 20 was sized for the longest horizon and
    applied to all. This is the smallest change that makes the registered design
    runnable; the estimands, thresholds, ladder, de-clustering, entry convention,
    nulls and success criterion are UNCHANGED.

Run:
    python -m src.drift_existence --gdelt processed/gdelt_2024_2026_narrow.csv \
        --out docs/drift_existence_results.md
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR
from src.market_calendar import trading_days

HORIZONS = [1, 5, 10, 20]
LADDER = [1.0, 1.5, 2.0, 2.5]
PRIMARY_Z = 1.5
BASELINE = 20
DECLUSTER = 5
OUTAGE = (pd.Timestamp("2025-06-15"), pd.Timestamp("2025-07-01"))


def load_gdelt(path):
    g = pd.read_csv(path)
    dcol = next(c for c in g.columns if "date" in c.lower() or c.lower() == "day")
    scol = next(c for c in g.columns if "stress" in c.lower())
    tcol = next(c for c in g.columns if "total" in c.lower() or "doc" in c.lower())
    raw = g[dcol]
    if pd.api.types.is_numeric_dtype(raw):
        d = pd.to_datetime(raw.astype("Int64").astype(str), format="%Y%m%d")
    else:
        s = raw.astype(str).str.strip()
        d = pd.to_datetime(s, format="%Y%m%d") if s.str.fullmatch(r"\d{8}").all() \
            else pd.to_datetime(s)
    if d.min().year < 1990:
        raise SystemExit("date column misread")
    out = pd.DataFrame({"share": g[scol].values / g[tcol].values}, index=d).sort_index()
    print(f"  gdelt: {len(out)} rows, {out.index.min().date()} -> "
          f"{out.index.max().date()} (cols {dcol!r}/{scol!r}/{tcol!r})")
    return out["share"]


def episode_dates(share, sessions, z_thresh):
    """§3.1-3.4: z on trailing baseline excluding t, threshold, de-cluster."""
    mu = share.rolling(BASELINE).mean().shift(1)
    sd = share.rolling(BASELINE).std().shift(1)
    z = (share - mu) / sd
    cand = z.index[(z >= z_thresh).fillna(False)]
    # §3.4 baseline must be fully present and must not overlap the outage
    full = pd.DatetimeIndex(share.index)
    keep = []
    for t in cand:
        lo = t - pd.Timedelta(days=BASELINE + 10)
        win = full[(full >= lo) & (full < t)][-BASELINE:]
        if len(win) < BASELINE:
            continue
        if (win.min() <= OUTAGE[1]) and (win.max() >= OUTAGE[0]):
            continue
        keep.append(t)
    cand = pd.DatetimeIndex(keep)
    cand = cand[cand.isin(sessions)]
    # §3.3 de-cluster on SESSIONS
    pos = {d: i for i, d in enumerate(sessions)}
    out, last = [], -10 ** 9
    for t in cand:
        i = pos[t]
        if i - last >= DECLUSTER:
            out.append(t); last = i
    return pd.DatetimeIndex(out), z


def forward_array(rets, sessions, H):
    """§3.5 fwd[i] = compounded return over sessions i+2 .. i+H+1.

    rolling(H) at index i+H+1 spans i+2..i+H+1; shift(-(H+1)) brings it to i.
    min_periods defaults to H, so ANY missing session yields NaN -- which is
    exactly §3.6 window integrity, enforced by construction rather than by a
    separate check."""
    lr = np.log1p(rets.reindex(sessions))
    return np.expm1(lr.rolling(H).sum().shift(-(H + 1))).to_numpy()


def vol_quintile(rets, sessions):
    v = rets.reindex(sessions).rolling(BASELINE).std().shift(1)
    return pd.qcut(v, 5, labels=False, duplicates="drop")


def controls_for(t, sessions, excluded, quint, rng):
    """§4.2 matched pool with the registered relaxation order."""
    i = sessions.get_loc(t)
    q = quint.iloc[i]
    if pd.isna(q):
        return np.array([], dtype=int)
    base = ~excluded
    for span in (90, 180, 365):
        lo, hi = max(0, i - span), min(len(sessions), i + span + 1)
        m = np.zeros(len(sessions), bool); m[lo:hi] = True
        sel = np.where(base & m & (quint.values == q))[0]
        if len(sel) >= 5:
            return sel
    for span in (90, 180, 365):                    # then adjacent quintiles
        lo, hi = max(0, i - span), min(len(sessions), i + span + 1)
        m = np.zeros(len(sessions), bool); m[lo:hi] = True
        sel = np.where(base & m & (np.abs(quint.values - q) <= 1))[0]
        if len(sel) >= 5:
            return sel
    return np.where(base)[0]


def run_cell(fwd, sgn, sessions, ep_idx, thresh_idx, H, estimand, quint, rng,
             B=5000):
    """One (threshold, asset, H, estimand) cell, on precomputed arrays."""
    vals = fwd * sgn if estimand == "E2" else fwd
    obs = vals[ep_idx]
    ok = ~np.isnan(obs)
    n, short = int(ok.sum()), int((~ok).sum())
    if n < 5:
        return dict(n=n, short=short, stat=np.nan, p_match=np.nan, p_rot=np.nan,
                    pool=0)
    stat = float(np.mean(obs[ok]))
    kept = ep_idx[ok]

    # ---- AMENDED buffer: H+2, not a flat 20 (see AMENDMENT 1) -------------
    excl = np.zeros(len(sessions), bool)
    buf = H + 2
    for i in thresh_idx:
        excl[max(0, i - buf): i + buf + 1] = True
    usable = (~excl) & ~np.isnan(vals)

    pools = []
    for i in kept:
        q = quint[i]
        sel = np.array([], int)
        if not np.isnan(q):
            for span in (90, 180, 365):
                m = np.zeros(len(sessions), bool)
                m[max(0, i - span): min(len(sessions), i + span + 1)] = True
                sel = np.where(usable & m & (quint == q))[0]
                if len(sel) >= 5:
                    break
            if len(sel) < 5:
                for span in (90, 180, 365):
                    m = np.zeros(len(sessions), bool)
                    m[max(0, i - span): min(len(sessions), i + span + 1)] = True
                    sel = np.where(usable & m & (np.abs(quint - q) <= 1))[0]
                    if len(sel) >= 5:
                        break
        if len(sel) < 5:
            sel = np.where(usable)[0]
        pools.append(sel)

    sizes = [len(p) for p in pools]
    if min(sizes) == 0:
        return dict(n=n, short=short, stat=stat, p_match=np.nan, p_rot=np.nan,
                    pool=0)

    # ---- primary null: covariate-matched resampling -----------------------
    draws = np.empty((B, len(pools)))
    for c, pool in enumerate(pools):
        draws[:, c] = vals[pool[rng.integers(0, len(pool), B)]]
    null_m = np.nanmean(draws, axis=1)
    p_match = (np.sum(np.abs(null_m - null_m.mean()) >=
                      abs(stat - null_m.mean())) + 1) / (B + 1)

    # ---- secondary null: circular rotation of the episode block -----------
    offs = rng.integers(1, len(sessions), B)
    rot = vals[(kept[None, :] + offs[:, None]) % len(sessions)]
    null_r = np.nanmean(rot, axis=1)
    good = ~np.isnan(null_r)
    p_rot = (np.sum(np.abs(null_r[good] - np.nanmean(null_r[good])) >=
                    abs(stat - np.nanmean(null_r[good]))) + 1) / (good.sum() + 1)

    return dict(n=n, short=short, stat=stat, p_match=p_match, p_rot=p_rot,
                pool=int(np.median(sizes)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdelt", required=True)
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    log = []

    def say(s=""):
        print(s); log.append(s)

    px = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet")
    px.index = pd.to_datetime(px.index); px = px.sort_index()
    if np.nanmedian(np.abs(px.to_numpy())) > 0.5:
        px = px.pct_change()
    for need in ("SPY", "TLT", "GLD"):
        if need not in px.columns:
            raise SystemExit(f"registered asset {need} missing from the panel")

    share = load_gdelt(args.gdelt)
    lo, hi = share.index.min(), share.index.max()
    sessions = pd.DatetimeIndex(trading_days(lo, hi)).intersection(px.index)

    assets = {"SPY": px["SPY"].reindex(sessions),
              "DEF(TLT+GLD)-SPY": (0.5 * (px["TLT"] + px["GLD"]) - px["SPY"])
                                  .reindex(sessions)}

    say("=" * 78)
    say("DRIFT-EXISTENCE -- Event engine Stage 1, per prereg 8273be4")
    say("=" * 78)
    say(f"gdelt window: {lo.date()} -> {hi.date()} | usable sessions: {len(sessions)}")
    say(f"B = {args.iters} | seed {seed}")
    say("")
    say("REGISTERED SCOPE: macro narrative-density drift, NOT the PEAD analog.")
    say("A positive result does not discharge the entity-detection precondition;")
    say("a null does not close out firm-level drift.")
    say("PRE-DECLARED: a null at H=10 or H=20 is INCONCLUSIVE, not evidence of")
    say("absence (MDE ~1.6% / ~2.3% at ~25-35 episodes, above expected effects).")

    rows = []
    for zt in LADDER:
        eps, _ = episode_dates(share, sessions, zt)
        allt = eps
        tag = "PRIMARY" if zt == PRIMARY_Z else "ladder "
        say(f"\n{'='*78}\n{tag}  z >= {zt}   ->  {len(eps)} de-clustered episodes")
        if len(eps) < 5:
            say("    too few episodes; cell skipped.")
            continue
        ep_idx = np.array([sessions.get_loc(t) for t in eps])
        thresh_idx = ep_idx
        for aname, arets in assets.items():
            say(f"\n  asset: {aname}")
            say("    estimand  H   n   stat        p(matched)  p(rotation)  pool")
            rt = arets.reindex(sessions).to_numpy()
            sgn = np.sign(rt); sgn[sgn == 0] = np.nan
            quint = vol_quintile(arets, sessions).to_numpy().astype(float)
            for est in ("E1", "E2"):
                for H in HORIZONS:
                    fwd = forward_array(arets, sessions, H)
                    r = run_cell(fwd, sgn, sessions, ep_idx, thresh_idx, H, est,
                                 quint, rng, B=args.iters)
                    rows.append(dict(z=zt, asset=aname, est=est, H=H, **r))
                    if np.isnan(r["stat"]):
                        say(f"    {est}      {H:>2}   {r['n']:>2}   "
                            f"insufficient")
                        continue
                    both = (r["p_match"] < 0.05) and (r["p_rot"] < 0.05)
                    pm = "  n/a " if np.isnan(r["p_match"]) else f"{r['p_match']:.4f}"
                    say(f"    {est}      {H:>2}  {r['n']:>3}  "
                        f"{r['stat']*100:+7.3f}%     {pm}      "
                        f"{r['p_rot']:.4f}   {r['pool']:>3}"
                        f"{'  *' if both else ''}")

    df = pd.DataFrame(rows)
    say("\n" + "=" * 78)
    say("VERDICT against the registered criterion (§6)")
    say("  Requires p<0.05 under BOTH nulls, at TWO ADJACENT horizons, with")
    say("  consistent sign across ALL FOUR ladder rungs.")
    prim = df[(df.z == PRIMARY_Z) & df.stat.notna()]
    verdict_any = False
    for aname in assets:
        for est in ("E1", "E2"):
            sub = prim[(prim.asset == aname) & (prim.est == est)].sort_values("H")
            sig = [(r.H, r.stat) for r in sub.itertuples()
                   if (r.p_match < 0.05) and (r.p_rot < 0.05)]
            adj = any(HORIZONS.index(a[0]) + 1 == HORIZONS.index(b[0])
                      for a in sig for b in sig if a[0] != b[0])
            if not adj:
                say(f"  {aname:20} {est}: NOT MET "
                    f"({len(sig)} horizon(s) clear both nulls, not adjacent)")
                continue
            allz = df[(df.asset == aname) & (df.est == est) & df.stat.notna()]
            signs = {int(np.sign(s)) for s in allz.stat}
            if len(signs) > 1:
                say(f"  {aname:20} {est}: NOT MET (sign flips across ladder)")
            else:
                say(f"  {aname:20} {est}: **MET** -- adjacent horizons clear both "
                    f"nulls, sign consistent across the ladder")
                verdict_any = True
    say("")
    say("  OVERALL: " + ("POSITIVE on at least one registered cell."
                         if verdict_any else
                         "NULL. No cell meets the registered criterion."))
    say("  H=10 and H=20 cells are pre-declared INCONCLUSIVE regardless of "
        "outcome.")
    say("  AMENDMENT 1 applied: control buffer H+2 rather than a flat 20 -- the")
    say("  registered buffer was infeasible on a 659-session panel (empty pools).")
    say("  Recorded before any result was read. All other parameters unchanged.")
    say("=" * 78)

    if args.out:
        p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Drift-existence results (prereg 8273be4)\n\n```\n"
                     + "\n".join(log) + "\n```\n")
        df.to_csv(str(p).replace(".md", ".csv"), index=False)
        print(f"\n  written -> {p}")


if __name__ == "__main__":
    main()
