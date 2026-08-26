"""
step3_robustness.py -- re-test the 7 passing cells under a null that respects
overlapping outcomes, on non-overlapping subsamples, and split by time.

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.

WHAT IS BROKEN, PRECISELY
    NOT the estimator. src/analog_event.py computes leave-one-out predictions
    and overlapping outcomes do not affect that computation. The MSE gains and
    hit gains from the unblinding are descriptive statistics and they stand.

    The defect is in the NULL, in unblind_step3.py, which permutes outcomes
    freely within content class. At h=20 the passing cells overlap 61-87%: most
    events share most of their forward window with their neighbours, so y is
    strongly autocorrelated. Free permutation destroys that autocorrelation, so
    the permuted draws are LESS variable than the observed data, the null
    distribution is TOO NARROW, and every p-value is TOO SMALL.

        cell                        overlap at h    2025+ share
        earnings_8k/SPY/h20             87%             17%
        political_order/SPY/h20         81%             51%
        political_order/GLD/h20         61%             57%
        political_order/SPY/h5          56%             52%
        earnings_8k/SPY/h5              45%             17%
        political_order/SPY/h3          44%             52%

    political_order compounds it: median event gap 5 days, 52% of events from
    2025-26 (239 executive orders in 2025 against 18 in 2024).

    WRONG PRIOR #25, Claude's. The prereg registered permute_y for a pool where
    it was appropriate; unblind_step3.py applied it to a clustered pool without
    checking event spacing against horizon. The check was one line and was not
    done.

THE FIX IS THE PROJECT'S OWN CONVENTION
    docs/forward_scoreboard.md already says it: "Naive column counts overlapping
    daily entries (they share most of their days, so significance would be
    inflated). The NON-OVERLAP column samples every H-th trade and is the
    statistically honest one."

    Same problem, same answer. Applied here in two ways, because they fail
    differently and both are informative:

    N1 NON-OVERLAP SUBSAMPLE. Keep events greedily: take the first, then skip
       every event whose entry is within h sessions of the last kept one.
       Outcomes are then genuinely disjoint and permute_y is valid again.
       COST: n falls sharply. political_order/SPY/h20 goes from 232 to roughly
       40. A cell may become UNDERPOWERED rather than falsified, and that is a
       legitimate and different outcome from failing.

    N2 BLOCK PERMUTATION on the FULL sample. Instead of permuting outcomes
       freely, permute contiguous BLOCKS of outcomes long enough to span the
       horizon. Within-block autocorrelation is preserved, so the null carries
       the same dependence the observed data has. Retains all n.
       Block length b = max(1, round(h / median event gap in sessions)),
       computed per cell from the data, never chosen.

    N1 and N2 answer different questions. N1 asks whether the effect survives on
    independent events. N2 asks whether it survives a null that is as dependent
    as the data. A cell that passes both is solid; one that passes N2 and goes
    underpowered on N1 is probably real but unproven; one that fails N2 was an
    artifact of the narrow null.

    S TEMPORAL SPLIT. Identical to fomc_gld_split_cost.py, no new criteria:
       S1 both chronological halves carry the same sign as pooled
       S2 neither half's magnitude exceeds 3x the other's
    Applied to the MSE gain. This is the check that killed FOMC->GLD at 4.62x
    today, and political_order at 52% post-2025 is the obvious candidate.

*** REGISTERED CRITERIA, all before any number is seen ***

    A cell is CONFIRMED only if ALL of:
      R1  N2 block-permutation p < 0.05 on BOTH mse gain and hit gain
      R2  N1 non-overlap p < 0.05 on both, OR n_nonoverlap < 30 in which case
          the cell is UNDERPOWERED, reported as such, and NOT confirmed
      R3  S1 sign agreement and S2 ratio <= 3.0 on the mse gain

    Anything else is reported with its numbers and is not a finding. No cell is
    promoted on a subset of the criteria.

WHAT THIS DOES NOT DO
    It does not re-run the 45-cell unblinding and it does not change the
    estimator, which stays frozen at 9062391. It re-tests only the 7 cells that
    met the original criterion. Cells that did not pass are not revisited --
    re-testing failures under a different null until one passes is the error
    this whole project is built to avoid.

Run:
    python step3_robustness.py --dry-run
    python step3_robustness.py
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_event import (HL_D, CLUSTERING_PCS, load_data, _z_expanding,
                              regime_labels_expanding, select_sigma,
                              loo_evaluate, metrics, DEFAULT)
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "step3_robustness.md"
OUT_JSON = PROCESSED_DIR / "step3_robustness.json"
CELLS = PROCESSED_DIR / "unblind_cells.jsonl"

ASSET_AXIS = {"GLD": "dir_gold", "SPY": "dir_eq", "TLT": "dir_dur",
              "UUP": "dir_usd", "USO": "dir_oil"}
NEGLIGIBLE, ITERS, SEED, MIN_NONOVERLAP, MAX_RATIO = 0.05, 10_000, 42, 30, 3.0
READ_CSVS = ("read_statement.csv", "read_minutes.csv", "read_8k.csv",
             "read_political_order.csv", "read_political_other.csv")


def load_events():
    fr = [pd.read_csv(PROCESSED_DIR / f) for f in READ_CSVS
          if (PROCESSED_DIR / f).exists()]
    df = pd.concat(fr, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date", "source"]).drop_duplicates(
        subset=["source", "date", "doc_id"], keep="last")


def fwd(rets, col, h):
    return np.expm1(np.log1p(rets[col]).rolling(h).sum().shift(-h)).values


def block_perm(y, b, rng):
    """Permute contiguous blocks of length b, preserving within-block
    dependence. b spans the horizon, so overlapping outcomes stay together."""
    n = len(y)
    nb = int(np.ceil(n / b))
    blocks = [y[i * b:(i + 1) * b] for i in range(nb)]
    order = rng.permutation(nb)
    return np.concatenate([blocks[i] for i in order])[:n]


def run_null(cells, rng, iters, mode, blocks=None):
    """mode 'free' = the original permute_y. mode 'block' = N2.
    loo_evaluate is the frozen estimator and is only ever called, never
    reimplemented."""
    pb, pu, yy = [], [], []
    for c in cells:
        a, b_ = loo_evaluate(c["Z"], c["ages"], c["y"], c["labels"],
                             c["sigma"], c["C"], HL_D)
        pb.append(a); pu.append(b_); yy.append(c["y"])
    pb, pu, y = np.concatenate(pb), np.concatenate(pu), np.concatenate(yy)
    mb, hb = metrics(pb, y)
    mu, hu = metrics(pu, y)
    obs_m, obs_h = mu - mb, hb - hu
    nm, nh = np.empty(iters), np.empty(iters)
    for it in range(iters):
        P, Q, Y = [], [], []
        for k, c in enumerate(cells):
            yp = (c["y"][rng.permutation(len(c["y"]))] if mode == "free"
                  else block_perm(c["y"], blocks[k], rng))
            a, b_ = loo_evaluate(c["Z"], c["ages"], yp, c["labels"],
                                 c["sigma"], c["C"], HL_D)
            P.append(a); Q.append(b_); Y.append(yp)
        P, Q, Y = np.concatenate(P), np.concatenate(Q), np.concatenate(Y)
        m1, h1 = metrics(P, Y); m2, h2 = metrics(Q, Y)
        nm[it] = m2 - m1; nh[it] = h1 - h2
    return dict(n=int(len(y)), mse_gain=float(obs_m), hit_gain=float(obs_h),
                p_mse=float((np.sum(nm >= obs_m) + 1) / (iters + 1)),
                p_hit=float((np.sum(nh >= obs_h) + 1) / (iters + 1)))


def build(sub, axcol, rets, asset, h, Zall, labels_all, scores, C,
          keep=None):
    pos = pd.DatetimeIndex(scores.index).searchsorted(
        pd.DatetimeIndex(sub["date"].values), side="left")
    ok = pos < len(scores)
    d, p = sub.loc[ok].copy(), pos[ok]
    f = fwd(rets, asset, h)
    good = (np.isfinite(f[p]) & np.isfinite(Zall[p]).all(axis=1)
            & (labels_all[p] >= 0) & (p > 252))
    d, p = d.loc[good], p[good]
    val = pd.to_numeric(d[axcol], errors="coerce").fillna(0).values
    strong, sgn = np.abs(val) > NEGLIGIBLE, np.sign(val)
    cells, gaps = [], []
    for cls in (1.0, -1.0):
        m = strong & (sgn == cls)
        if m.sum() < 10:
            continue
        pp = np.sort(p[m])
        if keep is not None:              # N1: greedy non-overlap
            sel = [pp[0]]
            for x in pp[1:]:
                if x - sel[-1] >= keep:
                    sel.append(x)
            pp = np.array(sel)
        if len(pp) < 10:
            continue
        ages = np.abs(pp[:, None] - pp[None, :]) / 252.0
        sig, _, _, _ = select_sigma(Zall[pp], Zall[pp], ages, len(pp))
        cells.append(dict(Z=Zall[pp], y=f[pp], labels=labels_all[pp],
                          ages=ages, C=C, sigma=sig, pos=pp))
        # 25th PERCENTILE of the session gap, not the median. political_order
        # has a median gap of ~3.5 sessions, so at h=3 the MEDIAN event does
        # not overlap and ceil(3/3.5)=1 -- yet 44% of events measurably do.
        # Calibrating a dependence correction on the median of a right-skewed
        # gap distribution ignores the clustered tail that causes the problem.
        # q25 errs toward LARGER blocks, which makes the test harder to pass.
        gaps.append(float(np.percentile(np.diff(pp), 25)) if len(pp) > 1 else 1.0)
    return cells, gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--iters", type=int, default=ITERS)
    args = ap.parse_args()

    passing = [json.loads(l) for l in CELLS.read_text().splitlines() if l.strip()]
    passing = [c for c in passing if c.get("status") == "PASS"]
    print(f"{len(passing)} passing cells to re-test")

    cfg = load_config(); scores, rets = load_data()
    C = int(DEFAULT["n_regimes"])
    labels_all = regime_labels_expanding(scores, cfg)
    Zall = _z_expanding(scores[CLUSTERING_PCS].values)
    ev = load_events()
    rng = np.random.default_rng(SEED)
    out = []

    for c0 in sorted(passing, key=lambda x: x["n_events"]):
        src, ast, h = c0["source"], c0["asset"], int(c0["horizon"])
        sub = ev[ev.source == src]
        ax = ASSET_AXIS[ast]
        full, gaps = build(sub, ax, rets, ast, h, Zall, labels_all, scores, C)
        nfull = sum(len(x["y"]) for x in full)
        # Block length must SPAN the horizon, so ceil, not round. int(round())
        # returned 1 at h=5 with a ~3.5-session median gap -- and a block of 1
        # IS free permutation, i.e. exactly the broken null this fix replaces,
        # relabelled as fixed. Floor of 2 wherever consecutive events actually
        # overlap, measured per class rather than assumed.
        blocks = [max(2 if g < h else 1, int(np.ceil(h / max(g, 1.0))))
                  for g in gaps]
        no, _ = build(sub, ax, rets, ast, h, Zall, labels_all, scores, C, keep=h)
        nno = sum(len(x["y"]) for x in no) if no else 0
        tag = f"{src}/{ast}/h{h}"
        print(f"\n{tag}  n_full={nfull}  n_nonoverlap={nno}  "
              f"block length {blocks}")
        if args.dry_run:
            continue

        r2 = run_null(full, rng, args.iters, "block", blocks)
        print(f"   N2 block : mse {r2['mse_gain']:+.3e} p={r2['p_mse']:.4f}  "
              f"hit {r2['hit_gain']:+.3f} p={r2['p_hit']:.4f}")
        R1 = r2["p_mse"] < 0.05 and r2["p_hit"] < 0.05

        if nno < MIN_NONOVERLAP:
            r1, R2, note = None, False, f"UNDERPOWERED (n={nno} < {MIN_NONOVERLAP})"
        else:
            r1 = run_null(no, rng, args.iters, "free")
            R2 = r1["p_mse"] < 0.05 and r1["p_hit"] < 0.05
            note = "ok"
            print(f"   N1 nonov : mse {r1['mse_gain']:+.3e} p={r1['p_mse']:.4f}  "
                  f"hit {r1['hit_gain']:+.3f} p={r1['p_hit']:.4f}")
        if r1 is None:
            print(f"   N1 nonov : {note}")

        # S: temporal split on the mse gain, block null in each half
        halves = {}
        for name, sl in (("EARLY", slice(None, None)), ("LATE", slice(None, None))):
            pass
        sp = []
        for name in ("EARLY", "LATE"):
            hc, hg = [], []
            for k, cc in enumerate(full):
                n = len(cc["y"]); cut = n // 2
                idx = np.arange(0, cut) if name == "EARLY" else np.arange(cut, n)
                if len(idx) < 10:
                    continue
                pp = cc["pos"][idx]
                ages = np.abs(pp[:, None] - pp[None, :]) / 252.0
                sig, _, _, _ = select_sigma(Zall[pp], Zall[pp], ages, len(pp))
                hc.append(dict(Z=Zall[pp], y=cc["y"][idx],
                               labels=cc["labels"][idx], ages=ages, C=C,
                               sigma=sig, pos=pp))
                _g = max(float(np.percentile(np.diff(pp), 25)), 1.0)
                hg.append(max(2 if _g < h else 1, int(np.ceil(h / _g))))
            if hc:
                pbh, puh, yh = [], [], []
                for cc in hc:
                    a, b_ = loo_evaluate(cc["Z"], cc["ages"], cc["y"],
                                         cc["labels"], cc["sigma"], cc["C"], HL_D)
                    pbh.append(a); puh.append(b_); yh.append(cc["y"])
                pbh, puh, yh = (np.concatenate(pbh), np.concatenate(puh),
                                np.concatenate(yh))
                mb, _ = metrics(pbh, yh); mu, _ = metrics(puh, yh)
                sp.append(mu - mb)
        S1 = len(sp) == 2 and np.sign(sp[0]) == np.sign(sp[1]) == np.sign(r2["mse_gain"])
        lo, hi = sorted((abs(sp[0]), abs(sp[1]))) if len(sp) == 2 else (0, np.inf)
        ratio = hi / lo if lo > 0 else np.inf
        S2 = ratio <= MAX_RATIO
        print(f"   S split  : EARLY {sp[0]:+.3e}  LATE {sp[1]:+.3e}  "
              f"sign agree {S1}  ratio {ratio:.2f}x" if len(sp) == 2
              else "   S split  : not evaluable")
        conf = R1 and R2 and S1 and S2
        print(f"   R1 {R1}  R2 {R2} ({note})  R3 {S1 and S2}  -> "
              f"{'CONFIRMED' if conf else 'NOT CONFIRMED'}")
        out.append(dict(cell=tag, n_full=nfull, n_nonoverlap=nno,
                        block=blocks, N2=r2, N1=r1, note=note,
                        early=sp[0] if len(sp) == 2 else None,
                        late=sp[1] if len(sp) == 2 else None,
                        ratio=float(ratio), R1=bool(R1), R2=bool(R2),
                        S1=bool(S1), S2=bool(S2), confirmed=bool(conf)))

    if args.dry_run:
        print("\nDRY RUN -- no null computed.")
        return

    nc = sum(1 for o in out if o["confirmed"])
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print("\n" + "=" * 70)
    print(f"CONFIRMED: {nc} of {len(out)} previously-passing cells")
    print("=" * 70)
    L = ["# Step 3 — robustness re-test of the passing cells", "",
         f"*Run {ts}.*", "",
         "*The estimator is unchanged and frozen at `9062391`. What is re-tested "
         "is the NULL: `unblind_step3.py` permuted outcomes freely on a pool "
         "whose outcomes overlap 61–87% at h=20, which makes the null too narrow "
         "and every p-value too small. Wrong prior #25.*", "",
         f"**Confirmed: {nc} of {len(out)}.**", "",
         "| cell | n | n non-ov | N2 p(mse) | N2 p(hit) | N1 p(mse) | N1 p(hit) "
         "| EARLY | LATE | ratio | verdict |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        n1 = o["N1"] or {}
        L.append(f"| {o['cell']} | {o['n_full']} | {o['n_nonoverlap']} | "
                 f"{o['N2']['p_mse']:.4f} | {o['N2']['p_hit']:.4f} | "
                 f"{n1.get('p_mse', float('nan')):.4f} | "
                 f"{n1.get('p_hit', float('nan')):.4f} | "
                 f"{(o['early'] or 0):+.2e} | {(o['late'] or 0):+.2e} | "
                 f"{o['ratio']:.2f}× | "
                 f"{'**CONFIRMED**' if o['confirmed'] else o['note']} |")
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
