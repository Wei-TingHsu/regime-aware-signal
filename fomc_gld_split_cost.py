"""
fomc_gld_split_cost.py -- the two checks that FOMC->GLD has never had.

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.
(Same convention as src/macro_event_test.py, which registered the original
result in its docstring at commit 8640d2d.)

WHAT IS BEING TESTED, AND WHY IT IS NOT YET A FINDING
    macro_event_test.py measured, on GLD, the Q2 sign-conditioned statistic
        stat_h = mean( sign(DAY_N) x NEXT_h )
    at -0.3% for h = 2, 3, 5, with p = 0.028 / 0.0096 / 0.0104.

    Negative means REVERSAL: the decision-day move partly unwinds. The implied
    position is -sign(DAY) taken at the CLOSE of the decision day and held h
    sessions. That is a real round trip and it must pay a real cost.

    CURRENT_STATE section 2.3 records the status verbatim: "FOMC->GLD IS NOT YET
    A FINDING. It meets its criterion but has not had the temporal split or the
    cost test -- the two checks that killed both rotation pairs."

    This file is those two checks. It does NOT re-register the original result:
    that stays at its own tier -- "registered in a script docstring committed
    before the run, 8640d2d" -- and this document must not be read as upgrading
    it. Two different evidential tiers on one cell, and the report says so.

THE MULTIPLICITY PROBLEM, STATED BEFORE THE SPLIT IS RUN
    macro_event_test.py tests 4 assets x 4 horizons x 2 questions = 32 cells.
    At alpha = 0.05 that is ~1.6 expected false positives. Exactly one cell
    survived. Its own docstring says "Read the pattern, not one cell."

    So the honest prior going in is that FOMC->GLD at 1-of-32 is INDISTINGUISHABLE
    FROM CHANCE on the original evidence alone. The three horizons are not three
    independent confirmations either: NEXT_2, NEXT_3 and NEXT_5 share sessions
    and are strongly correlated by construction.

    THE SPLIT IS THEREFORE NOT A BONUS CHECK. It is the test that decides
    whether this is real, and it is the reason the result was withheld.

POWER, COMPUTED BEFORE THE SPLIT -- and why the criterion is what it is
    GLD begins 2004, so roughly 170 usable FOMC events, ~85 per temporal half.
    GLD daily sigma ~1.0%, so the standard error on a half at h=3 is about
    1.0% x sqrt(3) / sqrt(85) = 0.19%, against an effect of 0.30%: t ~ 1.6.

    A REAL effect of this size would FAIL a "both halves significant" criterion
    more often than it passed. Requiring it would be a test rigged to fail.
    Requiring only one half would be a test rigged to pass -- and would accept
    exactly the pattern that killed PEAD, where the H=1 effect lived entirely in
    the hindsight-selected half (TSLA/NVDA/MSFT +0.454%, the four mature
    laggards flat at +0.041%).

    The criterion below is therefore about SIGN AGREEMENT and MAGNITUDE
    STABILITY, not per-half significance. This is registered here, with the
    arithmetic, before any split number is seen.

*** REGISTERED CRITERIA ***

SPLIT (S). The event list is cut at its chronological median into EARLY and
LATE. Registered pass requires ALL of:
    S1  both halves carry the SAME SIGN as the pooled estimate, at BOTH h=2
        and h=3 (the adjacent pair that carried the original result)
    S2  neither half's magnitude is more than 3x the other's, at both h=2 and
        h=3 -- an effect concentrated 4:1 or worse in one half is a subsample
        result, whatever its sign
    S3  the pooled estimate remains p < 0.05 under both registered nulls at
        both h=2 and h=3, recomputed here rather than quoted

    Per-half p-values ARE reported but are NOT part of the criterion, for the
    power reason above. A half that reaches p < 0.05 is noted, not required.

COST (C). The position is -sign(DAY) at close(N), exited at close(N+h): one
round trip per event, two crossings.
    Net_h(c) = |stat_h| - c, where c is the round-trip cost in the same units.
    Reported at c = 2, 5, 10, 20 bps. Registered pass requires:
    C1  Net > 0 at c = 10 bps at BOTH h=2 and h=3
    C2  the break-even cost is reported as a number regardless of outcome

    10 bps is the registered hurdle. GLD's quoted spread is ~1 bp and it is one
    of the most liquid ETFs listed, so 10 bps is roughly 5-10x a realistic
    institutional round trip. It is set deliberately high because the purpose is
    to find out whether the effect is robust to costs, not to pass.

WHAT FAILURE MEANS, STATED IN ADVANCE
    Fail S -> FOMC->GLD is reported as a subsample artifact and does NOT become
              the Tier-1 demo exemplar. The demo ships with an abstention or a
              Tier-3 cell instead. This is the same outcome that SPY->GLD and
              SOXX->XAR received, and it is reported the same way.
    Fail C -> the effect is real but not tradeable at the registered hurdle.
              Reported as such; it may still be shown as INFORMATION (a regime
              statement) but never as an implied position.
    Pass both -> FOMC->GLD becomes a finding, at the evidential tier of its
              original registration (docstring, 8640d2d) plus this document.

    None of these stops the product shipping.

NO API CALLS. Reuses fetch_ohlc and windows from src.macro_event_test rather
than reimplementing the entry convention -- a reimplementation would silently
change what is being compared.

Run:
    python fomc_gld_split_cost.py --dry-run    # counts and split boundary only
    python fomc_gld_split_cost.py
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.macro_event_test import fetch_ohlc, windows, HORIZONS
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "fomc_gld_split_cost.md"
OUT_JSON = PROCESSED_DIR / "fomc_gld_split_cost.json"
DATES = PROCESSED_DIR / "fomc_decisions.csv"

ASSET = "GLD"
ADJACENT = (2, 3)          # the pair that carried the original result
COSTS_BPS = (2, 5, 10, 20)
HURDLE_BPS = 10            # registered
MAX_RATIO = 3.0            # registered, S2
ITERS = 10_000


def signed_stat(day, nxt):
    s = np.sign(day); s[s == 0] = 1
    return float((s * nxt).mean())


def nulls(day, nxt, rng, iters):
    """The two registered nulls from macro_event_test.py, unchanged:
    sign-flip and sign-permutation."""
    s = np.sign(day); s[s == 0] = 1
    obs = float((s * nxt).mean())
    n = len(nxt)
    n1 = (rng.choice([-1.0, 1.0], size=(iters, n)) * nxt).mean(axis=1)
    p1 = (np.sum(np.abs(n1) >= abs(obs)) + 1) / (iters + 1)
    n2 = np.array([(rng.permutation(s) * nxt).mean() for _ in range(iters)])
    p2 = (np.sum(np.abs(n2 - n2.mean()) >= abs(obs - n2.mean())) + 1) / (iters + 1)
    return obs, float(p1), float(p2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--iters", type=int, default=ITERS)
    args = ap.parse_args()

    cfg = load_config()
    rng = np.random.default_rng(int(cfg["project"]["random_seed"]))

    dts = pd.read_csv(DATES)
    col = next(c for c in dts.columns if "date" in c.lower())
    ev = pd.DatetimeIndex(pd.to_datetime(dts[col])).sort_values()

    ohlc = fetch_ohlc([ASSET])
    if ASSET not in ohlc:
        raise SystemExit(f"no data for {ASSET}")
    px = ohlc[ASSET]
    sess = px.index

    # identical event->session mapping to macro_event_test.py
    idx = [sess.get_loc(sess[sess >= d][0]) for d in ev
           if len(sess[sess >= d]) and sess[sess >= d][0] - d <= pd.Timedelta("5D")]
    idx = sorted(set(i for i in idx if 250 < i < len(sess) - 6))
    rows = [windows(px, i, HORIZONS) for i in idx]
    df = pd.DataFrame([r for r in rows if r])
    df["session"] = [sess[i] for i in idx][:len(df)]

    cut = len(df) // 2
    boundary = df["session"].iloc[cut]

    print("=" * 78)
    print("FOMC -> GLD : TEMPORAL SPLIT AND COST TEST")
    print("prereg = this file's docstring. Original result: docstring 8640d2d.")
    print("=" * 78)
    print(f"  {len(df)} events  {df['session'].iloc[0].date()} -> "
          f"{df['session'].iloc[-1].date()}")
    print(f"  split at the chronological median: EARLY n={cut} "
          f"(< {boundary.date()}), LATE n={len(df)-cut}")
    print(f"  registered: S1 sign agreement, S2 ratio <= {MAX_RATIO}x, "
          f"S3 pooled p<0.05 both nulls, at h={ADJACENT[0]} and {ADJACENT[1]}")
    print(f"  registered: C1 net > 0 at {HURDLE_BPS} bps round trip")

    if args.dry_run:
        print("\n  DRY RUN -- no statistic computed.")
        return

    res, L = {}, []
    print(f"\n  {'h':>2} {'arm':>6} {'n':>5} {'stat':>9} {'p_flip':>8} "
          f"{'p_perm':>8}")
    for h in HORIZONS:
        v = df[f"NEXT_{h}"].to_numpy()
        d = df["DAY"].to_numpy()
        ok = ~np.isnan(v)
        arms = {"pooled": ok,
                "EARLY": ok & (np.arange(len(df)) < cut),
                "LATE": ok & (np.arange(len(df)) >= cut)}
        r = {}
        for name, m in arms.items():
            if m.sum() < 20:
                continue
            stat, p1, p2 = nulls(d[m], v[m], rng, args.iters)
            r[name] = dict(n=int(m.sum()), stat=stat, p_flip=p1, p_perm=p2)
            print(f"  {h:>2} {name:>6} {int(m.sum()):5d} {stat*100:+8.3f}% "
                  f"{p1:8.4f} {p2:8.4f}")
        res[h] = r

    # ---- registered criteria -------------------------------------------
    print("\n" + "=" * 78)
    print("REGISTERED CRITERIA")
    print("=" * 78)
    s1 = s2 = s3 = True
    for h in ADJACENT:
        r = res.get(h, {})
        if not all(k in r for k in ("pooled", "EARLY", "LATE")):
            s1 = s2 = s3 = False; continue
        sp, se, sl = r["pooled"]["stat"], r["EARLY"]["stat"], r["LATE"]["stat"]
        agree = np.sign(se) == np.sign(sp) and np.sign(sl) == np.sign(sp)
        lo, hi = sorted((abs(se), abs(sl)))
        ratio = hi / lo if lo > 0 else np.inf
        sig = r["pooled"]["p_flip"] < 0.05 and r["pooled"]["p_perm"] < 0.05
        s1 &= bool(agree); s2 &= bool(ratio <= MAX_RATIO); s3 &= bool(sig)
        print(f"  h={h}: pooled {sp*100:+.3f}%  EARLY {se*100:+.3f}%  "
              f"LATE {sl*100:+.3f}%   sign agree {agree}   "
              f"ratio {ratio:.2f}x   pooled sig {sig}")
    split_pass = s1 and s2 and s3
    print(f"\n  S1 sign agreement at h={ADJACENT}: {'PASS' if s1 else 'FAIL'}")
    print(f"  S2 magnitude ratio <= {MAX_RATIO}x:  {'PASS' if s2 else 'FAIL'}")
    print(f"  S3 pooled p<0.05 both nulls:  {'PASS' if s3 else 'FAIL'}")
    print(f"  SPLIT: {'PASS' if split_pass else 'FAIL'}")

    print("\n  cost, round trip, on |stat|:")
    cost_rows, cost_pass = [], True
    for h in ADJACENT:
        g = abs(res[h]["pooled"]["stat"]) * 1e4     # bps
        be = g
        line = {f"net_{c}bps": g - c for c in COSTS_BPS}
        line.update(h=h, gross_bps=g, breakeven_bps=be)
        cost_rows.append(line)
        cost_pass &= bool(g - HURDLE_BPS > 0)
        print(f"   h={h}  gross {g:6.1f} bps  " +
              "  ".join(f"@{c}bp {g-c:+6.1f}" for c in COSTS_BPS) +
              f"   break-even {be:.1f} bps")
    print(f"\n  C1 net > 0 at {HURDLE_BPS} bps at h={ADJACENT}: "
          f"{'PASS' if cost_pass else 'FAIL'}")

    verdict = ("FINDING -- split and cost both pass. FOMC->GLD becomes the "
               "Tier-1 demo exemplar, at the evidential tier of its original "
               "docstring registration (8640d2d) plus this document."
               if split_pass and cost_pass else
               "NOT A FINDING. " + ("Split failed: reported as a subsample "
               "artifact, same treatment as SPY->GLD and SOXX->XAR. "
               if not split_pass else "") + ("Cost failed: real but not "
               "tradeable at the registered 10 bps hurdle; may be shown as "
               "information, never as an implied position. "
               if not cost_pass else "") +
               "It does not become the Tier-1 exemplar and the demo abstains.")
    print("\n" + "=" * 78)
    print(verdict)
    print("=" * 78)
    print("\n  Reminder recorded before the run: macro_event_test.py tests 32")
    print("  cells and ~1.6 false positives are expected at alpha=0.05. On the")
    print("  original evidence alone this cell is indistinguishable from")
    print("  chance. That is what this split was for.")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = [f"# FOMC → GLD — temporal split and cost test", "", f"*Run {ts}.*", "",
         "*Pre-registered in this script's docstring, committed before the run. "
         "The original result stays at its own tier — docstring `8640d2d` — and "
         "this document does not upgrade it.*", "",
         f"{len(df)} events, {df['session'].iloc[0].date()} → "
         f"{df['session'].iloc[-1].date()}. Split at the chronological median, "
         f"{boundary.date()}.", "",
         "| h | arm | n | stat | p(flip) | p(perm) |", "|---|---|---|---|---|---|"]
    for h in HORIZONS:
        for name, d_ in res.get(h, {}).items():
            L.append(f"| {h} | {name} | {d_['n']} | {d_['stat']*100:+.3f}% | "
                     f"{d_['p_flip']:.4f} | {d_['p_perm']:.4f} |")
    L += ["", f"- **S1** sign agreement: **{'PASS' if s1 else 'FAIL'}**",
          f"- **S2** magnitude ratio ≤ {MAX_RATIO}×: **{'PASS' if s2 else 'FAIL'}**",
          f"- **S3** pooled p < 0.05 under both nulls: "
          f"**{'PASS' if s3 else 'FAIL'}**",
          f"- **C1** net > 0 at {HURDLE_BPS} bps: "
          f"**{'PASS' if cost_pass else 'FAIL'}**", "",
          "| h | gross (bps) | " +
          " | ".join(f"net @{c}bp" for c in COSTS_BPS) + " | break-even |",
          "|---|---|" + "---|" * (len(COSTS_BPS) + 1)]
    for r_ in cost_rows:
        L.append(f"| {r_['h']} | {r_['gross_bps']:.1f} | " +
                 " | ".join(f"{r_[f'net_{c}bps']:+.1f}" for c in COSTS_BPS) +
                 f" | {r_['breakeven_bps']:.1f} |")
    L += ["", f"## Verdict", "", verdict, "",
          "**Multiplicity, recorded before this run.** `macro_event_test.py` "
          "evaluates 4 assets × 4 horizons × 2 questions = 32 cells; ~1.6 false "
          "positives are expected at α = 0.05 and exactly one cell survived. "
          "NEXT_2, NEXT_3 and NEXT_5 overlap by construction and are not three "
          "independent confirmations. On the original evidence alone this cell "
          "is indistinguishable from chance — which is why the result was "
          "withheld pending this split.", "",
          "**Power, computed before this run.** ~85 events per half; GLD daily "
          "σ ≈ 1.0% gives se ≈ 0.19% at h=3 against a 0.30% effect, t ≈ 1.6. A "
          "real effect of this size would fail a both-halves-significant "
          "criterion more often than it passed, so the registered criterion is "
          "sign agreement and magnitude stability. Per-half p-values are "
          "reported and are not part of the criterion.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        dict(run=ts, n_events=len(df), boundary=str(boundary.date()),
             results={str(k): v for k, v in res.items()}, cost=cost_rows,
             S1=bool(s1), S2=bool(s2), S3=bool(s3), split_pass=bool(split_pass),
             cost_pass=bool(cost_pass), hurdle_bps=HURDLE_BPS), indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
