"""selloff_forward.py -- the SEVERE SELL-OFF rule: what the old data says about it in detail, its forward record, and the card on the live page.
Registered in TRACK 3.101 (22 Nov 2026) before any forward case exists.

THE RULE (code SS-1), fixed. A stock of the list is in a SEVERE SELL-OFF at a close when all three hold:
    1. it closed 5% or more below the previous close;
    2. its volume that day was more than 1.98 times its average of the 60 sessions before;
    3. the fall was more than 2.72 times its own usual daily move (usual = the 60 sessions before).
Conditions 2 and 3 are the two marks of the machine's own group that carried the confirmed patterns of the search (TRACK 3.100, 3.101); 1.98 and 2.72 are the cuts the
search fixed on 2005-2017. What history says about the days AFTER such a close is measured by `describe`; what happens from 23 Nov 2026 onward is counted by `scan`.

    python -m src.selloff_forward describe   # old data only, no download: is the rule in every company or a few? does the market's state change it? can it be traded from the next open? -> docs/selloff_rule.md, .json
    python -m src.selloff_forward scan       # downloads the last two years of daily prices (Yahoo, free), records new cases and fills in what followed -> data_provenance/live/selloff_forward.csv, docs/selloff_forward.md
The live page starts `scan` by itself in the background (every 15 minutes while New York trades, every hour otherwise) and shows the 'Severe Sell-off' card.
"""
from __future__ import annotations
import argparse, json, os, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd

ROOT = Path("data_provenance/selloff"); DOCS = Path("docs"); FWD = Path("data_provenance/live/selloff_forward.csv"); CARD = Path("processed/selloff_card.json"); RULE_JSON = DOCS / "selloff_rule.json"
FALL, VOLX, SIZE = -5.0, 1.98, -2.72; START = pd.Timestamp("2026-11-23"); SPLIT = pd.Timestamp("2018-01-01"); VERDICT_AT = 30; NY = ZoneInfo("America/New_York")
F_VOL, F_SIZE, F_VIX, F_200, F_RUN = "volume against normal", "size in units of its own usual move", "VIX level", "S&P 500 against its 200-day average %", "run-up over the 60 sessions before %"
COLS = ["ticker", "day", "rule", "move_pct", "volume_x", "size_x", "run_up_60_pct", "close", "spy_close", "after1_vs_spx_bp", "after2_vs_spx_bp", "after3_vs_spx_bp", "after2_price_bp", "gap_next_open_bp", "open_to2_vs_spx_bp", "open_to3_vs_spx_bp"]


def _rate(y, w): ok = np.isfinite(y); return (float((y[ok] * w[ok]).sum() / w[ok].sum()), float(w[ok].sum())) if ok.any() and w[ok].sum() > 0 else (float("nan"), 0.0)


def _regimes():
    """the MAIN PAGE's market conditions (the four regimes of the 'Today' tab), by the same call app.py makes, with the same names (processed/regime_profile.json).
    Labels are the expanding ones: each day's condition uses only data up to that day. Returns (labels by day, {label: name}) or (None, {}) when the inputs are missing."""
    try:
        import asset_extension as AE
        cfg = AE.load_config(); sc, _ = AE.load_data(); lab = pd.Series(np.asarray(AE.regime_labels_expanding(sc, cfg)), index=pd.DatetimeIndex(sc.index)); prof = json.loads(Path("processed/regime_profile.json").read_text()).get("regimes", {})
        return lab, {int(k): v.get("label", f"Condition {int(k) + 1} of 4") for k, v in prof.items()}
    except Exception as e: print(f"  (the main page's market conditions could not be loaded: {type(e).__name__}: {str(e)[:120]})"); return None, {}


# ------------------------------------------------------------------ describe: the old data, in detail
def cmd_describe():
    from src.selloff_study import _px
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); spy = P["SPY"]
    B = E[(E.unit == "stocks") & (E.definition == "1 session, -5% or worse")].sort_values("day").reset_index(drop=True); n = len(B)
    b1, b2, b3, up2, gap, o2, o3, c2 = (np.full(n, np.nan) for _ in range(8))
    for q, r in enumerate(B.itertuples()):
        d = P[r.ticker]; c = d.close; i = int(r.i)
        if i + 3 >= len(c) or r.day not in spy.index: continue
        js = spy.index.get_loc(r.day)
        if js + 3 >= len(spy): continue
        s = spy.close; so = spy.open; m = lambda h: c.iloc[i + h] / c.iloc[i] - 1; ms = lambda h: s.iloc[js + h] / s.iloc[js] - 1
        b1[q], b2[q], b3[q], up2[q] = m(1) > ms(1), m(2) > ms(2), m(3) > ms(3), m(2) > 0; c2[q] = (m(2) - ms(2)) * 1e4; gap[q] = ((d.open.iloc[i + 1] / c.iloc[i] - 1) - (so.iloc[js + 1] / s.iloc[js] - 1)) * 1e4
        o2[q] = ((c.iloc[i + 2] / d.open.iloc[i + 1] - 1) - (s.iloc[js + 2] / so.iloc[js + 1] - 1)) * 1e4; o3[q] = ((c.iloc[i + 3] / d.open.iloc[i + 1] - 1) - (s.iloc[js + 3] / so.iloc[js + 1] - 1)) * 1e4
    ok = np.isfinite(b2); B = B[ok].reset_index(drop=True); b1, b2, b3, up2, gap, o2, o3, c2 = (x[ok] for x in (b1, b2, b3, up2, gap, o2, o3, c2))
    w = (1.0 / B.groupby("day").day.transform("size")).to_numpy(); rule = ((B[F_VOL] > VOLX) & (B[F_SIZE] < SIZE)).to_numpy(); old = (B.day < SPLIT).to_numpy(); new = ~old; pct = lambda x: "n/a" if x != x else f"{x:.0%}"
    L = ["# Severe sell-off rule (SS-1): what the old data says in detail", "", f"Rule: a stock of the list closes {-FALL:.0f}% or more below the previous close, on volume above {VOLX} times its 60-session average, with a fall larger than {-SIZE} times its own usual daily move. "
         f"Old data: {len(B)} one-day sell-offs of {B.ticker.nunique()} companies, 2005 to {B.day.max():%Y}; {int(rule.sum())} of them meet the rule ({B[rule].ticker.nunique()} companies). Each day counts once ('days'). "
         "**This page DESCRIBES the rule on data the search already used; it is not a new test.** The test is the forward record (docs/selloff_forward.md).", ""]
    # 1. the rule against all sell-offs
    L += ["## 1. After a severe sell-off, against all one-day sell-offs of 5% or more", "", "| period | group | beats the S&P 500 over 1 session | over 2 sessions | over 3 sessions | price higher after 2 sessions | days |", "|---|---|---|---|---|---|---|"]; S = {}
    for pn, pm in (("2005-2017", old), ("2018-2026", new)):
        for gn, gm in (("severe sell-off (the rule)", rule), ("all sell-offs of 5% or more", np.ones(len(B), bool))):
            m = pm & gm; r1, _ = _rate(b1[m], w[m]); r2, dys = _rate(b2[m], w[m]); r3, _ = _rate(b3[m], w[m]); ru, _ = _rate(up2[m], w[m]); S[(pn, gn[:3])] = (r2, dys, ru, r1, r3); L.append(f"| {pn} | {gn} | {pct(r1)} | {pct(r2)} | {pct(r3)} | {pct(ru)} | {dys:.0f} |")
    print("\n".join(L[-6:]))
    # 2. every company or a few?
    R = B[rule].assign(b2=b2[rule]); A = B.assign(b2=b2); base = float(A.b2.mean()); per = R.groupby("ticker").b2.agg(["size", "mean"]); k = 8; big = per[per["size"] >= k]
    sect = pd.read_csv(ROOT / "tables" / "T2.csv").drop_duplicates("event_id").set_index("event_id").sector if (ROOT / "tables" / "T2.csv").exists() else None
    L += ["", "## 2. Is it every company, or a few?", "", f"{B.ticker.nunique()} companies have at least one sell-off of 5% or more; **{len(per)} of them have at least one severe sell-off**. Over all sell-offs a stock beats the S&P 500 over the next 2 sessions {base:.0%} of the time (each sell-off counted once here, not each day). "
          f"**Of the {len(big)} companies with {k} or more severe sell-offs, {int((big['mean'] < base).sum())} are below that {base:.0%} after a severe sell-off, {int((big['mean'] >= base).sum())} are at or above it.** With {k} to 30 cases per company, one company's own number is noisy; the count of companies below is the point.", ""]
    print(L[-2])
    if sect is not None:
        R["sector"] = sect.reindex(R.event_id).to_numpy(); A["sector"] = sect.reindex(A.event_id).to_numpy(); L += ["| sector | companies with a severe sell-off | severe sell-offs | beats the S&P 500 over 2 sessions after a severe sell-off | after all its sell-offs | difference (points) |", "|---|---|---|---|---|---|"]
        for sname, g in sorted(R.groupby("sector"), key=lambda x: -len(x[1])):
            a = A[A.sector == sname].b2.mean(); L.append(f"| {sname} | {g.ticker.nunique()} | {len(g)} | {g.b2.mean():.0%} | {a:.0%} | {(g.b2.mean() - a) * 100:+.0f}{'' if len(g) >= 40 else ' (few cases)'} |")
        print("\n".join(L[-(R.sector.nunique() + 2):]))
    L += ["", "| company | severe sell-offs | beat the S&P 500 over 2 sessions |", "|---|---|---|"] + [f"| {t} | {int(x['size'])} | {x['mean']:.0%} |" for t, x in per.sort_values("size", ascending=False).iterrows()]
    # 3. does the state of the market change it?
    L += ["", "## 3. Does the state of the market change it?", "", "Each row: sell-offs that happened in that state. The pattern is the DIFFERENCE between the two percentage columns. The first rows use the MAIN PAGE's four market conditions, under the same names; the rows below them are single measures (VIX, stress index), which are not conditions of the main page.", "", "| state of the market on the day | severe sell-offs: beat the S&P 500 over 2 sessions | all sell-offs | difference (points) | days (severe) |", "|---|---|---|---|---|"]; n3 = len(L)
    def split(name, masks):
        for lab, m in masks:
            a, da = _rate(b2[m & rule], w[m & rule]); c, _ = _rate(b2[m], w[m]); L.append(f"| {name}: {lab} | {pct(a)} | {pct(c)} | {'n/a' if a != a else f'{(a - c) * 100:+.0f}'} | {da:.0f} |")
    lab, names = _regimes(); REG = {}
    if lab is not None:
        lab = lab[~lab.index.duplicated()].sort_index(); ud = pd.DatetimeIndex(B.day.unique()); g = lab.reindex(lab.index.union(ud)).ffill().reindex(B.day).to_numpy(float)
        for k in sorted(names):
            m = g == k; a, da = _rate(b2[m & rule], w[m & rule]); c, _ = _rate(b2[m], w[m]); REG[names[k]] = dict(rule=a, all=c, days=da); L.append(f"| Market condition (main page): {names[k]} | {pct(a)} | {pct(c)} | {'n/a' if a != a else f'{(a - c) * 100:+.0f}'} | {da:.0f} |")
    v = B[F_VIX].to_numpy(float); q1, q2 = np.nanquantile(v[old], [1 / 3, 2 / 3]); split("VIX", [(f"low (under {q1:.1f})", v < q1), (f"middle ({q1:.1f} to {q2:.1f})", (v >= q1) & (v <= q2)), (f"high (over {q2:.1f})", v > q2)])
    s2 = B[F_200].to_numpy(float); split("S&P 500", [("above its 200-day average", s2 >= 0), ("below its 200-day average", s2 < 0)])
    t4 = ROOT / "tables" / "T4.csv"; col = "St. Louis Fed financial stress index"
    if t4.exists():
        T4 = pd.read_csv(t4).drop_duplicates("event_id").set_index("event_id")
        if col in T4.columns:
            x = T4[col].reindex(B.event_id).to_numpy(float)
            if np.isfinite(x[old]).sum() > 100: a1, a2 = np.nanquantile(x[old], [1 / 3, 2 / 3]); split("financial stress index (St. Louis Fed)", [(f"low (under {a1:.2f})", x < a1), (f"middle ({a1:.2f} to {a2:.2f})", (x >= a1) & (x <= a2)), (f"high (over {a2:.2f})", x > a2)])
    ru = B[F_RUN].to_numpy(float); split("the stock's own 60 sessions before", [("rose (run-up)", ru > 1.77), ("flat or fell", ru <= 1.77)])
    print("\n".join(L[n3 - 2:]))
    # 4. can it be traded from the next open?
    L += ["", "## 4. Can it be acted on at the next open? (2018-2026, severe sell-offs, against the S&P 500 over the same span, before cost)", "", "| span | average, basis points | share of days below zero | days |", "|---|---|---|---|"]; n4 = len(L); m = rule & new; T = {}
    for lab, x in (("close of the sell-off day -> next open (cannot be traded: it happens overnight)", gap), ("next open -> close two sessions after the sell-off", o2), ("next open -> close three sessions after", o3), ("close -> close two sessions after (what the search measured)", c2)):
        g = np.isfinite(x) & m; dd = pd.DataFrame(dict(d=B.day[g].to_numpy(), x=x[g])).groupby("d").x.mean(); T[lab[:22]] = float(dd.mean()) if len(dd) else float("nan"); L.append(f"| {lab} | {dd.mean():+.0f} | {(dd < 0).mean():.0%} | {len(dd)} |" if len(dd) else f"| {lab} | n/a | n/a | 0 |")
    print("\n".join(L[n4 - 2:])); L += ["", "A cost of about 30 basis points for a round trip is not taken off. If the 'next open' rows are near zero, the fall after a severe sell-off happens overnight and cannot be captured by selling at the open."]
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_rule.md").write_text("\n".join(L) + "\n")
    J = dict(made=f"{datetime.now():%Y-%m-%d %H:%M}", companies=int(B.ticker.nunique()), companies_with_rule=int(len(per)), companies_8plus=int(len(big)), companies_8plus_below=int((big["mean"] < base).sum()), rule_beat2_old=S[("2005-2017", "sev")][0], rule_beat2_new=S[("2018-2026", "sev")][0], all_beat2_new=S[("2018-2026", "all")][0],
             rule_up2_new=S[("2018-2026", "sev")][2], all_up2_new=S[("2018-2026", "all")][2], days_new=S[("2018-2026", "sev")][1], days_old=S[("2005-2017", "sev")][1], open_to2_bp=T.get("next open -> close two"[:22]), open_to3_bp=T.get("next open -> close three"[:22]), close_to2_bp=T.get("close -> close two sessions"[:22]), by_condition=REG)
    RULE_JSON.write_text(json.dumps(J, indent=1)); print("-> docs/selloff_rule.md, docs/selloff_rule.json")


# ------------------------------------------------------------------ scan: the forward record and the card
def _download(ticks):
    import yfinance as yf
    D = yf.download(ticks, period="2y", interval="1d", auto_adjust=True, group_by="ticker", progress=False, threads=True); out = {}
    for t in ticks:
        try:
            d = D[t].dropna(subset=["Close"])[["Open", "High", "Low", "Close", "Volume"]]; d.columns = ["open", "high", "low", "close", "volume"]; d.index = pd.DatetimeIndex(d.index).tz_localize(None)
            if len(d) > 130: out[t] = d
        except Exception: pass
    return out


def _measure(d, i):
    """the three numbers of the rule for session i of one stock (uses only sessions up to i)"""
    c = d.close; ret = c.pct_change(); vol = float(ret.iloc[i - 61:i - 1].std()); v60 = float(d.volume.iloc[i - 60:i].mean()); r = float(ret.iloc[i])
    return r * 100, (float(d.volume.iloc[i]) / v60 if v60 > 0 else np.nan), (r / vol if vol > 0 else np.nan), float(c.iloc[i - 1] / c.iloc[i - 61] - 1) * 100


def scan(quiet=False, download=None, now=None):
    from src.selloff_study import _stocks
    say = (lambda *a: None) if quiet else print; stocks = _stocks(); P = (download or _download)(stocks + ["SPY"]); now = now or datetime.now(NY)
    if "SPY" not in P: say("  no prices downloaded (network?) -- nothing changed"); return None
    spy = P["SPY"]; last = spy.index[-1]; live = last.date() == now.date() and now.hour * 60 + now.minute < 16 * 60 + 10      # today's bar is not finished
    done = spy.index[:-1] if live else spy.index; F = pd.read_csv(FWD, parse_dates=["day"]) if FWD.exists() else pd.DataFrame(columns=COLS); have = {(r.ticker, r.day) for r in F.itertuples()}; rows = []; falling = []; recent = []; last_rule = None
    for t in stocks:
        d = P.get(t)
        if d is None: continue
        dd = d[d.index.isin(done)]
        for i in range(max(62, len(dd) - 260), len(dd)):
            day = dd.index[i]; mv, vx, sx, run = _measure(dd, i)
            if not (mv <= FALL): continue
            is_rule = bool(vx > VOLX and sx < SIZE); age = int((done > day).sum())
            if is_rule and (last_rule is None or day > last_rule["day"]): last_rule = dict(ticker=t, day=day, move_pct=mv, volume_x=vx)
            if is_rule and age <= 3: recent.append(dict(ticker=t, day=f"{day:%Y-%m-%d}", move_pct=round(mv, 1), volume_x=round(vx, 1), sessions_since=age))
            if day >= START and (t, day) not in have and day in spy.index: rows.append(dict(ticker=t, day=day, rule=int(is_rule), move_pct=round(mv, 2), volume_x=round(vx, 2), size_x=round(sx, 2), run_up_60_pct=round(run, 1), close=round(float(dd.close.iloc[i]), 4), spy_close=round(float(spy.close.loc[day]), 4)))
        if live and d.index[-1] == last and len(d) > 62:
            mv, vx, sx, _ = _measure(d, len(d) - 1)
            if mv <= FALL: falling.append(dict(ticker=t, move_pct=round(mv, 1), volume_x=round(vx, 1), size_ok=bool(sx < SIZE)))
    if rows: F = pd.concat([F, pd.DataFrame(rows)], ignore_index=True)
    for c in COLS:
        if c not in F.columns: F[c] = np.nan
    F["day"] = pd.to_datetime(F["day"]); sd = spy[spy.index.isin(done)]
    for k, r in F.iterrows():      # fill in what followed, once the sessions exist
        d = P.get(r.ticker)
        if d is None or r.day not in d.index or r.day not in sd.index: continue
        d = d[d.index.isin(done)]; i = d.index.get_loc(r.day); j = sd.index.get_loc(r.day); c, s = d.close, sd.close
        for h in (1, 2, 3):
            if i + h < len(d) and j + h < len(sd) and pd.isna(r.get(f"after{h}_vs_spx_bp")): F.at[k, f"after{h}_vs_spx_bp"] = round(((c.iloc[i + h] / c.iloc[i] - 1) - (s.iloc[j + h] / s.iloc[j] - 1)) * 1e4, 1)
        if i + 1 < len(d) and j + 1 < len(sd): F.at[k, "gap_next_open_bp"] = round(((d.open.iloc[i + 1] / c.iloc[i] - 1) - (sd.open.iloc[j + 1] / s.iloc[j] - 1)) * 1e4, 1)
        if i + 2 < len(d) and j + 2 < len(sd): F.at[k, "after2_price_bp"] = round((c.iloc[i + 2] / c.iloc[i] - 1) * 1e4, 1); F.at[k, "open_to2_vs_spx_bp"] = round(((c.iloc[i + 2] / d.open.iloc[i + 1] - 1) - (s.iloc[j + 2] / sd.open.iloc[j + 1] - 1)) * 1e4, 1)
        if i + 3 < len(d) and j + 3 < len(sd): F.at[k, "open_to3_vs_spx_bp"] = round(((c.iloc[i + 3] / d.open.iloc[i + 1] - 1) - (s.iloc[j + 3] / sd.open.iloc[j + 1] - 1)) * 1e4, 1)
    F = F[COLS].sort_values(["day", "ticker"]).reset_index(drop=True); FWD.parent.mkdir(parents=True, exist_ok=True); tmp = FWD.with_suffix(".tmp"); F.to_csv(tmp, index=False); os.replace(tmp, FWD)
    # ---- the tally
    R = F[(F.rule == 1) & F.after2_vs_spx_bp.notna()]; A = F[F.after2_vs_spx_bp.notna()]; byday = R.assign(b=(R.after2_vs_spx_bp > 0).astype(float)).groupby("day").agg(b=("b", "mean"), o=("open_to2_vs_spx_bp", "mean")); nd = len(byday); H = json.loads(RULE_JSON.read_text()) if RULE_JSON.exists() else {}
    tally = dict(days=nd, cases=int(len(R)), beat2=float(byday.b.mean()) if nd else None, open_to2_bp=float(byday.o.mean()) if nd else None, all_cases=int(len(A)), all_beat2=float((A.after2_vs_spx_bp > 0).mean()) if len(A) else None, waiting=int(((F.rule == 1) & F.after2_vs_spx_bp.isna()).sum()))
    L = ["# Severe sell-off rule (SS-1): the forward record", "", f"Registered in TRACK 3.101 on 22 Nov 2026. Counts every case from {START:%d %b %Y}. Rule: a stock of the list closes 5% or more down, on volume above {VOLX} times its 60-session average, with a fall larger than {-SIZE} times its usual daily move. "
         f"Prediction: after such a close the stock beats the S&P 500 over the next 2 sessions LESS often than the 48% of all sell-offs. **Verdict at {VERDICT_AT} separate days** (each day counts once); a second, firmer look at 60. Sell-offs of 5% that do not meet the rule are recorded too, for comparison.", "",
         f"**So far: {nd} separate days with a severe sell-off and a known result ({tally['cases']} cases); {tally['waiting']} waiting for their two sessions.** " + (f"Beat the S&P 500 over 2 sessions: {tally['beat2']:.0%} of days. From the next open to the close two sessions after, against the S&P 500: {tally['open_to2_bp']:+.0f} basis points on average, before cost. " if nd else "") +
         (f"Other sell-offs of 5% (rule not met) with a known result: {tally['all_cases'] - tally['cases']}." if tally["all_cases"] else "") + (f" **{VERDICT_AT - nd} more days to the verdict.**" if nd < VERDICT_AT else " **The verdict is due: see TRACK.**"), "",
         "| day | stock | meets the rule | move % | volume, times normal | fall, times its usual move | against the S&P 500 after 1 / 2 / 3 sessions (bp) | overnight to next open (bp) | next open to close +2 (bp) |", "|---|---|---|---|---|---|---|---|---|"]
    f = lambda x: "" if pd.isna(x) else f"{x:+.0f}"
    L += [f"| {r.day:%Y-%m-%d} | {r.ticker} | {'YES' if r.rule == 1 else 'no'} | {r.move_pct:+.1f} | {r.volume_x:.1f} | {-r.size_x:.1f} | {f(r.after1_vs_spx_bp)} / {f(r.after2_vs_spx_bp)} / {f(r.after3_vs_spx_bp)} | {f(r.gap_next_open_bp)} | {f(r.open_to2_vs_spx_bp)} |" for r in F.sort_values("day", ascending=False).itertuples()]
    if not len(F): L.append("| (no sell-off of 5% or more since the start) | | | | | | | | |")
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_forward.md").write_text("\n".join(L) + "\n")
    cond = None
    try:
        old = json.loads(CARD.read_text()) if CARD.exists() else {}
        if old.get("condition") and old.get("last_close") == f"{done[-1]:%Y-%m-%d}": cond = old["condition"]      # worked out once per finished session (it takes about a minute)
        else:
            lab, names = _regimes()
            if lab is not None and len(lab.dropna()): x = lab.dropna(); cond = dict(name=names.get(int(x.iloc[-1]), f"Condition {int(x.iloc[-1]) + 1} of 4"), day=f"{x.index[-1]:%Y-%m-%d}")
    except Exception: pass
    card = dict(updated=datetime.now(NY).isoformat(), condition=cond, last_close=f"{done[-1]:%Y-%m-%d}", session_open=bool(live), falling=sorted(falling, key=lambda x: x["move_pct"]), recent=sorted(recent, key=lambda x: (x["sessions_since"], x["move_pct"])),
                last_rule=dict(last_rule, day=f"{last_rule['day']:%Y-%m-%d}") if last_rule else None, tally=tally, history=H, stocks=len([t for t in stocks if t in P]))
    CARD.parent.mkdir(parents=True, exist_ok=True); tmp = CARD.with_suffix(".tmp"); tmp.write_text(json.dumps(card, indent=1, default=float)); os.replace(tmp, CARD)
    say(f"  {card['stocks']} stocks priced; last finished session {card['last_close']}; New York session {'OPEN' if live else 'closed'}"); say(f"  severe sell-offs in the last 3 sessions: {', '.join(x['ticker'] + ' ' + x['day'] for x in recent) or 'none'}" + (f"; falling 5% or more right now: {', '.join(x['ticker'] for x in falling) or 'none'}" if live else ""))
    say(f"  forward record: {len(rows)} new sell-offs recorded now; {nd} separate days with a known result, {tally['waiting']} waiting; verdict at {VERDICT_AT} days -> {FWD}, docs/selloff_forward.md"); return card


# ------------------------------------------------------------------ the card on the live page
CARD_CSS = """<style>
.sso-wrap{position:relative;height:0}
.sso{position:absolute;top:2px;right:0;width:310px;z-index:60;border-radius:18px;padding:9px 14px 10px 14px;border:1px solid rgba(255,255,255,.8);outline:1px solid rgba(20,23,31,.08);font-size:.78rem;line-height:1.4;color:#14171F;
     background:linear-gradient(135deg,rgba(255,255,255,.92) 0%,rgba(240,242,246,.86) 55%,rgba(226,229,236,.84) 100%);-webkit-backdrop-filter:blur(18px) saturate(1.15);backdrop-filter:blur(18px) saturate(1.15);box-shadow:0 8px 28px rgba(20,23,31,.09), inset 0 1px 0 rgba(255,255,255,.9);
     transition:transform .18s ease, box-shadow .18s ease}
.sso:hover{transform:translateY(-1px);box-shadow:0 12px 34px rgba(20,23,31,.14), inset 0 1px 0 rgba(255,255,255,.9)}
.sso summary{cursor:pointer;list-style:none;outline:none}.sso summary::-webkit-details-marker{display:none}
.sso-t{font-size:.9rem;font-weight:700;letter-spacing:.01em}.sso-more{float:right;color:#5F6672;font-size:.72rem;margin-top:2px}
.sso-s{display:block;margin-top:1px}.sso-on{outline:2px solid rgba(20,23,31,.55)}
.sso-d{margin-top:8px;padding-top:8px;border-top:1px solid rgba(20,23,31,.10)}.sso-d p{margin:0 0 6px 0}.sso-m{color:#5F6672;font-size:.72rem}
</style>"""


def _refresh_if_stale():
    """the page keeps the card fresh by itself: starts `scan` in the background when the card is older than 15 minutes (New York session) or 60 minutes (otherwise)"""
    import threading
    now = datetime.now(NY); trading = now.weekday() < 5 and 9 * 60 + 30 <= now.hour * 60 + now.minute <= 16 * 60 + 20; limit = 900 if trading else 3600; lock = CARD.with_suffix(".lock")
    age = time.time() - CARD.stat().st_mtime if CARD.exists() else 1e9; tried = time.time() - lock.stat().st_mtime if lock.exists() else 1e9
    if age < limit or tried < 300: return
    try: lock.parent.mkdir(parents=True, exist_ok=True); lock.write_text(str(time.time()))
    except Exception: return
    def job():
        try: scan(quiet=True)
        except Exception: pass
    threading.Thread(target=job, daemon=True).start()


def card_html() -> str:
    try: _refresh_if_stale()
    except Exception: pass
    if not CARD.exists(): return "<div class='sso-wrap'><details class='sso'><summary><span class='sso-t'>Severe Sell-off</span><span class='sso-s sso-m'>Loading prices for the first time (about a minute)…</span></summary></details></div>"
    try: C = json.loads(CARD.read_text())
    except Exception: return ""
    H = C.get("history") or {}; T = C.get("tally") or {}; rec = C.get("recent") or []; fal = C.get("falling") or []; cls = ""; pc = lambda x: f"{x:.0%}"
    if rec: cls = "sso-on"; x = rec[0]; status = "<b>" + ", ".join(f"{r['ticker']} {r['move_pct']:+.1f}%" for r in rec[:3]) + (f" +{len(rec) - 3} more" if len(rec) > 3 else "") + "</b><br>" + (f"closed {x['day']} on {x['volume_x']:.1f}× volume · " if len(rec) == 1 else "") + "candidate rule, not a tested trade"
    elif fal: cls = "sso-on"; status = "<b>Falling 5%+ now: " + ", ".join(f"{r['ticker']} {r['move_pct']:+.1f}%" for r in fal[:3]) + (f" +{len(fal) - 3}" if len(fal) > 3 else "") + "</b><br>counts only if it holds at the close"
    else: lr = C.get("last_rule"); status = "None in the last 3 sessions." + (f"<br><span class='sso-m'>Last one: {lr['ticker']} {lr['move_pct']:+.1f}% on {lr['day']}</span>" if lr else "")
    d = []
    for r in rec: d.append(f"<p><b>{r['ticker']}</b> closed {r['move_pct']:+.1f}% on {r['day']}, on {r['volume_x']:.1f} times its normal volume · {r['sessions_since']} of 3 sessions gone.</p>")
    if rec and fal: d.append("<p>Falling 5% or more right now (not counted until the close): " + ", ".join(f"{r['ticker']} {r['move_pct']:+.1f}%" for r in fal[:6]) + ".</p>")
    if H.get("rule_beat2_new") is not None: d.append(f"<p><b>History (2018–2026, {H['days_new']:.0f} days):</b> after a severe sell-off the stock beat the S&P 500 over the next 2 sessions {pc(H['rule_beat2_new'])} of the time, against {pc(H['all_beat2_new'])} after any sell-off of 5%. Its price was higher after 2 sessions {pc(H['rule_up2_new'])} of the time (any sell-off: {pc(H['all_up2_new'])}).</p>" +
                                                     (f"<p>From the next open to the close two sessions later, against the S&P 500: {H['open_to2_bp']:+.0f} basis points on average, before cost.</p>" if H.get("open_to2_bp") is not None else ""))
    else: d.append("<p><b>History:</b> in the pattern search (2018–2026) stocks that fell 5% or more on heavy volume beat the S&P 500 over the next 2 sessions about 33–38% of the time, against 48% after any sell-off of 5%.</p>")
    cd = C.get("condition"); bc = (H.get("by_condition") or {}).get((cd or {}).get("name"))
    if cd: d.append(f"<p><b>Market condition (main page) on {cd['day']}:</b> {cd['name']}." + (f" In this condition, after a severe sell-off the stock beat the S&P 500 over 2 sessions {pc(bc['rule'])} of the time, against {pc(bc['all'])} after any sell-off of 5% ({bc['days']:.0f} days)." if bc and bc.get("rule") == bc.get("rule") else "") + "</p>")
    d.append("<p><b>No colour on purpose:</b> on this page red, yellow and green belong to tested rules only. This rule is a candidate until its forward record reaches 30 days.</p>")
    d.append("<p><b>Rule:</b> a stock of the list closes 5% or more down, on volume above 1.98 times its 60-session average, with a fall larger than 2.72 times its usual daily move. The card shows it for 3 sessions.</p>")
    d.append(f"<p><b>Forward record:</b> {T.get('days', 0)} of {VERDICT_AT} days counted" + (f"; beat the S&P 500 over 2 sessions on {pc(T['beat2'])} of them" if T.get("beat2") is not None else "") + ". Candidate, not a tested trade: the verdict comes at 30 live days.</p>")
    try: up = datetime.fromisoformat(C["updated"]); d.append(f"<p class='sso-m'>{C.get('stocks', 0)} large US stocks · daily prices from Yahoo · last finished session {C.get('last_close')} · checked {up:%d %b %H:%M} New York</p>")
    except Exception: pass
    return f"<div class='sso-wrap'><details class='sso {cls}'><summary><span class='sso-t'>Severe Sell-off</span><span class='sso-more'>details ▾</span><span class='sso-s'>{status}</span></summary><div class='sso-d'>{''.join(d)}</div></details></div>"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["describe", "scan"]); a = ap.parse_args()
    cmd_describe() if a.cmd == "describe" else scan()
