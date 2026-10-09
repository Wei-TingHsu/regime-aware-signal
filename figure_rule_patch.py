"""Standing rule for presenting figures (founder, 8 Oct) -> TRACK §7, the app's 'read this first' box, and the 18.16 sentence."""
from pathlib import Path
RULE = """
**Standing rule for every figure shown to the founder or an investor (8 Oct).** A number is never
shown alone. It carries, in this order: (1) **the population it is over** — the denominator in
words ("of the 100 days SPY moved more than 2σ *and* the engine had a document"); (2) **what it
measures and what it does not** ("how often the document present pointed against the move — not
how often the engine misread one, because on most of those days the document was not the driver");
(3) **its status** — *measured* (a count on history), *tested* (a registered criterion and a
verdict), or *registered, not run*; (4) **its date and source file**. A figure that cannot be
written in that form is not shown. "31% wrong" fails the rule; the sentence that replaces it is
in CURRENT_STATE §18.16.
"""
p = Path("docs/TRACK.md"); s = p.read_text()
if "Standing rule for every figure" not in s:
    k = s.find("**Two standing rules (7 Oct).**")
    if k >= 0: s = s[:k] + RULE.strip() + "\n\n" + s[k:]
    else:
        k7 = s.find("## 7."); eol = s.index("\n", k7) + 1; s = s[:eol] + RULE + s[eol:]
    p.write_text(s); print("TRACK §7: figure rule")
p = Path("docs/CURRENT_STATE_2026-08-23.md"); s = p.read_text()
old = "Readings: on the days that matter most, a document present is read backwards\nmore often than correctly for SPY, TLT and GLD — the referee's FAIL from the other side;"
new = ("Reading, in the form the figure rule requires: *of the 100 days SPY moved more than 2σ and the\n"
       "engine had any document, on 31 the document present pointed against the move.* That measures how\n"
       "often the engine was looking at a document that did not move the market, not how often it misread\n"
       "one: the attribution diagnostic of the same day found that most of those days were scheduled data\n"
       "releases or unfiled events the engine does not read. The genuine misread rate is not yet separable\n"
       "from this number; it is bounded above by it, and T16 Part B (two-bin attribution) splits it into\n"
       "*misread* and *not the driver* from its first run. Measured, 8 Oct, `docs/blindspot_backfill.md`;")
if old in s: s = s.replace(old, new); p.write_text(s); print("18.16: sentence rewritten under the rule")
else: print("18.16 anchor not found (already rewritten?)")
p = Path("app.py"); s = p.read_text()
old = '"C": "the engine\'s sources account for it"}[st_]'
new = '"C": "the engine\'s sources account for it"}[st_]  # B is relabelled \'misread\' vs \'not the driver\' once T16 attribution runs nightly'
if old in s and "relabelled" not in s:
    s = s.replace(old, new)
    s = s.replace('"B": "the engine read it backwards (wrong)",', '"B": "a document the engine read pointed the other way — on most such days the document was not the driver (see How this works)",')
    p.write_text(s); print("app: coverage wording no longer says 'wrong'")
