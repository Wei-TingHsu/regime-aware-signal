"""missed_news.py -- the detector the founder asked for on 20 Nov and again on 28 Nov 2026 (TRACK 3.73, 3.74, 3.144, 3.145): find the news about the watched
companies that the listener did NOT record, and write it to docs/MISSED_NEWS.md by itself.

How it works, in three steps:
  1. ASK. For every watched company, ask the GDELT Project's free news index for the English-language articles of the last hours that name the company.
     (GDELT watches news sites all over the world and lists each article's headline, publisher, link and the time GDELT saw it.)
  2. GROUP. Headlines that share most of their words are one STORY. A story counts when at least MIN_PUBLISHERS different publishers carried it:
     one site writing something is noise, many sites writing the same thing is news.
  3. COMPARE. Every story is set against what the listener recorded for that company in the same hours. No listener item with the same words -> MISSED.

What it is NOT: it is not a signal, it scores nothing, it sends nothing to a paid model, and nothing of it is shown on the page. It fills a list for the founder.
Limits: GDELT gives the time IT saw an article (steps of 15 minutes), not the minute of publication; English only; the grouping is by words, so two headlines
about the same thing in different words can stay apart, and the listener's SEC items have no words in their titles ('8-K items 5.02'), so a story the listener
did have as a filing can still be listed -- the column 'what the listener had' shows what there was, for the founder to judge.

Why GDELT and not Google News or Gemini: Google News' terms allow personal, non-commercial display only and forbid robots (read 28 Nov 2026), so the plan of
20 Nov to use its search feed is dropped. Gemini needs a paid key. GDELT's terms: free 'for any academic, commercial, or governmental use', with credit.

    python -m src.missed_news run              # free; about 2 minutes (one question every 6 seconds, as GDELT asks); the last 30 hours
    python -m src.missed_news run --hours 72   # a longer look back (at most 72)
"""
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York"); MD = Path("docs/MISSED_NEWS.md"); LOG = Path("data_provenance/live/events.jsonl"); OUTDIR = Path("data_provenance/missed_news"); SEEN = OUTDIR / "seen.json"; FOUND = OUTDIR / "found.jsonl"
MIN_PUBLISHERS = 5      # chosen, not tested: a story needs this many different publishers
SHARE = 0.5             # chosen, not tested: a headline joins a story when at least this share of its words are the story's words (and at least 2 words)
NEAR_H = 36             # the listener's items of the company within this many hours of the story are compared with it
PAUSE = 6.0             # GDELT asks for at most one question every 5 seconds
API = "https://api.gdeltproject.org/api/v2/doc/doc?query={q}&mode=artlist&maxrecords=250&timespan={h}h&sort=datedesc&format=json"
# the words asked for, and the words a headline must hold to count as being ABOUT the company
ASK = {"NVDA": ["Nvidia"], "AMD": ["AMD"], "MU": ["Micron"], "INTC": ["Intel"], "AVGO": ["Broadcom"], "SNDK": ["SanDisk"], "SKHY": ["SK Hynix"], "ORCL": ["Oracle"], "TSM": ["TSMC"], "CRWD": ["CrowdStrike"],
       "GOOG": ["Alphabet", "Google"], "META": ["Meta Platforms", "Meta"], "AMZN": ["Amazon"], "MSFT": ["Microsoft"]}
STOP = set("""about after again against amid also and are been before being below between both but can could does down during each for from had has have her here his how into its just more most new not now off one only other our out over own
said says say same she should some such than that the their them then there these they this those through too under until very was were what when where which while who why will with would you your
stock stocks share shares price prices market markets today week news report reports reported analyst analysts buy sell hold rating target inc corp company companies nasdaq nyse ticker here's heres what's whats""".split())


def _words(title: str, names: list) -> set:
    t = title.lower()
    for n in names: t = t.replace(n.lower(), " ")
    return {w for w in re.findall(r"[a-z][a-z0-9\-']{2,}", t) if w not in STOP}


def _ask(names: list, hours: int) -> list:
    from src import news_listener as N
    q = "(" + " OR ".join(f'"{n}"' for n in names) + ")" if len(names) > 1 else f'"{names[0]}"'
    body = N.fetch(API.format(q=urllib.parse.quote(q + " sourcelang:english"), h=hours), timeout=60)
    try: J = json.loads(body)
    except Exception: raise ValueError("GDELT answered with text, not a list: " + body[:90].decode("utf-8", "replace").replace("\n", " "))
    out = []
    for a in J.get("articles", []):
        try: when = datetime.strptime(a["seendate"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except Exception: continue
        out.append(dict(title=str(a.get("title", "")).strip(), domain=str(a.get("domain", "")), url=str(a.get("url", "")), when=when))
    return out


def stories(arts: list, names: list) -> list:
    """group headlines that share most of their words; oldest article first; a later headline joins the story whose words it shares most"""
    S = []
    for a in sorted(arts, key=lambda x: x["when"]):
        if not any(re.search(rf"(?<![A-Za-z0-9]){re.escape(n)}(?![A-Za-z0-9])", a["title"], re.I if len(n) >= 6 else 0) for n in names): continue      # the headline itself must name the company
        w = _words(a["title"], names)
        if len(w) < 3: continue
        best = None; bs = 0.0
        for s in S:
            k = len(w & s["words"]); sh = k / len(w)
            if k >= 2 and sh >= SHARE and sh > bs: best, bs = s, sh
        if best is None: S.append(dict(words=set(w), core=set(w), arts=[a]))
        else: best["arts"].append(a); best["words"] |= w
    for s in S: s["domains"] = sorted({a["domain"] for a in s["arts"]}); s["first"] = min(a["when"] for a in s["arts"])
    return S


def _listener(ticker: str) -> list:
    out = []
    if not LOG.exists(): return out
    for ln in LOG.read_text().splitlines():
        try: d = json.loads(ln)
        except Exception: continue
        if d.get("ticker") != ticker: continue
        try: w = datetime.fromisoformat(str(d.get("published") or d.get("seen")).replace(" ", "T"))
        except Exception: continue
        if w.tzinfo is None: w = w.replace(tzinfo=timezone.utc)
        ev = (d.get("read") or {}).get("evidence") or ""; out.append(dict(when=w, title=str(d.get("title", "")), source=str(d.get("source", "")), text=str(d.get("title", "")) + " " + str(ev)))
    return out


def _had(s: dict, L: list, names: list):
    """what the listener recorded for the company within NEAR_H hours of the story: (verdict, text)"""
    near = [x for x in L if abs((x["when"] - s["first"]).total_seconds()) <= NEAR_H * 3600]
    if not near: return "MISSED", "nothing of this company in these hours"
    same = [x for x in near if len(_words(x["text"], names) & s["core"]) >= 2]
    if same: return "the listener had it", f"{same[0]['source']}: {same[0]['title'][:70]}"
    return "MISSED", "other items only: " + "; ".join(f"{x['source']}: {x['title'][:40]}" for x in near[:2])


def cmd_run(hours: int):
    hours = max(6, min(int(hours), 72)); OUTDIR.mkdir(parents=True, exist_ok=True); seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set(); now = datetime.now(timezone.utc); rows = []; nart = 0; bad = []
    print(f"Looking for news of the last {hours} hours about {len(ASK)} watched companies that the listener did not record. Free (the GDELT Project's news index); about {len(ASK) * PAUSE / 60:.0f} minutes; "
          f"a story needs {MIN_PUBLISHERS} different publishers. Nothing is sent to a paid model. Safe to stop with Ctrl+C and run again.")
    for i, (tk, names) in enumerate(ASK.items()):
        if i: time.sleep(PAUSE)
        try: A = _ask(names, hours)
        except SystemExit: raise
        except Exception as ex: bad.append(tk); print(f"  {tk}: no answer ({type(ex).__name__}: {str(ex)[:80]})"); continue
        nart += len(A); S = [s for s in stories(A, names) if len(s["domains"]) >= MIN_PUBLISHERS]; L = _listener(tk); k = 0
        for s in sorted(S, key=lambda x: -len(x["domains"])):
            key = tk + "|" + hashlib.md5(" ".join(sorted(s["core"])).encode()).hexdigest()[:12]; verdict, what = _had(s, L, names)
            if key in seen or any(r["ticker"] == tk and len(r["core"] & s["core"]) >= 3 for r in rows): continue      # already listed, or the same story in other words
            seen.add(key); first = min(s["arts"], key=lambda a: a["when"]); k += 1
            rows.append(dict(ticker=tk, core=s["core"], headline=first["title"][:160], publishers=len(s["domains"]), domains=s["domains"][:4], first=s["first"], url=first["url"], verdict=verdict, what=what))
        print(f"  {tk}: {len(A)} articles, {len(S)} stories carried by {MIN_PUBLISHERS}+ publishers, {k} new")
    miss = [r for r in rows if r["verdict"] == "MISSED"]
    with FOUND.open("a") as f:
        for r in rows: f.write(json.dumps(dict(found=now.isoformat(), ticker=r["ticker"], headline=r["headline"], publishers=r["publishers"], domains=r["domains"], first_seen_by_gdelt=r["first"].isoformat(), url=r["url"], verdict=r["verdict"], listener=r["what"]), ensure_ascii=False) + "\n")
    SEEN.write_text(json.dumps(sorted(seen)[-20000:]))
    if miss:
        head = "## Found by the detector"; s = MD.read_text() if MD.exists() else "# News the listener missed\n"
        if head not in s:
            s = s.rstrip("\n") + f"\n\n{head}\n\nAdded by `python -m src.missed_news run` (TRACK 3.145). A row = a story about a watched company carried by at least {MIN_PUBLISHERS} different publishers, with no listener item in the same words within {NEAR_H} hours. " \
                "'First seen' is the time the GDELT Project's index saw the first article (steps of 15 minutes), not the minute of publication. Headlines belong to their publishers; the link goes to the first article. Information for the founder only: not scored, not a signal, not shown on the page. Index: the GDELT Project, https://www.gdeltproject.org/.\n\n" \
                "| found (New York) | company | headline of the first article | publishers | first seen (New York) | what the listener had | link |\n|---|---|---|---|---|---|---|\n"
        for r in sorted(miss, key=lambda x: x["first"]):
            s += f"| {now.astimezone(NY):%Y-%m-%d %H:%M} | {r['ticker']} | {r['headline'].replace('|', '/')} | {r['publishers']} ({', '.join(r['domains'])}) | {r['first'].astimezone(NY):%Y-%m-%d %H:%M} | {r['what'].replace('|', '/')} | [first article]({r['url']}) |\n"
        MD.write_text(s)
    print(f"DONE: {nart} articles read, {len(rows)} new stories, of which {len(miss)} MISSED by the listener and {len(rows) - len(miss)} the listener had" + (f"; no answer for: {', '.join(bad)}" if bad else "") + f". -> {MD} (the missed ones), {FOUND} (all)")
    for r in sorted(miss, key=lambda x: -x["publishers"])[:12]: print(f"    MISSED | {r['ticker']} | {r['publishers']} publishers | first seen {r['first'].astimezone(NY):%d %b %H:%M} New York | {r['headline'][:100]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.add_argument("--hours", type=int, default=30); a = ap.parse_args(); cmd_run(a.hours)
