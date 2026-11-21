# Source register — every place the engine listens, and every place the founder has asked for

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
| third party | **Grizzly Research** (publishes short reports; may hold a short position) | publisher feed | **21 Nov 2026** | live as ALERTS (no rule); admitted after SR-1 (TRACK 3.85) |
| third party | **Blue Orca** (short and some long reports; may hold a position) | publisher feed | **21 Nov 2026** | live as ALERTS (no rule) |
| third party | **Fuzzy Panda** (publishes short reports; may hold a short position) | publisher feed | **21 Nov 2026** | live as ALERTS (no rule) |
| wire | Business Wire (Intel, Amazon, CrowdStrike, SanDisk) | refuses scripts | — | not reachable live; SEC route used |
| wire | GlobeNewswire (NVIDIA, AMD, Micron) | refuses scripts | — | not reachable live; company feeds / SEC route used |

## Asked for by the founder, not yet connected

| source | asked | note |
|---|---|---|
| Other funds and research houses that publish reports on the listed companies ("famous capital companies such as Hunterbrook") | 20 Nov 2026 | name each one here when the founder names it; each needs a feed that answers |
| Anthropic and OpenAI (companies) | 12 Nov 2026 | to join the company list once listed |
| Media reports of company events before the company files | 15 Nov 2026 (raised by the test's limits) | no free, timed, primary route found |

## Research data sources (not news): see `SPEC_GRID.md` §3.
