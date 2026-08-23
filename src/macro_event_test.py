"""
macro_event_test.py -- drift around SCHEDULED macro events, entered at a window
that is actually tradeable.

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.

WHY THE ENTRY CONVENTION CHANGES HERE
    Every prior event test in this project entered at t+2. The NVDA spillover
    result (2026-08-23) showed why they were all null: the semiconductor complex
    repriced ENTIRELY in the overnight gap -- 5/7 peers significant on GAP, then
    0/7 INTRA and 0/7 NEXT. The event was over before t+2 began. The engine was
    never broken; the entry convention was blind.

    Scheduled macro events land MID-SESSION, not overnight. An FOMC statement is
    released at 14:00 ET. So the windows are different from an earnings release:

      PRE    = open(N)/close(N-1)-1   overnight into the decision day. Contains
                                      the pre-FOMC drift anomaly (Lucca &
                                      Moench). Tradeable ONLY by holding
                                      overnight beforehand.
      DAY    = close(N)/open(N)-1     the session containing the 14:00 release.
                                      Daily bars CANNOT separate the pre-2pm
                                      part from the reaction -- stated, not
                                      hidden.
      NEXT_h = close(N+h)/close(N)-1  from the CLOSE of the decision day. This
                                      is the first fully tradeable post-event
                                      window: the statement is public, the
                                      session has closed, and entry is at a
                                      price everyone could get.

    NEXT_h is the estimand that matters. h in {1, 2, 3, 5}.

TWO QUESTIONS, BOTH REGISTERED
  Q1 UNCONDITIONAL  Is the mean NEXT_h return after events different from
                    non-event days? Null: date rotation -- shift the whole event
                    block by a random offset, preserving spacing and the return
                    series intact.
  Q2 SIGN-CONDITIONED  Does the decision-day move CONTINUE or REVERSE?
                    stat = mean( sign(DAY) x NEXT_h ). sign(DAY) is known at the
                    close of N, so entering at that close is legitimate -- no
                    look-ahead. Positive = continuation, negative = reversal.
                    Nulls: sign-flip and sign-permutation.

REGISTERED PARAMETERS
    Assets     --assets, default SPY,TLT,GLD,UUP -- one risk asset, one duration,
               one metal, one dollar. Not swept over the universe.
    Horizons   h in {1, 2, 3, 5} sessions.
    Adjustment Raw returns. NOT market-adjusted: a scheduled macro event moves
               the whole market, so removing the market would remove the effect.
               (This is the opposite of the earnings-spillover case, and the
               reason is the opposite too.)
    Success    p < 0.05 under all applicable nulls at TWO ADJACENT horizons.
               A single horizon is not a result.
    Power      ~200 FOMC events since 2000. With daily SPY sigma ~1.2%, the
               80%-power MDE is roughly 0.24% at h=1 and 0.53% at h=5. Effects
               smaller than that are invisible here and a null must be reported
               as inconclusive at those magnitudes.

Run:
    python -m src.macro_event_test --dates processed/fomc_decisions.csv \
        --label FOMC --out docs/fomc_drift.md
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config

HORIZONS = [1, 2, 3, 5]


def fetch_ohlc(tickers, start="1999-01-01"):
    import yfinance as yf
    df = yf.download(tickers, start=start, auto_adjust=True, progress=False,
                     group_by="ticker", threads=True)
    out = {}
    for t in tickers:
        try:
            sub = df[t][["Open", "Close"]].dropna()
            if len(sub) > 200:
                out[t] = sub
        except Exception:
            pass
    return out


def windows(ohlc, i, hs):
    o = ohlc["Open"].to_numpy(); c = ohlc["Close"].to_numpy()
    if i < 1 or i >= len(c):
        return None
    d = dict(PRE=o[i] / c[i - 1] - 1, DAY=c[i] / o[i] - 1)
    for h in hs:
        d[f"NEXT_{h}"] = c[i + h] / c[i] - 1 if i + h < len(c) else np.nan
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", required=True)
    ap.add_argument("--label", default="EVENT")
    ap.add_argument("--assets", default="SPY,TLT,GLD,UUP")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    assets = [a.strip() for a in args.assets.split(",")]
    log = []

    def say(s=""):
        print(s); log.append(s)

    dts = pd.read_csv(args.dates)
    col = next(c for c in dts.columns if "date" in c.lower())
    ev = pd.DatetimeIndex(pd.to_datetime(dts[col])).sort_values()

    say("=" * 78)
    say(f"SCHEDULED MACRO EVENT DRIFT -- {args.label}")
    say("=" * 78)
    say(f"dates: {len(ev)} from {args.dates}, "
        f"{ev.min().date()} -> {ev.max().date()}")
    say(f"assets: {', '.join(assets)} | iters {args.iters} | seed {seed}")
    say("")
    say("PRE    = open(N)/close(N-1)-1   overnight into the event day")
    say("DAY    = close(N)/open(N)-1     session containing the release;")
    say("                                daily bars cannot split pre/post release")
    say("NEXT_h = close(N+h)/close(N)-1  FIRST FULLY TRADEABLE window  <-- the test")
    say("")
    say("Entry convention changed from t+2 deliberately: the NVDA spillover result")
    say("showed events fully reprice before t+2, so every earlier null measured an")
    say("empty window. Raw returns, NOT market-adjusted -- a macro event moves the")
    say("whole market and adjusting would remove the effect being measured.")

    say("\nfetching adjusted OHLC ...")
    ohlc = fetch_ohlc(assets)
    for a in assets:
        if a not in ohlc:
            say(f"  {a}: no data, dropped")
    assets = [a for a in assets if a in ohlc]

    for a in assets:
        px = ohlc[a]
        sess = px.index
        idx = [sess.get_loc(sess[sess >= d][0]) for d in ev
               if len(sess[sess >= d]) and sess[sess >= d][0] - d <= pd.Timedelta("5D")]
        idx = sorted(set(i for i in idx if 250 < i < len(sess) - 6))
        if len(idx) < 30:
            say(f"\n{a}: only {len(idx)} usable events -- skipped")
            continue

        rows = [windows(px, i, HORIZONS) for i in idx]
        df = pd.DataFrame([r for r in rows if r])
        say(f"\n{a}: {len(df)} events, "
            f"{sess[idx[0]].date()} -> {sess[idx[-1]].date()}")
        say(f"  mean PRE {df['PRE'].mean()*100:+.3f}%   "
            f"mean DAY {df['DAY'].mean()*100:+.3f}%")

        c = px["Close"].to_numpy()
        say("   h    n    Q1 uncond   p(rot)    Q2 signed   p(flip)  p(perm)")
        for h in HORIZONS:
            v = df[f"NEXT_{h}"].to_numpy()
            ok = ~np.isnan(v)
            n = int(ok.sum())
            if n < 30:
                continue
            # Q1: unconditional mean vs rotated event block
            m = float(v[ok].mean())
            ai = np.array(idx)[ok]
            null_r = np.empty(args.iters)
            for b in range(args.iters):
                off = rng.integers(1, len(sess))
                j = (ai + off) % (len(sess) - h - 1)
                null_r[b] = np.nanmean(c[j + h] / c[j] - 1)
            p_r = (np.sum(np.abs(null_r - null_r.mean()) >=
                          abs(m - null_r.mean())) + 1) / (args.iters + 1)
            # Q2: sign-conditioned on DAY (known at close N)
            s = np.sign(df["DAY"].to_numpy()[ok]); s[s == 0] = 1
            st = float((s * v[ok]).mean())
            n1 = (rng.choice([-1.0, 1.0], size=(args.iters, n)) * v[ok]).mean(axis=1)
            p1 = (np.sum(np.abs(n1) >= abs(st)) + 1) / (args.iters + 1)
            n2 = np.array([(rng.permutation(s) * v[ok]).mean()
                           for _ in range(args.iters)])
            p2 = (np.sum(np.abs(n2 - n2.mean()) >= abs(st - n2.mean())) + 1) / \
                 (args.iters + 1)
            star = " *" if (p1 < 0.05 and p2 < 0.05) else ""
            say(f"  {h:>2}  {n:>4}  {m*100:+8.3f}%  {p_r:.4f}   "
                f"{st*100:+8.3f}%   {p1:.4f}   {p2:.4f}{star}")

    say("\n" + "=" * 78)
    say("READING")
    say("  Q1 asks whether returns after the event differ from ordinary days.")
    say("  Q2 asks whether the event-day move continues (+) or reverses (-),")
    say("  entered at the close of the event day -- no look-ahead.")
    say("  A single significant horizon is NOT a result; two adjacent are needed.")
    say("  PRE and DAY are reported for context. Daily bars cannot separate the")
    say("  pre-release part of DAY from the reaction, so DAY is not a trade.")
    say(f"  Multiple testing: {len(assets)} assets x {len(HORIZONS)} horizons x 2")
    say("  questions. Read the pattern, not one cell.")
    say("=" * 78)

    if args.out:
        p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {args.label} drift\n\n```\n" + "\n".join(log) + "\n```\n")
        print(f"\n  written -> {p}")


if __name__ == "__main__":
    main()
