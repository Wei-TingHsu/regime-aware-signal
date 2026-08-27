"""
count_collisions.py -- how many same-day, same-asset document COLLISIONS exist?

WHY THIS RUNS BEFORE STEP 5 IS WRITTEN
    prereg_analog_event.md section 10 registers the branch:

        "Collisions < 50 -> section 7.3 is not attempted and step 5 ships on
         the FIXED rule."

    Step 5 turns several documents landing on one day into one net view per
    asset. If the weights are to be ESTIMATED rather than asserted, there must
    be enough days carrying more than one document to estimate them from. That
    count is registered as the deciding number and it has never been computed.

    So this is not a diagnostic, it is the registered precondition. The answer
    determines which step 5 gets built, and it costs nothing.

WHAT COUNTS AS A COLLISION
    Two or more documents whose ENTRY SESSION and ASSET are the same, and whose
    reader direction on that asset's axis clears the same |direction| > 0.05
    floor the estimator uses. Documents below the floor are not competing views;
    they are silence, and silence does not need weighing.

    Entry session, not publication date: two documents published on a Saturday
    and a Sunday both enter at Monday's close and DO collide. Mapping is
    forward-only, identical to unblind_step3.py.

WHAT IS REPORTED
    - collisions by asset and by size (2 documents, 3, 4+)
    - how many are CROSS-SOURCE (an 8-K against an FOMC statement) versus
      within one source, because only cross-source collisions can inform a rule
      about which SOURCE to trust more
    - how often colliding documents DISAGREE in sign, since a weighting rule
      only changes the answer when they disagree

No API calls. Reads cached reads and the panel index.

Run:  python count_collisions.py
"""
import json
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_event import load_data
from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "collision_count.md"
OUT_JSON = PROCESSED_DIR / "collision_count.json"
AX = {"GLD": "dir_gold", "SPY": "dir_eq", "TLT": "dir_dur",
      "UUP": "dir_usd", "USO": "dir_oil"}
READS = ("read_statement.csv", "read_minutes.csv", "read_8k.csv",
         "read_political_order.csv", "read_political_other.csv")
NEGLIGIBLE = 0.05
REGISTERED_MIN = 50          # prereg section 10


def main():
    scores, _ = load_data()
    idx = pd.DatetimeIndex(scores.index)

    frames = []
    for f in READS:
        p = PROCESSED_DIR / f
        if p.exists():
            frames.append(pd.read_csv(p))
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "source"]).drop_duplicates(
        subset=["source", "date", "doc_id"], keep="last")

    # forward-only mapping to the entry session, identical to unblind_step3.py
    pos = idx.searchsorted(pd.DatetimeIndex(df["date"].values), side="left")
    ok = pos < len(idx)
    df = df.loc[ok].copy()
    df["session"] = idx[pos[ok]]

    print("=" * 76)
    print("SAME-DAY DOCUMENT COLLISIONS -- the registered precondition for step 5")
    print("prereg_analog_event.md section 10: collisions < 50 -> FIXED rule")
    print("=" * 76)
    print(f"  {len(df)} reads mapped to {df.session.nunique()} entry sessions")

    out, total = {}, 0
    for asset, axcol in AX.items():
        if axcol not in df.columns:
            continue
        v = pd.to_numeric(df[axcol], errors="coerce").fillna(0)
        live = df[v.abs() > NEGLIGIBLE].copy()
        live["dir"] = v[v.abs() > NEGLIGIBLE].values
        g = live.groupby("session")
        sizes = g.size()
        coll = sizes[sizes >= 2]
        # cross-source and sign-disagreement among colliding days
        cross = disagree = 0
        for sess, grp in g:
            if len(grp) < 2:
                continue
            if grp.source.nunique() > 1:
                cross += 1
            if len(set(np.sign(grp["dir"].values))) > 1:
                disagree += 1
        by_size = Counter(coll.values)
        out[asset] = dict(live_docs=int(len(live)),
                          sessions_with_any=int(sizes.size),
                          collisions=int(coll.size),
                          cross_source=int(cross),
                          sign_disagree=int(disagree),
                          size_2=int(by_size.get(2, 0)),
                          size_3=int(by_size.get(3, 0)),
                          size_4plus=int(sum(n for k, n in by_size.items()
                                             if k >= 4)))
        total += int(coll.size)
        print(f"\n  {asset}: {len(live)} documents above the floor on "
              f"{sizes.size} sessions")
        print(f"     collisions (>=2 docs on one session): {coll.size}")
        print(f"       of size 2: {by_size.get(2,0)}   size 3: "
              f"{by_size.get(3,0)}   size 4+: "
              f"{sum(n for k,n in by_size.items() if k>=4)}")
        print(f"       cross-source: {cross}   opposite signs: {disagree}")

    print("\n" + "=" * 76)
    print(f"  TOTAL COLLISIONS ACROSS ASSETS: {total}")
    branch = ("ESTIMATED weights are admissible (section 7.3 attempted)"
              if total >= REGISTERED_MIN else
              "FIXED rule -- section 7.3 NOT attempted (prereg section 10)")
    print(f"  Registered threshold: {REGISTERED_MIN}")
    print(f"  -> STEP 5 BRANCH: {branch}")
    print("=" * 76)
    print("\n  Note on what a weighting rule can and cannot buy: it only ever")
    print("  changes the answer on collisions where the documents DISAGREE in")
    print("  sign. Agreeing documents produce the same net direction under any")
    print("  non-negative weights. The disagreement column is therefore the")
    print("  real sample size for the rule, not the collision count.")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Same-day document collisions", "", f"*Run {ts}. No API calls.*", "",
         "*Registered precondition for step 5: `prereg_analog_event.md` §10 — "
         f"collisions < {REGISTERED_MIN} means §7.3 is not attempted and step 5 "
         "ships on the fixed rule.*", "",
         "| asset | docs above floor | sessions | collisions | size 2 | size 3 "
         "| size 4+ | cross-source | opposite signs |",
         "|---|---|---|---|---|---|---|---|---|"]
    for a, d in out.items():
        L.append(f"| {a} | {d['live_docs']} | {d['sessions_with_any']} | "
                 f"**{d['collisions']}** | {d['size_2']} | {d['size_3']} | "
                 f"{d['size_4plus']} | {d['cross_source']} | "
                 f"{d['sign_disagree']} |")
    L += ["", f"**Total collisions: {total}** against a registered threshold of "
              f"{REGISTERED_MIN}.", "", f"**Step 5 branch: {branch}**", "",
          "A weighting rule only changes the answer where colliding documents "
          "disagree in sign — agreeing documents give the same net direction "
          "under any non-negative weights. The opposite-signs column is the "
          "real sample size for estimating a rule.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(dict(run=ts, per_asset=out, total=total,
                                        threshold=REGISTERED_MIN,
                                        branch=branch), indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
