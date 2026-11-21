"""apply_21nov_panels.py -- founder, 21 Nov: every tab's content sits in a rounded, frosted white-and-grey panel; the three blocks of the live tab are
real blocks with smaller text. One line is added to app.py after its style sheet; TRACK 3.88. All-or-nothing; idempotent."""
from pathlib import Path
a = Path("app.py"); s = a.read_text(); anchor = "st.markdown(CSS, unsafe_allow_html=True)\n"
line = "try:\n    from src import live_page as _lp_css; st.markdown(_lp_css.PANEL_CSS, unsafe_allow_html=True)      # 21 Nov 2026: each tab's content in a rounded frosted panel\nexcept Exception: pass\n"
if "_lp_css.PANEL_CSS" in s: print("  app.py: the panel style is already there -- skipped")
elif s.count(anchor) != 1: print("  app.py NOT changed -- the style-sheet line was not found exactly once. Tell Claude.")
else: a.write_text(s.replace(anchor, anchor + line)); print("  app.py: panel style added after the style sheet (one line)")
t = Path("docs/TRACK.md"); x = t.read_text()
A = """

### 3.88 Look of the page: blocks and tab panels (21 Nov 14:00)
**Founder (21 Nov):** the three blocks of the live tab must look like blocks -- rounded like app icons ('smooth edge'), with a blurred white-and-grey background, and their text smaller than sections such as 'Scored news'; every other tab gets the same rounded panel around its content.
**Applied.** `src/live_page.py`: each of the three blocks is one rounded frosted panel (title 1.02rem, text 0.88rem; section titles elsewhere stay larger); the cards inside keep their colours (green = open suggestion, amber = alert, grey = past). `app.py` (one line, `apply_21nov_panels.py`): a style that puts the content of EVERY tab in a rounded frosted panel. Checked on Streamlit 1.67 with a small copy of the page; the founder's Streamlit version may name the tab area differently, so the style names three variants.
"""
if "### 3.88 Look of the page" not in x: t.write_text(x.rstrip("\n") + A); print("  TRACK.md: 3.88 added")
else: print("  TRACK.md: 3.88 already there -- skipped")
