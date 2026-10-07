"""
app.py -- Regime-Aware Signal, the demonstration terminal (v3, 2026-09-28).

What changed from v2: live market data from Yahoo Finance on the instruments a
desk actually watches (S&P 500, US 10-year yield, gold $/oz, DXY, WTI); a
click-through detail dashboard per market with 1m/5m/1h/1d/1wk bars, line or
candles; hover-lift only on the things that can be clicked; a mesh-gradient
backdrop with frosted cards.

What did not change: the report, its words, its abstention rule. The model runs
on the five ETFs; the page shows the instruments people recognise and says so.
There is no buy or sell control by design.

Live data is display only. Nothing here feeds the estimator.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAVE_PLOTLY = True
except Exception:
    HAVE_PLOTLY = False
try:
    import yfinance as yf
    HAVE_YF = True
except Exception:
    HAVE_YF = False

ROOT = Path(__file__).resolve().parent
DOCS, PROC = ROOT / "docs", ROOT / "processed"
REPORTS = ROOT / "outputs" / "reports"

st.set_page_config(page_title="Regime-Aware Signal", page_icon="◐",
                   layout="wide", initial_sidebar_state="collapsed")

# ==========================================================================
# DESIGN SYSTEM
# ==========================================================================
INK, INK2, INK3 = "#14171F", "#5F6672", "#98A0AD"
LINE = "rgba(20,23,31,.09)"
ACCENT = "#0A2540"
UP, DOWN, WARN, MUTE = "#178A4C", "#C9341F", "#B7791F", "#7B8290"
REGIME_COLOURS = ["#4F6D9A", "#6FA37A", "#C9A24B", "#B5645A"]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp {{ font-family: Inter, -apple-system, "SF Pro Text", "Segoe UI", sans-serif; color:{INK}; }}
.stApp {{
  background:
    radial-gradient(1100px 620px at 8% -8%, rgba(10,37,64,.10), transparent 60%),
    radial-gradient(900px 560px at 104% 104%, rgba(183,121,31,.09), transparent 60%),
    linear-gradient(180deg, #F8F9FC 0%, #EDF0F5 100%);
  background-attachment: fixed;
}}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility:hidden; height:0; }}
.block-container {{ padding-top:1.3rem; padding-bottom:3rem; max-width:1280px; }}
h1,h2,h3,h4 {{ letter-spacing:-0.012em; }}
.stTabs [data-baseweb="tab-list"] {{ gap:4px; background:rgba(20,23,31,.06); padding:4px; border-radius:12px; width:max-content; }}
.stTabs [data-baseweb="tab"] {{ height:34px; padding:0 16px; border-radius:9px; background:transparent; color:{INK2}; font-weight:500; }}
.stTabs [aria-selected="true"] {{ background:rgba(255,255,255,.92) !important; color:{INK} !important; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display:none; }}
div[data-baseweb="select"] > div, .stTextInput input {{ border-radius:10px !important; border-color:{LINE} !important; background:rgba(255,255,255,.85); }}
.stButton > button {{ border-radius:10px; border:1px solid transparent; background:{ACCENT}; color:#fff; font-weight:600; padding:.45rem 1.1rem; }}
.stButton > button:hover {{ background:#133A66; color:#fff; }}
div[data-testid="stExpander"] {{ border:1px solid {LINE}; border-radius:14px; background:rgba(255,255,255,.7); backdrop-filter:blur(10px); }}
div[data-testid="stRadio"] label {{ font-weight:500; }}

/* glass surfaces */
.g {{ background:rgba(255,255,255,.72); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
      border:1px solid rgba(255,255,255,.65); box-shadow:0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.06); border-radius:18px; }}
/* only clickable surfaces respond to the cursor */
a.rs-link {{ text-decoration:none !important; color:inherit !important; display:block; }}
.rs-hover {{ transition:transform .18s ease, box-shadow .18s ease; cursor:pointer; }}
.rs-hover:hover {{ transform:translateY(-2px) scale(1.015); box-shadow:0 2px 4px rgba(16,24,40,.05), 0 16px 36px rgba(10,37,64,.14); }}

.rs-wordmark {{ font-weight:700; font-size:1.15rem; letter-spacing:-.01em; }}
.rs-wordmark span {{ color:{INK3}; font-weight:500; margin-left:.5rem; font-size:.92rem; }}
.rs-banner {{ padding:18px 22px; margin:6px 0 14px; }}
.rs-banner h2 {{ margin:0 0 4px; font-size:1.35rem; }}
.rs-banner p {{ margin:0; color:{INK2}; }}
.rs-tiles {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:6px 0 14px; }}
.rs-tile {{ padding:14px 16px; min-height:98px; border-radius:16px; }}
.rs-k {{ font-size:.68rem; letter-spacing:.09em; text-transform:uppercase; color:{INK3}; font-weight:600; }}
.rs-v {{ font-size:1.45rem; font-weight:700; margin-top:6px; font-variant-numeric:tabular-nums; line-height:1.15; }}
.rs-s {{ color:{INK2}; font-size:.8rem; margin-top:4px; }}
.rs-dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }}
.rs-bar {{ height:6px; background:rgba(20,23,31,.08); border-radius:6px; overflow:hidden; margin-top:8px; }}
.rs-bar > div {{ height:100%; background:{ACCENT}; border-radius:6px; }}
.rs-strip {{ display:flex; gap:1px; height:10px; border-radius:6px; overflow:hidden; margin:4px 0 6px; }}
.rs-strip > div {{ flex:1; }}
.rs-legend {{ display:flex; gap:14px; flex-wrap:wrap; font-size:.78rem; color:{INK2}; }}
.rs-cards {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; }}
.rs-card {{ padding:14px 16px 12px; border-radius:18px; height:100%; }}
.rs-card .name {{ font-weight:600; font-size:.95rem; }}
.rs-card .tick {{ color:{INK3}; font-size:.74rem; margin-left:6px; font-weight:500; }}
.rs-card .px {{ font-size:1.32rem; font-weight:700; margin-top:6px; font-variant-numeric:tabular-nums; letter-spacing:-.01em; }}
.rs-card .chg {{ font-size:.84rem; font-weight:600; margin-left:8px; font-variant-numeric:tabular-nums; }}
.rs-card .live {{ color:{INK3}; font-size:.7rem; margin-top:2px; }}
.rs-card svg {{ display:block; width:100%; height:56px; margin-top:8px; }}
.rs-pill {{ display:inline-block; padding:3px 10px; border-radius:999px; font-size:.74rem; font-weight:600; }}
.rs-reason {{ color:{INK2}; font-size:.78rem; margin-top:6px; line-height:1.35; min-height:2.6em; }}
.rs-ev {{ margin-top:8px; padding-top:8px; border-top:1px solid rgba(20,23,31,.08); font-size:.74rem; color:{INK2}; line-height:1.35; }}
.rs-ev b {{ color:{INK}; }}
.rs-doc {{ padding:12px 14px; height:100%; border-radius:14px; }}
.rs-doc .src {{ font-weight:600; font-size:.9rem; }}
.rs-doc .meta {{ color:{INK3}; font-size:.74rem; margin:2px 0 8px; }}
.rs-chip {{ display:inline-block; padding:2px 8px; border-radius:6px; font-size:.74rem; margin:0 4px 4px 0; background:rgba(20,23,31,.05); }}
.rs-mini {{ display:grid; grid-template-columns:70px 1fr 36px; gap:8px; align-items:center; font-size:.74rem; color:{INK2}; margin-top:4px; }}
.rs-mini .b {{ height:5px; background:rgba(20,23,31,.08); border-radius:5px; overflow:hidden; }}
.rs-mini .b > div {{ height:100%; background:{ACCENT}; }}
.rs-foot {{ color:{INK3}; font-size:.78rem; line-height:1.45; }}
.rs-section {{ font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; color:{INK3}; font-weight:600; margin:18px 0 8px; }}
.rs-back {{ display:inline-block; font-size:.85rem; color:{INK2}; margin-bottom:8px; }}
.rs-back:hover {{ color:{INK}; }}
.rs-quote {{ display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }}
.rs-quote .big {{ font-size:2.1rem; font-weight:700; font-variant-numeric:tabular-nums; letter-spacing:-.02em; }}
.rs-quote .d {{ font-size:1rem; font-weight:600; font-variant-numeric:tabular-nums; }}
.rs-quote .t {{ color:{INK3}; font-size:.78rem; }}
@media (max-width: 1000px) {{ .rs-tiles {{ grid-template-columns:repeat(2,1fr); }} .rs-cards {{ grid-template-columns:repeat(2,1fr); }} }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ==========================================================================
# WHAT IS SHOWN vs WHAT IS MODELLED
# The model runs on five ETFs. The page shows the instruments a desk watches,
# quoted the way the desk quotes them, and says so on every card.
# ==========================================================================
SOURCE = {"fomc_statement": "Fed policy statement", "fomc_minutes": "Fed meeting minutes",
          "earnings_8k": "Company earnings release", "political_order": "Executive order",
          "political_other": "Proclamation or notice", "political": "Federal Register document"}
ASSET = {"SPY": "US equities", "TLT": "US Treasuries", "GLD": "Gold", "UUP": "US dollar", "USO": "Oil"}
DISPLAY = {
    "SPY": dict(tk="^GSPC", name="S&P 500", unit="index", fmt="{:,.2f}", chg="pct", vol=True,
                note="Model asset: SPY."),
    "TLT": dict(tk="^TNX", name="US 10-year yield", unit="%", fmt="{:.3f}%", chg="bp", vol=False,
                note="Model asset: TLT (bond prices). A positive read means yields expected lower."),
    "GLD": dict(tk="GC=F", name="Gold", unit="$/oz", fmt="${:,.2f}", chg="pct", vol=True,
                note="Model asset: GLD."),
    "UUP": dict(tk="DX-Y.NYB", name="US dollar index", unit="DXY", fmt="{:.2f}", chg="pct", vol=False,
                note="Model asset: UUP."),
    "USO": dict(tk="CL=F", name="WTI crude", unit="$/bbl", fmt="${:.2f}", chg="pct", vol=True,
                note="Model asset: USO."),
}
AXIS_WORD = {"equity": "US equities", "duration": "Treasuries", "gold": "Gold", "dollar": "US dollar", "oil": "Oil"}
AXIS_OF = {"SPY": "equity", "TLT": "duration", "GLD": "gold", "UUP": "dollar", "USO": "oil"}


@st.cache_data(show_spinner=False)
def load_fomc_days():
    p = PROC / "fomc_decisions.csv"
    if not p.exists():
        return set()
    try:
        return set(pd.to_datetime(pd.read_csv(p).iloc[:, 0], errors="coerce").dropna())
    except Exception:
        return set()


def event_line(a: str, R: dict, day: str, fomc_days) -> str:
    """The app's second line, per docs/prereg_event_time.md section 4. What the statement said is always
    allowed; a number is allowed only on an EXTENDS/REVERSES verdict with a same-regime pool, which no
    market has (phase A: NULL on S&P and 10-year, 29 Sep 2026); gold, oil and the dollar have no intraday
    precedents until the forward collection (S5) reaches its floor."""
    docs = [d for d in R.get("documents", []) if d.get("source") == "fomc_statement"]
    if not docs and pd.Timestamp(day) not in fomc_days:
        return '<div class="rs-ev"><b>Rest of session</b> — no scheduled event today</div>'
    if docs:
        d = docs[0]; dirs = d.get("direction") or {}
        v = dirs.get(AXIS_OF[a], dirs.get(a))
        stance = d.get("stance")
        st_txt = f"{stance} stance; " if isinstance(stance, str) and stance else ""
        if v is None or abs(v) <= 0.05:
            read = f"no clear read for {ASSET[a].lower()}"
        elif a == "TLT":
            read = "implies " + ("higher bond prices (yields lower)" if v > 0 else "lower bond prices (yields higher)")
        else:
            read = "implies " + ("higher " if v > 0 else "lower ") + ASSET[a].lower()
        said = f"Statement read: {st_txt}{read}. "
    else:
        said = "Fed statement day — statement not yet read. "
    pattern = ("No measurable rest-of-session pattern (292 meetings, 1988–2023)."
               if a in ("SPY", "TLT") else "No intraday precedents yet — collecting.")
    return f'<div class="rs-ev"><b>Rest of session</b> · {said}{pattern}</div>'


RANGES = {"1D": ("1d", "1m"), "5D": ("5d", "5m"), "1M": ("1mo", "60m"), "6M": ("6mo", "1d"),
          "1Y": ("1y", "1d"), "5Y": ("5y", "1wk")}


def jload(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def plain_reason(raw, e=None):
    r = (raw or "").lower()
    if "direction floor" in r or "no document" in r:
        return "Nothing we read today spoke to this market"
    if "ess" in r:
        n = ((e or {}).get("estimate") or {}).get("ess")
        return (f"Only {n:.0f} genuinely comparable past situations — we need at least 8"
                if n is not None else "Too few genuinely comparable past situations")
    if "pool" in r or "precedent" in r:
        return "Not enough past situations of this kind to compare against"
    if "vetoed" in r:
        return "Today's news was too vague to act on"
    if "not in the price panel" in r:
        return "We do not carry price history for this instrument"
    return raw or "Conditions for a view were not met"


def verdict(e):
    est = e.get("estimate")
    if e["net_view"] is None or est is None or e.get("abstain"):
        return "No view", MUTE, plain_reason(e.get("abstain_reason"), e)
    word = "Clear signal" if est["tier"] == 1 else "Weak signal"
    return word, (UP if est["tier"] == 1 else WARN), f"{est['estimate']:+.2%} over the next 3 trading days"


PILL_BG = {UP: "#E4F4EA", WARN: "#FBF0D9", MUTE: "rgba(20,23,31,.05)"}


# ==========================================================================
# DATA
# ==========================================================================
@st.cache_data(show_spinner=False)
def load_index():
    ix = jload(PROC / "report_index.json")
    return pd.DataFrame(ix).sort_values("date") if ix else None


@st.cache_data(show_spinner=False)
def load_report(day: str):
    return jload(REPORTS / f"{day.replace('-', '')}.json")


@st.cache_data(show_spinner=False)
def load_profile():
    return jload(PROC / "regime_profile.json")


@st.cache_data(show_spinner=True)
def load_regimes():
    """Expanding regime labels; about a minute once per session, cached after."""
    try:
        import asset_extension as AE
        cfg = AE.load_config(); sc, _ = AE.load_data()
        lab = AE.regime_labels_expanding(sc, cfg)
        return pd.Series(np.asarray(lab), index=pd.DatetimeIndex(sc.index))
    except Exception:
        return None


def _flat(df):
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    keep = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in df.columns]
    return df[keep].dropna(subset=["Close"])


@st.cache_data(ttl=60, show_spinner=False)
def fetch_bars(tk: str, period: str, interval: str) -> pd.DataFrame:
    """Live bars from Yahoo Finance (delayed ~15 min for most venues). Cached 60 s."""
    if not HAVE_YF:
        return pd.DataFrame()
    try:
        return _flat(yf.Ticker(tk).history(period=period, interval=interval, auto_adjust=False))
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_daily(tk: str, period: str = "3mo") -> pd.DataFrame:
    if not HAVE_YF:
        return pd.DataFrame()
    try:
        d = _flat(yf.Ticker(tk).history(period=period, interval="1d", auto_adjust=False))
        if not d.empty:
            ix = pd.to_datetime(d.index)
            d.index = ix.tz_localize(None) if getattr(ix, "tz", None) is not None else ix
        return d
    except Exception:
        return pd.DataFrame()


def quote(spec: dict):
    """Last close, change, %-change, as-of date and a 60-session series, from live daily data."""
    d = fetch_daily(spec["tk"], "3mo")
    if d.empty or len(d) < 2:
        return None
    last, prev = float(d["Close"].iloc[-1]), float(d["Close"].iloc[-2])
    return dict(last=last, chg=last - prev, pct=last / prev - 1, as_of=d.index[-1], series=d["Close"].tail(60))


def fmt_change(spec, q):
    return f"{q['chg']*100:+.0f} bp" if spec["chg"] == "bp" else f"{q['pct']:+.2%}"


def regime_runs(reg):
    if reg is None or reg.empty:
        return []
    out, start, cur = [], reg.index[0], reg.iloc[0]
    for d, v in reg.items():
        if v != cur:
            out.append((start, d, cur)); start, cur = d, v
    out.append((start, reg.index[-1], cur))
    return out


# ==========================================================================
# VISUAL COMPONENTS
# ==========================================================================
def rgba(hex_colour: str, alpha: float) -> str:
    h = hex_colour.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def svg_sparkline(vals, colour: str, w=240, h=56) -> str:
    """Inline SVG so the whole card, chart included, is one clickable surface."""
    v = np.asarray(vals, float); v = v[np.isfinite(v)]
    if len(v) < 2:
        return ""
    lo, hi = v.min(), v.max(); rng = (hi - lo) or 1.0
    xs = np.linspace(4, w - 4, len(v)); ys = h - 6 - (v - lo) / rng * (h - 12)
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    gid = f"g{abs(hash((colour, len(v), float(v[-1])))) % 100000}"
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none"><defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{colour}" stop-opacity=".22"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/></linearGradient></defs>'
            f'<polygon points="{xs[0]:.1f},{h} {pts} {xs[-1]:.1f},{h}" fill="url(#{gid})"/>'
            f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/></svg>')


def market_card(a: str, e: dict, q, href: str, ev: str = "") -> str:
    spec = DISPLAY[a]; head, colour, detail = verdict(e)
    if q:
        col = UP if q["chg"] >= 0 else DOWN
        px, chg = spec["fmt"].format(q["last"]), fmt_change(spec, q)
        spark = svg_sparkline(q["series"].values, col)
        live = f"live · {q['as_of']:%d %b} close · delayed ~15 min"
    else:
        col, px, chg, spark, live = INK3, "—", "", "", "live data unavailable"
    return (f'<a class="rs-link" href="{href}" target="_self"><div class="g rs-card rs-hover">'
            f'<div><span class="name">{spec["name"]}</span><span class="tick">{spec["tk"]} · {spec["unit"]}</span></div>'
            f'<div class="px">{px}<span class="chg" style="color:{col}">{chg}</span></div>'
            f'<div class="live">{live}</div>{spark}'
            f'<div style="margin-top:8px"><span class="rs-pill" style="background:{PILL_BG[colour]};color:{colour}">{head}</span></div>'
            f'<div class="rs-reason">{detail}</div>{ev}</div></a>')


def regime_strip_html(reg, day, prof, n=250):
    if reg is None:
        return ""
    r = reg.loc[:day].tail(n)
    cells = "".join(
        f'<div style="background:{REGIME_COLOURS[int(v) % 4] if v is not None and v >= 0 else "rgba(20,23,31,.08)"};'
        f'{"outline:2px solid " + INK + "; outline-offset:-1px;" if d == r.index[-1] else ""}"></div>' for d, v in r.items())
    legend = "".join(f'<span><span class="rs-dot" style="background:{REGIME_COLOURS[int(k) % 4]}"></span>{v["label"]} '
                     f'<span style="color:{INK3}">· {v["share_pct"]}% of history</span></span>'
                     for k, v in sorted((prof or {}).get("regimes", {}).items()))
    return (f'<div class="rs-section">Market condition, last {len(r)} sessions</div>'
            f'<div class="rs-strip">{cells}</div><div class="rs-legend">{legend}</div>')


def price_chart(bars: pd.DataFrame, spec: dict, kind: str, reg, day, height=420):
    """TradingView-style: candles or line, volume pane when meaningful, regime bands on daily ranges."""
    if bars.empty:
        st.info("No bars returned for this range — the venue may be closed for the intraday windows, or the feed is unavailable.")
        return
    if not HAVE_PLOTLY:
        st.line_chart(bars["Close"], height=height); return
    has_vol = bool(spec.get("vol")) and "Volume" in bars.columns and float(bars["Volume"].fillna(0).sum()) > 0
    f = make_subplots(rows=2 if has_vol else 1, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                      row_heights=[0.78, 0.22] if has_vol else [1.0])
    daily = bool(bars.index.to_series().diff().median() >= pd.Timedelta("20h")) if len(bars) > 2 else True
    tz = getattr(bars.index, "tz", None)
    if daily and reg is not None:
        idx = pd.DatetimeIndex(bars.index).tz_localize(None) if tz is not None else pd.DatetimeIndex(bars.index)
        r = reg.reindex(idx, method="ffill")
        for a, b, lab in regime_runs(r):
            if lab is None or (isinstance(lab, float) and math.isnan(lab)) or int(lab) < 0:
                continue
            f.add_vrect(x0=a, x1=b, fillcolor=REGIME_COLOURS[int(lab) % 4], opacity=0.09, line_width=0, row=1, col=1)
    if kind == "Candles" and all(c in bars.columns for c in ("Open", "High", "Low")):
        f.add_trace(go.Candlestick(x=bars.index, open=bars["Open"], high=bars["High"], low=bars["Low"], close=bars["Close"],
                                   increasing_line_color=UP, decreasing_line_color=DOWN, increasing_fillcolor=UP,
                                   decreasing_fillcolor=DOWN, line=dict(width=1), name=spec["name"]), row=1, col=1)
    else:
        up = bool(bars["Close"].iloc[-1] >= bars["Close"].iloc[0])
        f.add_trace(go.Scatter(x=bars.index, y=bars["Close"], mode="lines", name=spec["name"],
                               line=dict(width=2, color=UP if up else DOWN), fill="tozeroy",
                               fillcolor=rgba(UP if up else DOWN, 0.07),
                               hovertemplate="%{x}<br>%{y:,.3f}<extra></extra>"), row=1, col=1)
    if has_vol:
        opens = bars["Open"] if "Open" in bars.columns else bars["Close"]
        vc = [UP if c >= o else DOWN for c, o in zip(bars["Close"], opens)]
        f.add_trace(go.Bar(x=bars.index, y=bars["Volume"], marker_color=vc, opacity=.55, name="volume",
                           hovertemplate="%{y:,.0f}<extra></extra>"), row=2, col=1)
    if daily and day is not None:
        d0 = pd.Timestamp(day)
        lo, hi = pd.Timestamp(bars.index.min()), pd.Timestamp(bars.index.max())
        lo, hi = (lo.tz_localize(None), hi.tz_localize(None)) if tz is not None else (lo, hi)
        if lo <= d0 <= hi:
            f.add_vline(x=d0, line_width=1, line_dash="dot", line_color=INK2, row=1, col=1)
    f.update_layout(height=height, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False, hovermode="x unified", xaxis_rangeslider_visible=False, dragmode="pan")
    f.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color=INK3, size=11),
                   rangebreaks=([dict(bounds=["sat", "mon"])] if daily else []))
    f.update_yaxes(showgrid=True, gridcolor="rgba(20,23,31,.07)", zeroline=False, tickfont=dict(color=INK3, size=11), side="right")
    if has_vol:
        f.update_yaxes(showgrid=False, showticklabels=False, row=2, col=1)
    st.plotly_chart(f, use_container_width=True, config=dict(displayModeBar=False, scrollZoom=True))


def chart_controls(key: str, default_range="1Y"):
    c = st.columns([3.2, 1.2, 1])
    rng = c[0].radio("Range", list(RANGES.keys()), index=list(RANGES.keys()).index(default_range),
                     horizontal=True, key=f"rng_{key}", label_visibility="collapsed")
    kind = c[1].radio("Type", ["Line", "Candles"], horizontal=True, key=f"kind_{key}", label_visibility="collapsed")
    if c[2].button("Refresh", key=f"rf_{key}"):
        fetch_bars.clear(); fetch_daily.clear()
    return RANGES[rng], kind


def detail_dashboard(a: str, R: dict, day: str, reg):
    """Same-page detail view for one market: quote, range/interval, chart type, the report's read."""
    spec = DISPLAY[a]; e = R["assets"][a]; head, colour, detail = verdict(e)
    st.markdown('<a class="rs-back rs-link" href="?" target="_self">← Back to overview</a>', unsafe_allow_html=True)
    q = quote(spec)
    if q:
        col = UP if q["chg"] >= 0 else DOWN
        abs_chg = "" if spec["chg"] == "bp" else f" · {q['chg']:+,.2f}"
        st.markdown(f'<div class="g rs-banner"><div class="rs-quote"><span style="font-weight:700;font-size:1.1rem">{spec["name"]}</span>'
                    f'<span class="t">{spec["tk"]} · {spec["unit"]}</span></div>'
                    f'<div class="rs-quote"><span class="big">{spec["fmt"].format(q["last"])}</span>'
                    f'<span class="d" style="color:{col}">{fmt_change(spec, q)}{abs_chg}</span>'
                    f'<span class="t">as of {q["as_of"]:%d %b %Y} close · Yahoo Finance, delayed</span></div>'
                    f'<p style="margin-top:6px">{spec["note"]}</p></div>', unsafe_allow_html=True)
    (period, interval), kind = chart_controls("today")
    bars = fetch_bars(spec["tk"], period, interval)
    st.markdown('<div class="g" style="padding:8px 8px 2px">', unsafe_allow_html=True)
    price_chart(bars, spec, kind, reg, day)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-foot">{interval} bars over {period}. Shaded bands on daily ranges are the four market conditions '
                f'as the model labelled them at the time. The dotted line is the selected report day.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-section">The report on {day}</div>', unsafe_allow_html=True)
    est = e.get("estimate") or {}
    notes = []
    if e["net_view"] is not None:
        tone = "positive" if e["net_view"] > 0 else "negative"
        src = SOURCE.get(e["dominant_source"], e["dominant_source"] or "")
        notes.append(f"Today's documents read <b>{tone}</b> for {ASSET[a].lower()}, mostly from a {src.lower()}.")
    if e.get("sources_disagree"):
        notes.append(f'<span style="color:{WARN}">Two documents point opposite ways — both shown, neither combined.</span>')
    if e.get("agreement") == "DISCORDANT":
        notes.append(f'<span style="color:{WARN}">The documents and the history disagree.</span>')
    st.markdown(f"""
<div class="rs-tiles">
  <div class="g rs-tile"><div class="rs-k">Read</div><div class="rs-v"><span class="rs-pill" style="background:{PILL_BG[colour]};color:{colour};font-size:.9rem">{head}</span></div><div class="rs-s">{detail}</div></div>
  <div class="g rs-tile"><div class="rs-k">Past situations matched</div><div class="rs-v">{est.get('n_matched', '—')}</div><div class="rs-s">same condition, same document class, outcome already closed</div></div>
  <div class="g rs-tile"><div class="rs-k">Genuinely comparable</div><div class="rs-v">{f"{est['ess']:.0f}" if est else "—"}</div><div class="rs-s">effective sample size; a view needs at least 8</div></div>
  <div class="g rs-tile"><div class="rs-k">History weight</div><div class="rs-v">{f"{est['w_shrink']:.2f}" if est else "—"}</div><div class="rs-s">0 = the past adds nothing beyond the long-run average</div></div>
</div>""", unsafe_allow_html=True)
    if notes:
        st.markdown('<div class="rs-foot">' + " &nbsp;·&nbsp; ".join(notes) + "</div>", unsafe_allow_html=True)
    st.markdown('<div class="rs-section">Rest of session</div>', unsafe_allow_html=True)
    st.markdown('<div class="g rs-banner" style="padding:12px 18px">' + event_line(a, R, day, load_fomc_days()).replace('rs-ev', 'rs-ev" style="border:none;margin:0;padding:0;font-size:.86rem') +
                '<p class="rs-foot" style="margin-top:8px">Whether the first half-hour\'s reaction extends or reverses by the close was tested on 292 meetings since 1988 (docs/event_time_phaseA.md): no measurable pattern for equities or Treasuries. A number appears here only if a registered test establishes one. Intraday bars are being collected every session for the markets that have no history yet.</p></div>', unsafe_allow_html=True)


def doc_cards(docs: list):
    if not docs:
        st.markdown('<div class="rs-foot">None of the five document types we read was published for this session. '
                    'A quiet day here means our sources were quiet, not that the world was.</div>', unsafe_allow_html=True)
        return
    cols = st.columns(min(3, len(docs)))
    for i, d in enumerate(docs):
        chips = "".join(f'<span class="rs-chip">{"▲" if v > 0 else "▼"} {ASSET.get(k, AXIS_WORD.get(k, k))}</span>'
                        for k, v in d["direction"].items() if v is not None and abs(v) > 0.05) or '<span class="rs-chip">no clear read</span>'

        def bar(label, v):
            pct = int((v or 0) * 100)
            return f'<div class="rs-mini"><span>{label}</span><div class="b"><div style="width:{pct}%"></div></div><span>{pct}%</span></div>'
        with cols[i % len(cols)]:
            st.markdown(f'<div class="g rs-doc"><div class="src">{SOURCE.get(d["source"], d["source"])}</div>'
                        f'<div class="meta">published {d["published"]}{" · truncated" if d.get("truncated") else ""}</div>'
                        f'<div>{chips}</div>{bar("specific", d.get("specificity"))}{bar("new", d.get("novelty"))}'
                        f'{bar("confident", d.get("confidence"))}</div>', unsafe_allow_html=True)
            st.write("")


# ==========================================================================
# HEADER + TABS
# ==========================================================================
st.markdown('<div class="rs-wordmark">◐ Regime-Aware Signal <span>a daily read on five core markets — '
            'and, more often than not, an explicit refusal to call it</span></div>', unsafe_allow_html=True)
tabs = st.tabs(["Today", "Look up an asset", "The record", "How this works"])
try:
    focus_param = st.query_params.get("focus")
except Exception:
    focus_param = None
if isinstance(focus_param, list):
    focus_param = focus_param[0] if focus_param else None

# ==========================================================================
# TODAY
# ==========================================================================
with tabs[0]:
    ix = load_index()
    if ix is None or ix.empty:
        st.warning("No reports on disk yet. Run `python step6_report.py --pending`."); st.stop()
    ctl = st.columns([1.3, 1.6, 4])
    only = ctl[1].toggle("Only days with a signal", value=False, key="today_only")
    pool = ix[ix.best_tier <= 2] if only else ix
    if pool.empty:
        st.info("No day matches that filter."); st.stop()
    dates = list(pool.date)
    day = ctl[0].selectbox("Date", dates, index=len(dates) - 1, key="today_date", label_visibility="collapsed")
    R = load_report(day)
    if not R:
        st.warning(f"No report for {day}."); st.stop()
    T = pd.Timestamp(day)
    prof, reg = load_profile(), load_regimes()

    if focus_param in R["assets"]:
        detail_dashboard(focus_param, R, day, reg)
    else:
        views = [a for a, e in R["assets"].items() if e.get("estimate") and not e.get("abstain")]
        if views:
            st.markdown(f'<div class="g rs-banner"><h2>{len(views)} of 5 markets have a view · {day}</h2>'
                        f'<p>{", ".join(DISPLAY[v]["name"] for v in views)}. Every other market abstains, with the reason on its card.</p></div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="g rs-banner"><h2>No view on any market · {day}</h2>'
                        '<p>Either nothing we read was published, or what was published does not resemble enough past '
                        'situations to support a view. That is the system\'s most common answer — and it is the product working.</p></div>',
                        unsafe_allow_html=True)
        g = R["regime"]
        rl = ((prof or {}).get("regimes", {}).get(str(g["label"]), {}) or {}).get("label")
        cond = rl or f"Condition {g['label'] + 1} of 4"
        post = g.get("posterior") or 0
        warn = (f'<div class="rs-s" style="color:{WARN}">The model is not confident which condition today belongs to.</div>'
                if g.get("warning") else '<div class="rs-s">that today belongs to this condition</div>')
        st.markdown(f"""
<div class="rs-tiles">
  <div class="g rs-tile"><div class="rs-k">Market condition</div>
    <div class="rs-v"><span class="rs-dot" style="background:{REGIME_COLOURS[int(g['label']) % 4]}"></span>{cond}</div>
    <div class="rs-s">one of four, learned from macro data</div></div>
  <div class="g rs-tile"><div class="rs-k">Confidence</div><div class="rs-v">{f"{post:.0%}" if post else "—"}</div>
    <div class="rs-bar"><div style="width:{int(post*100)}%"></div></div>{warn}</div>
  <div class="g rs-tile"><div class="rs-k">Documents today</div><div class="rs-v">{len(R['documents'])}</div>
    <div class="rs-s">from five sources we read; not the news</div></div>
  <div class="g rs-tile"><div class="rs-k">Markets with a view</div><div class="rs-v">{len(views)} <span style="color:{INK3};font-weight:500">of 5</span></div>
    <div class="rs-s">a view needs at least 8 comparable past situations</div></div>
</div>""", unsafe_allow_html=True)
        st.markdown(regime_strip_html(reg, T, prof), unsafe_allow_html=True)

        st.markdown('<div class="rs-section">The five markets — click a card for the full chart</div>', unsafe_allow_html=True)
        fomc_days = load_fomc_days()
        cards = "".join(market_card(a, e, quote(DISPLAY[a]), f"?focus={a}", event_line(a, R, day, fomc_days))
                        for a, e in R["assets"].items())
        st.markdown(f'<div class="rs-cards">{cards}</div>', unsafe_allow_html=True)
        st.markdown('<div class="rs-foot" style="margin-top:8px">Prices are live from Yahoo Finance (delayed about 15 minutes) '
                    'on the instruments a desk watches; the model runs on SPY, TLT, GLD, UUP and USO underneath, and each card '
                    'says which. The signal pill and its reason are for the selected report day.</div>', unsafe_allow_html=True)

        st.markdown('<div class="rs-section">What landed today</div>', unsafe_allow_html=True)
        doc_cards(R["documents"])

        with st.expander("Wider coverage — on the roadmap, and a paid tier"):
            st.markdown("""
Everything above is a **filed decision**. The moment a policy is *threatened* rather than enacted — a tariff warning,
a sanctions signal, a closure of a shipping lane — is usually where a market moves first, and it is not covered here
today. Four further US-government sources would close that gap: White House statements and remarks, Federal Reserve
speeches and testimony, Treasury and OFAC releases, and USTR press releases. Costed, registered, not built — and intended
as a subscription tier, because reading *intentions* rather than only *decisions* is a materially different service.""")
        prev = ix[ix.date < day]
        if len(prev):
            pday = prev.iloc[-1].date; P = load_report(pday)
            if P:
                lines = [f"- **{DISPLAY[a]['name']}**: documents read {'positive' if e['net_view'] > 0 else 'negative'}"
                         for a, e in P["assets"].items() if e["net_view"] is not None]
                if lines:
                    with st.expander(f"What the last document day said ({pday})"):
                        st.markdown("\n".join(lines))
                        st.caption("Shown as it was, not faded with age. Whether older documents should count for less is a "
                                   "modelling question we have not answered, so we do not pretend to.")
        st.markdown("""<div class="rs-foot" style="margin-top:18px">
A view is withheld unless at least 8 past situations are genuinely comparable; that threshold was fixed in writing before any
result was seen. Where the documents and the history disagree, both are shown and no combined number is produced. We tested
whether their agreement predicts better outcomes — it does not — so agreement is displayed and changes no number.
No live performance figure is shown anywhere in this tool.</div>""", unsafe_allow_html=True)

# ==========================================================================
# LOOK UP AN ASSET
# ==========================================================================
with tabs[1]:
    ix = load_index()
    if ix is None or ix.empty:
        st.warning("No reports generated yet."); st.stop()
    st.markdown('<div class="g rs-banner"><h2>Look up any asset</h2><p>Enter a listed ticker. We identify which broad market it '
                'behaves like, pull its price history if we do not already hold it, and ask the same question of that asset\'s '
                'own record. Tickers outside the core universe take a few seconds.</p></div>', unsafe_allow_html=True)
    c = st.columns([1.2, 1.2, 1.2, .8])
    tk = c[0].text_input("Ticker", value="SMH", key="lookup_tk").strip().upper()
    lday = c[1].selectbox("Date", list(ix.date), index=len(ix) - 1, key="lookup_date")
    ax = c[2].selectbox("Market", ["decide for me", "equities", "bonds", "gold", "dollar", "oil"], key="lookup_axis")
    AXMAP = {"equities": "equity", "bonds": "duration", "gold": "gold", "dollar": "dollar", "oil": "oil"}
    c[3].write(""); c[3].write("")
    if c[3].button("Check", key="lookup_go", use_container_width=True):
        st.session_state["lookup_result"] = None
        with st.spinner("Checking history…"):
            try:
                import asset_extension as AE
                cfg = AE.load_config(); sc, rt = AE.load_data()
                ii = pd.DatetimeIndex(sc.index)
                lab = AE.regime_labels_expanding(sc, cfg)
                Z = AE._z_expanding(sc[AE.CLUSTERING_PCS].values)
                amap = AE.axis_map(cfg); docs = AE.load_reads()
                pos = ii.searchsorted(pd.DatetimeIndex(docs["date"].values), side="left"); ok = pos < len(ii)
                docs = docs.loc[ok].copy(); docs["session"] = ii[pos[ok]]
                for cc in ("magnitude", "specificity", "novelty", "confidence"):
                    docs[cc] = pd.to_numeric(docs.get(cc), errors="coerce")
                docs["weight"] = (docs.magnitude.fillna(0) * docs.specificity.fillna(0)
                                  * docs.novelty.fillna(0) * docs.confidence.fillna(0))
                t = pd.Timestamp(lday); ti = int(ii.get_loc(t))
                axis = amap.get(tk, ("equity", "?"))[0] if ax == "decide for me" else AXMAP[ax]
                st.session_state["lookup_result"] = (tk, lday, ax, AE.run_asset(
                    tk, axis, t, ti, ii, sc, rt, Z, lab, int(AE.DEFAULT["n_regimes"]),
                    docs[docs.session == t], docs[docs.session < t]))
            except FileNotFoundError as ex:
                st.error(f"**Missing data file:** `{ex.filename or ex}` — this tab runs the estimator live and needs the price "
                         "panel and document reads on disk.")
            except Exception as ex:
                st.error(f"Could not check {tk}: {type(ex).__name__}: {ex}")
    res = st.session_state.get("lookup_result")
    if res:
        tk, lday, ax, e = res
        head, colour, detail = verdict(e)
        nice = {"equity": "equities", "duration": "bonds", "gold": "gold", "dollar": "the dollar", "oil": "oil"}
        spec = dict(tk=tk, name=tk, unit="", fmt="{:,.2f}", chg="pct", vol=True, note="")
        q = quote(spec)
        qtxt = (f'<span class="big">{q["last"]:,.2f}</span><span class="d" style="color:{UP if q["chg"] >= 0 else DOWN}">'
                f'{q["pct"]:+.2%}</span><span class="t">as of {q["as_of"]:%d %b %Y} close · Yahoo Finance, delayed</span>') if q else ""
        st.markdown(f'<div class="g rs-banner"><div class="rs-quote"><span style="font-weight:700;font-size:1.1rem">{tk}</span>'
                    f'<span class="rs-pill" style="background:{PILL_BG[colour]};color:{colour}">{head}</span></div>'
                    f'<div class="rs-quote">{qtxt}</div><p style="margin-top:6px">{detail} · treated as a <b>{nice[e["axis"]]}</b> exposure</p></div>',
                    unsafe_allow_html=True)
        el = e.get("eligibility") or {}; est = e.get("estimate") or {}
        st.markdown(f"""
<div class="rs-tiles">
  <div class="g rs-tile"><div class="rs-k">Price history</div><div class="rs-v">{el.get('sessions_of_history', 0):,}</div><div class="rs-s">sessions from {el.get('first_priced', '—')}</div></div>
  <div class="g rs-tile"><div class="rs-k">Market conditions seen</div><div class="rs-v">{el.get('regimes_covered', '—')} <span style="color:{INK3};font-weight:500">of {el.get('regimes_total', 4)}</span></div><div class="rs-s">the limit on what history can say about it</div></div>
  <div class="g rs-tile"><div class="rs-k">Comparable situations</div><div class="rs-v">{f"{est['ess']:.0f}" if est else "—"}</div><div class="rs-s">{f"of {est['n_matched']} matched · history weight {est['w_shrink']:.2f}" if est else "no estimate"}</div></div>
  <div class="g rs-tile"><div class="rs-k">Prices</div><div class="rs-v" style="font-size:1rem">{el.get('price_source', '—')}</div></div>
</div>""", unsafe_allow_html=True)
        (period, interval), kind = chart_controls("lookup")
        st.markdown('<div class="g" style="padding:8px 8px 2px">', unsafe_allow_html=True)
        price_chart(fetch_bars(tk, period, interval), spec, kind, load_regimes(), lday)
        st.markdown('</div>', unsafe_allow_html=True)
        if ax == "decide for me" and el.get("price_source") and el.get("price_source") != "project price panel":
            st.info(f"We have no recorded classification for {tk}, so it was treated as an equity exposure by default. "
                    "If that is wrong, pick the right market above and run it again — the answer will change.")
        if not e.get("is_proxy"):
            st.markdown(f'<div class="rs-foot">The documents we read describe {nice[e["axis"]]} broadly. They say nothing specific to '
                        f'{tk}\'s own industry, so treat this as a market-level read, not a company-level one.</div>', unsafe_allow_html=True)

# ==========================================================================
# THE RECORD
# ==========================================================================
with tabs[2]:
    st.markdown('<div class="g rs-banner"><h2>The record</h2><p>What runs, what has been tested, and what the referee says. '
                'No performance figure appears here until the forward record can report an interval rather than a point.</p></div>',
                unsafe_allow_html=True)
    fl = PROC / "forward_ledger.csv"; n_rows = mat = 0
    if fl.exists():
        try:
            L = pd.read_csv(fl); n_rows = len(L); mat = int((L.get("status") == "matured").sum())
        except Exception:
            pass
    reads_dir = ROOT / "data_provenance" / "doc_reads"
    n_reads = len(list(reads_dir.glob("*.json"))) if reads_dir.exists() else 0
    bf = sorted(PROC.glob("report_scoreboard_backfill_*.json"), key=lambda p: p.stat().st_mtime)
    bf_verdict = ((jload(bf[-1]) or {}).get("verdict", "—") if bf else "—")
    bf_word = {"FAIL": "did not beat the market's own drift", "INCONCLUSIVE": "met one criterion of two",
               "PASS": "met both criteria"}.get(str(bf_verdict).upper(), str(bf_verdict))
    st.markdown(f"""
<div class="rs-tiles">
  <div class="g rs-tile"><div class="rs-k">Forward test</div><div class="rs-v">{n_rows}</div><div class="rs-s">rows since 19 Aug 2026; {mat} matured — too few to report</div></div>
  <div class="g rs-tile"><div class="rs-k">Documents read</div><div class="rs-v">{n_reads:,}</div><div class="rs-s">one schema, one prompt version, one model</div></div>
  <div class="g rs-tile"><div class="rs-k">Report referee · forward</div><div class="rs-v" style="font-size:1.05rem">too few to report</div><div class="rs-s">30 non-overlapping rows before any figure prints</div></div>
  <div class="g rs-tile"><div class="rs-k">Report referee · backfill</div><div class="rs-v" style="font-size:1.05rem">{bf_word}</div><div class="rs-s">directional calls, 3-session horizon, 1,500+ historical document days</div></div>
</div>""", unsafe_allow_html=True)
    st.markdown("""
**What was tested and rejected.** Gold does not reliably decouple from equities under liquidity stress. Sector rotation has no
stable running order — peers reprice in the overnight gap. A trend-aware model's advantage was a look-ahead in feature scaling.
The one surviving price model held on the full universe and not on the survivorship-controlled one.

**What the referee found.** The report's own short-horizon directional calls sit at, then below, what following the market's
drift would give — first inconclusive, then fail after one document source was rebuilt more completely and re-read. Both runs
are recorded side by side. The next phase leads with exposure, expected move and unfamiliarity rather than direction.

**The discipline.** Every threshold committed before the code that tests it; every null published; nearly thirty logged beliefs
overturned by running code. The full record — every registration, test and date — is in the repository:
[github.com/Wei-TingHsu/regime-aware-signal](https://github.com/Wei-TingHsu/regime-aware-signal).
""")
    with st.expander("Coming: log your own trades against the same referee"):
        st.markdown("A registered route adds a ledger for the user's own rules — entry, size, stop — written down or logged as an "
                    "actual fill, and scored by the same scorer as the models. It is the one action control that belongs on this "
                    "page: it records *your* decision rather than recommending one. Not yet built.")

# ==========================================================================
# HOW THIS WORKS
# ==========================================================================
with tabs[3]:
    st.markdown("""
Every trading day we read the policy and company documents published that day — Federal Reserve statements and minutes,
company earnings releases, executive orders and proclamations. A language model classifies each one: what it says, how
specific it is, how much of it was already public.

We separately identify which of **four broad market environments** today resembles, using macro data alone.

Then we ask one question: **when documents like today's landed in environments like today's, what happened next?** If enough
genuinely comparable situations exist, we report what they did. If they do not, we say so and give no number.

That last part is the product. Most days, for most markets, the honest answer is that there is no usable precedent — and a
tool that produced a number anyway would be worse than useless.
""")
    prof = load_profile()
    st.markdown('<div class="rs-section">The four market conditions, and what is in them</div>', unsafe_allow_html=True)
    if prof:
        rows = [{"Condition": f"{int(r)+1} of {len(prof['regimes'])}", "What it looks like": d["label"],
                 "Share of history": f"{d['share_pct']}%"} for r, d in sorted(prof["regimes"].items())]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        st.caption("Each description is the average of the macro series inside that condition, against their own long-run "
                   "averages. It describes; it does not validate.")
    st.markdown('<div class="rs-section">What is shown, and what is modelled</div>', unsafe_allow_html=True)
    st.markdown("The model runs on five ETFs — SPY, TLT, GLD, UUP, USO — because those are the tradeable, long-history proxies "
                "the estimator was built and tested on. The page shows the instruments a desk quotes — the S&P 500 index, the "
                "10-year Treasury yield, gold in dollars an ounce, the DXY dollar index, WTI crude — from Yahoo Finance, delayed "
                "about fifteen minutes. The one translation that matters: the model's Treasury view is on bond *prices*, so a "
                "positive read means yields expected *lower*. Live prices are display only; nothing on this page feeds the estimator. **Tested 29 September 2026:** the report was re-run with the five display instruments substituted for the ETFs; the verdict, the hit-rate and the asymmetry were unchanged within the registered tolerances (`docs/instrument_robustness.md`).")
    st.markdown('<div class="rs-section">What this cannot see</div>', unsafe_allow_html=True)
    ixx = load_index()
    R0 = load_report(ixx.iloc[-1].date) if ixx is not None and not ixx.empty else None
    if R0:
        for hh, b in R0["cannot_see"]:
            plain = b.replace("`transcript`", "earnings call transcripts").replace("`bank_research`", "sell-side research").replace("**", "")
            st.markdown(f"- **{hh}.** {plain}")
    st.markdown("**On the roadmap.** Four further government sources would let this system read *intentions* rather than only "
                "*decisions*; a blind-spot monitor would say, each day, how much of the market's move the covered sources can "
                "account for. Costed and registered, not built.")
    st.markdown("""<div class="rs-foot" style="margin-top:14px">
Every threshold in this system was written down and committed to version control before any result was looked at. Where a test
failed, the failure is recorded rather than the test rerun. No live performance figure is shown anywhere in this tool.</div>""",
                unsafe_allow_html=True)
