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
import argparse, json
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
    dict(name="Bank of Japan: what's new", owner="Bank of Japan", fmt="feed", rights=CHECK, url="https://www.boj.or.jp/en/rss/whatsnew.xml"),
]


def _t(raw):
    if not raw: return None
    try: t = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception: return None
    return t if t.tzinfo else t.replace(tzinfo=NY)      # the Treasury and the Federal Register give New York clock time without a zone


def items(c: dict) -> list:
    """the items of one candidate as dicts: id, title, link, published (a time with zone, or None)"""
    from src import news_listener as N
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["probe"]); ap.parse_args(); cmd_probe()
