"""wire_probe.py -- step 0 for the live news listener and for the past release times: which public feeds and pages answer from THIS machine, how fresh
they are and how far back they go. Read-only: it fetches each address once, prints what it finds, writes docs/wire_probe.md. No cost, no key.

The addresses below are CANDIDATES (Claude's best knowledge of where each wire and each company publishes); the probe is what tells us which are real.

    python -m src.wire_probe
"""
from __future__ import annotations
import re, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
import os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
FEEDS = [      # (group, name, address)
    ("wire", "PR Newswire: all releases", "https://www.prnewswire.com/rss/news-releases-list.rss"),
    ("wire", "PR Newswire: earnings", "https://www.prnewswire.com/rss/financial-services-latest-news/earnings-list.rss"),
    ("wire", "Business Wire: earnings", "https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeEFpRWA=="),
    ("wire", "Business Wire: technology", "https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeGVtRXA=="),
    ("wire", "GlobeNewswire: public companies", "https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies"),
    ("wire", "GlobeNewswire: earnings releases", "https://www.globenewswire.com/RssFeed/subjectcode/13-Earnings%20Releases%20And%20Operating%20Results/feedTitle/GlobeNewswire%20-%20Earnings%20Releases%20And%20Operating%20Results"),
    ("regulator", "SEC: latest 8-K filings (backup)", "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&count=40&output=atom"),
    ("company", "NVDA newsroom", "https://nvidianews.nvidia.com/releases.xml"),
    ("company", "NVDA investor page", "https://investor.nvidia.com/rss/news-releases.xml"),
    ("company", "AMD investor page", "https://ir.amd.com/rss/news-releases.xml"),
    ("company", "MU investor page", "https://investors.micron.com/rss/news-releases.xml"),
    ("company", "INTC investor page", "https://www.intc.com/rss/news-releases.xml"),
    ("company", "AVGO investor page", "https://investors.broadcom.com/rss/news-releases.xml"),
    ("company", "SNDK investor page", "https://investor.sandisk.com/rss/news-releases.xml"),
    ("company", "ORCL investor page", "https://investor.oracle.com/rss/news-releases.xml"),
    ("company", "CRWD investor page", "https://ir.crowdstrike.com/rss/news-releases.xml"),
    ("company", "GOOG investor page (no feed known; page only)", "https://abc.xyz/investor/"),
    ("company", "META investor page", "https://investor.atmeta.com/rss/pressrelease.aspx"),
    ("company", "AMZN investor page", "https://ir.aboutamazon.com/rss/news-releases.xml"),
    ("company", "MSFT news", "https://news.microsoft.com/feed/"),
    ("company", "MSFT investor page (page only)", "https://www.microsoft.com/en-us/investor/earnings/press-releases"),
    ("company", "TSM newsroom (page only)", "https://pr.tsmc.com/english/latest-news"),
    ("company", "SKHY newsroom", "https://news.skhynix.com/feed/"),
    ("history", "GlobeNewswire: search NVIDIA (past releases with times?)", "https://www.globenewswire.com/search/organization/NVIDIA"),
    ("history", "PR Newswire: Meta company page (past releases with times?)", "https://www.prnewswire.com/news/meta/"),
    ("history", "Business Wire: search Intel (past releases with times?)", "https://www.businesswire.com/portal/site/home/search/?searchType=news&searchTerm=Intel%20Reports"),
]
TIME_RX = r"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?\s?(?:ET|EST|EDT|Eastern)\b"


def fetch(url):
    hdr = {"User-Agent": (os.environ.get("SEC_CONTACT") or UA) if "sec.gov" in url else UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html;q=0.8, */*;q=0.5"}
    t = time.time(); r = urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=25); body = r.read(3_000_000); return r.status, body, time.time() - t


def parse_feed(body: bytes):
    """-> list of (title, time) for an RSS or Atom feed, or None when the body is not a feed"""
    try: root = ET.fromstring(body)
    except ET.ParseError: return None
    strip = lambda tag: tag.split("}")[-1]; items = [e for e in root.iter() if strip(e.tag) in ("item", "entry")]
    if not items: return None
    out = []
    for it in items:
        d = {strip(c.tag): (c.text or "").strip() for c in it}; raw = d.get("pubDate") or d.get("updated") or d.get("published") or d.get("date") or ""; when = None
        try: when = parsedate_to_datetime(raw)
        except Exception:
            try:
                from datetime import datetime
                when = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except Exception: when = None
        if when is not None and when.tzinfo is None:
            from datetime import timezone
            when = when.replace(tzinfo=timezone.utc)      # a time without a zone is read as UTC, only so the items can be put in order
        out.append((d.get("title", "")[:90], when, raw))
    return out


def main():
    L = ["# Wire probe: which public news sources answer from this machine", "", "| group | source | answer | items | newest item (time as the feed gives it) | oldest item in the feed |", "|---|---|---|---|---|---|"]; good = []
    for group, name, url in FEEDS:
        try: status, body, secs = fetch(url)
        except urllib.error.HTTPError as e: print(f"  [{group:9}] {name[:52]:52} HTTP {e.code} (refused)"); L.append(f"| {group} | {name} | HTTP {e.code} | | | |"); continue
        except Exception as e: print(f"  [{group:9}] {name[:52]:52} no answer: {type(e).__name__}: {str(e)[:60]}"); L.append(f"| {group} | {name} | no answer ({type(e).__name__}) | | | |"); continue
        try: items = parse_feed(body)
        except Exception: items = None
        if items:
            dated = sorted([x for x in items if x[1] is not None], key=lambda x: x[1]); new = dated[-1] if dated else items[0]; old = dated[0] if dated else items[-1]
            print(f"  [{group:9}] {name[:52]:52} FEED, {len(items)} items, {secs:.1f}s | newest: {new[2][:31]} | {new[0][:60]} | oldest: {old[2][:31]}"); L.append(f"| {group} | {name} | feed, {secs:.1f}s | {len(items)} | {new[2][:31]}: {new[0][:70]} | {old[2][:31]} |"); good.append(name)
        else:
            text = body.decode("utf-8", "ignore"); times = re.findall(TIME_RX, text); blocked = bool(re.search(r"access denied|captcha|are you a robot|request unsuccessful|enable javascript", text[:20000], re.I))
            note = "page" + (", looks BLOCKED for scripts" if blocked else "") + f", {len(text) // 1000} KB, {len(times)} clock times with ET found" + (f" (e.g. {times[0]})" if times else "")
            print(f"  [{group:9}] {name[:52]:52} HTTP {status}, {note}"); L.append(f"| {group} | {name} | HTTP {status}; {note} | | | |")
        time.sleep(0.4)
    print(f"\n{len(good)} feeds answered: " + "; ".join(good)); Path("docs").mkdir(exist_ok=True); Path("docs/wire_probe.md").write_text("\n".join(L) + "\n"); print("-> docs/wire_probe.md")


if __name__ == "__main__": main()
