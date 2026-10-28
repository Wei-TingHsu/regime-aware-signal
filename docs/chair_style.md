# T-K3 — chair style on the rubric (exact permutation) — run 2026-10-28 01:17

Rubric reads: 128 statements under `style-v1-2026-10-28`, own cache folder, never pooled with v1.

## Acceptance check (registered 28 Oct 2026, prior #82)

| transition | n | energy | exact p | arrangements | separates | dimensions by p |
|---|---|---|---|---|---|---|
| Bernanke->Yellen | 8 vs 8 | 1.223 | 0.0169 | 12,870 | yes | guidance_strength 0.000, inflation_vs_labour 0.026, hawk_dove 0.028, novelty_vs_prev 0.149 |
| Yellen->Powell | 8 vs 8 | 1.057 | 0.0050 | 12,870 | yes | balance_sheet 0.001, hedging_density 0.014, dissents 0.200, inflation_vs_labour 0.343 |

Verdict: INSTRUMENT OK (at least one past transition separates). Prior #82: wrong.

## Warsh vs Powell's last 8 (T-K3, prior #79)

n = 2; energy 2.876; exact p = 0.3778 over 45 arrangements (floor 0.0222); does not separate at 0.05.

| dimension | exact p | mean current | mean previous |
|---|---|---|---|
| hedging_density | 0.0889 | +0.200 | +0.350 |
| inflation_vs_labour | 0.1111 | +0.250 | -0.075 |
| hawk_dove | 0.2222 | +0.325 | -0.012 |
| guidance_strength | 0.4000 | +0.050 | +0.100 |
| balance_sheet | 0.4222 | +0.100 | +0.106 |
| length_change | 0.9111 | -0.000 | -0.004 |
| dissents | 1.0000 | +1.500 | +1.625 |
| novelty_vs_prev | 1.0000 | +0.400 | +0.463 |

Per-dimension p-values are descriptive (eight dimensions; a single one at 0.05 is not a finding).

## Rubric means by chair

| chair | hawk_dove | guidance_strength | balance_sheet | inflation_vs_labour | hedging_density | dissents | length_change | novelty_vs_prev | words |
|---|---|---|---|---|---|---|---|---|---|
| Bernanke | -0.16 | +0.64 | +0.47 | -0.28 | +0.40 | +1.00 | +0.06 | +0.29 | 454 |
| Powell | +0.02 | +0.28 | +0.19 | +0.00 | +0.35 | +0.41 | -0.00 | +0.38 | 390 |
| Warsh | +0.33 | +0.05 | +0.10 | +0.25 | +0.20 | +1.50 | +0.00 | +0.40 | 149 |
| Yellen | +0.14 | +0.34 | +0.23 | -0.06 | +0.40 | +0.71 | -0.01 | +0.29 | 551 |
