"""22 Oct: (1) src/latency_audit.py — how stale each engine input is at run time, logged nightly (TRACK 3.27);
(2) TRACK 3.28 blind-spot fill plan; (3) TRACK §4 design note: reason-weighted path range (founder, 22 Oct); CURRENT_STATE 18.33.
Run from the repo root:  python latency_and_plan.py ; python -m src.download_data ; python -m src.latency_audit"""
from pathlib import Path
import sys

la = Path("src/latency_audit.py")
if la.exists(): print("  latency_audit.py: already")
else:
    la.write_text(r'''"""
Input latency audit (TRACK 3.27). At run time: for every series the engine reads, the last session it holds vs the last completed
NYSE session, in sessions; plus the timestamp of Yahoo's live quote for the display instruments. Appends to processed/latency_log.csv,
writes docs/latency_audit.md. Criterion (prereg in TRACK 3.27): a series that is >= 2 sessions behind on >= 20% of runs over 20 runs is
flagged STALE; every live rule that reads it must state the lag on the app, and the backfill alignment for that series is re-checked.

  python -m src.latency_audit
"""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PROC, DOCS = Path("processed"), Path("docs")
LOG = PROC / "latency_log.csv"
FILES = {"asset_returns.parquet": ["SPY", "TLT", "GLD", "UUP", "USO"], "macro_panel.parquet": None, "wti_cont.parquet": ["WTI_SPOT", "WTI_FUT", "USO"]}
LIVE = ["SPY", "GLD", "USO", "TLT", "UUP", "^TNX", "DX-Y.NYB", "CL=F", "SI=F"]


def last_completed():
    try:
        from src.market_calendar import last_completed_session
        return pd.Timestamp(last_completed_session()).normalize()
    except Exception:
        return (pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(hours=21)).normalize()


def sessions_between(a: pd.Timestamp, b: pd.Timestamp) -> int:
    """NYSE sessions strictly after a up to b (business days; holidays count as a day of lag, stated)."""
    if pd.isna(a) or a >= b: return 0
    return len(pd.bdate_range(a, b)) - 1


def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M"); lc = last_completed(); rows = []
    for f, cols in FILES.items():
        p = PROC / f
        if not p.exists(): rows.append(dict(run=now, file=f, series="(missing)", last="", lag=np.nan)); continue
        df = pd.read_parquet(p); df.index = pd.to_datetime(df.index)
        for c in (cols or list(df.columns)):
            if c not in df.columns: continue
            ld = df[c].last_valid_index()
            rows.append(dict(run=now, file=f, series=c, last=("" if ld is None else ld.strftime("%Y-%m-%d")), lag=(np.nan if ld is None else sessions_between(ld, lc))))
    try:
        import yfinance as yf
        for t in LIVE:
            try:
                h = yf.Ticker(t).history(period="5d", interval="1d")
                ld = pd.to_datetime(h.index[-1]).tz_localize(None).normalize() if len(h) else None
                rows.append(dict(run=now, file="yahoo-live", series=t, last=("" if ld is None else ld.strftime("%Y-%m-%d")), lag=(np.nan if ld is None else sessions_between(ld, lc))))
            except Exception as e:
                rows.append(dict(run=now, file="yahoo-live", series=t, last=f"error {type(e).__name__}", lag=np.nan))
    except ImportError:
        pass
    new = pd.DataFrame(rows)
    old = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(columns=new.columns)
    allr = pd.concat([old, new], ignore_index=True); allr.to_csv(LOG, index=False)
    # summary over the last 20 runs
    runs = sorted(allr.run.unique())[-20:]; rec = allr[allr.run.isin(runs)]
    L = [f"# Input latency audit", "", f"*{now}. Last completed NYSE session: {lc.date()}. Lag = sessions the series is behind it at run time. "
         f"Flag rule (TRACK 3.27): ≥ 2 sessions behind on ≥ 20% of the last 20 runs → STALE. Runs on record: {len(runs)}.*", "",
         "| file | series | last date this run | lag now | runs seen | share ≥ 2 behind | flag |", "|---|---|---|---|---|---|---|"]
    for (f, s_), g in rec.groupby(["file", "series"], sort=False):
        cur = g.iloc[-1]; share = float((g.lag >= 2).mean()) if g.lag.notna().any() else np.nan
        flag = "STALE" if (len(g) >= 5 and share >= 0.2) else ("watch" if (isinstance(cur.lag, float) and cur.lag >= 2) else "")
        L.append(f"| {f} | {s_} | {cur['last']} | {'' if pd.isna(cur.lag) else int(cur.lag)} | {len(g)} | {'' if pd.isna(share) else f'{share:.0%}'} | {flag} |")
    L += ["", "Reading: a lag of 1 on FRED series (yields, dollar, oil spot) is their publication schedule, declared where it matters (the oil leg's "
          "provisional flag). A lag of 1 on the price panel at the nightly run time means the download missed the latest close — the fault seen on "
          "16 and 21 Oct 2026. Backtests are unaffected by latency only where the backfill used the same as-of alignment; that is checked per flagged series."]
    (DOCS / "latency_audit.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> docs/latency_audit.md, {LOG}")


if __name__ == "__main__":
    run()
''')
    print("  latency_audit.py: written")

d = Path("daily_run.sh"); s = d.read_text()
if "latency_audit" in s: print("  daily_run latency hook: already")
else:
    old = 'python -m src.oil_shock forward || echo "  oil forward failed -- continuing"\n'
    if old not in s: print("  daily_run anchor not found -- add by hand after the oil forward line: python -m src.latency_audit || echo \"  latency audit failed -- continuing\"")
    else: d.write_text(s.replace(old, old + 'python -m src.latency_audit || echo "  latency audit failed -- continuing"\n', 1)); print("  daily_run latency hook: added")

t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "## 4. Potential upgrades — not registered, not costed\n"
if "### 3.27 Input latency audit" in s: print("  TRACK 3.27/3.28: already")
elif anchor not in s: sys.exit("  TRACK anchor not found")
else:
    add = """### 3.27 Input latency audit (registered 22 Oct, running nightly)

Founder's check after the 20–22 Oct week: are the engine's inputs stale at the moment it acts? `src/latency_audit.py` logs, every run, how many
sessions each input series is behind the last completed NYSE session (price panel, macro panel, oil columns, Yahoo live quotes) to
`processed/latency_log.csv` and `docs/latency_audit.md`. Criterion, fixed: a series ≥ 2 sessions behind on ≥ 20% of the last 20 runs is STALE;
every live rule reading it must state the lag on the app, and the backfill alignment for that series is re-checked (tests are unaffected by
latency only where the backfill used the same as-of alignment the live engine sees). Known at registration: FRED daily series publish one
session late (declared on the oil leg as "provisional"); the price download missed the latest close on 16 and 21 Oct (no 21 Oct report was
written at the 22 Oct run) and the nightly 8-K fetch printed nothing on 22 Oct — both to be diagnosed from the first audit rows.

### 3.28 Blind-spot fill plan (registered 22 Oct as a plan; built after the current list is cleared)

What the 20–22 Oct week showed the engine cannot see, and the fill for each, in order:
1. **8-K ticker list** — add the AI-capex bellwethers (META, GOOGL, AMZN, AAPL, AVGO, AMD) as a dated corpus amendment; backfill read ~US$15.
2. **Metals and a long dollar series** — silver (SI=F / spot), LBMA gold spot, DXY from the 1970s as display + history columns, the §3.13 pattern;
   unlocks H3 (dollar events) and the gold/dollar/oil cells of H4up; free, ~1 day.
3. **Positioning** — CFTC Commitments of Traders (gold, silver, oil; free, weekly) as a blind-spot input, registered before any use.
4. **Sector axis** — schema v2 (§3.3, US$200–400) so "capex up / capex cut" can be scored; until then the reader's five axes cannot represent it.
5. **Rhetoric** — GDELT trigger (§3.4) / source expansion (§3.2), as costed.
Every fill is a corpus or population change and goes in as a dated amendment with its own prior; nothing above alters a recorded verdict.

"""
    s = s.replace(anchor, add + anchor, 1)
    note = """- **Reason-weighted path range (founder, 22 Oct).** Segment past rises and falls per market (episodes ≥ 10% peak-to-trough); have the reader
  label the reasons present in each episode's documents; fit a walk-forward model from reason indicators + macro legs to the forward 60-session
  path; apply today's reasons to give a path **range** (median, worst, best — never a point target) under the current regime. Pieces already in
  the repo: `episode_rotation.py`, `attribution.py` (T13 influence cells, 1 earned), the A3b nearest-neighbour estimate (FAIL vs the plain median),
  T2 expected-move (registered, not built). Risk stated at registration: an LLM asked why a market rose always produces a story, and the same
  stories precede falls; ~40 swings since 1995 against dozens of labels fits the stories, not the market. Criterion if built: beats the
  unconditional path range on held-out episodes (MAE of the median, coverage of the range). Prior (Claude): attribution earns cells slowly;
  the magnitude model fails as A3b did. Taken up after the list, with the founder choosing whether the prior is worth the test.
"""
    s = s.replace(anchor, anchor + note, 1)
    t.write_text(s); print("  TRACK 3.27, 3.28, §4 note: done")

c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
if "### 18.33" in s: print("  CURRENT_STATE 18.33: already")
else:
    c.write_text(s.rstrip("\n") + """

### 18.33 Latency audit and blind-spot fill plan (22 Oct)

The 20–22 Oct week (gold −2%, silver −4% on the day and −53% from its January record, Brent $110 on the Shaybah drone and the Hormuz stalemate,
December-hike odds ~90% after a hot core CPI, Meta −10% on *raised* capex, Tesla's deck showing a capex cut) was outside the engine's sight by
construction: no sector axis, no silver, no positioning data, Meta not in the 8-K list, and the live reports still carrying zero documents.
Three things registered: an input latency audit running nightly (3.27), a fill plan for the holes (3.28), and the founder's reason-weighted
path-range idea as a §4 design note with its risk and prior stated. Two faults to diagnose from the audit: the price download missing the latest
close at run time (16 and 21 Oct) and the nightly 8-K fetch printing nothing on 22 Oct.
"""); print("  CURRENT_STATE 18.33: appended")
print("done -- python -m src.download_data ; python -m src.latency_audit")
