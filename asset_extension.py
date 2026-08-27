"""
asset_extension.py -- any asset the user names, through the five-axis route.

THIS FILE IS THE PRE-REGISTRATION. Commit it BEFORE running it.

THE ROUTE, PLAINLY
    The reader emits direction on five AXES -- equity, duration, gold, dollar,
    oil -- not five assets. estimate() does not care which asset it scores:
    its pool is document events and its outcome y is the forward return of
    whatever asset is named. So any asset can be run through the pipeline by
    ONE decision: which axis conditions it.

        1. user names an asset      -> SMH
        2. asset maps to an axis    -> dir_eq      (from config role, or user-set)
        3. today's net view on that axis, from step 5, gives the CONTENT CLASS
        4. pool = historical events with the same sign on that axis
        5. y  = SMH's own forward returns over those events
        6. estimate() -> ESS, w, tau2, tier, abstain      (frozen, imported)
        7. report: the axis used, the net view, and the estimate or abstention

    Nothing in the estimator changes. Nothing in the reader changes. The only
    new object is the mapping in step 2, and it is printed in every output so
    a user always sees WHICH AXIS spoke for their asset.

THE MAPPING, from config.yaml roles
    Roles are grouped by the axis they load on most. This is a judgement and it
    is exposed: --axis overrides it for any ticker. A user who thinks XLE is
    an oil asset rather than an equity asset can say so and see both.

*** REGISTERED PREDICTION, written before any asset beyond the five is run ***
    Assets further from their axis proxy will show LOWER precedent strength w
    than the proxy itself, because "the document reads equity up" is weaker
    conditioning for SMH than for SPY -- it says nothing semiconductor-specific.

    Testable statement: across the equity-axis assets, median w for sector and
    thematic ETFs is below median w for SPY, on the same set of sessions.
    If it is NOT -- if SMH conditions as well as SPY on a macro-equity read --
    then sector specificity in the document does not matter and schema v2's
    sector axes are less valuable than assumed. Either answer is reported.

WHAT THE USER FINALLY SEES, per asset
    - the axis that conditioned it, and whether it was auto-mapped or user-set
    - today's net view on that axis and its dominant source
    - matched precedents, realised ESS, precedent strength w, tau2, tier
    - the blended estimate at the primary horizon, OR the abstention reason
    - the agreement label, display-only, with the failed-test note
    - a one-line caveat when the asset is not the axis proxy: the conditioning
      is macro-level and carries no sector content

No API calls. Reuses step6_report.build_report() machinery via a shared
helper; the estimator is imported from src.analog_event and never redefined.

Run:
    python asset_extension.py --date 20250407 --assets SMH,XLE,IAU
    python asset_extension.py --date 20250407 --assets XLE --axis oil
    python asset_extension.py --date 20250407 --all
    python asset_extension.py --prediction        # test the registered claim
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_event import (HL_D, CLUSTERING_PCS, load_data, _z_expanding,
                              regime_labels_expanding, select_sigma,
                              kernel_weights, estimate, DEFAULT)
from src.data_io import load_config, PROCESSED_DIR
from step6_report import load_reads, fwd_returns, NEGLIGIBLE, PRIMARY_H

REPO = PROCESSED_DIR.parent
OUT_DIR = REPO / "outputs" / "assets"

AXIS_COL = {"equity": "dir_eq", "duration": "dir_dur", "gold": "dir_gold",
            "dollar": "dir_usd", "oil": "dir_oil"}
PROXY = {"equity": "SPY", "duration": "TLT", "gold": "GLD",
         "dollar": "UUP", "oil": "USO"}

# role (config.yaml) -> axis. Exposed and overridable.
ROLE_AXIS = {
    "gold": "gold", "gold_alt": "gold", "silver": "gold",
    "long_treasuries": "duration",
    "usd_index": "dollar",
    "oil": "oil", "energy_broad": "oil", "energy_mlp": "oil",
    "energy_mlp_alt": "oil",
}
DEFAULT_AXIS = "equity"          # every other role: an equity claim


def axis_map(cfg):
    m = {}
    for grp in ("core", "overlay", "spotlight"):
        for a in cfg["assets"].get(grp, []):
            m[a["ticker"]] = (ROLE_AXIS.get(a["role"], DEFAULT_AXIS),
                              a["role"])
    return m


def run_asset(ticker, axis, t, ti, idx, scores, rets, Zall, labels_all, C,
              docs_today, docs_hist):
    col = AXIS_COL[axis]
    e = {"asset": ticker, "axis": axis, "axis_proxy": PROXY[axis],
         "is_proxy": ticker == PROXY[axis], "net_view": None,
         "dominant_source": None, "estimate": None, "abstain": True,
         "abstain_reason": None, "agreement": "UNINFORMATIVE"}
    if ticker not in rets.columns:
        e["abstain_reason"] = f"{ticker} is not in the price panel"
        return e
    td = docs_today.copy()
    td["dir"] = pd.to_numeric(td[col], errors="coerce").fillna(0)
    live = td[td["dir"].abs() > NEGLIGIBLE]
    if not len(live) or live.weight.sum() <= 0:
        e["abstain_reason"] = f"no document with a {axis} direction today"
        return e
    wsum = live.weight.sum()
    e["net_view"] = float((live.weight * live["dir"]).sum() / wsum)
    dom = live.loc[live.weight.idxmax()]
    e["dominant_source"] = str(dom.source)
    cls = float(np.sign(e["net_view"]))

    hd = docs_hist.copy()
    hd["dir"] = pd.to_numeric(hd[col], errors="coerce").fillna(0)
    pool = hd[(hd["dir"].abs() > NEGLIGIBLE) & (np.sign(hd["dir"]) == cls)]
    f = fwd_returns(rets, ticker, PRIMARY_H)
    ppos = np.array(sorted({int(idx.get_loc(s)) for s in pool.session}),
                    dtype=int)
    ppos = ppos[(ppos > 252) & (ppos < ti)].astype(int)
    if ppos.size:
        ppos = ppos[np.isfinite(f[ppos]) & np.isfinite(Zall[ppos]).all(axis=1)
                    & (labels_all[ppos] >= 0)]
    e["pool_size"] = int(ppos.size)
    if ppos.size < 10:
        e["abstain_reason"] = (f"content-class pool too small "
                               f"({ppos.size} precedents with {ticker} prices)")
        return e
    ages = np.abs(ppos[:, None] - ppos[None, :]) / 252.0
    sigma, _, _, _ = select_sigma(Zall[ppos], Zall[ppos], ages, len(ppos))
    w = kernel_weights(Zall[ppos], Zall[ti], (ti - ppos) / 252.0, sigma, HL_D)
    est = estimate(f[ppos], w, labels_all[ppos], C)
    e["estimate"] = {k: (None if isinstance(v, float) and not np.isfinite(v)
                         else v) for k, v in est.items()}
    e["abstain"] = bool(est["abstain"])
    if est["abstain"]:
        e["abstain_reason"] = (f"realised ESS {est['ess']:.1f} below the "
                               f"registered floor of 8")
    pt = est["estimate"]
    if pt is not None and np.isfinite(pt) and abs(pt) > 1e-12:
        e["agreement"] = ("CONCORDANT" if np.sign(e["net_view"]) == np.sign(pt)
                          else "DISCORDANT")
    return e


def render(t, results):
    L = [f"# Asset view — {t.date()}", "",
         "*Any asset, through the five-axis route. The axis that conditioned "
         "each asset is named; where the asset is not the axis proxy, the "
         "conditioning is macro-level and carries no sector content.*", ""]
    for e in results:
        L.append(f"## {e['asset']}  ·  axis **{e['axis']}**"
                 + ("" if e["is_proxy"] else f"  (proxy {e['axis_proxy']})"))
        if e["net_view"] is None:
            L += ["", f"**ABSTAIN.** {e['abstain_reason']}.", ""]
            continue
        L += ["", f"Net view on the {e['axis']} axis today: "
              f"**{e['net_view']:+.3f}**, dominant source "
              f"**{e['dominant_source']}**.", ""]
        est = e["estimate"]
        if est is None:
            L += [f"**ABSTAIN.** {e['abstain_reason']}.", ""]
            continue
        L += ["| quantity | value |", "|---|---|",
              f"| precedents (with {e['asset']} prices) | {est['n_matched']} |",
              f"| realised ESS | {est['ess']:.1f} |",
              f"| precedent strength `w` | {est['w_shrink']:.3f} |",
              f"| tier | {est['tier']} |",
              (f"| **blended estimate ({PRIMARY_H}-session)** | "
               f"**{est['estimate']:+.4%}** |") if est["estimate"] is not None
              else "| blended estimate | — |", ""]
        if e["abstain"]:
            L += [f"> **ABSTAIN.** {e['abstain_reason']}. Estimate printed for "
                  "transparency; not a recommendation.", ""]
        if e["agreement"] != "UNINFORMATIVE":
            L += [f"> Agreement: **{e['agreement']}** — display only. A "
                  "registered test found concordant cases performed worse "
                  "than discordant; this label changes no number.", ""]
        if not e["is_proxy"]:
            L += [f"> *{e['asset']} was conditioned on the {e['axis']} axis. "
                  "The document read says nothing specific to this asset's "
                  "sector; schema v2's sector axes are the registered route "
                  "to that.*", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--assets", help="comma-separated tickers")
    ap.add_argument("--axis", choices=list(AXIS_COL),
                    help="override the axis for every asset named")
    ap.add_argument("--all", action="store_true", help="all 47 in config")
    ap.add_argument("--prediction", action="store_true",
                    help="test the registered prediction across ~40 sessions")
    a = ap.parse_args()

    cfg = load_config()
    scores, rets = load_data()
    idx = pd.DatetimeIndex(scores.index)
    C = int(DEFAULT["n_regimes"])
    labels_all = regime_labels_expanding(scores, cfg)
    Zall = _z_expanding(scores[CLUSTERING_PCS].values)
    amap = axis_map(cfg)

    docs = load_reads()
    pos = idx.searchsorted(pd.DatetimeIndex(docs["date"].values), side="left")
    ok = pos < len(idx)
    docs = docs.loc[ok].copy()
    docs["session"] = idx[pos[ok]]
    for c in ("magnitude", "specificity", "novelty", "confidence"):
        docs[c] = pd.to_numeric(docs.get(c), errors="coerce")
    docs["weight"] = (docs.magnitude.fillna(0) * docs.specificity.fillna(0)
                      * docs.novelty.fillna(0) * docs.confidence.fillna(0))

    def one_session(t, tickers, axis_override=None):
        ti = int(idx.get_loc(t))
        today, hist = docs[docs.session == t], docs[docs.session < t]
        out = []
        for tk in tickers:
            ax = axis_override or amap.get(tk, (DEFAULT_AXIS, "?"))[0]
            out.append(run_asset(tk, ax, t, ti, idx, scores, rets, Zall,
                                 labels_all, C, today, hist))
        return out

    if a.prediction:
        # REGISTERED PREDICTION: equity-axis non-proxies show lower median w
        # than SPY on the same sessions.
        eq = [tk for tk, (ax, _) in amap.items() if ax == "equity"
              and tk in rets.columns]
        sess = [s for s in idx[idx >= "2015-01-01"][::40]
                if s in set(docs.session)]
        rows = []
        for t in sess:
            for e in one_session(t, eq):
                if e["estimate"]:
                    rows.append((str(t.date()), e["asset"], e["is_proxy"],
                                 e["estimate"]["w_shrink"],
                                 e["estimate"]["ess"], e["estimate"]["tier"]))
        d = pd.DataFrame(rows, columns=["date", "asset", "proxy", "w", "ess",
                                        "tier"])
        px, npx = d[d.proxy], d[~d.proxy]
        print("=" * 70)
        print("REGISTERED PREDICTION -- equity-axis non-proxies vs SPY")
        print("=" * 70)
        print(f"  sessions {len(sess)}   SPY asset-days {len(px)}   "
              f"other equity asset-days {len(npx)}")
        print(f"  median w   SPY {px.w.median():.3f}   others "
              f"{npx.w.median():.3f}")
        print(f"  median ESS SPY {px.ess.median():.1f}   others "
              f"{npx.ess.median():.1f}")
        print(f"  tier-1 rate SPY {100*(px.tier==1).mean():.0f}%   others "
              f"{100*(npx.tier==1).mean():.0f}%")
        held = npx.w.median() < px.w.median()
        print(f"\n  prediction {'HELD' if held else 'NOT HELD'}: "
              + ("macro-axis conditioning is weaker off the proxy, as "
                 "registered -- sector specificity matters and schema v2's "
                 "sector axes would add value."
                 if held else
                 "sector ETFs condition as well as SPY on a macro-equity read. "
                 "Sector specificity in the document does not matter here, "
                 "and schema v2 is less valuable than assumed."))
        print("\n  per asset, median w:")
        for tk, g in npx.groupby("asset"):
            print(f"    {tk:6} w {g.w.median():.3f}  ESS {g.ess.median():5.1f}  "
                  f"n={len(g)}")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "prediction_test.json").write_text(json.dumps(
            dict(held=bool(held), spy_w=float(px.w.median()),
                 others_w=float(npx.w.median()), n_spy=len(px),
                 n_others=len(npx)), indent=2))
        return

    if not a.date:
        raise SystemExit("give --date YYYYMMDD")
    t = pd.Timestamp(a.date)
    if t not in idx:
        t = idx[idx >= t][0]
    tickers = ([tk for tk in amap if tk in rets.columns] if a.all
               else [x.strip().upper() for x in (a.assets or "").split(",")
                     if x.strip()])
    if not tickers:
        raise SystemExit("give --assets or --all")
    res = one_session(t, tickers, a.axis)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = t.strftime("%Y%m%d")
    md = render(t, res)
    (OUT_DIR / f"{stem}.md").write_text(md)
    (OUT_DIR / f"{stem}.json").write_text(json.dumps(res, indent=2,
                                                     default=str))
    print(md)
    print(f"  -> {OUT_DIR / (stem + '.md')}")


if __name__ == "__main__":
    main()
