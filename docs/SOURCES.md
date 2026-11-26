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

## Trading costs and single-stock funds (22 Nov 2026)
| source | what it is used for | status |
|---|---|---|
| The founder's broker, fee board 'US shares, ordinary orders' (screenshots, 22 Nov 2026) | the real fees in `src/real_cost.py` | primary (the founder's own account) |
| Direxion, 'Single Stock ETFs List' (direxion.com/uploads/Single-Stock-ETFs-List.pdf) | which stocks have a 2x long or a 1x inverse fund | issuer's own list; each fund also checked against prices |
| GraniteShares, product guide (graniteshares.com) | 2x long and 2x short single-stock funds | issuer's own list; checked against prices |
| REX Shares, 'T-REX leveraged ETFs' (rexshares.com/t-rex-leveraged-etfs) | 2x long and 2x inverse single-stock funds | issuer's own list; checked against prices |
| Tradr (TSLQ, NVDS) | two more inverse funds | named from memory, claims unverified; used only if the price check agrees |
| Yahoo Finance daily prices with splits (free) | real share prices of each day, the funds' prices | secondary data vendor, free |
| TrendForce press centre, Semiconductors (trendforce.com/presscenter/news/Semiconductors; feed trendforce.com/feed/Semiconductors.html) | research releases on memory, foundry, servers | third party, claims unverified; date only, no time of day; free |
| Reuters, 'AI credit default swap spreads widen on unease over cash flow' (24 Nov 2026); Investing.com, 'U.S. chip stocks extend losses premarket as AI spending concerns resurface' (25 Nov 2026) | the event behind test LI-1 | news reports, headlines read; single-name credit default swap spreads themselves are sold data and not held |
| Federal Reserve Bank of Cleveland, Inflation Nowcasting (clevelandfed.org/indicators-and-data/inflation-nowcasting) | checked as a daily stand-in for core PCE (TRACK 3.119) -- NOT used | primary; page read 25 Nov 2026: no data file, and the core PCE figure changes only when new CPI or PCE data arrive |
| FRED: T5YIE, T10YIE, T5YIFR (market-based expected inflation), PCEPILFE (core PCE price index, Bureau of Economic Analysis) | test LI-1b, daily stand-ins for core PCE (TRACK 3.119) | primary, free; breakevens follow the CPI, not the PCE |
| NYSE Group, 'NYSE Group Announces 2026, 2027 and 2028 Holiday and Early Closings Calendar' (Intercontinental Exchange press release, ir.theice.com) | market holidays and 13:00 closes in the daily check of the sell-off rules (TRACK 3.121) | primary; read 25 Nov 2026 |
| Forte and Pena (2009), 'Credit spreads: An empirical analysis on the informational content of stocks, bonds, and CDS', Journal of Banking & Finance 33 | which market moves first: shares, CDS or bonds (TRACK 3.123) | peer-reviewed; read 26 Nov 2026 (copy at e-archivo.uc3m.es) |
| FINRA, Fixed Income Data User Agreement (finra.org/finra-data/fixed-income/user-agreement); FINRA API, Specific Terms for Fixed Income Data (developer.finra.org) | what may be done with FINRA's bond data (TRACK 3.123): website = personal, non-commercial, no robots; API = non-commercial personal or professional use, FINRA named, no extra fee | primary; read 26 Nov 2026 |
| market reports of 25 Nov 2026: The Motley Fool, InvestorPlace, FinScans, Finexus (market wraps) | reasons given for the recovery of 25 Nov (TRACK 3.123) | secondary, claims unverified; none gives a cause at 11:00 New York time |
| market-wide headlines (collected live from 26 Nov 2026): Federal Reserve Board feeds (press, speeches, testimony), TreasuryDirect auction results, White House (presidential actions; briefings and statements), Federal Register public-inspection list, USTR press releases, SEC press releases, BEA releases, EIA press | `data_provenance/live/market_wire.jsonl`; test MW-1 (TRACK 3.125-3.126) | primary; US federal government works |
| Regulation SBSR public CDS trade data (DTCC Data Repository; ICE Trade Vault) -- described by Clarus Financial Technology (clarusft.com) | a possible free, automatic source of single-company CDS spreads (TRACK 3.126) | the description is secondary, claims unverified; the data itself would be primary; terms of use NOT yet read; probe only |
| DTCC Data Repository public file of credit security-based swaps (pddata.dtcc.com, 'SEC cumulative credits', daily) | single-company CDS trades with the company, the time and the size; tests CDS-1 (TRACK 3.127) | primary, published under SEC Regulation SBSR (17 CFR 242.900(tt): 'on a non-fee basis'); terms for re-use NOT yet read -- own testing only, not uploaded, not on the page |
| SEC EDGAR submissions: debt filings (forms 424B2, 424B3, 424B5, FWP; 8-K item 2.03) of 17 large technology companies | test DN-1, new debt of the AI spenders against shares (TRACK 3.137); `data_provenance/debt_news/filings.csv` | primary, public domain |
