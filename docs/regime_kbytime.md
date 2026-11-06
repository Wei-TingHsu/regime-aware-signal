# R4 — which regime count wins, year by year

At each year-end the mixture is refit on data to date for k = 3…8 (5 seeds). Stability = mean adjusted Rand index across seeds; persistence = median run length; separation = silhouette. Winner = best summed rank.

| year | winning k | stability | median run | silhouette |
|---|---|---|---|---|
| 2010 | **3** | 1.000 | 274 | 0.486 |
| 2011 | **5** | 1.000 | 217 | 0.552 |
| 2012 | **5** | 1.000 | 227 | 0.579 |
| 2013 | **5** | 1.000 | 218 | 0.544 |
| 2014 | **6** | 1.000 | 20 | 0.481 |
| 2015 | **3** | 1.000 | 44 | 0.329 |
| 2016 | **8** | 0.711 | 8 | 0.439 |
| 2017 | **4** | 0.998 | 74 | 0.398 |
| 2018 | **8** | 0.886 | 6 | 0.384 |
| 2019 | **3** | 0.910 | 81 | 0.377 |
| 2020 | **6** | 0.791 | 4 | 0.344 |
| 2021 | **5** | 0.713 | 2 | 0.423 |
| 2022 | **5** | 0.996 | 4 | 0.406 |
| 2023 | **5** | 0.865 | 4 | 0.408 |
| 2024 | **3** | 0.929 | 23 | 0.392 |
| 2025 | **5** | 0.935 | 5 | 0.428 |
| 2026 | **5** | 0.916 | 5 | 0.437 |

Full table in the JSON. A switch of k is a founder decision (it relabels history and the precedent pools are keyed by label).
