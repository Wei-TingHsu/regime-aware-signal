"""Event signals -- the same view as the 'Event-driven company signals' tab of app.py, kept so the old address still works."""
from __future__ import annotations
import os, sys
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from src import live_page
st.set_page_config(page_title="Event-driven company signals", page_icon="◐", layout="wide", initial_sidebar_state="collapsed")
try: st.page_link("app.py", label="← Main page")
except Exception: pass
st.title("Event-driven company signals"); live_page.render()
