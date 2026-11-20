"""source_probe.py -- stage A of tests SR-1 / SR-2 / SR-3 (TRACK 3.74): where can dated lists of past short reports, public calls and media items be
read from this machine, and how far back do they go? Read-only: fetches each address, prints what it finds, writes docs/source_probe.md. No cost, no key.

Every address below is a CANDIDATE (Claude's best knowledge of where each publisher keeps its reports); the probe shows which are real.

    python -m src.source_probe
"""
from __future__ import annotations
import json, re, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from src.news_listener import feed_items, UA

PUBLISHERS = [      # (name, kind, address). kind: wp = a site whose feed pages back with ?paged=N; substack = a newsletter with a list API; feed = a plain feed
    ("Hunterbrook", "substack", "https://newsletter.hntrbrk.com"), ("Hindenburg Research (archive)", "wp", "https://hindenburgresearch.com/feed/"), ("Muddy Waters", "wp", "https://www.muddywatersresearch.com/feed/"),
    ("Citron Research", "wp", "https://citronresearch.com/feed/"), ("Spruce Point", "feed", "https://www.sprucepointcap.com/research?format=rss"), ("Kerrisdale", "wp", "https://www.kerrisdalecap.com/feed/"),
    ("Grizzly Research", "wp", "https://grizzlyreports.com/feed/"), ("Viceroy Research", "wp", "https://viceroyresearch.org/feed/"), ("Blue Orca", "wp", "https://www.blueorcacapital.com/feed/"),
    ("Wolfpack Research", "feed", "https://www.wolfpackresearch.com/items?format=rss"), ("Fuzzy Panda", "wp", "https://fuzzypandaresearch.com/feed/"), ("Culper Research", "wp", "https://culperresearch.com/feed/"),
    ("Gotham City Research", "feed", "https://www.gothamcityresearch.com/main?format=rss"), ("Iceberg Research", "wp", "https://iceberg-research.com/feed/"), ("Jehoshaphat Research", "wp", "https://jehoshaphatresearch.com/feed/"),
    ("Scorpion Capital", "wp", "https://scorpioncapital.com/feed/"), ("J Capital Research", "wp", "https://www.jcapitalresearch.com/feed/"), ("Michael Burry's newsletter", "substack", "https://michaeljburry.substack.com"),
    ("SemiAnalysis", "wp", "https://semianalysis.com/feed/")]
GNEWS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
SEARCHES = [("public call, now", '"Michael Burry" short'), ("public call, one past month", '"Michael Burry" short after:2025-11-01 before:2025-12-01'), ("public call, an older month", '"Michael Burry" short after:2023-08-01 before:2023-09-01'),
            ("short report, one past month", '"short report" Hindenburg after:2024-06-01 before:2024-07-01'), ("media by publisher, now", "AMD site:reuters.com when:7d"), ("media by publisher, now", "Nvidia site:cnbc.com when:7d"),
            ("media by publisher, now", "AMD site:bloomberg.com when:7d"), ("media by publisher, now", "Nvidia site:seekingalpha.com when:7d"), ("media by publisher, one past month", "Nvidia site:reuters.com after:2025-05-01 before:2025-06-01")]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"}), timeout=25).read(4_000_000)


def _span(items):
    d = sorted(i["published"] for i in items if i.get("published")); return (f"{d[0]:%Y-%m-%d} -> {d[-1]:%Y-%m-%d}" if d else "no dates")


def main():
    L = ["# Source probe: dated lists of short reports, public calls and media items", "", "## Publishers' own lists", "", "| publisher | answer | items on the first page | dates | older pages | examples |", "|---|---|---|---|---|---|"]
    for name, kind, url in PUBLISHERS:
        try:
            if kind == "substack":
                rows = []; off = 0
                while off < 600:
                    page = json.loads(get(f"{url}/api/v1/archive?sort=new&offset={off}&limit=50")); rows += page; off += 50; time.sleep(0.4)
                    if len(page) < 50: break
                dates = sorted(str(r.get("post_date", ""))[:10] for r in rows if r.get("post_date")); ex = "; ".join(str(r.get("title", ""))[:60] for r in rows[:2])
                print(f"  {name[:30]:30} list API answers: {len(rows)} posts, {dates[0] if dates else '?'} -> {dates[-1] if dates else '?'} | {ex}"); L.append(f"| {name} | list API | {len(rows)} in all | {dates[0] if dates else '?'} -> {dates[-1] if dates else '?'} | whole history | {ex} |"); continue
            it = feed_items(get(url)); time.sleep(0.4); older = ""
            if kind == "wp" and it:
                for pg in (2, 10, 40):
                    try: more = feed_items(get(url + ("&" if "?" in url else "?") + f"paged={pg}")); older += f"page {pg}: {len(more)} items, {_span(more)}; " if more and more[0]["id"] != it[0]["id"] else f"page {pg}: same as page 1; "
                    except Exception as e: older += f"page {pg}: {type(e).__name__}; "; break
                    time.sleep(0.4)
            ex = "; ".join(i["title"][:60] for i in it[:2]); print(f"  {name[:30]:30} feed answers: {len(it)} items, {_span(it)} | {older}| {ex}"); L.append(f"| {name} | feed | {len(it)} | {_span(it)} | {older} | {ex} |")
        except urllib.error.HTTPError as e: print(f"  {name[:30]:30} HTTP {e.code}"); L.append(f"| {name} | HTTP {e.code} | | | | |")
        except Exception as e: print(f"  {name[:30]:30} no answer: {type(e).__name__}: {str(e)[:50]}"); L.append(f"| {name} | no answer ({type(e).__name__}) | | | | |")
        time.sleep(0.3)
    L += ["", "## Google News search feed (free, no key)", "", "| what | search | answer | items | dates | publishers seen | examples |", "|---|---|---|---|---|---|---|"]
    for what, q in SEARCHES:
        try:
            body = get(GNEWS.format(q=urllib.parse.quote(q))); it = feed_items(body); srcs = re.findall(r"<source[^>]*>([^<]+)</source>", body.decode("utf-8", "ignore")); top = ", ".join(f"{k} {v}" for k, v in sorted({s: srcs.count(s) for s in set(srcs)}.items(), key=lambda kv: -kv[1])[:5])
            ex = "; ".join(i["title"][:70] for i in it[:2]); print(f"  search [{what}] {q[:58]:58} {len(it)} items, {_span(it)} | {top} | {ex}"); L.append(f"| {what} | `{q}` | feed | {len(it)} | {_span(it)} | {top} | {ex} |")
        except Exception as e: print(f"  search [{what}] {q[:58]:58} no answer: {type(e).__name__}: {str(e)[:50]}"); L.append(f"| {what} | `{q}` | no answer ({type(e).__name__}) | | | | |")
        time.sleep(1.0)
    Path("docs").mkdir(exist_ok=True); Path("docs/source_probe.md").write_text("\n".join(L) + "\n"); print("-> docs/source_probe.md")


if __name__ == "__main__": main()
