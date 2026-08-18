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
  * Horizons are counted in NYSE TRADING DAYS (src.market_calendar), not in
    panel index rows -- the panel is a plain bdate_range, so market holidays
    sit in it as all-NaN rows and would otherwise be miscounted as sessions.
  * Results are 'pending' until the horizon matures, then back-filled.
  * WINDOW INTEGRITY (pre-registered 2026-08-18, at 0 matured / 3 pending):
    a row is scored 'matured' only if EVERY day of its H-day window has a
    return for EVERY picked asset. Incomplete windows are marked
    'short_window' with their realised day count and excluded from the
    headline summary, but stay visible in the full log. Entry dates and picks
    are frozen at log time and are never reassigned.
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
from src.market_calendar import trading_days

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
        cmd = [sys.executable, "-m", mod]
        if mod == "src.download_data":
            cmd.append("--force")          # cache-first fetch would serve STALE data
        r = subprocess.run(cmd, capture_output=True, text=True)
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

    # --- signal date must be the last date with REAL price coverage ---------
    # The macro panel is forward-filled, so PCA scores exist even on days with
    # no prices. Using the last index row would compute picks from an empty bar.
    cov = rets.notna().sum(axis=1)
    min_assets = max(10, int(0.4 * rets.shape[1]))
    valid = cov[cov >= min_assets].index
    if len(valid) == 0:
        die("no date has usable price coverage -- run: python -m src.download_data --force")
    signal_date = valid[-1]
    pos = int(dates.get_indexer([signal_date])[0])

    stale_days = (pd.Timestamp.now("UTC").tz_localize(None).normalize() - signal_date).days
    print(f"latest US close WITH PRICE DATA: {signal_date.date()} "
          f"({int(cov.loc[signal_date])}/{rets.shape[1]} assets, {stale_days}d old)")
    if dates[-1] != signal_date:
        print(f"  note: panel index runs to {dates[-1].date()} but those rows have no "
              f"prices yet -- using {signal_date.date()} as the signal bar.")
    if stale_days > 5:
        die(f"price data is {stale_days} days stale (latest {signal_date.date()}). "
            f"Check the data source before logging -- refusing to log stale picks.")

    ledger = pd.read_csv(LEDGER, parse_dates=["signal_date", "entry_date"]) \
        if LEDGER.exists() else pd.DataFrame(
            columns=["signal_date", "entry_date", "model", "regime", "n_analogs",
                     "longs", "shorts", "horizon", "status", "long_ret",
                     "short_ret", "spread", "realised_days"])
    if "realised_days" not in ledger.columns:
        ledger["realised_days"] = np.nan          # back-compat: pre-rule rows

    # ---- 1. log today's picks (skip if this US close is already logged) ----
    already = (not ledger.empty) and (ledger["signal_date"] == signal_date).any()
    if already:
        print("  no new US close since last run -> skipping new entries (no duplicates).")
    else:
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
                long_ret=np.nan, short_ret=np.nan, spread=np.nan,
                realised_days=np.nan))
            print(f"  {name}: regime {p['regime']} | L: {', '.join(p['longs'])} "
                  f"| S: {', '.join(p['shorts'])}")
        if args.dry_run:
            print("\n(dry run -- nothing written)"); return
        ledger = pd.concat([ledger, pd.DataFrame(new_rows)], ignore_index=True)

    # The dry-run guard above only fires when new picks were computed. Repeat it
    # here so --dry-run is inert on days with no new US close too, when the run
    # would otherwise fall straight through to the write in section 2/3.
    if args.dry_run:
        print("\n(dry run -- nothing written)"); return

    # ---- 2. resolve entry dates + back-fill matured results ----------------
    # Sessions, not index rows. The panel index is a bdate_range, so NYSE
    # holidays appear in it as all-NaN rows; counting them as trading days
    # would both mis-date entries and shorten every horizon that spans one.
    ret_dates = rets.index
    tdays = ret_dates.intersection(trading_days(ret_dates[0], ret_dates[-1]))
    if len(tdays) == 0:
        die("no NYSE trading days found in the panel index -- check market_calendar.")

    for i, row in ledger.iterrows():
        sd = pd.to_datetime(row["signal_date"])

        # entry is FROZEN once written -- never recompute a logged entry date
        if pd.isna(row["entry_date"]):
            later = tdays[tdays > sd]
            if len(later) == 0:
                continue                               # entry hasn't happened yet
            entry = later[0]
            ledger.at[i, "entry_date"] = entry
        else:
            entry = pd.to_datetime(row["entry_date"])

        if row["status"] == "matured":
            continue                                   # settled; nothing to revisit

        H = int(row["horizon"])
        after = tdays[tdays > entry]
        if len(after) < H:
            continue                                   # window not fully formed
        window = after[:H]                             # H SESSIONS after entry
        if window[-1] > signal_date:
            continue                                   # window runs past usable data

        L = [t for t in str(row["longs"]).split("|") if t in rets.columns]
        S = [t for t in str(row["shorts"]).split("|") if t in rets.columns]
        picks = L + S
        if not picks:
            print(f"  WARNING: {row['model']} entry {entry.date()} has no resolvable "
                  f"picks in the current universe -- left unscored.")
            continue

        # STRICT window integrity: every session, every picked asset.
        day_ok = rets.loc[window, picks].notna().all(axis=1)
        realised = int(day_ok.sum())

        lr = float(np.expm1(np.log1p(rets.loc[window, L]).sum()).mean())
        sr = float(np.expm1(np.log1p(rets.loc[window, S]).sum()).mean())
        ledger.at[i, "long_ret"] = lr
        ledger.at[i, "short_ret"] = sr
        ledger.at[i, "spread"] = lr - sr
        ledger.at[i, "realised_days"] = realised
        ledger.at[i, "status"] = "matured" if realised == H else "short_window"

        if realised < H:
            missing = [d.date() for d in window[~day_ok]]
            print(f"  SHORT WINDOW: {row['model']} entry {entry.date()} scored on "
                  f"{realised}/{H} sessions (missing {', '.join(map(str, missing))}) "
                  f"-- excluded from the headline summary.")

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(LEDGER, index=False)

    # ---- 3. write the Markdown scoreboard ---------------------------------
    lines = ["# Forward-test scoreboard (live, out-of-sample)", "",
             "Pre-registered models frozen in `config/models.yaml` before any live data.",
             "Signal = last completed US close; **entry = next US session**; exit = H trading days later.",
             "`pending` = horizon has not elapsed yet (expected on recent rows). "
             "`short_window` = the horizon elapsed but at least one session was missing "
             "data for at least one picked asset; the spread is shown with its realised "
             "session count and is EXCLUDED from the summary above.", "",
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
        if r["status"] == "matured":
            sp = f"{r['spread']*100:+.3f}%"
        elif r["status"] == "short_window":
            rd = r["realised_days"]
            rd = "?" if pd.isna(rd) else int(rd)
            sp = f"{r['spread']*100:+.3f}% ({rd}/{r['horizon']} sessions)"
        else:
            sp = "pending"
        ed = "" if pd.isna(r["entry_date"]) else pd.to_datetime(r["entry_date"]).date()
        lines.append(f"| {pd.to_datetime(r['signal_date']).date()} | {ed} | {r['model']} | "
                     f"{r['regime']} | {str(r['longs']).replace('|', ', ')} | "
                     f"{str(r['shorts']).replace('|', ', ')} | {r['horizon']} | {r['status']} | {sp} |")
    SCOREBOARD.write_text("\n".join(lines) + "\n")

    n_pend = int((ledger["status"] == "pending").sum())
    n_short = int((ledger["status"] == "short_window").sum())
    print(f"\n  ledger: {len(ledger)} rows ({len(mat)} matured, {n_pend} pending, "
          f"{n_short} short_window)")
    print(f"  scoreboard -> {SCOREBOARD}")
    print("=" * 72)


if __name__ == "__main__":
    main()
