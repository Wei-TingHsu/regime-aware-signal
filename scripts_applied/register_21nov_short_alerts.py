"""register_21nov_short_alerts.py -- founder, 21 Nov ('both yes'): (1) Grizzly Research, Blue Orca and Fuzzy Panda are read live as ALERTS;
(2) the one lead of SR-1 gets a forward record. TRACK 3.86; docs/SOURCES.md; docs/SOURCE_CANDIDATES.md. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.86 Short-report publishers read live as alerts; forward record of the 'during the session' lead (21 Nov 13:30)
**Founder (21 Nov): yes to both.**
**(1) Live alerts.** `src/news_listener.py` now also reads Grizzly Research, Blue Orca and Fuzzy Panda (Hunterbrook was already read; its reports on companies OUTSIDE the fourteen are now alerts too instead of being skipped). Admitted because SR-1 showed their kind of report moves the price on the day (TRACK 3.85) -- not because any rule exists. Each new item is read by SR-1's reader (`short-v1-2026-11-21`, title and the feed's own text, a fraction of a cent): is it a report, on which company, negative or positive, first report or follow-up, kind of claim, severity AS STATED, and whether it was published before the open, during the session or after the close. On the page it is a 'Short-seller report (unverified)', alert only; the 'Own stock' column shows direction x severity as stated (a negative report of severity 0.9 shows -0.90) -- that is the publisher's allegation, not Claude's view of the price. Notes, media coverage and replies are read and not shown. A source is scored only on items after its admission: the existing items of the three new sources are memorised, not read.
**(2) Forward record of the lead.** Lead (a split found after the fact in SR-1: 62 reports, next session fell a further 232 bp, fell on 69%): a NEGATIVE report on a US-listed company published DURING the New York session -- sell at that session's close, buy back at the next close; return minus the S&P 500. `python -m src.short_reports forward` counts it on reports published after 2026-11-21 05:00 UTC, taken from the publishers' own lists (so it does not depend on the listener being on); reports published before the open are listed beside it as the comparison. **Verdict at 30 complete reports, fixed now:** the lead becomes a registered candidate rule only if the average is above +30 bp (the cost assumption) AND the share fell on at least 55% of the reports AND fewer than 5% of 5,000 sets of other dates do as well; otherwise it is dropped. Every earlier look is labelled interim. At the publishers' present pace (roughly one such report a fortnight) 30 reports take about a year.
**Prior #178:** the lead shrinks: the forward average is under half of the 232 bp seen in the backtest split.
**Limits.** The fee to borrow shares is not counted; publishers may post on social media minutes before their website; daily prices.
"""
if "### 3.86 Short-report publishers read live" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.86 added")
else: print("  TRACK.md: 3.86 already there -- skipped")
p = Path("docs/SOURCES.md"); x = p.read_text(); rows = ("| third party | **Grizzly Research** (publishes short reports; may hold a short position) | publisher feed | **21 Nov 2026** | live as ALERTS (no rule); admitted after SR-1 (TRACK 3.85) |\n"
    "| third party | **Blue Orca** (short and some long reports; may hold a position) | publisher feed | **21 Nov 2026** | live as ALERTS (no rule) |\n| third party | **Fuzzy Panda** (publishes short reports; may hold a short position) | publisher feed | **21 Nov 2026** | live as ALERTS (no rule) |\n")
if "**Grizzly Research**" in x: print("  SOURCES.md: already has the three publishers")
else:
    i = x.find("| third party | **SemiAnalysis**"); j = x.find("\n", i) if i != -1 else -1
    if j == -1: print("  SOURCES.md: the SemiAnalysis row was not found -- unchanged. Tell Claude.")
    else: p.write_text(x[:j + 1] + rows + x[j + 1:]); print("  SOURCES.md: Grizzly Research, Blue Orca, Fuzzy Panda added (live as alerts)")
c = Path("docs/SOURCE_CANDIDATES.md"); y = c.read_text(); old = "Qualify as live ALERTS (no rule): Grizzly, Blue Orca, Fuzzy Panda, Hunterbrook -- founder's decision."; new = "Read live as ALERTS since 21 Nov (no rule): Grizzly, Blue Orca, Fuzzy Panda, Hunterbrook (TRACK 3.86)."
if old in y: c.write_text(y.replace(old, new)); print("  SOURCE_CANDIDATES.md: short-report row updated")
else: print("  SOURCE_CANDIDATES.md: already updated or not found -- unchanged")
