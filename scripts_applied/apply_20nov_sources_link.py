"""apply_20nov_sources_link.py -- (1) docs/SOURCES.md: the register of news sources, so the list never has to be repeated; (2) a link from the main page
to 'Event signals' (the app hides Streamlit's header, which also hid the page menu); (3) TRACK 3.72 and the standing rules. Idempotent."""
from pathlib import Path
SOURCES = """# Source register — every place the engine listens, and every place the founder has asked for

**Why this file exists (founder, 20 Nov 2026):** "I am very sure I have mentioned a lot of the sources previously and these should have been recorded
somewhere … so that I avoid mentioning the list to add many times." Checked on 20 Nov: SemiAnalysis and Hunterbrook were NOT written in any project
file before today (the files held only the data-source list in `SPEC_GRID.md` §3 and the 'provisional source pool' idea of the blind-spot monitor).
From now on every source named by the founder is written here the day it is named, with its status.

**Rules.** (1) A source is scored only on items published AFTER its admission date; an item that made the founder add the source is not credited to
it. (2) Company and official sources are primary. A THIRD PARTY (research firm, or an investor that publishes and may hold a position, such as a short
seller) is admitted as its own class: every item is labelled "third-party report, claims unverified", scored by its own reader, never pooled with
company news, and has no trading rule until one is tested. (3) Anonymous posts and unsourced rumours are not admitted. (4) Never Wikipedia.

## Live listener (`src/news_listener.py`)

| class | source | route | admitted | status |
|---|---|---|---|---|
| company | NVIDIA newsroom | company feed | 15 Nov 2026 | live |
| company | AMD investor page | company feed | 15 Nov 2026 | live |
| company | Meta investor page | company feed | 15 Nov 2026 | live |
| company | SK Hynix newsroom | company feed | 15 Nov 2026 | live |
| wire | PR Newswire (all releases; earnings) | wire feed | 15 Nov 2026 | live (carries Meta, Oracle, Broadcom, Microsoft) |
| regulator | SEC filings of all fourteen companies | SEC filing list | 15 Nov 2026 | live; the backup for every company, minutes later |
| central bank | Federal Reserve monetary-policy press releases | Fed feed | 15 Nov 2026 | live |
| third party | **Hunterbrook** (publishes investigations and may trade on them) | publisher feed (candidate addresses; `once` shows which answers) | **20 Nov 2026** | added; first item to be seen live |
| third party | **SemiAnalysis** (semiconductor and AI research) | publisher feed (candidates) | **20 Nov 2026** | added; paid articles are scored from the public part only |
| wire | Business Wire (Intel, Amazon, CrowdStrike, SanDisk) | refuses scripts | — | not reachable live; SEC route used |
| wire | GlobeNewswire (NVIDIA, AMD, Micron) | refuses scripts | — | not reachable live; company feeds / SEC route used |

## Asked for by the founder, not yet connected

| source | asked | note |
|---|---|---|
| Other funds and research houses that publish reports on the listed companies ("famous capital companies such as Hunterbrook") | 20 Nov 2026 | name each one here when the founder names it; each needs a feed that answers |
| Anthropic and OpenAI (companies) | 12 Nov 2026 | to join the company list once listed |
| Media reports of company events before the company files | 15 Nov 2026 (raised by the test's limits) | no free, timed, primary route found |

## Research data sources (not news): see `SPEC_GRID.md` §3.
"""
T = """
### 3.72 Third-party research publishers admitted as a source class; source register; no more Databento spending (20 Nov)
**Founder (20 Nov):** include research reports such as SemiAnalysis and funds that publish such as Hunterbrook; Hunterbrook's report on AMD of 19 Nov moved AMD about 9% lower (his figure) and the listener saw nothing; the sources he names must be recorded so he does not repeat them; the live page must be reachable and refresh itself; **Databento credit is not to be used from now on.**
**Checked.** Neither name was in any project file before today (search of `docs/`); recorded now in `docs/SOURCES.md`, which is the register from here on.
**Built.** (1) Listener: a `research` class with Hunterbrook and SemiAnalysis (candidate feed addresses; the first that answers is used). An item is taken when its title or summary names a listed company; it is scored by its own reader `ai-research-v1-2026-11-20` against the company's latest results (stance, new information, material, free-cash-flow outlook, uncertainty, own stock, other companies, main claims), labelled 'third-party report, claims unverified'. Paid articles are scored from the public part. No trading rule: alert only, until a test exists. Admission date 20 Nov: the 19 Nov AMD report is not credited; `python -m src.news_listener research --ticker AMD` scores the newest such report as a drill. Each event and report now keeps its own saved read (two items from one source on one day no longer share one). (2) Forward record prices: Yahoo's free 1-minute bars (kept about a week); no paid data. Lower quality than exchange data, stated. (3) Main page: a link to 'Event signals' (the app's own style sheet hides Streamlit's header, and with it the page menu).
**Product question, open:** for a user the listener and the page must run all day on a server, not on the founder's laptop; estimated at a few US dollars a month for a small server plus cents of scoring; founder's decision.
"""
RULE = """
### Standing rules added 20 Nov 2026
- **No Databento spending** (founder, 20 Nov): the app no longer shows 1-minute prices, and no paid market data is requested. The forward record prices events with Yahoo's free 1-minute bars.
- **Source register**: every source the founder names is written into `docs/SOURCES.md` the day it is named.
"""
p = Path("docs/SOURCES.md")
if p.exists() and "Source register" in p.read_text(): print("  docs/SOURCES.md: already present -- skipped")
else: p.write_text(SOURCES); print("  docs/SOURCES.md: written (source register)")
for path, marker, text in (("docs/TRACK.md", "### 3.72 Third-party research publishers admitted", T), ("docs/PROJECT_MASTER.md", "### Standing rules added 20 Nov 2026", RULE)):
    q = Path(path); s = q.read_text()
    if marker in s: print(f"  {path}: already recorded -- skipped")
    else: q.write_text(s.rstrip("\n") + "\n" + text); print(f"  {path}: recorded")
a = Path("app.py"); s = a.read_text(); anchor = 'tabs = st.tabs(["Today", "Look up an asset"'
link = 'try: st.page_link("pages/Event_signals.py", label="Event signals: live company news, scores and rule windows →")      # 20 Nov: the header (and its page menu) is hidden by the style sheet\nexcept Exception: pass\n'
if 'st.page_link("pages/Event_signals.py"' in s: print("  app.py: link already present -- skipped")
elif s.count(anchor) != 1: print("  app.py: the tabs line was not found exactly once -- NOT changed; tell Claude")
else: a.write_text(s.replace(anchor, link + anchor)); print("  app.py: link to 'Event signals' added above the tabs (one line; nothing else changed)")
