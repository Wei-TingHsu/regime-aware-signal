# Sell-off study, stage D: the input tables (no outcome computed)

20776 sell-offs (15886 of stocks, 4890 of index and sector funds). A column is empty for a sell-off when its input did not exist yet at that date. 'Rows with every column' is what a search inside that table alone can use.

| table | what it holds | rows | columns | rows with every column | first year with every column |
|---|---|---|---|---|---|
| T1 | the fall and the market | 20776 | 12 | 20776 | 2000 |
| T2 | who fell and who set it off | 15886 | 16 | 13733 | 2005 |
| T3 | the company's condition | 15886 | 9 | 9064 | 2010 |
| T4 | stress and other markets | 20776 | 19 | 10396 | 2014 |
| T5 | calendar | 20776 | 8 | 11785 | 2011 |
| T6 | Claude's reading (AI chain) | 2397 | 6 | 204 | 2010 |
| T7 | short selling | 9549 | 3 | 9549 | 2011 |
| T8 | insiders' trades | 15684 | 4 | 15684 | 2006 |

## Sectors (Claude's grouping of the SEC's industry codes)

| sector | fund used for 'against its sector' | companies | sell-offs (all definitions) |
|---|---|---|---|
| banks and finance | XLF | 11 | 2762 |
| semiconductors | XLK | 7 | 2518 |
| cars, aircraft and industry | XLI | 15 | 2155 |
| software and internet | XLK | 10 | 1814 |
| computers and equipment | XLK | 7 | 1022 |
| telecom and media | XLC | 6 | 942 |
| insurance and health insurers | XLF | 4 | 889 |
| retail and consumer | XLY | 6 | 690 |
| drugs and biotech | XLV | 9 | 590 |
| payments and business services | XLF | 5 | 535 |
| medical devices and services | XLV | 4 | 515 |
| consumer staples | XLP | 10 | 477 |
| energy | XLE | 3 | 356 |
| real estate | XLRE | 2 | 311 |
| utilities | XLU | 3 | 135 |
| other | SPY | 1 | 110 |
| materials | XLB | 1 | 65 |

| company | SEC industry code | SEC's description | sector given |
|---|---|---|---|
| AXP | 6199 | Finance Services | banks and finance |
| BAC | 6021 | National Commercial Banks | banks and finance |
| BLK | 6211 | Security Brokers, Dealers & Flotation Companies | banks and finance |
| C | 6021 | National Commercial Banks | banks and finance |
| COF | 6021 | National Commercial Banks | banks and finance |
| GS | 6211 | Security Brokers, Dealers & Flotation Companies | banks and finance |
| JPM | 6021 | National Commercial Banks | banks and finance |
| MS | 6211 | Security Brokers, Dealers & Flotation Companies | banks and finance |
| SCHW | 6211 | Security Brokers, Dealers & Flotation Companies | banks and finance |
| USB | 6021 | National Commercial Banks | banks and finance |
| WFC | 6021 | National Commercial Banks | banks and finance |
| BA | 3721 | Aircraft | cars, aircraft and industry |
| BKNG | 4700 | Transportation Services | cars, aircraft and industry |
| CAT | 3531 | Construction Machinery & Equip | cars, aircraft and industry |
| DE | 3523 | Farm Machinery & Equipment | cars, aircraft and industry |
| DHR | 3823 | Industrial Instruments For Measurement, Display, and Control | cars, aircraft and industry |
| FDX | 4513 | Air Courier Services | cars, aircraft and industry |
| GD | 3730 | Ship & Boat Building & Repairing | cars, aircraft and industry |
| GM | 3711 | Motor Vehicles & Passenger Car Bodies | cars, aircraft and industry |
| HON | 3724 | Aircraft Engines & Engine Parts | cars, aircraft and industry |
| LMT | 3760 | Guided Missiles & Space Vehicles & Parts | cars, aircraft and industry |
| RTX | 3724 | Aircraft Engines & Engine Parts | cars, aircraft and industry |
| TMO | 3829 | Measuring & Controlling Devices, NEC | cars, aircraft and industry |
| TSLA | 3711 | Motor Vehicles & Passenger Car Bodies | cars, aircraft and industry |
| UNP | 4011 | Railroads, Line-Haul Operating | cars, aircraft and industry |
| UPS | 4210 | Trucking & Courier Services (No Air) | cars, aircraft and industry |
| AAPL | 3571 | Electronic Computers | computers and equipment |
| CSCO | 3576 | Computer Communications Equipment | computers and equipment |
| EMR | 3600 | Electronic & Other Electrical Equipment (No Computer Equip) | computers and equipment |
| GE | 3600 | Electronic & Other Electrical Equipment (No Computer Equip) | computers and equipment |
| IBM | 3570 | Computer & office Equipment | computers and equipment |
| QCOM | 3663 | Radio & Tv Broadcasting & Communications Equipment | computers and equipment |
| SNDK | 3572 | Computer Storage Devices | computers and equipment |
| CL | 2844 | Perfumes, Cosmetics & Other Toilet Preparations | consumer staples |
| COST | 5331 | Retail-Variety Stores | consumer staples |
| KO | 2080 | Beverages | consumer staples |
| MDLZ | 2000 | Food and Kindred Products | consumer staples |
| MO | 2111 | Cigarettes | consumer staples |
| PEP | 2080 | Beverages | consumer staples |
| PG | 2840 | Soap, Detergents, Cleang Preparations, Perfumes, Cosmetics | consumer staples |
| PM | 2111 | Cigarettes | consumer staples |
| TGT | 5331 | Retail-Variety Stores | consumer staples |
| WMT | 5331 | Retail-Variety Stores | consumer staples |
| ABBV | 2834 | Pharmaceutical Preparations | drugs and biotech |
| ABT | 2834 | Pharmaceutical Preparations | drugs and biotech |
| AMGN | 2836 | Biological Products, (No Diagnostic Substances) | drugs and biotech |
| BMY | 2834 | Pharmaceutical Preparations | drugs and biotech |
| GILD | 2836 | Biological Products, (No Diagnostic Substances) | drugs and biotech |
| JNJ | 2834 | Pharmaceutical Preparations | drugs and biotech |
| LLY | 2834 | Pharmaceutical Preparations | drugs and biotech |
| MRK | 2834 | Pharmaceutical Preparations | drugs and biotech |
| PFE | 2834 | Pharmaceutical Preparations | drugs and biotech |
| COP | 2911 | Petroleum Refining | energy |
| CVX | 2911 | Petroleum Refining | energy |
| XOM | 2911 | Petroleum Refining | energy |
| AIG | 6331 | Fire, Marine & Casualty Insurance | insurance and health insurers |
| BRK-B | 6331 | Fire, Marine & Casualty Insurance | insurance and health insurers |
| MET | 6311 | Life Insurance | insurance and health insurers |
| UNH | 6324 | Hospital & Medical Service Plans | insurance and health insurers |
| LIN | 2810 | Industrial Inorganic Chemicals | materials |
| CVS | 5912 | Retail-Drug Stores and Proprietary Stores | medical devices and services |
| ISRG | 3842 | Orthopedic, Prosthetic & Surgical Appliances & Supplies | medical devices and services |
| MDT | 3845 | Electromedical & Electrotherapeutic Apparatus | medical devices and services |
| MMM | 3841 | Surgical & Medical Instruments & Apparatus | medical devices and services |
| DIS | 7990 | Services-Miscellaneous Amusement & Recreation | other |
| ACN | 7389 | Services-Business Services, NEC | payments and business services |
| MA | 7389 | Services-Business Services, NEC | payments and business services |
| PYPL | 7389 | Services-Business Services, NEC | payments and business services |
| UBER | 7389 | Services-Business Services, NEC | payments and business services |
| V | 7389 | Services-Business Services, NEC | payments and business services |
| AMT | 6798 | Real Estate Investment Trusts | real estate |
| SPG | 6798 | Real Estate Investment Trusts | real estate |
| AMZN | 5961 | Retail-Catalog & Mail-Order Houses | retail and consumer |
| HD | 5211 | Retail-Lumber & Other Building Materials Dealers | retail and consumer |
| LOW | 5211 | Retail-Lumber & Other Building Materials Dealers | retail and consumer |
| MCD | 5812 | Retail-Eating  Places | retail and consumer |
| NKE | 3021 | Rubber & Plastics Footwear | retail and consumer |
| SBUX | 5810 | Retail-Eating & Drinking Places | retail and consumer |
| AMD | 3674 | Semiconductors & Related Devices | semiconductors |
| AVGO | 3674 | Semiconductors & Related Devices | semiconductors |
| INTC | 3674 | Semiconductors & Related Devices | semiconductors |
| MU | 3674 | Semiconductors & Related Devices | semiconductors |
| NVDA | 3674 | Semiconductors & Related Devices | semiconductors |
| TSM | 3674 | Semiconductors & Related Devices | semiconductors |
| TXN | 3674 | Semiconductors & Related Devices | semiconductors |
| ADBE | 7372 | Services-Prepackaged Software | software and internet |
| CRM | 7372 | Services-Prepackaged Software | software and internet |
| CRWD | 7372 | Services-Prepackaged Software | software and internet |
| GOOG | 7370 | Services-Computer Programming, Data Processing, Etc. | software and internet |
| INTU | 7372 | Services-Prepackaged Software | software and internet |
| META | 7370 | Services-Computer Programming, Data Processing, Etc. | software and internet |
| MSFT | 7372 | Services-Prepackaged Software | software and internet |
| NOW | 7372 | Services-Prepackaged Software | software and internet |
| ORCL | 7372 | Services-Prepackaged Software | software and internet |
| PLTR | 7372 | Services-Prepackaged Software | software and internet |
| CHTR | 4841 | Cable & Other Pay Television Services | telecom and media |
| CMCSA | 4841 | Cable & Other Pay Television Services | telecom and media |
| NFLX | 7841 | Services-Video Tape Rental | telecom and media |
| T | 4813 | Telephone Communications (No Radiotelephone) | telecom and media |
| TMUS | 4812 | Radiotelephone Communications | telecom and media |
| VZ | 4813 | Telephone Communications (No Radiotelephone) | telecom and media |
| DUK | 4931 | Electric & Other Services Combined | utilities |
| NEE | 4911 | Electric Services | utilities |
| SO | 4911 | Electric Services | utilities |

## Notes

- high-yield credit spread: not downloaded
- 10-year minus 2-year yield: not downloaded
- Chicago Fed financial conditions index: not downloaded
- 2-year yield: not downloaded
- 10-year expected inflation: not downloaded
- news-based policy uncertainty index: not downloaded
- St. Louis Fed financial stress index: not downloaded
- new jobless claims: not downloaded
- Fed funds rate: not downloaded
- T1 columns (share of rows filled): size in units of its own usual move (100%); last day's move % (100%); where it closed in the day's range (100%); gap at the open % (100%); volume against normal (100%); distance below the one-year high % (100%); run-up over the 60 sessions before % (100%); the S&P 500 over the same sessions % (100%); share of large stocks down 3%+ that day (100%); VIX level (100%); VIX change over the same sessions % (100%); S&P 500 against its 200-day average % (100%)
- T2 columns (share of rows filled): sector (100%); in_ai_chain (100%); own_results_filing (100%); own_other_filing (100%); own_filings_in_the_last_30_days (99%); days_since_own_results (96%); share_of_peers_down_3pct (93%); peers_average_move_pct (93%); fell_more_than_every_peer (93%); worst_peer_move_pct (93%); worst_peer_had_results (93%); worst_peer_had_any_filing (93%); a_peer_reported_results_and_fell_3pct (93%); no_own_filing_but_a_peer_filed_and_fell (93%); sector_fund_move_pct (95%); move_against_sector_fund_pct (95%)
- T3 columns (share of rows filled): profitable_last_year (59%); revenue_growth_last_year_pct (60%); profit_margin_pct (58%); liabilities_to_assets_pct (63%); cash_to_assets_pct (61%); size_rank_in_the_list (100%); move_over_the_year_before_pct (100%); sensitivity_to_the_market (100%); usual_daily_move_pct (100%)
- T4 columns (share of rows filled): VIX against the three-month VIX (93%); VIX against the nine-day VIX (58%); volatility of the VIX (92%); SKEW index (100%); 10-year yield, change over 5 sessions (100%); 3-month yield, change over 5 sessions (100%); dollar index, move over 5 sessions % (100%); oil, move over 5 sessions % (99%); gold, move over 5 sessions % (99%); copper, move over 5 sessions % (99%); high-yield bond fund, move over 5 sessions % (92%); investment-grade bond fund, move over 5 sessions % (96%); long Treasury fund, move over 5 sessions % (96%); emerging-market shares, move over 5 sessions % (95%); regional banks, move over 5 sessions % (93%); bitcoin, move over 5 sessions % (50%); small against large companies, 5 sessions % (99%); value against growth shares, 5 sessions % (99%); the average share against the S&P 500, 5 sessions % (95%)
- T5 columns (share of rows filled): weekday (100%); month (100%); sessions_to_month_end (100%); sessions_to_quarter_end (100%); option_expiry_week (100%); days_to_next_fed_statement (57%); days_since_last_fed_statement (58%); results_filings_in_the_list_last_10_days (100%)
- T6 columns (share of rows filled): latest_results_score (100%); days_since_those_results (100%); results_in_the_window (100%); event_in_the_window_score (9%); event_in_the_window_material (9%); event_in_the_window_type (9%)
- T7 columns (share of rows filled): short_sales_share_of_volume_that_day (100%); short_sales_share_average_of_20_days_before (100%); short_sales_share_that_day_against_its_average (100%)
- T8 columns (share of rows filled): insider_purchase_filings_in_90_days (100%); insider_sale_filings_in_90_days (100%); any_insider_purchase_in_90_days (100%); insider_purchases_minus_sales_in_90_days (100%)
