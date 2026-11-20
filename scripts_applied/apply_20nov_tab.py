"""apply_20nov_tab.py -- founder's page instructions of 20 Nov, applied to app.py: (1) the main title is the largest text on the page; (2) the live
view becomes a TAB named 'Event-driven company signals', placed after 'Look up an asset' (the link added earlier is removed); (3) the list of sources
and news kinds waiting for a test (docs/SOURCE_CANDIDATES.md); (4) TRACK 3.74. All-or-nothing on app.py; idempotent."""
from pathlib import Path
a = Path("app.py"); s = a.read_text(); NEW_TAB = "Event-driven company signals"
old_tabs = 'tabs = st.tabs(["Today", "Look up an asset", "The record", "How this works", "Reading this page"])'
new_tabs = f'tabs = st.tabs(["Today", "Look up an asset", "{NEW_TAB}", "The record", "How this works", "Reading this page"])'
link = 'try: st.page_link("pages/Event_signals.py", label="Event signals: live company news, scores and rule windows →")      # 20 Nov: the header (and its page menu) is hidden by the style sheet\nexcept Exception: pass\n'
css_old = ".rs-wordmark {{ font-weight:700; font-size:1.15rem;"; css_new = ".rs-wordmark {{ font-weight:800; font-size:2.3rem; line-height:1.15;"
tail = f'''

# ==========================================================================
# {NEW_TAB.upper()}  (tab 3; added 20 Nov 2026 -- src/live_page.py draws it and redraws it every 30 seconds)
# ==========================================================================
with tabs[2]:
    from src import live_page as _live_page
    _live_page.render()
'''
if NEW_TAB in s: print("  app.py: the tab is already there -- skipped")
else:
    checks = {"the tabs line": s.count(old_tabs) == 1, "tab 3 block": s.count("with tabs[2]:") == 1, "tab 4 block": s.count("with tabs[3]:") == 1, "tab 5 block": s.count("with tabs[4]:") == 1, "the title style": s.count(css_old) == 1}
    if not all(checks.values()): print("  app.py NOT changed -- these were not found exactly once: " + ", ".join(k for k, v in checks.items() if not v) + ". Tell Claude.")
    else:
        s = s.replace(link, "").replace(old_tabs, new_tabs).replace("with tabs[4]:", "with tabs[5]:").replace("with tabs[3]:", "with tabs[4]:").replace("with tabs[2]:", "with tabs[3]:").replace(css_old, css_new)
        a.write_text(s.rstrip("\n") + tail); print(f"  app.py: title enlarged; tab '{NEW_TAB}' added after 'Look up an asset'; the three later tabs moved one place right; the earlier link removed")
C = """### Sources and kinds of news waiting for a test

A source is read and scored for money only after a test shows that its items move prices. Until then it waits here. (Founder, 20 Nov 2026: "we need
to know how strong these sources can influence the market; if it doesn't, there is no need to waste money in scoring and reading it.")

| what | examples named by the founder | test | status |
|---|---|---|---|
| Institutions that publish short reports | Hunterbrook; others to be listed from the probe | SR-1: the target's price on the day of the report and on each of the next 7 sessions, one by one; each publisher on its own | registered 20 Nov; collecting the report lists |
| Well-known investors who make public calls on a stock | Michael Burry; others to be named | SR-2: the same reaction test; and whether two or more calls in the same direction within two weeks move the price more than one alone | registered 20 Nov; needs a dated list of calls |
| News media | Reuters, Bloomberg, CNBC, Seeking Alpha | SR-3: whether their items about the listed companies move the price on the day and the next 7 sessions | registered 20 Nov; after SR-1 and SR-2 |
| Research publishers | SemiAnalysis | read live since 20 Nov as information only; reaction test with SR-1's method once enough items exist | live, no rule |

New source addresses found later by the discovery search are added to this table automatically, with the date found.
"""
p = Path("docs/SOURCE_CANDIDATES.md")
if p.exists(): print("  docs/SOURCE_CANDIDATES.md: already present -- skipped")
else: p.write_text(C); print("  docs/SOURCE_CANDIDATES.md: written")
T = """
### 3.74 Page as a tab; rules renamed; short reports, public calls and media registered as tests SR-1 to SR-3; discovery plan simplified (20 Nov 02:00)
**Founder's instructions (20 Nov).** (a) The main title must be the largest text. (b) The live view is to be a tab like 'Look up an asset', named 'Event-driven company signals'. (c) Swap the places of 'Source' and 'What it is'. (d) Show 15 rows of scored news. (e) Rename the rules; 'market-score rule' and 'step rule' are not understandable after a few days. (f) Test what is only 'information' today: institutions that publish short reports, each on its own; well-known investors' calls (Michael Burry and others); his hypothesis that one call alone makes no ripple but two or more in the same direction within two weeks bring 'sensational fear'; the reaction on the day and on each of the next 1-7 sessions separately, because a short may be closed before seven sessions. (g) Media (Reuters, Bloomberg, CNBC, Seeking Alpha) only after the same test shows they move prices. (h) The discovery search (Gemini) is an IDENTIFICATION layer: it finds new source addresses for the library; it does not score, and no separate date check is wanted. (i) New routes and untested strong items are to be written down automatically and he is to be reminded daily.
**Applied.** (a)-(d) in `app.py` and `src/live_page.py`. (e) Names: FA-4 **Strong-results rule**; FA-3 **Sector-reading rule**; QC-3 **Overnight Nasdaq rule**; FA-1 **Fed-statement rule**; FA-2 **Fed-day gold rule**; CV-1 **What a user could have done** (codes kept as record keys). (i) `docs/SOURCE_CANDIDATES.md` and a 'Waiting for a test' section on the tab, which also lists live items that read strongly but have no rule.
**Registered, stage A only (no price looked at).** SR-1 short-report publishers: collect each publisher's own list of reports with dates; the target and direction read from the title and summary; daily closes; market-adjusted reaction on day 0 and on each of sessions +1 to +7 one by one; per publisher and pooled. SR-2 public calls by named investors: a dated list from a news search by person and month; the same reaction test; clusters (two or more people, same direction, within ten sessions) against single calls. SR-3 media: the same test by publisher. Stage A is `python -m src.source_probe`: which publishers' archives and which news-search feeds answer, and how far back. Priors and exact cells are fixed in stage B, before prices.
**Plan agreed for discovery:** two layers only -- the listener reads the library; the search layer proposes new addresses into SOURCE_CANDIDATES, which are tested before they are read for money.
"""
t = Path("docs/TRACK.md"); s2 = t.read_text()
if "### 3.74 Page as a tab; rules renamed" in s2: print("  TRACK: 3.74 already present -- skipped")
else: t.write_text(s2.rstrip("\n") + "\n" + T); print("  TRACK: 3.74 appended")
