"""record_21nov_lag_plan.py -- TRACK 3.83: the three steps to shorten the lag (founder, 21 Nov: 'you are to follow the steps'), what is built, what is
measured before anything is changed, and the server price found. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.83 Shortening the lag: three steps, measurement first (21 Nov 13:00)
**Founder (21 Nov):** follow the steps for how the lag can be shortened; the page is accepted as it is.
**Step 1 -- a machine that is always on (removes the 8,000-83,000 s cases).** Needs: Python, 1 GB of memory, the listener and the page running permanently, the Anthropic key typed there by the founder. Price found 21 Nov (third-party price tracker cloudtally.eu, 'verified 10 Nov 2026', excluding VAT; to be confirmed on the provider's own page before buying): Hetzner's smallest server (1 processor, 1 GB) about EUR 4.99 a month in Finland, EUR 5.99 in Germany, EUR 7.49 in Singapore; the 2-processor 4 GB type about EUR 5.49 where available. DigitalOcean's price could not be verified today. Open risk: some sources refuse requests from data-centre addresses -- the lag watch is run on the server on its first day. **Decision is the founder's (provider, go or no-go).**
**Step 2 -- faster addresses.** Already known (docs/wire_probe.md, 15 Nov): Business Wire and GlobeNewswire refuse scripts; most company investor pages refuse or have no feed; that is not worked around. What is left and free: the SEC has TWO addresses for the same filing -- one list of the latest filings of all companies, and each company's own list (what the listener uses, 14 requests per pass). Which is earlier is not known. `src/lag_watch.py` measures both on every 8-K and 6-K of the whole market (hundreds a day), against the SEC's acceptance time.
**Step 3 -- checking more often than every 30 seconds.** The same watch checks the SEC lists every 5 s and the feeds every 15 s and counts refusals (HTTP 403/429); a source that refuses three times in a row is left alone.
**Rule for the change.** The listener is changed only after the watch has run in US hours: the SEC address that is earlier on the middle filing becomes the listener's SEC route, and the checking interval is lowered to what was not refused. Prior #171: the single list is earlier than the company's own list on most filings. Prior #172: no source refuses at these frequencies.
**Also seen:** PR Newswire's 'all releases' feed holds only 20 items; in a busy minute more than 20 releases can be published, so at one check every 30 s items can be missed altogether -- the watch's 15 s checks will show how fast the list turns over.
"""
if "### 3.83 Shortening the lag" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.83 added")
else: print("  TRACK.md: 3.83 already there -- skipped")
