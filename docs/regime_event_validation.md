# Did Our Market "Weather" Match the Real News?

### A plain-language walkthrough of the regime–event alignment test

*From the Regime-Aware Cross-Asset Signal Framework. Written for someone new to statistics — every term is explained where it first appears.*

---

> **STATUS NOTE (read this first).** The event-alignment result described below was
> computed on the **original macro panel (≈2018 onward)**, where the risk-stress axis
> was PC2. We later **extended the panel back to 2006** (by dropping SOFR, which was
> truncating it) and re-fit the PCA. Two things changed as a result:
> (1) the components were renumbered — the VIX/risk-stress axis moved from PC2 to PC3;
> (2) **re-running this alignment on the extended basis, the n=4 result no longer reaches
> significance** (permutation p ≈ 0.32, 0 of 7 windows significant, versus p < 0.001
> before). So this document should be read as **(a) a correct explanation of the method**,
> which is unchanged, and **(b) a record of the original finding**, which did not survive
> the panel extension. The current, honest status of the regime-count choice is in the
> **"What the panel extension changed"** and **"Bottom line"** sections at the end.

---

## 1. The goal, in one sentence

We built a system that sorts every trading day into a small number of **market moods** (*regimes*), using only market data — interest rates, stock movements, a fear gauge called the VIX. The question:

> When our system says a day was a "stress" day, was there actually more stressful news happening that day in the real world?

If yes, that's reassuring: moods built purely from market numbers line up with something independent. If no, that's also worth knowing. We want the honest answer, not the flattering one — a principle that ends up mattering a great deal in this document.

## 2. The two things we compare

**The regimes.** Our model grouped days that "look alike" in market data into clusters; one behaves like a stress cluster (it lines up with high VIX). The model never saw any news when it built these groups.

**The news.** Separately, **GDELT** counts, for every day, how many news documents worldwide were tagged as financial *stress*. So each day has a number like "75,000 stress-tagged articles."

The whole test asks whether these two agree *more than they would by pure luck* — the heart of all statistics, and the thread through everything below.

## 3. A warm-up that worked: the Fed-day check

Before trusting the news data, we checked it against something certain: scheduled Fed meeting dates. We took the ten biggest *monetary-policy* news spikes and asked how many landed within a day of a real Fed meeting. **Nine of ten did.** The news dataset genuinely picks up real events. Our measuring stick is sound.

## 4. The first attempt — and why it quietly failed

The obvious approach: average the stress-news count on stress-regime days, average it on other days, divide to get a **ratio**. Above 1 = more stress news on stress days.

It came out ≈ **1.00** — no difference. Case closed? No. The stress-news count has an enormous **baseline**: *every* day has ~75,000 stress-tagged articles. Like a stadium murmur, it drowns out a single shout. The genuine extra stress on a truly stressful day is a small bump on a huge baseline, so the raw ratio gets **swamped**. That's not "no signal" — it's "this measurement is too blunt to see it." Confusing those two is one of the most common mistakes in data work.

## 5. Two sharper measurements

**Proportions ("share"):** stress articles ÷ total articles — the *fraction* of the day's news that's about stress, which cancels the volume baseline.

**Relative-to-recent-normal ("z-score"):** a **z-score** answers "how unusual is today versus lately?", measured in **standard deviations** (a standard deviation is the typical wiggle around the average). This ignores the constant baseline and reacts only to genuine spikes.

## 6. The luck test (the important idea)

We had ~30 stress-regime days scoring a small edge. To know if that edge is real, we ask: what edge would a *random* set of 30 days score? We **simulate luck**: slide the real stress days to a random spot on the calendar, re-measure, and repeat **5,000 times**. This is a **permutation test**; the "slide" is a **circular rotation** (days sliding off December wrap to January). Sliding rather than scattering preserves the *clumping* of real stress episodes, making the test fair. The **p-value** is the fraction of the 5,000 lucky runs that match or beat the real result: below 0.05 = unlikely to be luck (**statistically significant**); above 0.10 = indistinguishable from chance.

## 7. What the luck test said — on the original panel

On the original ≈2018+ panel, the z-score measure gave the **n=4** model **p = 0.000** (no random slide beat it), significant at 6 of 7 measurement windows. The proportions measure was a dead end (all p large). That was the headline: n=4's stress regime landed on days with *unusually elevated* stress news, and it was robust across windows.

**This is the result that did not survive the panel extension** — see the next section.

## 8. What the panel extension changed

Extending the panel to 2006 and re-fitting the PCA (with the stress axis now correctly identified as PC3, data-driven) and re-running the *same* method on 2024:

- **n=4 permutation p rose from < 0.001 to ≈ 0.32** — no longer significant.
- The window sweep went from **6/7 significant to 0/7**.
- n=3 and n=5 are also non-significant. No regime count shows event alignment on the extended basis.

Why? The alignment test is **2024-only, with ~30 stress days** — always the lowest-powered, most fragile piece of evidence (its standing caveat). Re-fitting the PCA on a longer span changes the 2024 clustering and which days count as "stress," and that single-year, small-sample test is sensitive to exactly that. The honest reading is **"the 2024 news corroboration is not robust to the analysis basis,"** not "n=4 is wrong."

## 9. Bottom line (honest, current)

The original "three independent lines converge on n=4" story **does not hold on the extended 2006+ panel.** Here is what actually stands:

**n=4 is still the best regime count — but on internal structural grounds, not this event-alignment.** On the full 2006–2026 history: n=4 is the most **seed-stable** (identical regimes across every random seed; n=5 is fragile), the most **persistent** (median regime lasts ~52 days — genuine macro states — while n=3 flickers with a 3-day median), and has the best **cluster separation** (silhouette). Neither n=3 (flickers) nor n=5 (unstable) is a serious competitor.

**What weakened:** the temporal generalization gap now mildly favors fewer regimes, and — as this document records — the 2024 event-alignment no longer corroborates n=4.

So n=4 is a **defensible choice justified by stability, persistence, and separation**, with its external/out-of-sample corroboration now honestly described as basis-sensitive and, for the 2024 event-alignment specifically, not reproduced on the extended panel. That is a weaker but *true* claim — and in data work, knowing the real strength of your evidence is itself the finding.
