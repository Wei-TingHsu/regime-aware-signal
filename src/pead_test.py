"""
pead_test.py -- POST-EARNINGS ANNOUNCEMENT DRIFT, the firm-level event test.

THIS FILE IS THE PRE-REGISTRATION. Every parameter below is fixed. COMMIT IT
BEFORE RUNNING IT -- the git timestamp is the evidence, exactly as 8273be4 was
for drift-existence. If you run first and commit after, this is exploratory and
worth far less.

WHY THIS TEST EXISTS
    The Stage 1 drift-existence null (prereg 8273be4) covers economy-wide
    narrative-stress density predicting MARKET-LEVEL drift. It says nothing
    about firm-specific news predicting THAT FIRM's drift, because the 944-day
    GDELT panel has one global document count and no entity field. That gap was
    recorded as thread 11 and has never been tested.

    PEAD is the canonical event-drift anomaly and has the strongest prior
    support of anything in this project. Concluding "event-driven effects do
    not exist" without testing it would be unsupported.

REGISTERED DESIGN
  Universe   The single names in the panel (Group 3 spotlight). Pooled across
             firms; NOT swept per-firm, and no firm is dropped after seeing
             results.
  Event      Earnings announcement dates from yfinance. Announcement calendar
             date d -> EVENT SESSION t = first NYSE session >= d.
  Timing     yfinance does not reliably flag before-open vs after-close. The
             announcement response is therefore measured over sessions
             {t, t+1} COMBINED, which captures both cases. This is registered
             in advance, not chosen after inspecting the data.
  Abnormal   AR = firm return - (alpha + beta * SPY), beta fit on the trailing
             250 sessions ending the day BEFORE t and FROZEN. No look-ahead,
             no post-event contamination of the beta.
  Signal     ann_AR = compounded AR over {t, t+1}. This is the return-based
             surprise proxy. Analyst-estimate SUE is NOT used: coverage is
             patchy and adding it would create a second specification.
  Drift      fwd_CAR(H) = compounded AR over {t+2 .. t+H+1}. Same conservative
             entry as everywhere else in this project -- the whole announcement
             response window is DISCARDED, so drift cannot be contaminated by
             the announcement move itself.
  Horizons   H in {1, 5, 10, 20} NYSE sessions.
  Estimand   PEAD = mean( sign(ann_AR) x fwd_CAR ). Registered prediction:
             POSITIVE (under-reaction continues in the direction of the
             announcement move). Reversal appears as the negative tail.
  Integrity  An event scores only if every session of its window has a return,
             and only if the trailing beta window has >= 120 observations.
  Nulls      PRIMARY: sign-flip permutation. Randomly flip sign(ann_AR) per
             event; this tests exactly whether the announcement sign carries
             information, holding every return path fixed.
             SECONDARY: sign permutation. Shuffle WHICH sign attaches to
             WHICH event. This preserves the marginal distribution of signs,
             so unlike sign-flip it cannot be passed by a sign imbalance
             alone (e.g. if 60% of announcements were positive).
  Success    p < 0.05 under BOTH nulls at TWO ADJACENT horizons, with the
             registered positive sign. Anything less is reported as observed
             and labelled exploratory.
  Power      With ~240 events and daily AR sigma ~2%, the 80%-power MDE is
             roughly 0.9% at H=5 and 1.8% at H=20. Published PEAD effects have
             weakened since the 1990s; if the true effect is under ~0.5% this
             test cannot see it, and a null must be reported as INCONCLUSIVE
             rather than as evidence of absence.

KNOWN LIMITATION, registered up front
    yfinance earnings history is typically only a few years deep and is not an
    audited source. The number of events retrieved and the date span are
    reported. SEC EDGAR 8-K Item 2.02 is the clean source and remains thread 11.

Run:
    python -m src.pead_test --out docs/pead_results.md
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config, PROCESSED_DIR
from src.market_calendar import trading_days

HORIZONS = [1, 5, 10, 20]
BETA_WIN = 250
MIN_BETA = 120
DEFAULT_NAMES = "NVDA,TSM,ASML,MU,INTC,MSFT,ORCL,PLTR,TSLA,ARM,LMT,SNDK"


def fetch_earnings(tickers, verbose=True):
    import yfinance as yf
    out = {}
    for t in tickers:
        try:
            df = yf.Ticker(t).get_earnings_dates(limit=200)
            if df is None or len(df) == 0:
                if verbose:
                    print(f"    {t:6} no earnings dates returned")
                continue
            d = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
            d = pd.DatetimeIndex(sorted(set(d)))
            out[t] = d
            if verbose:
                print(f"    {t:6} {len(d):3d} dates  "
                      f"{d.min().date()} -> {d.max().date()}")
        except Exception as e:
            if verbose:
                print(f"    {t:6} FAILED: {e}")
    return out


def abnormal_returns(r_firm, r_mkt, sessions, t_idx):
    """Frozen-beta AR path for one event. Returns (ann_AR, {H: fwd_CAR})."""
    b0 = max(0, t_idx - BETA_WIN)
    if t_idx - b0 < MIN_BETA:
        return None
    y = r_firm[b0:t_idx]
    x = r_mkt[b0:t_idx]
    if np.isnan(y).any() or np.isnan(x).any():
        return None
    A = np.vstack([x, np.ones_like(x)]).T
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    ar = r_firm - (beta[0] * r_mkt + beta[1])

    if t_idx + 2 > len(sessions):
        return None
    w = ar[t_idx: t_idx + 2]
    if np.isnan(w).any():
        return None
    ann = float(np.expm1(np.log1p(w).sum()))

    fwd = {}
    for H in HORIZONS:
        s, e = t_idx + 2, t_idx + 2 + H
        if e > len(sessions):
            fwd[H] = np.nan
            continue
        seg = ar[s:e]
        fwd[H] = np.nan if np.isnan(seg).any() else \
            float(np.expm1(np.log1p(seg).sum()))
    return ann, fwd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", default=DEFAULT_NAMES)
    ap.add_argument("--market", default="SPY")
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
    if args.market not in px.columns:
        raise SystemExit(f"market proxy {args.market} not in panel")

    names = [n.strip() for n in args.names.split(",") if n.strip() in px.columns]
    missing = [n.strip() for n in args.names.split(",") if n.strip() not in px.columns]
    sessions = px.index
    pos = {d: i for i, d in enumerate(sessions)}
    r_mkt = px[args.market].to_numpy()

    say("=" * 78)
    say("PEAD -- post-earnings announcement drift (firm-level event test)")
    say("=" * 78)
    say(f"universe: {', '.join(names)}")
    if missing:
        say(f"not in panel, skipped: {', '.join(missing)}")
    say(f"market proxy: {args.market} | beta: trailing {BETA_WIN} frozen at t")
    say(f"iters {args.iters} | seed {seed}")
    say("")
    say("Announcement response measured over {t, t+1} COMBINED (yfinance does")
    say("not flag BMO/AMC). Drift measured from t+2 -- the entire announcement")
    say("window is DISCARDED, so drift cannot be contaminated by it.")
    say("\nfetching earnings dates:")
    eds = fetch_earnings(names)
    for t, d in eds.items():
        log.append(f"    {t:6} {len(d):3d} dates  {d.min().date()} -> {d.max().date()}")
    if not eds:
        raise SystemExit("no earnings dates retrieved -- check network / yfinance")

    ann_all, fwd_all, firm_all, date_all = [], [], [], []
    dropped = 0
    for tk, dates in eds.items():
        rf = px[tk].to_numpy()
        for d in dates:
            later = sessions[sessions >= d]
            if len(later) == 0:
                dropped += 1
                continue
            ti = pos[later[0]]
            res = abnormal_returns(rf, r_mkt, sessions, ti)
            if res is None:
                dropped += 1
                continue
            ann, fwd = res
            if ann == 0 or np.isnan(ann):
                dropped += 1
                continue
            ann_all.append(ann); fwd_all.append(fwd)
            firm_all.append(tk); date_all.append(sessions[ti])

    ann = np.array(ann_all)
    say(f"\nusable events: {len(ann)}  (dropped {dropped} for short beta window, "
        f"missing sessions, or zero announcement return)")
    if len(ann) < 30:
        say("FEWER THAN 30 EVENTS -- no statistic below carries meaningful power.")
    say(f"span: {min(date_all).date()} -> {max(date_all).date()}")
    say(f"mean |announcement AR| = {np.mean(np.abs(ann))*100:.2f}%")

    sgn = np.sign(ann)
    say("\n  H    n    PEAD stat   p(sign-flip)  p(rotation)   hit")
    rows = []
    for H in HORIZONS:
        f = np.array([x[H] for x in fwd_all])
        ok = ~np.isnan(f)
        n = int(ok.sum())
        if n < 10:
            say(f"  {H:>2}  {n:>3}   insufficient")
            continue
        pay = sgn[ok] * f[ok]
        stat = float(pay.mean())

        flips = rng.choice([-1.0, 1.0], size=(args.iters, n))
        null1 = (flips * f[ok]).mean(axis=1)
        p1 = (np.sum(np.abs(null1) >= abs(stat)) + 1) / (args.iters + 1)

        # SECONDARY null: permute WHICH sign goes with WHICH event. Unlike
        # sign-flip this preserves the marginal distribution of signs (if 60%
        # of announcements were positive, every draw keeps 60% positive), so
        # it cannot be passed by a sign imbalance alone.
        null2 = np.array([(rng.permutation(sgn[ok]) * f[ok]).mean()
                          for _ in range(args.iters)])
        p2 = (np.sum(np.abs(null2 - null2.mean()) >=
                     abs(stat - null2.mean())) + 1) / (args.iters + 1)

        rows.append(dict(H=H, n=n, stat=stat, p1=p1, p2=p2))
        both = (p1 < 0.05) and (p2 < 0.05)
        say(f"  {H:>2}  {n:>3}   {stat*100:+7.3f}%    {p1:.4f}        "
            f"{p2:.4f}     {(pay>0).mean():.0%}{'  *' if both else ''}")

    say("\n" + "=" * 78)
    say("VERDICT against the registered criterion")
    sig = [r for r in rows if r["p1"] < 0.05 and r["p2"] < 0.05 and r["stat"] > 0]
    adj = any(HORIZONS.index(a["H"]) + 1 == HORIZONS.index(b["H"])
              for a in sig for b in sig if a["H"] != b["H"])
    if adj:
        say("  **MET** -- PEAD detected: two adjacent horizons clear both nulls")
        say("  with the registered positive sign. This is firm-level event drift,")
        say("  and it is the FIRST positive result in the project. Next step is a")
        say("  pre-registered out-of-sample confirmation, not a claim.")
    else:
        say(f"  NOT MET ({len(sig)} horizon(s) clear both nulls with the")
        say("  registered sign; not adjacent).")
        say("  Scope: pooled across firms, return-based surprise proxy, drift")
        say("  measured from t+2. A null here does NOT rule out PEAD measured")
        say("  with analyst-estimate SUE, at intraday resolution, or on the")
        say("  announcement window itself -- none of which this test examines.")
    say("=" * 78)

    if args.out:
        p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# PEAD results\n\n```\n" + "\n".join(log) + "\n```\n")
        pd.DataFrame(dict(firm=firm_all, date=date_all, ann=ann)).to_csv(
            str(p).replace(".md", "_events.csv"), index=False)
        print(f"\n  written -> {p}")


if __name__ == "__main__":
    main()
