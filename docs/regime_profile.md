# What each market condition actually contains

*Run 2026-08-28 00:26:26 +0800. Description, not validation.*

Each regime is described by the mean of every macro series inside it, against that series' own full-panel mean, in panel standard deviations. This is arithmetic on the variables that formed the clusters — it cannot be wrong, only uninformative. It is a different operation from the regime–event alignment claim that collapsed in `CURRENT_STATE` §15, which tested the regimes against something outside themselves and failed.

| condition | label | sessions | share | strongest deviations |
|---|---|---|---|---|
| 1 of 4 | **A steep curve, low short-term rates** | 2264 | 43.6% | the yield curve +0.77sd, 2-year yield -0.75sd, the policy rate -0.73sd |
| 2 of 4 | **Low long-term rates, low or negative real rates** | 882 | 17.0% | 10-year yield -0.59sd, 10-year real yield -0.50sd, the policy rate -0.47sd |
| 3 of 4 | **A flat or inverted curve, a strong dollar** | 962 | 18.5% | the yield curve -0.96sd, the dollar +0.84sd, money supply +0.75sd |
| 4 of 4 | **Rapid money growth, a high policy rate** | 582 | 11.2% | money supply +1.52sd, the policy rate +1.27sd, the dollar +1.26sd |

A series contributes a phrase when its regime mean sits more than 0.5 panel standard deviations from the panel mean; the two largest contribute. Both are display choices and change no number in the pipeline.

