"""
Instrument robustness -- does the display panel change any verdict? (TRACK §3.10)

Registered: docs/prereg_instrument_robustness.md (2026-09-29). Criteria C1-C4 fixed there.

Steps
  1. build  : alternative daily log returns for the five model assets from Yahoo
              (^GSPC, GC=F, CL=F, DX-Y.NYB, and a 10-year price proxy from ^TNX with D=8.0),
              aligned to the panel's session index, written as
              processed/asset_returns_altinstr.parquet with the ORIGINAL column names.
  2. run    : swap the alternative panel in place of processed/asset_returns.parquet under a
              lock, run the report backfill into outputs/reports_backfill/<baseline>_altinstr/,
              restore the original panel (verified by hash) in a finally: block.
  3. compare: the two scoreboards' primary cells and the row-level hit/miss agreement,
              against C1-C4; write docs/instrument_robustness.md with the verdict and, if
              DIFFERENT, the attribution by asset and by mechanism.

Never run within an hour of the 15:00 nightly job: the swap is on disk.

Usage
  python -m src.instrument_robustness build
  python -m src.instrument_robustness run --baseline 48a6c4e879a1_n2617
  python -m src.instrument_robustness compare --baseline 48a6c4e879a1_n2617
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PANEL = Path("processed/asset_returns.parquet")
ALT = Path("processed/asset_returns_altinstr.parquet")
BACKUP = Path("processed/asset_returns.ORIGINAL_backup.parquet")
LOCK = Path("processed/.instrument_test.lock")
OUT_MD = Path("docs/instrument_robustness.md")
ALT_TICKERS = {"SPY": "^GSPC", "GLD": "GC=F", "USO": "CL=F", "UUP": "DX-Y.NYB", "TLT": "^TNX"}
DURATION = 8.0                 # registered, fixed; not fitted
C2_MIN, C3_MAX, C4_MAX = 0.90, 2.0, 0.15


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------- build
def _yahoo_close(tk: str, start: str) -> pd.Series:
    import yfinance as yf
    d = yf.Ticker(tk).history(start=start, interval="1d", auto_adjust=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    s = d["Close"].dropna()
    s.index = pd.to_datetime(s.index).tz_localize(None) if getattr(s.index, "tz", None) is not None else pd.to_datetime(s.index)
    return s


def cmd_build(a):
    base = pd.read_parquet(PANEL); base.index = pd.to_datetime(base.index)
    start = (base.index[0] - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    alt = base.copy()
    report = {}
    for model, tk in ALT_TICKERS.items():
        s = _yahoo_close(tk, start)
        if model == "TLT":
            y = s.reindex(base.index).ffill()                      # yield in percent
            r = -DURATION * (y - y.shift(1)) / 100 + (y.shift(1) / 100) / 252
        else:
            px = s.reindex(base.index)                            # sessions only; futures' off-session days dropped
            r = np.log(px / px.shift(1))
        # keep the model column's own NaN pattern where the original had no price (pre-inception)
        r = r.where(base[model].notna() | r.notna())
        alt[model] = r
        both = pd.concat([base[model], r], axis=1).dropna()
        corr = float(both.iloc[:, 0].corr(both.iloc[:, 1])) if len(both) > 100 else float("nan")
        report[model] = dict(alt=tk, corr_daily=round(corr, 4), n=int(len(both)))
        print(f"  {model:4} <- {tk:10} daily-return corr {corr:.4f} on {len(both):,} sessions")
    alt.to_parquet(ALT)
    Path("processed/asset_returns_altinstr.json").write_text(json.dumps(dict(built=str(datetime.now()), duration=DURATION,
                                                                            map=report), indent=2))
    print(f"  -> {ALT}")


# ---------------------------------------------------------------- run
def cmd_run(a):
    assert ALT.exists(), "run `build` first"
    if LOCK.exists():
        raise SystemExit(f"{LOCK} exists -- a previous run did not restore the panel. Check {BACKUP} by hand.")
    tag = f"{a.baseline}_altinstr"
    LOCK.write_text(str(datetime.now()))
    shutil.copy2(PANEL, BACKUP); orig_hash = _sha(PANEL)
    try:
        shutil.copy2(ALT, PANEL)
        print(f"  panel swapped (original {orig_hash} backed up). Running backfill -> {tag}")
        cmd = [sys.executable, "-m", "src.report_backfill", "--hash", tag, "--n-perm", str(a.n_perm)]
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print("  backfill returned non-zero; see its output above")
    finally:
        shutil.copy2(BACKUP, PANEL)
        ok = _sha(PANEL) == orig_hash
        print(f"  panel restored: {'verified' if ok else 'HASH MISMATCH -- inspect ' + str(BACKUP)}")
        if ok:
            LOCK.unlink(missing_ok=True)


# ---------------------------------------------------------------- compare
def _cell(tag: str):
    j = json.loads(Path(f"processed/report_scoreboard_backfill_{tag}.json").read_text())
    return j["verdict"], j["cells"]["h3_primary"]


def _rows(tag: str) -> pd.DataFrame:
    df = pd.read_csv(f"processed/report_backfill_{tag}.csv", parse_dates=["date"])
    df = df[(df["h"] == 3) & (df["kind"] == "call") & (df["status"] == "matured")].copy()
    df["hit"] = (np.sign(df["call"]) == np.sign(df["ret_primary"])) & (df["ret_primary"] != 0)
    return df.set_index(["date", "asset"])


def cmd_compare(a):
    base_tag, alt_tag = a.baseline, f"{a.baseline}_altinstr"
    vb, cb = _cell(base_tag); va, ca = _cell(alt_tag)
    rb, ra = _rows(base_tag), _rows(alt_tag)
    common = rb.index.intersection(ra.index)
    agree = (rb.loc[common, "hit"].to_numpy() == ra.loc[common, "hit"].to_numpy())
    c2 = float(agree.mean()) if len(common) else float("nan")
    hb, ha = cb["nonoverlap"].get("hit"), ca["nonoverlap"].get("hit")
    ab, aa = cb["nonoverlap"].get("asym"), ca["nonoverlap"].get("asym")
    c1 = (vb == va); c3 = (hb is not None and ha is not None and abs(hb - ha) * 100 <= C3_MAX)
    c4 = (ab is not None and aa is not None and np.isfinite(ab) and np.isfinite(aa) and abs(ab - aa) <= C4_MAX)
    verdict = "CONSISTENT" if (c1 and c2 >= C2_MIN and c3 and c4) else "DIFFERENT"

    L = ["# Instrument robustness — result", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_instrument_robustness.md`. "
         f"Baseline `{base_tag}` vs alternative `{alt_tag}` (^GSPC, GC=F, CL=F, DX-Y.NYB, ^TNX price proxy with D={DURATION}).*", "",
         "| criterion | baseline | alternative | threshold | met |", "|---|---|---|---|---|",
         f"| C1 primary verdict | {vb} | {va} | identical | {'yes' if c1 else 'NO'} |",
         f"| C2 row-level hit/miss agreement | — | {c2:.1%} on {len(common):,} shared rows | ≥ {C2_MIN:.0%} | {'yes' if c2 >= C2_MIN else 'NO'} |",
         f"| C3 non-overlap hit-rate | {hb:.1%} | {ha:.1%} | within {C3_MAX} pts | {'yes' if c3 else 'NO'} |" if hb is not None and ha is not None else "| C3 | too few | too few | — | — |",
         f"| C4 asymmetry | {ab:.3f} | {aa:.3f} | within {C4_MAX} | {'yes' if c4 else 'NO'} |" if ab is not None and aa is not None else "| C4 | — | — | — | — |",
         "", f"## Verdict: **{verdict}**", ""]
    if verdict == "CONSISTENT":
        L.append("The app may state: *Modelled on SPY, TLT, GLD, UUP and USO; shown as the S&P 500, the 10-year yield, gold "
                 "futures, DXY and WTI. Verdicts are unchanged on the alternative panel.*")
    # attribution, always reported
    L += ["", "## Attribution (reported whichever way the verdict fell)", "", "| asset | shared rows | agreement | flips |", "|---|---|---|---|"]
    flips = pd.Series(~agree, index=common)
    for asset in ["SPY", "TLT", "GLD", "UUP", "USO"]:
        m = [i for i in common if i[1] == asset]
        if not m:
            continue
        L.append(f"| {asset} | {len(m)} | {1 - flips.loc[m].mean():.1%} | {int(flips.loc[m].sum())} |")
    # FOMC-day concentration
    fomc = Path("processed/fomc_decisions.csv")
    if fomc.exists():
        fd = set(pd.to_datetime(pd.read_csv(fomc).iloc[:, 0], errors="coerce").dropna())
        on_f = flips[[i[0] in fd for i in common]]
        off_f = flips[[i[0] not in fd for i in common]]
        L += ["", f"Flip rate on FOMC statement days: **{on_f.mean():.1%}** (n={len(on_f)}) vs other days **{off_f.mean():.1%}** "
                  f"(n={len(off_f)}). A large gap points at settlement timing (GLD 4 pm vs GC=F 1:30 pm ET against a 2 pm statement)."]
    OUT_MD.write_text("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n  -> {OUT_MD}")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    r = sub.add_parser("run"); r.add_argument("--baseline", required=True); r.add_argument("--n-perm", type=int, default=10000); r.set_defaults(fn=cmd_run)
    c = sub.add_parser("compare"); c.add_argument("--baseline", required=True); c.set_defaults(fn=cmd_compare)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
