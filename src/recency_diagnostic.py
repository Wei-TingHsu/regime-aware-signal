"""
recency_diagnostic.py -- what does each half-life COST, measured on the real panel?

THE QUESTION THIS ANSWERS
    Choosing a recency half-life by whichever Sharpe comes out highest is how
    backtests get flattered, and this project already has 0.25-0.51 on the table.
    So decide on structure FIRST, using a quantity that has nothing to do with
    returns:

        ESS = (sum w)^2 / sum(w^2)      effective number of analogs

    A basket nominally built from 100 analogs but with ESS 8 is really built
    from 8. Every test in this project has hit a power wall; a decay that
    quietly reduces the analog set to single digits will hit it again, and the
    Sharpe it produces will be noise whichever direction it points.

    NOTHING HERE LOOKS AT RETURNS. Run this, choose the half-life on the
    evidence below plus your economic reasoning, write it down, and only then
    run the sweep.

FUNCTIONAL FORMS COMPARED
    exponential   exp(-ln2 * age / HL)         memoryless; the locked design
    power law     (1 + age)^(-alpha)           heavy-tailed; old analogs retain
                                               more weight. alpha calibrated so
                                               weight at HL equals 0.5, making
                                               the two directly comparable.
    half-gaussian exp(-ln2 * (age/HL)^2)       flat near 0, then falls fast
    none          1.0                          the control

    All three decay forms are pinned to the SAME half-life, so the comparison
    isolates the SHAPE rather than confounding it with the timescale.

WHAT TO LOOK FOR
    * ESS: how many analogs you are really averaging over.
    * median age of the weighted analog set: what "recent" ends up meaning.
    * overlap vs no-decay: what fraction of the top-k set actually changes. If
      overlap stays above ~0.9, the recency term is only breaking ties, which
      is what the 2026-08-18 design intended. If it drops below ~0.5, recency
      is DRIVING selection, not adjusting it -- a different model from the one
      that was locked.

Run:
    python -m src.recency_diagnostic
    python -m src.recency_diagnostic --half-lives 2,4,6,8,16
"""
import argparse

import numpy as np
import pandas as pd

from src.data_io import load_config
from src.analog_core import DEFAULT, load_data, frozen_labels, feature_matrix


def sim_kernel(dist, spec):
    if spec["kernel"] == "exp":
        return np.exp(-dist / spec["sigma"])
    return np.exp(-(dist ** 2) / (2 * spec["sigma"] ** 2))


def recency(age, hl, form):
    if hl is None or form == "none":
        return np.ones_like(age)
    if form == "exponential":
        return np.exp(-np.log(2.0) * age / hl)
    if form == "power":
        alpha = np.log(2.0) / np.log(1.0 + hl)      # weight at age=HL is 0.5
        return (1.0 + age) ** (-alpha)
    if form == "halfgauss":
        return np.exp(-np.log(2.0) * (age / hl) ** 2)
    raise ValueError(form)


def ess(w):
    w = np.asarray(w, float)
    s = w.sum()
    return float(s * s / np.sum(w * w)) if s > 0 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--half-lives", default="2,4,6,8,16")
    ap.add_argument("--n-dates", type=int, default=120)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    HLS = [float(x) for x in args.half_lives.split(",")]

    scores, rets = load_data()
    spec = dict(DEFAULT)
    labels = frozen_labels(scores, spec, cfg)
    X = feature_matrix(scores, spec)
    H, K = spec["horizon"], spec["topk"]
    dates = scores.index

    lo = int(dates.get_indexer([pd.Timestamp("2012-01-01")], method="bfill")[0])
    pool = [p for p in range(lo, len(dates) - H)
            if not np.isnan(X[p]).any()]
    sample = sorted(rng.choice(pool, size=min(args.n_dates, len(pool)),
                               replace=False))

    print("=" * 78)
    print("RECENCY DIAGNOSTIC -- structural cost of each half-life")
    print("=" * 78)
    print(f"panel {dates[0].date()} -> {dates[-1].date()} | "
          f"{len(sample)} sampled rebalance dates from 2012 on")
    print(f"spec: sigma {spec['sigma']}, top-k {K}, kernel {spec['kernel']}")
    print("\nNo returns are computed anywhere in this script.\n")

    base_sets = {}
    rows = []
    for form in ("none", "exponential", "power", "halfgauss"):
        for hl in ([None] if form == "none" else HLS):
            E, AGE, OVR = [], [], []
            for pos in sample:
                r_now = labels[pos]
                idx = np.arange(pos)
                cand = idx[(labels[:pos] == r_now) & (idx + H < pos)]
                cand = cand[~np.isnan(X[cand]).any(axis=1)]
                if len(cand) < spec["min_analogs"]:
                    continue
                d = np.linalg.norm(X[cand] - X[pos], axis=1)
                age = (pos - cand) / 252.0
                w = sim_kernel(d, spec) * recency(age, hl, form)
                if len(cand) > K:
                    keep = np.argsort(-w)[:K]
                    c_sel, w_sel, a_sel = cand[keep], w[keep], age[keep]
                else:
                    c_sel, w_sel, a_sel = cand, w, age
                w_sel = w_sel / w_sel.sum()
                E.append(ess(w_sel))
                AGE.append(float(np.sum(w_sel * a_sel)))
                if form == "none":
                    base_sets[pos] = set(c_sel.tolist())
                elif pos in base_sets:
                    b = base_sets[pos]
                    OVR.append(len(b & set(c_sel.tolist())) / max(1, len(b)))
            rows.append(dict(form=form, hl=hl, n=len(E),
                             ess=np.median(E), age=np.median(AGE),
                             overlap=(np.median(OVR) if OVR else 1.0)))

    df = pd.DataFrame(rows)
    print("  form          half-life   median ESS   wtd mean age   top-k overlap")
    print("                                          (years)       vs no-decay")
    for r in df.itertuples():
        hl = "  -  " if r.hl is None else f"{r.hl:5.1f}"
        flag = ""
        if r.form != "none":
            if r.overlap < 0.5:
                flag = "  <- recency DRIVES selection, not a tie-break"
            elif r.ess < 15:
                flag = "  <- ESS below 15: thin"
        print(f"  {r.form:12}  {hl}      {r.ess:8.1f}      {r.age:7.2f}"
              f"        {r.overlap:.2f}{flag}")

    base = df[df.form == "none"].iloc[0]
    print(f"\nNo-decay baseline: ESS {base.ess:.1f}, weighted mean analog age "
          f"{base.age:.2f}y.")
    print("\nHOW TO READ THIS")
    print("  overlap >= 0.90  recency only re-ranks within essentially the same")
    print("                   analog set -- the tie-break the 2026-08-18 design")
    print("                   specified.")
    print("  overlap <= 0.50  recency is choosing WHICH analogs are used. That is")
    print("                   a materially different model from the locked one and")
    print("                   should be registered as such, not slipped in.")
    print("  ESS              the honest count of analogs behind each basket.")
    print("                   Every null in this project came from thin samples;")
    print("                   do not create another one to chase a Sharpe.")
    print("\nDecide the half-life and form from THIS table plus your economic")
    print("argument, write both down, commit, and only then run the sweep.")


if __name__ == "__main__":
    main()
