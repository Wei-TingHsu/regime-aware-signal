# Agreement flag — Amendment 2 §4 result

*Run 2026-08-26 21:03:31 +0800. Primary horizon h=3 only; labels permuted within (source, asset) cell.*

| arm | n | mean signed realised return |
|---|---|---|
| CONCORDANT | 1221 | +0.193% |
| DISCORDANT | 803 | +0.406% |

Difference **-0.213%**, bootstrap 95% CI [-0.407%, -0.025%]. Permutation p (stratified) **0.0845**; unstratified 0.0251.

## Verdict: FAIL -- label removed, section 7.3 reverts to display-only

**Caveat recorded before the run.** Step 3's estimates mostly did not beat the unconditional mean under correct inference (`CURRENT_STATE` §17.7.4). The history half of any agreement is therefore weak; a positive result here largely measures the reader agreeing with a noisy sign.

Amendment 3's ρ̂ and coverage check require interval half-widths that `unblind_step3.py` did not write out; they are not attempted here.

