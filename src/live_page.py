"""live_page.py -- the 'Event-driven company signals' tab of app.py (also served by pages/Event_signals.py). It only DISPLAYS what the news listener
logs; it redraws itself every 30 seconds. The listener runs in its own terminal: caffeinate -i python -m src.news_listener run --poll 30"""
from __future__ import annotations
import time
from pathlib import Path
import streamlit as st
from src import live_view as V

REFRESH_S = 30; CANDIDATES = Path("docs/SOURCE_CANDIDATES.md")
CSS = """<style>
.sig{padding:10px 14px;border-radius:14px;border:1px solid rgba(20,23,31,.10);margin:8px 0 0 0;font-size:.88rem;line-height:1.45;background:rgba(255,255,255,.55)}
.sopen{background:rgba(234,246,239,.85);border-color:#178A4C}.swait{background:rgba(255,247,230,.85);border-color:#B7791F}.sshut{background:rgba(244,245,247,.7)}
.sbig{font-size:1.0rem;font-weight:700}.smut{color:#5F6672;font-size:.8rem}
/* founder, 21 Nov 2026: the three blocks are real blocks -- rounded like app icons, with a soft white-and-grey frosted background, text smaller than the other sections */
.blk{border-radius:22px;padding:16px 20px 18px 20px;margin:4px 0 16px 0;border:1px solid rgba(255,255,255,.75);outline:1px solid rgba(20,23,31,.07);
     background:linear-gradient(135deg,rgba(255,255,255,.82) 0%,rgba(240,242,246,.62) 55%,rgba(226,229,236,.55) 100%);-webkit-backdrop-filter:blur(18px) saturate(1.15);backdrop-filter:blur(18px) saturate(1.15);
     box-shadow:0 8px 28px rgba(20,23,31,.07), inset 0 1px 0 rgba(255,255,255,.9)}
.blk-title{font-size:1.02rem;font-weight:700;letter-spacing:.01em;color:#14171F}.blk-cap{font-size:.78rem;color:#5F6672;margin-top:2px}
</style>"""
PANEL_CSS = """<style>
/* every tab's content sits in the same kind of rounded frosted panel */
div[data-baseweb="tab-panel"], div[data-testid="stTabPanel"], div[role="tabpanel"]{border-radius:26px;padding:22px 26px 26px 26px;margin-top:14px;border:1px solid rgba(255,255,255,.8);outline:1px solid rgba(20,23,31,.06);
     background:linear-gradient(160deg,rgba(255,255,255,.72) 0%,rgba(243,244,248,.5) 60%,rgba(230,233,240,.45) 100%);-webkit-backdrop-filter:blur(22px) saturate(1.1);backdrop-filter:blur(22px) saturate(1.1);
     box-shadow:0 12px 40px rgba(20,23,31,.06), inset 0 1px 0 rgba(255,255,255,.9)}
</style>"""      # injected once by app.py for the whole app (apply_21nov_panels.py)


def _df(x, rows=None):
    kw = dict(hide_index=True) if rows is None else dict(hide_index=True, height=38 * (rows + 1))
    try: st.dataframe(x, width="stretch", **kw)
    except Exception: st.dataframe(x, use_container_width=True, **kw)


def _colour(minutes: float) -> str:
    """founder, 21 Nov 2026: counted from the RELEASE of the news -- red for the first 5 minutes, yellow from 5 to 10, green from 10 to 15, then the usual background"""
    if minutes < 5: return "background-color: #FF8A8A; color: #14171F"
    if minutes < 10: return "background-color: #FFE680; color: #14171F"
    if minutes < 15: return "background-color: #A8E6B4; color: #14171F"
    return ""


def _coloured(T, minutes: list):
    if not any(m < 15 for m in minutes): return T      # nothing recent: the plain table
    try:
        css = [_colour(m) for m in minutes]; num = [c for c in T.columns if str(T[c].dtype).startswith(("float", "int"))]
        return T.style.apply(lambda r: [css[r.name]] * len(r), axis=1).format(precision=2, na_rep="", subset=num)
    except Exception: return T


def _body(tz: str):
    D = V.load(); now = D["now"]; hb = D["heartbeat_s"]; Z = V.ZoneInfo(tz); live = hb is not None and hb < 180
    st.caption(f"Updated {now.astimezone(Z):%Y-%m-%d %H:%M:%S} local time · redraws every {REFRESH_S} seconds · " + (f"news listener running (last check {hb:.0f} seconds ago)" if live else "NEWS LISTENER NOT RUNNING" + (f" (last check {hb / 60:.0f} minutes ago)" if hb is not None else "")))
    if not live: st.warning("The news listener is not running, so nothing new can appear here.")

    def block(title, caption, cards): st.markdown(f"<div class='blk'><div class='blk-title'>{title}</div><div class='blk-cap'>{caption}</div>{''.join(cards)}</div>", unsafe_allow_html=True)

    act = [b for b in D["scored"] if b["action"].get("state") in ("before entry", "OPEN")]; cards = []
    for b in act:
        a = b["action"]; cls = "sopen" if a["state"] == "OPEN" else "swait"
        cards.append(f"<div class='sig {cls}'><span class='sbig'>{a['text']}</span><br>{V.RULE_NAMES.get(a['rule'], a['rule'])} · score {a['score']:+.2f} · {'open now' if a['state'] == 'OPEN' else 'not yet open'} · {a['minutes_left']} minutes left · exit at {a['exit'].astimezone(Z):%Y-%m-%d %H:%M} local time<br><span class='smut'>{b['source']}: {b['title']} — {V.kind_label(b)}</span></div>")
    if not cards: cards = ["<div class='sig sshut'><span class='sbig'>No suggestion right now.</span><br><span class='smut'>A suggestion appears when a company's financial results score 0.7 or more in size, or when the Fed issues a statement. It stays for the hour the rule covers.</span></div>"]
    block("Current High-Confidence Suggestions", "From a tested rule, while its hour is open. The strongest evidence on this page — still a candidate: each rule gets its verdict after 30 live trades (see Forward record).", cards)

    cards = []
    for b in D["alerts"][:6]:
        d = b["read"] or {}; cards.append(f"<div class='sig swait'><b>{b['ticker']}: reads as {V.direction(b)}</b> (own-stock score {V._num(d.get('own_stock')):+.2f}) · released {b['release'].astimezone(Z):%Y-%m-%d %H:%M} local time<br>{b['source']}: {b['title']} — {V.kind_label(b)}<br><span class='smut'>Information only: no tested trading rule exists yet for this kind of news.</span></div>")
    if not cards: cards = ["<div class='sig sshut'><span class='smut'>No alert in the last 24 hours.</span></div>"]
    block("Current Low-Confidence Alerts (no tested rule)", "News from the last 24 hours that reads strongly but has no tested trading rule. Information, not a trade suggestion: the kinds tested so far (short-seller reports, well-known investors' calls) moved the price before a user could act.", cards)

    cards = []
    for b in [x for x in D["scored"] if x["action"].get("state") in ("closed", "missed")][:3]:
        a = b["action"]; cards.append(f"<div class='sig sshut'><b>{'Ended:' if a['state'] == 'closed' else 'Arrived too late:'}</b> {a['text']} · {V.RULE_NAMES.get(a['rule'], a['rule'])} · score {a['score']:+.2f} · released {b['release'].astimezone(V.NY):%Y-%m-%d %H:%M} New York<br><span class='smut'>{b['source']}: {b['title']}</span></div>")
    if not cards: cards = ["<div class='sig sshut'><span class='smut'>None yet.</span></div>"]
    block("Past Suggestions (Reference)", "The three most recent suggestions whose hour is over, or that reached us too late to act on. For reference only.", cards)

    st.subheader("Scored news, newest first")
    items = D["scored"][:200]; T = V.table(items, tz, now)
    if len(T):
        st.markdown("<span class='smut'>Row colour = time since the source released the item: <span style='background:#FF8A8A;padding:1px 8px;border-radius:4px;color:#14171F'>under 5 minutes</span> <span style='background:#FFE680;padding:1px 8px;border-radius:4px;color:#14171F'>5 to 10 minutes</span> <span style='background:#A8E6B4;padding:1px 8px;border-radius:4px;color:#14171F'>10 to 15 minutes</span> no colour = released more than 15 minutes ago. An item that reaches us late never turns red: see the two Time Lag columns.</span>", unsafe_allow_html=True)
        _df(_coloured(T, [V.since_release(b, now) for b in items]), rows=15)
    else: st.info("Nothing scored yet.")
    st.caption("Source = where the item came from. What it is — Financial results: a company's quarterly report. Company announcement: any other item on the company's own news page or the news wire. Regulatory filing: a filing with the US regulator (SEC). Third-party report: research or an investigation by someone else, who may hold a position; its claims are not verified. Fed statement: the central bank's policy statement. "
               "Scores run from -1 (bad for the stock) to +1 (good). The two Time Lag columns show our speed: 'publish -> listener' is how many seconds after the source published the item our listener saw it; 'listener -> Claude responsiveness' is how many seconds Claude then took to return the score."
               + (f" {D['old_hidden']} older items, read when a source was first connected, are not shown." if D["old_hidden"] else "") + (f" {D['duplicates']} second copies of a release already scored were not scored again." if D["duplicates"] else ""))

    st.subheader("Forward record")
    R = D["record"]
    if len(R): _df(R.rename(columns={"name": "Rule", "rule": "Code", "trades": "Live trades priced", "average_pct": "Average per trade, % before cost", "right_on": "Right on, %"})); st.caption("The forward record counts live cases as they happen. A rule gets a verdict only after 30 live trades.")
    else: st.info("No live trade has been priced yet.")

    with st.expander("How the suggestions are made (rules, evidence, limits)"):
        for r in V.RULES: st.markdown(f"**{r['name']}** ({r['id']}) — {r['text']}  \n<span class='smut'>{r['evidence']}</span>", unsafe_allow_html=True)
        st.caption(V.STATUS + " Scores are Claude's reading of the document alone. The tests behind the rules covered only the first hour after a release; a score says nothing tested about later days.")
    with st.expander("Waiting for a test (strong news with no tested rule, and sources not yet admitted)"):
        U = D["untested"]
        if len(U): st.markdown("**Seen live, strong, no rule yet**"); _df(U)
        if CANDIDATES.exists(): st.markdown(CANDIDATES.read_text())
        elif not len(U): st.caption("Nothing is waiting.")


def render():
    st.markdown(CSS, unsafe_allow_html=True)
    c1, c2 = st.columns([1, 3]); tz = c1.selectbox("Local time zone", ["Asia/Singapore", "Asia/Taipei", "America/New_York", "Europe/London"], index=0, key="ev_tz")
    if hasattr(st, "fragment"): st.fragment(run_every=REFRESH_S)(_body)(tz); return
    auto = c2.checkbox(f"Redraw every {REFRESH_S} seconds", value=True, key="ev_auto"); _body(tz)      # older Streamlit: the whole app is redrawn
    if auto: time.sleep(REFRESH_S); (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()
