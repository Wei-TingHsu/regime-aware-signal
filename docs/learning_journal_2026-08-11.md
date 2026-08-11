# Learning Journal — 2026-08-11

**Session theme:** Problem 1 (safe-haven inversion), macro-panel history, and an honest re-validation of the regime count.

---

### 1. Problem 1 — safe-haven inversion test

**Route:** Built a liquidity sub-classifier (2-component GMM on cross-asset correlation breadth + realized vol, on a core basket excluding gold/equity to avoid circularity) → validated its states (stress state over-samples crisis episodes ~2.9×) → tested the GLD–SPY 20-day correlation across states, permutation-tested, with the n=4 macro regime as cross-check → ran a robustness sweep (windows 5/10/20/60 × raw vs Fisher-z).

**Reasoning:** Chose a *separate* liquidity classifier over reusing the macro regime because the macro regime is built partly from VIX, and the outcome (gold–equity correlation) moves with VIX — reusing it would make the test semi-circular.

**Outcome — NEGATIVE and robust:** No inversion under either definition (liquidity gap +0.017, p=0.44; macro gap +0.16, wrong direction). Gold does **not** decouple from equities in stress; if anything it co-moves slightly more — consistent with **dash-for-cash** selling. A clean, well-tested negative finding that contradicts a popular intuition.

### 2. Extending the macro panel (2018+ → 2006+)

**Reasoning:** The macro cross-check only spanned ~2018+ because the PCA panel inner-joins its FRED series and SOFR (starts 2018) truncated it. Checked SOFR vs EFFR (already in the panel): R²=0.998, level corr 0.999 → SOFR is redundant.

**Route:** Dropped SOFR → refit panel + PCA → panel now spans 2006+ (DTWEXBGS becomes the binding series). **No imputation, no weaker data** — the key principle: extend history by removing a redundant series, not by manufacturing data.

### 3. A bug the refit exposed — PC renumbering

**Reasoning:** Refitting PCA on a different span renumbers/re-signs components. The VIX/risk-stress axis **moved from PC2 to PC3**. Every script that hard-coded "stress = highest PC2" would now silently mislabel the stress regime.

**Route:** Built `stress_axis.py` — selects the stress axis **data-drivenly** (PC most correlated with VIX), robust to any future refit. Ported it into the safe-haven and event-alignment scripts. **Lesson: never hard-code a component index; identify axes by economic meaning.** This also revealed the earlier macro cross-check had accidentally conditioned on the money/dollar axis, producing a spurious −0.207 gap that vanished once corrected.

### 4. Honest re-validation of n=4 (Option B)

**Reasoning:** After the refit, chose to re-run the *full* count selection (not just a spot-check) — because if n=4 had shifted on the new basis, a spot-check would have hidden it and we'd redo the work anyway. Better to catch it now than work on luck.

**Outcome — MIXED, not the old "confirmed":**
- **Still favors n=4 (internal structure):** seed-stability ARI 1.000 (n=5 fragile at 0.774); run-length persistence median 52.5 days (n=3 flickers at 3-day median); best silhouette.
- **Weakened (external validation):** generalization gap now favors fewer regimes (n=3 +0.45 vs n=4 +4.89); 2024 event-alignment **collapsed** (n=4 permutation p 0.32, 0/7 windows — was p<0.001 on the old panel).

**Decision:** Keep n=4 — it is the only partition that is stable, persistent, and well-separated; n=3 flickers, n=5 is fragile. But **re-document honestly**: n=4 rests on structural grounds, not the event-alignment, which is 2024-only, low-powered, and basis-sensitive. Corrected the explainer and methodology log rather than ship docs the code no longer reproduces.

---

### Methodological lessons
1. A null result deserves the same scrutiny as a positive one (robustness sweep before banking Problem 1).
2. Extend data by removing redundancy, never by imputation.
3. Identify axes by meaning, not index — refits renumber components.
4. Re-validate, don't assume, when you change the substrate underneath prior conclusions.
5. Correct the record when new evidence weakens an earlier claim; "structurally best but weaker corroboration" is a truer finding than an overstated one.
