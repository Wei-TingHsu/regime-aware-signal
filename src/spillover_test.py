"""
spillover_test.py -- does one firm's earnings news propagate to its ECONOMIC
LINKS, and is any of it capturable AFTER the open?

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.

THE TWO PROBLEMS WITH EVERY PRIOR EVENT TEST
  (1) They used MACRO-WIDE triggers. No entity-level event source existed, so
      "the event names the SET" was never actually tested. Earnings dates ARE
      an entity-level source: NVDA reports, and the set is NVDA's suppliers and
      sector. This is the conditional merge as originally specified.
  (2) They measured drift from t+2 on DAILY closes. If the market prices
      supply-chain news at the next OPEN, a t+2 entry measures leftovers. The
      design was blind to the moment that matters, so a null could not
      distinguish "no effect" from "we looked after it was over".

THE FIX -- INTRADAY RESOLUTION FROM DAILY OHLC
    The response decomposes into two pieces that answer different questions:

        GAP    = open(N) / close(N-1) - 1     priced BEFORE anyone can act
        INTRA  = close(N) / open(N)   - 1     available AFTER the open
        NEXT   = close(N+1) / close(N) - 1    next-session drift

    All three market-adjusted by SPY over the SAME window (SPY's own gap, SPY's
    own intraday), so a market-wide overnight move cannot masquerade as
    spillover.

    GAP significant, INTRA null  -> instant, efficient, UNCAPTURABLE.
    INTRA significant            -> residual under-reaction a trader entering
                                    at the opening bell could actually take.
    This is the distinction daily-close tests cannot make, and it is measured
    here rather than assumed in either direction.

TIMING, INFERRED FROM DATA (yfinance does not flag BMO/AMC)
    Announcement calendar date d -> t = first session >= d. The announcer
    itself reveals when the news landed: compare |gap| into t against |gap|
    into t+1. The larger one is the news session N. An announcement after the
    close of t shows up as a large gap into t+1; a before-open announcement
    shows up as a large gap into t. The split is reported.

REGISTERED PARAMETERS
    Announcer   --announcer (default NVDA)
    Peers       --peers, default TSM,ASML,MU,INTC,SOXX,SMH,XSD -- suppliers and
                sector proxies, chosen on economic-link grounds. The announcer
                is ALSO reported separately as a control: if the announcer's own
                INTRA is null while peers' is not, that is incoherent and the
                result should be distrusted.
    Surprise    sign of the announcer's market-adjusted close-to-close return
                over the news session N. Return-based proxy; analyst SUE is not
                used (patchy coverage, second specification).
    Estimand    mean( sign(announcer surprise) x peer X ) for X in
                {GAP, INTRA, NEXT}. Registered prediction: POSITIVE for GAP
                (news propagates); the OPEN question is INTRA.
    Nulls       sign-flip (primary) and sign-permutation (secondary, preserves
                the marginal sign distribution). Both verified calibrated in
                pead_test at 1 false positive in 60 replications.
    Success     p < 0.05 under BOTH nulls. Reported per component; GAP and
                INTRA are separate questions, not a ladder.

KNOWN LIMITATIONS, registered up front
    Adjusted OHLC from yfinance; splits/dividends handled by the vendor.
    Opening auctions can be volatile and a real trader would not fill exactly
    at the printed open. INTRA is therefore an UPPER BOUND on what is
    capturable. Transaction costs are not deducted; a positive INTRA needs the
    same cost test the rotation pairs received before it means anything.

Run:
    python -m src.spillover_test --announcer NVDA --out docs/spillover_nvda.md
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_io import load_config

DEF_PEERS = "TSM,ASML,MU,INTC,SOXX,SMH,XSD"


def fetch_ohlc(tickers, start="2000-01-01"):
    import yfinance as yf
    df = yf.download(tickers, start=start, auto_adjust=True, progress=False,
                     group_by="ticker", threads=True)
    out = {}
    for t in tickers:
        try:
            sub = df[t][["Open", "Close"]].dropna()
            if len(sub) > 100:
                out[t] = sub
        except Exception:
            pass
    return out


def earnings_dates(ticker):
    import yfinance as yf
    d = yf.Ticker(ticker).get_earnings_dates(limit=100)
    if d is None or len(d) == 0:
        return pd.DatetimeIndex([])
    idx = pd.DatetimeIndex(d.index).tz_localize(None).normalize()
    return pd.DatetimeIndex(sorted(set(idx)))


def components(ohlc, i):
    """(gap, intra, full) at session index i, from adjusted OHLC."""
    o = ohlc["Open"].to_numpy()
    c = ohlc["Close"].to_numpy()
    if i < 1 or i >= len(c):
        return np.nan, np.nan, np.nan
    return o[i] / c[i - 1] - 1, c[i] / o[i] - 1, c[i] / c[i - 1] - 1


def pvals(stat, vals, sgn, rng, B):
    n = len(vals)
    n1 = (rng.choice([-1.0, 1.0], size=(B, n)) * vals).mean(axis=1)
    p1 = (np.sum(np.abs(n1) >= abs(stat)) + 1) / (B + 1)
    n2 = np.array([(rng.permutation(sgn) * vals).mean() for _ in range(B)])
    p2 = (np.sum(np.abs(n2 - n2.mean()) >= abs(stat - n2.mean())) + 1) / (B + 1)
    return p1, p2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--announcer", default="NVDA")
    ap.add_argument("--peers", default=DEF_PEERS)
    ap.add_argument("--market", default="SPY")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    A = args.announcer.strip()
    peers = [p.strip() for p in args.peers.split(",") if p.strip()]
    log = []

    def say(s=""):
        print(s); log.append(s)

    say("=" * 78)
    say(f"EARNINGS SPILLOVER -- {A} announces; do its links move, and is any of")
    say("it capturable AFTER the open?")
    say("=" * 78)
    say(f"announcer: {A} | peers: {', '.join(peers)} | market: {args.market}")
    say(f"iters {args.iters} | seed {seed}")
    say("")
    say("GAP   = open(N)/close(N-1)-1   priced before anyone can act")
    say("INTRA = close(N)/open(N)-1     available AFTER the open  <-- the question")
    say("NEXT  = close(N+1)/close(N)-1  next-session drift")
    say("All market-adjusted by SPY over the SAME window.")

    tickers = sorted(set([A, args.market] + peers))
    say("\nfetching adjusted OHLC ...")
    ohlc = fetch_ohlc(tickers)
    missing = [t for t in tickers if t not in ohlc]
    if A not in ohlc or args.market not in ohlc:
        raise SystemExit(f"missing OHLC for announcer or market: {missing}")
    if missing:
        say(f"  no OHLC, dropped: {', '.join(missing)}")
        peers = [p for p in peers if p in ohlc]

    eds = earnings_dates(A)
    say(f"{A}: {len(eds)} earnings dates "
        f"{eds.min().date()} -> {eds.max().date()}" if len(eds) else "no dates")
    if len(eds) == 0:
        raise SystemExit("no earnings dates")

    sess = ohlc[A].index
    mkt = ohlc[args.market].reindex(sess).ffill()

    rows, bmo, amc = [], 0, 0
    for d in eds:
        later = sess[sess >= d]
        if len(later) < 3:
            continue
        t = sess.get_loc(later[0])
        if t + 2 >= len(sess):
            continue
        g_t, _, _ = components(ohlc[A], t)
        g_t1, _, _ = components(ohlc[A], t + 1)
        if np.isnan(g_t) or np.isnan(g_t1):
            continue
        N = t + 1 if abs(g_t1) > abs(g_t) else t
        bmo += (N == t); amc += (N == t + 1)

        _, _, a_full = components(ohlc[A], N)
        _, _, m_full = components(mkt, N)
        if np.isnan(a_full) or np.isnan(m_full):
            continue
        surprise = a_full - m_full
        if surprise == 0:
            continue

        rec = dict(date=sess[N], sign=np.sign(surprise), surprise=surprise)
        for p in peers + [A]:
            if p not in ohlc:
                continue
            pi = ohlc[p].reindex(sess).ffill()
            g, it, _ = components(pi, N)
            gN, itN, _ = components(pi, N + 1)
            mg, mi, _ = components(mkt, N)
            _, _, mn = components(mkt, N + 1)
            _, _, pn = components(pi, N + 1)
            rec[f"{p}_GAP"] = g - mg
            rec[f"{p}_INTRA"] = it - mi
            rec[f"{p}_NEXT"] = pn - mn
        rows.append(rec)

    df = pd.DataFrame(rows)
    say(f"\nusable events: {len(df)}   timing split: "
        f"{bmo} before-open, {amc} after-close")
    if len(df) < 20:
        say("FEWER THAN 20 EVENTS -- nothing below carries meaningful power.")
    say(f"mean |{A} surprise| = {df['surprise'].abs().mean()*100:.2f}%")
    sgn = df["sign"].to_numpy()

    say("\n  peer     component      n    stat      p(flip)  p(perm)")
    out = []
    for p in peers + [A]:
        for comp in ("GAP", "INTRA", "NEXT"):
            col = f"{p}_{comp}"
            if col not in df:
                continue
            v = df[col].to_numpy()
            ok = ~np.isnan(v)
            if ok.sum() < 15:
                continue
            stat = float((sgn[ok] * v[ok]).mean())
            p1, p2 = pvals(stat, v[ok], sgn[ok], rng, args.iters)
            star = " *" if p1 < 0.05 and p2 < 0.05 else ""
            tag = "(announcer)" if p == A else ""
            say(f"  {p:6} {comp:>7} {tag:>12}  {ok.sum():>3}  "
                f"{stat*100:+7.3f}%  {p1:.4f}   {p2:.4f}{star}")
            out.append(dict(peer=p, comp=comp, n=int(ok.sum()), stat=stat,
                            p1=p1, p2=p2, is_announcer=(p == A)))

    res = pd.DataFrame(out)
    say("\n" + "=" * 78)
    say("READING")
    pr = res[~res.is_announcer]
    sig = lambda c: pr[(pr.comp == c) & (pr.p1 < 0.05) & (pr.p2 < 0.05)]
    ng, ni, nn = len(sig("GAP")), len(sig("INTRA")), len(sig("NEXT"))
    npeer = pr.peer.nunique()
    say(f"  peers with significant GAP:   {ng}/{npeer}")
    say(f"  peers with significant INTRA: {ni}/{npeer}   <-- the capturable one")
    say(f"  peers with significant NEXT:  {nn}/{npeer}")
    say("")
    if ng and not ni:
        say("  PROPAGATION IS INSTANT. The links reprice in the overnight gap and")
        say("  nothing survives the open. This is efficient pricing MEASURED, not")
        say("  assumed -- and it explains why every t+2 test was null: by then it")
        say("  was already over. No tradeable spillover.")
    elif ni:
        say("  RESIDUAL AFTER THE OPEN. Some spillover is still available to a")
        say("  trader entering at the bell. Before this means anything: (a) it is")
        say("  an UPPER BOUND -- a real fill is not the printed open; (b) it needs")
        say("  the transaction-cost test the rotation pairs got; (c) it needs a")
        say("  temporal split, which is what killed SPY->GLD and SOXX->XAR.")
    else:
        say("  NO propagation detected in any component. Either the links are not")
        say("  economically real, or the effect is below what this sample can see.")
    say("")
    say(f"  Multiple testing: {len(pr)} peer-component cells, ~{0.05*len(pr):.1f}")
    say("  false positives expected at alpha=0.05. Read the pattern, not one cell.")
    say("  Announcer's own rows are the coherence check: if the announcer shows")
    say("  no GAP, the timing inference failed and nothing else is meaningful.")
    say("=" * 78)

    if args.out:
        pth = Path(args.out); pth.parent.mkdir(parents=True, exist_ok=True)
        pth.write_text(f"# Earnings spillover -- {A}\n\n```\n" + "\n".join(log)
                       + "\n```\n")
        res.to_csv(str(pth).replace(".md", "_cells.csv"), index=False)
        print(f"\n  written -> {pth}")


if __name__ == "__main__":
    main()
