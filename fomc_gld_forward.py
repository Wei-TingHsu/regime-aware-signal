"""
fomc_gld_forward.py -- FORWARD TEST of a hypothesis found by looking.

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE the 2026-09-17 FOMC decision.

WHAT IS BEING TESTED, AND WHY ONLY FORWARD
    On 2026-09-08 a descriptive breakdown of the retired FOMC->GLD cell showed
    gold's three-session return after an FOMC decision was negative in three of
    four monetary regimes and positive in the fourth:

        regime 0  steep curve, low rates              n=50   -0.37%
        regime 1  low long rates, low real rates       n=30   -0.51%
        regime 2  flat curve, strong dollar            n=30   +0.42%
        regime 3  rapid money growth, high policy rate n=21   -1.14%

    That pattern was found by cutting 131 events four ways and reading the
    result. Every one of the 131 was used. There is NO held-out data, so no
    statistic on those 131 can be evidence -- a four-way split of noise
    produces one quarter that flips sign. The only honest test is on FOMC
    meetings that have not yet happened.

    THE MODEL DOES NOT FORECAST THIS. The regime engine emits a label and the
    document reader emits a direction; neither says "gold falls in three
    sessions". This file registers a directional prediction that will be
    checked against reality, meeting by meeting, with no way to have peeked.

REGISTERED PREDICTION -- per regime, sign only
    regime 0, 1, 3:  GLD NEXT_3 < 0      (close(N+3)/close(N) - 1, N = decision day)
    regime 2:        GLD NEXT_3 > 0

    Regime is the expanding-window label on the decision day, read from the
    same pipeline the product uses. It is recorded WITH the prediction, before
    the outcome, so the regime assignment cannot be adjusted afterwards.

REGISTERED CRITERION -- fixed before the first observation
    After n >= 10 forward meetings (any regime):
      C1  sign hit-rate > 50% at one-sided binomial p < 0.05
      C2  mean signed return (sign of prediction x realised NEXT_3) > 0 at
          sign-flip permutation p < 0.05
    Both, or the hypothesis is not supported. At 8 meetings a year this is
    ~15 months to a verdict. An interim count is printed and is NOT a result.

WHAT IS NOT PERMITTED
    Changing the prediction for any regime after a miss. Adding a regime
    exclusion. Changing the horizon from 3. Trading on it before C1 and C2
    are met. Each of those converts a forward test into a fitted one.

FIRST OBSERVATION
    FOMC decision 2026-09-17. Regime on that day to be recorded by this script
    when run on or after 2026-09-22 (three sessions later).

Run after each FOMC decision has three completed sessions:
    python fomc_gld_forward.py
"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from src.analog_event import load_data, regime_labels_expanding
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
LEDGER = PROCESSED_DIR / "fomc_gld_forward_ledger.csv"
OUT_MD = REPO / "docs" / "fomc_gld_forward.md"
DATES = PROCESSED_DIR / "fomc_decisions.csv"
REGISTERED_ON = pd.Timestamp("2026-09-08")
H = 3
PRED = {0: -1, 1: -1, 2: +1, 3: -1}      # registered sign per regime
MIN_N = 10


def main():
    cfg = load_config()
    scores, rets = load_data()
    idx = pd.DatetimeIndex(scores.index)
    lab = pd.Series(regime_labels_expanding(scores, cfg), index=idx)
    close = (1 + rets["GLD"].fillna(0)).cumprod()

    dts = pd.read_csv(DATES)
    col = next(c for c in dts.columns if "date" in c.lower())
    ev = pd.DatetimeIndex(pd.to_datetime(dts[col])).sort_values()
    ev = ev[ev > REGISTERED_ON]                  # forward only

    led = pd.read_csv(LEDGER, parse_dates=["decision"]) if LEDGER.exists() \
        else pd.DataFrame(columns=["decision", "session", "regime",
                                   "predicted", "next_3", "hit", "recorded"])
    done = set(pd.to_datetime(led["decision"]).dt.date) if len(led) else set()

    new = []
    for d in ev:
        if d.date() in done:
            continue
        hit = idx[idx >= d]
        if not len(hit):
            continue
        i = idx.get_loc(hit[0])
        if i + H >= len(idx) or pd.isna(rets["GLD"].iloc[i + H]):
            continue                              # not matured yet
        r = int(lab.iloc[i])
        if r < 0:
            continue
        nxt = close.iloc[i + H] / close.iloc[i] - 1
        new.append(dict(decision=d.date(), session=hit[0].date(), regime=r,
                        predicted=PRED[r], next_3=float(nxt),
                        hit=int(np.sign(nxt) == PRED[r]),
                        recorded=datetime.now(timezone.utc).date()))
    if new:
        led = pd.concat([led, pd.DataFrame(new)], ignore_index=True)
        led.to_csv(LEDGER, index=False)

    print("=" * 70)
    print("FOMC -> GLD forward test.  Registered 2026-09-08.")
    print("=" * 70)
    print(f"  {len(new)} new observation(s) matured; ledger now {len(led)} rows")
    if len(led):
        for _, r in led.iterrows():
            print(f"    {r.decision}  regime {r.regime}  predicted "
                  f"{'fall' if r.predicted<0 else 'rise'}  realised "
                  f"{r.next_3*100:+.2f}%  {'HIT' if r.hit else 'miss'}")
    n = len(led)
    if n < MIN_N:
        print(f"\n  {n} of {MIN_N} required. INTERIM -- not a result.")
        verdict = "INTERIM"
    else:
        k = int(led.hit.sum())
        p_bin = binomtest(k, n, 0.5, alternative="greater").pvalue
        signed = (led.predicted * led.next_3).values
        rng = np.random.default_rng(42)
        fl = np.array([(signed * rng.choice([-1, 1], n)).mean() for _ in range(10000)])
        p_perm = (np.sum(fl >= signed.mean()) + 1) / 10001
        C1, C2 = p_bin < 0.05, (signed.mean() > 0 and p_perm < 0.05)
        print(f"\n  hits {k}/{n}  binomial p {p_bin:.4f}   C1 {C1}")
        print(f"  mean signed {signed.mean()*100:+.3f}%  perm p {p_perm:.4f}   C2 {C2}")
        verdict = "SUPPORTED" if C1 and C2 else "NOT SUPPORTED"
        print(f"  -> {verdict}")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %z")
    L = ["# FOMC → GLD forward test", "", f"*Registered 2026-09-08. Updated {ts}.*",
         "", "Prediction per regime, sign only: fall in regimes 0/1/3, rise in "
         "regime 2. Criterion: after ≥10 meetings, hit-rate p<0.05 AND mean "
         "signed return p<0.05. **The model does not forecast this**; it is a "
         "hypothesis found by looking, tested only forward.", "",
         f"**Status: {verdict}** ({n} of {MIN_N} observations)", ""]
    if len(led):
        L += ["| decision | regime | predicted | realised NEXT_3 | hit |",
              "|---|---|---|---|---|"]
        for _, r in led.iterrows():
            L.append(f"| {r.decision} | {r.regime} | "
                     f"{'fall' if r.predicted<0 else 'rise'} | "
                     f"{r.next_3*100:+.2f}% | {'✓' if r.hit else '✗'} |")
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\n  -> {OUT_MD}\n  -> {LEDGER}")


if __name__ == "__main__":
    main()
