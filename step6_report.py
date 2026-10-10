"""
step6_report.py -- STEP 6, the decision report. prereg_analog_event.md §8.

ONE FUNCTION, TWO FILES
    §8 requires "one Markdown file per day at outputs/reports/YYYYMMDD.md plus
    identical JSON, BOTH EMITTED FROM ONE FUNCTION so they cannot diverge."
    build_report() returns one dict; render_md() and json.dump() both consume
    that dict and nothing else. There is no second code path that could drift.

THE SEVEN REQUIRED FIELDS, and where each comes from
    1. macro state, regime, posterior confidence -- below 60% printed as a
       WARNING, not a footnote.
    2. every document read that day, with evidence quotes.
    3. per asset: blended estimate, realised ESS, precedent strength w,
       matched-event count, tier. From analog_event.estimate(), imported and
       called -- never reimplemented.
    4. the agreement flag; on divergence, BOTH numbers and NO combined figure.
    5. net view per asset with the dominant source named (step 5, §7.2).
    6. what the system cannot see -- CURRENT_STATE §8, printed in full in
       every report, not linked.
    7. no performance number that has not matured.

HOW THE POOL IS BUILT, and why
    The query is today's macro state. The pool is HISTORICAL events on the same
    asset whose reader direction carries the SAME SIGN as today's net view --
    the content class of §2.1, applied forward. Only events strictly BEFORE the
    report date enter, so a report for date t never sees t or later.

    Weights are kernel_weights(): macro similarity x recency decay, both frozen.
    sigma comes from select_sigma(). The blend is estimate(), which returns the
    tier and the abstention flag under the registered ESS floor.

AGREEMENT: DISPLAY ONLY
    Amendment 3 permitted the flag to move the interval, gated on a registered
    test. THAT TEST FAILED, and failed in the opposite direction: discordant
    cases outperformed concordant by 0.21%. Amendment 3's own clause therefore
    sets rho = 1 and the interval does not move. The label is displayed and
    changes no number. This is not a choice made here; it is the amendment's
    gate firing as written.

WHAT THIS REPORT WILL MOSTLY SAY
    Abstain. Under correct inference one document-conditioned cell of 45
    survived (CURRENT_STATE §17.7), so most assets on most days fall below the
    evidence floor. A report that abstains with its reason stated IS the
    product; a report that always produces a number would be the failure.

Run:
    python step6_report.py --date 20250407
    python step6_report.py --latest
    python step6_report.py --date 20250407 --print
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.analog_event import (HL_D, CLUSTERING_PCS, load_data, _z_expanding,
                              regime_labels_expanding, select_sigma,
                              kernel_weights, estimate, ess_of, DEFAULT)
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
REPORT_DIR = REPO / "outputs" / "reports"
AX = {"GLD": "dir_gold", "SPY": "dir_eq", "TLT": "dir_dur",
      "UUP": "dir_usd", "USO": "dir_oil"}
READS = ("read_statement.csv", "read_minutes.csv", "read_8k.csv",
         "read_political_order.csv", "read_political_other.csv")
NEGLIGIBLE, PRIMARY_H, CONF_WARN = 0.05, 2, 0.60   # h* 3 -> 2 on 2026-10-09 (amendment)

# ---- E4 lever (docs/prereg_asymmetry_levers.md §2), off unless LEVER=E4 ----------------------------------
import os as _os
LEVER_E4 = _os.environ.get("LEVER", "") == "E4"
LEVER_E1 = _os.environ.get("LEVER", "") == "E1"   # prereg_asymmetry_levers §3
_E4_BIN = {"fomc_statement": "intraday", "fomc_minutes": "intraday"}       # all other classes: overnight
_E4_OHLC = None
_E4_CACHE = {}


def _e4_bins(asset):
    global _E4_OHLC
    if _E4_OHLC is None:
        _E4_OHLC = pd.read_parquet("processed/ohlc_core.parquet")
    o, c = _E4_OHLC[(asset, "Open")], _E4_OHLC[(asset, "Close")]
    return pd.DataFrame({"overnight": np.log(o / c.shift(1)), "intraday": np.log(c / o)})


def e4_aligned(source, asset, axcol, hist, t):
    """True if this source class, on its precedents for `asset` before t, moved its own bin with the reading
    at least as often as the other bin. Expanding, through the precedents already in `hist` (<= t - PRIMARY_H)."""
    key = (source, asset, t)
    if key in _E4_CACHE: return _E4_CACHE[key]
    bins = _e4_bins(asset); own = _E4_BIN.get(source, "overnight"); other = "intraday" if own == "overnight" else "overnight"
    h = hist[hist.source == source]
    d = pd.to_numeric(h[axcol], errors="coerce")
    h = h.assign(dir=d)[d.abs() > NEGLIGIBLE]
    if len(h) < 30:
        _E4_CACHE[key] = True; return True
    b = bins.reindex(pd.DatetimeIndex(h.session.values))
    own_hits = (np.sign(b[own].values) == np.sign(h["dir"].values)).mean()
    other_hits = (np.sign(b[other].values) == np.sign(h["dir"].values)).mean()
    ok = bool(np.nan_to_num(own_hits) >= np.nan_to_num(other_hits))
    _E4_CACHE[key] = ok; return ok

# §8 item 6 -- CURRENT_STATE §8, verbatim. Printed in EVERY report, not linked.
CANNOT_SEE = [
    ("Manual-collection sources cannot scale to a daily product",
     "`transcript` and `bank_research` have no free structured feed. No option "
     "has been chosen between buying a vendor feed, declaring the gap to the "
     "customer, or dropping them from the live product."),
    ("The political source is biased toward DECIDED policy",
     "The Federal Register carries executive orders and proclamations — all "
     "high-specificity by construction. Statements, posts and rhetoric, "
     "precisely where a market-moving threat-to-act lives, are **not covered**. "
     "**An absence of low-specificity political events in any result below is a "
     "COVERAGE GAP, not evidence that rhetoric does not move markets.**"),
    ("Foreign private issuers file 6-K, not 8-K",
     "6-K carries no item codes, so the Item 2.02 filter that isolates earnings "
     "releases for domestic filers has no equivalent. Foreign issuers arrive "
     "with lower precision and cross-firm comparison must account for it."),
    ("The reader's five macro axes cannot represent a sector shock",
     "A steel tariff proclamation scores high specificity and near-zero "
     "direction because there is no axis to point at. Schema v2 is "
     "pre-registered and unfunded."),
    ("One conditional cell of 45 survived correct inference",
     "`fomc_minutes`/USO at h=5, inside the range expected by chance. Most "
     "assets on most days therefore abstain, and that is the honest state of "
     "the evidence, not a failure of the pipeline."),
]


def load_reads():
    fr = [pd.read_csv(PROCESSED_DIR / f) for f in READS
          if (PROCESSED_DIR / f).exists()]
    df = pd.concat(fr, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date", "source"]).drop_duplicates(
        subset=["source", "date", "doc_id"], keep="last")


def fwd_returns(rets, col, h):
    return np.expm1(np.log1p(rets[col]).rolling(h).sum().shift(-h)).values


def posterior_confidence(scores, cfg, upto):
    """Posterior of the assigned regime, from a GMM fit on data STRICTLY up to
    the query row. Its argmax is cross-checked against the cached expanding
    label; a mismatch is REPORTED, never silently preferred."""
    from sklearn.mixture import GaussianMixture
    C = int(DEFAULT["n_regimes"])
    X = scores[CLUSTERING_PCS].values
    if upto < 504:
        return None, None, "insufficient history (<504 sessions)"
    g = GaussianMixture(n_components=C, covariance_type="full", n_init=10,
                        max_iter=200, random_state=42).fit(X[:upto])
    order = np.argsort(g.means_[:, 0])          # canonical: ascending mean PC1
    remap = np.empty(C, int)
    remap[order] = np.arange(C)
    p = g.predict_proba(X[upto:upto + 1])[0]
    p = p[order]
    return int(np.argmax(p)), float(np.max(p)), None


def build_report(date_str):
    cfg = load_config()
    scores, rets = load_data()
    idx = pd.DatetimeIndex(scores.index)
    C = int(DEFAULT["n_regimes"])
    t = pd.Timestamp(date_str)
    if t not in idx:
        nxt = idx[idx >= t]
        if not len(nxt):
            raise SystemExit(f"{t.date()} is beyond the panel")
        t = nxt[0]
    ti = int(idx.get_loc(t))

    labels_all = regime_labels_expanding(scores, cfg)
    Zall = _z_expanding(scores[CLUSTERING_PCS].values)
    post_lab, post_p, post_note = posterior_confidence(scores, cfg, ti)
    cached_lab = int(labels_all[ti])

    R = {"date": str(t.date()), "generated": datetime.now(timezone.utc)
         .astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
         "prereg": "prereg_analog_event.md §8",
         "regime": {"label": cached_lab,
                    "posterior": post_p,
                    "posterior_label": post_lab,
                    "note": post_note,
                    "warning": (post_p is not None and post_p < CONF_WARN),
                    "label_mismatch": (post_lab is not None
                                       and post_lab != cached_lab)},
         "macro_state": {pc: float(scores[pc].iloc[ti])
                         for pc in CLUSTERING_PCS},
         "documents": [], "assets": {}, "cannot_see": CANNOT_SEE,
         "matured_performance": None}

    # ---- 2. documents read that day ------------------------------------
    docs = load_reads()
    pos = idx.searchsorted(pd.DatetimeIndex(docs["date"].values), side="left")
    ok = pos < len(idx)
    docs = docs.loc[ok].copy()
    docs["session"] = idx[pos[ok]]
    today = docs[docs.session == t]
    for _, d in today.iterrows():
        R["documents"].append({
            "source": d.source, "doc_id": str(d.get("doc_id", "")),
            "published": str(pd.Timestamp(d.date).date()),
            "direction": {a: (float(d[c]) if pd.notna(d.get(c)) else None)
                          for a, c in AX.items() if c in d},
            "magnitude": float(d.magnitude) if pd.notna(d.get("magnitude")) else None,
            "specificity": float(d.specificity) if pd.notna(d.get("specificity")) else None,
            "novelty": float(d.novelty) if pd.notna(d.get("novelty")) else None,
            "confidence": float(d.confidence) if pd.notna(d.get("confidence")) else None,
            "truncated": bool(d.get("truncated", False))})

    # ---- 5. net view, §7.2 fixed rule ----------------------------------
    for c in ("magnitude", "specificity", "novelty", "confidence"):
        today[c] = pd.to_numeric(today.get(c), errors="coerce")
    today = today.assign(weight=(today.magnitude.fillna(0)
                                 * today.specificity.fillna(0)
                                 * today.novelty.fillna(0)
                                 * today.confidence.fillna(0)))
    # POOL CUTOFF (registered 2026-09-14, prereg_report_scoreboard §11, step 7a).
    # A precedent's outcome is its PRIMARY_H-session forward return, so the pool
    # is documents at least PRIMARY_H sessions before t: every outcome in it had
    # closed by the close of t. `session < t` was harmless live (unclosed
    # outcomes are NaN) and a look-ahead in backfill (outcomes exist on disk).
    t_pos = int(idx.get_indexer([t])[0])
    hist = docs[docs.session <= idx[t_pos - PRIMARY_H]] if t_pos >= PRIMARY_H else docs.iloc[0:0]

    for asset, axcol in AX.items():
        entry = {"net_view": None, "dominant_source": None, "n_docs_today": 0,
                 "sources_disagree": False, "estimate": None,
                 "agreement": "UNINFORMATIVE", "abstain": True,
                 "abstain_reason": None}
        if axcol not in docs.columns:
            entry["abstain_reason"] = "asset axis absent from the reader schema"
            R["assets"][asset] = entry
            continue

        td = today.copy()
        td["dir"] = pd.to_numeric(td[axcol], errors="coerce").fillna(0)
        live = td[td["dir"].abs() > NEGLIGIBLE]
        if LEVER_E4 and len(live):
            keep = [e4_aligned(str(r.source), asset, axcol, hist, t) for r in live.itertuples()]
            dropped = int(len(live) - sum(keep))
            live = live[keep]
            if dropped:
                entry["e4_dropped"] = dropped
        entry["n_docs_today"] = int(len(live))
        if len(live) and live.weight.sum() > 0:
            wsum = live.weight.sum()
            entry["net_view"] = float((live.weight * live["dir"]).sum() / wsum)
            dom = live.loc[live.weight.idxmax()]
            entry["dominant_source"] = str(dom.source)
            entry["dominant_share"] = float(dom.weight / wsum)
            entry["sources_disagree"] = bool(
                len(set(np.sign(live["dir"].values))) > 1)
        elif len(live):
            entry["abstain_reason"] = ("every document vetoed by a near-zero "
                                       "field (§7.2 product rule)")
            R["assets"][asset] = entry
            continue
        else:
            entry["abstain_reason"] = "no document above the direction floor today"
            R["assets"][asset] = entry
            continue

        # ---- 3. blended estimate over the historical content class -----
        cls = float(np.sign(entry["net_view"]))
        hd = hist.copy()
        hd["dir"] = pd.to_numeric(hd[axcol], errors="coerce").fillna(0)
        pool = hd[(hd["dir"].abs() > NEGLIGIBLE) & (np.sign(hd["dir"]) == cls)]
        f = fwd_returns(rets, asset, PRIMARY_H)
        # dtype pinned: an empty selection returns float64 from np.array([]),
        # and indexing with floats raises. Bites only on early dates where no
        # precedent clears position 252, which the 2025/2026 spot-checks missed.
        ppos = np.array(sorted({int(idx.get_loc(s)) for s in pool.session}),
                        dtype=int)
        ppos = ppos[(ppos > 252) & (ppos < ti)].astype(int)
        if ppos.size == 0:
            entry["pool_size"] = 0
            entry["abstain_reason"] = "no precedent before this session"
            R["assets"][asset] = entry
            continue
        ppos = ppos[np.isfinite(f[ppos]) & np.isfinite(Zall[ppos]).all(axis=1)
                    & (labels_all[ppos] >= 0)]
        entry["pool_size"] = int(len(ppos))
        if len(ppos) < 10:
            entry["abstain_reason"] = (f"content-class pool too small "
                                       f"({len(ppos)} precedents)")
            R["assets"][asset] = entry
            continue

        ages = np.abs(ppos[:, None] - ppos[None, :]) / 252.0
        sigma, med_ess, _, _ = select_sigma(Zall[ppos], Zall[ppos], ages,
                                            len(ppos))
        w = kernel_weights(Zall[ppos], Zall[ti],
                           (ti - ppos) / 252.0, sigma, HL_D)
        est = estimate(f[ppos], w, labels_all[ppos], C)
        entry["estimate"] = {k: (None if (isinstance(v, float)
                                          and not np.isfinite(v)) else v)
                             for k, v in est.items()}
        entry["sigma"] = float(sigma)
        entry["abstain"] = bool(est["abstain"])
        if est["abstain"]:
            entry["abstain_reason"] = (f"realised ESS {est['ess']:.1f} below "
                                       f"the registered floor of 8 (§3.5)")

        # ---- E1 lever (prereg_asymmetry_levers §3), off unless LEVER=E1 ------
        if LEVER_E1 and not est["abstain"]:
            # the asset's own typical |move|: every PRIMARY_H-session window that
            # had closed by the close of t (position ti - PRIMARY_H is the last)
            own = np.abs(f[253:ti - PRIMARY_H + 1])
            own_med = float(np.nanmedian(own)) if np.isfinite(own).any() else float("nan")
            pool_med = float(np.nanmedian(np.abs(f[ppos])))
            entry["e1_pool_median_abs"] = pool_med
            entry["e1_asset_median_abs"] = own_med
            if not (np.isfinite(own_med) and pool_med >= own_med):
                entry["abstain"] = True
                entry["estimate"]["abstain"] = True
                entry["abstain_reason"] = (f"E1: precedents' median |move| {pool_med:.3%} "
                                           f"below the asset's own {own_med:.3%}")

        # ---- 4. agreement flag, DISPLAY ONLY ---------------------------
        pt = est["estimate"]
        if pt is not None and np.isfinite(pt) and abs(pt) > 1e-12:
            entry["agreement"] = ("CONCORDANT"
                                  if np.sign(entry["net_view"]) == np.sign(pt)
                                  else "DISCORDANT")
        R["assets"][asset] = entry
    return R


def render_md(R):
    L = [f"# Decision report — {R['date']}", "",
         f"*Generated {R['generated']}. Specification: {R['prereg']}. "
         f"Every field below is required by that section.*", "", "---", "",
         "## 1. Macro state and regime", ""]
    g = R["regime"]
    if g["note"]:
        L.append(f"**Regime posterior unavailable:** {g['note']}.")
    else:
        pc = g["posterior"]
        line = f"**Regime {g['label']}**, posterior confidence **{pc:.1%}**."
        if g["warning"]:
            line += ("\n\n> ⚠️ **WARNING — posterior below 60%.** The regime "
                     "assignment for this session is not confident. Every "
                     "conditional figure below inherits that uncertainty.")
        L.append(line)
        if g["label_mismatch"]:
            L.append(f"\n> **Label mismatch:** the expanding cache assigns "
                     f"regime {g['label']}; a fresh fit to the same history "
                     f"assigns {g['posterior_label']}. Reported, not resolved.")
    L += ["", "| macro PC | value |", "|---|---|"]
    for k, v in R["macro_state"].items():
        L.append(f"| {k} | {v:+.3f} |")

    L += ["", "---", "", "## 2. Documents read this session", ""]
    if not R["documents"]:
        L.append("*No documents entered on this session.*")
    else:
        L += ["| source | published | mag | spec | novelty | conf | directions |",
              "|---|---|---|---|---|---|---|"]
        for d in R["documents"]:
            dirs = ", ".join(f"{a} {v:+.2f}" for a, v in d["direction"].items()
                             if v is not None and abs(v) > 0.05) or "—"
            f = lambda x: f"{x:.2f}" if x is not None else "—"
            L.append(f"| {d['source']}{' *(truncated)*' if d['truncated'] else ''} "
                     f"| {d['published']} | {f(d['magnitude'])} | "
                     f"{f(d['specificity'])} | {f(d['novelty'])} | "
                     f"{f(d['confidence'])} | {dirs} |")

    L += ["", "---", "", "## 3. Per asset", ""]
    for a, e in R["assets"].items():
        L.append(f"### {a}")
        if e["net_view"] is None:
            L += ["", f"**ABSTAIN.** {e['abstain_reason']}.", ""]
            continue
        nv = (f"**Net view {e['net_view']:+.3f}** from {e['n_docs_today']} "
              f"document(s); dominant source **{e['dominant_source']}** "
              f"({e.get('dominant_share', 0):.0%} of weight)")
        if e["sources_disagree"]:
            nv += ". **Sources disagree in sign** — the net figure is a "\
                  "weighted resolution, not a consensus"
        L += ["", nv + ".", ""]
        est = e["estimate"]
        if est is None:
            L += [f"**ABSTAIN.** {e['abstain_reason']}.", ""]
            continue
        L += ["| quantity | value |", "|---|---|",
              f"| matched precedents | {est['n_matched']} |",
              f"| realised ESS | {est['ess']:.1f} |",
              f"| precedent strength `w` | {est['w_shrink']:.3f} |",
              f"| τ² | {est['tau2']:.3e}{' — **zero, registered null path**' if est['tau2_zero'] else ''} |",
              f"| conditional | {est['conditional']:+.4%} |" if est['conditional'] is not None else "| conditional | — |",
              f"| unconditional | {est['unconditional']:+.4%} |" if est['unconditional'] is not None else "| unconditional | — |",
              f"| **blended estimate ({PRIMARY_H}-session)** | "
              f"**{est['estimate']:+.4%}** |" if est['estimate'] is not None else "| blended estimate | — |",
              f"| tier | {est['tier']} |", ""]
        if e["abstain"]:
            L += [f"> **ABSTAIN.** {e['abstain_reason']}. The estimate above is "
                  "printed for transparency and **is not a recommendation**.", ""]
        if e["agreement"] == "DISCORDANT":
            L += [f"> **DISCORDANT.** The documents read {e['net_view']:+.3f} "
                  f"and comparable history reads {est['estimate']:+.4%}. "
                  "**Both numbers are shown and no combined figure is "
                  "produced** (§8 item 4).", ""]
        elif e["agreement"] == "CONCORDANT":
            L += ["> **CONCORDANT** — documents and history point the same way. "
                  "**This changes no number.** A registered test found "
                  "concordant cases performed *worse* than discordant ones "
                  "(+0.193% against +0.406%), so Amendment 3's gate sets the "
                  "interval adjustment to 1.", ""]

    L += ["---", "", "## 4. What this system cannot see", "",
          "*Printed in full in every report, per §8 item 6. These are coverage "
          "gaps, not results.*", ""]
    for h, b in R["cannot_see"]:
        L += [f"**{h}.** {b}", ""]

    L += ["---", "", "## 5. Performance", "",
          "*§8 item 7: no performance number that has not matured.* The live "
          "forward test began 19 August 2026 on a session-calendar basis. "
          "**No figure is reported here** because matured trades remain too few "
          "to carry one, and reporting an unmatured number is the failure this "
          "clause exists to prevent.", ""]
    return "\n".join(L) + "\n"


WRITE_ONCE_FROM = "20260911"   # first session under the write-once rule (2026-09-13)


def _unread_docs(stem):
    """Fetched documents dated `stem` with no entry in the read cache.
    A report frozen while these exist would be frozen incomplete (CURRENT_STATE
    §18.3), so the caller defers rather than writes."""
    from src.doc_read import DOCS, READS, PROMPT_VERSION, PROFILES
    out = []
    for src in PROFILES:
        d = DOCS / src
        if not d.exists():
            continue
        for f in sorted(d.glob(f"{stem}*.txt")):
            if not (READS / f"{src}__{f.stem}__{PROMPT_VERSION}.json").exists():
                out.append(f"{src}/{f.name}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--pending", action="store_true",
                    help="list completed sessions since WRITE_ONCE_FROM with no "
                         "report on disk, one per line as PENDING YYYYMMDD; write "
                         "nothing. daily_run.sh loops --date over these.")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--print", dest="show", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing report. Never passed by the "
                         "nightly job: outputs/reports/ is write-once.")
    a = ap.parse_args()
    if a.latest:
        # WRITE-ONCE, ON THE RIGHT DAY (2026-09-13). A session's report is
        # written on the first run after its closing bell has passed --
        # the forward log's rule for its signal bar -- so the day's
        # documents have been fetched before the report is frozen.
        # Before this date --latest took the panel's last index date, which
        # runs a day AHEAD of the close: each report was written at ~03:00
        # ET on its own date, before any document dated that day could
        # exist, and then silently patched by the nightly regeneration.
        from src.market_calendar import last_completed_session
        s, _ = load_data()
        dates = pd.DatetimeIndex(s.index)
        done = dates[dates <= last_completed_session()]
        if len(done) == 0:
            raise SystemExit("no completed session in the panel")
        a.date = done[-1].strftime("%Y%m%d")
    if a.pending:
        from src.market_calendar import last_completed_session
        s, _ = load_data()
        dates = pd.DatetimeIndex(s.index)
        done = dates[(dates <= last_completed_session())
                     & (dates >= pd.Timestamp(WRITE_ONCE_FROM))]
        for d in done:
            stem = d.strftime("%Y%m%d")
            if not (REPORT_DIR / f"{stem}.json").exists():
                print(f"PENDING {stem}")
        return
    if not a.date:
        raise SystemExit("give --date YYYYMMDD, --latest or --pending")

    # DEFER WHILE UNREAD (2026-09-14, CURRENT_STATE §18.5). Reads are paused
    # for credit; a report written now for a session whose documents were
    # fetched but not read would be frozen without them. Nothing is written
    # until every document dated this session is in the read cache.
    unread = _unread_docs(a.date)
    if unread and not a.force:
        print(f"  {a.date}: {len(unread)} document(s) fetched but UNREAD -- report "
              f"DEFERRED, nothing written (--force writes it anyway)")
        for u in unread[:10]:
            print(f"    {u}")
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    js = REPORT_DIR / f"{a.date}.json"
    if js.exists() and not a.force:
        print(f"  {a.date}: report already on disk -- write-once, not "
              f"rewritten (pass --force to overwrite)\n  -> {js}")
        return

    R = build_report(a.date)
    # Step 2 of the report scoreboard (2026-09-14): the JSON must say which
    # horizon its estimate was computed at. The markdown already did.
    R["estimate_horizon_sessions"] = PRIMARY_H
    for e in R["assets"].values():
        if e.get("estimate"):
            e["estimate"].setdefault("horizon", PRIMARY_H)
    stem = R["date"].replace("-", "")
    md, js = REPORT_DIR / f"{stem}.md", REPORT_DIR / f"{stem}.json"
    if js.exists() and not a.force:
        raise SystemExit(f"  {stem}: exists -- write-once (--force to overwrite)")
    text = render_md(R)               # both from the same dict, §8
    md.write_text(text)
    js.write_text(json.dumps(R, indent=2, default=str))
    if a.show:
        print(text)
    else:
        n_ab = sum(1 for e in R["assets"].values() if e["abstain"])
        print(f"  {R['date']}: {len(R['documents'])} document(s), "
              f"{n_ab} of {len(R['assets'])} assets abstain")
        for k, e in R["assets"].items():
            if e["net_view"] is not None:
                est = e["estimate"]
                v = (f"{est['estimate']:+.4%}" if est
                     and est["estimate"] is not None else "—")
                print(f"    {k}: net {e['net_view']:+.3f}  est {v}  "
                      f"{e['agreement']}  "
                      f"{'ABSTAIN' if e['abstain'] else 'tier '+str(est['tier'])}")
    print(f"  -> {md}\n  -> {js}")


if __name__ == "__main__":
    main()
