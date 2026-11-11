"""record_11nov_n1v3a.py -- N1 v3a/v3b on record (priors #124-#127 judged from the files on disk) and v3c (the joint size test) registered BEFORE it runs.
Run AFTER `python -m src.news_events3 grid` has completed with the crash fix, BEFORE `joint`. Idempotent.    python scripts_applied/record_11nov_n1v3a.py"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.news_events import _returns

g = json.loads(Path("docs/news_events_v3_grid.json").read_text()); groups, untest = g["groups"], g.get("untestable", [])
size = pd.DataFrame(json.loads(Path("docs/news_events_v3_size.json").read_text())); rd = pd.read_csv("processed/news_doc_reads_v3.csv", parse_dates=["date"])
ev = pd.read_csv("processed/news_events.csv", parse_dates=["date"]); idx = _returns().index; cov = pd.read_csv("processed/news_corpus_coverage.csv", dtype={"date": str})
gl = "; ".join(f"{x['label'].split(':')[0].replace('N1 v3 ', '')}: best {x['best']['family']} / cutoff {x['best']['cutoff']} / window {x['best']['window']} / h {x['best']['h']}, gap {x['best_stat']:+.1f} pts vs null q95 {x['q95']:+.1f}, p_family {x['p_family']:.3f}" for x in groups)
p124 = all(x["p_family"] >= 0.0125 for x in groups)
nsig = int((size.p < 0.05).sum()); pos = int((size.rank_corr > 0).sum()); sig_pos = int(((size.p < 0.05) & (size.rank_corr > 0)).sum()); sox = size[size["index"] == "SOX"]
p125 = (nsig <= 5) and not (sig_pos == nsig and nsig >= 2)
src = [c for c in cov.columns if c != "date"]; anyd = cov[src].sum(axis=1) > 0; yr = cov["date"].str[:4].astype(int); share, share20 = float(anyd.mean()), float(anyd[yr >= 2020].mean()); p126 = share < 0.40 and share20 > 0.50
rd["pos"] = idx.searchsorted(rd["date"]); ep = idx.searchsorted(ev["date"]); after = {-1: [], 1: []}
for p_, sg in zip(ep, ev["sign"]):
    m = (rd["pos"] > p_) & (rd["pos"] <= p_ + 10); after[int(sg)].extend(rd.loc[m, "implication"].tolist())
mf, mr = float(np.mean(after[-1])), float(np.mean(after[1])); p127 = mf > 0 and mr > 0 and abs(mf - mr) <= 0.1
print(f"grid: {gl}; untestable: {untest}\nsize: {nsig} of {len(size)} cells p < 0.05 ({sig_pos} positive); {pos} of {len(size)} rank correlations positive; SOX {int((sox.rank_corr > 0).sum())} of {len(sox)} positive\ncorpus: {share:.0%} of event days, {share20:.0%} from 2020\nmean equity implication of documents in the 10 sessions after falls {mf:+.3f}, after rises {mr:+.3f}\n#124 {'right' if p124 else 'WRONG'}, #125 {'right' if p125 else 'WRONG'}, #126 {'right' if p126 else 'WRONG'}, #127 {'right' if p127 else 'WRONG'}")
ROWS = f"""| 2026-11-11 | v3b corpus survey | {int(anyd.sum())} of {len(cov)} event days have a same-day document in the project's corpus ({share:.0%}); from 2020 {share20:.0%}. By source (event days): """ + ", ".join(f"{c} {int((cov[c] > 0).sum())}" for c in src if (cov[c] > 0).any()) + f""". Company filings cover only {int((cov.get('earnings_8k', pd.Series(dtype=int)) > 0).sum())} event days — a corpus-based cause read is feasible from 2020 only. | **#126 {'right' if p126 else 'wrong (counted)'}** |
| 2026-11-11 | v3a documents and read | {len(rd)} official documents inside an event window read once each under n1-doc-v3 ({rd['kind'].value_counts().to_dict()}), ≈ US$8.57. BLS archive index lists ~225 releases per series (≈ 2008 →): events before that have Fed documents only. Mean equity implication of documents in the 10 sessions after falls {mf:+.3f}, after rises {mr:+.3f}. **Caveat recorded:** the reader was told to judge each document on its own, but the model has general knowledge of market history up to its training cut-off; a hindsight leak into the implication score cannot be excluded for well-known episodes. | **#127 {'right' if p127 else 'wrong (counted)'}** |
| 2026-11-11 | v3a grid (reversal RATE with − without a contradicting document; 4 groups, bar p_family < 0.0125) | {gl}. Not testable (no cell with 20 events on both sides): {', '.join(untest) or 'none'}. First run crashed on the untestable group (my bug — `run` raises when every cell is empty); rerun with the fix, same seeds, same numbers. | **#124 {'right' if p124 else 'wrong (counted)'}**: no group passes. A contradicting official document does not raise how OFTEN prices reverse, at any cutoff, window, horizon or family. |
| 2026-11-11 | v3a size (reversal SIZE vs contradiction score; 32 testable cells, ~1.6 below 0.05 by chance) | {nsig} cells with p < 0.05, all {sig_pos} positive; {pos} of {len(size)} rank correlations positive; SOX: {int((sox.rank_corr > 0).sum())} of {len(sox)} positive, typical size +0.10 to +0.23. In SOX the largest quarter of reversals had a higher mean contradiction score than the rest in nearly every cell. The cells overlap (same events, nested horizons), so the count is not {nsig} independent findings. | **#125 {'right' if p125 else 'wrong (counted)'}** — the count is within 5, but the significant cells DO share a sign, which the prior said they would not. This is the first N1 result that is not flat; it earns one joint test, registered below before it runs. |
| 2026-11-11 | **v3c registered before running — joint size test** | One statistic per index × direction: the mean rank correlation between contradiction score and reversal return over windows 3, 5, 10 × horizons 1, 3, 5, 10; 2,000 shuffles of outcomes (one shuffle applied to every horizon, keeping the overlap); one-sided; primary family = all documents; bar **p < 0.0125** (four groups). Beside it, measured not judged: Fed-only and BLS-only, before / from 2020, and the 5-session reversal return by third of the score. Prior **#128:** SOX-fall and SOX-rise both show a positive mean (+0.08 to +0.15) with p below 0.05, and at least one of them clears 0.0125; the S&P groups do not. If a group clears the bar the claim is only "after a ≥ 4% semiconductor move, the more the next days' official documents lean against the move, the larger the reversal tends to be" — rank correlation ≈ 0.1–0.2 is a tilt, not a trade rule; a rule would need its own registration (entry at the document's release, fixed exit, costs). | — |
"""
TRACK = f"""
### 3.47 N1 v3a/v3b on record; v3c registered (11 Nov 14:45)
Grid on the reversal RATE: null in every testable group (#124 {'right' if p124 else 'wrong'}). Size test: {nsig} of {len(size)} cells below 0.05, all positive, and SOX rank correlations positive in {int((sox.rank_corr > 0).sum())} of {len(sox)} cells — the first non-flat N1 result (#125 {'right' if p125 else 'counted wrong'} on its sign clause). Joint size test v3c registered before running (prior #128; bar 0.0125). Corpus covers {share:.0%} of event days, {share20:.0%} from 2020 (#126 {'right' if p126 else 'wrong'}); #127 {'right' if p127 else 'counted wrong'}. Hindsight-leak caveat on LLM implication scores recorded. N1 spend ≈ US$18.9 of 25.
"""
p = Path("docs/prereg_news_events.md"); s = p.read_text()
if "v3b corpus survey |" in s: print("  prereg_news_events: v3a already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("  prereg_news_events: v3a/v3b results recorded; v3c registered (#128)")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.47 N1 v3a/v3b" in s: print("  TRACK: 3.47 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.47 appended")
