# Horizon audit — summary

Every test re-measured on the event day and on days +1 … +5, signed in the direction of its claim. Label rule: family p on the days after < 0.05 → QUANT candidate; else family p on day 0 < 0.05 → SUBJECTIVE grade B candidate (information events) or CONTEXT (price-move events); else NEITHER.

| test | event kind | day 0 — best cell | days after — best cell | day −1 check | label |
|---|---|---|---|---|---|
| the report's document-driven calls: the report day itself and the days after (rows 24/27/33, A, D7) | information | day 0: +6 bp (t +2.1), calls on SPY; family p 0.245 | days +1..+3: +16 bp (t +3.6), all calls, pooled; family p 0.034 | family p 0.007 | **QUANT candidate** |
| gold and Treasuries around Fed statement days, signed by the rate surprise (row 14, T9b) | information | day 0: +76 bp (t +7.6), all statement days → gold; family p 0.000 | day +1: +38 bp (t +1.9), larger-than-median rate surprise → gold; family p 0.403 | family p 0.187 | **SUBJECTIVE grade B candidate** |
| the history tables' events — Fed decision days (H1), dollar jumps and drops (H3), 2-year yield shocks (H4), regime changes (H5) — on five markets | price move | day 0: -42 bp (t -8.7), H1 → UUP; family p 0.000 | day +1: -141 bp (t -3.1), H4dn → USO; family p 0.122 | family p 0.087 | **CONTEXT (same-day co-movement)** |
| gold around a large daily change in the Fed's reverse-repo balance (D2c) | information | day 0: +10 bp (t +1.6), reverse-repo balance change beyond 1.5 sd → gold; family p 0.231 | day +1: +7 bp (t +1.1), reverse-repo balance change beyond 1.5 sd → gold; family p 0.838 | family p 0.446 | **NEITHER** |
| gold around an oil shock (A3a, D5) | price move | day 0: +31 bp (t +3.1), all oil shocks → gold; family p 0.009 | days +1..+5: +23 bp (t +1.3), all oil shocks → gold; family p 0.808 | family p 0.041 | **CONTEXT (same-day co-movement)** |
| after a large unexplained move, does the asset continue (+) or reverse (−) over the next 1–5 sessions (T-H) | price move | not measured | days +1..+5: -55 bp (t -4.4), SPY: unexplained move over 20 session(s) beyond 1.5 sd; family p 0.106 | not measured | **NEITHER** |
| gold (and the S&P) around the day an S&P drawdown is completed (D1, T-L5b) | price move | day 0: -27 bp (t -1.2), S&P 20-session return crosses -4% → gold; family p 0.704 | days +1..+5: +128 bp (t +3.1), S&P 10-session return crosses -4% → S&P itself; family p 0.160 | family p 0.490 | **NEITHER** |
| fast states and day-types → the next 1, 2, 3, 5 sessions (F1, Y3 at short spans) | price move | not measured | days +1..+5: +31 bp (t +7.9), fast state k3:1 → SPY; family p 0.002 | not measured | **QUANT candidate** |
| gold and the S&P around a sudden one-day S&P fall (D1b) | price move | day 0: +51 bp (t +1.2), S&P falls ≥ 4.0% in one session → gold; family p 0.613 | days +1..+3: +35 bp (t +1.9), S&P falls ≥ 1.5% in one session → S&P itself; family p 0.876 | family p 0.062 | **NEITHER** |
