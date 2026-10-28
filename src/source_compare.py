"""The source-expansion rule (prereg_report_scoreboard section 8) applied to a new corpus against the baseline backfill,
plus the session-coverage count the political backfill is judged on (docs/prereg_political_backfill.md, C1).

  python -m src.source_compare coverage --tag before|after
      sessions since 2011 carrying at least one read document, from the read CSVs step 6 uses (the same mapping as
      generate_reports.document_sessions); saved to processed/source_coverage_<tag>.json
  python -m src.source_compare newdocs --source earnings_8k --on 2026-10-28
      the documents of one source whose v1 read was CREATED on that day (cache-file mtime), mapped to their sessions;
      written to processed/newdoc_dates_<source>_<on>.txt -- the exclusion list for a comparison that must judge one
      expansion while another happened in the same corpus hash
  python -m src.source_compare compare --baseline processed/report_backfill_<old>.csv --new processed/report_backfill_<new>.csv
                                       [--exclude-dates FILE] [--gate PASS|FAIL|NOT_RUN] [--record]
      document-day coverage of calls on each side; on the days BOTH sides issued a call (minus the excluded days), the
      pooled hit-rate of each at the primary horizon, close-to-close; the difference new - old with a block bootstrap over
      dates (block = h, 2,000 draws); the section-8 clause: point estimate not below -2 points AND the 95% lower bound
      above -5. The excluded days are reported separately as an unregistered observation. The verdict is PASS only when
      the hit clause, the coverage clause (C1) AND the gate (C2, passed in with --gate from gate_check's output) are met.
      --record writes the row into docs/prereg_political_backfill.md (replace-or-add by the new corpus tag).

v2 (28 Oct, after the first run): --exclude-dates, --gate and the newdocs subcommand; the asset mix of the new calls; a
verdict is never written without the gate.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
READS_DIR = Path("data_provenance/doc_reads")
PROMPT_VERSION = "v1-2026-08-23"
H = 2                                   # primary horizon since the 9 Oct amendment
START = pd.Timestamp("2011-01-03")       # the corpus starts with the January 2011 statement


def _sessions() -> pd.DatetimeIndex | None:
    try:
        r = pd.read_parquet(PROC / "asset_returns.parquet")
        return pd.DatetimeIndex(pd.to_datetime(r.index)).sort_values()
    except Exception:
        return None


def coverage(tag: str) -> dict:
    import sys
    sys.path.insert(0, ".")
    from generate_reports import document_sessions, READS
    idx = _sessions()
    if idx is None:
        raise SystemExit("processed/asset_returns.parquet not readable")
    idx = idx[(idx >= START)]
    ds = document_sessions(idx)
    ds = ds[ds["session"] >= START]
    sess = set(ds["session"].unique())
    per = ds.groupby("source")["session"].nunique().to_dict()
    docs = ds.groupby("source").size().to_dict()
    out = dict(tag=tag, run=datetime.now().strftime("%Y-%m-%d %H:%M"), sessions=int(len(idx)), sessions_with_docs=int(len(sess)),
               coverage=float(len(sess) / len(idx)), sessions_by_source=per, documents_by_source=docs, csvs=[f for f in READS if (PROC / f).exists()])
    (PROC / f"source_coverage_{tag}.json").write_text(json.dumps(out, indent=1))
    print(f"coverage ({tag}): {len(sess):,} of {len(idx):,} sessions since {START.date()} carry a read document = {out['coverage']:.1%}; "
          + ", ".join(f"{k} {v}" for k, v in sorted(per.items())))
    return out


def newdocs(source: str, on: str) -> list[str]:
    """Stems of <source> whose v1 cache file was created on <on> (local date), and their sessions."""
    day = pd.Timestamp(on).date()
    stems = []
    for f in sorted(READS_DIR.glob(f"{source}__*__{PROMPT_VERSION}.json")):
        if datetime.fromtimestamp(f.stat().st_mtime).date() == day:
            stems.append(f.name.split("__")[1])
    dates = pd.to_datetime([s[:8] for s in stems], format="%Y%m%d", errors="coerce").dropna()
    idx = _sessions()
    if idx is not None and len(dates):
        pos = idx.searchsorted(pd.DatetimeIndex(dates), side="left"); ok = pos < len(idx)
        sessions = sorted({idx[p].strftime("%Y-%m-%d") for p in pos[ok]})
    else:
        sessions = sorted({d.strftime("%Y-%m-%d") for d in dates})
    out = PROC / f"newdoc_dates_{source}_{on}.txt"
    out.write_text("\n".join(sessions) + ("\n" if sessions else ""))
    print(f"{source}: {len(stems)} read(s) created on {on} -> {len(sessions)} session(s); first {sessions[:3]} ... last {sessions[-3:]}" if sessions
          else f"{source}: no reads created on {on}")
    print(f"  -> {out}")
    return sessions


def _calls(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path); df["date"] = pd.to_datetime(df["date"])
    df = df[df["h"] == H].copy()
    df["hit"] = (np.sign(df["call"]) == np.sign(df["ret_primary"])) & (df["ret_primary"] != 0)
    return df


def _block_boot(dates: np.ndarray, d_new: dict, d_old: dict, block: int, draws: int, seed: int = 0) -> np.ndarray:
    """Resample blocks of consecutive shared dates; each draw re-pools both sides' calls on the drawn dates."""
    rng = np.random.default_rng(seed); n = len(dates); starts = np.arange(0, n); out = np.empty(draws)
    for k in range(draws):
        picked = []
        while len(picked) < n:
            s = rng.choice(starts); picked.extend(dates[s:s + block])
        picked = picked[:n]
        hn = np.concatenate([d_new[d] for d in picked]); ho = np.concatenate([d_old[d] for d in picked])
        out[k] = hn.mean() - ho.mean()
    return out


def _hit(x: pd.Series) -> float:
    return float(x.mean()) if len(x) else float("nan")


def compare(baseline: Path, new: Path, record: bool, draws: int = 2000, exclude_file: Path | None = None, gate: str | None = None) -> dict:
    old, nw = _calls(baseline), _calls(new)
    excl = set()
    if exclude_file:
        excl = {pd.Timestamp(x.strip()) for x in Path(exclude_file).read_text().split() if x.strip()}
    o_days, n_days = set(old["date"].unique()), set(nw["date"].unique())
    oc, nc = old[old["kind"] == "call"], nw[nw["kind"] == "call"]
    o_call_days, n_call_days = set(oc["date"].unique()), set(nc["date"].unique())
    cov_o, cov_n = len(o_call_days) / max(len(o_days), 1), len(n_call_days) / max(len(n_days), 1)
    shared_all = sorted(o_call_days & n_call_days)
    shared = [d for d in shared_all if d not in excl]
    d_old = {d: oc.loc[oc["date"] == d, "hit"].to_numpy(float) for d in shared}
    d_new = {d: nc.loc[nc["date"] == d, "hit"].to_numpy(float) for d in shared}
    ho = np.concatenate([d_old[d] for d in shared]) if shared else np.array([]); hn = np.concatenate([d_new[d] for d in shared]) if shared else np.array([])
    delta = float(hn.mean() - ho.mean()) * 100 if len(shared) else float("nan")
    boot = _block_boot(np.array(shared, dtype=object), d_new, d_old, H, draws) * 100 if len(shared) >= 10 else np.array([np.nan])
    lb, ub = (float(np.nanpercentile(boot, 2.5)), float(np.nanpercentile(boot, 97.5))) if len(shared) >= 10 else (float("nan"), float("nan"))
    both = oc.merge(nc, on=["date", "asset"], suffixes=("_old", "_new"))
    both_kept = both[~both["date"].isin(excl)]
    same_sign = float((np.sign(both_kept["call_old"]) == np.sign(both_kept["call_new"])).mean()) if len(both_kept) else float("nan")
    # the calls the new corpus added (asset-days with a call now and none before), outside the excluded days
    added = nc.merge(oc[["date", "asset"]], on=["date", "asset"], how="left", indicator=True)
    added = added[(added["_merge"] == "left_only") & (~added["date"].isin(excl))]
    add_mix = added["asset"].value_counts().to_dict(); add_hit = _hit(added["hit"])
    # the excluded days: an unregistered observation, reported, not judged
    ex = {}
    if excl:
        oe, ne = oc[oc["date"].isin(excl)], nc[nc["date"].isin(excl)]
        be = both[both["date"].isin(excl)]
        ex = dict(days=len(excl & n_days), calls_old=int(len(oe)), calls_new=int(len(ne)), hit_old=_hit(oe["hit"]), hit_new=_hit(ne["hit"]),
                  same_sign=(float((np.sign(be["call_old"]) == np.sign(be["call_new"])).mean()) if len(be) else float("nan")), shared_asset_days=int(len(be)),
                  added_calls=int(len(ne.merge(oe[["date", "asset"]], on=["date", "asset"], how="left", indicator=True).query("_merge == 'left_only'"))))
    hit_met = bool(np.isfinite(delta) and delta >= -2.0 and np.isfinite(lb) and lb > -5.0)
    cov = {}
    for t in ("before", "after"):
        p = PROC / f"source_coverage_{t}.json"
        if p.exists():
            cov[t] = json.loads(p.read_text())
    cov_met = bool(cov.get("after", {}).get("coverage", 0) >= 0.50) if "after" in cov else None
    g = (gate or "NOT_RUN").upper()
    if g == "PASS" and hit_met and cov_met:
        verdict = "PASS — C1 coverage, C2 gate and C3 hit-rate all met"
    elif g != "PASS":
        verdict = ("NO VERDICT — the gate (C2) was not run or not passed in; the hit clause is " + ("met" if hit_met else "not met")) if g == "NOT_RUN" \
            else "FAIL — C2 gate FAIL: the new documents are reported separately and never pooled (prereg section 3)"
    elif not hit_met:
        verdict = "FAIL — C3 hit-rate outside tolerance"
    else:
        verdict = "FAIL — C1 coverage below 50%" if cov_met is False else "NO VERDICT — coverage not measured"
    tag_new = new.stem.replace("report_backfill_", ""); tag_old = baseline.stem.replace("report_backfill_", "")
    res = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), baseline=tag_old, new=tag_new, h=H, gate=g,
               excluded_days=len(excl), exclude_file=str(exclude_file) if exclude_file else None,
               doc_days=dict(old=len(o_days), new=len(n_days)), call_days=dict(old=len(o_call_days), new=len(n_call_days)),
               calls=dict(old=int(len(oc)), new=int(len(nc))), call_day_coverage=dict(old=cov_o, new=cov_n),
               hit_all_calls=dict(old=_hit(oc["hit"]), new=_hit(nc["hit"])),
               shared_days_all=len(shared_all), shared_days=len(shared), hit_shared=dict(old=_hit(pd.Series(ho)), new=_hit(pd.Series(hn))),
               delta_pts=delta, ci95=[lb, ub], same_sign_on_shared_asset_days=same_sign, shared_asset_days=int(len(both_kept)),
               added_calls=int(len(added)), added_calls_by_asset=add_mix, added_calls_hit=add_hit, excluded=ex,
               session_coverage=cov, hit_clause_met=hit_met, coverage_clause_met=cov_met, verdict=verdict)
    (PROC / f"source_compare_{tag_new}.json").write_text(json.dumps(res, indent=1, default=float))
    md = [f"# Source expansion — `{tag_new}` against baseline `{tag_old}` (section 8 rule) — {res['run']}", "",
          f"Primary horizon {H}, close-to-close. Calls: {len(oc):,} → {len(nc):,}; document days {len(o_days):,} → {len(n_days):,}; "
          f"days with at least one call {len(o_call_days):,} ({cov_o:.0%}) → {len(n_call_days):,} ({cov_n:.0%}).", "",
          f"Hit-rate on all own calls: {res['hit_all_calls']['old']:.1%} → {res['hit_all_calls']['new']:.1%} (naive, overlapping; the registered cell is the backfill's own scoreboard).", ""]
    if excl:
        md += [f"**Excluded from the registered comparison:** {len(excl)} session(s) listed in `{exclude_file}` — days carrying a document outside the registered "
               f"expansion. Of the {len(shared_all):,} days both sides called, {len(shared_all) - len(shared)} fall on those days and are set aside.", ""]
    md += [f"On the {len(shared):,} days both sides called{' (excluded days removed)' if excl else ''}: old {res['hit_shared']['old']:.1%}, new {res['hit_shared']['new']:.1%}, "
           f"difference {delta:+.1f} points, 95% block-bootstrap interval [{lb:+.1f}, {ub:+.1f}] ({draws:,} draws, block {H}). "
           f"Same sign on {same_sign:.0%} of the {len(both_kept):,} shared asset-day calls.", "",
           f"Calls the new corpus added on days the baseline had none: {len(added):,}, hit-rate {add_hit:.1%}; by asset: "
           + (", ".join(f"{k} {v}" for k, v in sorted(add_mix.items(), key=lambda kv: -kv[1])) or "none") + ".", ""]
    if ex:
        md += [f"**Excluded days, reported not judged (unregistered observation):** {ex['days']} day(s); calls {ex['calls_old']:,} → {ex['calls_new']:,} "
               f"({ex['added_calls']} added); hit-rate old {ex['hit_old']:.1%}, new {ex['hit_new']:.1%}; same sign on {ex['same_sign']:.0%} of {ex['shared_asset_days']} shared asset-days.", ""]
    if cov:
        md.append("Session coverage (sessions since 2011 carrying a read document): " + "; ".join(f"{t} {c['coverage']:.1%} ({c['sessions_with_docs']:,} of {c['sessions']:,})" for t, c in cov.items()) + ".")
        md.append("")
    md.append(f"Gate (C2) as passed in: **{g}**.  Hit clause (point ≥ −2, lower bound > −5): {'met' if hit_met else 'not met'}.  Coverage clause (≥ 50%): "
              f"{'met' if cov_met else 'not met' if cov_met is False else 'not measured'}.")
    md.append("")
    md.append(f"**Verdict: {verdict}.**")
    (DOCS / f"source_compare_{tag_new}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    if record:
        _record(res)
    return res


def _record(res: dict):
    p = DOCS / "prereg_political_backfill.md"
    if not p.exists():
        print("  prereg_political_backfill.md not found; nothing recorded"); return
    s = p.read_text(); stamp = res["run"][:10]
    cov = res.get("session_coverage", {})
    cov_txt = "; ".join(f"{t} {c['coverage']:.1%}" for t, c in cov.items()) or "not measured"
    ex = res.get("excluded") or {}
    ex_txt = (f"; {res['excluded_days']} day(s) carrying documents outside the registered expansion set aside (on them: calls {ex.get('calls_old', 0):,} → {ex.get('calls_new', 0):,}, "
              f"hit-rate {ex.get('hit_old', float('nan')):.1%} → {ex.get('hit_new', float('nan')):.1%}, unregistered observation)") if ex else ""
    mix = ", ".join(f"{k} {v}" for k, v in sorted(res["added_calls_by_asset"].items(), key=lambda kv: -kv[1])[:4]) or "none"
    row = (f"| {stamp} | source expansion `{res['new']}` vs `{res['baseline']}` | gate (C2) {res['gate']}; calls {res['calls']['old']:,} → {res['calls']['new']:,}; "
           f"call-day coverage {res['call_day_coverage']['old']:.0%} → {res['call_day_coverage']['new']:.0%}; session coverage {cov_txt}; "
           f"hit-rate on the {res['shared_days']:,} shared days {res['hit_shared']['old']:.1%} → {res['hit_shared']['new']:.1%} "
           f"({res['delta_pts']:+.1f} pts, 95% [{res['ci95'][0]:+.1f}, {res['ci95'][1]:+.1f}]); same sign on {res['same_sign_on_shared_asset_days']:.0%} of shared asset-days; "
           f"{res['added_calls']:,} calls added (hit {res['added_calls_hit']:.1%}; {mix}){ex_txt} "
           f"→ **{res['verdict']}**. docs/source_compare_{res['new']}.md | #83: judged by the founder against the prior's clauses |")
    pat = r"^\| \d{4}-\d{2}-\d{2} \| source expansion `" + re.escape(res["new"]) + r"`.*$"
    m = re.search(pat, s, flags=re.M)
    s = (s[:m.start()] + row + s[m.end():]) if m else s.rstrip("\n") + "\n" + row + "\n"
    p.write_text(s); print("  prereg_political_backfill: results row " + ("replaced" if m else "added"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["coverage", "newdocs", "compare"])
    ap.add_argument("--tag", default="now")
    ap.add_argument("--source", default="earnings_8k"); ap.add_argument("--on", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--baseline"); ap.add_argument("--new")
    ap.add_argument("--exclude-dates"); ap.add_argument("--gate", choices=["PASS", "FAIL", "NOT_RUN", "pass", "fail", "not_run"])
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--draws", type=int, default=2000)
    a = ap.parse_args()
    if a.cmd == "coverage":
        coverage(a.tag)
    elif a.cmd == "newdocs":
        newdocs(a.source, a.on)
    else:
        if not (a.baseline and a.new):
            raise SystemExit("compare needs --baseline and --new")
        compare(Path(a.baseline), Path(a.new), a.record, a.draws, Path(a.exclude_dates) if a.exclude_dates else None, a.gate)
