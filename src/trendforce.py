"""trendforce.py -- TrendForce (market-research firm: memory, foundry, servers, displays) as a research source. Founder, 22 Nov 2026: its release of
19 Nov 2026 says NAND Flash prices are set to fall in 2027, which can move the memory stocks of our list; add it to the research-report test.

Step 1 (this file, free): collect the list of its press releases in 'Semiconductors' from its own press centre -- date, title, address -- and count
them. The releases carry a DATE only (no time of day) and often name NO company (the NAND release names none), so the test needs a mapping from the
subject of a release to the stocks it touches. The test itself is registered only after these counts are seen.

    python -m src.trendforce collect            # about 5 minutes, no cost -> data_provenance/trendforce/releases.csv, docs/trendforce_releases.md
    python -m src.trendforce collect --pages 3  # a quick try
"""
from __future__ import annotations
import argparse, html, re, time
from pathlib import Path
import pandas as pd

ROOT = Path("data_provenance/trendforce"); DOCS = Path("docs"); BASE = "https://www.trendforce.com"; LIST = BASE + "/presscenter/news/Semiconductors?page={}"; FEED = BASE + "/feed/Semiconductors.html"
LINK = re.compile(r'<a[^>]+href="(?:https?://www\.trendforce\.com)?/presscenter/news/(\d{8})-(\d+)\.html"[^>]*>(.*?)</a>', re.S | re.I)
SUBJECTS = {"NAND / flash / SSD": r"\bnand\b|flash|\bssd\b", "DRAM / HBM / memory": r"\bdram\b|\bhbm\b|memory", "foundry / wafers": r"foundry|wafer|\btsmc\b|\b\dnm\b", "AI servers / chips": r"\bai\b|server|\bgpu\b|\basic\b|nvidia", "prices up": r"\b(?:rise|rises|rising|increase|increases|surge|surges|hike|hikes|climb|climbs|up)\b",
            "prices down": r"\b(?:decline|declines|fall|falls|drop|drops|slide|weaken|weakens|downturn|cut|cuts|down)\b"}


def cmd_collect(pages: int | None):
    from src.news_listener import fetch, feed_items
    ROOT.mkdir(parents=True, exist_ok=True); f = ROOT / "releases.csv"; old = pd.read_csv(f, dtype=str) if f.exists() else pd.DataFrame(columns=["id", "date", "title", "url"]); seen = dict(zip(old.id, old.to_dict("records"))); new = 0; empty = 0; p = 0; last = None
    while True:
        p += 1
        if pages and p > pages: break
        try: body = fetch(LIST.format(p)).decode("utf-8", "ignore")
        except Exception as e: print(f"  page {p}: {type(e).__name__} {str(e)[:80]} -- stopped here; run again to continue"); break
        if last is None:
            m = re.search(r"([\d,]+)\s*results", body, re.I); last = int(m.group(1).replace(",", "")) if m else None
            if last: print(f"  the press centre says: {last} releases in Semiconductors")
        got = {}
        for d, n, t in LINK.findall(body):
            t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip(); k = f"{d}-{n}"
            if len(t) > len(got.get(k, {}).get("title", "")) or k not in got: got[k] = dict(id=k, date=f"{d[:4]}-{d[4:6]}-{d[6:]}", title=t, url=f"{BASE}/presscenter/news/{k}.html")
        fresh = [k for k in got if k not in seen or (not seen[k].get("title") and got[k]["title"])]
        for k in got:
            if k not in seen or len(got[k]["title"]) > len(str(seen[k].get("title") or "")): seen[k] = got[k]
        new += len(fresh); empty = empty + 1 if not got else 0
        if p % 25 == 0: print(f"  page {p}: {len(seen)} releases so far"); pd.DataFrame(seen.values()).to_csv(f, index=False)
        if empty >= 2 or (len(old) and not fresh and p >= 3 and not pages): break      # past the end, or everything from here on is already on disk
        time.sleep(0.6)
    R = pd.DataFrame(seen.values()).sort_values("date", ascending=False) if seen else old; R.to_csv(f, index=False)
    if not len(R): print("  nothing collected (the page layout may differ from what the code expects) -- tell Claude"); return
    R["year"] = R.date.str[:4]; T = R.title.fillna("").str.lower(); no_title = int((T.str.len() < 15).sum())
    L = ["# TrendForce press releases, Semiconductors (list only: date, title, address; nothing read, no price looked at)", "", f"{len(R)} releases, {R.date.min()} to {R.date.max()}; {new} new in this run. Dates only: the press centre shows no time of day. Titles under 15 characters (to be fetched from the release itself): {no_title}.", "",
         "| year | releases | " + " | ".join(SUBJECTS) + " |", "|---|---|" + "---|" * len(SUBJECTS)]
    for y, g in R.groupby("year", sort=False):
        t = g.title.fillna("").str.lower(); L.append(f"| {y} | {len(g)} | " + " | ".join(str(int(t.str.contains(rx, regex=True).sum())) for rx in SUBJECTS.values()) + " |")
    L += ["", "The subject columns are a rough word count in the titles, to size the test; they are not a reading.", "", "## The 15 newest", ""] + [f"- {r.date} — {r.title}" for r in R.head(15).itertuples()]
    DOCS.mkdir(exist_ok=True); (DOCS / "trendforce_releases.md").write_text("\n".join(L) + "\n")
    print(f"{len(R)} releases, {R.date.min()} to {R.date.max()} ({new} new now). In the titles: " + ", ".join(f"{k} {int(T.str.contains(rx, regex=True).sum())}" for k, rx in SUBJECTS.items()) + f". Titles missing: {no_title}.")
    print("  by year: " + ", ".join(f"{y} {len(g)}" for y, g in R.groupby("year", sort=False)))
    for r in R.head(5).itertuples(): print(f"  {r.date}  {r.title[:130]}")
    try: items = feed_items(fetch(FEED)); print(f"  live feed {FEED}: {len(items)} items read" + (f"; newest: {str(items[0].get('title', ''))[:90]}" if items else " (the feed did not parse -- tell Claude)"))
    except Exception as e: print(f"  live feed {FEED}: {type(e).__name__} {str(e)[:80]}")
    print("No cost. Nothing was read by Claude and no price was looked at. -> data_provenance/trendforce/releases.csv, docs/trendforce_releases.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["collect"]); ap.add_argument("--pages", type=int, default=None); a = ap.parse_args(); cmd_collect(a.pages)
