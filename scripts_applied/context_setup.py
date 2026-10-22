"""
TRACK §3.23 — the Context block (16 Oct). Run from the repo root:  python context_setup.py
  1. src/context.py — builds the four-paragraph Context block for a model asset or any ticker, every sentence with its status tag,
     from files already on disk (regime profile + labels, outputs/blindspot/*.json, outputs/event_time/*.json, processed/oil_shocks.csv,
     processed/oil_tail.json, processed/oil_inverse_forward.csv, processed/chain_forward.csv, the referee scoreboard).
  2. src/blindspot.py — chain firings get their own forward row (processed/chain_forward.csv): gold's 20/60-session return filled
     when matured, so the count toward A2's 10 is visible without a backfill rerun.
  3. app.py — Context under each market's detail view, a "Context, in words" section on Today (one expander per market),
     and under the searched ticker on "Look up an asset". Nothing else on the page changes.
Then:  python -m src.context selftest ; python -m src.context show GLD ; streamlit run app.py (look), commit.
"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. src/context.py
ctx = Path("src/context.py")
if ctx.exists(): print("  src/context.py: already")
else:
    ctx.write_text(r'''"""
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


def referee():
    bf = sorted(PROC.glob("report_scoreboard_backfill_*.json"), key=lambda p: p.stat().st_mtime)
    if not bf: return None
    j = _j(bf[-1]) or {}; h = j.get("primary_h", 2); cell = ((j.get("cells") or {}).get(f"h{h}_primary") or {}); no = cell.get("nonoverlap") or {}
    return dict(hit=no.get("hit"), q95=no.get("null_q95") or cell.get("null_q95"), asym=no.get("asym"), n=no.get("n"), h=h)


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
    try:
        import yfinance as yf
        d = yf.Ticker(tk).history(period="max", interval="1d", auto_adjust=False)
        if d.empty: return None
        px = d["Close"]; px.index = pd.to_datetime(px.index).tz_localize(None); r = np.log(px).diff().dropna()
    except Exception:
        return None
    rows = []
    for ds in dates:
        t = pd.Timestamp(ds)
        if t < r.index[0] or t > r.index[-1]: continue
        i = r.index.searchsorted(t)
        if i + 60 >= len(r): continue
        seg = r.iloc[i + 1:i + 61]; cum = seg.cumsum()
        rows.append(dict(f20=float(seg.iloc[:20].sum()), f60=float(seg.sum()), worst=float(min(cum.min(), 0)), worst_t=int(cum.argmin()) + 1))
    return pd.DataFrame(rows) if rows else None


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
        s1.append(f"Today's scheduled release <b>{r['event_type'].split(':')[1]}</b>: {h.get('value')} ({h.get('unit')}), "
                  f"{'above' if (su or 0) > 0 else 'below'} the last print by {abs(su):.1f} {tag('measured')}.")
    if s1: P.append(("Where we are", " ".join(s1)))

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
    rf = referee()
    if rf and rf.get("hit") is not None:
        s2.append(f"The engine's own two-session direction calls, across all five markets on the 1,532-day backfill: hit-rate {rf['hit']:.1%} against a "
                  f"chance level of {rf['q95']:.1%}, asymmetry {rf['asym']:.2f} (how much a right call pays against what a wrong one costs; 1.0 = even), "
                  f"{rf['n']} non-overlapping calls {tag('tested: below chance')}.")
    if s2: P.append(("What history says in this environment", " ".join(s2)))

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
    if "chain" in fc: s4.append(f"Chain alarm → gold: {fc['chain'][0]} firing(s) logged forward since 13 Oct 2026, {fc['chain'][1]} matured; the rule needs ten {tag('running')}.")
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
        day = a.day or sorted(glob.glob("outputs/reports/*.json"))[-1].split("/")[-1][:10]
        prof = _j("processed/regime_profile.json")
        html = context_block(a.asset if a.asset in MODEL else None, day, prof=prof, ticker=None if a.asset in MODEL else a.asset)
        print(re.sub(r"<[^>]+>", "", html.replace("</p>", "\n\n").replace("rs-ctx-h", "")).strip())
''')
    print("  src/context.py: written")

# ---------------------------------------------------------------- 2. chain forward rows in blindspot --today
p = Path("src/blindspot.py"); s = p.read_text()
if "chain_forward.csv" in s: print("  blindspot chain forward: already")
else:
    old = '''    f.write_text(json.dumps(rec, indent=2))
    flagged = {a: s for a, s in rec["states"].items() if s}'''
    new = '''    f.write_text(json.dumps(rec, indent=2))
    # chain firings get a forward row (TRACK 3.23): gold's 20/60-session return filled when matured; counts toward A2's ten
    CF = PROC / "chain_forward.csv"
    cf = pd.read_csv(CF, parse_dates=["fire_date"]) if CF.exists() else pd.DataFrame(columns=["fire_date", "logged_at", "pos", "provisional", "gld_f20", "gld_f60", "matured_at"])
    i = len(rets.index) - 1
    if alert and (cf.empty or (i - int(cf.pos.max())) > 5):
        cf = pd.concat([cf, pd.DataFrame([dict(fire_date=rets.index[i], logged_at=datetime.now().strftime("%Y-%m-%d %H:%M"), pos=i, provisional=provisional,
                                               gld_f20=np.nan, gld_f60=np.nan, matured_at="")])], ignore_index=True)
        print(f"chain forward: firing logged {rets.index[i].date()}{' (provisional)' if provisional else ''}")
    for j, r in cf.iterrows():
        p0 = int(r.pos)
        if pd.isna(r.gld_f20) and p0 + 20 <= i: cf.loc[j, "gld_f20"] = float(rets["GLD"].iloc[p0 + 1:p0 + 21].sum())
        if pd.isna(r.gld_f60) and p0 + 60 <= i: cf.loc[j, ["gld_f60", "matured_at"]] = [float(rets["GLD"].iloc[p0 + 1:p0 + 61].sum()), rets.index[i].strftime("%Y-%m-%d")]
    cf.to_csv(CF, index=False)
    flagged = {a: s for a, s in rec["states"].items() if s}'''
    if old not in s: sys.exit("  blindspot anchor not found -- stopped")
    p.write_text(s.replace(old, new, 1)); print("  blindspot chain forward: done")

# ---------------------------------------------------------------- 3. app.py
a = Path("app.py"); s = a.read_text()
if "from src.context import context_block" in s: print("  app.py: already")
else:
    # import + css after the referee_numbers definition block (safe anchor: def plain_reason)
    s = s.replace("def plain_reason(raw, e=None):", "from src.context import context_block, CSS as CTX_CSS\nst.markdown(CTX_CSS, unsafe_allow_html=True)\n\n\ndef plain_reason(raw, e=None):", 1)
    # detail view: after the Rest-of-session banner (end of detail_dashboard)
    old = "Intraday bars are being collected every session for the markets that have no history yet.</p></div>', unsafe_allow_html=True)\n"
    if old not in s: sys.exit("  app detail anchor not found -- stopped")
    s = s.replace(old, old + "    st.markdown(context_block(a, day, prof=load_profile(), reg=reg, R=R), unsafe_allow_html=True)\n", 1)
    # Today overview: after the cards' footnote
    old = "'says which. The signal pill and its reason are for the selected report day.</div>', unsafe_allow_html=True)\n"
    if old not in s: sys.exit("  app today anchor not found -- stopped")
    s = s.replace(old, old + "        st.markdown('<div class=\"rs-section\">Context, in words — each market</div>', unsafe_allow_html=True)\n"
                             "        for _i, _a in enumerate(R['assets']):\n"
                             "            with st.expander(f\"{DISPLAY[_a]['name']} — the environment, what history says here, the severe case\", expanded=(_i == 0)):\n"
                             "                st.markdown(context_block(_a, day, prof=prof, reg=reg, R=R).replace('<div class=\"rs-section\">Context, in words</div>', ''), unsafe_allow_html=True)\n", 1)
    # Look-up tab: after the market-level-read footnote
    old = "f'{tk}\\'s own industry, so treat this as a market-level read, not a company-level one.</div>', unsafe_allow_html=True)\n"
    if old not in s: sys.exit("  app lookup anchor not found -- stopped")
    s = s.replace(old, old + "        st.markdown(context_block(tk if tk in ('SPY','TLT','GLD','UUP','USO') else None, lday, prof=load_profile(), reg=load_regimes(), ticker=tk), unsafe_allow_html=True)\n", 1)
    a.write_text(s); print("  app.py: Context block wired (detail, Today, Look up)")
print("done -- python -m src.context selftest ; python -m src.context show GLD")
