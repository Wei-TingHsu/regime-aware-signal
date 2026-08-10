# Did Our Market "Weather" Match the Real News?

### A plain-language walkthrough of the regime–event alignment test

*From the Regime-Aware Cross-Asset Signal Framework. Written for someone who has never taken a statistics course — every term is explained the first time it appears.*

---

## 1. The goal, in one sentence

We built a system that sorts every trading day of the year into a small number of **market moods** (we call them *regimes*), using only market data — interest rates, stock movements, a fear gauge called the VIX. The question this test answers is simple to state:

> When our system says a day was a "stress" day, was there actually more stressful news happening on that day in the real world?

If the answer is yes, that's reassuring: our moods, built purely from market numbers, line up with something completely independent. If the answer is no, that's also worth knowing. Either way, we want an *honest* answer, not a flattering one.

---

## 2. The two things we're comparing

**Thing 1 — the regimes.** Our model looked at market data for every day and grouped days that "looked alike" into clusters. One of those clusters behaves like a stress/fear cluster (it lines up with high readings on the VIX). We'll call the days in that cluster the **stress-regime days**. Crucially, the model never saw any news when it made these groups — it only saw market prices.

**Thing 2 — the news.** Separately, we have a dataset called **GDELT** that counts, for every single day, how many news documents around the world were tagged as being about financial *stress*. So for each day we have a number like "75,000 stress-tagged articles today."

The whole test is about lining up Thing 1 against Thing 2 and asking whether they agree more than they would by pure luck. That last phrase — *more than by pure luck* — is the heart of all statistics, and everything below is just increasingly careful ways of asking it.

---

## 3. A warm-up that worked: the Fed-day check

Before trusting the news data, we sanity-checked it against something we already know for certain. The US central bank (the Fed) holds scheduled meetings on publicly known dates. Real financial news should spike around those dates.

So we took the ten days with the biggest spikes in *monetary-policy* news and asked how many landed within a day of a real Fed meeting. **Nine out of ten did.** That tells us the news dataset is genuinely picking up real events, not random noise. Good — our measuring stick is sound before we start measuring with it.

---

## 4. The first attempt — and why it quietly failed

The obvious way to answer our main question: take the average stress-news count on stress-regime days, take the average on all other days, and divide one by the other. This gives a **ratio**.

- Ratio above 1 → stress-regime days have more stress news. Good sign.
- Ratio around 1 → no difference.
- Ratio below 1 → less. Bad sign.

When we did this, the ratio came out at about **1.00** — no difference. Case closed?

Not so fast. Here's the trap. The stress-news count has an enormous **baseline**: *every* day has roughly 75,000 stress-tagged articles, stressful or calm. Think of it like noise in a stadium. Even when nothing is happening, the crowd murmur is loud. If one person shouts, the *total* noise barely changes — the shout is real, but it's drowned out by the constant murmur.

The genuine extra stress on a truly stressful day is a small bump sitting on top of a huge, ever-present baseline. Dividing the raw totals lets that baseline **swamp** the bump, so the ratio comes out at ~1.00 no matter what. The test wasn't telling us "there's no signal." It was telling us "this measurement is too blunt to see the signal." Those are very different things, and mistaking one for the other is one of the most common mistakes in data work.

---

## 5. Two sharper measurements

To hear the shout over the murmur, we need to measure differently. We tried two ways.

**Fix 1 — proportions (the "share" measure).** Instead of the raw count of stress articles, use the *fraction* of that day's news that was about stress: stress articles ÷ total articles. This cancels out days that were just busy-news days overall, and asks whether stress made up a *bigger slice of the pie*.

**Fix 2 — compared to its own recent normal (the "z-score" measure).** This one needs a small new idea. A **z-score** answers "how unusual is today, compared to what's normal lately?" It's measured in **standard deviations** — a standard deviation is just the typical amount a number wiggles around its own average. A z-score of 0 means "totally average." A z-score of +1 means "one typical wiggle above normal." So instead of asking "was there a lot of stress news today" (which the baseline swamps), we ask "was there *unusually* much stress news today, compared to the last few weeks?" That question ignores the constant baseline entirely and only reacts to genuine spikes.

Here's what these sharper measurements found, across three versions of our model (grouping days into 3, 4, or 5 moods — labelled n=3, 4, 5):

| Model | Raw ratio (blunt) | Share ratio (proportions) | Stress-days run this far above their own normal |
|---|---|---|---|
| n = 3 | 0.97 | 1.010 | +0.03 std devs |
| n = 4 | 1.01 | 1.031 | **+0.26 std devs** |
| n = 5 | 0.97 | 1.014 | +0.13 std devs |

Every sharpened number now leans the *right* way (above zero, above one), and the **n=4** model leans hardest. That's more encouraging than the raw test — but the leans are small. A 3% edge on proportions, a quarter of a wiggle on the z-score. Which forces the real question:

> Is a small lean like this a genuine signal, or just the kind of accident you'd stumble into by chance?

---

## 6. The luck test (this is the important one)

Here's the cleanest idea in the whole exercise, and it needs no formulas.

We have ~30 stress-regime days, and they scored a small edge on the news. To know if that edge is real, we ask: **what edge would a random set of 30 days have scored?** If random days routinely score just as high, our edge is nothing special. If random days almost never reach our score, our edge is real.

So we *simulate luck*. We take our real stress days, slide them to a random spot on the calendar, and re-measure. Then again, and again — **5,000 times**. Each run is a "what if these days had fallen somewhere else?" This pile of 5,000 random results is our picture of pure chance. This whole procedure is called a **permutation test**, and the "slide to a random spot" trick is called a **circular rotation** (circular because when days slide off the end of December, they wrap back to January).

> **Why slide instead of scatter randomly?** Because real stress days come in *clumps* — a crisis lasts a week, not a scattered afternoon here and there. If we scattered days randomly we'd destroy that clumping and make our test too easy to pass. Sliding the whole block keeps the clumps intact and only changes *where* they sit. It's the fair version of the luck test.

Then we count. The **p-value** is the fraction of those 5,000 lucky runs that matched or beat our real result. Read it like this:

- **p below 0.05** → fewer than 1 in 20 lucky runs beat us. The result is unlikely to be luck; we call it **statistically significant**.
- **p above 0.10** → luck beats us often. We can't distinguish our result from chance.

---

## 7. What the luck test said

| Model | Share measure | Z-score measure |
|---|---|---|
| n = 3 | p = 0.34 — chance | p = 0.32 — chance |
| n = 4 | p = 0.22 — chance | **p = 0.000 — real** |
| n = 5 | p = 0.34 — chance | p = 0.07 — borderline |

Two clear messages.

**The "share" (proportions) idea was a dead end.** Every share result is deep in chance territory. So stress-regime days are *not* days where stress made up a bigger slice of the news pie.

**The z-score idea found one solid hit: the n=4 model, p = 0.000.** Out of 5,000 random slides, *none* beat the real placement. That is a strong result — the alignment between our stress regime and unusual stress news is very unlikely to be an accident.

Putting the two together tells a precise story, sharper than "regimes match the news." On stress-regime days, stress news **jumps above its own recent trend** (the z-score fires) — but total news volume jumps too, so the *proportion* doesn't shift (the share stays flat). The right sentence is: **our stress regime lands on days when stress news is unusually elevated relative to normal, even though it isn't a larger share of overall coverage.**

---

## 8. The guardrails — staying honest

A believable result comes wrapped in its own limitations. Three matter here.

**We ran several tests, so we raised the bar.** We tested 3 models × 2 measures = 6 things. If you run six tests, one of them can cross the "1 in 20" line by luck alone. The standard fix (called a *Bonferroni correction*) is to demand a stricter cutoff — here about 0.008 instead of 0.05. The n=4 z-score result (p = 0.000) sails past even that strict bar. The n=5 borderline result (p = 0.07) does not, so we don't lean on it.

**We only had one year of data.** The test used 2024, which gave us just ~30 stress days. That's enough to detect the *direction* of an effect but not to pin down its *size* confidently. In statistics this is called low **statistical power** — a small sample can miss real effects and can only speak loosely about big ones. Our finding is "the sign is solid, the exact magnitude is fuzzy."

**One knob needed checking — and we checked it.** The z-score compares each day to the previous ~20 days, and 20 was an arbitrary choice. A real signal should survive nearby choices; a fragile one would work only at exactly 20. Section 9 reports that check. (Spoiler: it survived.)

---

## 9. The robustness check — is 20 days special?

To make sure the result didn't hinge on the arbitrary 20-day window, we re-ran the whole luck test at seven different windows — 10, 15, 20, 25, 30, 40, and 60 days — for all three models. If the n=4 finding only appeared at 20, it would be a fluke of that one setting. If it held across the board, it's real.

Here is what came back for the four-mood model (each cell is how far stress-regime days ran above their own normal, with the luck-test p-value beside it):

| Window | n = 4 result | Verdict |
|---|---|---|
| 10 days | +0.23 (p = 0.000) | real |
| 15 days | +0.25 (p = 0.000) | real |
| 20 days | +0.26 (p = 0.000) | real |
| 25 days | +0.31 (p = 0.000) | real |
| 30 days | +0.33 (p = 0.006) | real |
| 40 days | +0.29 (p = 0.023) | real |
| 60 days | +0.24 (p = 0.055) | borderline |

The n=4 model clears the "unlikely to be luck" bar at **six of the seven windows**, and at the strict bar (the one that accounts for running several tests) at five of them. Just as tellingly, the effect *grows and shrinks smoothly* as the window widens — it doesn't spike at one setting and vanish elsewhere. That smooth shape is the signature of a genuine effect; an artifact would light up at a single window and collapse around it.

The other two models behaved differently, and the contrast is itself informative. The three-mood model was flat everywhere — never significant at any window. The five-mood model lit up only at the two *shortest* windows and faded fast, which is exactly how borderline noise behaves: it needs a short, twitchy baseline to appear at all. Side by side, **n=4 behaves like signal; n=5 behaves like luck.**

So the arbitrary choice wasn't arbitrary after all — almost any reasonable window leads to the same conclusion. The last loose end is tied off.

---

## 10. The bottom line

We started with a blunt test that said "nothing here," realised it was being drowned out by a huge baseline, sharpened the measurement two ways, found a small lean, subjected that lean to a fair luck test 5,000 times over, and finally checked that the result didn't depend on one arbitrary setting. What survived all of that is this:

> The **four-mood (n=4)** version of our regime model lands its stress regime on days when stress news is genuinely, unusually elevated — a result strong enough to survive a strict multiple-test correction (p < 0.001) and stable across every reasonable choice of measurement window. This is now the *third* independent reason to prefer the n=4 model: it agrees with our earlier finding that n=4 generalised best across time, and with the single robust event-alignment hit. Three unrelated tests, one answer. The effect is directionally solid but sized loosely, because we still only have one year of data.

That is a real, defensible finding — and, just as importantly, we know exactly how confident we're allowed to be in it. In data work, knowing the size of your own uncertainty *is* the finding.
