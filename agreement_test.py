"""
agreement_test.py -- Amendment 2 section 4, run as registered.

    Hypothesis. Cases labelled CONCORDANT have better realised outcomes than
    cases labelled DISCORDANT.

    Statistic. Signed realised return = realised x sign(step 3 point estimate).
    Positive means the estimate pointed the right way.

    Comparison. Mean signed realised return, CONCORDANT vs DISCORDANT,
    two-sided permutation on label assignment (10,000, seed 42), bootstrap 95%
    CI on the difference.

    Criterion. Ships only if CONCORDANT mean > DISCORDANT mean AND p < 0.05.
    UNDERPOWERED if either arm < 20.

TWO DESIGN DECISIONS, declared before the number is seen, because the
amendment left them open:

  1. PRIMARY HORIZON ONLY. The same event appears at h=3, 5 and 20 for a given
     source and asset. Pooling all three triple-counts every event. h=3 was
     declared primary in unblind_step3.py before the unblinding ran.

  2. STRATIFIED PERMUTATION. The same FOMC minute appears once per asset (GLD,
     SPY, TLT, UUP, USO), and cells differ in base rate. Labels are permuted
     WITHIN each (source, asset) cell, which preserves cell structure and every
     cell's own concordance rate, and only destroys the label<->outcome link.
     The unstratified version is also computed and reported, because the
     difference between them is itself informative.

CAVEAT RECORDED BEFORE THE RUN (CURRENT_STATE 17.7.4): step 3's estimates
mostly did not beat the unconditional mean under correct inference. The
"history" half of any agreement is therefore weak, and a positive result here
would largely measure the READER agreeing with a noisy sign. That goes in the
result whichever way it lands.

Amendment 3's rho-hat and coverage check need interval half-widths, which
unblind_step3.py did not write out. They run separately once that is added;
this script does not attempt them.

Run from the repo root:  python agreement_test.py
"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.data_io import PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_MD = REPO / "docs" / "agreement_test.md"
OUT_JSON = PROCESSED_DIR / "agreement_test.json"
AX = {"GLD": "dir_gold", "SPY": "dir_eq", "TLT": "dir_dur",
      "UUP": "dir_usd", "USO": "dir_oil"}
READS = ("read_statement.csv", "read_minutes.csv", "read_8k.csv",
         "read_political_order.csv", "read_political_other.csv")
PRIMARY_H, NEGLIGIBLE, ITERS, SEED, MIN_ARM = 3, 0.05, 10_000, 42, 20


def main():
    p = pd.read_csv(PROCESSED_DIR / "unblind_step3_predictions.csv")
    p["date"] = pd.to_datetime(p.date)
    p = p[p.horizon == PRIMARY_H].copy()
    R = pd.concat([pd.read_csv(PROCESSED_DIR / f) for f in READS
                   if (PROCESSED_DIR / f).exists()], ignore_index=True)
    R["date"] = pd.to_datetime(R.date, errors="coerce")

    rows = []
    for (s, a), g in p.groupby(["source", "asset"]):
        r = R[R.source == s][["date", AX[a]]].rename(columns={AX[a]: "rd"})
        m = g.merge(r, on="date", how="left")
        m["rd"] = pd.to_numeric(m.rd, errors="coerce").fillna(0)
        est_floor = NEGLIGIBLE * m.pred_blend.abs().max()
        live = (m.rd.abs() > NEGLIGIBLE) & (m.pred_blend.abs() > est_floor)
        m["label"] = np.where(~live, "UNINFORMATIVE",
                              np.where(np.sign(m.rd) == np.sign(m.pred_blend),
                                       "CONCORDANT", "DISCORDANT"))
        m["signed"] = m.realised * np.sign(m.pred_blend)
        m["cell"] = f"{s}/{a}"
        rows.append(m[["cell", "date", "label", "signed", "realised",
                       "pred_blend"]])
    df = pd.concat(rows, ignore_index=True)
    d = df[df.label != "UNINFORMATIVE"].copy()
    con, dis = d[d.label == "CONCORDANT"], d[d.label == "DISCORDANT"]
    nC, nD = len(con), len(dis)
    obs = con.signed.mean() - dis.signed.mean()

    print("=" * 74)
    print("AGREEMENT FLAG -- Amendment 2 section 4, primary horizon h=3")
    print("=" * 74)
    print(f"  CONCORDANT n={nC}  mean signed {con.signed.mean()*100:+.3f}%")
    print(f"  DISCORDANT n={nD}  mean signed {dis.signed.mean()*100:+.3f}%")
    print(f"  UNINFORMATIVE {int((df.label=='UNINFORMATIVE').sum())} (excluded)")
    print(f"  difference    {obs*100:+.3f}%")

    rng = np.random.default_rng(SEED)
    y = d.signed.values
    lab = (d.label == "CONCORDANT").values
    cells = d.cell.values

    # stratified permutation: shuffle labels within each cell
    null_s = np.empty(ITERS)
    idx_by_cell = {c: np.where(cells == c)[0] for c in np.unique(cells)}
    for it in range(ITERS):
        lp = lab.copy()
        for c, ix in idx_by_cell.items():
            lp[ix] = lab[ix][rng.permutation(len(ix))]
        null_s[it] = y[lp].mean() - y[~lp].mean()
    p_strat = (np.sum(np.abs(null_s) >= abs(obs)) + 1) / (ITERS + 1)

    # unstratified, for comparison
    null_u = np.empty(ITERS)
    for it in range(ITERS):
        lp = lab[rng.permutation(len(lab))]
        null_u[it] = y[lp].mean() - y[~lp].mean()
    p_unstrat = (np.sum(np.abs(null_u) >= abs(obs)) + 1) / (ITERS + 1)

    # bootstrap CI on the difference, resampling within arm
    boot = np.empty(ITERS)
    cy, dy = con.signed.values, dis.signed.values
    for it in range(ITERS):
        boot[it] = (cy[rng.integers(0, nC, nC)].mean()
                    - dy[rng.integers(0, nD, nD)].mean())
    lo, hi = np.percentile(boot, [2.5, 97.5])

    under = nC < MIN_ARM or nD < MIN_ARM
    passed = (not under) and obs > 0 and p_strat < 0.05
    print(f"\n  p (stratified within cell, primary) {p_strat:.4f}")
    print(f"  p (unstratified, for comparison)    {p_unstrat:.4f}")
    print(f"  bootstrap 95% CI on difference      [{lo*100:+.3f}%, {hi*100:+.3f}%]")
    verdict = ("UNDERPOWERED" if under else "PASS -- label ships" if passed
               else "FAIL -- label removed, section 7.3 reverts to display-only")
    print(f"\n  {verdict}")
    print("\n  Recorded before the run: step 3's estimates mostly did not beat")
    print("  the unconditional mean under correct inference (17.7.4), so any")
    print("  agreement here is largely the reader agreeing with a noisy sign.")

    print("\n  per cell:")
    for c, g in d.groupby("cell"):
        cc, dd = g[g.label == "CONCORDANT"], g[g.label == "DISCORDANT"]
        print(f"    {c:24} C n={len(cc):4} {cc.signed.mean()*100:+.3f}%   "
              f"D n={len(dd):4} {dd.signed.mean()*100:+.3f}%")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    L = ["# Agreement flag — Amendment 2 §4 result", "", f"*Run {ts}. "
         f"Primary horizon h={PRIMARY_H} only; labels permuted within "
         f"(source, asset) cell.*", "",
         f"| arm | n | mean signed realised return |", "|---|---|---|",
         f"| CONCORDANT | {nC} | {con.signed.mean()*100:+.3f}% |",
         f"| DISCORDANT | {nD} | {dis.signed.mean()*100:+.3f}% |", "",
         f"Difference **{obs*100:+.3f}%**, bootstrap 95% CI "
         f"[{lo*100:+.3f}%, {hi*100:+.3f}%]. Permutation p (stratified) "
         f"**{p_strat:.4f}**; unstratified {p_unstrat:.4f}.", "",
         f"## Verdict: {verdict}", "",
         "**Caveat recorded before the run.** Step 3's estimates mostly did not "
         "beat the unconditional mean under correct inference "
         "(`CURRENT_STATE` §17.7.4). The history half of any agreement is "
         "therefore weak; a positive result here largely measures the reader "
         "agreeing with a noisy sign.", "",
         "Amendment 3's ρ̂ and coverage check require interval half-widths that "
         "`unblind_step3.py` did not write out; they are not attempted here.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    OUT_JSON.write_text(json.dumps(dict(run=ts, nC=nC, nD=nD, diff=float(obs),
                                        p_strat=float(p_strat),
                                        p_unstrat=float(p_unstrat),
                                        ci=[float(lo), float(hi)],
                                        verdict=verdict), indent=2))
    print(f"\n  -> {OUT_MD}\n  -> {OUT_JSON}")


if __name__ == "__main__":
    main()
