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
st.title("Event signals"); tz = st.selectbox("Local time zone", ["Asia/Singapore", "Asia/Taipei", "America/New_York", "Europe/London"], index=0, key="tz")


def _df(x):
    try: st.dataframe(x, width="stretch", hide_index=True)      # newer Streamlit
    except Exception: st.dataframe(x, use_container_width=True, hide_index=True)


def body():
    D = V.load(); now = D["now"]; hb = D["heartbeat_s"]
    live = hb is not None and hb < 180
    st.caption(f"Updated {now.astimezone(V.NY):%H:%M:%S} New York · refreshes every {REFRESH_S} seconds · " + ("news listener running (last check " + f"{hb:.0f} s ago)" if live else "NEWS LISTENER NOT RUNNING" + (f" (last check {hb / 60:.0f} min ago)" if hb is not None else "") + " — start it in a terminal: caffeinate -i python -m src.news_listener run --poll 30"))
    if not live: st.warning("The listener is not running, so nothing new can appear here. This page only displays what the listener logs.")
    st.subheader("Rules in force")
    for r in V.RULES: st.markdown(f"**{r['id']}** — {r['text']}  \n<span class='mut'>{r['evidence']}</span>", unsafe_allow_html=True)
    st.caption(V.STATUS)
    st.subheader("Signal windows")
    act = [b for b in D["scored"] if b["action"].get("state") in ("before entry", "OPEN")]; recent = [b for b in D["scored"] if b["action"].get("state") == "closed"][:3]
    if not act: st.markdown("<div class='sig shut'><span class='big'>No signal window is open.</span><br><span class='mut'>A window opens when a results release scores 0.7 or more in size, or when the Fed issues a statement.</span></div>", unsafe_allow_html=True)
    for b in act:
        a = b["action"]; cls = "open" if a["state"] == "OPEN" else "wait"
        st.markdown(f"<div class='sig {cls}'><span class='big'>{a['text']}</span><br>{a['rule']} · score {a['score']:+.2f} · {a['state']} · {a['minutes_left']} min left · exit {a['exit'].astimezone(V.ZoneInfo(tz)):%H:%M} local<br><span class='mut'>{b['title']} — {b['source']}</span></div>", unsafe_allow_html=True)
    for b in recent:
        a = b["action"]; st.markdown(f"<div class='sig shut'><b>Closed:</b> {a['text']} · {a['rule']} · score {a['score']:+.2f} · released {b['release'].astimezone(V.NY):%d %b %H:%M} New York<br><span class='mut'>{b['title']}</span></div>", unsafe_allow_html=True)
    st.subheader("Scored news")
    T = V.table(D["scored"][:40], tz)
    if len(T): _df(T)
    else: st.info("Nothing scored yet.")
    st.subheader("Forward record")
    R = D["record"]
    if len(R): _df(R.rename(columns={"rule": "Rule", "trades": "Trades priced", "average_pct": "Average per trade, % before cost", "right_on": "Right on, %"})); st.caption("No verdict before 30 trades per rule. Updated by: python -m src.live_outcomes ledger")
    else: st.info("No live trade has been priced yet. After an event: python -m src.live_outcomes fetch, then ledger.")
    with st.expander(f"Other items seen, not scored ({len(D['other'])})"):
        O = V.table(D["other"][:60], tz)
        if len(O): _df(O[["Released (New York)", "Local time", "Company", "Type", "Headline", "Source"]])
    st.caption("Sources: the companies' own releases and filings, PR Newswire, the SEC, the Federal Reserve. Scores are Claude's reading of the document alone. Times are the release time as the source states it. The backtests behind the rules tested only the first hour after a release; a score says nothing tested about later days.")


if hasattr(st, "fragment"):
    st.fragment(run_every=REFRESH_S)(body)()
else:      # older Streamlit: redraw the whole page every 30 seconds
    body(); time.sleep(REFRESH_S); (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()
