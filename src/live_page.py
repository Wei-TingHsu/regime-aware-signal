"""live_page.py -- the 'Event-driven company signals' tab of app.py (also served by pages/Event_signals.py). It only DISPLAYS what the news listener
logs; it redraws itself every 30 seconds. The listener runs in its own terminal: caffeinate -i python -m src.news_listener run --poll 30"""
from __future__ import annotations
import time
from pathlib import Path
import streamlit as st
from src import live_view as V

REFRESH_S = 30; CANDIDATES = Path("docs/SOURCE_CANDIDATES.md")
CSS = "<style>.sig{padding:14px 18px;border-radius:12px;border:1px solid rgba(20,23,31,.12);margin:6px 0 10px 0}.sopen{background:#EAF6EF;border-color:#178A4C}.swait{background:#FFF7E6;border-color:#B7791F}.sshut{background:#F4F5F7}.sbig{font-size:1.25rem;font-weight:700}.smut{color:#5F6672;font-size:.86rem}</style>"


def _df(x, rows=None):
    kw = dict(hide_index=True) if rows is None else dict(hide_index=True, height=38 * (rows + 1))
    try: st.dataframe(x, width="stretch", **kw)
    except Exception: st.dataframe(x, use_container_width=True, **kw)


def _body(tz: str):
    D = V.load(); now = D["now"]; hb = D["heartbeat_s"]; Z = V.ZoneInfo(tz); live = hb is not None and hb < 180
    st.caption(f"Updated {now.astimezone(Z):%Y-%m-%d %H:%M:%S} local time · redraws every {REFRESH_S} seconds · " + (f"news listener running (last check {hb:.0f} seconds ago)" if live else "NEWS LISTENER NOT RUNNING" + (f" (last check {hb / 60:.0f} minutes ago)" if hb is not None else "")))
    if not live: st.warning("The news listener is not running, so nothing new can appear here.")

    st.subheader("Suggestions")
    act = [b for b in D["scored"] if b["action"].get("state") in ("before entry", "OPEN")]
    if not act: st.markdown("<div class='sig sshut'><span class='sbig'>No suggestion right now.</span><br><span class='smut'>A suggestion appears when a company's financial results score 0.7 or more in size, or when the Fed issues a statement. It stays for the hour the rule covers.</span></div>", unsafe_allow_html=True)
    for b in act:
        a = b["action"]; cls = "sopen" if a["state"] == "OPEN" else "swait"
        st.markdown(f"<div class='sig {cls}'><span class='sbig'>{a['text']}</span><br>{V.RULE_NAMES.get(a['rule'], a['rule'])} · score {a['score']:+.2f} · {'open now' if a['state'] == 'OPEN' else 'not yet open'} · {a['minutes_left']} minutes left · exit at {a['exit'].astimezone(Z):%Y-%m-%d %H:%M} local time<br><span class='smut'>{b['source']}: {b['title']} — {V.kind_label(b)}</span></div>", unsafe_allow_html=True)
    for b in D["alerts"][:6]:
        d = b["read"] or {}; st.markdown(f"<div class='sig swait'><b>{b['ticker']}: reads as {V.direction(b)}</b> (own-stock score {V._num(d.get('own_stock')):+.2f}) · released {b['release'].astimezone(Z):%Y-%m-%d %H:%M} local time<br>{b['source']}: {b['title']} — {V.kind_label(b)}<br><span class='smut'>Information only: no tested trading rule exists yet for this kind of news.</span></div>", unsafe_allow_html=True)
    for b in [x for x in D["scored"] if x["action"].get("state") == "closed"][:3]:
        a = b["action"]; st.markdown(f"<div class='sig sshut'><b>Ended:</b> {a['text']} · {V.RULE_NAMES.get(a['rule'], a['rule'])} · score {a['score']:+.2f} · released {b['release'].astimezone(V.NY):%Y-%m-%d %H:%M} New York<br><span class='smut'>{b['source']}: {b['title']}</span></div>", unsafe_allow_html=True)

    st.subheader("Scored news, newest first")
    T = V.table(D["scored"][:200], tz)
    if len(T): _df(T, rows=15)
    else: st.info("Nothing scored yet.")
    st.caption("Source = where the item came from. What it is — Financial results: a company's quarterly report. Company announcement: any other item on the company's own news page or the news wire. Regulatory filing: a filing with the US regulator (SEC). Third-party report: research or an investigation by someone else, who may hold a position; its claims are not verified. Fed statement: the central bank's policy statement. "
               "Scores run from -1 (bad for the stock) to +1 (good). The two delay columns show our speed: how many seconds after the source published the item our listener saw it, and how many seconds later Claude's score was ready."
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
