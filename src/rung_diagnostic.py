"""
rung_diagnostic.py -- what is lambda actually DOING to analog selection?

REGISTERED IN docs/prereg_rung_diagnostic.md BEFORE THIS RAN.
    Threshold: median top-k overlap vs the no-decay control >= 0.90 at the
    primary rung (HL=4y) means lambda is TIE-BREAKING as the locked design
    claims. Below 0.90 means lambda is RESELECTING -- choosing which analogs
    enter the average, not merely how they are weighted -- and the engine is a
    recency filter with a regime gate, not a similarity-dominant analog engine.

WHY THIS EXISTS
    The ladder returned opposite verdicts on the same panel on the same day:
    Engine A POSITIVE (primary 0.3205 > control 0.2526), Engine B NULL (primary
    0.3200 < control 0.3800, and no-decay is its best rung). The engines differ
    only in feature basis, GMM refit policy, and decay default. A result that
    flips on those is basis-carried, not phenomenon-carried.

    Neither verdict is reportable as a finding about recency until we know
    whether lambda is reordering analogs or replacing them.

NO FORWARD RETURN ENTERS ANY QUANTITY HERE
    Weighted analog age, ESS and top-k overlap are properties of the weighting
    and selection alone. They cannot be tuned against an outcome, which is why
    they can settle a question the Sharpes cannot.

COST
    Regime labels and features do NOT depend on lambda, so the expensive part --
    Engine B's ~209 expanding-window GMM refits -- is computed ONCE and reused
    across all five rungs. After that each rung is arithmetic on cached
    distances and ages.

Run:
    python -m src.rung_diagnostic                 # both engines
    python -m src.rung_diagnostic --engine A      # analog_core only
    python -m src.rung_diagnostic --engine B      # analog_backtest only
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml

from src.analog_core import (DEFAULT, CLUSTERING_PCS, load_data, feature_matrix,
                             frozen_labels, _kw)
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
MODELS_YAML = REPO / "config" / "models.yaml"
OUT_MD = REPO / "docs" / "rung_diagnostic_results.md"
OUT_JSON = REPO / "processed" / "rung_diagnostic.json"

LADDER = [float("inf"), 16.0, 8.0, 4.0, 2.0]
PRIMARY_HL = 4.0
OVERLAP_THRESHOLD = 0.90          # registered
TOPK_DEFAULT = 100


def fmt_hl(hl):
    return "inf (no decay)" if np.isinf(hl) else f"{hl:g}y"


def baseline_spec():
    raw = yaml.safe_load(MODELS_YAML.read_text())["models"]
    s = dict(DEFAULT)
    s.update({k: v for k, v in raw["model_1_baseline"].items() if k != "note"})
    return s


# ---------------------------------------------------------------------------
# candidate structure -- computed ONCE per engine, reused across rungs
# ---------------------------------------------------------------------------

def structure_engine_a(spec, cfg):
    """analog_core: z-scored PCs, ONE GMM frozen on all history."""
    scores, rets = load_data()
    labels = frozen_labels(scores, spec, cfg)
    X = feature_matrix(scores, spec)
    H = spec["horizon"]
    dates = scores.index
    start_pos = int(dates.get_indexer([pd.to_datetime("2010-01-01")],
                                      method="bfill")[0])
    out = []
    for pos in range(start_pos, len(dates) - H, H):
        if np.isnan(X[pos]).any():
            continue
        idx = np.arange(pos)
        cand = idx[(labels[:pos] == labels[pos]) & (idx + H < pos)]
        cand = cand[~np.isnan(X[cand]).any(axis=1)]
        if len(cand) < spec["min_analogs"]:
            continue
        dist = np.linalg.norm(X[cand] - X[pos], axis=1)
        out.append((cand, dist, (pos - cand) / 252.0))
    return out


def structure_engine_b(cfg, refit_every=20, horizon=5, min_analogs=20,
                       start="2010-01-01"):
    """analog_backtest: RAW PCs, GMM refit expanding-window every 20 sessions.

    Replicates that script's candidate selection exactly -- raw Xc, no
    z-scoring, expanding refit -- but computes no returns. Labels do not depend
    on lambda, so this runs once.
    """
    from sklearn.mixture import GaussianMixture
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores.index = pd.to_datetime(scores.index); scores = scores.sort_index()
    Xc = scores[CLUSTERING_PCS].values          # RAW, deliberately not _z()
    dates = scores.index
    H = horizon
    start_pos = int(dates.get_indexer([pd.to_datetime(start)], method="bfill")[0])

    model, last_fit, out = None, -10 ** 9, []
    n_fits = 0
    for pos in range(start_pos, len(dates) - H, H):
        if pos - last_fit >= refit_every or model is None:
            model = GaussianMixture(n_components=int(cfg["regime"]["n_regimes"]),
                                    covariance_type=cfg["regime"]["covariance_type"],
                                    max_iter=cfg["regime"]["max_iter"],
                                    n_init=cfg["regime"]["n_init"],
                                    random_state=cfg["project"]["random_seed"])
            model.fit(Xc[: pos + 1]); last_fit = pos; n_fits += 1
            if n_fits % 25 == 0:
                print(f"      ... {n_fits} GMM refits")
        lab = model.predict(Xc[: pos + 1])
        cand = np.where((lab[:-1] == lab[-1]) & (np.arange(pos) + H < pos))[0]
        if len(cand) < min_analogs:
            continue
        dist = np.linalg.norm(Xc[cand] - Xc[pos], axis=1)
        out.append((cand, dist, (pos - cand) / 252.0))
    print(f"      {n_fits} GMM refits, {len(out)} usable rebalances")
    return out


# ---------------------------------------------------------------------------
# per-rung measurement
# ---------------------------------------------------------------------------

def measure(structure, spec, hl, topk, control_sets=None):
    """Weighted analog age, ESS, and top-k overlap vs the control, per rebalance."""
    s = dict(spec)
    s["half_life_years"] = None if np.isinf(hl) else float(hl)
    ages, esss, overlaps, sets = [], [], [], []
    for i, (cand, dist, age) in enumerate(structure):
        w = _kw(dist, s, age)
        if len(cand) > topk:
            keep = np.argsort(-w)[:topk]
            c, w = cand[keep], w[keep]
            a = age[keep]
        else:
            c, a = cand, age
        tot = w.sum()
        if not np.isfinite(tot) or tot <= 0:
            continue
        wn = w / tot
        ages.append(float(np.sum(wn * a)))
        esss.append(float(1.0 / np.sum(wn ** 2)))
        sets.append(set(c.tolist()))
        if control_sets is not None:
            ctrl = control_sets[i]
            overlaps.append(len(sets[-1] & ctrl) / max(1, len(ctrl)))
    q = lambda v: (float(np.median(v)), float(np.percentile(v, 10)),
                   float(np.percentile(v, 90))) if v else (np.nan,) * 3
    return dict(age=q(ages), ess=q(esss),
                overlap=q(overlaps) if overlaps else None), sets


def run_engine(name, structure, spec, topk):
    print(f"\n{'=' * 78}\nENGINE {name}\n{'=' * 78}")
    print(f"  {len(structure)} rebalances | topk={topk}")
    _, control_sets = measure(structure, spec, float("inf"), topk)
    res = {}
    print(f"\n  {'rung':16} {'wtd age (y)':>22} {'ESS':>20} {'overlap vs inf':>22}")
    for hl in LADDER:
        m, _ = measure(structure, spec, hl, topk, control_sets)
        res[hl] = m
        a, e, o = m["age"], m["ess"], m["overlap"]
        ostr = "1.000 (control)" if np.isinf(hl) else \
               (f"{o[0]:.3f} [{o[1]:.3f},{o[2]:.3f}]" if o else "-")
        star = "  <- PRIMARY" if hl == PRIMARY_HL else ""
        print(f"  {fmt_hl(hl):16} {a[0]:8.3f} [{a[1]:5.2f},{a[2]:5.2f}] "
              f"{e[0]:8.1f} [{e[1]:5.1f},{e[2]:5.1f}] {ostr:>22}{star}")
    return res


def verdict(res):
    o = res[PRIMARY_HL]["overlap"]
    if o is None:
        return "INCONCLUSIVE", "no overlap computed at the primary rung."
    med = o[0]
    if med >= OVERLAP_THRESHOLD:
        return "TIE-BREAKING", (
            f"median top-k overlap at HL={PRIMARY_HL:g}y is {med:.3f}, at or above "
            f"the registered {OVERLAP_THRESHOLD:.2f}. Lambda reorders analogs that "
            f"similarity already selected; the set is largely intact. The locked "
            f"design's description holds.")
    return "RESELECTION", (
        f"median top-k overlap at HL={PRIMARY_HL:g}y is {med:.3f}, BELOW the "
        f"registered {OVERLAP_THRESHOLD:.2f}. Lambda is choosing WHICH analogs "
        f"enter the average, not merely how they are weighted. The ladder does not "
        f"measure 'does gentle recency decay improve analog quality'; it measures "
        f"'does restricting to recent history improve returns'. The report must say "
        f"the latter.")


def write_report(all_res, topk):
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Rung-level selection diagnostic — results", "",
         f"*Run {ts}. Registered in `docs/prereg_rung_diagnostic.md`, written "
         f"before any quantity below was computed.*", "",
         f"Registered threshold: median top-k overlap vs the no-decay control "
         f"**≥ {OVERLAP_THRESHOLD:.2f}** at HL={PRIMARY_HL:g}y = tie-breaking; "
         f"below = reselection.", "",
         "**No forward return enters any quantity here.** These are properties of "
         "the weighting and selection alone.", ""]
    for name, res in all_res.items():
        L += [f"## Engine {name}", "",
              "| rung | wtd mean analog age (y) | median ESS (of "
              f"{topk}) | top-k overlap vs ∞ |", "|---|---|---|---|"]
        for hl in LADDER:
            m = res[hl]
            a, e, o = m["age"], m["ess"], m["overlap"]
            ostr = "1.000 (control)" if np.isinf(hl) else \
                   (f"{o[0]:.3f} [{o[1]:.3f}, {o[2]:.3f}]" if o else "—")
            tag = " **← PRIMARY**" if hl == PRIMARY_HL else ""
            L.append(f"| {fmt_hl(hl)}{tag} | {a[0]:.3f} [{a[1]:.2f}, {a[2]:.2f}] | "
                     f"{e[0]:.1f} [{e[1]:.1f}, {e[2]:.1f}] | {ostr} |")
        v, why = verdict(res)
        L += ["", f"**VERDICT: {v}**", "", why, "",
              "*Bracketed figures are the 10th and 90th percentiles across "
              "rebalances.*", ""]
    L += ["## Reading", "",
          "If overlap is low on both engines, the A/B Sharpe disagreement is not "
          "a disagreement about recency — both ladders are measuring a recency "
          "filter, and Engine A's POSITIVE verdict is a recency-filter result, "
          "not an analog result.", "",
          "If overlap changes sharply between HL=2y and HL=4y on Engine B, the "
          "incumbent's interior Sharpe dip (0.25 at HL 3.438y, below both "
          "neighbours at 0.30 and 0.32) is attributable to discrete top-k "
          "membership changes. If overlap is flat across that interval, the dip "
          "is unexplained and is reported as unexplained.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        {f"{n}|{k}": v for n, r in all_res.items() for k, v in r.items()},
        indent=2, default=str))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["A", "B", "both"], default="both")
    args = ap.parse_args()

    cfg = load_config()
    spec = baseline_spec()
    topk = int(spec.get("topk", TOPK_DEFAULT))

    print("=" * 78)
    print("RUNG-LEVEL SELECTION DIAGNOSTIC")
    print("=" * 78)
    print(f"  registered threshold: overlap >= {OVERLAP_THRESHOLD:.2f} at "
          f"HL={PRIMARY_HL:g}y = tie-breaking, below = reselection")
    print(f"  baseline: horizon {spec['horizon']}d | {spec['sim_mode']} | "
          f"sigma {spec['sigma']} | topk {topk}")

    all_res = {}
    if args.engine in ("A", "both"):
        print("\n  building Engine A candidate structure (frozen GMM) ...")
        all_res["A"] = run_engine("A", structure_engine_a(spec, cfg), spec, topk)
    if args.engine in ("B", "both"):
        print("\n  building Engine B candidate structure "
              "(expanding GMM refits -- this is the slow part) ...")
        all_res["B"] = run_engine("B", structure_engine_b(cfg), spec, topk)

    print("\n" + "=" * 78)
    for n, r in all_res.items():
        v, why = verdict(r)
        print(f"ENGINE {n}: {v}")
        print(f"  {why}")
    print("=" * 78)
    write_report(all_res, topk)


if __name__ == "__main__":
    main()
