"""19 Oct: record H0 (prior #49 wrong, tally 49) and wire the H0 paragraph into the app's Context block.
Run from the repo root:  python h0_record_wire.py ; python -m src.context selftest ; python -m src.context show GLD | head -12"""
from pathlib import Path
import sys

# ---- prereg §5 results
p = Path("docs/prereg_history_tables.md"); s = p.read_text()
if "## 5. Results" in s: print("  prereg §5: already")
else:
    p.write_text(s.rstrip("\n") + """

## 5. Results

| date | table | result | prior |
|---|---|---|---|
| 2026-10-19 | H0 | Measured, no test (as registered). 20-session medians inside each label vs all history: SPY, TLT, UUP within 1 pt everywhere. Gold regime 3 **+2.4% vs +0.7%** (60 sessions +7.5% vs +2.4%; positive 68% vs 56%). WTI regime 1 +2.6%, regime 3 **−1.3%** vs +0.9%; USO regime 1 +2.0% vs +0.5%. Label −1 = sessions before the model had enough history to label. Session counts are overlapping windows (÷20 ≈ independent cases). `docs/history_H0.md`, `processed/history_tables.json`. | **#49 wrong**: gold and oil exceed 1 pt; TLT does not. Tally 49. |
"""); print("  prereg §5 H0 result: appended")

# ---- TRACK
t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "Build order H0, H1, H3, H4, H5; H2 after the 08:30 reader's first month; H6, H7 after.\n"
if "H0 measured 19 Oct" in s: print("  TRACK 3.25 H0: already")
elif anchor not in s: sys.exit("  TRACK 3.25 anchor not found")
else:
    t.write_text(s.replace(anchor, anchor + "**H0 measured 19 Oct:** gold regime 3 +2.4% vs +0.7% all-history at 20 sessions, oil ±1.5–2.2 pts by regime, SPY/TLT/UUP flat; "
                 "prior #49 wrong (tally 49). In the app as `measured` under \"What history says in today's condition\". H1, H3, H4, H5 next.\n", 1)); print("  TRACK 3.25 H0: done")

# ---- MASTER tally
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
old = "tally 48 (#40–#43 lever priors, #44 July calendar, #45–#48 oil-shock pool size, gold's sign, the legs' value, the USO held-out, all Claude's)"
if "tally 49" in s: print("  MASTER tally: already")
elif old not in s: print("  MASTER tally anchor not found -- edit by hand: tally 48 -> 49 (#49 H0 regime spread)")
else:
    s = s.replace(old, "tally 49 (#40–#43 lever priors, #44 July calendar, #45–#48 oil-shock pool size, gold's sign, the legs' value, the USO held-out, #49 H0 regime spread, all Claude's)", 1)
    s = s.replace("| priors #49–#53: all tests FAIL, tables informative |", "| H0 measured 19 Oct: gold regime 3 +2.4% vs +0.7% (#49 wrong); priors #50–#53 open |", 1)
    m.write_text(s); print("  MASTER tally 49 + row 45: done")

# ---- CURRENT_STATE
c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
if "### 18.31" in s: print("  CURRENT_STATE 18.31: already")
else:
    c.write_text(s.rstrip("\n") + """

### 18.31 History tables H0–H7 registered; H0 measured (19 Oct)

The app's Context block was fed by one study (oil shocks). `docs/prereg_history_tables.md` registers eight conditional path tables with one
shared engine and one uniform test (20-session sign share vs the market's own base rate, ≥ 15 pts, n ≥ 30, random-date null); priors #49–#53.
H0 (each market inside each regime label, measured only by design): gold in regime 3 ran +2.4% at 20 sessions against +0.7% over all history
and +7.5% vs +2.4% at 60; WTI −1.3% in regime 3, +2.6% in regime 1; SPY, TLT and the dollar within a point of their all-history rows. Prior #49
(nothing beyond 1 pt) wrong — tally 49. Session counts are overlapping windows; the app states the independent-case count (÷20). Also found
this day: the live document feed has delivered zero documents on 29 of the last 30 report days (political source 0; earnings 8-K live status
to confirm), so the "0 of 5" on Today is the feed, not the engine; and `daily_run.sh` has no git step — the cloud app shows the last manual push.
"""); print("  CURRENT_STATE 18.31: appended")

# ---- context.py: H0 paragraph
q = Path("src/context.py"); s = q.read_text()
if "def h0_sentence" in s: print("  context H0 paragraph: already")
else:
    helper = '''
def h0_sentence(asset, k, label, name, ticker=None, reg=None):
    """What history says in today's condition: the asset's own row for label k vs the all-history row (processed/history_tables.json, H0).
    For a searched ticker, computed now from its prices against the label series. Measured only — prereg_history_tables §2."""
    if k is None: return None
    lab_txt = label if k >= 0 else "the stretch before the model had enough history to label"
    if asset in MODEL:
        H0 = ((_j(PROC / "history_tables.json") or {}).get("H0") or {}).get("markets", {}).get(asset)
        if not H0 or str(k) not in H0: return None
        me, al = H0[str(k)], H0["all"]
    else:
        if reg is None or not ticker: return None
        try:
            import yfinance as yf
            d = yf.Ticker(ticker).history(period="max", interval="1d", auto_adjust=False)["Close"]; d.index = pd.to_datetime(d.index).tz_localize(None)
            r = np.log(d).diff(); f20, f60 = r.rolling(20).sum().shift(-20), r.rolling(60).sum().shift(-60)
            df = pd.DataFrame({"f20": f20, "f60": f60}).join(reg.rename("lab"), how="inner").dropna()
            g = df[df.lab == k]
            if len(g) < 100: return None
            me = dict(n=len(g), f20=float(g.f20.median()), f60=float(g.f60.median()), sign20=float((g.f20 > 0).mean()))
            al = dict(n=len(df), f20=float(df.f20.median()), f60=float(df.f60.median()), sign20=float((df.f20 > 0).mean()))
        except Exception:
            return None
    return (f"Inside today's condition ({lab_txt}), {name}'s return over the next month (20 sessions) has had a median of <b>{_pct(me['f20'])}</b>, "
            f"against {_pct(al['f20'])} across all history; it was positive {me['sign20']:.0%} of the time, against {al['sign20']:.0%}; over a quarter "
            f"(60 sessions) {_pct(me['f60'])} against {_pct(al['f60'])}. Counted over {me['n']:,} sessions in this condition — overlapping windows, so about "
            f"{me['n'] // 20} independent month-long cases {tag('measured')}. The condition label is the engine's own input, so this is a count of what "
            f"followed it, not a test of it and not a forecast.")

'''
    s = s.replace("\n# ---------------------------------------------------------------- the block\n", helper + "\n# ---------------------------------------------------------------- the block\n", 1)
    old = "    # 2. what history says here\n    s2 = []\n"
    if old not in s: sys.exit("  context s2 anchor not found")
    new = ("    # 1b. today's condition (H0)\n"
           "    h0 = h0_sentence(asset, k, label, name, ticker=ticker, reg=reg)\n"
           "    if h0: P.append((\"What history says in today's condition\", h0))\n\n"
           "    # 2. what history says here\n    s2 = []\n")
    s = s.replace(old, new, 1)
    s = s.replace('    if s2: P.append(("What history says in this environment", " ".join(s2)))', '    if s2: P.append(("What history says after oil shocks, and the engine\'s record", " ".join(s2)))', 1)
    # terminal `show` gets the label series too, so the H0 paragraph prints outside the app
    old = "        html = context_block(a.asset if a.asset in MODEL else None, day, prof=prof, ticker=None if a.asset in MODEL else a.asset)"
    if old in s:
        s = s.replace(old, "        from src.oil_shock import load, regime_labels\n"
                           "        lo = load(); rets_ = lo[0] if isinstance(lo, tuple) else lo\n"
                           "        reg_ = pd.Series(np.asarray(regime_labels(rets_.index)), index=rets_.index)\n"
                           "        html = context_block(a.asset if a.asset in MODEL else None, day, prof=prof, reg=reg_, ticker=None if a.asset in MODEL else a.asset)", 1)
    q.write_text(s); print("  context H0 paragraph: wired")
print("done -- python -m src.context selftest ; python -m src.context show GLD | head -12")
