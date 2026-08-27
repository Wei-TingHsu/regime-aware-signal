"""
step5_weighting.py -- STEP 5, the weighted net view. prereg_analog_event.md §7.

WHAT IS IMPLEMENTED, AND WHAT IS DELIBERATELY NOT
    §7.2 FIXED RULE, implemented exactly as registered:

        weight_d         = magnitude * specificity * novelty * confidence
        net_direction[a] = SUM(weight_d * direction_d[a]) / SUM(weight_d)

    A straight product, so any near-zero field vetoes the document -- the
    registered intent for a low-specificity threat-to-act. `specificity^2` is
    NOT used: §7.2 forbids it by name as an unregistered strength parameter.
    The §4 gate PASSED (spread 0.517, CI [0.494, 0.539]), so `specificity`
    stays in the product and no substitution is reported.

    §7.3 ESTIMATED ALTERNATIVE is NOT implemented here. §7.3's own words:
    "Requires its own registration before running; it is not authorised by this
    document." Clearing the §7.1 threshold makes §7.3 ADMISSIBLE, not
    permitted. Writing it now, after seeing which sources look strong, is the
    move this project exists to forbid. A separate pre-registration is the
    only route to it.

THE §7.1 COUNT, COMPUTED CORRECTLY
    §7.1 registers "the number of days carrying documents from TWO OR MORE
    DIFFERENT SOURCES" -- one number over days, not a per-asset tally summed
    across assets. An earlier count (count_collisions.py, 194) computed the
    per-asset version and is superseded for this purpose. Both are reported
    here so the difference is visible rather than silently corrected.

WHAT A WEIGHTING RULE CAN AND CANNOT BUY
    It only ever changes the sign of the net view on days where the documents
    DISAGREE. Where they agree, every non-negative weighting scheme returns the
    same direction. So the disagreement count -- not the collision count -- is
    the real sample size for any estimated rule, and it is reported alongside.

No API calls. Reads cached reads and the panel index.

Run:
    python step5_weighting.py                 # compute and write
    python step5_weighting.py --show 20260814 # inspect one session
"""
import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_event import load_data
from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "step5_net_view.md"
OUT_CSV = PROCESSED_DIR / "step5_net_view.csv"
OUT_JSON = PROCESSED_DIR / "step5_weighting.json"
AX = {"GLD": "dir_gold", "SPY": "dir_eq", "TLT": "dir_dur",
      "UUP": "dir_usd", "USO": "dir_oil"}
READS = ("read_statement.csv", "read_minutes.csv", "read_8k.csv",
         "read_political_order.csv", "read_political_other.csv")
NEGLIGIBLE = 0.05
REGISTERED_MIN = 50          # §7.1
GATE_PASSED = True           # §4 gate: spread 0.517, CI [0.494, 0.539]


def load_reads():
    frames = [pd.read_csv(PROCESSED_DIR / f) for f in READS
              if (PROCESSED_DIR / f).exists()]
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date", "source"]).drop_duplicates(
        subset=["source", "date", "doc_id"], keep="last")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", help="YYYYMMDD, print one session in detail")
    args = ap.parse_args()

    scores, _ = load_data()
    idx = pd.DatetimeIndex(scores.index)
    df = load_reads()

    # forward-only mapping to the entry session, identical to unblind_step3.py
    pos = idx.searchsorted(pd.DatetimeIndex(df["date"].values), side="left")
    ok = pos < len(idx)
    df = df.loc[ok].copy()
    df["session"] = idx[pos[ok]]

    for c in ("magnitude", "specificity", "novelty", "confidence"):
        df[c] = pd.to_numeric(df.get(c), errors="coerce")

    # ---- §7.1, the registered count ------------------------------------
    per_session_sources = df.groupby("session").source.nunique()
    registered_count = int((per_session_sources >= 2).sum())
    print("=" * 78)
    print("STEP 5 -- WEIGHTED NET VIEW.  prereg_analog_event.md §7")
    print("=" * 78)
    print(f"  §7.1 REGISTERED COUNT: days carrying documents from two or more")
    print(f"       different sources = {registered_count}"
          f"   (threshold {REGISTERED_MIN})")
    branch = ("ADMISSIBLE but NOT AUTHORISED by this document"
              if registered_count >= REGISTERED_MIN else "NOT attempted")
    print(f"       -> §7.2 fixed rule is used. §7.3 is {branch} and is not "
          f"implemented here.")
    print(f"  §4 gate PASSED, so `specificity` stays in the weight product; no")
    print(f"       substitution reported.")

    # ---- §7.2, the fixed rule ------------------------------------------
    # Straight product. Any near-zero field vetoes the document.
    df["weight"] = (df.magnitude.fillna(0) * df.specificity.fillna(0)
                    * df.novelty.fillna(0) * df.confidence.fillna(0))

    rows, dis_total = [], 0
    for asset, axcol in AX.items():
        if axcol not in df.columns:
            continue
        d = df.copy()
        d["dir"] = pd.to_numeric(d[axcol], errors="coerce").fillna(0)
        live = d[d["dir"].abs() > NEGLIGIBLE]
        for sess, g in live.groupby("session"):
            wsum = g.weight.sum()
            if wsum <= 0:
                # every document vetoed by a near-zero field: this is an
                # ABSTENTION, not a zero view, and is recorded as one.
                rows.append(dict(session=sess, asset=asset, n_docs=len(g),
                                 n_sources=int(g.source.nunique()),
                                 net=np.nan, weight_sum=0.0,
                                 dominant=None, disagree=None,
                                 status="ABSTAIN — all documents vetoed"))
                continue
            net = float((g.weight * g["dir"]).sum() / wsum)
            dom = g.loc[g.weight.idxmax()]
            disagree = len(set(np.sign(g["dir"].values))) > 1
            if disagree:
                dis_total += 1
            rows.append(dict(session=sess, asset=asset, n_docs=len(g),
                             n_sources=int(g.source.nunique()),
                             net=net, weight_sum=float(wsum),
                             dominant=f"{dom.source}",
                             dominant_weight=float(dom.weight),
                             dominant_share=float(dom.weight / wsum),
                             disagree=bool(disagree),
                             status="ok"))
    net = pd.DataFrame(rows).sort_values(["session", "asset"])
    net.to_csv(OUT_CSV, index=False)

    multi = net[net.n_docs >= 2]
    print(f"\n  net views produced: {len(net)}  "
          f"({len(multi)} from two or more documents)")
    print(f"  sign disagreements among those: {dis_total} "
          f"-- the real sample size for any ESTIMATED rule")
    print(f"  abstentions (all documents vetoed): "
          f"{int((net.status != 'ok').sum())}")

    print(f"\n  {'asset':6} {'views':>7} {'multi':>7} {'disagree':>9} "
          f"{'mean |net|':>11} {'mean weight':>12}")
    per = {}
    for a, g in net.groupby("asset"):
        gm = g[g.n_docs >= 2]
        per[a] = dict(views=int(len(g)), multi=int(len(gm)),
                      disagree=int(gm.disagree.fillna(False).sum()),
                      mean_abs_net=float(g.net.abs().mean()),
                      mean_weight=float(g.weight_sum.mean()))
        print(f"  {a:6} {len(g):7d} {len(gm):7d} "
              f"{int(gm.disagree.fillna(False).sum()):9d} "
              f"{g.net.abs().mean():11.3f} {g.weight_sum.mean():12.3f}")

    # which source dominates when there IS a disagreement -- REPORTED ONLY.
    # This is descriptive. It is NOT the §7.3 estimated rule and must not be
    # turned into weights without a separate registration.
    dd = net[(net.disagree == True) & (net.status == "ok")]
    if len(dd):
        print(f"\n  dominant source on the {len(dd)} disagreement days "
              f"(DESCRIPTIVE ONLY -- not a fitted weight):")
        for src, c in dd.dominant.value_counts().items():
            print(f"     {src:20} {c:4}  ({100*c/len(dd):.0f}%)")
        print("  Turning this table into weights is §7.3 and requires its own")
        print("  pre-registration. It is printed, not used.")

    if args.show:
        t = pd.Timestamp(args.show)
        sel = net[net.session == t]
        print(f"\n  --- session {t.date()} ---")
        if sel.empty:
            print("     no net view on this session")
        for _, r in sel.iterrows():
            print(f"   {r.asset}: net {r.net:+.3f} from {r.n_docs} doc(s), "
                  f"{r.n_sources} source(s), dominant {r.dominant} "
                  f"({100*r.get('dominant_share', 0):.0f}% of weight)"
                  f"{'  [SOURCES DISAGREE]' if r.disagree else ''}")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Step 5 — weighted net view", "", f"*Run {ts}. No API calls.*", "",
         "**Rule implemented: `prereg_analog_event.md` §7.2, fixed.** "
         "`weight = magnitude · specificity · novelty · confidence`; "
         "`net = Σ(weight · direction) / Σ(weight)`. A straight product, so any "
         "near-zero field vetoes the document. `specificity²` is not used — "
         "§7.2 forbids it by name. The §4 gate passed, so `specificity` stays "
         "in and no substitution is reported.", "",
         f"**§7.1 registered count: {registered_count} days carry documents "
         f"from two or more different sources**, against a threshold of "
         f"{REGISTERED_MIN} fixed on 2026-08-24 before any counting. §7.3, the "
         "estimated alternative, is therefore *admissible* — but it is **not "
         "authorised by that document** and is not implemented here. It needs "
         "its own pre-registration.", "",
         "*(An earlier script counted per-asset collisions and summed them to "
         "194. That is a different statistic from the one §7.1 registers; both "
         "are reported so the correction is visible rather than silent.)*", "",
         "| asset | net views | from ≥2 docs | sign disagreements | mean \\|net\\| | mean weight |",
         "|---|---|---|---|---|---|"]
    for a, d in per.items():
        L.append(f"| {a} | {d['views']} | {d['multi']} | {d['disagree']} | "
                 f"{d['mean_abs_net']:.3f} | {d['mean_weight']:.3f} |")
    L += ["", f"Abstentions (every document vetoed by a near-zero field): "
              f"**{int((net.status != 'ok').sum())}**. These are recorded as "
              "abstentions, not as a zero view — the distinction the product "
              "turns on.", "",
          "**A weighting rule only changes the sign of the net view where the "
          "documents disagree.** Where they agree, every non-negative scheme "
          f"gives the same answer. The {dis_total} disagreement days are the "
          "real sample size for any estimated rule, and that is a thin base — "
          "thinner than the step 3 cells that failed re-testing.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(
        dict(run=ts, registered_count_days_multi_source=registered_count,
             threshold=REGISTERED_MIN, rule="7.2 fixed",
             gate_passed=GATE_PASSED, per_asset=per,
             disagreements=dis_total,
             abstentions=int((net.status != "ok").sum())), indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_CSV}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
