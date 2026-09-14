"""
Report backfill -- as-of decision reports over the historical corpus, scored by
the same scorer as the forward ledger.

Registered: docs/prereg_report_scoreboard.md §7.2 and the step-7 §11 row (2026-09-14).

What it does
  1. corpus_hash  = sha256 over the sorted read-cache filenames and sizes, so two
                    backfills built on different corpora are never confused.
  2. generate     one report per document-bearing session with a labelled regime,
                    via step6_report.build_report -- the SAME function, prompt version
                    and model as the live reports -- written to
                    outputs/reports_backfill/<corpus_hash>/YYYYMMDD.{json,md}.
                    Resumable: a date whose JSON exists is skipped.
  3. score        rows -> realised returns -> src.report_scoreboard.score, written to
                    processed/report_backfill_<hash>.csv (rebuilt whole, not appended),
                    docs/report_scoreboard_backfill_<hash>.md and .json.

What it never does
  - write under outputs/reports/ (asserted), touch processed/report_ledger.csv, or
    call any API. $0.

Why the three cached wrappers
  build_report() calls load_data(), regime_labels_expanding() and _z_expanding()
  afresh on every call -- about a minute each for the expanding GMM refits. Over
  ~1,500 dates that is a day of compute; cached once it is minutes. The wrappers
  replace the names in step6_report's namespace for THIS process only. The inputs
  are identical on every call within a run, so the cache changes nothing about
  what build_report computes.

Usage
  python -m src.report_backfill --limit 20            # pilot: first 20 candidate dates, timed
  python -m src.report_backfill                       # full generate + score
  python -m src.report_backfill --score-only          # re-score an existing hash folder
  python -m src.report_backfill --since 20150101 --until 20251231
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # repo root, so step6_report imports
import step6_report as s6                                           # noqa: E402
from src import report_scoreboard as rs                            # noqa: E402

READS_DIR = Path("data_provenance/doc_reads")
BACKFILL_ROOT = Path("outputs/reports_backfill")
FORWARD_DIR = Path("outputs/reports").resolve()


# ---- 1. corpus hash ---------------------------------------------------------
def corpus_hash(reads_dir: Path = READS_DIR) -> str:
    h = hashlib.sha256()
    files = sorted(reads_dir.glob("*.json"))
    for p in files:
        h.update(p.name.encode()); h.update(str(p.stat().st_size).encode()); h.update(b"\n")
    return f"{h.hexdigest()[:12]}_n{len(files)}"


# ---- 2. cache the three expensive calls, in step6_report's namespace --------
_CACHE: dict = {}


def _install_caches():
    orig_load, orig_lab, orig_z = s6.load_data, s6.regime_labels_expanding, s6._z_expanding

    def load_data_cached():
        if "data" not in _CACHE:
            _CACHE["data"] = orig_load()
        return _CACHE["data"]

    def labels_cached(scores, cfg):
        if "labels" not in _CACHE:
            t0 = time.time(); _CACHE["labels"] = orig_lab(scores, cfg)
            print(f"  expanding regime labels computed once ({time.time()-t0:.0f}s), cached for this run")
        return _CACHE["labels"]

    def z_cached(arr):
        key = ("z", getattr(arr, "shape", None))
        if key not in _CACHE:
            _CACHE[key] = orig_z(arr)
        return _CACHE[key]

    s6.load_data, s6.regime_labels_expanding, s6._z_expanding = load_data_cached, labels_cached, z_cached


# ---- 3. candidate dates -----------------------------------------------------
def candidate_dates(since: str | None, until: str | None) -> list[str]:
    """Document-bearing sessions with a labelled regime, as YYYYMMDD stems."""
    from src.market_calendar import last_completed_session
    scores, _ = s6.load_data()
    idx = pd.DatetimeIndex(scores.index)
    cfg = s6.load_config() if hasattr(s6, "load_config") else None
    labels = s6.regime_labels_expanding(scores, cfg)
    lab = pd.Series(np.asarray(labels), index=idx)
    try:
        from generate_reports import document_sessions
        doc_sess = set(pd.to_datetime(document_sessions(idx).session.unique()))
    except Exception as e:
        raise SystemExit(f"could not list document sessions via generate_reports.document_sessions ({type(e).__name__}: {e}); "
                         f"pass --all-sessions to backfill every labelled session instead")
    end = last_completed_session()
    dates = [d for d in idx if d in doc_sess and lab.loc[d] >= 0 and d <= end]
    if since:
        dates = [d for d in dates if d >= pd.Timestamp(since)]
    if until:
        dates = [d for d in dates if d <= pd.Timestamp(until)]
    return [d.strftime("%Y%m%d") for d in dates]


# ---- 4. generate ------------------------------------------------------------
def generate(out_dir: Path, stems: list[str], limit: int | None) -> int:
    assert out_dir.resolve() != FORWARD_DIR and FORWARD_DIR not in out_dir.resolve().parents, \
        "backfill must never write under outputs/reports/"
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = [s for s in stems if not (out_dir / f"{s}.json").exists()]
    if limit:
        todo = todo[:limit]
    print(f"  {len(stems)} candidate dates, {len(stems)-len(todo)} already on disk, {len(todo)} to generate")
    t0 = time.time(); n = 0
    for k, stem in enumerate(todo, 1):
        try:
            R = s6.build_report(stem)
        except SystemExit as e:
            print(f"    {stem}: build_report declined ({e}); skipped"); continue
        R["backfill"] = True
        R["estimate_horizon_sessions"] = s6.PRIMARY_H
        for e in R["assets"].values():
            if e.get("estimate"):
                e["estimate"].setdefault("horizon", s6.PRIMARY_H)
        (out_dir / f"{stem}.json").write_text(json.dumps(R, indent=2, default=str))
        (out_dir / f"{stem}.md").write_text(s6.render_md(R))
        n += 1
        if k % 25 == 0 or k == len(todo):
            el = time.time() - t0
            print(f"    {k}/{len(todo)}  {el:.0f}s elapsed, {el/k:.1f}s per report, "
                  f"~{el/k*(len(todo)-k)/60:.0f} min remaining", flush=True)
    return n


# ---- 5. score ---------------------------------------------------------------
def score_backfill(out_dir: Path, tag: str, n_perm: int) -> dict:
    reports = rs.load_reports(out_dir, since="19000101")
    rows = rs.rows_from_reports(reports)
    if rows.empty:
        raise SystemExit("no backfill reports to score")
    assets = sorted(rows["asset"].unique())
    closes, opens, closes_raw, sessions = rs.load_prices_real(assets)
    led = rs.realise(rows, closes, None, sessions)
    if opens is not None:
        tr = rs.realise(rows, closes_raw, opens, sessions)
        led["ret_tradeable"] = tr["ret_tradeable"].to_numpy()
    led["logged_at"] = "backfill"
    led["matured_at"] = np.where(led["status"] == "matured", "backfill", None)
    ledger_path = Path(f"processed/report_backfill_{tag}.csv")
    ledger_path.parent.mkdir(parents=True, exist_ok=True); led.to_csv(ledger_path, index=False)
    res = rs.score(led, do_null=True, n_perm=n_perm)
    res["backfill_tag"] = tag; res["reports_dir"] = str(out_dir); res["n_reports"] = len(reports)
    Path(f"processed/report_scoreboard_backfill_{tag}.json").write_text(json.dumps(res, indent=2, default=str))
    md_path = Path(f"docs/report_scoreboard_backfill_{tag}.md")
    md_path.write_text(rs.render_md(res, tag=f"backfill {tag}"))
    print(f"  ledger {len(led)} rows -> {ledger_path}")
    print(f"  verdict: {res['verdict']}")
    print(f"  -> {md_path}")
    return res


# ---- 6. entry ---------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since"); ap.add_argument("--until")
    ap.add_argument("--limit", type=int, help="pilot: generate at most N reports, then score what exists")
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--n-perm", type=int, default=rs.N_PERM)
    ap.add_argument("--hash", help="use an existing backfill folder by hash instead of recomputing")
    a = ap.parse_args()

    print("=" * 72); print("REPORT BACKFILL -- as-of reports over the corpus (prereg_report_scoreboard §7.2)"); print("=" * 72)
    tag = a.hash or corpus_hash()
    out_dir = BACKFILL_ROOT / tag
    print(f"  corpus hash {tag}\n  folder      {out_dir}")

    if not a.score_only:
        _install_caches()
        stems = candidate_dates(a.since, a.until)
        n = generate(out_dir, stems, a.limit)
        print(f"  generated {n} report(s)")
    score_backfill(out_dir, tag, a.n_perm)


if __name__ == "__main__":
    main()
