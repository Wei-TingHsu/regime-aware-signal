"""record_12nov_e2all.py -- E2-all on record (#144); the second SUBJECTIVE grade A candidate filed (small); the founder's AI-chain earnings test
written down as a DESIGN (not yet registered) with his company list and the listing-day agenda item. Idempotent."""
import json
from pathlib import Path
R = json.loads(Path("docs/intraday_v3e_releases_all.json").read_text()); rep = R["replication"]
# The first run's JSON kept only three of the four replication rows (two rows shared the label "same", so the S&P row of cell 2 was overwritten by cell 4 --
# fixed in the code now). Cells 1, 3, 4 are read from the JSON; cell 2 is taken from the run's printed table (docs/intraday_v3e_releases_all.md).
k1 = next(x for x in rep if "against the score" in x and x.endswith("NQ")); k3 = next(x for x in rep if "hold 30" in x and x.endswith("NQ")); k4 = next(x for x in rep if x.endswith("ES"))
CELL2 = "+3.1 bp, t +1.96, hit 56%, n 144, one-sided p 0.024"
def c(x): v = rep[x]; return f"{v['mean']:+.1f} bp, t {v['t']:+.2f}, hit {v['hit']:.0%}, n {v['n']}, one-sided p {v['p']:.3f}"
def b(d): x = d["best"]; return f"enter {x['entry']} min, hold {x['exit']}: {x['mean']:+.1f} bp, t {x['t']:+.2f}, hit {x['hit']:.0%}, n {x['n']}; family p {d['p_family']:.3f}"
main = rep[k1]; p144 = main["mean"] > 0 and not (main["p"] < 0.05)
print(f"#144 {'right' if p144 else 'WRONG'}: replication cell (1) {c(k1)}")
ROWS = f"""| 2026-11-12 | E2-all — every BLS release of the five series from June 2010 scored (680 more reads, US$10.52); {R['continuation']['ES']['n_days']} release days | First 5 minutes agree in sign with the composition score on {R['first_move_vs_score']['same_sign']:.0%} of days (n {R['first_move_vs_score']['n']}). All days — continuation: S&P {b(R['continuation']['ES'])}; Nasdaq {b(R['continuation']['NQ'])}. Score: S&P {b(R['score']['ES'])}; Nasdaq {b(R['score']['NQ'])}. First move against the score ({R['score_disagrees']['NQ']['n_days']} days): S&P {b(R['score_disagrees']['ES'])}; Nasdaq {b(R['score_disagrees']['NQ'])}. **Replication on the NEW days only (cells fixed in advance, no search):** (1) first 5 minutes against the score → enter the Nasdaq future with the score at 5 minutes, hold 60: **{c(k1)}**; (2) same, S&P future: {CELL2}; (3) all days, enter with the score at 5 minutes, hold 30, Nasdaq: {c(k3)}; (4) same, S&P: {c(k4)}. | **Cell (1) replicates at p < 0.05 on days never looked at → SUBJECTIVE grade A candidate** by the registered verdict. Size matters: +3.7 bp on the new days (+7.9 bp on all days) over an hour, against a 2 bp cost — real but thin; right on 60% of days. Plain reading: when the first five minutes after an 08:30 release go against what the document's composition says, prices tend to come round to the document over the next hour. The score on its own (cells 3–4) does not replicate. | **#144 {'right' if p144 else 'wrong (counted)'}** — predicted it would not reach p < 0.05; the size did fall below +7 bp as predicted |
"""
TRACK = f"""
### 3.59 E2-all result; AI-chain earnings test designed (12 Nov 02:20)
**E2-all.** On the 671 release days never looked at, the fixed rule "first five minutes against the document's score → enter the Nasdaq future with the score, hold 60 minutes" gives {c(k1)}; the S&P future {CELL2}. Replicates → second SUBJECTIVE grade A candidate, thin after cost (#144 {'right' if p144 else 'counted wrong'}). N1/intraday LLM spend to date ≈ US$30.5 (the founder authorised going past the earlier US$25 cap for this test).

**AI-chain earnings test — DESIGN, not yet registered (founder, 12 Nov).** Founder: only about six trades a year come from Fed statements; apply the same test to company news, because "these companies' financial reports can alter the whole market's basic logic — all are parts of the same chain called artificial intelligence", and one good report can lift the whole index.
- **Companies (founder's list):** AMD, NVDA, MU, INTC, AVGO, SNDK, SKHY (SK Hynix), ORCL, TSM, CRWD, GOOG, META, AMZN, MSFT. To be added when they have completed a listing: Anthropic and OpenAI (agenda item; nothing to test before then).
- **Events:** each company's quarterly results release — about 56 a year. Release minute from the SEC's acceptance timestamp of the filing (8-K item 2.02; 6-K for TSM). Stated limits: the filing can reach the SEC some minutes after the news wire; SK Hynix reports in Korea, outside the SEC, and needs its own source and time; SanDisk has traded again only since 2025.
- **Score:** the same story-free reader as the Fed statements (what the document means for stocks, −1 … +1), on the release text; a sample is checked first, because the reader has so far scored only official statistics and Fed documents. The project's earlier v1 reads of earnings filings (ASML, TSM, TSLA, ORCL, LMT, MU, INTC, NVDA, MSFT) are a different schema and are not pooled.
- **Test (same structure as E1(c)):** enter 1 minute after the release in the direction of the score; hold 15 / 30 / 60 minutes and to the next 09:30. Measured on (i) the Nasdaq-100 future — already on disk, trades after the close, and these companies are its largest weights, so it is the right instrument for "moves the whole market"; (ii) the company's own stock and the semiconductor ETFs, minute prices including before and after hours — to be bought (Stage 2). Checks as for E1(c): shuffled scores, no link before the release, periods, score strength, without the ten largest days; spill-over from one company's release to the other thirteen.
- **Data route:** quote Databento's US-equity datasets against the remaining credit first (`intraday_fetch equities`, quote only); a second free-credit account is not used (one promotional credit per user is the vendor's term); otherwise pay as you go or one month of Alpha Vantage.
- **Order:** quote → founder decides the purchase → registration with priors → filings and release times fetched → scores → Stage 1 on the future → Stage 2 on the stocks.
"""
p = Path("docs/prereg_intraday_v3e.md"); s = p.read_text()
if "E2-all — every BLS release" in s: print("  prereg_intraday_v3e: already recorded -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + ROWS); print("  prereg_intraday_v3e: E2-all result recorded (#144)")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.59 E2-all result" in s: print("  TRACK: 3.59 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.59 appended (E2-all; AI-chain earnings design; company list; listing agenda item)")
bk = Path("docs/TEST_BOOK.md"); s = bk.read_text(); line = "| **E2-all** | **08:30 releases, days never looked at: first 5 minutes against the document's score → enter the Nasdaq future with the score, hold 60 minutes** | **replicates: " + c(k1) + "; all days +7.9 bp, 60%** | **SUBJECTIVE grade A candidate** — thin after a 2 bp cost |\n"
if "| **E2-all** |" in s: print("  TEST_BOOK: E2-all row already present -- skipped")
elif "\n**Lists after the intraday tests.**" in s: bk.write_text(s.replace("\n**Lists after the intraday tests.**", line + "\n**Lists after the intraday tests.**", 1)); print("  TEST_BOOK: E2-all row added to B8")
else: print("  TEST_BOOK: B8 not found -- row not added")
