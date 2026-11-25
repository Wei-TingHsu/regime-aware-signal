"""news_listener.py -- the LIVE listener (step 2, founder 15 Nov): watch the fastest public sources that answer from this machine, and the moment one of
the fourteen AI-chain companies publishes results (or files a material event, or the Fed issues a statement) fetch the text, have Claude score it with
the SAME readers as the backtest, show the alert and write everything to the forward log with its times.

Customer-view rule: the product must show the news as fast as it is public. So every item is logged with three clocks -- when the source says it was
published, when this machine first saw it, when the score was ready -- and when two sources carry the same release the delay between them is logged
(this measures how late the SEC route is against the wire, which the backtest could not).

Sources (docs/wire_probe.md, 15 Nov): PR Newswire feeds; the NVIDIA, AMD, Meta and SK Hynix feeds; the Fed's press feed; and for every company the
SEC's filing list (the backup that covers all fourteen, some minutes later). Business Wire and GlobeNewswire refuse scripts from this machine.

    python -m src.news_listener once                 # one pass over every source: what answers, what is newest. Scores nothing.
    python -m src.news_listener test --ticker AMD    # drill: score that company's most recent results release end to end (about 3 US cents)
    python -m src.news_listener run                  # listen until stopped (Ctrl-C); --minutes 120 to stop by itself; --poll 30 seconds between passes
"""
from __future__ import annotations
import argparse, json, os, re, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LIVE = Path("data_provenance/live"); TEXTS = LIVE / "docs"; LOG = LIVE / "events.jsonl"; SEEN = LIVE / "seen.json"; MD = Path("docs/live_news_log.md")
NY, SG = ZoneInfo("America/New_York"), ZoneInfo("Asia/Singapore")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
NAMES = {"NVDA": ["NVIDIA"], "AMD": ["AMD", "Advanced Micro Devices"], "MU": ["Micron"], "INTC": ["Intel"], "AVGO": ["Broadcom"], "SNDK": ["Sandisk", "SanDisk"], "SKHY": ["SK hynix", "SK Hynix"], "ORCL": ["Oracle"],
         "TSM": ["TSMC", "Taiwan Semiconductor"], "CRWD": ["CrowdStrike"], "GOOG": ["Alphabet"], "META": ["Meta"], "AMZN": ["Amazon"], "MSFT": ["Microsoft"]}
SEC_ALIAS = {"GOOG": ["GOOG", "GOOGL"], "META": ["META", "FB"]}
FEEDS = [dict(name="PR Newswire: all releases", kind="wire", url="https://www.prnewswire.com/rss/news-releases-list.rss"),
         dict(name="PR Newswire: earnings", kind="wire", url="https://www.prnewswire.com/rss/financial-services-latest-news/earnings-list.rss"),
         dict(name="NVIDIA newsroom", kind="company", ticker="NVDA", url="https://nvidianews.nvidia.com/releases.xml"),
         dict(name="AMD investor page", kind="company", ticker="AMD", url="https://ir.amd.com/rss/news-releases.xml"),
         dict(name="Meta investor page", kind="company", ticker="META", url="https://investor.atmeta.com/rss/pressrelease.aspx"),
         dict(name="SK Hynix newsroom", kind="company", ticker="SKHY", url="https://news.skhynix.com/feed/"),
         dict(name="Federal Reserve: monetary policy press releases", kind="fed", url="https://www.federalreserve.gov/feeds/press_monetary.xml")]
RESEARCH = [      # founder, 20 Nov: research publishers and funds that publish their reports. THIRD PARTIES: their claims are theirs, they may hold a position.
    dict(name="Hunterbrook", kind="research", short=True, position="publishes investigations and may trade on them (long or short)", urls=["https://newsletter.hntrbrk.com/feed", "https://hntrbrk.com/feed/", "https://hntrbrk.com/rss.xml"]),
    dict(name="SemiAnalysis", kind="research", position="independent semiconductor and AI research; sells research", urls=["https://semianalysis.com/feed/", "https://newsletter.semianalysis.com/feed", "https://www.semianalysis.com/feed"]),
    dict(name="TrendForce", kind="research", position="market-research firm (memory, foundry, servers, displays); sells research; states no position", urls=["https://www.trendforce.com/feed/Semiconductors.html"]),
]      # the addresses are candidates; the first that answers is used (see `once`)
SHORT = [      # founder, 21 Nov: publishers of short reports, admitted as live ALERTS after SR-1 showed their reports move the price on the day (TRACK 3.85). THIRD PARTIES, claims unverified, no trading rule.
    dict(name="Grizzly Research", kind="short", position="publishes short reports and may hold a short position", url="https://grizzlyreports.com/feed/"),
    dict(name="Blue Orca", kind="short", position="publishes short (and some long) reports and may hold a position", url="https://www.blueorcacapital.com/feed/"),
    dict(name="Fuzzy Panda", kind="short", position="publishes short reports and may hold a short position", url="https://fuzzypandaresearch.com/feed/")]
PV_R = "ai-research-v1-2026-11-20"
SYS_R = """You are given (1) a BASELINE: a listed company's most recent reported financials and guidance, and (2) a REPORT about that company published by
a THIRD PARTY: a research firm, or an investor that may hold a position in the stock (for example a short seller). The claims are the publisher's own
and are NOT verified. Do not judge whether they are true. Score what the report means for the share price IF investors take it seriously, relative to
the baseline, and how specific and checkable it is. Judge from the two texts only; do not use anything you know about how markets reacted.
Return STRICT JSON, no preamble:
{"report_type": one of "short report", "long thesis", "industry research", "product or supply-chain analysis", "other",
 "stance": -1..+1 (the publisher's stance on the company: -1 = strongly negative),
 "new_information": 0..1 (how much is specific, checkable new information -- figures, documents, named sources -- rather than opinion),
 "material": 0..1 (how much this would matter against the size of the baseline if true),
 "fcf_outlook": -1..+1 (change in expected future free cash flow if the claims hold),
 "uncertainty": -1..+1 (+1 = makes future cash flows, guidance or governance clearly less predictable),
 "own_stock": -1..+1 (what the report means for the company's share price over the next few sessions if taken seriously),
 "market": -1..+1 (for large US technology shares as a group; 0 if it concerns only this company),
 "affected": [up to six OTHER companies named or implicated; each {"company": ticker or name, "relation": "competitor" | "supplier" | "customer" | "peer", "direction": -1..+1, "reason": a few words}],
 "main_claims": [up to three short sentences stating the report's main claims in neutral words],
 "evidence": one quoted clause that best supports own_stock}"""
RX_RESULTS = r"\b(reports?|announces?|posts?|delivers?)\b.*\b(quarter(ly)?|results|earnings)\b"
RX_NOT = r"\b(to (report|announce|host|release|webcast|present)|sets? (date|conference)|conference call|date for|schedules?|will (report|announce|host)|timing of|investor (day|conference))\b"
RX_EVENT = r"\$\s?\d[\d.,]*\s?(billion|million)|\b(acquir\w*|acquisition|merger|merge[sd]?|divest\w*|to sell|completes?|definitive agreement|strategic (partnership|collaboration|investment)|multi-?year|invest(s|ment)? (of )?\$|\$\s?\d[\d.,]*\s?(billion|million)|chief executive|\bCEO\b|\bCFO\b|chief financial|appoints?|names? new|resign\w*|retire\w*|steps? down|succession|guidance|outlook|preliminary|offering|notes due|buyback|repurchase|dividend|stock split|restructur\w*|layoffs?|workforce reduction|investigation|settle\w*|lawsuit|export (control|licen[cs]e)|breach|outage|recall)\b"      # a company-feed title that looks like a material event (17 Nov: the acquisition AMD announced on its own page was only logged)
EVENT_ITEMS = {"1.01", "1.02", "1.03", "1.05", "2.01", "2.03", "2.04", "2.05", "2.06", "3.01", "4.01", "4.02", "5.01", "5.02", "7.01", "8.01"}


# ------------------------------------------------------------------------------------------------ fetching
def fetch(url: str, timeout=20) -> bytes:
    sec = "sec.gov" in url
    if sec and not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set (the SEC asks every script to say who is calling)")
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": os.environ["SEC_CONTACT"] if sec else UA, "Accept": "*/*"}), timeout=timeout).read(4_000_000)


def _when(raw: str):
    try: t = parsedate_to_datetime(raw)
    except Exception:
        try: t = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception: return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def feed_items(body: bytes) -> list:
    root = ET.fromstring(body); strip = lambda tag: tag.split("}")[-1]; out = []
    for it in (e for e in root.iter() if strip(e.tag) in ("item", "entry")):
        d = {}
        for c in it:
            k = strip(c.tag); d[k] = (c.text or "").strip() or c.attrib.get("href", "") or d.get(k, "")
        link = d.get("link") or d.get("guid") or d.get("id") or ""; raw = d.get("pubDate") or d.get("updated") or d.get("published") or d.get("date") or ""
        summary = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", d.get("encoded") or d.get("description") or d.get("summary") or d.get("content") or ""))
        out.append(dict(id=d.get("guid") or d.get("id") or link or d.get("title", ""), title=re.sub(r"\s+", " ", d.get("title", "")), link=link, published=_when(raw), summary=summary))
    return out


def text_of(html: bytes) -> str:
    t = html.decode("utf-8", "ignore"); t = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", t, flags=re.S); t = re.sub(r"</(p|div|tr|li|h\d|br)[^>]*>|<br[^>]*>", "\n", t, flags=re.I); t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&nbsp;|&#160;", " ", t); t = re.sub(r"&amp;", "&", t); t = re.sub(r"[ \t]+", " ", t); return re.sub(r"\n\s*\n+", "\n", t).strip()


def sec_ciks() -> dict:
    cmap = json.loads(fetch("https://www.sec.gov/files/company_tickers.json")); look = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}
    return {t: next(look[a] for a in SEC_ALIAS.get(t, [t]) if a in look) for t in NAMES if any(a in look for a in SEC_ALIAS.get(t, [t]))}


def sec_recent(cik: str, n=6) -> list:
    r = json.loads(fetch(f"https://data.sec.gov/submissions/CIK{cik}.json"))["filings"]["recent"]; out = []
    for i in range(min(n, len(r.get("form", [])))):
        out.append(dict(id=r["accessionNumber"][i], form=r["form"][i], items=(r.get("items") or [""] * 99)[i] or "", accession=r["accessionNumber"][i], primary=(r.get("primaryDocument") or [""] * 99)[i], published=_when(str(r["acceptanceDateTime"][i])), title=f"{r['form'][i]} items {(r.get('items') or [''] * 99)[i] or 'n/a'}"))
    return out


SEC_CURRENT = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form}&company=&dateb=&owner=include&count=100&output=atom"


def sec_current(by_cik: dict) -> dict:
    """25 Nov 2026 (lag watch, TRACK 3.113): the SEC's single list of the newest filings shows a filing about half a minute before the company's own list does
    (middle 36 s against 73 s after acceptance). -> {source name: [items]} for the companies of the list, in the shape sec_recent gives; the company's own list
    stays as the backup, and a filing seen on both is taken once (same accession number)."""
    out = {}
    for form in ("8-K", "6-K"):
        for it in feed_items(fetch(SEC_CURRENT.format(form=form))):
            m = re.search(r"/data/(\d+)/", it.get("link", "")); a = re.search(r"(\d{10})-?(\d{2})-?(\d{6})", it.get("link", "").split("/data/")[-1])
            if not m or not a or it["title"].split(" - ")[0].strip().upper() != form or it.get("published") is None: continue
            src = by_cik.get(m.group(1).zfill(10))
            if src is None: continue
            acc = f"{a.group(1)}-{a.group(2)}-{a.group(3)}"; items = ",".join(re.findall(r"Item (\d+\.\d+)", it.get("summary", "")))
            out.setdefault(src, []).append(dict(id=acc, form=form, items=items, accession=acc, primary="", published=it["published"], title=f"{form} items {items or 'n/a'}"))
    return out


def sec_text(cik: str, accession: str, primary: str) -> str:
    acc = accession.replace("-", ""); base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/"; body = ""
    try: body = text_of(fetch(base + primary)) if primary else ""
    except Exception: pass
    try:
        items = json.loads(fetch(base + "index.json"))["directory"]["item"]      # 18 Nov: NVIDIA's exhibit files are not named 'ex99' or 'press', so the reader was given the cover page only
        def size(i):
            try: return int(i.get("size") or 0)
            except Exception: return 0
        docs = [i for i in items if i.get("name", "") != primary and i.get("name", "").lower().endswith((".htm", ".html")) and not re.match(r"(r\d+|.*-index.*|filingsummary)\.html?$", i.get("name", "").lower())]
        for i in sorted(docs, key=size, reverse=True)[:3]:      # the three largest: the press release and, where filed, the CFO commentary
            time.sleep(0.15); body += "\n\n[EXHIBIT]\n" + text_of(fetch(base + i["name"]))
    except Exception: pass
    return body


# ------------------------------------------------------------------------------------------------ what an item is
def company_of(title: str):
    for t, names in NAMES.items():
        if any(re.match(rf"\s*{re.escape(n)}(\b|,|\.|\s)", title) for n in names): return t      # a company's own release starts with its name
    return None


def companies_in(text: str) -> list:
    """every listed company whose name appears anywhere in the text (a third party writes ABOUT a company; the name need not come first)"""
    return [t for t, names in NAMES.items() if any(re.search(rf"(?<![A-Za-z0-9]){re.escape(n)}(?![A-Za-z0-9])", text, re.I if len(n) >= 6 else 0) for n in names)]      # long names in any letter case; short ones (AMD, Meta, Intel) exactly as written


def classify(src: dict, it: dict):
    """-> (ticker or 'FED', kind) with kind in results | event | fed | other; or (None, None) when the item is not about the list"""
    if src["kind"] == "sec":
        items = {x.strip() for x in it["items"].split(",")}
        if it["form"] == "8-K": return src["ticker"], ("results" if "2.02" in items else "event")
        return (src["ticker"], "event") if it["form"] == "6-K" else (None, None)
    if src["kind"] == "research":
        tk = companies_in(it["title"]) or companies_in(it.get("summary", "")[:1500]); it["companies"] = tk; return (tk[0], "research") if tk else (("?", "short report") if src.get("short") else (None, None))      # a short-report publisher writing about a company outside the list: an alert all the same
    if src["kind"] == "short": return "?", "short report"
    if src["kind"] == "fed": return ("FED", "fed") if re.search(r"FOMC statement", it["title"], re.I) else (None, None)
    tk = src.get("ticker") or company_of(it["title"])
    if tk is None: return None, None
    if re.search(RX_RESULTS, it["title"], re.I) and not re.search(RX_NOT, it["title"], re.I): return tk, "results"
    return tk, "event"      # 20 Nov, founder: every item about a listed company is scored; routine ones come back with 'material' near 0


# ------------------------------------------------------------------------------------------------ scoring (the backtest's readers, unchanged)
def score(tk: str, kind: str, text: str, stem: str, when: datetime) -> dict | None:
    from src.news_events2 import _client
    import src.ai_earnings as A
    client = _client(); TEXTS.mkdir(parents=True, exist_ok=True); f = TEXTS / f"{stem}.txt"; f.write_text(f"[{tk} live {kind}]\n\n{text}")
    if kind == "fed":
        from src.news_events2 import _ask
        from src.news_events3 import SYS_DOC, PV3, CHARS
        m = re.search(r"(Recent indicators|Information received|Economic activity|Available indicators|The Committee|Although|Indicators)", text); body = text[m.start():] if m else text
        d, _, _ = _ask(client, SYS_DOC, f"DOCUMENT (fomc, {when.astimezone(NY):%Y-%m-%d}):\n{body[:CHARS]}", stem, LIVE / "reads", PV3); return d
    R = A._results(); naive = when.astimezone(NY).replace(tzinfo=None)
    if kind == "results":
        pg = None
        for q in R[(R.ticker == tk) & (R.kind == "results") & (R.accepted_ny < naive)].iloc[::-1].itertuples():
            d0 = A._read1(q.file)
            if d0: pg = (d0.get("facts") or {}).get("guidance_next"); break
        d, _, _ = A._ask2(client, A.SYS1, f"PRIOR GUIDANCE (from the company's previous release): {pg or 'none available'}\n\nRELEASE:\n{A._release_body(str(f), A.CHARS1, A.TABLES)}", "LIVE_" + stem, A.PV1); return d
    if kind.startswith("research"):
        pub, pos = kind.split("|")[1:3] if kind.count("|") >= 2 else ("a third party", "unknown"); d, _, _ = A._ask2(client, SYS_R, f"BASELINE: {A._baseline(R, tk, naive)}\n\nREPORT about {tk}, published by {pub} ({pos}); claims unverified:\n{A._release_body(str(f), 9000)}", "LIVE_" + stem, PV_R); return d
    d, _, _ = A._ask2(client, A.SYS2, f"BASELINE: {A._baseline(R, tk, naive)}\n\nEVENT ({tk}, live):\n{A._release_body(str(f), A.CHARS2)}", "LIVE_" + stem, A.PV2); return d


def empty_read(d, kind: str) -> bool:
    """a results read that found no revenue and scored everything 0: the text given to the reader did not contain the release"""
    if not d: return True
    if kind != "results": return False
    nums = [d.get(k) for k in ("own_stock", "market", "ai_demand", "results_vs_prior_guidance", "guidance_change", "fcf_trend")]
    return (d.get("facts") or {}).get("revenue") in (None, "", "null") and all((x in (None, 0, 0.0, "0")) for x in nums)


def _line(d: dict, kind: str) -> str:
    if not d: return "NOT SCORED (the read failed; the text is saved)"
    if kind == "research": return f"THIRD-PARTY REPORT, claims unverified [{d.get('report_type')}] stance {d.get('stance')!s}, own stock {d.get('own_stock')!s}, material {d.get('material')!s}, new information {d.get('new_information')!s}, uncertainty {d.get('uncertainty')!s} | " + " ".join(str(x) for x in (d.get("main_claims") or []))[:260] + f" | affects {[(x.get('company'), x.get('direction')) for x in (d.get('affected') or []) if isinstance(x, dict)][:5]}"
    if empty_read(d, kind): return "NOT SCORED: the text fetched did not contain the results (no revenue found, every score 0); the next source will be tried"
    if kind == "fed": return f"for stocks {d.get('implication_equities')!s}, for rates {d.get('implication_rates')!s} | {str(d.get('evidence'))[:140]}"
    if kind == "results":
        fx = d.get("facts") or {}; return (f"own stock {d.get('own_stock')!s}, market {d.get('market')!s}, AI demand {d.get('ai_demand')!s}, vs prior guidance {d.get('results_vs_prior_guidance')!s}, new guidance {d.get('guidance_change')!s}, free cash flow {d.get('fcf_trend')!s} | "
            f"revenue {str(fx.get('revenue'))[:40]}; free cash flow {str(fx.get('free_cash_flow'))[:40]}; guidance {str(fx.get('guidance_next'))[:90]} | affects {[(x.get('company'), x.get('direction')) for x in (d.get('affected') or []) if isinstance(x, dict)][:5]}")
    return f"[{d.get('event_type')}] material {d.get('material')!s}, own stock {d.get('own_stock')!s}, uncertainty {d.get('uncertainty')!s}, free-cash-flow outlook {d.get('fcf_outlook')!s} | {str(d.get('evidence'))[:120]}"


# ------------------------------------------------------------------------------------------------ the loop
def _log(row: dict):
    LIVE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh: fh.write(json.dumps(row, default=str) + "\n")


def _md(row: dict):
    if not MD.exists(): MD.parent.mkdir(exist_ok=True); MD.write_text("# Live news log (forward record)\n\nEach row: a results release, a material company filing or a Fed statement seen live by `src/news_listener.py`, scored by the same readers as the backtest. Three clocks: published (as the source states), seen (this machine), scored. Prices are joined later.\n\n| seen (New York) | seen (Singapore) | who | kind | first source | published → seen | seen → scored | score | title |\n|---|---|---|---|---|---|---|---|---|\n")
    with MD.open("a") as fh: fh.write(f"| {row['seen_ny']} | {row['seen_sg']} | {row['ticker']} | {row['kind']}{' (DRILL)' if row.get('drill') else ''} | {row['source']} | {row.get('lag_published_s', '')} s | {row.get('score_s', '')} s | {row.get('line', '')[:230].replace('|', '/')} | {row['title'][:90].replace('|', '/')} |\n")


def handle_short(src: dict, it: dict, state: dict, drill=False, do_score=True):
    """a short-report publisher's item (any company, on the list or not): read with SR-1's reader (title and the feed's own text), logged as an ALERT. No rule."""
    import hashlib
    from src.short_reports import SYS, PV, _body
    now = datetime.now(timezone.utc); pub = it.get("published"); row = dict(ticker="?", kind="short report", source=src["name"], title=it["title"], link=it.get("link", ""), id=it["id"], published=pub, seen=now, seen_ny=now.astimezone(NY).strftime("%Y-%m-%d %H:%M:%S"), seen_sg=now.astimezone(SG).strftime("%Y-%m-%d %H:%M:%S"),
                                                                              lag_published_s=round((now - pub).total_seconds()) if pub else None, drill=drill, publisher=src["name"])
    if not do_score: row.update(kind="other", not_scored="today's scoring budget is used up"); _log(row); print(f"   .. {src['name']}: {it['title'][:100]}  [NOT read: today's budget of scores is used up]"); return
    try:
        from src.news_events2 import _client, _parse, MODEL
        f = LIVE / "reads" / f"SHORT_{re.sub(r'[^A-Za-z0-9]+', '', src['name'])[:14]}_{hashlib.sha1(str(it['id']).encode()).hexdigest()[:12]}__{PV}.json"; f.parent.mkdir(parents=True, exist_ok=True)
        if f.exists(): d = json.loads(f.read_text())
        else:
            a = _client().messages.create(model=MODEL, max_tokens=1500, system=SYS, messages=[{"role": "user", "content": _body(src["name"], dict(published=(pub or now).isoformat(), title=it["title"], summary=it.get("summary", "")))}]); d = _parse("".join(b.text for b in a.content if b.type == "text")); f.write_text(json.dumps(d, indent=1))
        tg = [x for x in (d.get("targets") or []) if isinstance(x, dict) and str(x.get("direction")).lstrip("-") == "1"] if d.get("is_report") else []
        if not tg: row.update(kind="other", line="not a report on a listed company (note, media coverage, reply or follow-up without a target)", score_s=round((datetime.now(timezone.utc) - now).total_seconds())); _log(row); print(f"   .. {src['name']}: {it['title'][:90]}  [read: not a report on a listed company]"); return
        x = tg[0]; dr = int(x["direction"]); tk = str(x.get("yahoo_symbol") or x.get("ticker") or x.get("company") or "?").upper()
        try: sev = float(d.get("severity") or 0)
        except Exception: sev = 0.0
        t = (pub or now).astimezone(NY); hm = t.hour * 60 + t.minute; when = "at a weekend" if t.weekday() >= 5 else ("before the open" if hm < 570 else ("during the session" if hm < 960 else "after the close"))
        read = dict(report_type="short report" if dr < 0 else "long thesis", own_stock=round(dr * sev, 2), material=sev, severity=sev, direction=dr, claim=d.get("claim"), first=bool(x.get("first")), targets=tg, main_claims=[d.get("summary")], published_when=when)
        line = f"SHORT-SELLER REPORT, claims unverified: {'NEGATIVE' if dr < 0 else 'POSITIVE'} on {x.get('company')} ({tk}); severity as stated {sev}; claim: {d.get('claim')}; {'first report' if x.get('first') else 'follow-up'}; published {when} | {d.get('summary')}" + (f" | also names {[y.get('yahoo_symbol') or y.get('company') for y in tg[1:4]]}" if len(tg) > 1 else "")
        row.update(ticker=tk, read=read, line=line, score_s=round((datetime.now(timezone.utc) - now).total_seconds()), companies=[y.get("yahoo_symbol") or y.get("company") for y in tg])
        print("\a" + "=" * 110 + f"\n{'DRILL  ' if drill else ''}{tk}  SHORT REPORT  seen {row['seen_ny']} New York / {row['seen_sg']} Singapore  via {src['name']}" + (f"  ({row['lag_published_s']} s after the source's own time)" if pub else "") + f"\n{it['title'][:160]}\n{line}\n(read {row['score_s']} s after it was seen)\n" + "=" * 110)
    except SystemExit: raise
    except Exception as e: row.update(kind="other", line=f"NOT READ: {type(e).__name__}: {str(e)[:120]}"); print(f"   .. {src['name']}: {it['title'][:90]}  [{row['line']}]")
    _log(row)
    if row["kind"] == "short report": _md(row)


def handle(src: dict, it: dict, tk: str, kind: str, state: dict, drill=False, do_score=True):
    if kind == "short report": return handle_short(src, it, state, drill=drill, do_score=do_score)
    now = datetime.now(timezone.utc); pub = it.get("published"); day = (pub or now).astimezone(NY).strftime("%Y%m%d"); key = f"{tk}|{kind}|{day}" if kind in ("results", "fed") else f"{tk}|{kind}|{it['id']}"
    row = dict(ticker=tk, kind=kind, source=src["name"], title=it["title"], link=it.get("link", ""), id=it["id"], published=pub, seen=now, seen_ny=now.astimezone(NY).strftime("%Y-%m-%d %H:%M:%S"), seen_sg=now.astimezone(SG).strftime("%Y-%m-%d %H:%M:%S"),
               lag_published_s=round((now - pub).total_seconds()) if pub else None, drill=drill)
    first = state["first"].get(key)
    if first and not drill:      # the same release from a second source: record how much later it came, do not score twice
        row.update(kind=kind + " (again)", second_source_after_s=round((now - datetime.fromisoformat(first["seen"])).total_seconds()), first_source=first["source"]); _log(row)
        print(f"   .. {tk} {kind}: also on {src['name']}, {row['second_source_after_s']} s after {first['source']}"); return
    if not do_score: row["not_scored"] = "today's scoring budget is used up"; _log(row); print(f"   .. {tk}: {it['title'][:100]}  [{src['name']}; NOT scored: today's budget of scores is used up -- raise --max-scores]"); return
    print("\a" + "=" * 110 + f"\n{'DRILL  ' if drill else ''}{tk}  {kind.upper()}  seen {row['seen_ny']} New York / {row['seen_sg']} Singapore  via {src['name']}" + (f"  ({row['lag_published_s']} s after the source's own time)" if pub else "") + f"\n{it['title'][:160]}")
    try:
        if src["kind"] == "research":
            try: text = text_of(fetch(it["link"]))
            except Exception: text = ""
            if len(text.split()) < 150 or len(it.get("summary", "").split()) > len(text.split()): text = it["title"] + "\n\n" + it.get("summary", "")      # paywalled page: use what the feed itself carries
            row.update(publisher=src["name"], companies=it.get("companies"))
        else: text = sec_text(src["cik"], it["accession"], it["primary"]) if src["kind"] == "sec" else text_of(fetch(it["link"]))
        if len(text.split()) < (25 if src["kind"] == "research" else 80): raise ValueError(f"only {len(text.split())} words fetched")
        import hashlib
        stem = f"{tk}_{day}_{re.sub(r'[^A-Za-z0-9]+', '', src['name'])[:14]}" + ("" if kind in ("results", "fed") else "_" + hashlib.md5(str(it["id"]).encode()).hexdigest()[:6]); d = score(tk, f"research|{src['name']}|{src.get('position', '')}" if kind == "research" else kind, text, stem, pub or now); row.update(score_s=round((datetime.now(timezone.utc) - now).total_seconds()), words=len(text.split()), read=d, line=_line(d, kind))
        if d and not empty_read(d, kind): state["first"][key] = dict(seen=now.isoformat(), source=src["name"])
        else: row["empty"] = True
    except SystemExit: raise
    except Exception as e: row.update(line=f"NOT SCORED: {type(e).__name__}: {str(e)[:120]}")
    print(f"{row['line']}\n(scored {row.get('score_s', '?')} s after it was seen)\n" + "=" * 110); _log(row); _md(row)


def sources() -> list:
    S = [dict(f) for f in FEEDS] + [dict(f) for f in RESEARCH] + [dict(f) for f in SHORT]
    try: S += [dict(name=f"SEC filings: {t}", kind="sec", ticker=t, cik=c) for t, c in sec_ciks().items()]
    except SystemExit: raise
    except Exception as e: print(f"  SEC company list not reachable ({type(e).__name__}); running without the SEC backup")
    return S


def poll(src: dict) -> list:
    if src["kind"] == "sec": return sec_recent(src["cik"])
    if "url" in src: return feed_items(fetch(src["url"]))
    err = None
    for u in src["urls"]:      # candidate addresses: keep the first that answers with a feed
        try: items = feed_items(fetch(u)); src["url"] = u; return items
        except Exception as e: err = e
    raise err


def cmd_once():
    print(f"one pass at {datetime.now(NY):%Y-%m-%d %H:%M:%S} New York / {datetime.now(SG):%H:%M:%S} Singapore"); ok = 0
    for src in sources():
        try: items = poll(src)
        except SystemExit: raise
        except Exception as e: print(f"  {src['name'][:48]:48} NO ANSWER: {type(e).__name__}: {str(e)[:70]}"); continue
        ok += 1; hits = [(it, *classify(src, it)) for it in items]; mine = [h for h in hits if h[1]]; new = max((it for it in items if it["published"]), key=lambda x: x["published"], default=None)
        print(f"  {src['name'][:48]:48} {len(items):3} items; newest {new['published'].astimezone(NY):%d %b %H:%M} NY" if new else f"  {src['name'][:48]:48} {len(items):3} items", end="")
        print(f"; about the list: {len(mine)}" + (f" (e.g. {mine[0][1]} {mine[0][2]}: {mine[0][0]['title'][:60]})" if mine else "") + (f"  [{src['url']}]" if src["kind"] == "research" and "url" in src else "")); time.sleep(0.2)
    print(f"{ok} sources answered. Nothing was scored.")


def cmd_test(ticker: str):
    S = [s for s in sources() if s.get("ticker") == ticker]; S.sort(key=lambda s: s["kind"] == "sec")      # the company's own feed first, the SEC as the fallback
    for src in S:
        try: items = poll(src)
        except Exception as e: print(f"  {src['name']}: {type(e).__name__}"); continue
        res = [it for it in items if classify(src, it) == (ticker, "results")]
        if res: it = max(res, key=lambda x: x["published"] or datetime.min.replace(tzinfo=timezone.utc)); handle(src, it, ticker, "results", dict(first={}), drill=True); return
        print(f"  {src['name']}: no results release among its {len(items)} newest items")
    print("no results release found to drill on -- try another --ticker")


def cmd_research(ticker: str):
    """drill: score the newest third-party report that names one company, end to end. Flagged as a drill; shows that the route works."""
    for src in [x for x in sources() if x["kind"] == "research"]:
        try: items = poll(src)
        except Exception as e: print(f"  {src['name']}: NO ANSWER from any of its candidate addresses ({type(e).__name__})"); continue
        hits = [it for it in items if classify(src, it) == (ticker, "research")]; print(f"  {src['name']}: {len(items)} items at {src.get('url')}; naming {ticker}: {len(hits)}")
        if hits: handle(src, max(hits, key=lambda x: x["published"] or datetime.min.replace(tzinfo=timezone.utc)), ticker, "research", dict(first={}), drill=True); return
    print(f"no third-party report naming {ticker} among the newest items")


def cmd_rescore(ticker: str):
    """Redo the latest results release of one company from its SEC filing (corrected text fetch). The score is made from the text alone, so the rules
    that depend only on the release time (FA-3, QC-3) can use it; it is flagged 'rescored' and is NOT a customer-view observation (CV-1)."""
    src = next((s for s in sources() if s["kind"] == "sec" and s.get("ticker") == ticker), None)
    if src is None: print(f"{ticker}: not found at the SEC"); return
    res = [it for it in sec_recent(src["cik"], n=12) if classify(src, it) == (ticker, "results")]
    if not res: print(f"{ticker}: no results filing among its 12 newest filings"); return
    it = max(res, key=lambda x: x["published"]); pub = it["published"]; day = pub.astimezone(NY).strftime("%Y%m%d"); text = sec_text(src["cik"], it["accession"], it["primary"]); print(f"{ticker}: filing {it['accession']} stamped {pub.astimezone(NY):%Y-%m-%d %H:%M:%S} New York; {len(text.split())} words fetched")
    d = score(ticker, "results", text, f"{ticker}_{day}_rescore", pub); first = None
    if LOG.exists():
        for x in LOG.read_text().splitlines():
            try: r = json.loads(x)
            except Exception: continue
            if r.get("ticker") == ticker and str(r.get("kind", "")).startswith("results") and not r.get("drill") and str(r.get("seen_ny", ""))[:10].replace("-", "") == day: first = first or r
    now = datetime.now(timezone.utc); row = dict(ticker=ticker, kind="results", source=src["name"] + " (rescored)", title=it["title"], id=it["id"], published=pub, seen=(first or {}).get("seen", now), seen_ny=(first or {}).get("seen_ny", now.astimezone(NY).strftime("%Y-%m-%d %H:%M:%S")), seen_sg=(first or {}).get("seen_sg", now.astimezone(SG).strftime("%Y-%m-%d %H:%M:%S")),
               lag_published_s=(first or {}).get("lag_published_s"), drill=False, rescored=True, rescored_at=now, words=len(text.split()), read=d, line=_line(d, "results"))
    print("=" * 110 + f"\n{ticker}  RESULTS (rescored after the fact)\n{row['line']}\n" + "=" * 110)
    if d and not empty_read(d, "results"): _log(row); _md(row); print("logged")
    else: print("still empty -- paste this output to Claude")


def cmd_run(minutes: float | None, every: float, max_scores: int):
    S = sources(); LIVE.mkdir(parents=True, exist_ok=True); state = json.loads(SEEN.read_text()) if SEEN.exists() else dict(ids=[], first={}); seen = set(state["ids"]); t_end = time.time() + minutes * 60 if minutes else None; n = 0
    known = set(state.get("warmed") or ({x.split("|")[0] for x in seen})); budget = state.get("budget") or {}      # sources already memorised once; scores used per New York day
    print(f"listening to {len(S)} sources every {every:.0f} s" + (f" for {minutes:.0f} minutes" if minutes else " until stopped with Ctrl-C") + f". A source connected for the first time is only memorised; items older than a day are never scored. Budget: {max_scores} scores a day.")
    try:
        while t_end is None or time.time() < t_end:
            t0 = time.time(); bad = []; now = datetime.now(timezone.utc); day = now.astimezone(NY).strftime("%Y-%m-%d")
            try: fast = sec_current({x["cik"]: x["name"] for x in S if x["kind"] == "sec"})      # 25 Nov: the SEC's single list first; about half a minute earlier than each company's own list
            except SystemExit: raise
            except Exception: fast = {}
            for src in S:
                if src["kind"] in ("research", "short") and time.time() - src.get("_last", 0) < 120: continue      # 25 Nov: these sites publish a few times a day and one refused a look every 15 s
                src["_last"] = time.time()
                try: items = fast.get(src["name"], []) + poll(src)
                except SystemExit: raise
                except Exception: bad.append(src["name"]); continue
                first_time = src["name"] not in known; old = 0
                for it in items:
                    uid = f"{src['name']}|{it['id']}"; tid = f"{src['name']}|title|{re.sub(r'[^a-z0-9]+', ' ', it['title'].lower()).strip()}"; lid = f"{src['name']}|link|{str(it.get('link') or it['id']).split('#')[0].split('?')[0].rstrip('/')}"
                    if uid in seen: continue
                    seen.add(uid); nt = tid.split("|title|")[1]; pre = src["name"] + "|title|"; again = src["kind"] != "sec" and (tid in seen or lid in seen or (len(nt) >= 25 and any(x.startswith(pre) and len(x) - len(pre) >= 25 and (nt in x or x[len(pre):] in nt) for x in seen))); seen.add(lid)      # 20 Nov (second fix): the same SK Hynix article arrived ten times under pieces of its headline -- the same address is the same article
                    if again: seen.add(tid); continue      # 20 Nov: one SK Hynix article arrived as twelve feed entries with the same headline and was scored twelve times
                    seen.add(tid)
                    if first_time: continue
                    if it.get("published") and (now - it["published"]).total_seconds() > 86400: old += 1; continue      # already old when first seen: not news
                    tk, kind = classify(src, it)
                    if tk:
                        used = int(budget.get(day, 0)); handle(src, it, tk, kind, state, do_score=used < max_scores); budget = {day: used + 1}
                if first_time: known.add(src["name"]); print(f"   .. {src['name']}: connected for the first time; {len(items)} existing items memorised, none scored")
                elif old: print(f"   .. {src['name']}: {old} item(s) older than a day skipped")
                if src["kind"] == "sec": time.sleep(0.12)
            n += 1; state["ids"] = sorted(seen)[-20000:]; state["warmed"] = sorted(known); state["budget"] = budget; SEEN.write_text(json.dumps(state))
            if n == 1 or n % 20 == 0: print(f"  {datetime.now(NY):%H:%M:%S} New York / {datetime.now(SG):%H:%M:%S} Singapore: pass {n}, {len(S) - len(bad)} of {len(S)} sources answered" + (f"; silent: {', '.join(bad)[:120]}" if bad else "") + f"; scores used today: {int(budget.get(day, 0))} of {max_scores}")
            time.sleep(max(1.0, every - (time.time() - t0)))
    except KeyboardInterrupt: print("\nstopped by you")
    print(f"{n} passes. Log: {LOG} and {MD}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["once", "test", "run", "rescore", "research"]); ap.add_argument("--ticker", default="AMD"); ap.add_argument("--minutes", type=float); ap.add_argument("--poll", type=float, default=30.0); ap.add_argument("--max-scores", type=int, default=150, help="scores allowed per New York day (cost guard; about 1 to 3 US cents each)")
    a = ap.parse_args(); {"once": cmd_once, "test": lambda: cmd_test(a.ticker), "rescore": lambda: cmd_rescore(a.ticker), "research": lambda: cmd_research(a.ticker), "run": lambda: cmd_run(a.minutes, a.poll, a.max_scores)}[a.cmd]()
