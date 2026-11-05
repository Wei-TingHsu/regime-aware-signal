# T-K3 — chair style on the rubric (exact permutation) — run 2026-11-05 17:11

Rubric reads: 133 of 133 statements on disk under `style-v1-2026-10-28`, own cache folder, never pooled with v1; the comparison sets are the registered ones (folder listing), every member read.

## Acceptance check (registered 28 Oct 2026, prior #82)

| transition | n | energy | exact p | arrangements | separates | dimensions by p |
|---|---|---|---|---|---|---|
| Bernanke->Yellen | 8 vs 8 | 1.262 | 0.0112 | 12,870 | yes | guidance_strength 0.000, inflation_vs_labour 0.026, hawk_dove 0.035, balance_sheet 0.182 |
| Yellen->Powell | 8 vs 8 | 1.063 | 0.0047 | 12,870 | yes | balance_sheet 0.001, hedging_density 0.014, dissents 0.200, inflation_vs_labour 0.343 |

Verdict: INSTRUMENT OK (at least one past transition separates). Prior #82: wrong.

## Warsh vs Powell's last 8 (T-K3, prior #79)

n = 4; energy 2.408; exact p = 0.0606 over 495 arrangements (floor 0.0020); does not separate at 0.05.

| dimension | exact p | mean current | mean previous |
|---|---|---|---|
| inflation_vs_labour | 0.0101 | +0.275 | -0.125 |
| hedging_density | 0.0384 | +0.225 | +0.356 |
| hawk_dove | 0.1192 | +0.263 | -0.037 |
| balance_sheet | 0.2747 | +0.125 | +0.125 |
| length_change | 0.4283 | -0.175 | +0.018 |
| guidance_strength | 0.5333 | +0.075 | +0.106 |
| novelty_vs_prev | 0.6222 | +0.450 | +0.481 |
| dissents | 0.7455 | +1.250 | +1.875 |

Per-dimension p-values are descriptive (eight dimensions; a single one at 0.05 is not a finding).

## Rubric means by chair

| chair | hawk_dove | guidance_strength | balance_sheet | inflation_vs_labour | hedging_density | dissents | length_change | novelty_vs_prev | words |
|---|---|---|---|---|---|---|---|---|---|
| Bernanke | -0.16 | +0.64 | +0.47 | -0.28 | +0.40 | +1.00 | +0.06 | +0.29 | 454 |
| Powell | +0.03 | +0.28 | +0.19 | +0.01 | +0.35 | +0.43 | -0.00 | +0.38 | 389 |
| Warsh | +0.26 | +0.07 | +0.12 | +0.28 | +0.23 | +1.25 | -0.17 | +0.45 | 150 |
| Yellen | +0.14 | +0.34 | +0.22 | -0.05 | +0.40 | +0.69 | -0.02 | +0.29 | 547 |
