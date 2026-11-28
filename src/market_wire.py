"""market_wire.py -- market-wide headlines during the session: the kind of source the engine did not have on 25 Nov 2026 (TRACK 3.124, 3.125).

The engine reads official documents and company filings. It had nothing for news that moves ALL markets at once inside the day: a Fed official speaking,
the result of a Treasury auction, a White House or trade-office statement, a document filed for tomorrow's Federal Register (tariff proclamations show there first).

Step 1 (this file, now):   python -m src.market_wire probe      # free; asks every candidate address once and reports which ones answer -> docs/market_wire_probe.md
Step 2 (after the probe):  the addresses that answer are admitted and the listener collects them (time, source, headline, link) into data_provenance/live/market_wire.jsonl.
Collecting costs nothing: no headline is sent to a paid model. Reading them with Claude is a separate, later decision (it needs Anthropic credit).

Rights. Works of the US federal government are not under copyright in the United States, so their headlines may be collected and shown in a commercial product
(Claude is not a lawyer; the rule is 17 U.S.C. 105). Central banks outside the US have their own re-use terms: probed here, admitted only after their terms are read.
News agencies (Reuters, Bloomberg, Dow Jones) are licensed and are NOT candidates.
"""
from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York"); DOCS = Path("docs")
US = "US federal government work: no copyright in the US"; CHECK = "own re-use terms: to be read before it is admitted"
CANDIDATES = [
    dict(name="Federal Reserve: all press releases", owner="Federal Reserve Board", fmt="feed", rights=US, url="https://www.federalreserve.gov/feeds/press_all.xml"),
    dict(name="Federal Reserve: speeches", owner="Federal Reserve Board", fmt="feed", rights=US, url="https://www.federalreserve.gov/feeds/speeches.xml"),
    dict(name="Federal Reserve: testimony", owner="Federal Reserve Board", fmt="feed", rights=US, url="https://www.federalreserve.gov/feeds/testimony.xml"),
    dict(name="New York Fed: speeches", owner="Federal Reserve Bank of New York", fmt="feed", rights=CHECK, url="https://www.newyorkfed.org/rss/feeds/speeches"),
    dict(name="Treasury: auction results", owner="US Treasury (TreasuryDirect)", fmt="auctions", rights=US, url="https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&days=10"),
    dict(name="Treasury: press releases", owner="US Treasury", fmt="feed", rights=US, url="https://home.treasury.gov/news/press-releases/feed"),
    dict(name="White House: presidential actions", owner="The White House", fmt="feed", rights=US, url="https://www.whitehouse.gov/presidential-actions/feed/"),
    dict(name="White House: briefings and statements", owner="The White House", fmt="feed", rights=US, url="https://www.whitehouse.gov/briefings-statements/feed/"),
    dict(name="Federal Register: documents filed for the next issues", owner="Office of the Federal Register", fmt="fedreg", rights=US, url="https://www.federalregister.gov/api/v1/public-inspection-documents/current.json"),
    dict(name="US Trade Representative: press releases", owner="USTR", fmt="feed", rights=US, url="https://ustr.gov/rss.xml"),
    dict(name="Commerce Department: news", owner="US Department of Commerce", fmt="feed", rights=US, url="https://www.commerce.gov/feeds/news"),
    dict(name="SEC: press releases", owner="US Securities and Exchange Commission", fmt="feed", rights=US, url="https://www.sec.gov/news/pressreleases.rss"),
    dict(name="Bureau of Economic Analysis: releases", owner="BEA", fmt="feed", rights=US, url="https://apps.bea.gov/rss/rss.xml"),
    dict(name="Bureau of Labor Statistics: latest numbers", owner="BLS", fmt="feed", rights=US, url="https://www.bls.gov/feed/bls_latest.rss"),
    dict(name="Energy Information Administration: press", owner="EIA", fmt="feed", rights=US, url="https://www.eia.gov/rss/press_rss.xml"),
    dict(name="European Central Bank: press", owner="ECB", fmt="feed", rights=CHECK, url="https://www.ecb.europa.eu/rss/press.html"),
    dict(name="Bank of England: news", owner="Bank of England", fmt="feed", rights=CHECK, url="https://www.bankofengland.co.uk/rss/news"),
    dict(name="SEC: new debt filed by a watched company", owner="US Securities and Exchange Commission (EDGAR)", fmt="secdebt", rights=US, url="https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form}&company=&dateb=&owner=include&count=100&output=atom"),
    dict(name="Treasury: auction results, Fiscal Data copy (lag measurement)", owner="US Treasury (Fiscal Data)", fmt="fiscal", rights=US, url="https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?format=json&sort=-auction_date&page%5Bsize%5D=60&filter=auction_date:gte:{since}"),
    dict(name="Bank of Japan: what's new", owner="Bank of Japan", fmt="feed", rights=CHECK, url="https://www.boj.or.jp/en/rss/whatsnew.xml"),
]


# Admitted 26 Nov 2026 after the probe (docs/market_wire_probe.md, TRACK 3.126): they answer, give a time of day, and are US federal government works.
ADMITTED = ["Federal Reserve: all press releases", "Federal Reserve: speeches", "Federal Reserve: testimony", "Treasury: auction results", "White House: presidential actions", "White House: briefings and statements",
            "Federal Register: documents filed for the next issues", "US Trade Representative: press releases", "SEC: press releases", "Bureau of Economic Analysis: releases", "Energy Information Administration: press", "SEC: new debt filed by a watched company",
            "Treasury: auction results, Fiscal Data copy (lag measurement)"]      # 28 Nov 2026 (TRACK 3.146): collected NEXT TO the TreasuryDirect source, only to measure how much later it shows a result
# Founder's YES of 26 Nov 2026 (TRACK 3.142): the minute a watched company files for new debt (prospectus and pricing forms for notes), the listener says so -- INFORMATION ONLY.
# No rule has passed a test on it (DN-1 to DN-3, TRACK 3.138-3.140): it is not scored, not coloured, not a signal.
DEBT_FORMS = ["424B5", "424B2", "424B3", "FWP"]; DEBT_WATCH = ["ORCL", "META", "GOOGL", "GOOG", "AMZN", "MSFT", "CRWV", "NVDA", "AVGO", "AMD", "INTC", "MU", "IBM", "CSCO", "AAPL", "DELL", "QCOM", "TXN"]; _cik: dict = {}
LIVE = Path("data_provenance/live"); OUT = LIVE / "market_wire.jsonl"; STATE = LIVE / "market_wire_seen.json"; EVERY = 60.0; SLOW = {"Federal Register: documents filed for the next issues": 180.0}
_last: dict = {}


def collect(quiet=False) -> int:
    """called by the listener on every pass; asks each admitted source at most once a minute (the Federal Register list every three minutes) and stores what is new:
    source, headline, link, the minute the source gives, the minute we saw it. No headline is sent to a paid model. Returns the number of new live items."""
    st = json.loads(STATE.read_text()) if STATE.exists() else dict(ids=[], warmed=[]); seen = set(st["ids"]); warmed = set(st["warmed"]); new = 0; rows = []; now = datetime.now(timezone.utc)
    for c in CANDIDATES:
        if c["name"] not in ADMITTED or time.time() - _last.get(c["name"], 0) < SLOW.get(c["name"], EVERY): continue
        _last[c["name"]] = time.time()
        try: I = items(c)
        except SystemExit: raise
        except Exception: continue
        first = c["name"] not in warmed
        for it in I:
            uid = f"{c['name']}|{it['id']}"
            if uid in seen: continue
            seen.add(uid); pub = it.get("published")
            rows.append(dict(source=c["name"], owner=c["owner"], title=it["title"][:400], link=it.get("link", ""), published=pub.astimezone(timezone.utc).isoformat() if pub else None, seen=now.isoformat(), first_pass=first))
            if not first:
                new += 1
                if not quiet: print(f"   [market] {(pub or now).astimezone(NY):%H:%M} New York | {c['name']} | {it['title'][:110]}")
        if first:
            warmed.add(c["name"])
            if not quiet: print(f"   .. market-wide source connected: {c['name']} ({len(I)} existing items stored with their own times)")
    if rows:
        LIVE.mkdir(parents=True, exist_ok=True)
        with OUT.open("a") as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if rows or not STATE.exists(): st = dict(ids=sorted(seen)[-60000:], warmed=sorted(warmed)); tmp = STATE.with_suffix(".tmp"); tmp.write_text(json.dumps(st)); tmp.replace(STATE)
    return new


def _t(raw):
    if not raw: return None
    try: t = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception: return None
    return t if t.tzinfo else t.replace(tzinfo=NY)      # the Treasury and the Federal Register give New York clock time without a zone


def items(c: dict) -> list:
    """the items of one candidate as dicts: id, title, link, published (a time with zone, or None)"""
    from src import news_listener as N
    if c["fmt"] == "secdebt":
        import re
        if not _cik:
            for v in json.loads(N.fetch("https://www.sec.gov/files/company_tickers.json")).values():
                if v["ticker"].upper() in DEBT_WATCH: _cik[str(v["cik_str"]).zfill(10)] = "GOOG" if v["ticker"].upper() == "GOOGL" else v["ticker"].upper()
        out = []
        for form in DEBT_FORMS:
            for it in N.feed_items(N.fetch(c["url"].format(form=form))):
                m = re.search(r"/data/(\d+)/", it.get("link", "")); a = re.search(r"(\d{10})-?(\d{2})-?(\d{6})", it.get("link", "").split("/data/")[-1])
                if not m or not a or it.get("published") is None: continue
                tick = _cik.get(m.group(1).zfill(10))
                if tick is None or it["title"].split(" - ")[0].strip().upper() != form: continue
                out.append(dict(id=f"{a.group(1)}-{a.group(2)}-{a.group(3)}", title=f"NEW DEBT FILED -- {tick} (form {form}). Information only: no tested rule.", link=it.get("link", ""), published=it["published"], summary=""))
        return out
    if c["fmt"] == "fiscal":
        from datetime import timedelta
        J = json.loads(N.fetch(c["url"].format(since=(datetime.now(NY) - timedelta(days=10)).strftime("%Y-%m-%d")), timeout=40)); out = []
        for a in J.get("data", []):
            y = next((v for k, v in a.items() if k.startswith("high_") and ("yield" in k or "rate" in k) and v not in (None, "", "null")), "")
            if not y: continue      # announced, not yet auctioned
            out.append(dict(id=f"{a.get('cusip')}|{str(a.get('auction_date'))[:10]}", title=f"Auction result: {a.get('security_term', '')} {a.get('security_type', '')} -- high yield/rate {y}, bid-to-cover {a.get('bid_to_cover_ratio', '')}", link="https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/", published=None, summary=""))
        return out
    body = N.fetch(c["url"])
    if c["fmt"] == "feed": return N.feed_items(body)
    J = json.loads(body); out = []
    if c["fmt"] == "auctions":
        for a in J:
            y = a.get("highYield") or a.get("highDiscountRate") or a.get("highInvestmentRate") or ""; btc = a.get("bidToCoverRatio") or ""
            if not y: continue      # announced, not yet auctioned
            out.append(dict(id=f"{a.get('cusip')}|{a.get('auctionDate')}", title=f"Auction result: {a.get('securityTerm', '')} {a.get('securityType', '')} -- high yield/rate {y}, bid-to-cover {btc}", link="https://www.treasurydirect.gov/auctions/auction-query/", published=_t(a.get("updatedTimestamp") or a.get("auctionDate")), summary=""))
    elif c["fmt"] == "fedreg":
        for d in J.get("results", []):
            ag = ", ".join(x.get("name") or x.get("raw_name") or "" for x in (d.get("agencies") or []))[:80]
            out.append(dict(id=str(d.get("document_number")), title=f"{d.get('title') or d.get('toc_doc') or ''} [{ag}]", link=d.get("html_url") or d.get("pdf_url") or "", published=_t(d.get("filed_at")), summary=""))
    return out


def cmd_probe():
    now = datetime.now(timezone.utc); rows = []
    print(f"Asking {len(CANDIDATES)} candidate addresses once each. Free; nothing is sent to a paid model; no file of the engine is changed.")
    for c in CANDIDATES:
        try:
            I = items(c); ts = sorted(x["published"] for x in I if x.get("published")); newest = ts[-1] if ts else None
            clock = sum(1 for t in ts if (t.hour, t.minute, t.second) != (0, 0, 0)); day = sum(1 for t in ts if (now - t).total_seconds() < 86400 * 7)
            rows.append(dict(c, ok=bool(I), n=len(I), newest=newest, clock=clock, timed=len(ts), week=day, sample=(max(I, key=lambda x: x["published"] or datetime(1970, 1, 1, tzinfo=timezone.utc))["title"] if I else "")[:110], why="" if I else "answers, but no items"))
        except SystemExit as ex: rows.append(dict(c, ok=False, n=0, newest=None, clock=0, timed=0, week=0, sample="", why=str(ex)[:80]))
        except Exception as ex: rows.append(dict(c, ok=False, n=0, newest=None, clock=0, timed=0, week=0, sample="", why=f"{type(ex).__name__}: {str(ex)[:70]}"))
        r = rows[-1]; print(f"  {'ANSWERS' if r['ok'] else 'NO     '} | {r['name']} | " + (f"{r['n']} items, {r['week']} in the last 7 days, newest {r['newest'].astimezone(NY):%d %b %H:%M} New York, time of day given on {r['clock']} of {r['timed']} | {r['sample']}" if r["ok"] and r["newest"] else (f"{r['n']} items, no dates" if r["ok"] else r["why"])))
    good = [r for r in rows if r["ok"]]; usable = [r for r in good if r["rights"] == US and r["clock"] >= max(1, r["timed"] // 2)]
    L = ["# Market-wide headline sources: the probe", "", f"Asked once each on {now.astimezone(NY):%Y-%m-%d %H:%M} New York time (TRACK 3.125). 'Time of day given' matters: a source that only gives the date cannot place a headline at 11:00.", "",
         "| source | owner | answers | items | in the last 7 days | newest (New York) | items with a time of day | rights | example or reason |", "|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {r['name']} | {r['owner']} | {'yes' if r['ok'] else 'NO'} | {r['n']} | {r['week']} | {r['newest'].astimezone(NY).strftime('%d %b %H:%M') if r['newest'] else ''} | {r['clock']} of {r['timed']} | {r['rights']} | {(r['sample'] or r['why']).replace('|', '/')} |" for r in rows]
    L += ["", f"**{len(good)} of {len(rows)} answer. {len(usable)} are usable now** (answer, give the time of day on at least half of their items, and are US federal government works): " + (", ".join(r["name"] for r in usable) or "none") + ".",
          "Not candidates: news agencies (Reuters, Bloomberg, Dow Jones) -- licensed. Central banks outside the US: admitted only after their re-use terms are read."]
    DOCS.mkdir(exist_ok=True); (DOCS / "market_wire_probe.md").write_text("\n".join(L) + "\n")
    print(f"=> {len(good)} of {len(rows)} answer; {len(usable)} usable now: " + (", ".join(r["name"] for r in usable) or "none") + ". -> docs/market_wire_probe.md")


def cmd_lag():
    """how much later the Fiscal Data copy shows an auction result than TreasuryDirect: for every result both sources showed LIVE (not on first connection), the minute each was first seen"""
    if not OUT.exists(): print(f"{OUT} is missing: the listener has not collected anything yet"); return
    TD = "Treasury: auction results"; FD = "Treasury: auction results, Fiscal Data copy (lag measurement)"; seen = {TD: {}, FD: {}}; first = {TD: 0, FD: 0}
    for ln in OUT.read_text().splitlines():
        try: d = json.loads(ln)
        except Exception: continue
        if d.get("source") not in seen: continue
        if d.get("first_pass"): first[d["source"]] += 1; continue
        seen[d["source"]].setdefault(d["title"].split(" -- ")[0], []).append(datetime.fromisoformat(d["seen"]))      # by the name of the security ('13-Week Bill'); the same name comes back every week or month
    from datetime import timedelta
    pairs = []; only_td = []
    for name, ts in seen[TD].items():
        ts = sorted(ts); fs = sorted(seen[FD].get(name, []))
        for n, t in enumerate(ts):
            nxt = ts[n + 1] if n + 1 < len(ts) else None; f = next((x for x in fs if x >= t - timedelta(minutes=10) and (nxt is None or x < nxt - timedelta(minutes=10))), None)      # the first Fiscal Data sighting of that security before its next auction
            (pairs.append((t, name, f)) if f else only_td.append((t, name)))
    pairs.sort(); only_td.sort(); lags = [(f - t).total_seconds() / 60 for t, _, f in pairs]; nTD = sum(len(v) for v in seen[TD].values()); nFD = sum(len(v) for v in seen[FD].values())
    L = ["# How much later Fiscal Data shows an auction result than TreasuryDirect", "", "Both sources are asked once a minute by the listener (TRACK 3.146). A row = one auction result that both showed while the listener was running. "
         "'Seen' = the minute our listener first saw it (New York time), so each time is exact to about one minute. Results that were already there when a source was first connected are left out.", "",
         "| auction result | TreasuryDirect: seen | Fiscal Data: seen | Fiscal Data later by, minutes |", "|---|---|---|---|"]
    for (t, name, f), g in zip(pairs, lags): L.append(f"| {name} | {t.astimezone(NY):%Y-%m-%d %H:%M} | {f.astimezone(NY):%Y-%m-%d %H:%M} | {g:.0f} |")
    L += ["", f"Results seen live: TreasuryDirect {nTD}, Fiscal Data {nFD}, on both {len(pairs)}. On TreasuryDirect and not yet on Fiscal Data: {len(only_td)}" + (" (" + "; ".join(f"{n}, seen {t.astimezone(NY):%d %b %H:%M}" for t, n in only_td[:6]) + ")" if only_td else "") + "."]
    if lags:
        z = sorted(lags); L.append(f"**Fiscal Data later by: smallest {z[0]:.0f}, middle {z[len(z) // 2]:.0f}, largest {z[-1]:.0f} minutes ({len(z)} results).**")
    else: L.append("**No result has been seen live on both sources yet. Auctions of bills are held on most Mondays to Thursdays at 11:30 New York; run this again after the listener has been on through one.**")
    DOCS.mkdir(exist_ok=True); (DOCS / "treasury_lag.md").write_text("\n".join(L) + "\n")
    print(f"  results seen live: TreasuryDirect {nTD}, Fiscal Data {nFD}, on both {len(pairs)} (stored on first connection and not counted: {first[TD]} and {first[FD]})")
    for (t, name, f), g in zip(pairs, lags): print(f"    Fiscal Data later by {g:.0f} minutes | {name} | TreasuryDirect {t.astimezone(NY):%d %b %H:%M} New York")
    for t, name in only_td[:8]: print(f"    on TreasuryDirect, not yet on Fiscal Data | {name} | seen {t.astimezone(NY):%d %b %H:%M} New York")
    print(L[-1].replace("**", "") + " -> docs/treasury_lag.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["probe", "once", "lag"]); a = ap.parse_args()
    if a.cmd == "probe": cmd_probe()
    elif a.cmd == "lag": cmd_lag()
    else: print(f"{collect()} new live items -> {OUT}")
