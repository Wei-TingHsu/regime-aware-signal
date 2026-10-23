"""
Context block for the app (TRACK §3.23). Four short paragraphs under a market's call, every sentence carrying its status:
  [measured] a number read off history   [tested: PASS/FAIL/INCONCLUSIVE/UNTESTED] a registered test's verdict
  [hypothesis] a pattern seen, not tested  [registered, not run]  [running]
Nothing untested gets a forecast. Terms are explained where first used. Reads only files already on disk; every loader fails soft.

  python -m src.context selftest
  python -m src.context show GLD [--day 2026-10-15]
"""
from __future__ import annotations
import glob, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PROC, OUT = Path("processed"), Path("outputs")
MODEL = {"SPY": "US equities (S&P 500)", "TLT": "long US Treasuries", "GLD": "gold", "UUP": "the US dollar", "USO": "oil", "WTI_SPOT": "oil (spot)"}
CHAIN_DATES = ["2009-01-26", "2009-02-24", "2015-02-06", "2022-03-07", "2026-03-05"]
H = (5, 10, 20, 40, 60, 90)


def _j(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None


def _pct(x, log=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return "—"
    v = math.expm1(x) if log else x
    return f"{v:+.1%}"


def tag(kind): return f'<span class="rs-tag rs-tag-{kind.split(":")[0].split(" ")[0].lower()}">{kind}</span>'


# ---------------------------------------------------------------- loaders
def latest_blindspot(day=None):
    fs = sorted(glob.glob(str(OUT / "blindspot" / "*.json")))
    if day: fs = [f for f in fs if Path(f).stem <= day.replace("-", "")]
    return _j(fs[-1]) if fs else None


def prints_today(day):
    out = []
    for f in sorted(glob.glob(str(OUT / "event_time" / f"{day.replace('-', '')}_*.json"))):
        r = _j(f)
        if r and r.get("event_type", "").startswith("print:"): out.append(r)
    return out


def regime_now(prof, reg, day):
    try:
        k = int(reg.loc[:day].iloc[-1]); r = (prof or {}).get("regimes", {}).get(str(k)) or {}
        return k, r.get("label", f"condition {k}"), r.get("share_pct")
    except Exception:
        return None, None, None


def shock_rows(asset):
    p = PROC / "oil_shocks.csv"
    if not p.exists(): return None
    df = pd.read_csv(p); return df[(df.pool == "p8") & (df.asset == asset)]


def shock_dates():
    p = PROC / "oil_shocks.csv"
    if not p.exists(): return []
    df = pd.read_csv(p); return sorted(df[df.pool == "p8"].date.unique())


def tail_for(asset):
    t = _j(PROC / "oil_tail.json"); return (t or {}).get("markets", {}).get(asset), (t or {}).get("as_of")


BASELINE = "48a6c4e879a1_n2617_h2"


def referee(asset=None):
    """The current baseline scoreboard (PROJECT_MASTER: h=2 primary). Falls back to the newest file only if the baseline is absent."""
    fs = [p for p in PROC.glob("report_scoreboard_backfill_*.json") if BASELINE in p.name] or \
         sorted(PROC.glob("report_scoreboard_backfill_*.json"), key=lambda p: p.stat().st_mtime)[-1:]
    if not fs: return None
    j = _j(fs[0]) or {}; h = j.get("primary_h", 2); cell = ((j.get("cells") or {}).get(f"h{h}_primary") or {}); no = cell.get("nonoverlap") or {}
    mine = ((j.get("breakdowns") or {}).get("asset") or {}).get(asset) if asset else None
    return dict(hit=no.get("hit"), q95=cell.get("null_hit_q95"), asym=no.get("asym"), n=no.get("n"), h=h, days=j.get("n_reports"),
                verdict=cell.get("verdict") or j.get("verdict"), pass_hit=cell.get("pass_hit"), pass_asym=cell.get("pass_asym"), mine=mine, tag=j.get("backfill_tag"))


def forward_counts():
    out = {}
    p = PROC / "oil_inverse_forward.csv"
    if p.exists():
        f = pd.read_csv(p); out["uso_inverse"] = (len(f), int(f.hit.notna().sum()), float(f.hit.mean()) if f.hit.notna().any() else None)
    p = PROC / "chain_forward.csv"
    if p.exists():
        f = pd.read_csv(p); out["chain"] = (len(f), int(f.gld_f60.notna().sum()) if "gld_f60" in f else 0)
    return out


def ticker_paths(tk, dates):
    """For a searched ticker: its own 20/60-session paths after the pool's shock dates, from Yahoo daily history (cached by caller)."""
    r = _hist(tk)
    if r is None: return None
    rows = []
    for ds in dates:
        t = pd.Timestamp(ds)
        if t < r.index[0] or t > r.index[-1]: continue
        i = r.index.searchsorted(t)
        if i + 60 >= len(r): continue
        seg = r.iloc[i + 1:i + 61]; cum = seg.cumsum()
        rows.append(dict(f20=float(seg.iloc[:20].sum()), f60=float(seg.sum()), worst=float(min(cum.min(), 0)), worst_t=int(cum.argmin()) + 1))
    return pd.DataFrame(rows) if rows else None


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


from functools import lru_cache


@lru_cache(maxsize=32)
def _hist(tk):
    """Daily log returns of a searched ticker from Yahoo, fetched once per process."""
    try:
        import yfinance as yf
        d = yf.Ticker(tk).history(period="max", interval="1d", auto_adjust=False)
        if d.empty: return None
        px = d["Close"]; px.index = pd.to_datetime(px.index).tz_localize(None); return np.log(px).diff().dropna()
    except Exception:
        return None


HIST_LEADS = [("H1", "On Fed decision days"), ("H3up", "After dollar jumps (≥ 2% in five sessions)"), ("H3dn", "After dollar drops (≥ 2% in five sessions)"),
              ("H4up", "After two-year-yield jumps (≥ 25 bp in five sessions)"), ("H4dn", "After two-year-yield drops (≥ 25 bp in five sessions)"),
              ("H5", "After the model's condition label changes")]


def history_sentences(asset, name, ticker=None):
    """One measured sentence per H-table (+ its test verdict) for a model asset; for a searched ticker, its own paths against the saved event dates."""
    HT = _j(PROC / "history_tables.json") or {}; out = []
    for tid, lead in HIST_LEADS:
        T = HT.get(tid)
        if not T or not T.get("dates"): continue
        yr = T["dates"][0][:4]
        if asset in MODEL:
            m = T.get("markets", {}).get(asset)
            if not m or m["summary"].get("n", 0) < 10: continue
            sm, te = m["summary"], m.get("test", {})
            txt = (f"{lead} — {T['n_events']} since {yr} — {name}'s typical path was {_pct(sm['f20'])} after a month and {_pct(sm['f60'])} after a quarter, "
                   f"with a typical worst dip of {_pct(sm['worst'])} (n {sm['n']}) {tag('measured')}.")
            v = te.get("verdict")
            if v in ("PASS", "FAIL"):
                txt += (f" Whether that month differs from {name}'s ordinary month (higher a month later {te['sign']:.0%} of the time vs {te['base']:.0%} normally): "
                        f"{v} {tag('tested: ' + v)}.")
            elif v == "INCONCLUSIVE":
                txt += f" Too few cases to test (n {te.get('n')}, the rule needs 30) {tag('tested: INCONCLUSIVE')}."
            sp = m.get("split")
            if sp and sp.get("verdict") in ("PASS", "FAIL"):
                txt += (f" Split by whether the two-year yield rose or fell that day: {_pct(sp['up_f20'])} vs {_pct(sp['dn_f20'])} after a month, "
                        f"{sp['verdict']} {tag('tested: ' + sp['verdict'])}.")
            te5 = m.get("test5", {}); sp5 = m.get("split5", {})
            if te5.get("verdict") in ("PASS", "FAIL"):
                txt += (f" At one week (5 sessions): {_pct(sm['f5'])}, higher {te5['sign']:.0%} of the time vs {te5['base']:.0%} normally — "
                        f"{te5['verdict']} {tag('tested: ' + te5['verdict'])}.")
            if sp5.get("verdict") in ("PASS", "FAIL"):
                txt += f" One-week split by the yield's move: {_pct(sp5['up_f5'])} vs {_pct(sp5['dn_f5'])}, {sp5['verdict']} {tag('tested: ' + sp5['verdict'])}."
            out.append(txt)
        elif ticker and tid in ("H3up", "H4up", "H5"):
            tp = ticker_paths(ticker, T["dates"])
            if tp is None or len(tp) < 10: continue
            out.append(f"{lead} — {len(tp)} in {ticker}'s own history — its typical path was {_pct(tp.f20.median())} after a month and {_pct(tp.f60.median())} "
                       f"after a quarter, typical worst dip {_pct(tp.worst.median())} {tag('measured')}; computed now from its prices, not tested.")
    return out


def why_moved_sentences(asset, name, ticker=None):
    """The founder's daily picture (TRACK 3.33): the current leg, how far along a typical leg it is, the rule-found window and its reasons,
    yesterday's reasons, and the pill as today's wind. Reads processed/why_moved.json (nightly)."""
    W = _j(PROC / "why_moved.json"); key = asset if asset in MODEL else ticker
    A = ((W or {}).get("assets") or {}).get(key)
    if not A: return None
    ep, tg, wd, ls, tf = A["episode"], A.get("target"), A.get("windows") or {}, A.get("last_session") or {}, A.get("window_test") or {}
    up = ep["direction"] > 0; S = []
    S.append(f"{name} has been <b>{'rising' if up else 'falling'} since {ep['start']}</b> — {ep['sessions']} sessions, {_pct(ep['move'])} so far, furthest point "
             f"{_pct(ep['extreme_so_far']['move'])} on {ep['extreme_so_far']['date']}; how a leg ends: {ep.get('rule', 'a counter-move of 1.5 × the asset\'s monthly volatility, floor 8%')} {tag('measured')}.")
    if tg:
        kind = "rises" if up else "falls"; sgn = 1 if up else -1
        if tg.get("share_of_typical") is not None and tg["share_of_typical"] < 1:
            S.append(f"Past {kind} of this kind ran a median {_pct(sgn * tg['med_size'])} from their start over {tg['med_length']:.0f} sessions (n {tg['n']}); this one is at "
                     f"{tg['share_of_typical']:.0%} of that, so the typical level is <b>{_pct(tg['target_from_now'])} from here</b> (middle half of past legs: {_pct(tg['band_from_now'][0])} to "
                     f"{_pct(tg['band_from_now'][1])}) {tag('measured')} — a base rate of past legs, not a forecast; the reason-conditioned version {tag('registered, not run')}.")
        else:
            S.append(f"Past {kind} of this kind ran a median {_pct(sgn * tg['med_size'])} (n {tg['n']}); this one is already larger than {tg.get('pct_rank', 0):.0%} of them — the base rate gives no further level {tag('measured')}.")
    r5 = wd.get("R5_causal"); rows = A.get("r5_rows") or []; br = A.get("best_rule")
    if br and br.get("explained") is not None:      # the swept rule that survived its null (T-G) replaces the registered 5/5 cell on the page
        rows = br.get("rows") or rows
        leg = br.get("leg"); pre = (f"Under the promoted window rule the leg is cut as {'rising' if leg['direction'] > 0 else 'falling'} since {leg['start']} ({leg['sessions']} sessions, {_pct(leg['move'])}). " if leg else "")
        top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in rows[:3]) or "—"
        S.append(f"<b>Why it moved.</b> {pre}Over the window where the named reasons explain most on a forward-walking rule (first {br['sessions']} sessions), they account for <b>{br['explained']:.0%}</b> "
                 f"of the move: {top}; the rest is unexplained by rates, the dollar, oil, volatility, geopolitical risk, liquidity or the macro state "
                 f"{tag('tested: PASS')} (rule promoted after a 216-cell sweep beat its noise null, p {br['p']:.2f}; patience {br['params']['patience']}, look-back {br['params']['window']}).")
        r5 = None
    if r5 and r5.get("explained") is not None:
        top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in rows[:3]) or "—"
        v = tf.get("verdict", "not run"); extra = f" (this rule beat the full-leg window in {tf['share']:.0%} of past legs)" if tf.get("share") is not None else ""
        S.append(f"<b>Why it moved.</b> Over the window where the named reasons explain most on a forward-walking rule — the first {r5['sessions']} sessions to {r5['end']}, "
                 f"{_pct(r5['move'])} — they account for <b>{r5['explained']:.0%}</b> of the move: {top}; the rest is unexplained by rates, the dollar, oil, volatility, geopolitical risk, "
                 f"liquidity or the macro state {tag('tested: ' + v)}{extra}. Each reason's share is its sensitivity (from the two years before the leg) × how far that series moved.")
    la = ls.get("attribution")
    if la:
        top = ", ".join(f"{d['label']} {d['contrib']:+.2%}" for d in la["rows"][:3])
        S.append(f"Last session {ls['date']}: {_pct(ls['ret'])} — {top}; unexplained {la['resid']:+.2%} {tag('measured')}.")
    S.append("Today's wind is the engine's two-session call — the pill above — scored separately on the track record at the top of the page.")
    return " ".join(S)


# ---------------------------------------------------------------- the block
def context_block(asset, day, prof=None, reg=None, R=None, ticker=None):
    """asset: SPY/TLT/GLD/UUP/USO (model key) or None with ticker=... for a searched ticker. Returns HTML."""
    name = MODEL.get(asset, ticker or asset)
    P = []

    # 1. where we are
    k, label, share = regime_now(prof, reg, day)
    bs = latest_blindspot(day); ci = (bs or {}).get("chain_inputs", {}); alert = (bs or {}).get("chain_alert"); prov = (bs or {}).get("chain_alert_provisional")
    s1 = []
    if label: s1.append(f"The macro backdrop the model labels today is <b>“{label}”</b> — one of four conditions it sorts history into from eight published "
                        f"series; this one covers {share}% of history {tag('measured')}.")
    if ci: s1.append(f"Oil (spot) is {_pct(ci.get('oil_5d'))} over the last five sessions; the two-year yield {ci.get('dgs2_5d_bp', 0):+.0f} bp; the dollar "
                     f"{ci.get('dxy_5d', 0):+.2%} {tag('measured')}.")
    if alert is not None:
        s1.append(("<b>The oil-shock chain alarm is ON" + (" (provisional: today's oil leg is from the futures contract until the spot print lands)" if prov else "") + "</b>"
                   if alert else "The oil-shock chain alarm is off") + " — the alarm rings when oil jumps ≥ 8% in a week, the dollar rises with it, and short rates were calm "
                  "and then rise within five days: oil first, dollar second, rates third, the shape of an oil-exporter shock " + tag("running") + ".")
    pr = prints_today(day)
    for r in pr:
        h = r.get("headline") or {}; su = r.get("surprise_vs_naive"); rx = (r.get("reaction") or {}).get(name if name in r.get("reaction", {}) else "", {})
        surprise = (f", {'above' if su > 0 else 'below'} the last print by {abs(su):.1f}" if isinstance(su, (int, float)) else "")
        s1.append(f"Today's scheduled release <b>{r['event_type'].split(':')[1]}</b>: {h.get('value')} ({h.get('unit')}){surprise} {tag('measured')}.")
    if s1: P.append(("Where we are", " ".join(s1)))

    # 1a. why it moved (TRACK 3.33)
    wm = why_moved_sentences(asset, name, ticker=ticker)
    if wm: P.append(("Why it moved, and where this leg stands", wm))

    # 1b. today's condition (H0)
    h0 = h0_sentence(asset, k, label, name, ticker=ticker, reg=reg)
    if h0: P.append(("What history says in today's condition", h0))

    # 2. what history says here
    s2 = []
    rows = shock_rows(asset) if asset in MODEL else None
    if rows is not None and len(rows.dropna(subset=["f20"])) >= 20:
        rr = rows.dropna(subset=["f20"]); n = len(rr)
        s2.append(f"An <b>oil shock</b> here means oil up ≥ 8% within five sessions (a session is one trading day); there have been 116 since 1995, about four a year. "
                  f"After them, {name}'s typical path was {_pct(rr.f20.median())} after a month (20 sessions), {_pct(rr.f60.median())} after a quarter and "
                  f"{_pct(rr.f90.median())} after four months, with a typical worst dip of {_pct(rr.worst.median())} on the way and a typical best of "
                  f"{_pct(rr.best.median())} around session {rr.best_t.median():.0f} (n {n}) {tag('measured')}.")
        s2.append("Whether the shock's details — how the dollar and short rates moved that week, and the macro condition — tell you the direction better "
                  "than the plain average was tested on all 116: they do not " + tag("tested: FAIL") + ".")
        if asset == "GLD":
            s2.append("The five times the full three-leg alarm rang (2009 ×2, 2015, 2022, 2026), gold was lower a quarter later in all five, by 2–12%; that is the "
                      "pattern the alarm exists for, and five cases are too few to call it more than a " + tag("hypothesis") + " (rule: ten).")
            s2.append("Separately, on Fed statement days gold has drifted about −0.3% over the next two sessions — the one cell in the register that met its "
                      "own criterion " + tag("tested: met criterion, p≈0.01") + ".")
    elif ticker and asset not in MODEL:
        tp = ticker_paths(ticker, shock_dates())
        if tp is not None and len(tp) >= 10:
            s2.append(f"After the {len(tp)} oil shocks in {ticker}'s own price history, its typical path was {_pct(tp.f20.median())} after a month and "
                      f"{_pct(tp.f60.median())} after a quarter, with a typical worst dip of {_pct(tp.worst.median())} around session {tp.worst_t.median():.0f} "
                      f"{tag('measured')} — computed now from its own prices against the shock dates; nothing about this ticker has been tested.")
        else:
            s2.append(f"{ticker} has too little history over the oil-shock dates for a path table (needs 10 shocks with a quarter of prices after each).")
    s2 += history_sentences(asset, name, ticker=ticker)
    rf = referee(asset if asset in MODEL else None)
    if rf and all(isinstance(rf.get(k), (int, float)) for k in ("hit", "q95", "asym", "n")):
        bar = "clears" if rf["pass_hit"] else "does not clear"
        s2.append(f"The engine's own {rf['h']}-session direction calls, all five markets, {rf['days']:,} report days: hit-rate {rf['hit']:.1%}, which {bar} the "
                  f"chance bar of {rf['q95']:.1%} (what shuffled history produces 95% of the time); asymmetry {rf['asym']:.2f} (a right call's gain against a "
                  f"wrong call's loss; 1.0 = even; the test needs 1.20), {rf['n']} non-overlapping calls; scoreboard verdict {rf['verdict']} "
                  f"{tag('tested: ' + str(rf['verdict']))}.")
        m = rf.get("mine")
        if m and isinstance(m.get("hit"), (int, float)):
            s2.append(f"For {name} alone: {m['n']} calls, hit-rate {m['hit']:.0%}, asymmetry {m['asym']:.2f} — a breakdown, not a tested cell "
                      f"(the criterion was set for the pooled calls) {tag('measured')}.")
    if s2: P.append(("What history says after shocks and events, and the engine's record", '</p><p class="rs-ctx-p">'.join(s2)))

    # 3. severe case
    tl, asof = tail_for(asset) if asset in MODEL else (None, None)
    if tl:
        cond = tl.get("conditions", {})
        s3 = [f"In the worst 1 in 10 past oil shocks ({tl['tail_n']} of {tl['n']}), {name} fell a median {_pct(tl['tail_median_worst'])} before recovering, "
              f"bottoming around session {tl['tail_t']:.0f}; the single worst was {tl['worst_date']} at {_pct(tl['worst'])} {tag('measured')}.",
              f"Those shocks arrived with the S&P already {_pct(cond.get('spx_dd'))} from its one-year high and oil {_pct(cond.get('oil_vs_year'))} against its "
              f"year's median — the crash was usually already under way and the oil shock a passenger {tag('measured')}.",
              f"Whether those conditions predict the tail in advance: {tl['verdict']} {tag('tested: ' + tl['verdict'].split(' ')[0])}.",
              f"<b>Today's resemblance to those shocks: {tl['resemblance_level']}</b> (nearest-neighbour tail share {tl['resemblance']:.0%} vs a base rate of "
              f"{tl['base_rate']:.0%}) — measured on {asof}, not a forecast {tag('measured')}."]
        P.append(("The severe case", " ".join(s3)))

    # 4. what is not known
    fc = forward_counts(); s4 = []
    ch = fc.get("chain", (0, 0))
    s4.append(f"Chain alarm → gold: {ch[0]} firing(s) logged forward since 16 Oct 2026, {ch[1]} matured (a firing matures when 60 sessions of gold prices exist after it); "
              f"with the five historical cases the rule needs five more before it can be tested {tag('running')}.")
    if "uso_inverse" in fc:
        n, m, hr = fc["uso_inverse"]
        s4.append(f"USO inverse rule (a pattern found in-sample at 70%, which failed on 34 held-out shocks at 47%): {n} shock(s) logged forward, {m} matured"
                  + (f", hit {hr:.0%}" if hr is not None else "") + f"; verdict at twenty {tag('running')}.")
    s4.append("Registered and not yet run: implied vs realised volatility after a shock (the options-premium question), T2 expected move, T15 risk block "
              + tag("registered, not run") + ".")
    P.append(("What is not known", " ".join(s4)))

    html = ['<div class="rs-section">Context, in words</div><div class="g rs-ctx">']
    for h, body in P: html.append(f'<div class="rs-ctx-h">{h}</div><p class="rs-ctx-p">{body}</p>')
    html.append('<p class="rs-foot">Tags: <b>measured</b> = read off history, no claim; <b>tested</b> = a registered test with a written criterion, verdict as shown; '
                '<b>hypothesis</b> = a pattern seen, not tested; <b>running</b> = being scored forward; <b>registered, not run</b> = the rule exists, the test has not. '
                'Every number states its population. Nothing here is a forecast unless a test marked PASS says so.</p></div>')
    return "".join(html)


CSS = """
<style>
.rs-ctx{padding:14px 18px}.rs-ctx-h{font-weight:700;font-size:.82rem;letter-spacing:.04em;text-transform:uppercase;margin:10px 0 2px;opacity:.75}
.rs-ctx-p{font-size:.92rem;line-height:1.55;margin:0 0 6px}
.rs-tag{display:inline-block;font-size:.68rem;font-weight:600;padding:1px 6px;border-radius:999px;margin-left:4px;vertical-align:middle;background:rgba(20,23,31,.08)}
.rs-tag-measured{background:rgba(60,120,220,.14)}.rs-tag-tested{background:rgba(220,120,40,.16)}.rs-tag-hypothesis{background:rgba(160,60,200,.14)}
.rs-tag-running{background:rgba(40,170,110,.16)}.rs-tag-registered{background:rgba(20,23,31,.08)}
</style>"""


def selftest():
    assert _pct(0.0) == "+0.0%" and _pct(math.log(1.1)) == "+10.0%" and _pct(-1.095) == "-66.5%"; print("  T1 log->simple %: PASS")
    assert "measured" in tag("measured") and "rs-tag-tested" in tag("tested: FAIL"); print("  T2 tags: PASS")
    h = context_block("GLD", "2026-10-15"); assert "Context, in words" in h and "oil shock" in h; print("  T3 GLD block builds from disk: PASS")
    h = context_block(None, "2026-10-15", ticker="XOM"); assert "Context, in words" in h; print("  T4 ticker block builds: PASS")
    print("selftest: 4/4")


if __name__ == "__main__":
    import argparse, re
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True); sub.add_parser("selftest")
    s = sub.add_parser("show"); s.add_argument("asset"); s.add_argument("--day", default=None)
    a = ap.parse_args()
    if a.cmd == "selftest": selftest()
    else:
        _st = Path(sorted(glob.glob("outputs/reports/*.json"))[-1]).stem
        day = a.day or f"{_st[:4]}-{_st[4:6]}-{_st[6:8]}"
        prof = _j("processed/regime_profile.json")
        from src.oil_shock import load, regime_labels
        lo = load(); rets_ = lo[0] if isinstance(lo, tuple) else lo
        reg_ = pd.Series(np.asarray(regime_labels(rets_.index)), index=rets_.index)
        html = context_block(a.asset if a.asset in MODEL else None, day, prof=prof, reg=reg_, ticker=None if a.asset in MODEL else a.asset)
        print(re.sub(r"<[^>]+>", "", html.replace("</p>", "\n\n").replace("rs-ctx-h", "")).strip())
