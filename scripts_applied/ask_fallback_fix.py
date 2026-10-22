"""22 Oct: price fallback tries Yahoo's short-window request first, then Stooq with a browser header; `ask` computes any target exactly and prints
the levels history gives a 1-in-2 / 1-in-3 / 1-in-10 chance of touching; the calibration check reads verdict cells, not the header.
Run from the repo root:  python ask_fallback_fix.py ; python -m src.price_fallback ; python -m src.target_range ask GLD --price 4090 --target 4500 5000 5400"""
from pathlib import Path

# ---- fallback
p = Path("src/price_fallback.py"); s = p.read_text()
if "yahoo-10d" in s: print("  fallback: already")
else:
    old = s[s.index("    filled = []\n    for a in need:"):s.index("    if filled:")]
    new = '''    filled = []
    for a in need:
        d, src = None, None
        for fn in (_yahoo, _stooq):
            try:
                d, src = fn(a)
                if d is not None and lc in d.index: break
            except Exception as e:
                print(f"  {a}: {fn.__name__[1:]} failed ({type(e).__name__})"); d = None
        if d is None or lc not in d.index: print(f"  {a}: no source has {lc.date()} yet -- left NaN"); continue
        i = d.index.get_loc(lc); prev = d.index[i - 1]; ret = float(np.log(d.iloc[i] / d.iloc[i - 1]))
        r.loc[lc, a] = ret; filled.append(dict(date=lc.strftime("%Y-%m-%d"), asset=a, ret=ret, prev=prev.strftime("%Y-%m-%d"), source=src, filled_at=now))
'''
    s = s.replace(old, new, 1)
    helpers = '''UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) regime-aware-signal academic research"}


def _yahoo(a):
    """Yahoo's short-window request (period=10d): the audit showed it current when the long-history request lags a session. Adjusted closes."""
    import yfinance as yf
    h = yf.Ticker(a).history(period="10d", interval="1d", auto_adjust=True)
    if h.empty: return None, None
    c = h["Close"]; c.index = pd.to_datetime(c.index).tz_localize(None).normalize(); return c.dropna(), "yahoo-10d"


def _stooq(a):
    """Stooq daily CSV (unadjusted closes); needs a browser-style header."""
    req = urllib.request.Request(f"https://stooq.com/q/d/l/?s={STOOQ[a]}&i=d", headers=UA)
    csv = urllib.request.urlopen(req, timeout=30).read().decode()
    d = pd.read_csv(io.StringIO(csv), parse_dates=["Date"]).set_index("Date")["Close"].dropna(); return d, "stooq"


'''
    s = s.replace("\n\ndef run():", "\n\n" + helpers + "def run():", 1)
    p.write_text(s); print("  fallback: yahoo-10d then stooq")

# ---- ask + calibration check
t = Path("src/target_range.py"); s = t.read_text()
old = s[s.index("def ask(asset, price, target, h, regime=None):"):s.index("def selftest():")]
new = '''def _passed() -> bool:
    cal = DOCS / "target_range_calibration.md"
    return cal.exists() and any(ln.strip().endswith("| PASS |") for ln in cal.read_text().splitlines())


def ask(asset, price, targets, h, regime=None):
    """The output form of the prereg, computed exactly from history for any list of price levels. Calibrated (unconditional) numbers first;
    the regime-conditional ones are marked uncalibrated until a Stage 1 cell passes."""
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; lab = regime_labels(rets.index).to_numpy(); r = rets[asset]
    if regime is None: regime = int(lab[-1])
    mx, mn, end = extremes(r, h); ok = np.isfinite(mx); m_all = ok; m_reg = ok & (lab == regime)
    px = lambda v: price * np.exp(v)
    def block(mask, name):
        e, hi, lo_ = end[mask], mx[mask], mn[mask]; n = int(mask.sum())
        q25, q50, q75 = np.quantile(e, [.25, .5, .75])
        print(f"{name} (n {n:,}, ≈{n // h} independent {h}-session cases):")
        print(f"  central target {px(q50):,.0f}  (band {px(q25):,.0f} – {px(q75):,.0f}); typical worst on the way {px(np.median(lo_)):,.0f}, typical best {px(np.median(hi)):,.0f}")
        print(f"  levels history gave a chance of touching within {h} sessions:  1-in-2: {px(np.quantile(hi, .5)):,.0f}   1-in-3: {px(np.quantile(hi, 2/3)):,.0f}   1-in-10: {px(np.quantile(hi, .9)):,.0f}"
              f"   | downside 1-in-2: {px(np.quantile(lo_, .5)):,.0f}   1-in-3: {px(np.quantile(lo_, 1/3)):,.0f}   1-in-10: {px(np.quantile(lo_, .1)):,.0f}")
        for tgt in targets:
            x = np.log(tgt / price); pr = float((hi >= x).mean()) if x > 0 else float((lo_ <= x).mean())
            print(f"  chance of touching {tgt:,.0f} ({x:+.1%}) within {h} sessions: {pr:.0%}")
    print(f"{asset} at {price:,.0f}, horizon {h} sessions.")
    block(m_all, "Over all history — the calibrated form")
    block(m_reg, f"In today's condition ({regime}) — " + ("calibrated cell on record" if _passed() else "NOT calibrated (Stage 1: 0 of 24 cells passed), shown for comparison"))
    print("Measured counts, not forecasts. Reasons (Stage 2) and weights (Stage 3) will shift these once they pass their tests.")


'''
if "def _passed()" in s: print("  ask: already")
else:
    s = s.replace(old, new, 1)
    s = s.replace('q = sub.add_parser("ask"); q.add_argument("asset"); q.add_argument("--price", type=float, required=True); q.add_argument("--target", type=float, required=True)',
                  'q = sub.add_parser("ask"); q.add_argument("asset"); q.add_argument("--price", type=float, required=True); q.add_argument("--target", type=float, nargs="*", default=[])', 1)
    s = s.replace('    if a.cmd == "ask": ask(a.asset, a.price, a.target, a.h, a.regime)',
                  '    if a.cmd == "ask": ask(a.asset, a.price, a.target or [a.price * k for k in (1.05, 1.10, 1.20, 1.30, 0.95, 0.90)], a.h, a.regime)', 1)
    t.write_text(s); print("  ask: exact targets, touch ladder, calibration check fixed")
print("done")
