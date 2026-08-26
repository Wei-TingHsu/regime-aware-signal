"""
unblind_step3.py -- THE UNBLINDING. prereg_analog_event.md sections 2-5.

WHAT THIS IS
    src/analog_event.py was built and accepted blind: build_blind() assembles
    real macro PCs, real expanding regimes, real return series with real
    volatility, fat tails, cross-asset correlation, missing values and NYSE
    holidays -- and then DESTROYS the event-date <-> return correspondence and
    plants a known effect on top.

    This script is that same pipeline with two changes and no others:

        1. event positions are the REAL document dates, not rng.choice(valid)
        2. y = fwd[pos]        -- the real alignment, not fwd[donor]
        3. no planted effect

    Everything else -- kernel_weights, select_sigma, estimate, loo_evaluate,
    metrics, permutation_null, regime_labels_expanding, _z_expanding -- is
    IMPORTED FROM src.analog_event AND NOT REDEFINED HERE. The estimator that
    passed six acceptance tests is the estimator that runs. If this file
    reimplemented any of it, the acceptance tests would no longer be evidence
    about the thing being run.

    This is a ONE-WAY DOOR. After it runs, the real correspondence has been
    seen and any subsequent change to the estimator is a change made with
    knowledge of the answer.

WHAT IS REGISTERED AND WHAT IS CHOSEN HERE
    Registered in prereg_analog_event.md, implemented not decided:
      - entry at the close of the document's PUBLIC date          (section 2)
      - content class = sign(direction[asset_class]) agrees, both non-zero,
        hard binary filter                                        (section 2.1)
      - all three PCs, no per-source axis selection               (section 2.2)
      - HL_d = 4 years, sigma_d by bisection on median ESS        (2.3, 4)
      - abstention at ESS < 8                                     (section 3.5)
      - the criterion: BOTH lower MSE AND higher hit-rate, p<0.05 (section 5.2)
      - permute_y primary, permute_Z retained, both reported      (section 5.3)
      - report regardless of outcome, every asset, every horizon  (section 5.4)
      - the transfer check at 0.90 top-k overlap                  (section 4.1)

    CHOSEN HERE, declared because the prereg left them open:
      - HORIZONS = (3, 5, 20) sessions. The blind harness used 3; section 5.1's
        power arithmetic is worked at 3. 5 and 20 are added because section 5.4
        requires "every horizon" and reporting one horizon would make the choice
        of that horizon invisible. ALL are reported. No horizon is designated
        primary after the fact -- 3 is primary, declared here, before the run.
      - ASSETS = the five schema axes' liquid proxies: GLD gold, SPY equity,
        TLT duration, UUP dollar, USO oil. One instrument per axis; no
        selection among candidates.
      - Content class is enforced by running the estimator SEPARATELY within
        each sign class and concatenating the leave-one-out predictions. The
        prereg makes the class a hard filter; this is the implementation of
        that, and it means a query is never predicted from an opposite-sign
        document.

WHAT THIS SCRIPT DOES NOT DO
    The Amendment 2 and Amendment 3 tests on the agreement flag are NOT run
    here. They need per-event predictions, which this writes out, and they are
    a separate registered step that runs AFTER this one. Mixing them into the
    unblinding would make the order of operations unauditable.

Run:
    python unblind_step3.py --dry-run     # assemble and report counts, no test
    python unblind_step3.py               # THE UNBLINDING
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# THE FROZEN ESTIMATOR. Imported, never redefined.
from src.analog_event import (HL_D, CLUSTERING_PCS, load_data, _z_expanding,
                              regime_labels_expanding, select_sigma,
                              loo_evaluate, metrics, ess_of, kernel_weights,
                              DEFAULT)
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "unblind_step3_results.md"
OUT_JSON = PROCESSED_DIR / "unblind_step3.json"
OUT_PRED = PROCESSED_DIR / "unblind_step3_predictions.csv"

HORIZONS = (3, 5, 20)              # declared above; 3 is primary
PRIMARY_H = 3
ASSET_AXIS = {"GLD": "dir_gold", "SPY": "dir_eq", "TLT": "dir_dur",
              "UUP": "dir_usd", "USO": "dir_oil"}
NEGLIGIBLE = 0.05                  # |direction| at or below this is "no sign"
ESS_FLOOR = 8                      # prereg 3.5
N_PERM = 10_000                    # prereg 5.3
SEED = 42
MIN_EVENTS = 30                    # below this a cell is reported, not tested

READ_CSVS = ("read_statement.csv", "read_minutes.csv", "read_8k.csv",
             "read_political_order.csv", "read_political_other.csv")


# ---------------------------------------------------------------------------
def load_events():
    """Every cached read, with its direction on each axis. Dates are PUBLIC
    dates -- prereg section 2, 'never event dates'."""
    frames = []
    for f in READ_CSVS:
        p = PROCESSED_DIR / f
        if p.exists():
            frames.append(pd.read_csv(p))
    if not frames:
        raise SystemExit("no read_*.csv in processed/. Run rebuild_csv.py --all")
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "source"])
    return df.drop_duplicates(subset=["source", "date", "doc_id"], keep="last")


def forward_return(rets, col, h):
    """h-session forward simple return, exactly as build_blind does at h=3."""
    return np.expm1(np.log1p(rets[col]).rolling(h).sum().shift(-h)).values


def map_to_positions(dates, index):
    """Document date -> panel position. Entry is the CLOSE of the public date,
    so a document published on a session maps to that session; one published on
    a non-session maps FORWARD to the next session (never backward, which would
    enter before the document existed)."""
    idx = pd.DatetimeIndex(index)
    pos = idx.searchsorted(pd.DatetimeIndex(dates), side="left")
    ok = pos < len(idx)
    return pos, ok


def pooled_perm_test(cells, rng, iters):
    """Pooled null, prereg 5.3, permute_y mode.

    Content class is a hard filter, so leave-one-out runs WITHIN each class.
    The null must respect that: outcomes are shuffled WITHIN class, which
    preserves every group size and every return path and destroys only the
    state<->outcome correspondence. Predictions are then concatenated across
    classes and the pooled statistic recomputed, exactly as observed.

    loo_evaluate is the frozen function; this loop only feeds it."""
    obs_pb, obs_pu, obs_y = [], [], []
    for c in cells:
        pb, pu = loo_evaluate(c["Z"], c["ages"], c["y"], c["labels"],
                              c["sigma"], c["C"], HL_D)
        obs_pb.append(pb); obs_pu.append(pu); obs_y.append(c["y"])
    pb, pu, y = (np.concatenate(obs_pb), np.concatenate(obs_pu),
                 np.concatenate(obs_y))
    mse_b, hit_b = metrics(pb, y)
    mse_u, hit_u = metrics(pu, y)
    obs_mse_gain, obs_hit_gain = mse_u - mse_b, hit_b - hit_u

    null_mse, null_hit = np.empty(iters), np.empty(iters)
    for it in range(iters):
        Pb, Pu, Y = [], [], []
        for c in cells:
            yp = c["y"][rng.permutation(len(c["y"]))]
            a, b = loo_evaluate(c["Z"], c["ages"], yp, c["labels"],
                                c["sigma"], c["C"], HL_D)
            Pb.append(a); Pu.append(b); Y.append(yp)
        Pb, Pu, Y = np.concatenate(Pb), np.concatenate(Pu), np.concatenate(Y)
        m_b, h_b = metrics(Pb, Y)
        m_u, h_u = metrics(Pu, Y)
        null_mse[it] = m_u - m_b
        null_hit[it] = h_b - h_u
    p_mse = (np.sum(null_mse >= obs_mse_gain) + 1) / (iters + 1)
    p_hit = (np.sum(null_hit >= obs_hit_gain) + 1) / (iters + 1)
    return dict(n=int(len(y)), mse_blend=float(mse_b), mse_uncond=float(mse_u),
                hit_blend=float(hit_b), hit_uncond=float(hit_u),
                obs_mse_gain=float(obs_mse_gain),
                obs_hit_gain=float(obs_hit_gain),
                p_mse=float(p_mse), p_hit=float(p_hit),
                pred_blend=pb, pred_uncond=pu, y=y)


def transfer_check(cells):
    """prereg 4.1 -- is the kernel selecting on macro similarity, or is lambda
    reselecting on recency here too? Median top-k overlap against a no-decay
    control. Below 0.90 the report must say step 3 conditions on RECENT
    same-class events, not on MACRO-SIMILAR ones."""
    ov = []
    for c in cells:
        Z, ages, sig = c["Z"], c["ages"], c["sigma"]
        n = len(Z)
        k = min(20, max(3, n // 5))
        for i in range(n):
            m = np.ones(n, bool); m[i] = False
            w_d = kernel_weights(Z[m], Z[i], ages[i][m], sig, HL_D)
            w_n = kernel_weights(Z[m], Z[i], ages[i][m], sig, 1e9)  # no decay
            if len(w_d) <= k:
                continue
            a = set(np.argsort(-w_d)[:k]); b = set(np.argsort(-w_n)[:k])
            ov.append(len(a & b) / k)
    return float(np.median(ov)) if ov else float("nan")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="assemble the cells and report counts. Computes NO "
                         "estimate against the real alignment.")
    ap.add_argument("--iters", type=int, default=N_PERM)
    args = ap.parse_args()

    cfg = load_config()
    scores, rets = load_data()
    C = int(DEFAULT["n_regimes"])
    labels_all = regime_labels_expanding(scores, cfg)
    Zall = _z_expanding(scores[CLUSTERING_PCS].values)
    ev = load_events()
    rng = np.random.default_rng(SEED)

    print("=" * 78)
    print("STEP 3 UNBLINDING -- real event/return correspondence")
    print("prereg_analog_event.md sections 2-5. Estimator frozen at 9062391.")
    print("=" * 78)
    print(f"  panel {len(scores)} sessions   documents {len(ev)}   "
          f"regimes C={C}")
    print(f"  horizons {HORIZONS} (primary {PRIMARY_H})   HL_d={HL_D}y   "
          f"ESS floor {ESS_FLOOR}")

    rows, results, preds = [], [], []
    for source in sorted(ev["source"].unique()):
        sub = ev[ev.source == source]
        for asset, axcol in ASSET_AXIS.items():
            if asset not in rets.columns or axcol not in sub.columns:
                continue
            for h in HORIZONS:
                fwd = forward_return(rets, asset, h)
                pos, ok = map_to_positions(sub["date"].values, scores.index)
                d = sub.loc[ok].copy()
                p = pos[ok]
                good = (np.isfinite(fwd[p]) & np.isfinite(Zall[p]).all(axis=1)
                        & (labels_all[p] >= 0) & (p > 252))
                d, p = d.loc[good], p[good]
                sgn = np.sign(pd.to_numeric(d[axcol], errors="coerce")
                              .fillna(0).values)
                strong = np.abs(pd.to_numeric(d[axcol], errors="coerce")
                                .fillna(0).values) > NEGLIGIBLE
                cells = []
                for cls in (1.0, -1.0):
                    m = strong & (sgn == cls)
                    if m.sum() < 10:
                        continue
                    pp = p[m]
                    order = np.argsort(pp)
                    pp = pp[order]
                    Zq = Zall[pp]
                    ages = np.abs(pp[:, None] - pp[None, :]) / 252.0
                    sigma, med_ess, tgt, okc = select_sigma(
                        Zq, Zq, ages, len(pp))
                    cells.append(dict(Z=Zq, y=fwd[pp], labels=labels_all[pp],
                                      ages=ages, C=C, sigma=sigma, cls=cls,
                                      med_ess=med_ess, target=tgt, conv=okc,
                                      pos=pp,
                                      dates=d.loc[m].iloc[order]["date"].values))
                n_ev = sum(len(c["y"]) for c in cells)
                row = dict(source=source, asset=asset, horizon=h,
                           n_events=int(n_ev), n_classes=len(cells),
                           median_ess=float(np.median([c["med_ess"]
                                                       for c in cells]))
                           if cells else float("nan"),
                           sigma=float(np.median([c["sigma"] for c in cells]))
                           if cells else float("nan"),
                           bisection_converged=all(c["conv"] for c in cells)
                           if cells else None)
                if not cells or n_ev < MIN_EVENTS:
                    row["status"] = f"too few events ({n_ev} < {MIN_EVENTS})"
                    rows.append(row); continue
                if row["median_ess"] < ESS_FLOOR:
                    row["status"] = (f"ABSTAIN -- median ESS "
                                     f"{row['median_ess']:.1f} < {ESS_FLOOR} "
                                     f"(prereg 3.5)")
                    rows.append(row); continue
                if args.dry_run:
                    row["status"] = "ready"
                    rows.append(row); continue

                r = pooled_perm_test(cells, rng, args.iters)
                r["overlap"] = transfer_check(cells)
                passed = (r["obs_mse_gain"] > 0 and r["obs_hit_gain"] > 0
                          and r["p_mse"] < 0.05 and r["p_hit"] < 0.05)
                row.update({k: v for k, v in r.items()
                            if k not in ("pred_blend", "pred_uncond", "y")})
                row["status"] = "PASS" if passed else "not met"
                rows.append(row); results.append(row)
                off = 0
                for c in cells:
                    k = len(c["y"])
                    for j in range(k):
                        preds.append(dict(source=source, asset=asset,
                                          horizon=h, cls=int(c["cls"]),
                                          date=str(pd.Timestamp(c["dates"][j]).date()),
                                          pred_blend=float(r["pred_blend"][off + j]),
                                          pred_uncond=float(r["pred_uncond"][off + j]),
                                          realised=float(r["y"][off + j])))
                    off += k
                print(f"  {source:18} {asset:4} h={h:<3} n={n_ev:5d} "
                      f"ESS {row['median_ess']:5.1f}  MSEgain "
                      f"{r['obs_mse_gain']:+.2e} p{r['p_mse']:.4f}  HITgain "
                      f"{r['obs_hit_gain']:+.3f} p{r['p_hit']:.4f}  "
                      f"-> {row['status']}")

    df = pd.DataFrame(rows)
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

    if args.dry_run:
        print("\n" + df.to_string(index=False))
        print("\n  DRY RUN -- no estimate computed against the real alignment.")
        print("  Re-run without --dry-run to unblind. This is a one-way door.")
        return

    if preds:
        pd.DataFrame(preds).to_csv(OUT_PRED, index=False)

    npass = sum(1 for r in results if r["status"] == "PASS")
    print("\n" + "=" * 78)
    print(f"REGISTERED CRITERION (prereg 5.2): BOTH lower MSE AND higher "
          f"hit-rate, p<0.05 on both.")
    print(f"  cells meeting it: {npass} of {len(results)} tested")
    print("  One of two is NOT a pass -- reported as inconclusive (prereg 5.2)")
    print("=" * 78)

    L = ["# Step 3 unblinding — result", "", f"*Run {ts}.*", "",
         "*The estimator was frozen at `9062391` and accepted blind under six "
         "tests (`prereg_analog_event.md` §9.2). This run supplies the real "
         "event-to-return correspondence and changes nothing else.*", "",
         f"**Registered criterion (§5.2):** the conditioned estimator must beat "
         f"the unconditional one on **both** lower MSE **and** higher sign "
         f"hit-rate, at p < 0.05 against the §5.3 null. One of two is not a "
         f"pass.", "",
         f"**Cells meeting the criterion: {npass} of {len(results)} tested.**",
         "", "Every asset, every horizon, reported regardless of outcome "
         "(§5.4).", "",
         df.to_markdown(index=False), "",
         "## Transfer check (§4.1)", "",
         "Median top-k overlap against a no-decay control, on the document "
         "pool. Below 0.90 the report must state that step 3 conditions on "
         "*recent same-class events* rather than on *macro-similar* ones — the "
         "same correction forced on step 1.", ""]
    if results:
        ovs = [r["overlap"] for r in results if np.isfinite(r.get("overlap", np.nan))]
        if ovs:
            m = float(np.median(ovs))
            L += [f"Median across tested cells: **{m:.3f}**.",
                  "", ("**RESELECTION.** λ is reselecting on the document pool "
                       "too. Step 3 conditions on recent same-class events, "
                       "not on macro-similar ones, and the report must say so."
                       if m < 0.90 else
                       "**Tie-breaking.** The kernel is selecting on macro "
                       "similarity, not merely on recency."), ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        dict(run=ts, horizons=list(HORIZONS), primary_horizon=PRIMARY_H,
             hl_d=HL_D, ess_floor=ESS_FLOOR, iters=args.iters, seed=SEED,
             n_pass=npass, n_tested=len(results),
             cells=df.to_dict("records")), indent=2, default=str))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}\n  -> {OUT_PRED}")


if __name__ == "__main__":
    main()
