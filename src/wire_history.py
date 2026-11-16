"""wire_history.py -- step 2 of the agenda: can the PAST release times be collected from PR Newswire's company pages? (The other two wires refuse
scripts from this machine, docs/wire_probe.md.) Read-only probe: for each company it tries a few candidate page addresses, counts the items that carry a
clock time, counts the results releases among them, and checks whether older pages can be reached. Writes docs/wire_history_probe.md. No cost, no key.

The page addresses are CANDIDATES (Claude's guesses at how PR Newswire names each company's page); the probe shows which are real.

    python -m src.wire_history probe
"""
from __future__ import annotations
import re, time, urllib.request, urllib.error
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.prnewswire.com/news/{slug}/?page={page}&pagesize=100"
SLUGS = {"META": ["meta", "meta-platforms,-inc.", "facebook"], "ORCL": ["oracle", "oracle-corporation"], "AVGO": ["broadcom-inc.", "broadcom", "broadcom-limited"], "MSFT": ["microsoft-corp.", "microsoft", "microsoft-corporation"],
         "INTC": ["intel-corporation", "intel"], "MU": ["micron-technology,-inc.", "micron-technology", "micron"], "AMZN": ["amazon.com,-inc.", "amazon", "amazon.com"], "NVDA": ["nvidia", "nvidia-corporation"],
         "AMD": ["amd", "advanced-micro-devices"], "CRWD": ["crowdstrike", "crowdstrike-holdings,-inc."], "SNDK": ["sandisk", "sandisk-corporation"], "GOOG": ["alphabet-inc.", "google", "alphabet"], "TSM": ["tsmc", "taiwan-semiconductor-manufacturing-company"], "SKHY": ["sk-hynix", "sk-hynix-inc."]}
RX_ITEM = r"<small[^>]*>\s*([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}\s+ET)\s*</small>\s*(.*?)\s*</h3>"
RX_RESULTS = r"\b(reports?|announces?|posts?|delivers?)\b.*\b(quarter(ly)?|results|earnings)\b"; RX_NOT = r"\b(to (report|announce|host|release|webcast|present)|sets? (date|conference)|conference call|date for|schedules?|will (report|announce|host))\b"


def get(url):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"}), timeout=25); return r.status, r.read(3_000_000).decode("utf-8", "ignore")


def items(html: str) -> list:
    return [(re.sub(r"\s+", " ", t), re.sub(r"<[^>]+>", "", re.sub(r"\s+", " ", title)).strip()) for t, title in re.findall(RX_ITEM, html, flags=re.S)]


def probe():
    L = ["# PR Newswire company pages: can past release times be collected?", "", "| company | page that answered | items with a clock time (page 1) | results releases among them | newest | oldest on page 1 | page 2 reachable | oldest on page 5 |", "|---|---|---|---|---|---|---|---|"]; sample = None
    for tk, slugs in SLUGS.items():
        found = None
        for slug in slugs:
            try: status, html = get(BASE.format(slug=slug, page=1))
            except urllib.error.HTTPError as e: print(f"  {tk:5} /news/{slug}/: HTTP {e.code}"); time.sleep(0.5); continue
            except Exception as e: print(f"  {tk:5} /news/{slug}/: {type(e).__name__}: {str(e)[:60]}"); time.sleep(0.5); continue
            it = items(html); time.sleep(0.5)
            if not it: print(f"  {tk:5} /news/{slug}/: HTTP {status}, {len(html) // 1000} KB, but no dated items in the layout the probe expects"); sample = sample or html; continue
            found = (slug, it); break
        if not found: L.append(f"| {tk} | none of {', '.join(slugs)} | | | | | | |"); continue
        slug, it = found; res = [x for x in it if re.search(RX_RESULTS, x[1], re.I) and not re.search(RX_NOT, x[1], re.I)]; p2 = p5 = ""
        try:
            _, h2 = get(BASE.format(slug=slug, page=2)); i2 = items(h2); p2 = f"yes, {len(i2)} items, oldest {i2[-1][0]}" if i2 and i2[0] != it[0] else ("no (same as page 1)" if i2 else "no items"); time.sleep(0.5)
            _, h5 = get(BASE.format(slug=slug, page=5)); i5 = items(h5); p5 = i5[-1][0] if i5 and i5[0] != it[0] else "not reachable"
        except Exception as e: p2 = p2 or f"{type(e).__name__}"
        print(f"  {tk:5} /news/{slug}/: {len(it)} dated items, {len(res)} results releases; newest {it[0][0]}; oldest on page 1 {it[-1][0]}; page 2: {p2}; page 5 oldest: {p5}")
        for x in res[:2]: print(f"          e.g. {x[0]} | {x[1][:90]}")
        L.append(f"| {tk} | /news/{slug}/ | {len(it)} | {len(res)}" + (f" (e.g. {res[0][0]}: {res[0][1][:60]})" if res else "") + f" | {it[0][0]} | {it[-1][0]} | {p2} | {p5} |"); time.sleep(0.5)
    if sample:
        m = re.search(r"\d{1,2}:\d{2}\s+ET", sample); a = max(0, (m.start() if m else 3000) - 500); print("\nA page answered but its layout was not recognised. A piece of it, for Claude to adjust the probe:\n" + re.sub(r"\s+", " ", sample[a:a + 1100]))
    Path("docs").mkdir(exist_ok=True); Path("docs/wire_history_probe.md").write_text("\n".join(L) + "\n"); print("-> docs/wire_history_probe.md")


# ------------------------------------------------------------------------------------------------ W1: collect, compare the two clocks, rerun
# Probe result (17 Nov): PR Newswire holds the past releases of four of the twelve US filers -- Meta, Oracle, Broadcom, Microsoft. The others publish
# through wires that refuse scripts. W1 is therefore a four-company answer, stated as such.
PAGES = {"META": "meta", "ORCL": "oracle", "AVGO": "broadcom-inc.", "MSFT": "microsoft-corp."}
WIRE = Path("data_provenance/ai_earnings/wire_times.csv"); RX_KEY = r"quarter|results|earnings|\bQ[1-4]\b|fiscal"; RX_SKIP = RX_NOT + r"|\b(dividend|offers? to purchase|offering|release date|notes)\b"
CELLS = [("own_stock", 1, 60), ("own_stock", 5, 60), ("own_stock", 15, 60), ("market", 5, 30)]      # the selling-point table and FA-3's cell; fixed, no search


def _save(rows: list, source: str):
    import pandas as pd
    W = pd.DataFrame(rows)
    if W.empty: print("  nothing collected"); return
    W["source"] = source; W = W.dropna(subset=["wire_time"])
    if WIRE.exists(): old = pd.read_csv(WIRE, parse_dates=["wire_time"]); old["source"] = old.get("source", "PR Newswire company page"); W = pd.concat([old, W], ignore_index=True)
    W = W.drop_duplicates(["ticker", "wire_time", "title"]).sort_values(["ticker", "wire_time"]); WIRE.parent.mkdir(parents=True, exist_ok=True); W.to_csv(WIRE, index=False); print(f"-> {WIRE}: {len(W)} items in all; by company: " + ", ".join(f"{k} {v}" for k, v in W.ticker.value_counts().sort_index().items()))


OWN = {"INTC": "https://www.intc.com/news-events/press-releases", "AMD": "https://ir.amd.com/news-events/press-releases"}      # probe 2: both lists answer, print clock times, and page with ?page=N
RX_OWN_T = r"([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})\s+(\d{1,2}:\d{2}\s?[AaPp][Mm])\s+E[SD]T"; RX_OWN_L = r'href="([^"]*press-releases/detail/\d+[^"]*)"'


def collect_own(stop="2018-04-01"):
    """Intel's and AMD's own press-release lists: each page prints one clock time per release, in the same order as the links; the title is read from the link."""
    import pandas as pd
    rows = []
    for tk, base in OWN.items():
        prev = None; n = bad = 0
        for page in range(1, 201):
            try: _, html = get(f"{base}?page={page}")
            except Exception as e: print(f"  {tk} page {page}: {type(e).__name__}"); break
            time.sleep(0.5); text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S))); ts = re.findall(RX_OWN_T, text); links = list(dict.fromkeys(re.findall(RX_OWN_L, html)))
            if not ts or links == prev: break
            prev = links
            if len(ts) != len(links): bad += 1; continue      # the page's times and links do not pair one to one: skipped, counted
            got = [dict(ticker=tk, wire_time=pd.to_datetime(f"{d} {c.upper().replace(' ', '')}", format="%b %d, %Y %I:%M%p", errors="coerce"), title=l.rstrip("/").split("/")[-1].replace("-", " ")) for (d, c), l in zip(ts, links)]; rows += got; n += len(got)
            if min(g["wire_time"] for g in got) < pd.Timestamp(stop): break
        w = [r["wire_time"] for r in rows if r["ticker"] == tk and pd.notna(r["wire_time"])]; print(f"  {tk}: {n} releases with a time" + (f", {min(w):%Y-%m-%d} -> {max(w):%Y-%m-%d}" if w else "") + (f"; {bad} pages skipped (times and links did not pair)" if bad else ""))
    _save(rows, "company's own press-release list")


MIRROR = {"AMZN": ["bizwire"], "CRWD": ["bizwire"], "SNDK": ["bizwire"], "INTC": ["bizwire"], "MU": ["gnwcq", "globenewswire"], "NVDA": ["gnwcq", "globenewswire"]}      # which wire each uses; the mirror's address starts with the wire's tag (bizwire is confirmed; the GlobeNewswire tag is a guess)
NAME = {"AMZN": r"Amazon\.com", "CRWD": "CrowdStrike", "SNDK": "Sandisk", "INTC": "Intel", "MU": "Micron", "NVDA": "NVIDIA"}


def _title(path: str, tk: str):
    lines = [re.sub(r"\s+", " ", x).strip() for x in Path(path).read_text()[:400000].split("\n")]; lines = [x for x in lines if x]
    for i, t in enumerate(lines):
        if 4 <= len(t.split()) <= 26 and re.match(rf"^{NAME[tk]}\b.*\b(Reports?|Announces?)\b", t, re.I) and re.search(r"quarter|results|fiscal", t, re.I):
            if re.search(r"\b(the|for|of|and|fiscal|record|quarter)$", t, re.I) and i + 1 < len(lines) and len(lines[i + 1].split()) <= 12: t = t + " " + lines[i + 1]      # a title broken over two lines
            return t
    return None


def collect_mirror(limit=None):
    """For the companies whose wire refuses scripts: build the public mirror's address of each past results release from its date and title (the pattern of
    the one confirmed page), and read 'Published at ... via <wire>'. A try-and-see collector: it reports how many it found, and shows addresses that failed."""
    import pandas as pd
    F = pd.read_csv("processed/ai_earnings_filings.csv", parse_dates=["accepted_ny"]); F = F[(F.form == "8-K") & F.file.notna() & (F.accepted_ny >= "2018-05-01") & F.ticker.isin(MIRROR)]; rows = []
    for tk, g in F.groupby("ticker"):
        g = g.sort_values("accepted_ny", ascending=False); g = g if limit is None else g.head(limit); hit = no_title = 0; fails = []
        for r in g.itertuples():
            t = _title(r.file, tk)
            if not t: no_title += 1; continue
            d = r.accepted_ny; slugs = list(dict.fromkeys([re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-"), re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", t.lower())).strip("-")])); dates = list(dict.fromkeys([f"{d.year}-{d.month}-{d.day}", f"{d:%Y-%m-%d}"])); found = None
            for url in [f"https://www.financialcontent.com/article/{pre}-{dt}-{sl}" for pre in MIRROR[tk] for dt in dates for sl in slugs]:
                try: _, html = get(url)
                except Exception: time.sleep(0.4); continue
                time.sleep(0.4); m = re.search(r"Published at\s+([A-Z][a-z]+ \d{1,2})(?:st|nd|rd|th)? (\d{4}), (\d{1,2}:\d{2} [AP]M) E[SD]T\s+via\s+([A-Za-z ]+)", re.sub(r"<[^>]+>", " ", html))
                if m: found = (pd.to_datetime(f"{m.group(1)} {m.group(2)} {m.group(3)}", format="%B %d %Y %I:%M %p", errors="coerce"), m.group(4).strip()); break
            if found: hit += 1; rows.append(dict(ticker=tk, wire_time=found[0], title=t))
            elif len(fails) < 2: fails.append(f"https://www.financialcontent.com/article/{MIRROR[tk][0]}-{dates[0]}-{slugs[0]}")
        print(f"  {tk}: {hit} of {len(g)} past results releases found on the mirror" + (f"; no title recognised in {no_title} texts" if no_title else "") + ("".join(f"\n      not found, e.g. {u}" for u in fails)))
    _save(rows, "public mirror of the wire (secondary source)")


def collect():
    import pandas as pd
    rows = []
    for tk, slug in PAGES.items():
        prev = None; n = 0
        for page in range(1, 61):
            try: _, html = get(BASE.format(slug=slug, page=page))
            except Exception as e: print(f"  {tk} page {page}: {type(e).__name__}"); break
            it = items(html); time.sleep(0.6)
            if not it or it == prev: break
            prev = it; n += len(it); rows += [dict(ticker=tk, wire_time=pd.to_datetime(t.replace(" ET", ""), format="%b %d, %Y, %H:%M", errors="coerce"), title=x.replace("&amp;", "&")) for t, x in it]
        w = [r["wire_time"] for r in rows if r["ticker"] == tk and pd.notna(r["wire_time"])]; print(f"  {tk}: {n} dated items" + (f", {min(w):%Y-%m-%d} -> {max(w):%Y-%m-%d}" if w else ""))
    _save(rows, "PR Newswire company page")


def matched():
    """each SEC results release of the four companies with the wire item of the same release: same New York day, a results-like title, published
    between 3 hours before the SEC stamp and 30 minutes after it; the earliest such item"""
    import pandas as pd
    W = pd.read_csv(WIRE, parse_dates=["wire_time"]); S = pd.read_csv("processed/ai_earnings_scores.csv", parse_dates=["accepted_ny"]); S = S[S.ticker.isin(set(W.ticker))]; out = []
    keep = W.title.apply(lambda t: bool(re.search(RX_KEY, t, re.I)) and not re.search(RX_SKIP, t, re.I)); W = W[keep]
    for r in S.itertuples():
        c = W[(W.ticker == r.ticker) & (W.wire_time >= r.accepted_ny - pd.Timedelta(hours=3)) & (W.wire_time <= r.accepted_ny + pd.Timedelta(minutes=30))]
        if len(c): w = c.sort_values("wire_time").iloc[0]; out.append(dict(ticker=r.ticker, accession=r.accession, sec_time=r.accepted_ny, wire_time=w.wire_time, lag_min=(r.accepted_ny - w.wire_time).total_seconds() / 60, title=w.title, own_stock=r.own_stock, market=r.market))
    return pd.DataFrame(out), len(S)


def lag():
    M, n = matched(); L = ["# W1: how late is the SEC stamp against the news wire?", "", "Wire times from PR Newswire's company pages, the companies' own press-release lists, and a public mirror of the wire (`data_provenance/ai_earnings/wire_times.csv`, column `source`).", ""]
    if M.empty: print("no release could be matched"); return
    print(f"matched {len(M)} of {n} results releases of {M.ticker.nunique()} companies ({M.sec_time.min():%Y-%m-%d} -> {M.sec_time.max():%Y-%m-%d})"); L += [f"Matched {len(M)} of {n} results releases. Lag = SEC stamp minus wire time, in minutes (the wire states whole minutes).", "", "| company | matched | median lag | wire first | lag 0-2 min | 2-10 min | 10-30 min | over 30 min | SEC first |", "|---|---|---|---|---|---|---|---|---|"]
    for k, g in list(M.groupby("ticker")) + [("all", M)]:
        x = g.lag_min; row = f"| {k} | {len(g)} | {x.median():.0f} min | {(x > 0).mean():.0%} | {((x >= 0) & (x <= 2)).sum()} | {((x > 2) & (x <= 10)).sum()} | {((x > 10) & (x <= 30)).sum()} | {(x > 30).sum()} | {(x < 0).sum()} |"; L.append(row); print("  " + row)
    for r in M.sort_values("sec_time").tail(6).itertuples(): print(f"      {r.ticker} wire {r.wire_time:%Y-%m-%d %H:%M} | SEC {r.sec_time:%H:%M:%S} | {r.title[:70]}")
    Path("docs/wire_lag.md").write_text("\n".join(L) + "\n"); print("-> docs/wire_lag.md")


def rerun():
    """The same fixed cells from the two clocks, on the SAME matched releases with stock prices (May 2018 on): entry counted from the wire time, and
    from the SEC stamp. No search; a description of what the earlier clock is worth."""
    import numpy as np
    from src.ai_chain_test import load_book, entry, ret, _stat, LAST
    M, _ = matched(); M = M[M.sec_time >= "2018-05-01"].reset_index(drop=True); need = {}
    for r in M.itertuples(): need.setdefault(r.ticker, set()).update([r.sec_time.normalize(), r.wire_time.normalize()])
    B = load_book(need); L = ["# W1: the results rule from the wire time and from the SEC stamp (same releases)", "", f"{len(M)} matched results releases of {', '.join(sorted(set(M.ticker)))} from May 2018. Trade = sign(score) x own-stock return, before cost; cells fixed in advance (TRACK 3.65).", "", "| score | enter after | hold | from the WIRE time | from the SEC stamp |", "|---|---|---|---|---|"]; out = {}
    for sig, k, x in CELLS:
        cell = []
        for col in ("wire_time", "sec_time"):
            v = np.array([np.sign(float(getattr(r, sig) or 0)) * ret(B, r.ticker, entry(B, r.ticker, getattr(r, col).normalize(), int(getattr(r, col).hour * 60 + getattr(r, col).minute), "ext", k), x, LAST["stock"]) if float(getattr(r, sig) or 0) != 0 else np.nan for r in M.itertuples()], float)
            st = _stat(v); cell.append(f"{st['mean']:+.1f} bp, t {st['t']:+.2f}, right on {st['hit']:.0%} of {st['n']}" if np.isfinite(st["mean"]) else f"n {st['n']} (under 30)"); out[(sig, k, x, col)] = st
        L.append(f"| {sig} | {k} min | {x} min | {cell[0]} | {cell[1]} |"); print(f"  {sig:10} enter {k:2} min, hold {x}: wire {cell[0]}  ||  SEC {cell[1]}")
    Path("docs/wire_rerun.md").write_text("\n".join(L) + "\n"); print("-> docs/wire_rerun.md")


# ------------------------------------------------------------------------------------------------ probe 2: the other eight companies
# Founder, 17 Nov: "why are we not continuing to find ways to find the remaining companies". Two further routes were confirmed by hand for ONE release
# (Intel, 29 Oct 2026, 4:01 PM EDT): the company's own press-release page, and a public mirror of the wire that prints "Published at ... via Business
# Wire". probe2 checks from this machine which of these routes answer for each company and whether their pages print clock times. Read-only.
P2 = [("INTC", "own site: one release (known to print the time)", "https://www.intc.com/news-events/press-releases/detail/1786/intel-reports-third-quarter-2026-financial-results"),
      ("INTC", "own site: list of releases", "https://www.intc.com/news-events/press-releases"), ("INTC", "own site: list, page 2", "https://www.intc.com/news-events/press-releases?page=2"),
      ("AMD", "own site: list of releases", "https://ir.amd.com/news-events/press-releases"), ("AMD", "own site: list, page 2", "https://ir.amd.com/news-events/press-releases?page=2"),
      ("NVDA", "own site: list of releases", "https://investor.nvidia.com/investors/news/default.aspx"), ("NVDA", "newsroom: list", "https://nvidianews.nvidia.com/news/latest"),
      ("MU", "own site: list of releases", "https://investors.micron.com/news-releases"), ("AMZN", "own site: list of releases", "https://ir.aboutamazon.com/news-releases/default.aspx"),
      ("CRWD", "own site: list of releases", "https://ir.crowdstrike.com/news-releases"), ("SNDK", "own site: list of releases", "https://investor.sandisk.com/news-events/press-releases"),
      ("GOOG", "own site: earnings page", "https://abc.xyz/investor/earnings/"), ("TSM", "own site: list", "https://pr.tsmc.com/english/latest-news"),
      ("mirror", "wire mirror: the Intel release (known to print 'Published at ... via Business Wire')", "https://www.financialcontent.com/article/bizwire-2026-10-29-intel-reports-third-quarter-2026-financial-results"),
      ("mirror", "wire mirror: news list for INTC", "https://www.financialcontent.com/quote/news?Symbol=INTC"), ("mirror", "wire mirror: news list for NVDA", "https://www.financialcontent.com/quote/news?Symbol=NVDA"),
      ("mirror", "wire mirror: news list for INTC (markets address)", "https://markets.financialcontent.com/stocks/quote/news?Symbol=INTC"),
      ("mirror", "second mirror: an NVIDIA results release", "https://finviz.com/news/385939/nvidia-announces-financial-results-for-second-quarter-fiscal-2027")]
RX_CLOCK = r"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm|a\.m\.|p\.m\.)?\s?(?:E[SD]?T|Eastern)\b"


def probe2():
    L = ["# Probe 2: release times for the companies PR Newswire does not hold", "", "| company | route | answer | clock times printed | example | links to single releases |", "|---|---|---|---|---|---|"]
    for tk, what, url in P2:
        try: status, html = get(url)
        except urllib.error.HTTPError as e: print(f"  {tk:6} {what[:58]:58} HTTP {e.code} (refused)"); L.append(f"| {tk} | {what} | HTTP {e.code} | | | |"); time.sleep(0.5); continue
        except Exception as e: print(f"  {tk:6} {what[:58]:58} no answer: {type(e).__name__}: {str(e)[:50]}"); L.append(f"| {tk} | {what} | no answer ({type(e).__name__}) | | | |"); time.sleep(0.5); continue
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S))); hits = [m for m in re.finditer(RX_CLOCK, text)]
        ex = text[max(0, hits[0].start() - 45):hits[0].end() + 5].strip() if hits else ""; links = len(set(re.findall(r'href="([^"]*(?:press-releases/detail|news-release-details|press-release-details|/article/(?:bizwire|gnwcq|prnews|globenewswire)|/news/\d+/)[^"]*)"', html)))
        blocked = bool(re.search(r"access denied|captcha|are you a robot|request unsuccessful|enable javascript|just a moment", text[:3000], re.I))
        print(f"  {tk:6} {what[:58]:58} HTTP {status}, {len(html) // 1000} KB{', looks BLOCKED' if blocked else ''}; {len(hits)} clock times; {links} release links" + (f" | e.g. …{ex}" if ex else "")); L.append(f"| {tk} | {what} | HTTP {status}, {len(html) // 1000} KB{', looks blocked' if blocked else ''} | {len(hits)} | {ex.replace('|', '/')} | {links} |"); time.sleep(0.6)
    Path("docs").mkdir(exist_ok=True); Path("docs/wire_history_probe2.md").write_text("\n".join(L) + "\n"); print("-> docs/wire_history_probe2.md")


if __name__ == "__main__":
    import sys
    {"probe": probe, "probe2": probe2, "collect": collect, "collect_own": collect_own, "collect_mirror": lambda: collect_mirror(int(sys.argv[2]) if len(sys.argv) > 2 else None), "lag": lag, "rerun": rerun}[sys.argv[1] if len(sys.argv) > 1 else "probe"]()
