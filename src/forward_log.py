"""
forward_log.py -- ONE self-contained daily command for the pre-registered
forward test. Refreshes data, computes every frozen model's picks, appends to
the Markdown scoreboard, back-fills matured results, and FAILS LOUD if anything
needs a human.

Architecture (see docs/architecture_decisions.md):
  * ONE shared daily clock. Signal = last completed US close.
  * Entry = NEXT US session (never the signal bar -- that would be look-ahead).
  * Exit  = H trading days after entry.
  * If no new US close since the last logged row, SKIP (no duplicate rows).
  * Results are 'pending' until the horizon matures, then back-filled.
  * Summary reports BOTH the naive all-overlapping-rows number AND the honest
    NON-OVERLAPPING number (every H-th entry), because overlapping daily rows
    share most of their days and would inflate apparent significance.

Run daily (any time after ~05:00 SGT, so the prior US close has landed):

    python -m src.forward_log                 # refresh data + log + backfill
    python -m src.forward_log --no-refresh    # skip the data pull
    python -m src.forward_log --dry-run       # show what would be logged
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.data_io import load_config, PROCESSED_DIR
from src.analog_core import DEFAULT, load_data, frozen_labels, feature_matrix, _kw, _forward, _expected_fwd

REPO = PROCESSED_DIR.parent
SCOREBOARD = REPO / "docs" / "forward_scoreboard.md"
LEDGER = REPO / "processed" / "forward_ledger.csv"   # machine-readable state
MODELS_YAML = REPO / "config" / "models.yaml"


def die(msg):
    print("\n" + "!" * 70)
    print("MANUAL INTERVENTION NEEDED:")
    print("  " + msg)
    print("!" * 70)
    sys.exit(1)


def refresh_data():
    """Pull fresh prices/macro and rebuild the panels + PCA scores."""
    for mod in ["src.download_data", "src.build_panel", "src.pca_macro"]:
        print(f"  refreshing: {mod} ...")
        r = subprocess.run([sys.executable, "-m", mod], capture_output=True, text=True)
        if r.returncode != 0:
            tail = (r.stderr or r.stdout)[-1500:]
            die(f"{mod} failed.\n{tail}")
    print("  data refresh OK")


def load_models():
    if not MODELS_YAML.exists():
        die(f"missing {MODELS_YAML} -- the frozen model registry.")
    spec_file = yaml.safe_load(MODELS_YAML.read_text())["models"]
    out = {}
    for name, s in spec_file.items():
        d = dict(DEFAULT); d.update({k: v for k, v in s.items() if k != "note"})
        out[name] = d
    return out


def picks_for(scores, rets, spec, cfg, pos):
    """Model's ranked picks using data up to and including index `pos`."""
    labels = frozen_labels(scores, spec, cfg)
    X = feature_matrix(scores, spec)
    H = spec["horizon"]
    FWD = _forward(rets, H)
    A = rets.shape[1]
    r_now, x_now = labels[pos], X[pos]
    if np.isnan(x_now).any():
        return None
    idx = np.arange(pos)
    cand = idx[(labels[:pos] == r_now) & (idx + H < pos)]
    cand = cand[~np.isnan(X[cand]).any(axis=1)]
    if len(cand) < spec["min_analogs"]:
        return None
    dist = np.linalg.norm(X[cand] - x_now, axis=1)
    w = _kw(dist, spec)
    if len(cand) > spec["topk"]:
        keep = np.argsort(-w)[: spec["topk"]]; cand, w = cand[keep], w[keep]
    w = w / w.sum()
    exp = _expected_fwd(FWD, cand, w, spec["min_cov"], A)
    assets = np.array(rets.columns)
    ok = np.where(~np.isnan(exp))[0]
    if len(ok) < 2 * spec["nbasket"]:
        return None
    ranked = ok[np.argsort(-exp[ok])]
    N = spec["nbasket"]
    return dict(regime=int(r_now), n_analogs=int(len(cand)),
                longs=list(assets[ranked[:N]]), shorts=list(assets[ranked[-N:]]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-refresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("FORWARD LOG -- daily pre-registered forward test")
    print("=" * 72)

    if not args.no_refresh and not args.dry_run:
        refresh_data()

    cfg = load_config()
    specs = load_models()
    try:
        scores, rets = load_data()
    except Exception as e:
        die(f"could not load panels ({e}). Run the pipeline manually.")

    dates = scores.index
    signal_date = dates[-1]                      # last completed US close
    print(f"latest US close in data: {signal_date.date()}")

    ledger = pd.read_csv(LEDGER, parse_dates=["signal_date", "entry_date"]) \
        if LEDGER.exists() else pd.DataFrame(
            columns=["signal_date", "entry_date", "model", "regime", "n_analogs",
                     "longs", "shorts", "horizon", "status", "long_ret",
                     "short_ret", "spread"])

    # ---- 1. log today's picks (skip if this US close is already logged) ----
    already = (not ledger.empty) and (ledger["signal_date"] == signal_date).any()
    if already:
        print("  no new US close since last run -> skipping new entries (no duplicates).")
    else:
        pos = len(dates) - 1
        new_rows = []
        for name, spec in specs.items():
            p = picks_for(scores, rets, spec, cfg, pos)
            if p is None:
                print(f"  WARNING: {name} produced no picks (too few analogs) -- skipped.")
                continue
            new_rows.append(dict(
                signal_date=signal_date, entry_date=pd.NaT, model=name,
                regime=p["regime"], n_analogs=p["n_analogs"],
                longs="|".join(p["longs"]), shorts="|".join(p["shorts"]),
                horizon=spec["horizon"], status="pending",
                long_ret=np.nan, short_ret=np.nan, spread=np.nan))
            print(f"  {name}: regime {p['regime']} | L: {', '.join(p['longs'])} "
                  f"| S: {', '.join(p['shorts'])}")
        if args.dry_run:
            print("\n(dry run -- nothing written)"); return
        ledger = pd.concat([ledger, pd.DataFrame(new_rows)], ignore_index=True)

    # ---- 2. resolve entry dates + back-fill matured results ----------------
    ret_dates = rets.index
    for i, row in ledger.iterrows():
        sd = pd.to_datetime(row["signal_date"])
        later = ret_dates[ret_dates > sd]
        if len(later) == 0:
            continue                                   # entry hasn't happened yet
        entry = later[0]
        ledger.at[i, "entry_date"] = entry
        if row["status"] == "matured":
            continue
        H = int(row["horizon"])
        after = ret_dates[ret_dates > entry]
        if len(after) < H:
            continue                                   # not matured yet
        window = ret_dates[(ret_dates > entry)][:H]     # H days AFTER entry
        L = [t for t in str(row["longs"]).split("|") if t in rets.columns]
        S = [t for t in str(row["shorts"]).split("|") if t in rets.columns]
        lr = float(np.expm1(np.log1p(rets.loc[window, L]).sum()).mean())
        sr = float(np.expm1(np.log1p(rets.loc[window, S]).sum()).mean())
        ledger.at[i, "long_ret"] = lr
        ledger.at[i, "short_ret"] = sr
        ledger.at[i, "spread"] = lr - sr
        ledger.at[i, "status"] = "matured"

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(LEDGER, index=False)

    # ---- 3. write the Markdown scoreboard ---------------------------------
    lines = ["# Forward-test scoreboard (live, out-of-sample)", "",
             "Pre-registered models frozen in `config/models.yaml` before any live data.",
             "Signal = last completed US close; **entry = next US session**; exit = H trading days later.",
             "`pending` = horizon has not elapsed yet (expected on recent rows).", "",
             "## Running summary", ""]

    mat = ledger[ledger["status"] == "matured"]
    lines += ["| model | matured trades | mean spread | hit-rate | "
              "NON-OVERLAP trades | NON-OVERLAP mean spread |",
              "|---|---|---|---|---|---|"]
    for name in specs:
        m = mat[mat["model"] == name].sort_values("entry_date")
        if m.empty:
            lines.append(f"| {name} | 0 | – | – | 0 | – |"); continue
        H = int(specs[name]["horizon"])
        no = m.iloc[::H]                                  # every H-th = independent
        lines.append(
            f"| {name} | {len(m)} | {m['spread'].mean()*100:+.3f}% | "
            f"{(m['spread']>0).mean():.0%} | {len(no)} | {no['spread'].mean()*100:+.3f}% |")
    lines += ["", "*Naive column counts overlapping daily entries (they share most of their "
              "days, so significance would be inflated). The NON-OVERLAP column samples "
              "every H-th trade and is the statistically honest one.*", "",
              "## Full log", "",
              "| signal date | entry date | model | regime | longs | shorts | H | status | spread |",
              "|---|---|---|---|---|---|---|---|---|"]
    for _, r in ledger.sort_values(["signal_date", "model"], ascending=[False, True]).iterrows():
        sp = "pending" if r["status"] != "matured" else f"{r['spread']*100:+.3f}%"
        ed = "" if pd.isna(r["entry_date"]) else pd.to_datetime(r["entry_date"]).date()
        lines.append(f"| {pd.to_datetime(r['signal_date']).date()} | {ed} | {r['model']} | "
                     f"{r['regime']} | {str(r['longs']).replace('|', ', ')} | "
                     f"{str(r['shorts']).replace('|', ', ')} | {r['horizon']} | {r['status']} | {sp} |")
    SCOREBOARD.write_text("\n".join(lines) + "\n")

    n_pend = int((ledger["status"] != "matured").sum())
    print(f"\n  ledger: {len(ledger)} rows ({len(mat)} matured, {n_pend} pending)")
    print(f"  scoreboard -> {SCOREBOARD}")
    print("=" * 72)


if __name__ == "__main__":
    main()
