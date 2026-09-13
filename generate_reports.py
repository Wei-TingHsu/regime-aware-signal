"""
generate_reports.py -- pre-generate step 6 reports, and measure the pipeline's
actual coverage.

WHY PRE-GENERATE
    step6_report.py fits a 10-restart GMM per report to get the regime
    posterior. That is seconds per report, which is fine on the command line
    and unusable in a UI where someone is clicking between dates. The app must
    READ, never compute -- both for speed and because a number computed live in
    a demo has no commit behind it.

WHY THE COVERAGE TABLE MATTERS MORE THAN THE REPORTS
    "Does the pipeline work for all conditions and regimes?" is answerable only
    by counting. If the document corpus sits mostly in one or two regimes, the
    engine has never been exercised in the others and the demo cannot show
    them. That is a coverage fact about the corpus, not a defect in the code,
    and it belongs in front of the user rather than in a footnote.

    Reported per regime: sessions, sessions carrying documents, net views,
    estimates produced, and the tier split.

Run:
    python generate_reports.py --docs-only        # the 1,566 document sessions
    python generate_reports.py --docs-only --limit 200
    python generate_reports.py --coverage-only    # count, generate nothing
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from step6_report import (build_report, render_md, REPORT_DIR, AX, READS,
                          NEGLIGIBLE)
from src.analog_event import load_data, regime_labels_expanding
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "pipeline_coverage.md"
OUT_JSON = PROCESSED_DIR / "pipeline_coverage.json"
INDEX = PROCESSED_DIR / "report_index.json"


def document_sessions(idx):
    fr = [pd.read_csv(PROCESSED_DIR / f) for f in READS
          if (PROCESSED_DIR / f).exists()]
    df = pd.concat(fr, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "source"])
    pos = idx.searchsorted(pd.DatetimeIndex(df["date"].values), side="left")
    ok = pos < len(idx)
    df = df.loc[ok].copy()
    df["session"] = idx[pos[ok]]
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-only", action="store_true")
    ap.add_argument("--recent", type=int, default=0, metavar="N",
                    help="also generate the last N panel sessions even if no "
                         "document landed on them. Without this the index ends "
                         "at the newest DOCUMENT session, so a user cannot "
                         "select today and sees a stale date instead of "
                         "'no news today' -- which is the answer they came for.")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--coverage-only", action="store_true")
    ap.add_argument("--index-only", action="store_true",
                    help="rebuild report_index.json from the report files "
                         "already on disk; write no report. The nightly job "
                         "uses this so an emitted report is never rewritten.")
    args = ap.parse_args()

    cfg = load_config()
    scores, _ = load_data()
    idx = pd.DatetimeIndex(scores.index)
    labels = regime_labels_expanding(scores, cfg)
    docs = document_sessions(idx)
    doc_sessions = sorted(docs.session.unique())

    print("=" * 76)
    print("PIPELINE COVERAGE")
    print("=" * 76)
    print(f"  panel sessions              {len(idx)}")
    print(f"  sessions carrying documents {len(doc_sessions)} "
          f"({100*len(doc_sessions)/len(idx):.0f}%)")
    print(f"  documents mapped            {len(docs)}")
    print(f"  assets in the reader schema {len(AX)} — {', '.join(AX)}")
    print(f"     (the 47-asset universe belongs to step 1; step 3 covers only")
    print(f"      the five macro axes the reader schema defines)")

    # ---- coverage by regime -------------------------------------------
    lab_of = pd.Series(labels, index=idx)
    per = defaultdict(lambda: dict(sessions=0, doc_sessions=0, documents=0))
    for s, l in lab_of.items():
        if l >= 0:
            per[int(l)]["sessions"] += 1
    ds = set(doc_sessions)
    for s in ds:
        l = int(lab_of.loc[s])
        if l >= 0:
            per[l]["doc_sessions"] += 1
    for s, g in docs.groupby("session"):
        l = int(lab_of.loc[s]) if s in lab_of.index else -1
        if l >= 0:
            per[l]["documents"] += len(g)

    print(f"\n  {'regime':>7} {'sessions':>10} {'with docs':>11} "
          f"{'% covered':>10} {'documents':>11}")
    for r in sorted(per):
        d = per[r]
        pct = 100 * d["doc_sessions"] / d["sessions"] if d["sessions"] else 0
        print(f"  {r:>7} {d['sessions']:>10} {d['doc_sessions']:>11} "
              f"{pct:>9.0f}% {d['documents']:>11}")
    thin = [r for r, d in per.items()
            if d["sessions"] and d["doc_sessions"] / d["sessions"] < 0.10]
    if thin:
        print(f"\n  ** REGIME(S) {thin} carry documents on under 10% of their")
        print(f"     sessions. The engine has barely been exercised there and")
        print(f"     the demo cannot honestly show those regimes at work.")
    else:
        print(f"\n  Every regime carries documents on at least 10% of its")
        print(f"  sessions — the pipeline has been exercised in all of them.")

    cov = dict(run=datetime.now(timezone.utc).astimezone()
               .strftime("%Y-%m-%d %H:%M:%S %z"),
               panel_sessions=int(len(idx)),
               document_sessions=int(len(doc_sessions)),
               documents=int(len(docs)), assets=list(AX),
               by_regime={str(k): v for k, v in sorted(per.items())},
               thin_regimes=thin)

    if args.coverage_only:
        OUT_JSON.write_text(json.dumps(cov, indent=2))
        print(f"\n  -> {OUT_JSON}")
        return

    # ---- generate ------------------------------------------------------
    targets = doc_sessions if args.docs_only else list(idx)
    if args.limit:
        targets = targets[-args.limit:]
    if args.recent:
        # union, preserving panel order, so today is always selectable
        extra = [t for t in list(idx)[-args.recent:] if t not in set(targets)]
        targets = sorted(set(list(targets) + extra))
        print(f"  + {len(extra)} recent session(s) with no documents, so the "
              f"latest date is always selectable")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    written, tiers, index = 0, defaultdict(int), []

    def _index_row(R):
        nv = sum(1 for e in R["assets"].values() if e["net_view"] is not None)
        ab = sum(1 for e in R["assets"].values() if e["abstain"])
        best = 3
        for e in R["assets"].values():
            if e.get("estimate"):
                tiers[e["estimate"]["tier"]] += 1
                best = min(best, int(e["estimate"]["tier"]))
        return dict(date=R["date"], regime=R["regime"]["label"],
                    posterior=R["regime"]["posterior"],
                    n_docs=len(R["documents"]), n_views=nv,
                    n_abstain=ab, best_tier=best)

    if args.index_only:
        # FROZEN REPORTS (2026-09-13). A report under outputs/reports/ is
        # never rewritten. The nightly job writes today's report once
        # (step6_report.py --latest) and rebuilds the index from what is on
        # disk. Regeneration writes to a backfill folder, never here.
        # Until this date the nightly --limit 30 --recent 10 call rewrote
        # the 40 most recent reports every night.
        targets = []
        for pth in sorted(REPORT_DIR.glob("*.json")):
            try:
                index.append(_index_row(json.loads(pth.read_text())))
            except Exception as e:
                print(f"    {pth.name}: unreadable ({type(e).__name__}), skipped")
        print(f"\n  index-only: {len(index)} report(s) on disk, none rewritten")
    else:
        print(f"\n  generating {len(targets)} report(s)...")
    for i, t in enumerate(targets):
        stem = pd.Timestamp(t).strftime("%Y%m%d")
        try:
            R = build_report(stem)
        except SystemExit:
            continue
        (REPORT_DIR / f"{stem}.md").write_text(render_md(R))
        (REPORT_DIR / f"{stem}.json").write_text(
            json.dumps(R, indent=2, default=str))
        nv = sum(1 for e in R["assets"].values() if e["net_view"] is not None)
        ab = sum(1 for e in R["assets"].values() if e["abstain"])
        best = 3
        for e in R["assets"].values():
            if e.get("estimate"):
                tiers[e["estimate"]["tier"]] += 1
                best = min(best, int(e["estimate"]["tier"]))
        index.append(dict(date=R["date"], regime=R["regime"]["label"],
                          posterior=R["regime"]["posterior"],
                          n_docs=len(R["documents"]), n_views=nv,
                          n_abstain=ab, best_tier=best))
        written += 1
        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{len(targets)}", flush=True)

    # Merge with whatever is already indexed: a --limit run must not shrink
    # the picker to the handful of dates it happened to regenerate.
    prev = []
    if INDEX.exists():
        try:
            prev = json.loads(INDEX.read_text())
        except Exception:
            prev = []
    merged = {r["date"]: r for r in prev}
    merged.update({r["date"]: r for r in index})
    index = [merged[k] for k in sorted(merged)]
    INDEX.write_text(json.dumps(index, indent=2))
    print(f"  index now spans {index[0]['date']} to {index[-1]['date']} "
          f"({len(index)} dates)")
    print(f"\n  written {written} report pairs -> {REPORT_DIR}")
    print(f"  tier counts across all asset-days: "
          + "  ".join(f"tier {k}: {v}" for k, v in sorted(tiers.items())))
    cov["reports_written"] = written
    cov["tier_counts"] = {str(k): v for k, v in sorted(tiers.items())}
    OUT_JSON.write_text(json.dumps(cov, indent=2))

    L = ["# Pipeline coverage", "", f"*Run {cov['run']}.*", "",
         f"The engine covers **{len(doc_sessions)} of {len(idx)} panel "
         f"sessions** ({100*len(doc_sessions)/len(idx):.0f}%) — the rest carry "
         f"no document, so every asset abstains for the plainest reason there "
         f"is. It covers **{len(AX)} assets**, the macro axes the reader schema "
         f"defines; the 47-asset universe belongs to step 1.", "",
         "| regime | sessions | with documents | % | documents |",
         "|---|---|---|---|---|"]
    for r in sorted(per):
        d = per[r]
        pct = 100 * d["doc_sessions"] / d["sessions"] if d["sessions"] else 0
        L.append(f"| {r} | {d['sessions']} | {d['doc_sessions']} | {pct:.0f}% "
                 f"| {d['documents']} |")
    L += ["", ("**Regimes " + str(thin) + " carry documents on under 10% of "
               "their sessions.** The engine has barely been exercised there."
               if thin else
               "Every regime carries documents on at least 10% of its "
               "sessions."), "",
          "Tier counts across all generated asset-days: "
          + ", ".join(f"tier {k}: {v}" for k, v in sorted(tiers.items()))
          + ".", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"  -> {OUT_MD}\n  -> {OUT_JSON}\n  -> {INDEX}")


if __name__ == "__main__":
    main()
