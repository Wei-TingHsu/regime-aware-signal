# Source probe: dated lists of short reports, public calls and media items

## Publishers' own lists

| publisher | answer | items on the first page | dates | older pages | examples |
|---|---|---|---|---|---|
| Hunterbrook | HTTP 400 | | | | |
| Hindenburg Research (archive) | feed | 10 | 2024-07-01 -> 2025-01-15 | page 2: 10 items, 2023-08-31 -> 2024-06-04; page 10: 10 items, 2017-12-11 -> 2018-03-22; page 40: HTTPError;  | A Personal Note From Our Founder; Carvana: A Father-Son Accounting Grift For The Ages |
| Muddy Waters | no answer (URLError) | | | | |
| Citron Research | HTTP 403 | | | | |
| Spruce Point | no answer (ParseError) | | | | |
| Kerrisdale | feed | 0 | no dates |  |  |
| Grizzly Research | feed | 10 | 2026-09-19 -> 2026-10-14 | page 2: 10 items, 2026-04-16 -> 2026-09-17; page 10: 10 items, 2020-02-25 -> 2020-11-16; page 40: HTTPError;  | International Games System (TPEx: 3293) — Profits and Divide; Media Coverage on Grizzly Research’s Investigation Into Arch |
| Viceroy Research | HTTP 404 | | | | |
| Blue Orca | feed | 6 | 2025-12-02 -> 2026-10-19 | page 2: 6 items, 2025-02-19 -> 2025-09-25; page 10: 6 items, 2011-12-06 -> 2014-03-19; page 40: HTTPError;  | Blue Orca is Long Rohm (6963 JP), Chubu Electric (9502 JP) a; Blue Orcaは、ローム(6963 JP)、中部電力(9502 JP)、およびTRE(9247 JP)をロングしてい |
| Wolfpack Research | no answer (ParseError) | | | | |
| Fuzzy Panda | feed | 10 | 2025-10-10 -> 2026-11-18 | page 2: same as page 1; page 10: same as page 1; page 40: same as page 1;  | BillionToOne (BLLN) – Undisclosed Fraudulent Billing Allegat; T1 Energy (TE) – Whistleblower Series: Internal Docs Expose  |
| Culper Research | HTTP 403 | | | | |
| Gotham City Research | no answer (ParseError) | | | | |
| Iceberg Research | HTTP 403 | | | | |
| Jehoshaphat Research | HTTP 403 | | | | |
| Scorpion Capital | HTTP 404 | | | | |
| J Capital Research | HTTP 404 | | | | |
| Michael Burry's newsletter | HTTP 400 | | | | |
| SemiAnalysis | feed | 10 | 2025-07-11 -> 2025-09-16 | page 2: 10 items, 2025-05-16 -> 2025-07-11; page 10: 10 items, 2023-05-13 -> 2023-07-05; page 40: HTTPError;  | xAI’s Colossus 2 – First Gigawatt Datacenter In The World, U; Another Giant Leap: The Rubin CPX Specialized Accelerator &  |

## Google News search feed (free, no key)

| what | search | answer | items | dates | publishers seen | examples |
|---|---|---|---|---|---|---|
| public call, now | `"Michael Burry" short` | feed | 100 | 2026-08-04 -> 2026-11-20 | Yahoo Finance 33, The Motley Fool 13, TradingView 9, Business Insider 8, 24/7 Wall St. 8 | Michael Burry Says He Tried to Warn You About Nvidia, CoreWeave and Ne; Michael Burry Shorted Nvidia Stock. Is He About to Make Another Fortun |
| public call, one past month | `"Michael Burry" short after:2025-11-01 before:2025-12-01` | feed | 35 | 2025-11-03 -> 2025-12-01 | CNBC 6, Business Insider 6, Yahoo Finance 5, Fortune 3, Investopedia 2 | Michael Burry of 'Big Short' fame discloses bets against Palantir, Nvi; Michael Burry of ‘The Big Short’ is back with cryptic messages — and t |
| public call, an older month | `"Michael Burry" short after:2023-08-01 before:2023-09-01` | feed | 31 | 2023-08-04 -> 2023-08-30 | markets.businessinsider.com 4, Daily Mail 2, India Today 2, CNN 2, Indy100 1 | Burry, famous for 'Big Short,' bought bearish options against S&P, Nas; Michael Burry, of Big Short fame, just bet $1.6 billion on a stock mar |
| short report, one past month | `"short report" Hindenburg after:2024-06-01 before:2024-07-01` | feed | 0 | no dates |  |  |
| media by publisher, now | `AMD site:reuters.com when:7d` | feed | 83 | 2022-06-14 -> 2026-11-20 | Reuters 83 | AMD shares slide as report says China links could invite US scrutiny -; US signed off on sales of nearly 900,000 AI chips to China in six mont |
| media by publisher, now | `Nvidia site:cnbc.com when:7d` | feed | 100 | 2026-11-13 -> 2026-11-20 | CNBC 100 | Nvidia board is not considering bringing Jensen Huang back as CEO, sou; Trump’s accounts traded up to $97.5 million in Nvidia as Huang gained  |
| media by publisher, now | `AMD site:bloomberg.com when:7d` | feed | 94 | 2015-06-03 -> 2026-11-20 | Bloomberg.com 92, Bloomberg 2 | AMD Shares Slump After Shortseller Raises China Concerns - Bloomberg.c; US Approved AI Chip Sales to China’s Tencent, Alibaba, Data Show - Blo |
| media by publisher, now | `Nvidia site:seekingalpha.com when:7d` | feed | 100 | 2026-11-15 -> 2026-11-20 | Seeking Alpha 100 | Nvidia: The Worst Is Yet To Come (NASDAQ:NVDA) - Seeking Alpha; Nvidia in advanced talks to buy diffusion AI startup Inception for ove |
| media by publisher, one past month | `Nvidia site:reuters.com after:2025-05-01 before:2025-06-01` | feed | 50 | 2025-05-01 -> 2025-05-29 | Reuters 50 | Nvidia's Huang sparks 'Jensanity' in Taiwan with AI hero's welcome - R; German chipmaker Infineon to work with Nvidia on power delivery chips  |
