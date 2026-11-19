"""Event signals -- live company news and Fed statements, scored on release, with the rule in force. Refreshes itself every 30 seconds.
It only DISPLAYS what the listener logs; keep the listener running in a terminal:  caffeinate -i python -m src.news_listener run --poll 30"""
from __future__ import annotations
import sys, time
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import os
os.chdir(ROOT)
from src import live_view as V

REFRESH_S = 30
st.set_page_config(page_title="Event signals", page_icon="◐", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>.sig{padding:14px 18px;border-radius:12px;border:1px solid rgba(20,23,31,.12);margin:6px 0 10px 0}.open{background:#EAF6EF;border-color:#178A4C}.wait{background:#FFF7E6;border-color:#B7791F}.shut{background:#F4F5F7}.big{font-size:1.25rem;font-weight:700}.mut{color:#5F6672;font-size:.86rem}</style>", unsafe_allow_html=True)
try: st.page_link("app.py", label="← Main page")
except Exception: pass
st.title("Event signals"); tz = st.selectbox("Local time zone", ["Asia/Singapore", "Asia/Taipei", "America/New_York", "Europe/London"], index=0, key="tz")


def _df(x):
    try: st.dataframe(x, width="stretch", hide_index=True)      # newer Streamlit
    except Exception: st.dataframe(x, use_container_width=True, hide_index=True)


def body():
    D = V.load(); now = D["now"]; hb = D["heartbeat_s"]; Z = V.ZoneInfo(tz); live = hb is not None and hb < 180
    st.caption(f"Updated {now.astimezone(Z):%Y-%m-%d %H:%M:%S} local time · refreshes every {REFRESH_S} seconds · " + (f"news listener running (last check {hb:.0f} s ago)" if live else "NEWS LISTENER NOT RUNNING" + (f" (last check {hb / 60:.0f} min ago)" if hb is not None else "")))
    if not live: st.warning("The news listener is not running, so nothing new can appear here.")

    st.subheader("Suggestions")
    act = [b for b in D["scored"] if b["action"].get("state") in ("before entry", "OPEN")]
    if not act: st.markdown("<div class='sig shut'><span class='big'>No suggestion right now.</span><br><span class='mut'>A suggestion appears when a company's financial results score 0.7 or more in size, or when the Fed issues a statement. It stays for the hour the rule covers.</span></div>", unsafe_allow_html=True)
    for b in act:
        a = b["action"]; cls = "open" if a["state"] == "OPEN" else "wait"
        st.markdown(f"<div class='sig {cls}'><span class='big'>{a['text']}</span><br>Score {a['score']:+.2f} · {'open now' if a['state'] == 'OPEN' else 'not yet open'} · {a['minutes_left']} minutes left · exit at {a['exit'].astimezone(Z):%Y-%m-%d %H:%M} local time<br><span class='mut'>{V.kind_label(b)}: {b['title']} — {b['source']}</span></div>", unsafe_allow_html=True)
    for b in D["alerts"][:6]:
        d = b["read"] or {}; st.markdown(f"<div class='sig wait'><b>{b['ticker']}: {V.kind_label(b)}, reads as {V.direction(b)}</b> (own-stock score {V._num(d.get('own_stock')):+.2f}) · released {b['release'].astimezone(Z):%Y-%m-%d %H:%M} local time<br>{b['title']} — {b['source']}<br><span class='mut'>Information only: no tested trading rule exists for this kind of news.</span></div>", unsafe_allow_html=True)
    done = [b for b in D["scored"] if b["action"].get("state") == "closed"][:3]
    for b in done:
        a = b["action"]; st.markdown(f"<div class='sig shut'><b>Ended:</b> {a['text']} · score {a['score']:+.2f} · released {b['release'].astimezone(V.NY):%Y-%m-%d %H:%M} New York<br><span class='mut'>{b['title']}</span></div>", unsafe_allow_html=True)

    st.subheader("Scored news, newest first")
    T = V.table(D["scored"][:60], tz)
    if len(T): _df(T)
    else: st.info("Nothing scored yet.")
    st.caption("What it is — Financial results: a company's quarterly report. Company announcement: any other item on the company's own news page or the news wire. Regulatory filing: a filing with the US regulator (SEC). Third-party report: research or an investigation by someone else, who may hold a position; its claims are not verified. Fed statement: the central bank's policy statement. "
               "Scores run from -1 (bad for the stock) to +1 (good)." + (f" {D['old_hidden']} older items, read when a source was first connected, are not shown." if D["old_hidden"] else "") + (f" {D['duplicates']} second copies of a release already scored were not scored again." if D["duplicates"] else ""))

    st.subheader("Forward record")
    R = D["record"]
    if len(R): _df(R.rename(columns={"rule": "Rule", "trades": "Trades priced", "average_pct": "Average per trade, % before cost", "right_on": "Right on, %"})); st.caption("No verdict before 30 trades per rule.")
    else: st.info("No live trade has been priced yet.")

    with st.expander("How the suggestions are made (rules, evidence, limits)"):
        for r in V.RULES: st.markdown(f"**{r['id']}** — {r['text']}  \n<span class='mut'>{r['evidence']}</span>", unsafe_allow_html=True)
        st.caption(V.STATUS + " Sources: the companies' own releases and filings, PR Newswire, the SEC, the Federal Reserve, and named research publishers. Scores are Claude's reading of the document alone. The tests behind the rules covered only the first hour after a release; a score says nothing tested about later days.")


if hasattr(st, "fragment"):
    st.fragment(run_every=REFRESH_S)(body)()
else:      # older Streamlit: redraw the whole page every 30 seconds
    body(); time.sleep(REFRESH_S); (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()
