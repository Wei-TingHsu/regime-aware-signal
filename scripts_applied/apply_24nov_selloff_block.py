"""apply_24nov_selloff_block.py -- the Severe Sell-off block shows the tested rules SS-2a, SS-2b, SS-2c (src/selloff_live.py) in place of the weak plain
rule SS-1 (founder's decision, 24 Nov; TRACK 3.110), and TRACK 3.111 records the daily check. Idempotent."""
from pathlib import Path
p = Path("src/live_page.py"); s = p.read_text(); a = "            from src import selloff_forward as _F\n            st.markdown(_F.CARD_CSS + _F.card_html(), unsafe_allow_html=True)"
b = "            from src import selloff_live as _F      # 24 Nov 2026: the tested rules SS-2a/b/c, with the page's colours\n            st.markdown(_F.card_html(), unsafe_allow_html=True)"
if "from src import selloff_live as _F" in s: print("  live_page.py: already shows the tested rules -- skipped")
elif a in s: p.write_text(s.replace(a, b)); print("  live_page.py: the block now shows SS-2a, SS-2b, SS-2c (restart the app)")
else: print("  live_page.py: the two lines were not found -- NOT changed; tell Claude")
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.111 The rules are frozen exactly; the daily check, the forward record and the block (24 Nov 19:40)
**Freeze (commit 4a27fe1).** The copy of the search's item builder gives the same 310 items as the search. All three rules reproduce EXACTLY: SS-2a 91 sell-offs in 2005-2017 and 94 in 2018-2026; SS-2b 204 and 168; SS-2c 166 and 214. `docs/selloff_rules.json` holds every cut and the two machine groups as numbers (SS-2a: 7 columns of 'who fell and who set it off'; SS-2b: 12 columns of 'the fall and the market').
**The daily check (`python -m src.selloff_live daily`, once a day after the New York close; free; about 5 to 10 minutes).** It downloads prices (Yahoo), the 8-K list (SEC) and the two index series of SS-2b (FRED: USEPUINDXD, STLFSI4) into a SEPARATE folder `data_provenance/selloff_live`, rebuilds the events and tables there with the study's own code, applies the frozen rules to every sell-off of 5% from 24 Nov 2026, records each match and fills in what followed. **The study's folder `data_provenance/selloff` is never written, so 3.98-3.110 stay reproducible.** A bar of a session that is not finished is left out.
**What is approximate, stated plainly.** (1) 'Size rank in the list' (SS-2c) uses the reported financials copied once from the study's folder; they change once a quarter and are not refreshed by the daily check yet. (2) The entry and exit days shown on the block are the next weekdays; public holidays are not known to the code (the forward record itself uses the real sessions). (3) If FRED cannot be reached, SS-2b is marked 'not checkable' for that day instead of being guessed. (4) A sell-off is seen only after the close and only when the daily check is run: the block says when it was last checked and asks for a run after 30 hours.
**The block.** 'Severe Sell-off' now shows SS-2a, SS-2b, SS-2c with the page's colours: red from the close of the sell-off day until 5 minutes after the next open, yellow until the rule's exit, green for 24 hours. SS-1 is no longer shown; its forward record (3.101) keeps running inside the daily check.
"""
if "### 3.111 The rules are frozen exactly" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.111 added")
else: print("  TRACK.md: 3.111 already there -- skipped")
