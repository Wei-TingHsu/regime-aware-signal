"""
T14 phase A -- does the initial 30-minute FOMC reaction extend or reverse by the close?

Registered: docs/prereg_event_time.md (2026-09-29). Criterion fixed there.

Inputs
  data_provenance/mps/monetary-policy-surprises-data.xlsx   sheet "FOMC (update 2023)"
  ^GSPC and ^TNX daily closes from Yahoo (fetched once, cached to data_provenance/mps/daily_*.csv)

Output
  docs/event_time_phaseA.md

Usage
  python -m src.event_time_phaseA
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

XLSX = Path("data_provenance/mps/monetary-policy-surprises-data.xlsx")
SHEET = "FOMC (update 2023)"
OUT = Path("docs/event_time_phaseA.md")
N_PERM = 10_000
EXCLUDE = {pd.Timestamp("2001-09-17")}
PRIOR = {"S&P 500": "NULL", "10-year yield": "EXTENDS"}


def daily(tk: str) -> pd.DataFrame:
    cache = Path(f"data_provenance/mps/daily_{tk.strip('^')}.csv")
    if cache.exists():
        d = pd.read_csv(cache, index_col=0, parse_dates=True)
    else:
        import yfinance as yf
        d = yf.Ticker(tk).history(start="1987-06-01", interval="1d", auto_adjust=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        d = d[["Open", "Close"]].dropna()
        d.index = pd.to_datetime(d.index).tz_localize(None) if getattr(d.index, "tz", None) is not None else pd.to_datetime(d.index)
        d.to_csv(cache)
    return d


def announcements() -> pd.DataFrame:
    f = pd.read_excel(XLSX, sheet_name=SHEET)
    f["Date"] = pd.to_datetime(f["Date"], errors="coerce")
    f = f.dropna(subset=["Date"])
    f = f[f["Unscheduled"].fillna(0) == 0]
    f = f[~f["Date"].isin(EXCLUDE)]
    # announcement time: exclude anything at/after 3:30 pm ET (no rest of session)
    def hhmm(x):
        try:
            return pd.to_datetime(str(x)).time()
        except Exception:
            return None
    t = f["Time"].map(hhmm)
    f = f[t.map(lambda v: v is None or (v.hour, v.minute) < (15, 30))]
    return f.set_index("Date").sort_index()


def build() -> pd.DataFrame:
    f = announcements()
    sp, tn = daily("^GSPC"), daily("^TNX")
    rows = []
    for t, r in f.iterrows():
        if t not in sp.index or t not in tn.index:
            continue
        i, j = sp.index.get_loc(t), tn.index.get_loc(t)
        if i < 1 or j < 1 or i + 1 >= len(sp) or j + 1 >= len(tn):
            continue
        r0_sp = float(r["SP500"]) / 100 if pd.notna(r["SP500"]) else np.nan
        r0_tn = float(r["TNOTE10"]) if pd.notna(r["TNOTE10"]) else np.nan
        day_sp = float(np.log(sp["Close"].iloc[i] / sp["Close"].iloc[i - 1]))
        day_tn = float(tn["Close"].iloc[j] - tn["Close"].iloc[j - 1])
        rows.append(dict(date=t, year=t.year,
                         sp_r0=r0_sp, sp_rest=day_sp - r0_sp, sp_next=float(np.log(sp["Close"].iloc[i + 1] / sp["Close"].iloc[i])),
                         tn_r0=r0_tn, tn_rest=day_tn - r0_tn, tn_next=float(tn["Close"].iloc[j + 1] - tn["Close"].iloc[j])))
    return pd.DataFrame(rows).set_index("date")


def perm_test(x: np.ndarray, y: np.ndarray, rng) -> tuple[float, float]:
    m = np.isfinite(x) & np.isfinite(y); x, y = x[m], y[m]
    xc = x - x.mean(); b = float((xc * (y - y.mean())).sum() / (xc ** 2).sum())
    null = np.array([(np.random.permutation(xc) * (y - y.mean())).sum() / (xc ** 2).sum() for _ in range(N_PERM)])
    return b, float((np.abs(null) >= abs(b)).mean()), int(m.sum())


def main():
    rng = np.random.default_rng(0); np.random.seed(0)
    df = build()
    L = ["# T14 phase A — does the initial FOMC reaction extend or reverse?", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_event_time.md`. {len(df)} scheduled announcements "
         f"{df.index.min().date()} → {df.index.max().date()}; initial reaction from the FRBSF 30-minute window; "
         f"{N_PERM:,} permutations. The rest-of-session proxy contains the unobserved pre-announcement move.*", ""]
    verdicts = {}
    for name, pre in (("S&P 500", "sp"), ("10-year yield", "tn")):
        L += [f"## {name}", "", "| sample | window | n | b (fraction of initial move) | p | reading |", "|---|---|---|---|---|---|"]
        for label, sub in (("all", df), ("2006+ (regime span)", df[df.year >= 2006]), ("2013+ (2 pm, press conf.)", df[df.year >= 2013])):
            for win, key in (("rest of session (primary)", "rest"), ("next session", "next")):
                b, p, n = perm_test(sub[f"{pre}_r0"].to_numpy(), sub[f"{pre}_{key}"].to_numpy(), rng)
                read = "EXTENDS" if (p < 0.05 and b > 0) else ("REVERSES" if (p < 0.05 and b < 0) else "NULL")
                if label == "all" and key == "rest":
                    verdicts[name] = read
                L.append(f"| {label} | {win} | {n} | {b:+.3f} | {p:.4f} | {read} |")
        # descriptive 2x2 on the primary window
        x, y = df[f"{pre}_r0"], df[f"{pre}_rest"]
        up, dn = y[x > 0], y[x < 0]
        unit = "%" if pre == "sp" else "pp"
        sc = 100 if pre == "sp" else 1
        L += ["", f"Descriptive: after an initial *up* move, mean rest-of-session {up.mean()*sc:+.3f}{unit} (n={len(up)}); "
                  f"after an initial *down* move, {dn.mean()*sc:+.3f}{unit} (n={len(dn)}).", ""]
    L += ["## Verdicts (primary window, full sample)", ""]
    for name, v in verdicts.items():
        L.append(f"- **{name}: {v}** (registered prior: {PRIOR[name]}{' — prior held' if v == PRIOR[name] else ' — prior wrong'})")
    L += ["", "Per §4 of the registration, an EXTENDS or REVERSES verdict permits the app's rest-of-session line for that market "
              "only with a same-regime precedent pool of ESS ≥ 8 (phase A2); NULL permits no number."]
    OUT.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"\n  -> {OUT}")


if __name__ == "__main__":
    main()
