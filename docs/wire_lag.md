# W1: how late is the SEC stamp against the news wire?

Wire times from PR Newswire's company pages, the companies' own press-release lists, and a public mirror of the wire (`data_provenance/ai_earnings/wire_times.csv`, column `source`).

Matched 227 of 548 results releases. Lag = SEC stamp minus wire time, in minutes (the wire states whole minutes).

| company | matched | median lag | wire first | lag 0-2 min | 2-10 min | 10-30 min | over 30 min | SEC first |
|---|---|---|---|---|---|---|---|---|
| AMD | 36 | 2 min | 100% | 16 | 17 | 1 | 2 | 0 |
| AMZN | 23 | 10 min | 100% | 0 | 12 | 9 | 2 | 0 |
| AVGO | 11 | 5 min | 100% | 0 | 6 | 5 | 0 | 0 |
| CRWD | 21 | 2 min | 100% | 11 | 10 | 0 | 0 | 0 |
| INTC | 33 | 8 min | 100% | 1 | 29 | 3 | 0 | 0 |
| META | 19 | 4 min | 100% | 1 | 15 | 3 | 0 | 0 |
| MSFT | 31 | -2 min | 23% | 0 | 4 | 1 | 2 | 24 |
| MU | 17 | -1 min | 41% | 5 | 2 | 0 | 0 | 10 |
| ORCL | 29 | 9 min | 100% | 0 | 18 | 10 | 1 | 0 |
| SNDK | 7 | 6 min | 100% | 0 | 7 | 0 | 0 | 0 |
| all | 227 | 4 min | 85% | 34 | 120 | 32 | 7 | 34 |
